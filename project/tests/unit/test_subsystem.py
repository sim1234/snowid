"""Tests for SubSystem classes."""

import typing

from gamepart.subsystem import SubSystem, SubSystemObject, SystemManager


class TestSubSystemObject:
    """Test SubSystemObject base class."""

    def test_initialization(self) -> None:
        """Test SubSystemObject initialization."""
        obj = SubSystemObject()
        assert obj._not_removed is True
        assert bool(obj) is True

    def test_remove(self) -> None:
        """Test removing an object."""
        obj = SubSystemObject()
        obj.remove()
        assert obj._not_removed is False
        assert bool(obj) is False


class TestSubSystem:
    """Test SubSystem class."""

    def test_initialization(self) -> None:
        """Test SubSystem initialization."""
        system: SubSystem[typing.Any] = SubSystem()
        assert len(system.objects) == 0

    def test_add_object(self) -> None:
        """Test adding an object to system."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj = TestObject("test")
        system.add(obj)
        assert len(system.objects) == 1
        assert system.objects[0] == obj

    def test_add_multiple_objects(self) -> None:
        """Test adding multiple objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        system.add(obj1, obj2)
        assert len(system.objects) == 2

    def test_remove_object(self) -> None:
        """Test removing an object from system."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj = TestObject("test")
        system.add(obj)
        assert len(system.objects) == 1
        system.remove(obj)
        assert len(system.objects) == 0

    def test_get_objects_by_type(self) -> None:
        """Test getting objects by type."""

        class TestObject1(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestObject2(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[SubSystemObject]):
            pass

        system = TestSubSystem()
        obj1 = TestObject1("test1")
        obj2 = TestObject2("test2")
        obj3 = TestObject1("test3")
        system.add(obj1, obj2, obj3)

        objects = list(system.get_objects(TestObject1))
        assert len(objects) == 2
        assert obj1 in objects
        assert obj3 in objects
        assert obj2 not in objects

    def test_remove_queued(self) -> None:
        """Test removing queued objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        system.add(obj1, obj2)
        obj1.remove()  # Mark for removal
        removed = list(system.remove_queued())
        assert len(removed) == 1
        assert obj1 in removed
        assert len(system.objects) == 1
        assert obj2 in system.objects

    def test_clear(self) -> None:
        """Test clearing all objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        system.add(obj1, obj2)
        cleared = list(system.clear())
        assert len(cleared) == 2
        assert len(system.objects) == 0


class TestSystemManager:
    """Test SystemManager class."""

    def test_initialization(self) -> None:
        """Test SystemManager initialization."""
        manager = SystemManager()
        assert len(manager.objects) == 0

    def test_add_system(self) -> None:
        """Test adding a system to manager."""

        class TestSystem(SubSystem[SubSystemObject]):
            pass

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)
        assert len(manager.objects) == 1

    def test_add_all_objects(self) -> None:
        """Test adding objects to all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj: typing.Any) -> bool:
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)

        obj = TestObject("test")
        manager.add_all(obj)
        assert obj in system.objects

    def test_remove_all_objects(self) -> None:
        """Test removing objects from all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj: typing.Any) -> bool:
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)

        obj = TestObject("test")
        system.add(obj)
        manager.remove_all(obj)
        assert obj not in system.objects

    def test_get_objects_all(self) -> None:
        """Test getting objects from all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj: typing.Any) -> bool:
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system1 = TestSystem()
        system2 = TestSystem()
        manager.add(system1, system2)

        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        system1.add(obj1)
        system2.add(obj2)

        objects = list(manager.get_objects_all(TestObject))
        assert len(objects) == 2
        assert obj1 in objects
        assert obj2 in objects

    def test_remove_queued_all(self) -> None:
        """Test removing queued objects from all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj: typing.Any) -> bool:
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system1 = TestSystem()
        system2 = TestSystem()
        manager.add(system1, system2)

        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        obj3 = TestObject("test3")
        system1.add(obj1, obj2)
        system2.add(obj3)

        obj1.remove()
        obj3.remove()

        removed = manager.remove_queued_all()
        assert obj1 in removed
        assert obj3 in removed
        assert obj2 not in removed
        assert len(system1.objects) == 1
        assert obj2 in system1.objects
        assert len(system2.objects) == 0

    def test_remove_queued_all_empty_systems(self) -> None:
        """Test remove_queued_all with no queued objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj: typing.Any) -> bool:
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)

        obj = TestObject("test")
        system.add(obj)

        removed = set(manager.remove_queued_all())
        assert len(removed) == 0
        assert len(system.objects) == 1

    def test_clear_all(self) -> None:
        """Test clearing all objects from all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str) -> None:
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj: typing.Any) -> bool:
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system1 = TestSystem()
        system2 = TestSystem()
        manager.add(system1, system2)

        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        obj3 = TestObject("test3")
        system1.add(obj1, obj2)
        system2.add(obj3)

        cleared = manager.clear_all()
        assert obj1 in cleared
        assert obj2 in cleared
        assert obj3 in cleared
        assert len(system1.objects) == 0
        assert len(system2.objects) == 0

    def test_clear_all_empty_systems(self) -> None:
        """Test clear_all with empty systems."""

        class TestSystem(SubSystem[SubSystemObject]):
            pass

        manager = SystemManager()
        system1 = TestSystem()
        system2 = TestSystem()
        manager.add(system1, system2)

        cleared = set(manager.clear_all())
        assert len(cleared) == 0
