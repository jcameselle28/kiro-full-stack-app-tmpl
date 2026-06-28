---
name: aws-dev
description: This skill enables building production-grade full-stack web applications that run on AWS (EC2, RDS, ALB, CloudFront, WAF). Covers Python (FastAPI/Flask/Django) and TypeScript/Node.js (Express/Fastify/NestJS), ORMs and migrations, AWS SDK integrations, IaC (CDK/Terraform), and CI/CD. Triggers on requests about coding, building, implementing, or scaffolding the application.
---

# Web Application Development Skill (AWS)

This skill enables building production-grade full-stack web applications deployed on AWS EC2 behind an ALB, fronted by CloudFront and WAF, backed by RDS.

## Activation Keywords
- code, write, build, implement, scaffold, refactor, test
- API, endpoint, route, controller, service, repository
- database, migration, ORM, SQL, RDS, Postgres, MySQL
- frontend, backend, full-stack, web app

## Supported Stacks

### Python
- **Runtime**: 3.11+
- **Frameworks**: FastAPI, Flask, Django
- **Server**: uvicorn / gunicorn behind the ALB
- **Data**: SQLAlchemy + Alembic migrations
- **AWS SDK**: Boto3 (latest) for S3, Secrets Manager, SSM, SES, etc.
- **Testing**: pytest, Docker database for integration tests
- **Linting**: ruff, mypy

### TypeScript / JavaScript (Node.js)
- **Runtime**: Node.js 20+
- **Frameworks**: Express, Fastify, NestJS; React/Next.js for the frontend
- **Data**: Prisma or TypeORM + migrations
- **AWS SDK**: @aws-sdk v3 (modular imports)
- **Testing**: Vitest, Jest, aws-sdk-client-mock
- **Linting**: ESLint, Prettier

### Infrastructure as Code
- **CDK**: TypeScript or Python constructs
- **Terraform**: HCL modules for application resources
- **CloudFormation**: YAML/JSON templates

## Target AWS Architecture
- **EC2 + Auto Scaling Group** behind an **Application Load Balancer**
- **RDS** (PostgreSQL/MySQL) in private subnets, Multi-AZ in prod
- **CloudFront** in front of the ALB and for static assets in **S3**
- **AWS WAF** on CloudFront/ALB for common web threat protection
- **Secrets Manager / SSM** for config and secrets, **CloudWatch** for logs/metrics
- **Route 53 + ACM** for DNS and TLS

## Code Generation Rules

### Always Do
- Use latest SDK versions with modular imports
- Use the default credential chain (EC2 instance profile) — never hardcode credentials
- Add structured logging (JSON format) to stdout/CloudWatch
- Include error handling with specific exception types
- Add type hints (Python) or strict TypeScript
- Use a connection pool to RDS; reuse it across requests
- Use parameterized queries / ORM bindings for all database access
- Expose health and readiness endpoints for ALB target groups
- Read configuration from environment variables and secrets stores
- Add input validation on all API endpoints
- Include pagination for list endpoints

### Never Do
- Hardcode credentials, account IDs, ARNs, or connection strings
- Use `import *` or wildcard SDK imports
- Build SQL by string concatenation
- Open a database connection per request
- Catch bare exceptions without handling
- Store session/user state on a single instance (breaks horizontal scaling)
- Skip error handling on SDK or database calls
- Run long blocking work in the request path (offload to a queue/worker)

## Project Templates

### Web API (Python / FastAPI)
```
project/
├── src/
│   ├── api/               # Routers / endpoints
│   ├── services/          # Business logic (no framework deps)
│   ├── repositories/      # Data access (SQLAlchemy)
│   ├── models/            # ORM models / Pydantic schemas
│   ├── adapters/          # AWS clients (S3, Secrets Manager)
│   └── core/              # Config, logging, middleware
├── migrations/            # Alembic migrations
├── tests/{unit,integration}/
├── infrastructure/        # CDK/Terraform
├── pyproject.toml
└── Dockerfile
```

### Web API (TypeScript / Express or NestJS)
```
project/
├── src/
│   ├── routes/            # Controllers / route handlers
│   ├── services/          # Business logic
│   ├── repositories/      # Data access (Prisma/TypeORM)
│   ├── models/            # Entities / schemas (Zod)
│   ├── adapters/          # AWS SDK v3 clients
│   └── core/              # Config, logging, middleware
├── prisma/ or migrations/ # Schema + migrations
├── test/
├── infrastructure/        # CDK/Terraform
├── tsconfig.json
└── Dockerfile
```

### Full-Stack (frontend + backend)
```
project/
├── apps/
│   ├── web/               # React/Next.js (served via S3 + CloudFront)
│   └── api/               # Backend API (see structure above)
├── packages/              # Shared types/utilities
├── infrastructure/        # CDK/Terraform for EC2/ALB/RDS/CloudFront/WAF
├── docker-compose.yml     # Local dev (app + local database)
└── docs/
```

## Common Patterns Reference

### RDS Access
- Use an ORM (SQLAlchemy / Prisma / TypeORM) with a bounded connection pool
- Keep migrations in version control; run them as a deploy step, not at app startup under load
- Use read replicas for read-heavy paths when needed
- Set sensible statement timeouts; handle transient connection errors with retry/backoff

### Application Load Balancer
- Implement `/healthz` (liveness) and `/readyz` (readiness, checks DB) endpoints
- Make the readiness check fail fast when the database is unreachable
- Run the app stateless so the ASG can scale horizontally

### CloudFront + S3
- Serve static assets and frontend builds from S3 via CloudFront
- Use cache behaviors and appropriate TTLs; invalidate on deploy
- Use signed URLs/cookies for private content

### Secrets & Config
- Load DB credentials and API keys from Secrets Manager / SSM at startup
- Cache secrets in memory; refresh on rotation
- Keep all environment-specific values out of the image

## AWS Service Integration Snippets

### Boto3 client (Python)
```python
import boto3
from botocore.config import Config

config = Config(retries={"max_attempts": 3, "mode": "adaptive"})
secrets = boto3.client("secretsmanager", config=config)
```

### AWS SDK v3 (TypeScript)
```typescript
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";

const client = new SecretsManagerClient({ maxAttempts: 3 });
const secret = await client.send(new GetSecretValueCommand({ SecretId: name }));
```

For deeper service-integration patterns (secrets loading, RDS pooling, S3 presigned URLs, SQS workers, SES, container build), see `references/service-patterns.md`.
