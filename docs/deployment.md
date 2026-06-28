# Deployment

The human side of shipping the app to AWS. This complements the agent-facing skills: `deploy-release` (rollout strategy and ordering), `iac-conventions` (infrastructure standards), and the ready-to-use pipelines in `.kiro/skills/testing-ci/references/cicd-templates.md`.

You don't run most of this by hand — you ask Kiro to do it and review the result. This guide explains **what's involved, what you need, and how to confirm it worked**.

---

## What You Need First

| Requirement | How to get it / check |
|---|---|
| An AWS account you can deploy to | `aws sts get-caller-identity` should return your account |
| AWS CLI configured | `aws configure` (or SSO) — credentials with permission to create infra |
| A registered domain (optional for dev) | Needed for a real URL + TLS; dev can use the ALB/CloudFront default name |
| `uv` installed | `brew install uv` (for the AWS docs/IaC MCP servers) |
| GitHub repo with CI secrets set | Add the deploy role ARN as a repo secret (see CI/CD below) |

If you're new to AWS, ask Kiro: *"Walk me through what AWS permissions I need to deploy this and how to check I have them."*

---

## The Target Architecture (what gets created)

This template deploys a standard, production-shaped AWS web app:

| Layer | AWS services | Purpose |
|---|---|---|
| Edge | CloudFront + AWS WAF | CDN, TLS, common web-threat protection |
| Load balancing | Application Load Balancer (ALB) | Routes traffic, health checks |
| Compute | EC2 in an Auto Scaling Group | Runs the app; scales horizontally |
| Database | RDS (PostgreSQL/MySQL), private subnets | Persistent data, encrypted at rest |
| Static assets | S3 (via CloudFront) | Frontend build, uploads |
| Config & secrets | Secrets Manager / SSM Parameter Store | Runtime config, DB credentials |
| Observability | CloudWatch | Logs and metrics |
| DNS / TLS | Route 53 + ACM | Domain and certificates |

The full standards for how this is provisioned live in `.kiro/steering/iac-conventions.md`.

---

## Deployment Phases

### Phase 0 — First-time account bootstrap (new AWS account only)

Do this **once per AWS account**, before any infrastructure exists. It's the setup that lets you (and CI) deploy at all. Ask Kiro:

> Walk me through bootstrapping this AWS account for deployment per the deploy-release account-bootstrap guide: confirm my identity, create the GitHub OIDC deploy role scoped to this repo, bootstrap CDK (or set up the Terraform state backend), and set up the Route 53 hosted zone + ACM certificate.

The checklist (full recipes in `.kiro/skills/deploy-release/references/aws-account-bootstrap.md`):

- [ ] **Identity** — IAM Identity Center (SSO) configured; `aws sts get-caller-identity` returns the right account (no long-lived root/user keys)
- [ ] **GitHub OIDC deploy role** — OIDC provider + an IAM role whose trust is scoped to `repo:<owner>/<repo>` (branch or environment); least-privilege permissions; role ARN saved as the `AWS_DEPLOY_ROLE_ARN` repo secret
- [ ] **IaC backend** — `cdk bootstrap aws://<account>/<region>` *or* a Terraform state backend (encrypted, versioned S3 bucket + DynamoDB lock table)
- [ ] **DNS & TLS** — Route 53 hosted zone live; ACM certificate **issued** (in `us-east-1` if it fronts CloudFront)
- [ ] **Guardrails** — primary region chosen; encryption defaults confirmed; no DB/admin ports open to `0.0.0.0/0`

Skip this phase entirely if you're deploying into an account that's already bootstrapped.

### Phase 1 — One-time infrastructure setup

You create the AWS infrastructure once per environment (start with `dev`). Ask Kiro:

> Using CDK per iac-conventions.md, create and deploy the dev infrastructure for this app: network (VPC + subnets), RDS Postgres, an EC2 Auto Scaling Group behind an ALB, CloudFront, and WAF. Explain each stack before deploying and run `cdk diff` first.

What to expect:
- Kiro generates IaC under `infrastructure/`, split into stacks (network, data, app, edge).
- Review `cdk diff` output before approving the deploy — this shows exactly what will be created.
- Stateful resources (RDS, S3) use `RETAIN` removal policies; dev compute uses `DESTROY`.

> ⚠️ Creating infrastructure costs money. RDS, NAT gateways, and ALBs bill hourly even when idle. For dev, prefer single-AZ and the smallest instance sizes. Ask Kiro to *"estimate the monthly cost of this dev stack"* and tear it down when not in use: *"destroy the dev infrastructure."*

### Phase 2 — Repeatable releases (CI/CD)

Once infrastructure exists, releases are automated through GitHub Actions. Ask Kiro:

> Add the GitHub Actions build-and-deploy workflow from the testing-ci CI/CD templates, wired to my ECR repository and Auto Scaling Group, using OIDC for AWS auth (no stored access keys).

This creates a workflow that, on merge to `main`:
1. Runs tests and linting
2. Builds **one immutable container image**, tags it with the git SHA, pushes to ECR
3. Runs database migrations (backward-compatible "expand" step)
4. Rolls out to the Auto Scaling Group with zero downtime
5. Runs smoke tests against the new version

**One-time CI setup:** add the AWS deploy role ARN as a GitHub repo secret (`AWS_DEPLOY_ROLE_ARN`). Ask Kiro to *"create an OIDC deploy role for GitHub Actions with least-privilege permissions for this stack."*

---

## How Releases Stay Safe

These behaviors come from the `deploy-release` skill and are applied automatically:

- **Build once, promote** — the same image moves dev → staging → prod; only config differs.
- **Expand/contract migrations** — schema changes are backward-compatible so the old and new app versions coexist during rollout. No DB rollback needed if you roll back the app.
- **Health-gated rollout** — new instances must pass ALB target-group health checks (`/readyz`) before old ones drain.
- **Zero-downtime** — rolling update by default; blue/green or canary for higher-risk releases.

---

## Confirming It's Live

After a deploy:

1. **Check the rollout finished** — ask Kiro: *"Show the status of the latest instance refresh on the ASG."*
2. **Hit the health endpoint** — `curl https://<your-domain>/healthz` should return OK.
3. **Check the version marker** — the app should expose its git SHA/version on a status endpoint so you can confirm what's running.
4. **Watch metrics for a soak window** — error rate and latency in CloudWatch should stay flat. Ask Kiro: *"Show me the CloudWatch error rate for the last 15 minutes."*

---

## Rolling Back

If something looks wrong:

> Roll back to the previous release.

- **Rolling deploys**: Kiro triggers an instance refresh back to the prior image tag.
- **Blue/green**: the ALB listener shifts back to the previous (blue) target group in seconds.
- Because migrations are expand/contract, the previous app version still works against the current schema — so an app rollback needs no database rollback.

Define your rollback triggers up front (error-rate threshold, failed smoke tests). See the `deploy-release` skill's pre-release checklist.

---

## Environments

Follow the strategy in `iac-conventions.md`:

| Environment | Config | Deploy gate |
|---|---|---|
| `dev` | Single-AZ, smallest sizes, `DESTROY` policies | Auto-deploy on merge to `main` |
| `staging` | Mirrors prod | Auto or manual; run integration + smoke tests |
| `prod` | Multi-AZ RDS, `RETAIN` policies, strict | Manual approval; canary/blue-green; soak + verify |

For v1.0, it's fine to start with just `dev` and add `prod` when you're ready to go live.
