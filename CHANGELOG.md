# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-23

### Added
- Initial release
- Dispatch-table based serializer for O(1) type lookup
- Support for Pydantic models and dataclasses with `@register_model()` decorator
- Model registry with stable aliases for versioning
- Integration with aiocache via `AiocacheJsonSerializer`
- Namespace support for format versioning
- Support for native JSON types: `str`, `int`, `float`, `bool`, `None`
- Support for dates: `datetime.datetime`, `datetime.date`
- Support for collections: `set`, `list`, `tuple`, `dict`
- Support for custom types: `Decimal`, `ObjectId` (MongoDB)
- Type-safe string conversion with `expected_type` parameter
- Full type annotations with mypy strict mode support

### Changed
- Simplified architecture compared to original implementation
- Removed chain-of-responsibility pattern in favor of dispatch tables
- Removed aggressive string parsing (`_get_parsed_str`)

### Fixed
- Cache key generation now uses `module.qualname` instead of function object
- Positional arguments preserve order (no more collisions)
- String conversion only happens with explicit `expected_type`
- Response objects are explicitly rejected (not silently cached as None)
- Loss of markers for nested dataclasses (Issue #001)
- Loss of markers for nested Pydantic models (Issue #002)
- Aggressive ISO datetime string conversion (Issue #003)
- Missing `expected_type` support for `set` elements (Issue #004)
- Stricter registration behavior (Issue #005)
- Inconsistent error types (`NotImplementedError` vs `TypeError`) (Issue #006)
- Hardcoded namespace constants (Issue #007)
- Missing `tuple` marker for type preservation (Issue #008)
- Inconsistent architecture for `TUPLE` marker (Issue #009)
- Unified registration exceptions (Issue #010)

## [Unreleased]





