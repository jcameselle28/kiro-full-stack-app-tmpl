# Deploy & Release Patterns — Deep Dive

Supporting reference for the `deploy-release` skill. EC2 + Auto Scaling + ALB on AWS.

## ASG Instance Refresh (rolling)

Trigger a rolling replacement when the launch template points at a new AMI or container image tag.

Key settings:
- **Minimum healthy percentage**: e.g., 90% — controls how many instances are replaced at once vs capacity kept serving
- **Instance warmup**: time before a new instance counts as healthy (let the app boot, warm caches, pass readiness)
- **Checkpoints** (optional): pause at a percentage to verify before continuing
- New instances must pass **ALB target group health checks** before old ones are terminated

Pair with launch-template versioning so a rollback is "set desired version back, refresh."

## ALB Target Groups — Blue/Green & Canary

Mechanics:
- Maintain two target groups: `blue` (current) and `green` (new)
- Register new instances/version into `green`; keep them out of the listener until verified
- Health-check and smoke-test `green` directly (internal hostname or test listener)
- **Cutover**: update the listener's forward action

Instant cutover:
```
listener default action -> forward 100% to green
```
Weighted canary:
```
forward: { blue: 95, green: 5 } -> 75/25 -> 0/100
```
- Use `target_group_stickiness` carefully during weighted shifts
- Set **deregistration delay** (connection draining), e.g., 30–60s, so in-flight requests complete before an instance leaves

Rollback: point the listener weight back to `blue` (100%). Seconds, not minutes.

## Migration Sequencing Examples

### Safe additive (expand) — deploy before code
```sql
ALTER TABLE accounts ADD COLUMN status text;          -- nullable, no default lock
CREATE INDEX CONCURRENTLY idx_accounts_status ON accounts(status);
-- backfill in batches
```
New code reads/writes `status`; old code ignores it → both versions safe.

### Breaking change done safely (rename) across 3 releases
1. Release N: add `email_address`; app writes both `email` and `email_address`, reads `email`
2. Release N+1: backfill done; app reads `email_address`, still writes both
3. Release N+2 (contract): drop `email`; app writes only `email_address`

At no point can a running previous version break.

### Why no DB rollback is needed
Because every in-flight schema is backward-compatible, rolling the **app** back to the prior artifact works against the expanded schema. Only run **contract** once you're certain you won't roll back past it.

## Rollback Runbook (template)

1. **Detect**: alarm fires / smoke test fails / error rate breaches threshold
2. **Decide**: is it the new release? Check the version marker on `/healthz` or a status endpoint
3. **Act**:
   - Blue/green: shift listener weight back to `blue` = 100%
   - Rolling: start instance refresh to previous launch-template version
4. **Verify**: error rate and health return to baseline; version marker shows the prior SHA
5. **Hold**: freeze further deploys; capture logs/metrics for the postmortem
6. **Do not** run `contract` migrations while a rollback is still possible

Define thresholds and owners before the release, not during the incident.

## Build-Once-Promote Pipeline Shape

```
CI on merge:
  test → build artifact (tag = git SHA) → scan → push to ECR / register AMI
CD:
  deploy-dev    (auto)   : migrate(expand) → rolling deploy → smoke
  deploy-stg    (gate)   : promote same artifact → migrate → deploy → integration+smoke
  deploy-prod   (manual) : promote same artifact → migrate → canary/blue-green → soak → verify
```
The artifact built in CI is the exact one promoted to prod. See `testing-ci/references/cicd-templates.md` for concrete pipeline YAML; this skill governs the ordering and gates.

## Config & Secrets Handling

- Environment config in **SSM Parameter Store**; secrets in **Secrets Manager**
- Instances load them at boot (user data / entrypoint) via the instance role
- A config-only change is a **redeploy/restart**, not a rebuild
- Keep a config version/marker so a rollback restores the matching config alongside the artifact

## Health Check Design

```python
# readiness — what the ALB target group polls
@app.get("/readyz")
async def readyz():
    try:
        await db.execute("SELECT 1")          # critical dependency
    except Exception:
        raise HTTPException(503, "not ready")  # ALB pulls this instance
    return {"status": "ready", "version": GIT_SHA}

# liveness — process up, no external deps
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "version": GIT_SHA}
```

## Common Pitfalls
- Rebuilding the artifact per environment (drift; "works in staging" failures)
- Running migrations at app startup → thundering herd across an ASG, partial schema during rollout
- Breaking schema change shipped with the code that needs it (no safe rollback)
- Liveness check that depends on the DB → mass restarts during a DB blip
- No connection draining → dropped in-flight requests on cutover
- Using `latest` image tags → ambiguous what's actually deployed
- Contracting the schema too early → can't roll the app back
