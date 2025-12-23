"""
Tests for utility functions.
"""


from redis_json_serializer.utils import default_key_builder, hash_args


class TestHashArgs:
    """Test hash_args function."""

    def test_preserves_order(self):
        """
        Positional arguments should preserve order.

        ВАЖНО: f(1, 2) и f(2, 1) должны давать разные хэши!
        """
        hash1 = hash_args(1, 2)
        hash2 = hash_args(2, 1)
        assert hash1 != hash2, "Positional arguments order should matter"

    def test_kwargs_order_independent(self):
        """
        Keyword arguments order should not matter.

        f(a=1, b=2) и f(b=2, a=1) должны давать одинаковый хэш.
        """
        hash1 = hash_args(a=1, b=2)
        hash2 = hash_args(b=2, a=1)
        assert hash1 == hash2, "Keyword arguments order should not matter"

    def test_deterministic(self):
        """Same arguments should produce same hash."""
        hash1 = hash_args(1, 2, 3, x=10, y=20)
        hash2 = hash_args(1, 2, 3, x=10, y=20)
        assert hash1 == hash2, "Same arguments should produce same hash"

    def test_mixed_args_kwargs(self):
        """Test with both positional and keyword arguments."""
        hash1 = hash_args(1, 2, a=10, b=20)
        hash2 = hash_args(1, 2, b=20, a=10)
        assert hash1 == hash2, "Keyword order should not matter with positional args"

        hash3 = hash_args(2, 1, a=10, b=20)
        assert hash1 != hash3, "Positional order should still matter"


class TestDefaultKeyBuilder:
    """Test default_key_builder function."""

    def test_stable_key(self):
        """
        Key should be stable across runs (no memory addresses).

        ВАЖНО: Не использовать str(func) - содержит адрес в памяти!
        """
        def test_func(x, y):
            return x + y

        key1 = default_key_builder(test_func, 1, 2)
        key2 = default_key_builder(test_func, 1, 2)

        # Ключ должен быть одинаковым при одинаковых аргументах
        assert key1 == key2, "Key should be stable"

        # Ключ должен содержать module.qualname, а не адрес памяти
        assert "test_func" in key1, "Key should contain function name"
        assert "@" not in key1, "Key should not contain memory address"

    def test_different_args_different_keys(self):
        """Different arguments should produce different keys."""
        def test_func(x, y):
            return x + y

        key1 = default_key_builder(test_func, 1, 2)
        key2 = default_key_builder(test_func, 2, 1)
        key3 = default_key_builder(test_func, 1, 2, z=3)

        assert key1 != key2, "Different positional args should produce different keys"
        assert key1 != key3, "Different kwargs should produce different keys"

    def test_module_qualname_in_key(self):
        """Key should use module.qualname format."""
        def test_func():
            pass

        key = default_key_builder(test_func)

        # Ключ должен содержать точку (разделитель module.qualname)
        assert "." in key, "Key should contain module.qualname format"

        # Ключ должен заканчиваться на имя функции
        assert key.endswith("test_func") or "test_func" in key, "Key should contain function name"

    def test_empty_args(self):
        """Test with no arguments."""
        def test_func():
            pass

        key = default_key_builder(test_func)
        assert isinstance(key, str), "Key should be a string"
        assert len(key) > 0, "Key should not be empty"
