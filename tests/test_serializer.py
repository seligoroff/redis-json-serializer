"""
Basic tests for JsonSerializer.
"""

import datetime
from dataclasses import dataclass
from decimal import Decimal

import pytest

from redis_json_serializer import register_model
from redis_json_serializer.registry import RegistrationError
from redis_json_serializer.types import Marks

try:
    from pydantic import BaseModel
except ImportError:
    pytest.skip("Pydantic not installed", allow_module_level=True)
    BaseModel = None


class TestBasicTypes:
    """Test serialization of basic types."""

    def test_string(self, serializer):
        """Test string serialization."""
        packed = serializer.pack("hello")
        assert packed == "hello"
        unpacked = serializer.unpack(packed)
        assert unpacked == "hello"

    def test_int(self, serializer):
        """Test integer serialization."""
        packed = serializer.pack(42)
        assert packed == 42
        unpacked = serializer.unpack(packed)
        assert unpacked == 42

    def test_float(self, serializer):
        """Test float serialization."""
        packed = serializer.pack(3.14)
        assert packed == 3.14
        unpacked = serializer.unpack(packed)
        assert unpacked == 3.14

    def test_bool(self, serializer):
        """Test boolean serialization."""
        packed_true = serializer.pack(True)
        packed_false = serializer.pack(False)
        assert packed_true is True
        assert packed_false is False

        unpacked_true = serializer.unpack(packed_true)
        unpacked_false = serializer.unpack(packed_false)
        assert unpacked_true is True
        assert unpacked_false is False

    def test_none(self, serializer):
        """Test None serialization."""
        packed = serializer.pack(None)
        assert packed is None
        unpacked = serializer.unpack(packed)
        assert unpacked is None


class TestDatetime:
    """Test datetime serialization."""

    def test_datetime_pack_unpack(self, serializer, sample_datetime):
        """Test datetime serialization."""
        packed = serializer.pack(sample_datetime)
        assert isinstance(packed, dict)
        assert str(Marks.DATETIME) in packed

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, datetime.datetime)
        assert unpacked == sample_datetime

    def test_date_pack_unpack(self, serializer, sample_date):
        """Test date serialization."""
        packed = serializer.pack(sample_date)
        assert isinstance(packed, dict)
        assert str(Marks.DATE) in packed

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, datetime.date)
        assert unpacked == sample_date

    def test_no_aggressive_string_conversion(self, serializer):
        """Test that strings are not aggressively converted without expected_type."""
        # ISO datetime строка должна остаться строкой
        iso_string = "2024-12-23T10:30:00"
        packed = serializer.pack(iso_string)
        unpacked = serializer.unpack(packed)
        assert unpacked == iso_string
        assert isinstance(unpacked, str)
        assert not isinstance(unpacked, datetime.datetime)

    def test_string_conversion_with_expected_type(self, serializer):
        """Test that strings are converted only with expected_type."""
        iso_string = "2024-12-23T10:30:00"
        packed = serializer.pack(iso_string)

        # Без expected_type - остается строкой
        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, str)
        assert unpacked == iso_string

        # С expected_type - конвертируется
        unpacked = serializer.unpack(packed, expected_type=datetime.datetime)
        assert isinstance(unpacked, datetime.datetime)
        assert unpacked == datetime.datetime.fromisoformat(iso_string)


class TestDecimal:
    """Test Decimal serialization."""

    def test_decimal_pack_unpack(self, serializer, sample_decimal):
        """Test Decimal serialization."""
        packed = serializer.pack(sample_decimal)
        assert isinstance(packed, dict)
        assert str(Marks.DECIMAL) in packed

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, Decimal)
        assert unpacked == sample_decimal


