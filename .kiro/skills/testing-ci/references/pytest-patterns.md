# Pytest Patterns for AWS

## conftest.py Setup

```python
import pytest
import boto3
from moto import mock_aws
import os

@pytest.fixture(autouse=True)
def aws_credentials():
    """Mock AWS credentials for moto."""
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table."""
    with mock_aws():
        client = boto3.resource("dynamodb", region_name="us-east-1")
        table = client.create_table(
            TableName="test-table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table

@pytest.fixture
def s3_bucket():
    """Create a mock S3 bucket."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        yield client

@pytest.fixture
def sqs_queue():
    """Create a mock SQS queue."""
    with mock_aws():
        client = boto3.client("sqs", region_name="us-east-1")
        response = client.create_queue(QueueName="test-queue")
        yield client, response["QueueUrl"]
```

## Testing Lambda Handlers

```python
from moto import mock_aws
from src.handlers.order import handler

@mock_aws
def test_handler_creates_order(dynamodb_table):
    event = {
        "body": '{"product_id": "prod-123", "quantity": 2}',
        "requestContext": {"authorizer": {"claims": {"sub": "user-456"}}},
    }

    response = handler(event, None)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert "order_id" in body

@mock_aws
def test_handler_returns_400_on_invalid_input():
    event = {"body": '{"invalid": "data"}'}

    response = handler(event, None)

    assert response["statusCode"] == 400
```

## Testing Service Layer

```python
class TestOrderService:
    def test_calculate_total_with_discount(self):
        service = OrderService()
        items = [
            {"price": 100.00, "quantity": 2},
            {"price": 50.00, "quantity": 1},
        ]

        total = service.calculate_total(items, discount_percent=10)

        assert total == 225.00  # (200 + 50) * 0.9

    def test_validate_order_rejects_empty_items(self):
        service = OrderService()

        with pytest.raises(ValidationError, match="at least one item"):
            service.validate_order(items=[])
```

## Testing Error Handling

```python
from botocore.exceptions import ClientError
from unittest.mock import patch, MagicMock

def test_handles_dynamodb_throttling():
    mock_table = MagicMock()
    mock_table.put_item.side_effect = ClientError(
        {"Error": {"Code": "ProvisionedThroughputExceededException"}},
        "PutItem",
    )

    with pytest.raises(ServiceUnavailableError):
        repository.save_order(mock_table, order_data)
```

## Markers and Organization

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (no AWS calls)",
    "integration: Integration tests (mocked AWS)",
    "e2e: End-to-end tests (real AWS)",
    "slow: Tests that take > 5 seconds",
]
testpaths = ["tests"]
```

Run selectively:
```bash
pytest -m unit                    # Fast, no AWS
pytest -m integration             # With moto mocks
pytest -m "not e2e"               # Everything except real AWS
pytest --cov=src --cov-report=html  # With coverage
```
