---
name: aws-dev
description: This skill enables building production-grade applications on AWS. Covers Python/Boto3, TypeScript/AWS SDK v3, CDK, SAM, SST, Lambda handlers, DynamoDB patterns, Step Functions, EventBridge, containers, and CI/CD. Triggers on requests about coding, building, implementing, or scaffolding AWS applications.
---

# AWS Application Development Skill

This skill enables building production-grade applications on AWS across multiple languages and frameworks.

## Activation Keywords
- code, write, build, implement, scaffold, refactor, test
- Lambda, handler, API, SDK, Boto3, CDK, SAM, SST
- serverless, container, microservice, app

## Supported Stacks

### Python
- **Runtime**: 3.11+
- **AWS SDK**: Boto3 (latest)
- **Frameworks**: FastAPI, Flask, Chalice, Powertools for AWS Lambda
- **Testing**: pytest, moto, localstack
- **Linting**: ruff, mypy

### TypeScript / JavaScript
- **Runtime**: Node.js 20+
- **AWS SDK**: @aws-sdk v3 (modular imports)
- **Frameworks**: CDK, SST, Express, Fastify
- **Testing**: Vitest, Jest, aws-sdk-client-mock
- **Linting**: ESLint, Prettier

### Go
- **Runtime**: 1.21+
- **AWS SDK**: aws-sdk-go-v2
- **Testing**: go test, testify

### Infrastructure as Code
- **CDK**: TypeScript or Python constructs
- **SAM**: template.yaml + local invoke
- **Terraform**: HCL modules for application resources
- **CloudFormation**: YAML templates

## Code Generation Rules

### Always Do
- Use latest SDK versions with modular imports
- Implement proper credential chains (never hardcode)
- Add structured logging (JSON format)
- Include error handling with specific exception types
- Add type hints (Python) or strict TypeScript
- Implement retries with exponential backoff for AWS calls
- Use environment variables for configuration
- Add input validation on all API endpoints
- Include pagination for list/scan operations

### Never Do
- Hardcode AWS credentials, account IDs, or ARNs
- Use `import *` or wildcard SDK imports
- Catch bare exceptions without handling
- Store state in Lambda /tmp across invocations
- Create over-permissive IAM policies
- Skip error handling on SDK calls
- Use synchronous patterns where event-driven is better

## Project Templates

### Lambda Function (Python)
```
function-name/
├── src/
│   ├── handler.py         # Entry point
│   ├── service.py         # Business logic
│   └── adapters/          # AWS service clients
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── template.yaml          # SAM template
└── Makefile
```

### CDK Application (TypeScript)
```
project/
├── bin/                   # CDK app entry
├── lib/                   # Stack definitions
│   ├── constructs/        # Reusable constructs
│   └── stacks/            # Stack classes
├── src/                   # Lambda/application code
├── test/                  # CDK + unit tests
├── cdk.json
├── tsconfig.json
└── package.json
```

### Containerized Service
```
service/
├── src/                   # Application source
├── tests/
├── Dockerfile             # Multi-stage build
├── docker-compose.yml     # Local dev
├── infrastructure/        # CDK/Terraform
└── .github/workflows/     # CI/CD
```

## Common Patterns Reference

### DynamoDB Single-Table Design
- Partition key: `PK` (entity type + ID)
- Sort key: `SK` (relationship or timestamp)
- GSI for access patterns
- Use `begins_with` for hierarchical queries

### Lambda Best Practices
- Handler thin, logic in service layer
- Initialize SDK clients outside handler (connection reuse)
- Set appropriate memory (128MB-3008MB) and timeout
- Use Powertools for logging, tracing, metrics
- Dead-letter queue for async invocations

### API Gateway Patterns
- Request validation with models
- Lambda authorizers for custom auth
- Usage plans and API keys for rate limiting
- CORS configuration for browser clients

## AWS Service Integration Snippets

### Boto3 Session (Python)
```python
import boto3
from botocore.config import Config

config = Config(
    retries={"max_attempts": 3, "mode": "adaptive"},
    connect_timeout=5,
    read_timeout=10,
)
session = boto3.Session()
client = session.client("dynamodb", config=config)
```

### AWS SDK v3 (TypeScript)
```typescript
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({
  maxAttempts: 3,
});
const docClient = DynamoDBDocumentClient.from(client);
```
