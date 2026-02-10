# Makefile for intellifire4py

.PHONY: venv coverage test update-deps lint docs docs-serve

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

# Build documentation
docs:
	cd docs && uv run sphinx-build -b html . _build/html

# Build and serve documentation with auto-reload
docs-serve:
	cd docs && uv run sphinx-autobuild -b html . _build/html
