"""Integration tests for UserEventType with real SDL."""

from collections.abc import Generator

import pytest
import sdl2
import sdl2.ext
from gamepart.event import UserEventType


@pytest.fixture(scope="module")
def sdl_init() -> Generator[None, None, None]:
    """Initialize SDL for the test module."""
    sdl2.SDL_Init(sdl2.SDL_INIT_EVENTS)
    yield
    sdl2.SDL_Quit()


class TestUserEventTypeInit:
    """Tests for UserEventType initialization."""

    def test_registers_event_type(self, sdl_init: None) -> None:
        """Test UserEventType registers a unique event type."""
        event_type = UserEventType()
        assert event_type.type >= sdl2.SDL_USEREVENT

    def test_multiple_instances_get_different_types(self, sdl_init: None) -> None:
        """Test multiple UserEventType instances get different types."""
        event1 = UserEventType()
        event2 = UserEventType()
        assert event1.type != event2.type


class TestUserEventTypeRepr:
    """Tests for UserEventType.__repr__."""

    def test_repr_includes_class_name(self, sdl_init: None) -> None:
        """Test repr includes class name."""
        event_type = UserEventType()
        result = repr(event_type)
        assert "UserEventType" in result

    def test_repr_includes_type_value(self, sdl_init: None) -> None:
        """Test repr includes type value."""
        event_type = UserEventType()
        result = repr(event_type)
        assert str(event_type.type) in result


class TestUserEventTypeEmit:
    """Tests for UserEventType.emit method."""

    def test_emit_creates_event_with_type(self, sdl_init: None) -> None:
        """Test emit creates event with correct type."""
        event_type = UserEventType()
        event = event_type.emit()
        assert event.type == event_type.type

    def test_emit_sets_user_code(self, sdl_init: None) -> None:
        """Test emit sets user code on event."""
        event_type = UserEventType()
        event = event_type.emit(code=42)
        assert event.user.code == 42

    def test_emit_with_default_code(self, sdl_init: None) -> None:
        """Test emit uses default code of 0."""
        event_type = UserEventType()
        event = event_type.emit()
        assert event.user.code == 0

    def test_emit_pushes_to_event_queue(self, sdl_init: None) -> None:
        """Test emit pushes event to SDL event queue."""
        sdl2.SDL_FlushEvents(sdl2.SDL_USEREVENT, sdl2.SDL_LASTEVENT)

        event_type = UserEventType()
        event_type.emit(code=123)

        polled_event = sdl2.SDL_Event()
        found = False
        while sdl2.SDL_PollEvent(polled_event):
            if polled_event.type == event_type.type:
                found = True
                assert polled_event.user.code == 123
                break

        assert found, "Event was not found in the queue"

    def test_emit_returns_event_object(self, sdl_init: None) -> None:
        """Test emit returns the created event object."""
        event_type = UserEventType()
        event = event_type.emit(code=99)

        assert event is not None
        assert event.type == event_type.type
        assert event.user.code == 99


class TestUserEventTypeDereferenceData:
    """Tests for UserEventType.dereference_data method."""

    def test_returns_none_for_wrong_event_type(self, sdl_init: None) -> None:
        """Test returns None when event type doesn't match."""
        event_type = UserEventType()

        other_event = sdl2.SDL_Event()
        other_event.type = sdl2.SDL_QUIT

        result = event_type.dereference_data(other_event)
        assert result is None

    def test_returns_none_when_data1_is_zero(self, sdl_init: None) -> None:
        """Test returns None when data1 is 0."""
        event_type = UserEventType()
        event = event_type.emit()

        result = event_type.dereference_data(event)
        assert result is None
