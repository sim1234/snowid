import typing


class ProtocolMeta(type):
    def __new__(
        mcs,
        name: str,
        bases: typing.Tuple[type, ...],
        dct: typing.Dict[str, typing.Any],
    ):
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
    def is_field(name, value):
        return not (
            callable(value) or name.startswith("_") or isinstance(value, classmethod)
        )


class Protocol(metaclass=ProtocolMeta):
    __slots__: typing.Tuple[str, ...]
    _defaults: typing.Tuple[typing.Tuple[str, typing.Any]]
    _keys: typing.Tuple[str, ...]

    def __init__(self):
        self.clear()

    def update(self, data: typing.Iterable[typing.Any]):
        for key, value in zip(self._keys, data):
            setattr(self, key, value)

    def update_dict(self, data: typing.Dict[str, typing.Any]):
        for key, value in data.items():
            setattr(self, key, value)

    def serialize(self) -> typing.List[typing.Any]:
        return [getattr(self, key, default) for key, default in self._defaults]

    def serialize_dict(self):
        return {key: getattr(self, key, default) for key, default in self._defaults}

    @classmethod
    def deserialize(cls, data: typing.List[typing.Any]) -> "Protocol":
        instance = cls()
        instance.update(data)
        return instance

    @classmethod
    def deserialize_dict(cls, data: typing.Dict[str, typing.Any]) -> "Protocol":
        instance = cls()
        instance.update_dict(data)
        return instance

    def clear(self):
        for key, default in self._defaults:
            setattr(self, key, default)

    def copy(self, source: "Protocol"):
        for key, default in self._defaults:
            setattr(self, key, getattr(source, key, default))

    def __repr__(self):
        return f"{self.__class__.__name__}<{self.serialize_dict()!r}>"
