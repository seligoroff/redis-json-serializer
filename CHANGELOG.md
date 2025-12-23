# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project skeleton
- Dispatch-table based serializer for O(1) type lookup
- Support for Pydantic models and dataclasses
- Model registry with stable aliases
- Integration with aiocache
- Namespace support for format versioning
- Fixed cache key generation (preserves argument order)
- Type-safe string conversion (only with expected_type)

### Changed
- Simplified architecture compared to original implementation
- Removed chain-of-responsibility pattern in favor of dispatch tables
- Removed aggressive string parsing (`_get_parsed_str`)

### Fixed
- Cache key generation now uses `module.qualname` instead of function object
- Positional arguments preserve order (no more collisions)
- String conversion only happens with explicit `expected_type`
- Response objects are explicitly rejected (not silently cached as None)

## [0.1.0] - TBD

### Added
- Initial release





