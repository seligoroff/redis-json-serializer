"""
Main serializer implementation using dispatch tables for O(1) type lookup.

TODO: Реализовать команде разработки
"""

from __future__ import annotations

import dataclasses
import datetime
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING, Any, get_args, get_origin

from redis_json_serializer.types import DATA_KEY, NS_KEY, Marks

from .registry import MODEL_ALIASES, RegistrationError

# Условные импорты для опциональных зависимостей
if TYPE_CHECKING:
    from bson import ObjectId  # type: ignore[import-not-found]
    from fastapi import Response  # type: ignore[import-not-found]
    from pydantic import BaseModel
else:
    try:
        from bson import ObjectId  # type: ignore[import-not-found]
    except ImportError:
        ObjectId = None  # type: ignore[assignment, misc]

    try:
        from fastapi import Response  # type: ignore[import-not-found]
    except ImportError:
        Response = None  # type: ignore[assignment, misc]

    try:
        from pydantic import BaseModel
    except ImportError:
        BaseModel = None  # type: ignore[assignment, misc]


class JsonSerializer:
    """
    Fast JSON serializer using dispatch tables for O(1) type lookup.

    TODO: Реализовать команде разработки на основе:
    - comparison_report.md (критические исправления)
    - DEVELOPMENT.md (архитектурные решения)
    """

    def __init__(self, namespace: str = ""):
        """
        Initialize serializer.

        Args:
            namespace: Optional namespace prefix for cache keys (e.g., "cache:v2:")
        """
        self.namespace = namespace

        # Dispatch-таблица для pack() - O(1) поиск обработчика по типу
        self._pack_handlers: dict[type[Any], Callable[[Any], Any]] = {
            datetime.datetime: self._pack_datetime,
            datetime.date: self._pack_date,
            Decimal: self._pack_decimal,
            set: self._pack_set,
        }

        # Условно добавляем ObjectId если pymongo установлен
        if ObjectId is not None:
            self._pack_handlers[ObjectId] = self._pack_object_id

        # Dispatch-таблица для unpack() - O(1) поиск обработчика по маркеру
        # Используем строковые ключи для совместимости с JSON
        # Обработчики принимают expected_type для поддержки generic типов (set[Type], etc.)
        self._unpack_handlers: dict[str, Callable[[dict[str, Any], type[Any] | None], Any]] = {
            str(Marks.DATE): self._unpack_date,
            str(Marks.DATETIME): self._unpack_datetime,
            str(Marks.DECIMAL): self._unpack_decimal,
            str(Marks.OBJECT_ID): self._unpack_object_id,
            str(Marks.SET): self._unpack_set,
            str(Marks.TUPLE): self._unpack_tuple,
        }

    # ========== Pack handlers (для dispatch-таблицы) ==========

    def _pack_datetime(self, obj: datetime.datetime) -> dict[str, Any]:
        """Pack datetime to dict with marker."""
        return {str(Marks.DATETIME): obj.isoformat()}

    def _pack_date(self, obj: datetime.date) -> dict[str, Any]:
        """Pack date to dict with marker."""
        return {str(Marks.DATE): obj.isoformat()}

    def _pack_decimal(self, obj: Decimal) -> dict[str, Any]:
        """Pack Decimal to dict with marker."""
        return {str(Marks.DECIMAL): str(obj)}

    def _pack_set(self, obj: set[Any]) -> dict[str, Any]:
        """Pack set to dict with marker and list of packed items."""
        return {str(Marks.SET): [self.pack(item) for item in obj]}

    def _pack_object_id(self, obj: Any) -> dict[str, Any]:
        """Pack ObjectId to dict with marker."""
        return {str(Marks.OBJECT_ID): str(obj)}

    # ========== Unpack handlers (для dispatch-таблицы) ==========

    def _unpack_datetime(self, obj: dict[str, Any], expected_type: type[Any] | None = None) -> datetime.datetime:
        """Unpack datetime from dict with marker."""
        # expected_type игнорируется для datetime (тип уже определен маркером)
        return datetime.datetime.fromisoformat(obj[str(Marks.DATETIME)])

    def _unpack_date(self, obj: dict[str, Any], expected_type: type[Any] | None = None) -> datetime.date:
        """Unpack date from dict with marker."""
        # expected_type игнорируется для date (тип уже определен маркером)
        return datetime.date.fromisoformat(obj[str(Marks.DATE)])

    def _unpack_decimal(self, obj: dict[str, Any], expected_type: type[Any] | None = None) -> Decimal:
        """Unpack Decimal from dict with marker."""
        # expected_type игнорируется для Decimal (тип уже определен маркером)
        return Decimal(obj[str(Marks.DECIMAL)])

    def _unpack_set(self, obj: dict[str, Any], expected_type: type[Any] | None = None) -> set[Any]:
        """Unpack set from dict with marker."""
        elem_type = None
        if expected_type:
            origin = get_origin(expected_type)
            if origin is set:
                args = get_args(expected_type)
                elem_type = args[0] if args else None
        return {self.unpack(item, elem_type) for item in obj[str(Marks.SET)]}

    def _unpack_tuple(self, obj: dict[str, Any], expected_type: type[Any] | None = None) -> tuple[Any, ...]:
        """
        Unpack tuple from dict with TUPLE marker.

        Args:
            obj: Dict with Marks.TUPLE marker and list of items
            expected_type: Optional expected type (tuple[Type1, Type2, ...])

        Returns:
            tuple with unpacked items
        """
        items = obj[str(Marks.TUPLE)]

        if expected_type:
            origin = get_origin(expected_type)
            if origin is tuple:
                # tuple[Type1, Type2, ...] - более точная десериализация
                elem_types = get_args(expected_type)
                return tuple(
                    self.unpack(item, elem_types[i] if i < len(elem_types) else None)
                    for i, item in enumerate(items)
                )

        # Без expected_type - просто восстановление tuple
        return tuple(self.unpack(item) for item in items)

    def _unpack_object_id(self, obj: dict[str, Any], expected_type: type[Any] | None = None) -> Any:
        """Unpack ObjectId from dict with marker."""
        # expected_type игнорируется для ObjectId (тип уже определен маркером)
        if ObjectId is None:
            raise ImportError("pymongo is required to unpack ObjectId")
        return ObjectId(obj[str(Marks.OBJECT_ID)])

    # ========== Model unpacking methods ==========

    def _unpack_model(self, obj: dict[str, Any]) -> Any:
        """
        Unpack model from dict with MODEL marker.

        Args:
            obj: Dict with Marks.MODEL marker and model data

        Returns:
            Model instance (Pydantic or dataclass)

        Raises:
            RegistrationError: If model is not registered
        """
        from .registry import REGISTERED_MODELS

        model_key = obj[str(Marks.MODEL)]
        cls = REGISTERED_MODELS.get(model_key)

        if cls is None:
            raise RegistrationError(
                f"Model with key '{model_key}' is not registered. Use @register_model()"
            )

        # Рекурсивный unpack полей
        data = {}
        for key, value in obj.items():
            if key != str(Marks.MODEL):
                # Получаем тип поля из аннотаций
                field_type = None
                if hasattr(cls, '__annotations__'):
                    field_type = cls.__annotations__.get(key)
                data[key] = self.unpack(value, field_type)

        # Создание экземпляра
        if BaseModel is not None and issubclass(cls, BaseModel):
            if hasattr(cls, 'model_validate'):
                # Pydantic v2
                return cls.model_validate(data)
            else:
                # Pydantic v1
                return cls(**data)
        else:
            # Dataclass
            return cls(**data)

    # ========== Model packing methods ==========

    def _pack_pydantic(self, obj: Any) -> dict[str, Any]:
        """
        Pack Pydantic model to dict with marker.

        Args:
            obj: Pydantic BaseModel instance

        Returns:
            Dict with Marks.MODEL marker and model data

        Raises:
            RegistrationError: If model is not registered
        """
        cls = type(obj)
        model_key = MODEL_ALIASES.get(cls)

        if model_key is None:
            raise RegistrationError(
                f"Pydantic model {cls} is not registered. Use @register_model()"
            )

        # Извлечение полей вручную (без model_dump/dict для сохранения вложенных объектов)
        # model_dump() и dict() рекурсивно преобразуют вложенные модели в dict,
        # что приводит к потере маркеров моделей при последующей упаковке
        packed_data = {}
        if hasattr(cls, 'model_fields'):
            # Pydantic v2 - итерация по model_fields класса (не экземпляра)
            for field_name in cls.model_fields:
                value = getattr(obj, field_name)
                packed_data[field_name] = self.pack(value)  # Рекурсивная упаковка
        elif hasattr(cls, '__fields__'):
            # Pydantic v1 - итерация по __fields__ класса
            for field_name in cls.__fields__:
                value = getattr(obj, field_name)
                packed_data[field_name] = self.pack(value)  # Рекурсивная упаковка
        else:
            # Fallback для совместимости
            if hasattr(obj, 'model_dump'):
                data = obj.model_dump(mode='python')
            else:
                data = obj.dict()
            for key, value in data.items():
                packed_data[key] = self.pack(value)

        return {str(Marks.MODEL): model_key, **packed_data}

    def _pack_dataclass(self, obj: Any) -> dict[str, Any]:
        """
        Pack dataclass to dict with marker.

        Args:
            obj: Dataclass instance

        Returns:
            Dict with Marks.MODEL marker and dataclass data

        Raises:
            RegistrationError: If dataclass is not registered
        """
        cls = type(obj)
        model_key = MODEL_ALIASES.get(cls)

        if model_key is None:
            raise RegistrationError(
                f"Dataclass {cls} is not registered. Use @register_model()"
            )

        # Извлечение полей вручную (без asdict для сохранения вложенных объектов)
        # dataclasses.asdict() рекурсивно преобразует вложенные dataclass в dict,
        # что приводит к потере маркеров моделей при последующей упаковке
        packed_data = {}
        for field in dataclasses.fields(obj):
            value = getattr(obj, field.name)
            packed_data[field.name] = self.pack(value)  # Рекурсивная упаковка

        return {str(Marks.MODEL): model_key, **packed_data}

    # ========== Utility methods ==========

    def _convert_string_to_type(self, obj: str, expected_type: type[Any]) -> Any:
        """
        Convert string to expected type (only when explicitly expected).

        This method is called only when expected_type is provided, avoiding
        aggressive string conversion that was a problem in the original system.

        Args:
            obj: String to convert
            expected_type: Expected type for conversion

        Returns:
            Converted object or original string if conversion fails
        """
        # Если expected_type это str, возвращаем как есть
        if expected_type is str:
            return obj

        try:
            if expected_type is Decimal:
                return Decimal(obj)
            if expected_type is ObjectId and ObjectId is not None:
                return ObjectId(obj)
            if expected_type is datetime.datetime:
                return datetime.datetime.fromisoformat(obj)
            if expected_type is datetime.date:
                return datetime.date.fromisoformat(obj)
        except (ValueError, TypeError, Exception):
            # Перехватываем все исключения, включая decimal.InvalidOperation
            pass
        return obj

    def pack(self, obj: Any) -> Any:
        """
        Pack Python object to JSON-serializable structure.

        Args:
            obj: Python object to serialize

        Returns:
            JSON-serializable structure

        Raises:
            TypeError: If object is a Response object or unsupported type
        """
        # Простые типы (быстрая проверка)
        if obj is None or isinstance(obj, (str, int, float, bool)):
            return obj

        # Проверка Response объектов (явный запрет сериализации)
        if Response is not None and isinstance(obj, Response):
            raise TypeError("Response objects cannot be serialized")

        # Dispatch-таблица (O(1) поиск обработчика)
        obj_type = type(obj)
        handler = self._pack_handlers.get(obj_type)
        if handler:
            return handler(obj)

        # Проверка Pydantic моделей
        if BaseModel is not None and isinstance(obj, BaseModel):
            return self._pack_pydantic(obj)

        # Проверка dataclass
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return self._pack_dataclass(obj)

        # Обработка list (рекурсивная упаковка)
        if isinstance(obj, list):
            return [self.pack(item) for item in obj]

        # Обработка tuple (сериализуется как dict с маркером)
        if isinstance(obj, tuple):
            return {str(Marks.TUPLE): [self.pack(item) for item in obj]}

        # Обработка dict (рекурсивная упаковка значений)
        if isinstance(obj, dict):
            return {k: self.pack(v) for k, v in obj.items()}

        # Fallback: другие типы...
        raise TypeError(f"Unsupported type for packing: {obj_type}")

    def unpack(self, obj: Any, expected_type: type[Any] | None = None) -> Any:
        """
        Unpack JSON-serializable structure to Python object.

        Args:
            obj: JSON-serializable structure
            expected_type: Optional expected type for better deserialization

        Returns:
            Python object

        Raises:
            RegistrationError: If model is not registered
        """
        # None
        if obj is None:
            return None

        # Простые типы (быстрая проверка) - исключаем str, она обрабатывается отдельно
        if isinstance(obj, (int, float, bool)):
            return obj

        # Маркеры типов (dispatch-таблица) - проверяем dict с маркерами
        if isinstance(obj, dict):
            # Проверка маркеров через dispatch-таблицу (O(1))
            for marker, handler in self._unpack_handlers.items():
                if marker in obj:
                    return handler(obj, expected_type)

            # Проверка MODEL (обрабатывается отдельно)
            if str(Marks.MODEL) in obj:
                return self._unpack_model(obj)

        # Обработка коллекций
        # list
        if isinstance(obj, list):
            if expected_type:
                origin = get_origin(expected_type)
                if origin is list:
                    # list[Type]
                    args = get_args(expected_type)
                    elem_type = args[0] if args else None
                    return [self.unpack(item, elem_type) for item in obj]
                elif origin is tuple:
                    # tuple[Type1, Type2, ...] - восстановление tuple
                    elem_types = get_args(expected_type)
                    return tuple(
                        self.unpack(item, elem_types[i] if i < len(elem_types) else None)
                        for i, item in enumerate(obj)
                    )

            # Без expected_type - просто рекурсивный unpack
            return [self.unpack(item) for item in obj]

        # dict (обычный, без маркеров)
        if isinstance(obj, dict):
            if expected_type:
                origin = get_origin(expected_type)
                if origin is dict:
                    # dict[str, Type]
                    args = get_args(expected_type)
                    value_type = args[1] if len(args) > 1 else None
                    return {k: self.unpack(v, value_type) for k, v in obj.items()}

            # Без expected_type - просто рекурсивный unpack
            return {k: self.unpack(v) for k, v in obj.items()}

        # Обработка строк
        if isinstance(obj, str):
            # Преобразование при expected_type
            if expected_type:
                converted = self._convert_string_to_type(obj, expected_type)
                if converted is not obj:
                    return converted

            # УДАЛЕН блок агрессивной конвертации ISO строк
            # Конвертация происходит только при наличии expected_type

            return obj

        # Fallback для неизвестных типов
        raise TypeError(f"Unsupported type for unpacking: {type(obj).__name__}")

    def dumps(self, value: Any) -> bytes:
        """
        Serialize to JSON bytes using orjson.

        All non-native JSON types (datetime, Decimal, set, models, etc.)
        are packed with type markers before serialization.

        Args:
            value: Python object to serialize

        Returns:
            JSON bytes

        Examples:
            >>> serializer = JsonSerializer()
            >>> data = {"name": "Alice", "age": 30}
            >>> serializer.dumps(data)
            b'{"name":"Alice","age":30}'

            >>> serializer = JsonSerializer(namespace="cache:v2:")
            >>> serializer.dumps(data)
            b'{"$ns":"cache:v2:","$data":{"name":"Alice","age":30}}'
        """
        import orjson

        # Pack объект (добавляет маркеры типов для нестандартных типов)
        packed = self.pack(value)

        # Namespace-обёртка (для версионирования)
        if self.namespace:
            packed = {NS_KEY: self.namespace, DATA_KEY: packed}

        # Сериализация через orjson (без passthrough опций, так как все типы уже обработаны в pack)
        return orjson.dumps(packed)

    def loads(self, value: bytes | None) -> Any:
        """
        Deserialize from JSON bytes using orjson.

        Handles namespace wrapper and unpacks objects with type markers
        back to their original Python types.

        Args:
            value: JSON bytes to deserialize (or None)

        Returns:
            Python object (or None if value is None)

        Examples:
            >>> serializer = JsonSerializer()
            >>> data = b'{"name":"Alice","age":30}'
            >>> serializer.loads(data)
            {'name': 'Alice', 'age': 30}

            >>> serializer = JsonSerializer(namespace="cache:v2:")
            >>> data = b'{"$ns":"cache:v2:","$data":{"name":"Alice","age":30}}'
            >>> serializer.loads(data)
            {'name': 'Alice', 'age': 30}
        """
        import orjson

        if value is None:
            return None

        # Десериализация через orjson
        data = orjson.loads(value)

        # Обработка namespace-обёртки
        if isinstance(data, dict) and NS_KEY in data and DATA_KEY in data:
            data = data[DATA_KEY]

        # Unpack объект (восстанавливает типы по маркерам)
        return self.unpack(data)
