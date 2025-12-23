"""
Model registry for safe deserialization.

TODO: Реализовать команде разработки
"""

import dataclasses
import warnings
from typing import Type, TypeVar, Callable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import BaseModel
else:
    try:
        from pydantic import BaseModel
    except ImportError:
        BaseModel = None  # type: ignore[assignment, misc]


T = TypeVar("T")


class SerializationSecurityError(Exception):
    """Base error for serialization security issues."""
    pass


class RegistrationError(SerializationSecurityError):
    """Error raised when trying to deserialize unregistered model."""
    pass


REGISTERED_MODELS: dict[str, type[Any]] = {}
MODEL_ALIASES: dict[type[Any], str] = {}  # O(1) lookup: {Type: alias}


def get_key_model(cls: type[Any], alias: str | None = None) -> str:
    """
    Generate model key for registration.
    
    Args:
        cls: Model class
        alias: Optional stable alias (recommended for production)
        
    Returns:
        Model key string
        
    Examples:
        # With alias:
        get_key_model(User, "user.v1") -> "user.v1"
        
        # Without alias (fallback):
        get_key_model(User) -> "myapp.models.User"
    """
    if alias:
        return alias
    
    # Fallback: use module.qualname for stable identification
    module = getattr(cls, "__module__", "")
    qualname = getattr(cls, "__qualname__", getattr(cls, "__name__", ""))
    return f"{module}.{qualname}"


def register_model(alias: str | None = None) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator for registering Pydantic models and dataclasses.
    
    Args:
        alias: Optional stable alias for the model (recommended for production).
               If not provided, uses class name and module path.
    
    Example:
        @register_model("user.v1")
        class User(BaseModel):
            id: str
            name: str
    
    Raises:
        TypeError: If model is not Pydantic BaseModel or dataclass
        RegistrationError: If alias is already registered for a different class or model is already registered
    """
    def decorator(cls: Type[T]) -> Type[T]:
        # Проверка типа
        is_pydantic = False
        if BaseModel is not None:
            try:
                is_pydantic = issubclass(cls, BaseModel)
            except (TypeError, AttributeError):
                # cls не является классом или BaseModel не определен
                pass
        
        is_dataclass = dataclasses.is_dataclass(cls)
        
        if not (is_pydantic or is_dataclass):
            cls_name = getattr(cls, '__name__', getattr(cls, '__qualname__', str(cls)))
            raise TypeError(
                f"Model must be Pydantic BaseModel or dataclass, got {cls_name}"
            )
        
        # Генерация ключа
        model_key = get_key_model(cls, alias)
        
        # Проверка дубликатов
        if model_key in REGISTERED_MODELS:
            existing_cls = REGISTERED_MODELS[model_key]
            if existing_cls is cls:
                # Строгий режим: повторная регистрация не допускается
                raise RegistrationError(
                    f"Model {cls} already registered with key '{model_key}'. "
                    "Duplicate registration is not allowed."
                )
            else:
                # Конфликт алиаса с другим классом - тоже RegistrationError для консистентности
                raise RegistrationError(
                    f"Duplicate alias '{model_key}': already registered for {existing_cls}, "
                    f"cannot register {cls}"
                )
        
        # Регистрация
        REGISTERED_MODELS[model_key] = cls
        MODEL_ALIASES[cls] = model_key  # O(1) lookup
        
        return cls
    
    return decorator


class ModelRegistry:
    """
    Registry for managing model registration.
    
    Can be used as an alternative to the decorator approach.
    Uses the same global dictionaries (REGISTERED_MODELS and MODEL_ALIASES)
    as the @register_model decorator.
    
    Example:
        registry = ModelRegistry()
        registry.register(User, "user.v1")
        user_class = registry.get("user.v1")
        alias = registry.get_alias(User)
    """
    
    def __init__(self) -> None:
        """Initialize registry instance."""
        pass
    
    def register(self, cls: Type[T], alias: str | None = None) -> Type[T]:
        """
        Register a model class.
        
        Uses the same registration logic as @register_model decorator.
        
        Args:
            cls: Model class to register
            alias: Optional stable alias
            
        Returns:
            The registered class
            
        Raises:
            TypeError: If model is not Pydantic BaseModel or dataclass
            RegistrationError: If alias is already registered for a different class or model is already registered
        """
        # Использовать тот же декоратор для консистентности
        return register_model(alias)(cls)
    
    def get(self, key: str) -> type[Any] | None:
        """
        Get model by key.
        
        Args:
            key: Model key (alias or module.qualname)
            
        Returns:
            Model class or None if not found
        """
        return REGISTERED_MODELS.get(key)
    
    def get_alias(self, cls: type[Any]) -> str | None:
        """
        Get alias for model class.
        
        Args:
            cls: Model class
            
        Returns:
            Model alias/key or None if not registered
        """
        return MODEL_ALIASES.get(cls)
    
    def is_registered(self, cls: type[Any]) -> bool:
        """
        Check if model is registered.
        
        Args:
            cls: Model class to check
            
        Returns:
            True if model is registered, False otherwise
        """
        return cls in MODEL_ALIASES


# Global registry instance
registry = ModelRegistry()
