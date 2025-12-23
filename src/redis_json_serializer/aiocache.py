"""
Integration with aiocache library.

TODO: Реализовать команде разработки
"""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from aiocache.serializers import BaseSerializer  # type: ignore[import-untyped]
    from .serializer import JsonSerializer
else:
    try:
        from aiocache.serializers import BaseSerializer  # type: ignore[import-untyped]
    except ImportError:
        BaseSerializer = None  # type: ignore[assignment, misc]
    
    # Импортируем JsonSerializer на уровне модуля для правильной работы с глобальными словарями
    try:
        from .serializer import JsonSerializer
    except ImportError:
        JsonSerializer = None  # type: ignore[assignment, misc]


if BaseSerializer is not None:
    class AiocacheJsonSerializer(BaseSerializer):  # type: ignore[misc]
        """
        aiocache serializer adapter using JsonSerializer.
        
        This class provides integration with aiocache library by implementing
        the BaseSerializer interface and delegating to JsonSerializer.
        """
        
        DEFAULT_ENCODING = None
        
        def __init__(self, namespace: str = ""):
            """
            Initialize serializer.
            
            Args:
                namespace: Optional namespace prefix for cache keys
            """
            super().__init__()
            if JsonSerializer is None:
                raise ImportError("JsonSerializer is not available")
            self._serializer = JsonSerializer(namespace=namespace)
        
        def dumps(self, value: Any) -> bytes:
            """
            Serialize value to bytes.
            
            Args:
                value: Python object to serialize
                
            Returns:
                Serialized bytes
            """
            return self._serializer.dumps(value)
        
        def loads(self, value: bytes | None) -> Any:
            """
            Deserialize bytes to value.
            
            Args:
                value: Serialized bytes (or None)
                
            Returns:
                Deserialized Python object (or None)
            """
            return self._serializer.loads(value)
