"""Tests for SubSystem classes."""

from gamepart.subsystem import SubSystem, SubSystemObject, SystemManager


class TestSubSystemObject:
    """Test SubSystemObject base class."""

    def test_initialization(self):
        """Test SubSystemObject initialization."""
        obj = SubSystemObject()
        assert obj._not_removed is True
        assert bool(obj) is True

    def test_remove(self):
        """Test removing an object."""
        obj = SubSystemObject()
        obj.remove()
        assert obj._not_removed is False
        assert bool(obj) is False


class TestSubSystem:
    """Test SubSystem class."""

    def test_initialization(self):
        """Test SubSystem initialization."""
        system = SubSystem()
        assert len(system.objects) == 0

    def test_add_object(self):
        """Test adding an object to system."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj = TestObject("test")
        system.add(obj)
        assert len(system.objects) == 1
        assert system.objects[0] == obj

    def test_add_multiple_objects(self):
        """Test adding multiple objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

        class TestSubSystem(SubSystem[TestObject]):
            pass

        system = TestSubSystem()
        obj1 = TestObject("test1")
        obj2 = TestObject("test2")
        system.add(obj1, obj2)
        assert len(system.objects) == 2

    def test_remove_object(self):
        """Test removing an object from system."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
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

    def test_get_objects_by_type(self):
        """Test getting objects by type."""

        class TestObject1(SubSystemObject):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

        class TestObject2(SubSystemObject):
            def __init__(self, name: str):
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

    def test_remove_queued(self):
        """Test removing queued objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
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

    def test_clear(self):
        """Test clearing all objects."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
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

    def test_initialization(self):
        """Test SystemManager initialization."""
        manager = SystemManager()
        assert len(manager.objects) == 0

    def test_add_system(self):
        """Test adding a system to manager."""

        class TestSystem(SubSystem[SubSystemObject]):
            pass

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)
        assert len(manager.objects) == 1

    def test_add_all_objects(self):
        """Test adding objects to all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj):
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)

        obj = TestObject("test")
        manager.add_all(obj)
        assert obj in system.objects

    def test_remove_all_objects(self):
        """Test removing objects from all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj):
                return isinstance(obj, TestObject)

        manager = SystemManager()
        system = TestSystem()
        manager.add(system)

        obj = TestObject("test")
        system.add(obj)
        manager.remove_all(obj)
        assert obj not in system.objects

    def test_get_objects_all(self):
        """Test getting objects from all systems."""

        class TestObject(SubSystemObject):
            def __init__(self, name: str):
                super().__init__()
                self.name = name

        class TestSystem(SubSystem[TestObject]):
            @staticmethod
            def accepts(obj):
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
