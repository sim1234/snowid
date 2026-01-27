"""Tests for Controller and Input classes."""

import pytest
from gamepart.control import Controller, Input
from gamepart.protocol import Protocol


class TestInput:
    """Test Input base class."""

    def test_input_is_protocol_subclass(self) -> None:
        """Test that Input inherits from Protocol."""
        assert issubclass(Input, Protocol)

    def test_input_can_be_instantiated(self) -> None:
        """Test that Input can be created."""
        inp = Input()
        assert inp is not None

    def test_custom_input_with_fields(self) -> None:
        """Test creating custom Input with fields."""

        class PlayerInput(Input):
            move_x = 0.0
            move_y = 0.0
            jump = False

        inp = PlayerInput()
        assert inp.move_x == 0.0
        assert inp.move_y == 0.0
        assert inp.jump is False

    def test_custom_input_inherits_protocol_methods(self) -> None:
        """Test that custom Input has Protocol methods."""

        class PlayerInput(Input):
            move_x = 0.0
            jump = False

        inp = PlayerInput()
        inp.move_x = 1.5
        inp.jump = True

        serialized = inp.serialize_dict()
        assert serialized["move_x"] == 1.5
        assert serialized["jump"] is True


class TestControllerInit:
    """Test Controller initialization."""

    def test_controller_initialization(self) -> None:
        """Test controller initializes with object and inputs."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

        controller = TestController("test_object")
        assert controller.object == "test_object"
        assert isinstance(controller.input, TestInput)
        assert isinstance(controller.last_input, TestInput)

    def test_controller_inputs_are_separate_instances(self) -> None:
        """Test that input and last_input are different objects."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

        controller = TestController("obj")
        assert controller.input is not controller.last_input

    def test_controller_inputs_start_with_defaults(self) -> None:
        """Test that inputs start with default values."""

        class TestInput(Input):
            value = 42
            name = "default"

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

        controller = TestController("obj")
        assert controller.input.value == 42
        assert controller.input.name == "default"
        assert controller.last_input.value == 42
        assert controller.last_input.name == "default"


class TestControllerInitInput:
    """Test Controller.init_input class method."""

    def test_init_input_creates_instance(self) -> None:
        """Test init_input creates new input instance."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

        inp = TestController.init_input()
        assert isinstance(inp, TestInput)
        assert inp.value == 0

    def test_init_input_creates_fresh_instance(self) -> None:
        """Test init_input creates new instance each call."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

        inp1 = TestController.init_input()
        inp2 = TestController.init_input()
        assert inp1 is not inp2


class TestControllerControl:
    """Test Controller.control method."""

    def test_control_calls_act(self) -> None:
        """Test control calls act method."""

        class TestInput(Input):
            value = 0

        act_calls: list[tuple[float, float]] = []

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                act_calls.append((game_time, delta))

        controller = TestController("obj")
        controller.control(1.0, 0.016)
        assert len(act_calls) == 1
        assert act_calls[0] == (1.0, 0.016)

    def test_control_copies_input_to_last_input(self) -> None:
        """Test control copies current input to last_input."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")
        controller.input.value = 99
        controller.control(1.0, 0.016)
        assert controller.last_input.value == 99

    def test_control_clears_current_input(self) -> None:
        """Test control clears current input after processing."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")
        controller.input.value = 99
        controller.control(1.0, 0.016)
        assert controller.input.value == 0

    def test_control_sequence_preserves_last_input(self) -> None:
        """Test multiple control calls update last_input correctly."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")

        controller.input.value = 10
        controller.control(1.0, 0.016)
        assert controller.last_input.value == 10
        assert controller.input.value == 0

        controller.input.value = 20
        controller.control(2.0, 0.016)
        assert controller.last_input.value == 20
        assert controller.input.value == 0


class TestControllerAct:
    """Test Controller.act method."""

    def test_act_raises_not_implemented(self) -> None:
        """Test base act method raises NotImplementedError."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

        controller = TestController("obj")
        with pytest.raises(NotImplementedError):
            controller.act(1.0, 0.016)


class TestControllerSetter:
    """Test Controller.setter method."""

    def test_setter_creates_callback(self) -> None:
        """Test setter creates a callable."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")
        callback = controller.setter("value", 42)
        assert callable(callback)

    def test_setter_callback_sets_attribute(self) -> None:
        """Test setter callback sets input attribute."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")
        callback = controller.setter("value", 42)
        callback()
        assert controller.input.value == 42

    def test_setter_callback_ignores_args(self) -> None:
        """Test setter callback ignores extra arguments."""

        class TestInput(Input):
            value = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")
        callback = controller.setter("value", 99)
        callback("ignored", 123, extra="kwargs")
        assert controller.input.value == 99

    def test_setter_with_different_types(self) -> None:
        """Test setter works with different value types."""

        class TestInput(Input):
            active = False
            name = ""
            count = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")

        controller.setter("active", True)()
        assert controller.input.active is True

        controller.setter("name", "test")()
        assert controller.input.name == "test"

        controller.setter("count", 5)()
        assert controller.input.count == 5

    def test_multiple_setters_same_attribute(self) -> None:
        """Test multiple setters for same attribute work independently."""

        class TestInput(Input):
            direction = 0

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")
        move_left = controller.setter("direction", -1)
        move_right = controller.setter("direction", 1)
        stop = controller.setter("direction", 0)

        move_left()
        assert controller.input.direction == -1

        move_right()
        assert controller.input.direction == 1

        stop()
        assert controller.input.direction == 0


class TestControllerIntegration:
    """Integration tests for Controller with realistic usage."""

    def test_full_input_cycle(self) -> None:
        """Test complete input processing cycle."""

        class PlayerInput(Input):
            move_x = 0.0
            move_y = 0.0
            jump = False

        class Player:
            def __init__(self) -> None:
                self.x = 0.0
                self.y = 0.0
                self.velocity_y = 0.0

        class PlayerController(Controller[PlayerInput, Player]):
            input_class = PlayerInput

            def act(self, game_time: float, delta: float) -> None:
                self.object.x += self.input.move_x * delta * 100
                self.object.y += self.input.move_y * delta * 100
                if self.input.jump and not self.last_input.jump:
                    self.object.velocity_y = 10.0

        player = Player()
        controller = PlayerController(player)

        controller.input.move_x = 1.0
        controller.input.jump = True
        controller.control(0.0, 0.1)

        assert player.x == 10.0
        assert player.velocity_y == 10.0

        controller.input.move_x = 1.0
        controller.input.jump = True
        controller.control(0.1, 0.1)

        assert player.x == 20.0
        assert player.velocity_y == 10.0

    def test_event_callback_integration(self) -> None:
        """Test setter callbacks work for event-driven input."""

        class TestInput(Input):
            left = False
            right = False

        class TestController(Controller[TestInput, str]):
            input_class = TestInput

            def act(self, game_time: float, delta: float) -> None:
                pass

        controller = TestController("obj")

        on_left_press = controller.setter("left", True)
        on_left_release = controller.setter("left", False)
        on_right_press = controller.setter("right", True)

        on_left_press()
        assert controller.input.left is True
        assert controller.input.right is False

        on_right_press()
        assert controller.input.left is True
        assert controller.input.right is True

        on_left_release()
        assert controller.input.left is False
        assert controller.input.right is True
