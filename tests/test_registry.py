"""
Tests for model registry.
"""

import pytest
from dataclasses import dataclass

from redis_json_serializer import register_model, ModelRegistry
from redis_json_serializer.registry import (
    REGISTERED_MODELS,
    MODEL_ALIASES,
    SerializationSecurityError,
    RegistrationError,
)

try:
    from pydantic import BaseModel
except ImportError:
    pytest.skip("Pydantic not installed", allow_module_level=True)
    BaseModel = None


class TestRegisterModel:
    """Test @register_model decorator."""
    
    def test_register_with_alias(self):
        """Test registering a model with a custom alias."""
        @register_model("test.user.v1")
        class User(BaseModel):
            id: str
            name: str
        
        assert "test.user.v1" in REGISTERED_MODELS
        assert REGISTERED_MODELS["test.user.v1"] is User
        assert MODEL_ALIASES[User] == "test.user.v1"
    
    def test_register_without_alias(self):
        """Test registering a model without alias (uses module.qualname)."""
        @register_model()
        class Product(BaseModel):
            id: str
            name: str
        
        # Должен использоваться module.qualname
        model_key = f"{Product.__module__}.{Product.__qualname__}"
        assert model_key in REGISTERED_MODELS
        assert REGISTERED_MODELS[model_key] is Product
        assert MODEL_ALIASES[Product] == model_key
    
    def test_duplicate_alias_raises(self):
        """Test that duplicate alias raises RegistrationError."""
        @register_model("test.duplicate")
        class Model1(BaseModel):
            id: str
        
        # Попытка зарегистрировать другой класс с тем же алиасом должна вызвать RegistrationError
        with pytest.raises(RegistrationError, match="Duplicate alias"):
            @register_model("test.duplicate")
            class Model2(BaseModel):
                id: str
    
    def test_duplicate_registration_raises_error(self):
        """Test that duplicate registration raises RegistrationError."""
        @register_model("test.duplicate.reg")
        class Model1(BaseModel):
            id: str
        
        # Повторная регистрация того же класса должна вызвать RegistrationError
        with pytest.raises(RegistrationError, match="already registered"):
            register_model("test.duplicate.reg")(Model1)
    
    def test_register_dataclass(self):
        """Test registering a dataclass."""
        @register_model("test.item.v1")
        @dataclass
        class Item:
            id: str
            name: str
        
        assert "test.item.v1" in REGISTERED_MODELS
        assert REGISTERED_MODELS["test.item.v1"] is Item
        assert MODEL_ALIASES[Item] == "test.item.v1"
    
    def test_register_non_model_raises(self):
        """Test that registering a non-model class raises TypeError."""
        with pytest.raises(TypeError, match="must be Pydantic BaseModel or dataclass"):
            @register_model("test.invalid")
            class InvalidClass:
                pass


class TestModelRegistry:
    """Test ModelRegistry class."""
    
    def test_register_and_get(self, registry):
        """Test registering and getting a model."""
        @dataclass
        class TestModel:
            id: str
        
        registered = registry.register(TestModel, "test.model.v1")
        assert registered is TestModel
        
        retrieved = registry.get("test.model.v1")
        assert retrieved is TestModel
    
    def test_get_nonexistent(self, registry):
        """Test getting a non-existent model returns None."""
        result = registry.get("nonexistent.key")
        assert result is None
    
    def test_get_alias(self, registry):
        """Test getting alias for a registered model."""
        @register_model("test.alias.v1")
        class AliasModel(BaseModel):
            id: str
        
        alias = registry.get_alias(AliasModel)
        assert alias == "test.alias.v1"
    
    def test_get_alias_unregistered(self, registry):
        """Test getting alias for unregistered model returns None."""
        class UnregisteredModel(BaseModel):
            id: str
        
        alias = registry.get_alias(UnregisteredModel)
        assert alias is None
    
    def test_is_registered(self, registry):
        """Test checking if a model is registered."""
        @register_model("test.registered.v1")
        class RegisteredModel(BaseModel):
            id: str
        
        class UnregisteredModel(BaseModel):
            id: str
        
        assert registry.is_registered(RegisteredModel) is True
        assert registry.is_registered(UnregisteredModel) is False
