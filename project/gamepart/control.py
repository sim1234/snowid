import typing


class Input:
    __slots__: typing.Tuple[str, ...]
    default: typing.Any = None

    def __init__(self, data: typing.Sequence = ()):
        self.update(data)

    def update(self, data: typing.Sequence):
        default = self.default
        for i, k in enumerate(self.__slots__):
            try:
                setattr(self, k, data[i])
            except IndexError:
                setattr(self, k, default)

    def clear(self):
        default = self.default
        for k in self.__slots__:
            setattr(self, k, default)

    def serialize(self) -> typing.Sequence:
        default = self.default
        return [getattr(self, k, default) for k in self.__slots__]

    def copy(self, control: "Input"):
        default = self.default
        for k in self.__slots__:
            setattr(self, k, getattr(control, k, default))

    def __repr__(self):
        return f"{self.__class__.__name__}({self.serialize()!r})"


T = typing.TypeVar("T", bound=Input)
TO = typing.TypeVar("TO")


class Controller(typing.Generic[T, TO]):
    input_class: typing.Type[T]

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
