# AWS Service Integration Patterns

Patterns for a web app running on **EC2 (behind an ALB)** with **RDS**, integrating supporting AWS services. Use the default credential chain (instance profile) — never hardcode credentials.

## Loading Secrets & Config

```python
import json, boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_db_secret() -> dict:
    client = boto3.client("secretsmanager")
    raw = client.get_secret_value(SecretId="myapp/prod/db")["SecretString"]
    return json.loads(raw)  # {username, password, host, port, dbname}
```
- Cache in memory; on an auth failure, clear the cache and re-fetch (the secret may have rotated).
- Read non-secret config from SSM Parameter Store or environment variables.

## RDS Access (via ORM)

Keep a single pooled engine/connection per process. See the `database-rds` skill for schema, migration, and pooling depth.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

s = get_db_secret()
engine = create_engine(
    f"postgresql+psycopg://{s['username']}:{s['password']}@{s['host']}:{s['port']}/{s['dbname']}",
    pool_size=10, max_overflow=5, pool_pre_ping=True, pool_recycle=1800,
    connect_args={"sslmode": "verify-full", "sslrootcert": "/etc/ssl/rds-ca.pem"},
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

## Web App Entry Point (FastAPI on EC2)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")          # liveness — no dependencies
def healthz():
    return {"status": "ok"}

@app.get("/readyz")           # readiness — ALB target group checks this
def readyz():
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT 1")
    return {"status": "ready"}
```
Run behind the ALB with `uvicorn`/`gunicorn`; the ASG scales instances horizontally, so keep the app stateless.

## S3 — Uploads & Downloads (presigned URLs)

Let the browser talk to S3 directly via short-lived presigned URLs; don't proxy large files through the app tier.

```python
s3 = boto3.client("s3")

def upload_url(key: str) -> str:
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": key, "ContentType": "application/octet-stream"},
        ExpiresIn=900,
    )

def download_url(key: str) -> str:
    return s3.generate_presigned_url(
        "get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=300,
    )
```
Serve public static assets through **CloudFront** in front of the bucket, not the bucket directly.

## Async Work — SQS Worker (not Lambda)

Offload slow work from the request path to a worker process (its own service/ASG) that polls SQS.

```python
sqs = boto3.client("sqs")

def worker_loop(queue_url: str):
    while True:
        resp = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=20)
        for msg in resp.get("Messages", []):
            try:
                handle(json.loads(msg["Body"]))
                sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg["ReceiptHandle"])
            except Exception:
                logger.exception("message failed")  # left on queue; redrive policy → DLQ
```
Configure a dead-letter queue with a redrive policy for poison messages. Make handlers idempotent.

## Sending Email (SES)

```python
ses = boto3.client("ses")
ses.send_email(
    Source="no-reply@example.com",
    Destination={"ToAddresses": [to]},
    Message={"Subject": {"Data": subject}, "Body": {"Html": {"Data": html}}},
)
```

## Container Build (for EC2/ECR)

Multi-stage build; runs the web app on port 8080. Built once in CI, tagged with the git SHA, pushed to ECR. See the `deploy-release` skill for rollout.

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd -m appuser
COPY --from=builder /app/deps /app/deps
COPY src/ ./src/
ENV PYTHONPATH=/app/deps
USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:8080/healthz || exit 1
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## TypeScript Equivalents (AWS SDK v3)

```typescript
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

const secrets = new SecretsManagerClient({ maxAttempts: 3 });
const s3 = new S3Client({ maxAttempts: 3 });

export const uploadUrl = (key: string) =>
  getSignedUrl(s3, new PutObjectCommand({ Bucket: BUCKET, Key: key }), { expiresIn: 900 });
```
Use modular imports only. Access RDS through Prisma/TypeORM with a pooled client; expose `/healthz` and `/readyz` from Express/Fastify/NestJS.
