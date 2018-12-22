import typing


class SubSystemObject:
    pass


T = typing.TypeVar("T", bound=SubSystemObject)
ST = typing.TypeVar("ST", bound=SubSystemObject)


class SubSystem(typing.Generic[T]):
    def __init__(self):
        self.objects: typing.List[T] = []

    def get_objects(self, *types: typing.Type[ST]) -> typing.Iterable[ST]:
        for obj in self.objects:
            if isinstance(obj, types):
                yield obj  # type: ignore

    def add(self, *objects: T) -> typing.Iterable[T]:
        self.objects.extend(objects)
        return objects

    def remove(self, *objects: T) -> typing.Iterable[T]:
        for obj in objects:
            self.objects.remove(obj)
        return objects

    def clear(self) -> typing.Iterable[T]:
        return self.remove(*self.objects)

    def __del__(self):
        self.clear()
