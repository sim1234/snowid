.PHONY: help install install-dev sync format format-check lint lint-fix typecheck test test-cov test-watch clean run run-shell stubs download-dlls

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install all dependencies including dev tools"
	@echo "  make sync          - Sync dependencies (equivalent to uv sync)"
	@echo "  make format        - Format code with black"
	@echo "  make format-check  - Check code formatting without making changes"
	@echo "  make lint          - Run ruff linter"
	@echo "  make lint-fix      - Run ruff linter and auto-fix issues"
	@echo "  make typecheck     - Run mypy type checker"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make test-watch    - Run tests in watch mode (requires pytest-watch)"
	@echo "  make clean         - Remove cache files and build artifacts"
	@echo "  make run           - Run the game"
	@echo "  make run-shell     - Run IPython shell"
	@echo "  make check-all     - Run all checks (format, lint, typecheck, test)"
	@echo "  make pre-commit    - Run checks typically used before committing"
	@echo "  make typings       - Generate type stubs for sdl2"
	@echo "  make download-dlls - Download SDL2 DLLs for Windows"

# Installation
install:
	uv sync

install-dev:
	uv sync --extra dev

sync:
	uv sync --extra dev

# Code formatting
format:
	uv run black project/

format-check:
	uv run black --check project/

# Linting
lint:
	uv run ruff check project/

lint-fix:
	uv run ruff check --fix project/

# Type checking
typecheck:
	uv run mypy project/

# Testing
test:
	uv run pytest project/tests/ -v

test-cov:
	uv run pytest project/tests/ --cov=project --cov-report=term-missing --cov-report=html

test-watch:
	uv run ptw project/tests/ -- -v

# Running the application
run:
	uv run python project/main.py

run-shell:
	uv run python project/shell.py

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Cleaned cache files and build artifacts"

# Combined checks
check-all: format-check lint typecheck test
	@echo "All checks passed!"

pre-commit: format-check lint typecheck test
	@echo "Pre-commit checks passed!"

# Code generation
typings:
	uv run python generate_typings.py

download-dlls:
	uv run python download_sdl2_dlls.py
