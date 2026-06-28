---
name: database-rds
description: This skill provides relational data layer patterns for web apps on AWS RDS — schema design, migrations, connection pooling on EC2, query performance, transactions, and database security. Covers PostgreSQL (primary) and MySQL, with SQLAlchemy + Alembic (Python) and Prisma (TypeScript). Triggers on requests about databases, schemas, models, migrations, queries, SQL, ORMs, RDS, Postgres, or MySQL.
---

# Database & RDS Skill

Patterns for the relational data layer of web applications running on AWS RDS. Default engine is **PostgreSQL** (MySQL notes called out where they differ).

## Activation Keywords
- database, db, schema, model, entity, table, column, index
- migration, migrate, alembic, prisma, typeorm
- query, SQL, ORM, transaction, join, N+1
- RDS, Postgres, PostgreSQL, MySQL, connection pool

## Default Stack

| Language | ORM / Toolkit | Migrations |
|---|---|---|
| Python | SQLAlchemy 2.x (typed) | Alembic |
| TypeScript | Prisma | Prisma Migrate |

Raw SQL is fine for hot paths and reports — always parameterized, never string-interpolated.

## Schema & Modeling Conventions

- **Table names**: `snake_case`, plural (`accounts`, `ledger_entries`)
- **Column names**: `snake_case`
- **Primary keys**: surrogate `id` as **UUID** (Postgres `uuid` with `gen_random_uuid()`); generate app-side or DB-side consistently
- **Timestamps**: every table has `created_at` and `updated_at`, stored in **UTC** (`timestamptz` in Postgres)
- **Soft deletes**: use a nullable `deleted_at timestamptz`; filter it out by default. Reserve hard deletes for compliance/data-retention needs
- **Foreign keys**: always declared with explicit `ON DELETE` behavior; name them predictably (`fk_{table}_{ref}`)
- **Constraints over app checks**: enforce `NOT NULL`, `UNIQUE`, `CHECK`, and FKs in the schema — don't rely on application code alone
- **Money**: use `NUMERIC`/`DECIMAL`, never float
- **Enums**: prefer a lookup table or a `CHECK` constraint over native DB enums (easier to evolve)

## Connection Management (EC2 / Auto Scaling)

- Use a **bounded connection pool** per process; never open a connection per request
- Size the pool from RDS `max_connections` ÷ expected concurrent app processes (instances × workers), leaving headroom
- When instance count scales aggressively, put **RDS Proxy** in front to multiplex connections and survive failovers
- Set sensible **statement and idle timeouts**; fail fast on a stuck query
- Connect over **TLS**; verify the RDS CA
- Pull credentials from **Secrets Manager** at startup; support rotation (refresh on auth failure)

## Migrations — Expand / Contract

Run migrations as a **deploy step**, not at app startup under load. Make every change backward-compatible so old and new code can run simultaneously during a rolling deploy:

1. **Expand** — add new columns/tables/indexes as nullable/optional; backfill data
2. **Migrate code** — deploy app that writes both old and new, reads new
3. **Contract** — in a later release, drop the old column/constraint

Rules:
- Never drop or rename a column in the same release that stops using it
- Add indexes **concurrently** in Postgres (`CREATE INDEX CONCURRENTLY`) to avoid table locks
- Backfill large tables in batches, not one giant `UPDATE`
- Every migration is reversible or has a documented forward-fix
- Migrations are reviewed like code and committed to the repo

## Query & Performance

- Index foreign keys and columns used in `WHERE`, `JOIN`, `ORDER BY`
- Avoid **N+1**: eager-load with joins/`selectinload` (SQLAlchemy) or `include`/`select` (Prisma)
- Use **keyset (cursor) pagination** for large lists, not deep `OFFSET`
- `SELECT` only needed columns on hot paths
- Read `EXPLAIN (ANALYZE, BUFFERS)` before optimizing; index based on real plans
- Route heavy read-only queries to a **read replica** when one exists
- Wrap multi-statement writes in a **transaction**; keep transactions short

## Transactions

- Default isolation (`READ COMMITTED`) is right for most web traffic
- Use explicit transactions for multi-row invariants; handle serialization failures with retry
- Use optimistic concurrency (a `version` column) rather than long-held locks
- Make write operations **idempotent** where retries are possible

## Security

- App connects as a **least-privilege** user (DML only) — not the master/owner role
- Separate migration credentials (DDL) from runtime credentials (DML)
- Credentials live in **Secrets Manager**; never in code, env files, or images
- Enforce **TLS** to RDS; keep RDS in **private subnets**, reachable only from the app tier
- Always parameterize queries; rely on ORM bindings
- Encrypt at rest (RDS storage encryption) — on by default in this template's IaC

## Code Examples

### SQLAlchemy 2.x model + base (Python)
```python
from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(default=None)

class Account(TimestampMixin, Base):
    __tablename__ = "accounts"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
```

### Pooled engine with Secrets Manager (Python)
```python
from sqlalchemy import create_engine

engine = create_engine(
    db_url,                 # built from Secrets Manager values
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,     # detect dropped connections after failover
    pool_recycle=1800,
    connect_args={"sslmode": "verify-full", "sslrootcert": "/etc/ssl/rds-ca.pem"},
)
```

### Prisma schema (TypeScript)
```prisma
model Account {
  id        String    @id @default(uuid()) @db.Uuid
  name      String    @db.VarChar(200)
  email     String    @unique @db.VarChar(320)
  createdAt DateTime  @default(now()) @map("created_at")
  updatedAt DateTime  @updatedAt @map("updated_at")
  deletedAt DateTime? @map("deleted_at")

  @@map("accounts")
}
```

### Keyset pagination (SQL)
```sql
SELECT id, name, created_at
FROM accounts
WHERE deleted_at IS NULL
  AND (created_at, id) < ($1, $2)   -- last row from previous page
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

For deeper patterns (online migration recipes, RDS Proxy setup, indexing strategy, multi-tenancy), see `references/patterns.md`.
