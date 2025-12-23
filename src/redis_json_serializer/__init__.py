"""
Redis JSON Serializer - Fast and secure JSON serialization for Redis caching.

This package provides a high-performance JSON serializer built on orjson
with support for Pydantic models, dataclasses, and custom types.
"""

from .registry import ModelRegistry, register_model
from .serializer import JsonSerializer

# Условный экспорт AiocacheJsonSerializer (только если aiocache установлен)
try:
    from .aiocache import AiocacheJsonSerializer
except ImportError:
    AiocacheJsonSerializer = None  # type: ignore

__version__ = "0.1.0"
__all__ = [
    "JsonSerializer",
    "register_model",
    "ModelRegistry",
]

# Добавляем AiocacheJsonSerializer в __all__ только если он доступен
if AiocacheJsonSerializer is not None:
    __all__.append("AiocacheJsonSerializer")
