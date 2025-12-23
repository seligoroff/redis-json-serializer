"""
Example with aiocache integration.

TODO: Обновить примеры после реализации команды разработки
"""

try:
    # Импорты будут использоваться после раскомментирования кода ниже
    from aiocache import cached, Cache  # noqa: F401
    from redis_json_serializer.aiocache import AiocacheJsonSerializer  # noqa: F401
except ImportError:
    print("aiocache not installed. Install with: pip install redis-json-serializer[aiocache]")
    exit(1)

try:
    from pydantic import BaseModel
    from redis_json_serializer import register_model
except ImportError:
    print("Pydantic not installed. Install with: pip install redis-json-serializer[pydantic]")
    exit(1)


@register_model("product.v1")
class Product(BaseModel):
    id: str
    name: str
    price: float


# TODO: Раскомментировать после реализации
# # Configure aiocache to use our serializer
# cache = Cache(
#     Cache.REDIS,
#     serializer=AiocacheJsonSerializer(namespace="cache:v2:"),
#     endpoint="localhost",
#     port=6379,
# )
# 
# 
# @cached(ttl=3600, cache=cache)
# async def get_product(product_id: str) -> Product:
#     """Example cached function."""
#     # Your business logic here
#     return Product(id=product_id, name="Example Product", price=99.99)
# 
# 
# # Usage
# import asyncio
# 
# async def main():
#     product = await get_product("123")
#     print(product)
# 
# if __name__ == "__main__":
#     asyncio.run(main())

print("TODO: Реализовать команде разработки")
