# AWS Web App Starter (Kiro)

A reusable [Kiro](https://kiro.dev) configuration for building **full-stack web applications that run on AWS**. It ships steering rules, skills, and MCP settings tuned for apps deployed on EC2 behind an ALB, fronted by CloudFront and WAF, backed by RDS.

The focus is **application development** — writing, testing, and deploying app code and the infrastructure that provisions it. It is intentionally free of operations tooling (SRE, FinOps, networking ops) to stay lightweight.

## What's Inside

```
.kiro/
├── agents/          → aws-dev application development agent
├── settings/        → MCP server configuration (single AWS MCP via the MCP Proxy for AWS)
├── skills/          → aws-dev, auth-security, database-rds, deploy-release, frontend-web, testing-ci, mermaid-visualizer
└── steering/        → coding standards, security, git workflow, output format, IaC conventions, project config template
.github/             → pull request template
docs/                → golden path, getting started, architecture, customization, deployment, MCP, style guide
```

| Area | Contents |
|---|---|
| **Agent** | `aws-dev` — full-stack web app development on AWS (Python & TypeScript/Node) |
| **Skills** | `aws-dev` (app/IaC patterns), `auth-security` (authn/authz), `database-rds` (RDS data layer), `deploy-release` (safe releases), `frontend-web` (UI engineering), `testing-ci` (tests + pipelines), `mermaid-visualizer` (diagrams) |
| **Steering (always-on)** | `security-guardrails.md`, `output-format.md`, `git-workflow.md`, and your `project-config.md` once created |
| **Steering (conditional)** | `python-standards.md` (`*.py`), `typescript-standards.md` (`*.ts/*.tsx`), `iac-conventions.md` (IaC files), `api-conventions.md` (source), `design-system.md` + `accessibility-standards.md` (frontend files) |
| **MCP servers** | `aws` — the MCP Proxy for AWS (`mcp-proxy-for-aws`) connecting to the managed AWS MCP Server; read-only and disabled by default |

## Target Stack

- **Languages**: Python 3.11+ and/or TypeScript (Node.js 20+)
- **Backend**: FastAPI / Flask / Django, or Express / Fastify / NestJS
- **Database**: RDS (PostgreSQL/MySQL) via an ORM (SQLAlchemy / Prisma / TypeORM)
- **AWS**: EC2 (Auto Scaling Group) + ALB + CloudFront + WAF + S3, with Secrets Manager/SSM, CloudWatch, Route 53/ACM
- **IaC**: CDK (TypeScript) or Terraform

## Quick Start

1. **Copy the template** into your new project (the whole repo, or just the `.kiro/` folder):
   ```bash
   cp -r /path/to/template/.kiro /path/to/your-project/.kiro
   ```

2. **Create your project config** from the template:
   ```bash
   cp .kiro/steering/project-config-template.md .kiro/steering/project-config.md
   ```
   Then change `inclusion: manual` to `inclusion: always` and fill in the `[placeholder]` values.

3. **Trim to your stack (optional)**: if you use only one language, delete the standards file you don't need (`python-standards.md` or `typescript-standards.md`).

4. **Install prerequisites**:
   ```bash
   brew install uv          # required for MCP servers
   aws sts get-caller-identity   # verify AWS credentials
   ```

5. **Open in Kiro** (IDE or CLI). The `.kiro/` folder is detected automatically — steering and skills activate immediately.

See [docs/getting-started.md](./docs/getting-started.md) for the full setup walkthrough, then follow [docs/golden-path.md](./docs/golden-path.md) to go from clone to a deployed v1.0.

## Documentation

| Doc | What it covers |
|---|---|
| [Golden Path](./docs/golden-path.md) | **Start here** — clone to a deployed v1.0, step by step, for any skill level |
| [Getting Started](./docs/getting-started.md) | Setup, interfaces, project config, enabling MCP |
| [Architecture](./docs/architecture.md) | How the `.kiro/` folder is structured and how it drives the agent |
| [Customization](./docs/customization.md) | Adding/removing steering, skills, and agents |
| [Deployment](./docs/deployment.md) | AWS prerequisites, infrastructure setup, releases, and rollback |
| [MCP Servers](./docs/mcp-servers.md) | Enabling/disabling the bundled MCP servers |
| [Style Guide](./docs/style-guide.html) | Project-agnostic visual design system reference |

## Notes

- **MCP is off by default** to save tokens. The single `aws` server uses the MCP Proxy for AWS and requires valid AWS credentials when enabled. Enable it in chat ("Enable the AWS MCP") or by flipping the `disabled` flag in `.kiro/settings/mcp.json`. See [docs/mcp-servers.md](./docs/mcp-servers.md).
- **No hooks are included** — add per-project as needed (see the [Kiro docs](https://kiro.dev/docs/hooks)).
- **Security**: never commit secrets; load them from Secrets Manager / SSM at runtime. See `.kiro/steering/security-guardrails.md`.
