# Contributing to redis-json-serializer

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:seligoroff/redis-json-serializer.git
   cd redis-json-serializer
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   # Using pyproject.toml (recommended)
   pip install -e ".[dev,all]"
   
   # Or using requirements file
   pip install -r requirements-dev.txt
   ```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=redis_json_serializer --cov-report=html
```

## Code Style

We use:
- `ruff` for linting
- `black` for formatting
- `mypy` for type checking

Run all checks:
```bash
ruff check .
black --check .
mypy src/
```

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Add tests
4. Ensure all tests pass
5. Submit a pull request

## Project Goals

- **Simplicity**: Keep the API simple and intuitive
- **Performance**: Optimize for speed
- **Security**: Maintain whitelist-based model registration
- **PyPI Ready**: Prepare for public release

