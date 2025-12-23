# redis-json-serializer

Fast and secure JSON serializer for Redis caching with Pydantic and dataclass support.

## Features

- 🚀 **Fast**: Built on top of `orjson` for maximum performance
- 🔒 **Secure**: Whitelist-based model registration prevents arbitrary code execution
- 📦 **Type-safe**: Full support for Pydantic models and dataclasses
- 🔧 **Extensible**: Plugin-based architecture for custom types
- 🎯 **Simple**: Clean API with minimal boilerplate

## Installation

### From PyPI (when published)
```bash
pip install redis-json-serializer
```

### From source (development)
```bash
# Clone repository
git clone git@github.com:seligoroff/redis-json-serializer.git
cd redis-json-serializer

# Install in development mode
pip install -e ".[dev,all]"

# Or using requirements files
pip install -r requirements-dev.txt
```

### With optional dependencies

```bash
# With Pydantic support
pip install redis-json-serializer[pydantic]

# With MongoDB ObjectId support
pip install redis-json-serializer[mongodb]

# With aiocache integration
pip install redis-json-serializer[aiocache]

# All optional dependencies
pip install redis-json-serializer[all]
```

## Quick Start

### Basic Usage

```python
from redis_json_serializer import JsonSerializer

serializer = JsonSerializer()

# Serialize
data = {"name": "John", "age": 30, "tags": {"python", "redis"}}
packed = serializer.pack(data)
json_bytes = serializer.dumps(data)

# Deserialize
unpacked = serializer.unpack(serializer.loads(json_bytes))
```

### With Pydantic Models

```python
from redis_json_serializer import JsonSerializer, register_model
from pydantic import BaseModel

@register_model("user.v1")  # Stable alias for versioning
class User(BaseModel):
    id: str
    name: str
    email: str

serializer = JsonSerializer()

user = User(id="123", name="Alice", email="alice@example.com")
packed = serializer.pack(user)
unpacked = serializer.unpack(packed)  # Returns User instance
```

### With aiocache

```python
from aiocache import cached
from aiocache.serializers import JsonSerializer
from redis_json_serializer import JsonSerializer as RedisJsonSerializer

# Configure aiocache to use our serializer
from aiocache import caches
caches.set_config({
    "default": {
        "cache": "aiocache.RedisCache",
        "serializer": {
            "class": "redis_json_serializer.aiocache.AiocacheJsonSerializer",
        },
    }
})

@cached(ttl=3600)
async def get_user(user_id: str) -> User:
    # Your logic here
    return User(id=user_id, name="Alice", email="alice@example.com")
```

## Architecture

The library uses a dispatch-table approach for O(1) type lookup instead of chain-of-responsibility pattern, providing better performance and simpler code.

### Supported Types

- **Native JSON**: `str`, `int`, `float`, `bool`, `None`
- **Dates**: `datetime.datetime`, `datetime.date`
- **Collections**: `set`, `list`, `tuple`, `dict`
- **Pydantic models**: With registration via `@register_model()`
- **Dataclasses**: With registration via `@register_model()`
- **Custom types**: `Decimal`, `ObjectId` (MongoDB)

## Versioning

The library supports format versioning through namespaces:

```python
serializer = JsonSerializer(namespace="cache:v2:")
```

This allows safe migration between format versions without clearing the entire Redis cache.

## License

MIT

## Contributing

Contributions are welcome! Please read our contributing guidelines first.

