"""
Pytest configuration and shared fixtures for redis-json-serializer tests.
"""

import datetime
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import pytest

from redis_json_serializer import JsonSerializer, ModelRegistry, register_model
from redis_json_serializer.registry import MODEL_ALIASES, REGISTERED_MODELS

try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None

try:
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    ObjectId = None


@pytest.fixture
def serializer():
    """Create a JsonSerializer instance without namespace."""
    return JsonSerializer()


@pytest.fixture
def serializer_with_namespace():
    """Create a JsonSerializer instance with namespace."""
    return JsonSerializer(namespace="test:v1")


@pytest.fixture(autouse=True)
def clear_registry():
    """
    Automatically clear model registry before and after each test.

    This ensures tests don't interfere with each other.
    """
    # Clear before test
    REGISTERED_MODELS.clear()
    MODEL_ALIASES.clear()

    yield

    # Clear after test
    REGISTERED_MODELS.clear()
    MODEL_ALIASES.clear()


@pytest.fixture
def registry():
    """Create a fresh ModelRegistry instance."""
    return ModelRegistry()


# Pydantic model fixtures
if PYDANTIC_AVAILABLE:
    @pytest.fixture
    def sample_pydantic_model():
        """Create a sample Pydantic model for testing."""
        @register_model("test.user.v1")
        class User(BaseModel):
            id: str
            name: str
            email: str
            age: int | None = None

        return User

    @pytest.fixture
    def unregistered_pydantic_model():
        """Create an unregistered Pydantic model for testing."""
        class UnregisteredUser(BaseModel):
            id: str
            name: str

        return UnregisteredUser

    @pytest.fixture
    def complex_pydantic_model():
        """Create a complex Pydantic model with nested data."""
        @register_model("test.product.v1")
        class Product(BaseModel):
            id: str
            name: str
            price: Decimal
            created_at: datetime.datetime
            tags: list[str]
            metadata: dict[str, Any]

        return Product


# Dataclass fixtures
@pytest.fixture
def sample_dataclass():
    """Create a sample dataclass for testing."""
    @register_model("test.item.v1")
    @dataclass
    class Item:
        id: str
        name: str
        quantity: int
        price: Decimal

    return Item


@pytest.fixture
def unregistered_dataclass():
    """Create an unregistered dataclass for testing."""
    @dataclass
    class UnregisteredItem:
        id: str
        name: str

    return UnregisteredItem


# Data fixtures
@pytest.fixture
def sample_datetime():
    """Sample datetime for testing."""
    return datetime.datetime(2024, 12, 23, 10, 30, 45, 123456)


@pytest.fixture
def sample_date():
    """Sample date for testing."""
    return datetime.date(2024, 12, 23)


@pytest.fixture
def sample_decimal():
    """Sample Decimal for testing."""
    return Decimal("123.456789")


@pytest.fixture
def sample_set():
    """Sample set for testing."""
    return {1, 2, 3, "a", "b", "c"}


@pytest.fixture
def sample_list():
    """Sample list for testing."""
    return [1, 2, 3, "a", "b", "c", None, True, False]


@pytest.fixture
def sample_dict():
    """Sample dict for testing."""
    return {
        "string": "value",
        "int": 42,
        "float": 3.14,
        "bool": True,
        "none": None,
        "list": [1, 2, 3],
        "nested": {"key": "value"},
    }


@pytest.fixture
def sample_tuple():
    """Sample tuple for testing."""
    return (1, 2, 3, "a", "b")


if PYMONGO_AVAILABLE:
    @pytest.fixture
    def sample_object_id():
        """Sample ObjectId for testing."""
        return ObjectId()


# Complex nested data fixtures
@pytest.fixture
def complex_nested_data():
    """Complex nested data structure for testing."""
    return {
        "users": [
            {"id": "1", "name": "Alice", "age": 30},
            {"id": "2", "name": "Bob", "age": 25},
        ],
        "metadata": {
            "created_at": "2024-12-23T10:30:00",
            "tags": ["tag1", "tag2"],
            "counts": [10, 20, 30],
        },
        "settings": {
            "enabled": True,
            "threshold": 0.95,
        },
    }


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "requires_pydantic: mark test as requiring Pydantic to be installed",
    )
    config.addinivalue_line(
        "markers",
        "requires_pymongo: mark test as requiring pymongo to be installed",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running",
    )


# Skip tests if dependencies are missing
def pytest_collection_modifyitems(config, items):
    """Skip tests that require missing dependencies."""
    skip_pydantic = pytest.mark.skip(reason="Pydantic not installed")
    skip_pymongo = pytest.mark.skip(reason="pymongo not installed")

    for item in items:
        if "requires_pydantic" in item.keywords and not PYDANTIC_AVAILABLE:
            item.add_marker(skip_pydantic)
        if "requires_pymongo" in item.keywords and not PYMONGO_AVAILABLE:
            item.add_marker(skip_pymongo)