class TestCollections:
    """Test collection serialization."""

    def test_list(self, serializer, sample_list):
        """Test list serialization."""
        packed = serializer.pack(sample_list)
        assert isinstance(packed, list)
        assert len(packed) == len(sample_list)

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, list)
        assert unpacked == sample_list

    def test_dict(self, serializer, sample_dict):
        """Test dict serialization."""
        packed = serializer.pack(sample_dict)
        assert isinstance(packed, dict)
        assert len(packed) == len(sample_dict)

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, dict)
        assert unpacked == sample_dict

    def test_set(self, serializer, sample_set):
        """Test set serialization."""
        packed = serializer.pack(sample_set)
        assert isinstance(packed, dict)
        assert str(Marks.SET) in packed

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, set)
        assert unpacked == sample_set

    def test_unpack_set_with_expected_type(self, serializer, sample_decimal):
        """Test unpacking set with expected type."""
        # Создаем set с Decimal (в виде строк)
        data = {str(Marks.SET): [str(sample_decimal), "123.456"]}

        # Без expected_type - элементы остаются строками
        unpacked = serializer.unpack(data)
        assert isinstance(unpacked, set)
        assert all(isinstance(x, str) for x in unpacked)

        # С expected_type=set[Decimal] - элементы конвертируются
        unpacked = serializer.unpack(data, expected_type=set[Decimal])
        assert isinstance(unpacked, set)
        assert all(isinstance(x, Decimal) for x in unpacked)
        assert Decimal("123.456") in unpacked
        assert sample_decimal in unpacked

    def test_unpack_set_with_datetime(self, serializer, sample_datetime):
        """Test unpacking set with datetime elements."""
        iso_string = sample_datetime.isoformat()
        data = {str(Marks.SET): [iso_string, "2024-01-01T00:00:00"]}

        unpacked = serializer.unpack(data, expected_type=set[datetime.datetime])
        assert isinstance(unpacked, set)
        assert all(isinstance(x, datetime.datetime) for x in unpacked)
        assert sample_datetime in unpacked
        assert datetime.datetime(2024, 1, 1, 0, 0, 0) in unpacked

    def test_tuple_preserves_type(self, serializer):
        """Test that tuple preserves its type during serialization."""
        data = (1, 2, 3, "a", "b")
        packed = serializer.pack(data)

        # Проверка маркера
        assert isinstance(packed, dict)
        assert str(Marks.TUPLE) in packed

        # Round-trip
        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, tuple)
        assert unpacked == data

    def test_tuple_with_nested_types(self, serializer, sample_decimal):
        """Test tuple with nested types."""
        data = (sample_decimal, "123.45", 42)
        packed = serializer.pack(data)
        unpacked = serializer.unpack(packed)

        assert isinstance(unpacked, tuple)
        assert isinstance(unpacked[0], Decimal)
        assert unpacked[1] == "123.45"
        assert unpacked[2] == 42
        assert unpacked == data


class TestPydanticModels:
    """Test Pydantic model serialization."""

    @pytest.mark.requires_pydantic
    def test_registered_model(self, serializer, sample_pydantic_model):
        """Test registered Pydantic model serialization."""
        user = sample_pydantic_model(id="123", name="Alice", email="alice@example.com", age=30)

        packed = serializer.pack(user)
        assert isinstance(packed, dict)
        assert str(Marks.MODEL) in packed

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, sample_pydantic_model)
        assert unpacked.id == "123"
        assert unpacked.name == "Alice"
        assert unpacked.email == "alice@example.com"
        assert unpacked.age == 30

    @pytest.mark.requires_pydantic
    def test_unregistered_model_raises(self, serializer, unregistered_pydantic_model):
        """Test that unregistered model raises RegistrationError."""
        user = unregistered_pydantic_model(id="123", name="Alice")

        with pytest.raises(RegistrationError, match="not registered"):
            serializer.pack(user)

    @pytest.mark.requires_pydantic
    def test_complex_pydantic_model(self, serializer, complex_pydantic_model, sample_decimal, sample_datetime):
        """Test complex Pydantic model with nested types."""
        product = complex_pydantic_model(
            id="prod-1",
            name="Test Product",
            price=sample_decimal,
            created_at=sample_datetime,
            tags=["tag1", "tag2"],
            metadata={"key": "value"}
        )

        packed = serializer.pack(product)
        unpacked = serializer.unpack(packed)

        assert isinstance(unpacked, complex_pydantic_model)
        assert unpacked.id == "prod-1"
        assert unpacked.name == "Test Product"
        assert isinstance(unpacked.price, Decimal)
        assert isinstance(unpacked.created_at, datetime.datetime)
        assert unpacked.tags == ["tag1", "tag2"]
        assert unpacked.metadata == {"key": "value"}

    @pytest.mark.requires_pydantic
    def test_nested_pydantic_preserves_markers(self, serializer):
        """Test that nested Pydantic model preserves MODEL markers."""
        @register_model("inner.v1")
        class Inner(BaseModel):
            value: int

        @register_model("outer.v1")
        class Outer(BaseModel):
            inner: Inner

        obj = Outer(inner=Inner(value=42))
        packed = serializer.pack(obj)

        # Проверка маркера для внешней модели
        assert str(Marks.MODEL) in packed
        assert packed[str(Marks.MODEL)] == "outer.v1"

        # Проверка маркера для вложенной модели
        assert str(Marks.MODEL) in packed["inner"]
        assert packed["inner"][str(Marks.MODEL)] == "inner.v1"

        # Round-trip
        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, Outer)
        assert isinstance(unpacked.inner, Inner)
        assert unpacked.inner.value == 42


