# Makefile for intellifire4py

.PHONY: venv coverage test update-deps lint

# Create virtual environment and install dependencies
venv:
	uv venv
	uv sync --all-extras

# Update dependencies and lock file
update-deps:
	uv sync --upgrade --all-extras --dev
	pre-commit autoupdate

# Run tests
test:
	uv run pytest

# Run tests with coverage
coverage:
	uv run pytest --cov --cov-report=term-missing

# Run linting and formatting
lint:
	uv run ruff check --fix .
	uv run ruff format .
