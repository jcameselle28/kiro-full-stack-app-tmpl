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

## Web & AWS Integration (EC2 / RDS)
- Use a web framework (FastAPI/Flask/Django) with an ASGI/WSGI server (uvicorn/gunicorn) behind the ALB
- Expose dedicated health and readiness endpoints for ALB target group checks
- Access RDS through an ORM (SQLAlchemy) with a configured connection pool; never open a connection per request
- Manage schema changes with Alembic migrations checked into the repo
- Always use parameterized queries / ORM bindings — never string-interpolate SQL
- Initialize boto3 clients once at module load (connection reuse); configure retries with `botocore.config.Config`
- Use the default credential chain (EC2 instance profile) — never hardcode credentials
- Load secrets and config from Secrets Manager / SSM Parameter Store, not from committed files
- Always handle `ClientError` from boto3 calls with specific error code checks

## Testing
- Use `pytest` as the test framework
- Run integration tests against a real local database (Docker Postgres/MySQL); use `moto` only when mocking auxiliary AWS services (S3, Secrets Manager)
- Use `pytest-cov` for coverage (target: 80%+)
- Fixtures in `conftest.py`, scoped appropriately
- Mark slow/integration tests with `@pytest.mark.integration`
