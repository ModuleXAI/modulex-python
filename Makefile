.PHONY: help install test test-integration lint format typecheck check build clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package in editable mode with dev dependencies
	pip install -e ".[dev]"

test: ## Run unit tests
	pytest tests/ --ignore=tests/integration -v --tb=short

test-integration: ## Run integration tests (requires .env with API credentials)
	pytest tests/integration/ -v --tb=short -s --override-ini="addopts="

lint: ## Run linter (ruff)
	ruff check .

format: ## Auto-format code (ruff)
	ruff format .

typecheck: ## Run type checker (mypy)
	mypy src/

check: lint typecheck test ## Run all quality checks (lint + typecheck + tests)

build: ## Build source and wheel distributions
	python -m build

clean: ## Remove build artifacts and caches
	rm -rf dist/ build/ *.egg-info src/*.egg-info .mypy_cache .pytest_cache .ruff_cache htmlcov coverage.xml .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
