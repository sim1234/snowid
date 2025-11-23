import typing

from .protocol import Protocol


class Input(Protocol):
    pass


T = typing.TypeVar("T", bound=Input)
TO = typing.TypeVar("TO")


class Controller(typing.Generic[T, TO]):
    input_class: type[T]

    def __init__(self, obj: TO):
        self.last_input: T = self.init_input()
        self.input: T = self.init_input()
        self.object: TO = obj

    @classmethod
    def init_input(cls) -> T:
        return cls.input_class()

    def control(self, game_time: float, delta: float):
        self.act(game_time, delta)
        self.last_input.copy(self.input)
        self.input.clear()

    def act(self, game_time: float, delta: float):
        raise NotImplementedError()

    def setter(self, attribute: str, value: typing.Any) -> typing.Callable:
        def callback(*args, **kwargs):
            setattr(self.input, attribute, value)

        return callback
