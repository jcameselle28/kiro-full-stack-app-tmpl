---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# Python Coding Standards

## Formatting & Style
- Use `ruff` for linting and formatting (replaces black, isort, flake8)
- Line length: 120 characters max
- Use double quotes for strings
- Sort imports: stdlib → third-party → local (ruff handles this)

## Type Hints
- All function signatures must have type hints (params and return)
- Use `from __future__ import annotations` for modern syntax
- Use `typing` module for complex types (Optional, Union, TypeVar)
- Prefer `X | None` over `Optional[X]` (Python 3.10+)

## Error Handling
- Never use bare `except:` — always catch specific exceptions
- Use custom exception classes for domain errors
- Log exceptions with `logger.exception()` for stack traces
- Re-raise or wrap exceptions, don't swallow them silently

## Naming Conventions
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Prefix private methods/attributes with `_`
- Use descriptive names — avoid single letters except in comprehensions

## Project Structure
- One class per file for major classes
- Group by feature/domain, not by type (avoid `models/`, `utils/` catch-alls)
- `__init__.py` should only re-export public API
- Tests mirror source structure: `src/handlers/order.py` → `tests/unit/handlers/test_order.py`

## Dependencies
- Use `pyproject.toml` for project metadata and dependencies
- Pin major versions in requirements: `boto3>=1.34,<2.0`
- Separate dev dependencies from runtime
- Use virtual environments always (venv or uv)

## AWS-Specific Python
- Initialize boto3 clients outside handler functions (connection reuse)
- Use `botocore.config.Config` for retry configuration
- Prefer `resource` API for simple CRUD, `client` API for advanced operations
- Always handle `ClientError` from boto3 calls with specific error code checks
- Use Powertools for Lambda: Logger, Tracer, Metrics, Parameters

## Testing
- Use `pytest` as the test framework
- Use `moto` for mocking AWS services in unit tests
- Use `pytest-cov` for coverage (target: 80%+)
- Fixtures in `conftest.py`, scoped appropriately
- Mark slow/integration tests with `@pytest.mark.integration`
