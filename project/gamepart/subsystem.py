import typing


class SubSystemObject:
    def __init__(self):
        self._not_removed: bool = True

    def remove(self):
        self._not_removed = False

    def __bool__(self) -> bool:
        return self._not_removed


T = typing.TypeVar("T", bound=SubSystemObject, contravariant=True)
ST = typing.TypeVar("ST", bound=SubSystemObject)


class SubSystem(SubSystemObject, typing.Generic[T]):
    def __init__(self):
        super().__init__()
        self.objects: typing.List[T] = []

    @staticmethod
    def accepts(obj: typing.Any) -> bool:
        return isinstance(obj, SubSystemObject)

    def get_objects(self, *types: typing.Type[ST]) -> typing.Generator[ST, None, None]:
        for obj in self.objects:
            if isinstance(obj, types):
                yield obj  # type: ignore

    def add(self, *objects: T) -> typing.Iterable[T]:
        for obj in objects:
            assert self.accepts(obj)
        self.objects.extend(objects)
        return objects

    def remove(self, *objects: T) -> typing.Iterable[T]:
        for obj in objects:
            self.objects.remove(obj)
        return objects

    def remove_queued(self) -> typing.Iterable[T]:
        return self.remove(*[obj for obj in self.objects if not obj])

    def clear(self) -> typing.Iterable[T]:
        return self.remove(*self.objects)

    def __del__(self):
        self.clear()


class SystemManager(SubSystem[SubSystem]):
    @staticmethod
    def accepts(obj: typing.Any) -> bool:
        return isinstance(obj, SubSystem)

    def get_objects_all(
        self, *types: typing.Type[ST]
    ) -> typing.Generator[ST, None, None]:
        seen: typing.Set[SubSystemObject] = set()
        for system in self.objects:
            for obj in system.get_objects(*types):
                if obj not in seen:
                    seen.add(obj)
                    yield obj

    def add_all(self, *objects: ST) -> typing.Iterable[ST]:
        for system in self.objects:
            system.add(*[obj for obj in objects if system.accepts(obj)])
        return objects

    def remove_all(self, *objects: ST) -> typing.Iterable[ST]:
        for system in self.objects:
            system.remove(*[obj for obj in objects if system.accepts(obj)])
        return objects

    def remove_queued_all(self) -> typing.Iterable[SubSystemObject]:
        all_objects: typing.Set[SubSystemObject] = set()
        for system in self.objects:
            all_objects.update(system.remove_queued())
        return all_objects

    def clear_all(self) -> typing.Iterable[SubSystemObject]:
        all_objects: typing.Set[SubSystemObject] = set()
        for system in self.objects:
            all_objects.update(system.clear())
        return all_objects
