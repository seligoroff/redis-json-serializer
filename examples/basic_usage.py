"""
Basic usage examples.

TODO: Обновить примеры после реализации команды разработки
"""

from redis_json_serializer import JsonSerializer

# Create serializer
serializer = JsonSerializer()

# Serialize basic types
data = {
    "name": "John",
    "age": 30,
    "active": True,
    "tags": {"python", "redis", "json"}
}

# TODO: Раскомментировать после реализации
# packed = serializer.pack(data)
# print("Packed:", packed)
# 
# # Round-trip serialization
# json_bytes = serializer.dumps(data)
# unpacked = serializer.loads(json_bytes)
# print("Unpacked:", unpacked)
# assert unpacked == data

print("TODO: Реализовать команде разработки")
