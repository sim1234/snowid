"""Tests for Protocol metaclass and base class."""

from gamepart.protocol import Protocol, ProtocolMeta


class TestProtocolMeta:
    """Test ProtocolMeta metaclass behavior."""

    def test_creates_slots_from_class_attributes(self) -> None:
        """Test that class attributes become slots."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        assert "__slots__" in dir(TestProtocol)
        assert "field_a" in TestProtocol.__slots__
        assert "field_b" in TestProtocol.__slots__

    def test_creates_defaults_tuple(self) -> None:
        """Test that defaults are stored as tuple."""

        class TestProtocol(Protocol):
            field_a = 10
            field_b = "default"

        assert hasattr(TestProtocol, "_defaults")
        defaults_dict = dict(TestProtocol._defaults)
        assert defaults_dict["field_a"] == 10
        assert defaults_dict["field_b"] == "default"

    def test_creates_keys_tuple(self) -> None:
        """Test that keys are stored as tuple."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        assert hasattr(TestProtocol, "_keys")
        assert "field_a" in TestProtocol._keys
        assert "field_b" in TestProtocol._keys

    def test_inherits_parent_defaults(self) -> None:
        """Test that child classes inherit parent defaults."""

        class ParentProtocol(Protocol):
            parent_field = 1

        class ChildProtocol(ParentProtocol):
            child_field = 2

        defaults_dict = dict(ChildProtocol._defaults)
        assert "parent_field" in defaults_dict
        assert "child_field" in defaults_dict
        assert defaults_dict["parent_field"] == 1
        assert defaults_dict["child_field"] == 2

    def test_excludes_callables(self) -> None:
        """Test that methods are not treated as fields."""

        class TestProtocol(Protocol):
            field_a = 0

            def some_method(self) -> None:
                pass

        assert "some_method" not in TestProtocol.__slots__
        assert "some_method" not in TestProtocol._keys

    def test_excludes_private_attributes(self) -> None:
        """Test that private attributes are not treated as fields."""

        class TestProtocol(Protocol):
            field_a = 0
            _private = 1

        assert "_private" not in TestProtocol.__slots__
        assert "_private" not in TestProtocol._keys

    def test_excludes_classmethods(self) -> None:
        """Test that classmethods are not treated as fields."""

        class TestProtocol(Protocol):
            field_a = 0

            @classmethod
            def class_method(cls) -> None:
                pass

        assert "class_method" not in TestProtocol.__slots__

    def test_is_field_with_callable(self) -> None:
        """Test is_field returns False for callables."""
        assert ProtocolMeta.is_field("method", lambda: None) is False

    def test_is_field_with_private(self) -> None:
        """Test is_field returns False for private names."""
        assert ProtocolMeta.is_field("_private", 42) is False

    def test_is_field_with_classmethod(self) -> None:
        """Test is_field returns False for classmethods."""
        assert ProtocolMeta.is_field("method", classmethod(lambda cls: None)) is False

    def test_is_field_with_valid_field(self) -> None:
        """Test is_field returns True for valid fields."""
        assert ProtocolMeta.is_field("field", 42) is True
        assert ProtocolMeta.is_field("name", "value") is True


class TestProtocolInit:
    """Test Protocol initialization."""

    def test_init_sets_defaults(self) -> None:
        """Test that __init__ sets default values."""

        class TestProtocol(Protocol):
            field_a = 10
            field_b = "hello"

        proto = TestProtocol()
        assert proto.field_a == 10
        assert proto.field_b == "hello"

    def test_init_empty_protocol(self) -> None:
        """Test initializing protocol with no fields."""

        class EmptyProtocol(Protocol):
            pass

        proto = EmptyProtocol()
        assert proto._keys == ()


class TestProtocolClear:
    """Test Protocol.clear method."""

    def test_clear_resets_to_defaults(self) -> None:
        """Test clear resets all fields to defaults."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol()
        proto.field_a = 100
        proto.field_b = "modified"
        proto.clear()
        assert proto.field_a == 0
        assert proto.field_b == ""


class TestProtocolUpdate:
    """Test Protocol.update methods."""

    def test_update_from_iterable(self) -> None:
        """Test update from iterable."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol()
        proto.update([42, "updated"])
        assert proto.field_a == 42
        assert proto.field_b == "updated"

    def test_update_dict(self) -> None:
        """Test update from dictionary."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol()
        proto.update_dict({"field_a": 99, "field_b": "dict_update"})
        assert proto.field_a == 99
        assert proto.field_b == "dict_update"

    def test_update_dict_partial(self) -> None:
        """Test partial update from dictionary."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol()
        proto.update_dict({"field_a": 77})
        assert proto.field_a == 77
        assert proto.field_b == ""


