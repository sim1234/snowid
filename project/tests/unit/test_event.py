"""Tests for event dispatchers."""

from unittest.mock import Mock

from gamepart.event import (
    Dispatcher,
    EventDispatcher,
    KeyboardEventDispatcher,
    MouseButtonEventDispatcher,
)


class TestDispatcher:
    """Test base Dispatcher class."""

    def test_on_registers_callback(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback = Mock()

        dispatcher.on("key1", callback)

        assert "key1" in dispatcher.callbacks
        assert callback in dispatcher.callbacks["key1"]

    def test_on_registers_multiple_callbacks_for_same_key(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback1 = Mock()
        callback2 = Mock()

        dispatcher.on("key1", callback1)
        dispatcher.on("key1", callback2)

        assert len(dispatcher.callbacks["key1"]) == 2
        assert callback1 in dispatcher.callbacks["key1"]
        assert callback2 in dispatcher.callbacks["key1"]

    def test_chain_after_registers_callback(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback = Mock()

        dispatcher.chain_after(callback)

        assert callback in dispatcher.after_chained

    def test_chain_before_registers_callback(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback = Mock()

        dispatcher.chain_before(callback)

        assert callback in dispatcher.before_chained

    def test_call_invokes_matching_callbacks(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback = Mock(return_value=None)

        dispatcher.on("key1", callback)
        dispatcher("key1")

        callback.assert_called_once_with("key1")

    def test_call_does_not_invoke_non_matching_callbacks(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback = Mock(return_value=None)

        dispatcher.on("key1", callback)
        dispatcher("key2")

        callback.assert_not_called()

    def test_call_invokes_chain_after_callbacks_after_keyed(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        call_order: list[str] = []
        keyed_callback = Mock(side_effect=lambda _: call_order.append("keyed"))
        after_callback = Mock(side_effect=lambda _: call_order.append("after"))

        dispatcher.on("key1", keyed_callback)
        dispatcher.chain_after(after_callback)
        dispatcher("key1")

        assert call_order == ["keyed", "after"]

    def test_call_invokes_chain_before_then_keyed_then_chain_after(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        call_order: list[str] = []
        before_callback = Mock(side_effect=lambda _: call_order.append("before"))
        keyed_callback = Mock(side_effect=lambda _: call_order.append("keyed"))
        after_callback = Mock(side_effect=lambda _: call_order.append("after"))

        dispatcher.chain_before(before_callback)
        dispatcher.on("key1", keyed_callback)
        dispatcher.chain_after(after_callback)
        dispatcher("key1")

        assert call_order == ["before", "keyed", "after"]

    def test_call_invokes_chain_after_even_without_matching_key(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        after_callback = Mock(return_value=None)

        dispatcher.chain_after(after_callback)
        dispatcher("any_key")

        after_callback.assert_called_once_with("any_key")

    def test_call_invokes_chain_before_even_without_matching_key(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        before_callback = Mock(return_value=None)

        dispatcher.chain_before(before_callback)
        dispatcher("any_key")

        before_callback.assert_called_once_with("any_key")

    def test_call_stops_propagation_when_callback_returns_truthy(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback1 = Mock(return_value=True)
        callback2 = Mock(return_value=None)

        dispatcher.on("key1", callback1)
        dispatcher.on("key1", callback2)
        result = dispatcher("key1")

        callback1.assert_called_once()
        callback2.assert_not_called()
        assert result is True

    def test_call_stops_propagation_before_chain_after(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        keyed_callback = Mock(return_value=True)
        after_callback = Mock(return_value=None)

        dispatcher.on("key1", keyed_callback)
        dispatcher.chain_after(after_callback)
        dispatcher("key1")

        keyed_callback.assert_called_once()
        after_callback.assert_not_called()

    def test_call_stops_propagation_when_chain_before_returns_truthy(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        before_callback = Mock(return_value=True)
        keyed_callback = Mock(return_value=None)
        after_callback = Mock(return_value=None)

        dispatcher.chain_before(before_callback)
        dispatcher.on("key1", keyed_callback)
        dispatcher.chain_after(after_callback)
        result = dispatcher("key1")

        before_callback.assert_called_once_with("key1")
        keyed_callback.assert_not_called()
        after_callback.assert_not_called()
        assert result is True

    def test_call_passes_data_to_callback(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        callback = Mock(return_value=None)

        dispatcher.on("key1", callback)
        dispatcher("key1")

        callback.assert_called_once_with("key1")

    def test_call_returns_none_when_no_callbacks_match(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()

        result = dispatcher("key1")

        assert result is None

    def test_clear_removes_all_callbacks(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        dispatcher.on("key1", Mock())
        dispatcher.on("key2", Mock())
        dispatcher.chain_before(Mock())
        dispatcher.chain_after(Mock())

        dispatcher.clear()

        assert len(dispatcher.callbacks) == 0
        assert len(dispatcher.before_chained) == 0
        assert len(dispatcher.after_chained) == 0

    def test_noop_does_nothing(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        dispatcher.noop("any_data")
        # noop returns None implicitly

    def test_stop_returns_true(self) -> None:
        dispatcher: Dispatcher[str, str] = Dispatcher()
        result: bool = dispatcher.stop("any_data")
        assert result is True

    def test_get_key_returns_data_as_key_by_default(self) -> None:
        result: str = Dispatcher.get_key("test_data")
        assert result == "test_data"


class MockSDLEvent:
    """Mock SDL_Event for testing."""

    def __init__(self, event_type: int) -> None:
        self.type = event_type


class MockKeyboardEvent:
    """Mock SDL_KeyboardEvent for testing."""

    def __init__(self, sym: int) -> None:
        self.keysym = Mock(sym=sym)


class MockMouseButtonEvent:
    """Mock SDL_MouseButtonEvent for testing."""

    def __init__(self, button: int) -> None:
        self.button = button


class TestEventDispatcher:
    """Test EventDispatcher class."""

    def test_get_key_returns_event_type(self) -> None:
        event = MockSDLEvent(event_type=42)

        result = EventDispatcher.get_key(event)  # type: ignore

        assert result == 42

    def test_dispatches_by_event_type(self) -> None:
        dispatcher = EventDispatcher()
        callback = Mock(return_value=None)
        event = MockSDLEvent(event_type=100)

        dispatcher.on(100, callback)
        dispatcher(event)  # type: ignore

        callback.assert_called_once_with(event)

    def test_does_not_dispatch_to_wrong_event_type(self) -> None:
        dispatcher = EventDispatcher()
        callback = Mock(return_value=None)
        event = MockSDLEvent(event_type=100)

        dispatcher.on(200, callback)
        dispatcher(event)  # type: ignore

        callback.assert_not_called()


class TestKeyboardEventDispatcher:
    """Test KeyboardEventDispatcher class."""

    def create_key_event(self, event_type: int, key_sym: int) -> MockSDLEvent:
        event = MockSDLEvent(event_type)
        event.key = MockKeyboardEvent(key_sym)  # type: ignore
        return event

    def test_get_key_returns_type_and_keysym(self) -> None:
        event = self.create_key_event(event_type=768, key_sym=27)

        result = KeyboardEventDispatcher.get_key(event)  # type: ignore

        assert result == (768, 27)

    def test_dispatches_by_event_type_and_keysym(self) -> None:
        dispatcher = KeyboardEventDispatcher()
        callback = Mock(return_value=None)
        event = self.create_key_event(event_type=768, key_sym=27)

        dispatcher.on((768, 27), callback)
        dispatcher(event)  # type: ignore

        callback.assert_called_once_with(event)

    def test_does_not_dispatch_to_wrong_key(self) -> None:
        dispatcher = KeyboardEventDispatcher()
        callback = Mock(return_value=None)
        event = self.create_key_event(event_type=768, key_sym=27)

        dispatcher.on((768, 32), callback)
        dispatcher(event)  # type: ignore

        callback.assert_not_called()

    def test_on_up_registers_for_keyup_event(self) -> None:
        dispatcher = KeyboardEventDispatcher()
        callback = Mock()
        sdl_keyup = 769  # SDL_KEYUP value

        dispatcher.on_up(27, callback)

        assert (sdl_keyup, 27) in dispatcher.callbacks
        assert callback in dispatcher.callbacks[(sdl_keyup, 27)]

    def test_on_down_registers_for_keydown_event(self) -> None:
        dispatcher = KeyboardEventDispatcher()
        callback = Mock()
        sdl_keydown = 768  # SDL_KEYDOWN value

        dispatcher.on_down(27, callback)

        assert (sdl_keydown, 27) in dispatcher.callbacks
        assert callback in dispatcher.callbacks[(sdl_keydown, 27)]

    def test_attach_to_registers_with_event_dispatcher(self) -> None:
        key_dispatcher = KeyboardEventDispatcher()
        event_dispatcher = EventDispatcher()
        sdl_keydown = 768  # SDL_KEYDOWN value
        sdl_keyup = 769  # SDL_KEYUP value

        key_dispatcher.attach_to(event_dispatcher)

        assert sdl_keydown in event_dispatcher.callbacks
        assert key_dispatcher in event_dispatcher.callbacks[sdl_keydown]
        assert sdl_keyup in event_dispatcher.callbacks
        assert key_dispatcher in event_dispatcher.callbacks[sdl_keyup]


class TestMouseButtonEventDispatcher:
    """Test MouseButtonEventDispatcher class."""

    def create_mouse_event(self, event_type: int, button: int) -> MockSDLEvent:
        event = MockSDLEvent(event_type)
        event.button = MockMouseButtonEvent(button)  # type: ignore
        return event

    def test_get_key_returns_type_and_button(self) -> None:
        event = self.create_mouse_event(event_type=1025, button=1)

        result = MouseButtonEventDispatcher.get_key(event)  # type: ignore

        assert result == (1025, 1)

    def test_dispatches_by_event_type_and_button(self) -> None:
        dispatcher = MouseButtonEventDispatcher()
        callback = Mock(return_value=None)
        event = self.create_mouse_event(event_type=1025, button=1)

        dispatcher.on((1025, 1), callback)
        dispatcher(event)  # type: ignore

        callback.assert_called_once_with(event)

    def test_does_not_dispatch_to_wrong_button(self) -> None:
        dispatcher = MouseButtonEventDispatcher()
        callback = Mock(return_value=None)
        event = self.create_mouse_event(event_type=1025, button=1)

        dispatcher.on((1025, 3), callback)
        dispatcher(event)  # type: ignore

        callback.assert_not_called()

    def test_on_up_registers_for_mousebuttonup_event(self) -> None:
        dispatcher = MouseButtonEventDispatcher()
        callback = Mock()
        sdl_mousebuttonup = 1026  # SDL_MOUSEBUTTONUP value

        dispatcher.on_up(1, callback)

        assert (sdl_mousebuttonup, 1) in dispatcher.callbacks
        assert callback in dispatcher.callbacks[(sdl_mousebuttonup, 1)]

    def test_on_down_registers_for_mousebuttondown_event(self) -> None:
        dispatcher = MouseButtonEventDispatcher()
        callback = Mock()
        sdl_mousebuttondown = 1025  # SDL_MOUSEBUTTONDOWN value

        dispatcher.on_down(1, callback)

        assert (sdl_mousebuttondown, 1) in dispatcher.callbacks
        assert callback in dispatcher.callbacks[(sdl_mousebuttondown, 1)]

    def test_attach_to_registers_with_event_dispatcher(self) -> None:
        event_dispatcher = EventDispatcher()
        mouse_dispatcher = MouseButtonEventDispatcher()
        sdl_mousebuttondown = 1025  # SDL_MOUSEBUTTONDOWN value
        sdl_mousebuttonup = 1026  # SDL_MOUSEBUTTONUP value

        mouse_dispatcher.attach_to(event_dispatcher)

        assert sdl_mousebuttondown in event_dispatcher.callbacks
        assert sdl_mousebuttonup in event_dispatcher.callbacks
        assert mouse_dispatcher in event_dispatcher.callbacks[sdl_mousebuttondown]
        assert mouse_dispatcher in event_dispatcher.callbacks[sdl_mousebuttonup]


class TestDispatcherIntegration:
    """Integration tests for dispatcher chaining."""

    def test_key_dispatcher_works_through_event_dispatcher(self) -> None:
        event_dispatcher = EventDispatcher()
        key_dispatcher = KeyboardEventDispatcher()
        callback = Mock(return_value=None)
        sdl_keydown = 768

        key_dispatcher.attach_to(event_dispatcher)
        key_dispatcher.on_down(27, callback)

        event = MockSDLEvent(event_type=sdl_keydown)
        event.key = MockKeyboardEvent(sym=27)  # type: ignore

        event_dispatcher(event)  # type: ignore

        callback.assert_called_once_with(event)

    def test_propagation_stops_through_chain(self) -> None:
        event_dispatcher = EventDispatcher()
        key_dispatcher = KeyboardEventDispatcher()
        stopper = Mock(return_value=True)
        not_called = Mock(return_value=None)
        sdl_keydown = 768

        key_dispatcher.attach_to(event_dispatcher)
        key_dispatcher.on_down(27, stopper)
        event_dispatcher.chain_after(not_called)

        event = MockSDLEvent(event_type=sdl_keydown)
        event.key = MockKeyboardEvent(sym=27)  # type: ignore

        event_dispatcher(event)  # type: ignore

        stopper.assert_called_once()
        not_called.assert_not_called()

    def test_chain_before_runs_before_key_dispatcher(self) -> None:
        event_dispatcher = EventDispatcher()
        key_dispatcher = KeyboardEventDispatcher()
        call_order: list[str] = []
        before_callback = Mock(side_effect=lambda e: call_order.append("before"))
        key_callback = Mock(side_effect=lambda e: call_order.append("key"))
        sdl_keydown = 768

        key_dispatcher.attach_to(event_dispatcher)
        event_dispatcher.chain_before(before_callback)
        key_dispatcher.on_down(27, key_callback)

        event = MockSDLEvent(event_type=sdl_keydown)
        event.key = MockKeyboardEvent(sym=27)  # type: ignore

        event_dispatcher(event)  # type: ignore

        assert call_order == ["before", "key"]
