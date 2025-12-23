# Руководство для команды разработки

## Обзор проекта

`redis-json-serializer` - это выделенная версия системы сериализации из основного проекта `gazpromneft-academy`, подготовленная для публикации на PyPI.

## Что уже реализовано в скелетоне

### ✅ Критические исправления (из comparison_report.md)

1. **Исправлена генерация ключей кэша** (`utils.py`)
   - Использует `module.qualname` вместо `str(func)`
   - Сохраняет порядок позиционных аргументов
   - Устранены коллизии ключей

2. **Убрана агрессивная конвертация строк**
   - Удалена функция `_get_parsed_str`
   - Конвертация только при наличии `expected_type`
   - Улучшена производительность

3. **Исправлен ResponseSerializer**
   - Явно запрещена сериализация Response объектов

### ✅ Архитектурные улучшения

1. **Dispatch-таблицы вместо цепочки** (`serializer.py`)
   - O(1) lookup вместо O(N) итераций
   - Упрощенная архитектура
   - Лучшая производительность

2. **Использование возможностей orjson**
   - `datetime.datetime` обрабатывается нативно через `OPT_PASSTHROUGH_DATETIME`
   - `dataclass` обрабатывается нативно через `OPT_PASSTHROUGH_DATACLASS`

3. **Объединены Pydantic/Dataclass сериализаторы**
   - Единая логика в `_pack_pydantic` и `_pack_dataclass`

4. **Стабильные алиасы для моделей** (`registry.py`)
   - Параметр `alias` в `@register_model()`
   - Решена проблема хрупкости при рефакторинге

5. **Оптимизация поиска алиаса**
   - `MODEL_ALIASES` для O(1) поиска
   - Улучшена производительность `_pack_pydantic` и `_pack_dataclass`

6. **Namespace для версионирования**
   - Параметр `namespace` в конструкторе `JsonSerializer`

## Структура проекта

```
redis-json-serializer/
├── src/
│   └── redis_json_serializer/
│       ├── __init__.py          # Экспорт публичного API
│       ├── serializer.py         # Основной сериализатор (dispatch-таблицы)
│       ├── registry.py           # Регистрация моделей
│       ├── types.py              # Маркеры типов (Marks)
│       ├── utils.py              # Утилиты (ключи кэша)
│       └── aiocache.py           # Интеграция с aiocache
├── tests/
│   ├── test_serializer.py        # Тесты сериализатора
│   ├── test_registry.py          # Тесты регистрации
│   └── test_utils.py             # Тесты утилит
├── examples/
│   ├── basic_usage.py            # Базовое использование
│   ├── with_pydantic.py         # С Pydantic моделями
│   └── with_aiocache.py         # С aiocache
├── pyproject.toml                # Конфигурация проекта
├── README.md                     # Документация для пользователей
├── TODO.md                       # Список задач
└── DEVELOPMENT.md                # Это руководство
```

## Что нужно доделать

### Приоритет 1: Тестирование и исправление багов

1. **Запустить тесты и исправить ошибки**
   ```bash
   cd localdocs/external/redis-json-serializer
   pip install -e ".[dev,all]"
   pytest
   ```

2. **Добавить недостающие тесты**
   - Тесты для всех edge cases
   - Тесты производительности
   - Интеграционные тесты

3. **Исправить найденные баги**
   - Проверить работу с опциональными зависимостями (pydantic, pymongo)
   - Проверить обработку ошибок

### Приоритет 2: Проброс expected_type в коллекции

Реализовать из предложения GPT-5:

```python
# В serializer.py, метод unpack
if isinstance(obj, list):
    elem_type = None
    if expected_type:
        from typing import get_origin, get_args
        origin = get_origin(expected_type)
        if origin in (list, tuple):
            args = get_args(expected_type)
            elem_type = args[0] if args else None
    
    return [self.unpack(i, expected_type=elem_type) for i in obj]
```

### Приоритет 3: Документация

1. **Расширить README.md**
   - Больше примеров
   - Описание архитектуры
   - Руководство по миграции

2. **Документация API**
   - Docstrings для всех публичных методов
   - Примеры использования

3. **Руководство по миграции**
   - Как мигрировать из текущей системы
   - План миграции данных

### Приоритет 4: Подготовка к PyPI

1. **Проверить pyproject.toml**
   - Все метаданные корректны
   - Зависимости правильные
   - Классификаторы актуальны

2. **Создать аккаунт на PyPI** (test и production)

3. **Настроить автоматическую публикацию** (GitHub Actions)

## Ключевые отличия от оригинальной системы

### Упрощения

1. **Нет цепочки сериализаторов** - используется dispatch-таблица
2. **Меньше классов** - простая архитектура
3. **Использование orjson** - меньше дублирования кода

### Улучшения

1. **Исправлены баги** - ключи кэша, конвертация строк
2. **Лучшая производительность** - O(1) вместо O(N)
3. **Стабильные алиасы** - не ломается при рефакторинге
4. **Namespace** - версионирование формата

### Сохранено

1. **Безопасность** - whitelist моделей через регистрацию
2. **Поддержка типов** - Pydantic, dataclass, Decimal, ObjectId, set, date
3. **Интеграция с aiocache** - готовый адаптер

## Связь с оригинальным проектом

Исходный код находится в:
- `src/infrastructure/cache/serializers/` - оригинальная система
- `localdocs/notes/cache_serialization/` - анализ и предложения

Этот проект - улучшенная версия, готовая к публикации.

## Следующие шаги

1. Запустить тесты и исправить ошибки
2. Добавить недостающий функционал (проброс expected_type)
3. Расширить документацию
4. Подготовить к публикации на PyPI

## Полезные ссылки

- [comparison_report.md](../../notes/cache_serialization/comparison_report.md) - анализ предложений AI
- [README.md](../../notes/cache_serialization/README.md) - описание оригинальной системы
- [ai_responses/](../../notes/cache_serialization/ai_responses/) - предложения от AI

