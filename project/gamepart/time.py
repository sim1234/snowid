import collections
import logging
import time
import typing

logger = logging.getLogger(__name__)


class FPSCounter:
    """FPS counter with throttling functionality"""

    def __init__(self, maxlen: int = 120):
        self.history: collections.deque[float] = collections.deque(maxlen=maxlen)
        self.sleep_history: collections.deque[float] = collections.deque(maxlen=maxlen)
        self.last_frame: int = time.perf_counter_ns()
        self.less_sleep: float = 0.001  # compensate for inaccuracy of sleep

    def frame(self) -> float:
        new_frame = time.perf_counter_ns()
        delta = new_frame - self.last_frame
        delta_f = delta / 1_000_000_000.0
        self.history.append(delta_f)
        self.last_frame = new_frame
        return (1.0 / delta_f) if delta_f else 0.0

    def target_fps(self, fps: float = 120.0, recent: int | None = None) -> None:
        if recent is None:
            recent = int(len(self.history) / 10)
        history = list(self.history)[-recent:]
        len_ = len(history)
        sum_ = sum(history)
        sleep = min((len_ / fps) - sum_, 1.0 / fps)
        if sleep <= 0:
            self.sleep_history.append(0.0)
        else:
            start = time.perf_counter_ns()
            time.sleep(max(0.0, sleep - self.less_sleep))
            actual = (time.perf_counter_ns() - start) / 1_000_000_000.0
            self.sleep_history.append(actual)
            logger.log(
                0,
                "FPS inhibition: %fms (%fms actual) FPS=%f",
                sleep * 1000.0,
                actual * 1000.0,
                1.0 / history[-1],
            )

    def clear(self) -> None:
        self.last_frame = time.perf_counter_ns()
        while self.history:
            self.history.pop()
        while self.sleep_history:
            self.sleep_history.pop()

    def get_fps(self) -> float:
        len_ = len(self.history)
        sum_ = sum(self.history)
        return (len_ / sum_) if sum_ else 0.0

    def get_fps_summary(self) -> str:
        total_time_data = []
        frame_time_data = []
        usage_data = []
        count = 0
        for total_time, sleep_time in zip(
            reversed(self.history), reversed(self.sleep_history)
        ):
            count += 1
            frame_time = total_time - sleep_time
            total_time_data.append(total_time)
            frame_time_data.append(frame_time)
            usage_data.append(100.0 * frame_time / total_time)
        if count == 0:
            return "No data"

        rows: list[tuple[str, str, list[float | str]]] = []
        # Why FPS avg is wrong?
        rows.append(("Metric", "", ["avg", "min", "max", "last"]))
        rows.append(
            (
                "FPS",
                "",
                [
                    count / sum(total_time_data),
                    1.0 / max(total_time_data),
                    1.0 / min(total_time_data),
                    1.0 / total_time_data[0],
                ],
            )
        )
        rows.append(
            (
                "Total",
                "ms",
                [
                    1000.0 * sum(total_time_data) / count,
                    1000.0 * min(total_time_data),
                    1000.0 * max(total_time_data),
                    1000.0 * total_time_data[0],
                ],
            )
        )
        rows.append(
            (
                "Frame",
                "ms",
                [
                    1000.0 * sum(frame_time_data) / count,
                    1000.0 * min(frame_time_data),
                    1000.0 * max(frame_time_data),
                    1000.0 * frame_time_data[0],
                ],
            )
        )
        rows.append(
            (
                "Usage",
                "%",
                [
                    sum(usage_data) / count,
                    min(usage_data),
                    max(usage_data),
                    usage_data[0],
                ],
            )
        )
        res = []
        for metric, unit, values in rows:
            vals = [
                (f"{v:.2f}{unit}" if isinstance(v, float) else v).rjust(10)
                for v in values
            ]
            res.append(f"{metric:>10} {' '.join(vals)}")
        return "\n".join(res)


class TimeFeeder:
    """Quantize passed time into time_step chunks"""

    def __init__(self, time_step: float = 1 / 2**10, speed: float = 1.0):
        self.time_step = time_step
        self.speed = speed
        self.system_time = 0.0
        self.world_time = 0.0

    def tick(
        self, delta: float, max_iter: int = 0
    ) -> typing.Generator[float, None, None]:
        self.system_time += delta * self.speed
        x = 0
        while self.world_time < self.system_time:
            self.world_time += self.time_step
            yield self.time_step
            x += 1
            if max_iter and x > max_iter:
                logger.warning(
                    "World time is lagging by %d steps",
                    round(self.lag / self.time_step),
                )
                return

    def catch_up(self) -> float:
        return sum(self.tick(0))

    @property
    def lag(self) -> float:
        return self.system_time - self.world_time
