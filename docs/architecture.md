# Architecture

## How It Works

The `.kiro/` folder is the brain of the agent. When you open a project in Kiro (IDE or CLI), it reads this folder and configures itself accordingly.

```
.kiro/
├── agents/          → Agent definitions (personality, tools, MCP servers)
├── settings/        → MCP server configuration
├── skills/          → Activatable knowledge modules
└── steering/        → Always-on or conditional behavioral rules
```

This is the **AWS Web App Starter (Kiro)** template — a configuration for **full-stack web applications that run on AWS** using EC2, RDS, ALB, CloudFront, and WAF. It focuses on application development — writing, testing, and deploying app code and the infrastructure that provisions it.

## Component Breakdown

### Agents

Agent definitions live in `.kiro/agents/` as paired files:
- `{name}.json` — Configuration (tools, MCP servers, model, permissions)
- `{name}-prompt.md` — Personality, capabilities, response formats

| Agent | Role | Domain |
|---|---|---|
| aws-dev | Application development | Python & TypeScript web apps, RDS data layer, IaC for EC2/ALB/CloudFront/WAF |

Note: Custom agent definitions are primarily a reference today. The single Kiro agent uses the steering files and skills below to cover the project's needs.

The agent JSON specifies a `"model"` field (e.g. `"claude-sonnet-4-5"`). This field is informational — the actual model used is determined by your Kiro IDE or CLI settings, so set it to whatever your Kiro install offers.

### Steering Files

Steering files in `.kiro/steering/` inject rules into conversations. Three inclusion modes:

| Mode | Behavior | Example |
|---|---|---|
| `always` (default) | Active in every conversation | project-config.md (once created), security-guardrails.md, output-format.md, git-workflow.md |
| `fileMatch` | Active only when matching files are in context | python-standards.md (`*.py`), typescript-standards.md (`*.ts/*.tsx`), iac-conventions.md (IaC files), design-system.md (frontend files), api-conventions.md (backend/frontend source), accessibility-standards.md (frontend files) |
| `manual` | Only when user explicitly includes via `#` in chat | project-config-template.md, instructions-mcp.md |

| Steering file | Inclusion | Purpose |
|---|---|---|
| project-config.md | always | The project's identity, stack, conventions, deployment, security (created per project from the template) |
| security-guardrails.md | always | Application & data security rules (secrets, encryption, input validation, edge protection) |
| output-format.md | always | How results and change reports are presented |
| git-workflow.md | always | GitHub Flow conventions — branch naming, Conventional Commits, PR process, git guardrails |
| python-standards.md | fileMatch (`*.py`) | Python coding standards + web/RDS integration |
| typescript-standards.md | fileMatch (`*.ts`,`*.tsx`) | TypeScript coding standards + web/RDS integration |
| iac-conventions.md | fileMatch (IaC files) | IaC conventions for the EC2/RDS/ALB/CloudFront/WAF stack |
| design-system.md | fileMatch (frontend files) | Enforces the style guide as the source of truth for visual tokens |
| api-conventions.md | fileMatch (backend/frontend source) | HTTP API contract — naming, status codes, errors, pagination, versioning |
| accessibility-standards.md | fileMatch (frontend files) | WCAG 2.2 AA target and per-feature acceptance criteria |
| instructions-mcp.md | manual | How to toggle MCP servers |
| project-config-template.md | manual | Blank template used to create project-config.md |

### Skills

Skills in `.kiro/skills/` are knowledge modules activated on demand when the conversation matches their keywords.

| Skill | Activates When |
|---|---|
| aws-dev | Application coding, building APIs, RDS/ORM work, scaffolding, IaC |
| auth-security | Authentication & authorization — Cognito/JWT/sessions, tokens, RBAC, route protection |
| database-rds | Schema design, migrations, queries, connection pooling, transactions, DB security |
| deploy-release | Release process — artifacts, migration ordering, zero-downtime rollout, rollback |
| frontend-web | UI engineering — React/Next.js components, state, data fetching, forms, a11y |
| testing-ci | Testing patterns, mocking, CI/CD pipelines, coverage |
| mermaid-visualizer | Diagram generation, architecture visualization |

Each skill has a `SKILL.md` (main instructions) and optional `references/` and `scripts/` folders.

### MCP Servers

MCP (Model Context Protocol) servers in `.kiro/settings/mcp.json` extend the agent with external tool access. The template ships a single AWS entry, disabled by default to save tokens.

| Server | Package | Purpose |
|---|---|---|
| aws | `mcp-proxy-for-aws` | Local proxy that SigV4-signs requests with your AWS credentials and connects to the managed AWS MCP Server — documentation, IaC/CDK/CloudFormation guidance, and multi-service AWS access through one endpoint. Ships read-only. |

This replaces the older per-service AWS Labs servers (separate documentation and IaC servers). See [MCP Servers](./mcp-servers.md) for details.

### Hooks (Not Included)

Kiro supports agent hooks (automated actions triggered by IDE events like file saves, tool use, or task completion). This repo intentionally does not include hooks to keep the foundation lightweight. Each project can add hooks as needed — see the [Kiro documentation](https://kiro.dev/docs/hooks) for details.

## Data Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  Steering Files  │ ← Always-on rules (project config, security, output format)
│  (behavioral)    │ ← Conditional rules (Python/TS/IaC standards when relevant)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Skills       │ ← Activated on demand by keyword matching
│  (knowledge)     │   (aws-dev, auth-security, database-rds, deploy-release,
│                  │    frontend-web, testing-ci, mermaid-visualizer)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Servers    │ ← External tools (AWS docs, IaC guidance)
│  (tools)         │ ← Only when enabled
└────────┬────────┘
         │
         ▼
    Agent Response
```
