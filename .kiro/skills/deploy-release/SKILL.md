---
name: deploy-release
description: This skill provides the release process for web apps on AWS — building artifacts (Docker/AMI), pushing to ECR, deploying to EC2/Auto Scaling behind an ALB, zero-downtime rollouts (rolling and blue/green via target groups), ordering database migrations safely, config/secrets at deploy, health checks, smoke tests, and rollback. It also covers first-time AWS account bootstrap (GitHub OIDC deploy role, CDK bootstrap, Terraform state backend, DNS/ACM). Bridges development and deployment without being full ops. Triggers on requests about deploy, release, rollout, blue/green, rollback, artifacts, shipping, account bootstrap, OIDC, or first deploy.
---

# Deploy & Release Skill

The process of safely shipping a web application to AWS. This is the **dev→deploy bridge**: how to turn a tested commit into a running release with zero downtime and a clean rollback path. It assumes the infrastructure exists (see `iac-conventions.md`) and the pipeline mechanics (see `testing-ci` for CI/CD templates); this skill is about **release strategy and ordering**.

## Activation Keywords
- deploy, deployment, release, ship, rollout, cutover
- blue/green, canary, rolling, target group, AMI, image, ECR
- rollback, smoke test, health check, migration order
- account bootstrap, first deploy, OIDC, cdk bootstrap, terraform backend, deploy role

## Account Bootstrap (First Time, Per Account)

Before the first deploy to a **new AWS account**, complete these one-time setup steps. The release process below assumes they're done. Keep everything least-privilege and credential-free per `security-guardrails.md`.

1. **Identity & credentials** — use IAM Identity Center (SSO) for human access; never long-lived root/IAM user keys. Verify with `aws sts get-caller-identity`.
2. **GitHub → AWS OIDC deploy role** — create an IAM OIDC identity provider for GitHub Actions and a deploy role with a trust policy scoped to your repo (and branch/environment); grant only the actions the deploy needs. This replaces stored access keys in CI.
3. **IaC backend**:
   - **CDK**: run `cdk bootstrap aws://<account>/<region>` once per account+region (creates the CDK toolkit stack/assets bucket).
   - **Terraform**: create the remote state backend — an encrypted S3 bucket (versioned, public access blocked) + a DynamoDB table for state locking — before `terraform init`.
4. **DNS & TLS** — create the Route 53 hosted zone for your domain and request/validate an ACM certificate (in `us-east-1` for CloudFront) so the edge layer can use HTTPS.
5. **Region & guardrails** — pick the primary region, confirm encryption defaults, and verify no security groups expose DB/admin ports to `0.0.0.0/0`.

Order: identity → OIDC role → IaC backend → DNS/ACM → first `cdk deploy` / `terraform apply` of the infra → then the release pipeline below.

For concrete recipes (OIDC trust policy, CDK bootstrap, Terraform state backend, DNS/ACM), see `references/aws-account-bootstrap.md`. When the AWS MCP is enabled, the agent can also pull current AWS docs and inspect the live account to confirm these are in place.

## Release Pipeline Overview

```
build → publish artifact → migrate DB (expand) → deploy app → health check → smoke test → shift traffic → verify → (rollback if needed) → contract DB later
```

Each step gates the next. A failure before traffic shift means users never saw the bad release.

## Artifacts — Build Once, Promote

- Build **one immutable artifact** per commit (a container image or a baked AMI) and promote that same artifact dev → staging → prod
- Never rebuild per environment; environment differences come from **config**, not the artifact
- Tag artifacts with the **git SHA** (and optional semver); never rely on `latest` in deploys
- Containers: multi-stage build, minimal base, non-root user, push to **ECR** with image scanning enabled
- AMIs: bake with the app + runtime via your image builder; reference the AMI id in the launch template

## Configuration & Secrets at Deploy
- Inject config via environment variables / SSM Parameter Store; pull secrets from **Secrets Manager** at boot
- The artifact contains **no environment-specific values and no secrets**
- Changing config should not require a rebuild — only a redeploy/restart
- Version config changes alongside the release so a rollback restores matching config

## Database Migrations During Deploy

Order matters. Use the **expand/contract** approach from `database-rds` so old and new app versions coexist during a rolling cutover:

1. **Expand** — run additive, backward-compatible migrations **before** new code is live
2. **Deploy** — roll out the new app version (which works against both old and new schema)
3. **Contract** — drop the now-unused columns/constraints in a **later** release, after no running code references them

Rules:
- Migrations run as a discrete **deploy step**, not at app startup under load
- Use separate **DDL credentials** for migrations vs the app's DML credentials
- Never deploy code and a breaking schema change that the previous version can't tolerate in the same release
- Have a forward-fix or reverse migration ready before shipping

## Zero-Downtime Rollout Strategies

### Rolling (default for EC2 Auto Scaling)
- Use an instance refresh / rolling update on the ASG with a healthy-percentage minimum
- New instances must pass **ALB target group health checks** before old ones are drained
- Set connection draining (deregistration delay) so in-flight requests finish
- Cheapest; brief period where both versions serve traffic (safe with expand/contract)

### Blue/Green (for higher-risk releases)
- Stand up a parallel "green" target group with the new version
- Health-check green out of band, run smoke tests against it
- Shift the ALB listener from blue → green (instant cutover or weighted)
- Keep blue warm for fast rollback; tear down after a soak period

### Canary (weighted)
- Use ALB weighted target groups to send a small % to the new version
- Watch health/error metrics, then ramp 5% → 25% → 100%
- Best when you can observe real traffic before full cutover

## Health Checks
- **Liveness** (`/healthz`): process is up — cheap, no dependencies
- **Readiness** (`/readyz`): can serve traffic — checks DB connectivity and critical deps; this is what the **ALB target group** uses
- Readiness must fail fast when the DB is unreachable so bad instances are pulled
- Don't make liveness depend on downstream services (avoids cascading restarts)

## Smoke Tests & Verification
- After deploy, before/while shifting traffic, run a small suite of **critical-path** smoke tests against the new version (login, a key read, a key write)
- Verify health and error rates for a soak window before declaring success
- Surface a release marker (version/SHA) on a status endpoint so you can confirm what's live

## Rollback
- Rollback = **redeploy the previous immutable artifact** (and its matching config) — fast and deterministic
- Blue/green: shift the ALB listener back to blue (seconds)
- Rolling: trigger an instance refresh to the prior artifact version
- **Schema**: because of expand/contract, the previous app version still works against the expanded schema — so an app rollback needs no DB rollback. Only contract after rollback is no longer a concern
- Define rollback triggers up front (error-rate threshold, failed smoke tests, health-check failures)

## Environments & Gates
Follow the environment strategy in `iac-conventions.md` (dev → staging → prod). Typical gates:
- **dev**: auto-deploy on merge to main
- **staging**: auto or manual; mirrors prod; run integration + smoke tests
- **prod**: manual approval; canary/blue-green; soak + verify

## Pre-Release Checklist
- [ ] Artifact built from the exact commit, tagged with SHA, scanned
- [ ] Expand migrations applied and backward-compatible
- [ ] Config/secrets present for the target environment (no rebuild needed)
- [ ] Readiness check covers the DB and critical deps
- [ ] Smoke tests defined for critical paths
- [ ] Rollback path verified (previous artifact available, triggers defined)
- [ ] CloudWatch alarms/metrics in place to judge the soak

For deeper recipes (ASG instance refresh settings, ALB weighted blue/green mechanics, migration sequencing examples, rollback runbook), see `references/patterns.md`.
