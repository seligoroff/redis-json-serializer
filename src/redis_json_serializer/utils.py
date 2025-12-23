"""
Utility functions for cache key generation.
"""

import hashlib
from typing import Any


def hash_args(*args: Any, **kwargs: Any) -> str:
    """
    Hash function arguments for cache key generation.

    Preserves order of positional arguments to avoid collisions.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        SHA1 hash hexdigest
    """
    # Сохраняем порядок позиционных аргументов (не сортировать!)
    args_repr = repr(args).encode("utf-8")
    # Сортируем только kwargs для детерминированности
    kwargs_repr = repr(tuple(sorted(kwargs.items()))).encode("utf-8")
    return hashlib.sha1(args_repr + kwargs_repr).hexdigest()


def default_key_builder(func: Any, *args: Any, **kwargs: Any) -> str:
    """
    Default cache key builder for functions.

    Uses module.qualname for stable function identification.

    Args:
        func: Function to build key for
        *args: Function positional arguments
        **kwargs: Function keyword arguments

    Returns:
        Cache key string
    """
    # Использовать module.qualname вместо str(func) для стабильности
    module = getattr(func, "__module__", "")
    qualname = getattr(func, "__qualname__", getattr(func, "__name__", ""))
    func_key = f"{module}.{qualname}"
    args_hash = hash_args(*args, **kwargs)
    return f"{func_key}:{args_hash}"