class TestDataclass:
    """Test dataclass serialization."""

    def test_registered_dataclass(self, serializer, sample_dataclass, sample_decimal):
        """Test registered dataclass serialization."""
        item = sample_dataclass(id="item-1", name="Test Item", quantity=10, price=sample_decimal)

        packed = serializer.pack(item)
        assert isinstance(packed, dict)
        assert str(Marks.MODEL) in packed

        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, sample_dataclass)
        assert unpacked.id == "item-1"
        assert unpacked.name == "Test Item"
        assert unpacked.quantity == 10
        assert isinstance(unpacked.price, Decimal)

    def test_unregistered_dataclass_raises(self, serializer, unregistered_dataclass):
        """Test that unregistered dataclass raises RegistrationError."""
        item = unregistered_dataclass(id="123", name="Test")

        with pytest.raises(RegistrationError, match="not registered"):
            serializer.pack(item)

    def test_nested_dataclass_preserves_markers(self, serializer):
        """Test that nested dataclass preserves MODEL markers."""
        @register_model("inner.v1")
        @dataclass
        class Inner:
            value: int

        @register_model("outer.v1")
        @dataclass
        class Outer:
            inner: Inner

        obj = Outer(inner=Inner(value=42))
        packed = serializer.pack(obj)

        # Проверка маркера для внешней модели
        assert str(Marks.MODEL) in packed
        assert packed[str(Marks.MODEL)] == "outer.v1"

        # Проверка маркера для вложенной модели
        assert str(Marks.MODEL) in packed["inner"]
        assert packed["inner"][str(Marks.MODEL)] == "inner.v1"

        # Round-trip
        unpacked = serializer.unpack(packed)
        assert isinstance(unpacked, Outer)
        assert isinstance(unpacked.inner, Inner)
        assert unpacked.inner.value == 42


class TestErrorHandling:
    """Test error handling for unsupported types."""

    def test_pack_unsupported_type_raises_type_error(self, serializer):
        """Test that packing unsupported type raises TypeError."""
        class UnsupportedType:
            pass

        obj = UnsupportedType()

        with pytest.raises(TypeError, match="Unsupported type for packing"):
            serializer.pack(obj)

    def test_unpack_unsupported_type_raises_type_error(self, serializer):
        """Test that unpacking unsupported type raises TypeError."""
        class UnsupportedType:
            pass

        obj = UnsupportedType()

        # unpack() должен выбрасывать TypeError (не NotImplementedError)
        with pytest.raises(TypeError, match="Unsupported type for unpacking"):
            serializer.unpack(obj)


class TestRoundTrip:
    """Test round-trip serialization (dumps/loads)."""

    def test_basic_round_trip(self, serializer):
        """Test basic round-trip serialization."""
        data = {
            "string": "hello",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
        }

        serialized = serializer.dumps(data)
        assert isinstance(serialized, bytes)

        deserialized = serializer.loads(serialized)
        assert deserialized == data

    def test_complex_round_trip(self, serializer, sample_decimal, sample_datetime, sample_date, sample_set):
        """Test complex round-trip serialization."""
        data = {
            "decimal": sample_decimal,
            "datetime": sample_datetime,
            "date": sample_date,
            "set": sample_set,
            "list": [1, 2, 3],
            "nested": {
                "key": "value",
                "number": 42,
            },
        }

        serialized = serializer.dumps(data)
        deserialized = serializer.loads(serialized)

        assert isinstance(deserialized["decimal"], Decimal)
        assert deserialized["decimal"] == sample_decimal
        assert isinstance(deserialized["datetime"], datetime.datetime)
        assert deserialized["datetime"] == sample_datetime
        assert isinstance(deserialized["date"], datetime.date)
        assert deserialized["date"] == sample_date
        assert isinstance(deserialized["set"], set)
        assert deserialized["set"] == sample_set
        assert deserialized["list"] == [1, 2, 3]
        assert deserialized["nested"] == {"key": "value", "number": 42}

    def test_namespace_round_trip(self, serializer_with_namespace):
        """Test round-trip with namespace."""
        data = {"key": "value"}

        serialized = serializer_with_namespace.dumps(data)
        deserialized = serializer_with_namespace.loads(serialized)

        assert deserialized == data

    @pytest.mark.requires_pydantic
    def test_pydantic_round_trip(self, serializer, sample_pydantic_model):
        """Test round-trip with Pydantic model."""
        user = sample_pydantic_model(id="123", name="Alice", email="alice@example.com", age=30)

        serialized = serializer.dumps(user)
        deserialized = serializer.loads(serialized)

        assert isinstance(deserialized, sample_pydantic_model)
        assert deserialized.id == user.id
        assert deserialized.name == user.name
        assert deserialized.email == user.email
        assert deserialized.age == user.age
