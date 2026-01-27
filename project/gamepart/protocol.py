import typing


class ProtocolMeta(type):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, typing.Any],
    ) -> "ProtocolMeta":
        defaults = sorted(
            [(key, value) for key, value in dct.items() if mcs.is_field(key, value)]
        )
        for key, value in defaults:
            dct.pop(key)
        dct["__slots__"] = tuple([key for key, value in defaults])
        for base in bases:
            defaults = list(getattr(base, "_defaults", [])) + defaults
        dct["_defaults"] = tuple(defaults)
        dct["_keys"] = tuple([key for key, value in defaults])
        return super().__new__(mcs, name, bases, dct)

    @staticmethod
    def is_field(name: str, value: typing.Any) -> bool:
        return not (
            callable(value) or name.startswith("_") or isinstance(value, classmethod)
        )


class Protocol(metaclass=ProtocolMeta):
    __slots__: tuple[str, ...]
    _defaults: tuple[tuple[str, typing.Any]]
    _keys: tuple[str, ...]

    def __init__(self) -> None:
        self.clear()

    def update(self, data: typing.Iterable[typing.Any]) -> None:
        for key, value in zip(self._keys, data):
            setattr(self, key, value)

    def update_dict(self, data: dict[str, typing.Any]) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    def serialize(self) -> list[typing.Any]:
        return [getattr(self, key, default) for key, default in self._defaults]

    def serialize_dict(self) -> dict[str, typing.Any]:
        return {key: getattr(self, key, default) for key, default in self._defaults}

    @classmethod
    def deserialize(cls, data: list[typing.Any]) -> "Protocol":
        instance = cls()
        instance.update(data)
        return instance

    @classmethod
    def deserialize_dict(cls, data: dict[str, typing.Any]) -> "Protocol":
        instance = cls()
        instance.update_dict(data)
        return instance

    def clear(self) -> None:
        for key, default in self._defaults:
            setattr(self, key, default)

    def copy(self, source: "Protocol") -> None:
        for key, default in self._defaults:
            setattr(self, key, getattr(source, key, default))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.serialize_dict()!r}>"
