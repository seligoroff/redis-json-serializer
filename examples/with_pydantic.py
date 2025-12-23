"""
Example with Pydantic models.

TODO: Обновить примеры после реализации команды разработки
"""

from redis_json_serializer import JsonSerializer, register_model

try:
    from pydantic import BaseModel
except ImportError:
    print("Pydantic not installed. Install with: pip install redis-json-serializer[pydantic]")
    exit(1)


# Register model with stable alias (recommended for production)
@register_model("user.v1")
class User(BaseModel):
    id: str
    name: str
    email: str


# Create serializer
serializer = JsonSerializer()

# TODO: Раскомментировать после реализации
# # Create and serialize user
# user = User(id="123", name="Alice", email="alice@example.com")
# packed = serializer.pack(user)
# print("Packed:", packed)
#
# # Deserialize
# unpacked = serializer.unpack(packed)
# print("Unpacked:", unpacked)
# print("Type:", type(unpacked))
# assert isinstance(unpacked, User)
# assert unpacked.id == "123"

print("TODO: Реализовать команде разработки")