class TestProtocolSerialize:
    """Test Protocol serialization methods."""

    def test_serialize_returns_list(self) -> None:
        """Test serialize returns list of values."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol()
        proto.field_a = 5
        proto.field_b = "test"
        result = proto.serialize()
        assert isinstance(result, list)
        assert 5 in result
        assert "test" in result

    def test_serialize_dict_returns_dict(self) -> None:
        """Test serialize_dict returns dictionary."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol()
        proto.field_a = 5
        proto.field_b = "test"
        result = proto.serialize_dict()
        assert result == {"field_a": 5, "field_b": "test"}

    def test_serialize_uses_defaults_for_missing(self) -> None:
        """Test serialize uses defaults for unset attributes."""

        class TestProtocol(Protocol):
            field_a = 42

        proto = TestProtocol()
        result = proto.serialize()
        assert result == [42]


class TestProtocolDeserialize:
    """Test Protocol deserialization methods."""

    def test_deserialize_from_list(self) -> None:
        """Test deserialize creates instance from list."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol.deserialize([100, "loaded"])
        assert getattr(proto, "field_a") == 100
        assert getattr(proto, "field_b") == "loaded"

    def test_deserialize_dict_from_dict(self) -> None:
        """Test deserialize_dict creates instance from dictionary."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        proto = TestProtocol.deserialize_dict({"field_a": 200, "field_b": "from_dict"})
        assert getattr(proto, "field_a") == 200
        assert getattr(proto, "field_b") == "from_dict"


class TestProtocolCopy:
    """Test Protocol.copy method."""

    def test_copy_copies_all_fields(self) -> None:
        """Test copy copies all fields from source."""

        class TestProtocol(Protocol):
            field_a = 0
            field_b = ""

        source = TestProtocol()
        source.field_a = 50
        source.field_b = "source"

        target = TestProtocol()
        target.copy(source)
        assert target.field_a == 50
        assert target.field_b == "source"

    def test_copy_uses_defaults_for_missing(self) -> None:
        """Test copy uses defaults if source lacks attribute."""

        class TestProtocol(Protocol):
            field_a = 99

        source = TestProtocol()
        target = TestProtocol()
        target.field_a = 1
        target.copy(source)
        assert target.field_a == 99


class TestProtocolRepr:
    """Test Protocol.__repr__ method."""

    def test_repr_includes_class_name(self) -> None:
        """Test repr includes class name."""

        class TestProtocol(Protocol):
            field_a = 0

        proto = TestProtocol()
        result = repr(proto)
        assert "TestProtocol" in result

    def test_repr_includes_serialized_dict(self) -> None:
        """Test repr includes serialized data."""

        class TestProtocol(Protocol):
            field_a = 0

        proto = TestProtocol()
        proto.field_a = 123
        result = repr(proto)
        assert "field_a" in result
        assert "123" in result


class TestProtocolInheritance:
    """Test Protocol inheritance behavior."""

    def test_child_inherits_parent_fields(self) -> None:
        """Test child protocol has parent fields."""

        class ParentProtocol(Protocol):
            parent_field = "parent"

        class ChildProtocol(ParentProtocol):
            child_field = "child"

        proto = ChildProtocol()
        assert proto.parent_field == "parent"
        assert proto.child_field == "child"

    def test_child_can_override_parent_defaults(self) -> None:
        """Test child can serialize/deserialize both parent and child fields."""

        class ParentProtocol(Protocol):
            field_a = 1

        class ChildProtocol(ParentProtocol):
            field_b = 2

        proto = ChildProtocol()
        proto.field_a = 10
        proto.field_b = 20
        serialized = proto.serialize_dict()
        assert serialized["field_a"] == 10
        assert serialized["field_b"] == 20

    def test_multiple_inheritance_levels(self) -> None:
        """Test protocol with multiple inheritance levels."""

        class Level1(Protocol):
            field_1 = 1

        class Level2(Level1):
            field_2 = 2

        class Level3(Level2):
            field_3 = 3

        proto = Level3()
        assert proto.field_1 == 1
        assert proto.field_2 == 2
        assert proto.field_3 == 3
        assert len(proto._defaults) == 3
