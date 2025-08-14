# Makefile for intellifire4py

.PHONY: coverage test update-deps

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
