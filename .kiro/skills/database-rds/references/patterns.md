# Database Patterns — Deep Dive

Supporting reference for the `database-rds` skill. PostgreSQL-first; MySQL differences are noted inline.

## Online (Zero-Downtime) Migration Recipes

### Add a NOT NULL column
1. Add the column **nullable** with a default in app code (not a volatile DB default on a huge table)
2. Backfill in batches
3. Once backfilled and all rows non-null, add the `NOT NULL` constraint:
   ```sql
   ALTER TABLE accounts ADD CONSTRAINT accounts_status_nn CHECK (status IS NOT NULL) NOT VALID;
   ALTER TABLE accounts VALIDATE CONSTRAINT accounts_status_nn;   -- non-blocking validate
   ```

### Rename a column
Never rename in place. Expand/contract:
1. Add the new column; write to both old and new in app code
2. Backfill new from old
3. Switch reads to new
4. Drop the old column in a later release

### Add an index without locking
```sql
CREATE INDEX CONCURRENTLY idx_ledger_entries_account_id ON ledger_entries (account_id);
```
- `CONCURRENTLY` cannot run inside a transaction block — configure the migration tool accordingly (Alembic: `with op.get_context().autocommit_block():`).
- MySQL: most `ALTER`s are online via `ALGORITHM=INPLACE, LOCK=NONE`, but verify per change.

### Backfill in batches
```sql
UPDATE accounts
SET tier = 'standard'
WHERE tier IS NULL AND id IN (
  SELECT id FROM accounts WHERE tier IS NULL ORDER BY id LIMIT 5000
);
```
Loop until zero rows affected; sleep briefly between batches to limit replication lag.

## Connection Pooling Math

```
effective_db_connections = instances × workers_per_instance × pool_size
```
Keep this comfortably under RDS `max_connections` (which scales with instance class). Leave headroom for migrations, admin tools, and monitoring.

When the app tier scales elastically (ASG), per-instance pools can overwhelm RDS. Use **RDS Proxy**:
- Multiplexes many app connections onto fewer DB connections
- Survives failover by holding client connections during the swap
- Integrates with Secrets Manager + IAM auth
- App points its pool at the Proxy endpoint instead of the DB endpoint

## Indexing Strategy

- Composite index column order: **equality columns first, then range/sort columns**
- A composite index on `(a, b)` serves queries filtering on `a` or `a, b` — not `b` alone
- Partial indexes for soft deletes: `CREATE INDEX ... WHERE deleted_at IS NULL`
- Covering indexes (`INCLUDE`) to satisfy a query from the index alone
- Drop unused indexes — they cost write throughput and storage (`pg_stat_user_indexes` shows usage)

## Reading Query Plans

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
```
Watch for:
- `Seq Scan` on large tables in a selective query → missing/unused index
- Large `Rows Removed by Filter` → poor index selectivity
- Nested loop with high loop count → N+1 surfacing in SQL
- Actual vs estimated rows far apart → stale stats; run `ANALYZE`

## Transaction & Concurrency Patterns

### Optimistic concurrency (version column)
```sql
UPDATE accounts SET balance = $1, version = version + 1
WHERE id = $2 AND version = $3;   -- 0 rows affected => someone else updated; retry
```

### Idempotent writes
Accept a client-supplied idempotency key; store it with a unique constraint so a retried request is a no-op rather than a duplicate insert.

### Serialization failure retry
Under `SERIALIZABLE`/`REPEATABLE READ`, catch the serialization error (Postgres `40001`) and retry the transaction a bounded number of times with backoff.

## Multi-Tenancy Options
- **Shared schema, tenant_id column** (simplest): every tenant-scoped table has `tenant_id`, indexed and filtered on every query. Enforce with Row-Level Security in Postgres for defense in depth.
- **Schema per tenant**: stronger isolation, heavier migration burden.
- **Database per tenant**: strongest isolation, highest operational cost.
Default to shared-schema with `tenant_id` + RLS unless compliance dictates otherwise.

## Secrets & Rotation
- Store the connection secret as JSON in Secrets Manager (`username`, `password`, `host`, `port`, `dbname`)
- Load at startup; cache in memory
- On an auth failure, re-fetch the secret (it may have rotated) and rebuild the pool before failing the request
- Use distinct secrets for DDL (migrations) and DML (runtime app)

## Testing the Data Layer
- Run integration tests against a **real local database** (Docker Postgres/MySQL) — not mocks — to exercise real SQL, constraints, and migrations
- Apply migrations to the test DB as part of setup so schema drift is caught
- Wrap each test in a transaction and roll back, or truncate between tests, for isolation
- Keep a small set of seed/factory helpers for fixtures
