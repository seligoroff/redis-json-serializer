"""
Type markers for serialization format.

Готово: Enum с маркерами типов (не требует реализации)
"""

import sys
from enum import Enum

# StrEnum доступен только в Python 3.11+
if sys.version_info >= (3, 11):
    from enum import StrEnum

    class Marks(StrEnum):
        """Type markers for non-JSON types in serialized format."""

        MODEL = "6c7372a7-e783-4f04-80d1-c0704d0e90e9"
        SET = "f3090927-571d-4687-991f-3c8cb061a355"
        DATE = "38213ce3-d72f-47a7-a499-7db04c9b6f20"
        DATETIME = "a7a58df1-0263-44a6-9799-563b7b3b6c2d"
        DECIMAL = "b0648f86-d983-424a-8743-9828c2ff9f6b"
        OBJECT_ID = "c5c64f69-2a90-4c7b-914a-1a0e8d0e5f2a"
        TUPLE = "d7e4f5a6-3b7c-4d8e-9f0a-1b2c3d4e5f6a"
else:
    # Fallback для Python 3.10
    class Marks(str, Enum):
        """Type markers for non-JSON types in serialized format."""

        MODEL = "6c7372a7-e783-4f04-80d1-c0704d0e90e9"
        SET = "f3090927-571d-4687-991f-3c8cb061a355"
        DATE = "38213ce3-d72f-47a7-a499-7db04c9b6f20"
        DATETIME = "a7a58df1-0263-44a6-9799-563b7b3b6c2d"
        DECIMAL = "b0648f86-d983-424a-8743-9828c2ff9f6b"
        OBJECT_ID = "c5c64f69-2a90-4c7b-914a-1a0e8d0e5f2a"
        TUPLE = "d7e4f5a6-3b7c-4d8e-9f0a-1b2c3d4e5f6a"

        def __str__(self) -> str:
            return self.value


# Константы для namespace-обёртки
NS_KEY = "$ns"
DATA_KEY = "$data"
