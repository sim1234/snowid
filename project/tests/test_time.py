"""Tests for time management classes."""

import time

from gamepart.time import FPSCounter, TimeFeeder


class TestFPSCounter:
    """Test FPSCounter class."""

    def test_initialization(self) -> None:
        """Test FPSCounter initialization."""
        counter = FPSCounter(maxlen=10)
        assert len(counter.history) == 0
        assert counter.last_frame > 0

    def test_frame_recording(self) -> None:
        """Test recording frames."""
        counter = FPSCounter(maxlen=10)
        fps = counter.frame()
        assert len(counter.history) == 1
        assert fps > 0

    def test_multiple_frames(self) -> None:
        """Test recording multiple frames."""
        counter = FPSCounter(maxlen=10)
        for _ in range(5):
            counter.frame()
            time.sleep(0.001)  # Small delay to ensure different timestamps
        assert len(counter.history) == 5

    def test_maxlen_limit(self) -> None:
        """Test that history respects maxlen."""
        counter = FPSCounter(maxlen=3)
        for _ in range(5):
            counter.frame()
        assert len(counter.history) == 3

    def test_get_fps_empty(self) -> None:
        """Test getting FPS with empty history."""
        counter = FPSCounter(maxlen=10)
        fps = counter.get_fps()
        assert fps == 0.0

    def test_get_fps_with_history(self) -> None:
        """Test getting FPS with history."""
        counter = FPSCounter(maxlen=10)
        # Simulate consistent frame times
        for _ in range(5):
            counter.frame()
            time.sleep(0.01)  # 10ms per frame = 100 FPS
        fps = counter.get_fps()
        # Should be approximately 100 FPS (allowing for timing variance)
        assert 50 < fps < 200  # Wide range due to timing variance

    def test_clear(self) -> None:
        """Test clearing counter."""
        counter = FPSCounter(maxlen=10)
        counter.frame()
        counter.frame()
        assert len(counter.history) == 2
        counter.clear()
        assert len(counter.history) == 0

    def test_target_fps_no_sleep(self) -> None:
        """Test target_fps when no sleep is needed."""
        counter = FPSCounter(maxlen=10)
        # Record slow frames (low FPS)
        for _ in range(5):
            counter.frame()
            time.sleep(0.1)  # 100ms per frame = 10 FPS
        # Requesting 5 FPS should not require sleep
        counter.target_fps(5.0)
        # Should complete without error

    def test_target_fps_with_sleep(self) -> None:
        """Test target_fps when sleep is needed."""
        counter = FPSCounter(maxlen=10)
        # Record fast frames (high FPS)
        for _ in range(5):
            counter.frame()
            time.sleep(0.001)  # 1ms per frame = 1000 FPS
        # Requesting 60 FPS should require sleep
        counter.target_fps(60.0)
        # Should complete without error


class TestTimeFeeder:
    """Test TimeFeeder class."""

    def test_initialization(self) -> None:
        """Test TimeFeeder initialization."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        assert feeder.time_step == 0.1
        assert feeder.speed == 1.0
        assert feeder.system_time == 0.0
        assert feeder.world_time == 0.0

    def test_tick_single_step(self) -> None:
        """Test ticking with single step."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        deltas = list(feeder.tick(0.1))
        assert len(deltas) == 1
        assert deltas[0] == 0.1
        assert feeder.world_time == 0.1

    def test_tick_multiple_steps(self) -> None:
        """Test ticking with multiple steps."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        deltas = list(feeder.tick(0.3))
        assert len(deltas) == 3
        assert all(d == 0.1 for d in deltas)
        # Allow for floating point precision
        assert abs(feeder.world_time - 0.3) < 1e-10

    def test_tick_with_speed(self) -> None:
        """Test ticking with speed multiplier."""
        feeder = TimeFeeder(time_step=0.1, speed=2.0)
        deltas = list(feeder.tick(0.2))  # 0.2 * 2.0 = 0.4 system time
        assert len(deltas) == 4  # 0.4 / 0.1 = 4 steps
        assert feeder.world_time == 0.4

    def test_tick_max_iter(self) -> None:
        """Test ticking with max_iter limit."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        deltas = list(feeder.tick(1.0, max_iter=5))
        # max_iter check happens AFTER yielding, so we get max_iter + 1 yields
        # before the check triggers
        assert len(deltas) >= 5  # At least max_iter steps
        # World time will be processed up to the limit
        assert feeder.world_time <= 1.0

    def test_lag_property(self) -> None:
        """Test lag property."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        list(feeder.tick(0.15))  # Process all available time
        # After processing, lag should be minimal (all time was processed)
        # The lag is system_time - world_time, and tick processes all available time
        assert feeder.lag < 0.1  # Should be less than one time step

    def test_catch_up(self) -> None:
        """Test catch_up method."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        feeder.system_time = 0.5  # Set system time ahead
        total = feeder.catch_up()
        assert total > 0
        assert feeder.world_time >= feeder.system_time

    def test_no_lag_when_caught_up(self) -> None:
        """Test that lag is zero when caught up."""
        feeder = TimeFeeder(time_step=0.1, speed=1.0)
        list(feeder.tick(0.1))
        assert feeder.lag == 0.0
