# Contributing to ModuleX Python SDK

Thank you for your interest in contributing! This guide will help you get started.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## Development Setup

### Prerequisites

- Python 3.9 or later
- [pip](https://pip.pypa.io/) package manager

### Getting Started

```bash
# Clone the repository
git clone https://github.com/ModuleXAI/modulex-python.git
cd modulex-python

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "from modulex import Modulex; print('OK')"
```

## Development Workflow

### Running Tests

```bash
# Unit tests (no API key needed)
make test

# Integration tests (requires .env with real API credentials)
cp .env.example .env
# Edit .env with your credentials
make test-integration

# All quality checks (lint + typecheck + unit tests)
make check
```

### Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for lint errors
make lint

# Auto-format code
make format

# Type checking with mypy
make typecheck
```

**Style guidelines:**
- Line length: 120 characters
- Target: Python 3.9+
- Ruff rules: `E`, `F`, `I`, `N`, `W`, `UP`
- All public methods must have type annotations
- Use `async`/`await` throughout (async-first SDK)

### Branch Naming

Use descriptive branch names with a prefix:

- `feat/add-new-resource` — New features
- `fix/retry-logic-bug` — Bug fixes
- `docs/update-readme` — Documentation changes
- `chore/update-deps` — Maintenance tasks

### Commit Messages

Write clear, concise commit messages:

```
feat: add bulk delete for credentials resource

fix: handle 204 No Content responses in _request

docs: add streaming usage examples to README

chore: update httpx to 0.28
```

Use conventional prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`.

## Pull Request Process

1. **Fork** the repository and create your branch from `main`
2. **Write tests** for any new functionality
3. **Ensure all checks pass**: `make check`
4. **Update documentation** if you changed public API
5. **Open a PR** with a clear description of the changes

### PR Checklist

- [ ] Tests pass (`make check`)
- [ ] New code has type annotations
- [ ] Public API changes are documented in README
- [ ] CHANGELOG.md updated (for user-facing changes)

### Review Process

- All PRs require at least one approving review
- CI must pass before merging
- Maintainers may request changes or suggest improvements

## Adding a New Resource

If you're adding support for a new API resource:

1. Create the type definitions in `src/modulex/types/<resource>.py`
2. Create the resource class in `src/modulex/resources/<resource>.py` (inherit from `_BaseResource`)
3. Register the resource as a lazy property in `src/modulex/_client.py`
4. Export new types in `src/modulex/types/__init__.py`
5. Add unit tests in `tests/test_<resource>.py`
6. Add integration tests in `tests/integration/test_<resource>.py`
7. Add usage examples to `README.md`
8. Add a documentation snippet in `docs/snippets/<resource>.mdx`

## Reporting Bugs

Use the [bug report template](https://github.com/ModuleXAI/modulex-python/issues/new?template=bug_report.yml) on GitHub Issues.

## Security Vulnerabilities

Please report security issues via email to **contact@modulex.dev** — do NOT use public issues. See [SECURITY.md](SECURITY.md) for details.

## Questions?

Open a [discussion](https://github.com/ModuleXAI/modulex-python/discussions) or reach out at contact@modulex.dev.
