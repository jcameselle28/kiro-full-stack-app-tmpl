# Pytest Patterns (Web App on RDS)

Test the data layer against a **real local database** (Docker Postgres/MySQL); reserve mocks for auxiliary AWS services (S3, Secrets Manager).

## conftest.py — Database & Client Fixtures

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Base

# A local Postgres for tests (docker compose / testcontainers); NOT production
TEST_DB_URL = "postgresql+psycopg://test:test@localhost:5432/test"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)   # or run Alembic migrations here
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine):
    """Each test runs in a transaction that is rolled back for isolation."""
    conn = engine.connect()
    txn = conn.begin()
    session = sessionmaker(bind=conn)()
    yield session
    session.close()
    txn.rollback()
    conn.close()

@pytest.fixture
def client(db_session):
    """FastAPI TestClient with the DB dependency overridden to the test session."""
    from fastapi.testclient import TestClient
    from src.main import app, get_db
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
```

## Service-Layer Unit Tests (no I/O)

```python
class TestInvoiceService:
    def test_total_with_discount(self):
        service = InvoiceService()
        items = [{"price": 100.00, "quantity": 2}, {"price": 50.00, "quantity": 1}]
        assert service.calculate_total(items, discount_percent=10) == 225.00

    def test_rejects_empty_items(self):
        with pytest.raises(ValidationError, match="at least one item"):
            InvoiceService().validate(items=[])
```

## Repository / Data-Layer Tests (real DB)

```python
def test_create_and_fetch_account(db_session):
    repo = AccountRepository(db_session)
    created = repo.create(name="Acme", email="ops@acme.test")
    db_session.flush()

    fetched = repo.get(created.id)
    assert fetched.email == "ops@acme.test"
    assert fetched.deleted_at is None

def test_unique_email_constraint(db_session):
    repo = AccountRepository(db_session)
    repo.create(name="A", email="dup@acme.test")
    db_session.flush()
    with pytest.raises(IntegrityError):
        repo.create(name="B", email="dup@acme.test")
        db_session.flush()
```

## API Endpoint Tests

```python
def test_create_account_endpoint(client):
    res = client.post("/v1/accounts", json={"name": "Acme", "email": "ops@acme.test"})
    assert res.status_code == 201
    assert res.json()["email"] == "ops@acme.test"

def test_validation_error_envelope(client):
    res = client.post("/v1/accounts", json={"name": ""})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "validation_error"

def test_requires_auth(client):
    res = client.get("/v1/accounts")
    assert res.status_code == 401
```

## Mocking Auxiliary AWS Services (moto)

Use moto only for non-database AWS calls the code makes (S3, Secrets Manager) — not for the relational DB.

```python
import boto3
from moto import mock_aws

@mock_aws
def test_generates_presigned_upload_url():
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="uploads")
    url = StorageService(bucket="uploads").upload_url("docs/a.pdf")
    assert "uploads" in url and "Signature" in url
```

## Markers & Running

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: pure logic, no I/O",
    "integration: hits the local database",
    "e2e: against a deployed environment",
]
testpaths = ["tests"]
```
```bash
pytest -m unit                      # fast, no DB
pytest -m integration               # requires local Postgres
pytest -m "not e2e"                 # everything but deployed tests
pytest --cov=src --cov-report=html  # coverage
```
Spin up the test database with docker compose (or testcontainers) in CI before integration tests.
