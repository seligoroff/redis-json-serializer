.PHONY: help install install-dev test lint format type-check clean build

help:
	@echo "Available commands:"
	@echo "  make install      - Install package and dependencies"
	@echo "  make install-dev  - Install with development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Run type checker"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build package"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,all]"

test:
	pytest

lint:
	ruff check .

format:
	black .
	ruff check --fix .

type-check:
	mypy src/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/

build:
	python -m build





