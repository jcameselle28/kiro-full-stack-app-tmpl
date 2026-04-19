# AWS Service Integration Patterns

## Lambda + API Gateway

### REST API with validation
```yaml
# SAM template
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/handler.handler
      Runtime: python3.11
      MemorySize: 256
      Timeout: 30
      Tracing: Active
      Environment:
        Variables:
          TABLE_NAME: !Ref DataTable
          LOG_LEVEL: INFO
      Events:
        Api:
          Type: Api
          Properties:
            Path: /items
            Method: GET
```

### Lambda Powertools (Python)
```python
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

@app.get("/items")
@tracer.capture_method
def get_items():
    logger.info("Fetching items")
    # business logic here
    return {"items": []}

@logger.inject_lambda_context
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

## DynamoDB Patterns

### Single-Table Access Pattern
```python
# Put item with condition
table.put_item(
    Item={
        "PK": f"USER#{user_id}",
        "SK": f"PROFILE#{user_id}",
        "name": name,
        "email": email,
        "created_at": datetime.utcnow().isoformat(),
    },
    ConditionExpression="attribute_not_exists(PK)",
)

# Query related items
response = table.query(
    KeyConditionExpression=Key("PK").eq(f"USER#{user_id}") & Key("SK").begins_with("ORDER#"),
    ScanIndexForward=False,
    Limit=20,
)
```

## Step Functions

### Express workflow for synchronous processing
```json
{
  "StartAt": "ValidateInput",
  "States": {
    "ValidateInput": {
      "Type": "Task",
      "Resource": "${ValidateFunctionArn}",
      "Next": "ProcessData",
      "Catch": [{
        "ErrorEquals": ["ValidationError"],
        "Next": "HandleError"
      }]
    },
    "ProcessData": {
      "Type": "Task",
      "Resource": "${ProcessFunctionArn}",
      "Retry": [{
        "ErrorEquals": ["States.TaskFailed"],
        "IntervalSeconds": 2,
        "MaxAttempts": 3,
        "BackoffRate": 2.0
      }],
      "End": true
    },
    "HandleError": {
      "Type": "Fail",
      "Error": "ProcessingFailed",
      "Cause": "Input validation failed"
    }
  }
}
```

## EventBridge Patterns

### Event publishing
```python
import json
from datetime import datetime

events_client = boto3.client("events")

events_client.put_events(
    Entries=[{
        "Source": "myapp.orders",
        "DetailType": "OrderCreated",
        "Detail": json.dumps({
            "order_id": order_id,
            "customer_id": customer_id,
            "total": total,
            "timestamp": datetime.utcnow().isoformat(),
        }),
        "EventBusName": os.environ["EVENT_BUS_NAME"],
    }]
)
```

## SQS Consumer Pattern

### Batch processing with partial failure
```python
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor, EventType, batch_processor
)

processor = BatchProcessor(event_type=EventType.SQS)

@tracer.capture_method
def process_record(record):
    payload = json.loads(record["body"])
    # process individual message
    return payload

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handler(event, context):
    batch = event["Records"]
    with processor(records=batch, handler=process_record):
        processed = processor.process()
    return processor.response()
```

## CDK Construct Patterns

### Well-architected Lambda construct
```typescript
import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as logs from "aws-cdk-lib/aws-logs";

export class WellArchitectedFunction extends Construct {
  public readonly function: lambda.Function;

  constructor(scope: Construct, id: string, props: FunctionProps) {
    super(scope, id);

    this.function = new lambda.Function(this, "Function", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: props.handler,
      code: props.code,
      memorySize: props.memorySize ?? 256,
      timeout: cdk.Duration.seconds(props.timeout ?? 30),
      tracing: lambda.Tracing.ACTIVE,
      logRetention: logs.RetentionDays.TWO_WEEKS,
      environment: {
        POWERTOOLS_SERVICE_NAME: props.serviceName,
        LOG_LEVEL: "INFO",
        ...props.environment,
      },
      deadLetterQueueEnabled: true,
      retryAttempts: 2,
    });
  }
}
```

## Container Patterns

### Multi-stage Dockerfile (Python)
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/deps /app/deps
COPY src/ ./src/
ENV PYTHONPATH=/app/deps
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/health || exit 1
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### ECS Task Definition (CDK)
```typescript
const taskDef = new ecs.FargateTaskDefinition(this, "TaskDef", {
  memoryLimitMiB: 512,
  cpu: 256,
});

taskDef.addContainer("app", {
  image: ecs.ContainerImage.fromEcrRepository(repo, "latest"),
  logging: ecs.LogDrivers.awsLogs({ streamPrefix: "app" }),
  portMappings: [{ containerPort: 8080 }],
  healthCheck: {
    command: ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
    interval: cdk.Duration.seconds(30),
    timeout: cdk.Duration.seconds(5),
    retries: 3,
  },
  environment: {
    NODE_ENV: "production",
  },
  secrets: {
    DB_PASSWORD: ecs.Secret.fromSsmParameter(dbPasswordParam),
  },
});
```
