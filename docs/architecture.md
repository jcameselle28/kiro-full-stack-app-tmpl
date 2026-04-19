# Architecture

## How It Works

The `.kiro/` folder is the brain of the agent. When you open a project in Kiro (IDE or CLI), it reads this folder and configures itself accordingly.

```
.kiro/
├── agents/          → Agent definitions (personality, tools, MCP servers)
├── hooks/           → Automated actions on IDE/editor events
├── settings/        → MCP server configuration
├── skills/          → Activatable knowledge modules
└── steering/        → Always-on or conditional behavioral rules
```

## Component Breakdown

### Agents

Agent definitions live in `.kiro/agents/` as paired files:
- `{name}.json` — Configuration (tools, MCP servers, model, permissions)
- `{name}-prompt.md` — Personality, capabilities, response formats

| Agent | Role | Domain |
|---|---|---|
| aws-ops | Orchestrator — routes requests to specialists | All AWS operations |
| cloudops | Infrastructure management | EC2, ECS, EKS, CDK, CloudFormation, scaling |
| sre | Reliability engineering | SLOs, monitoring, incidents, runbooks |
| finops | Cost optimization | Billing, rightsizing, Savings Plans, unit economics |
| security-ops | Security and compliance | IAM, GuardDuty, encryption, audits |
| network-ops | Networking | VPC, DNS, load balancers, connectivity |
| aws-dev | Application development | Python, TypeScript, Lambda, CDK, containers |

Note: Custom agent orchestration (aws-ops routing to sub-agents) is a future Kiro feature. Today, the single Kiro agent uses steering and skills to cover all domains.

All agent JSON files specify `"model": "claude-opus-4.6"`. This field is informational — the actual model used is determined by your Kiro IDE or CLI settings.

### Steering Files

Steering files in `.kiro/steering/` inject rules into every conversation. Three inclusion modes:

| Mode | Behavior | Example |
|---|---|---|
| `always` (default) | Active in every conversation | security-guardrails.md, output-format.md |
| `fileMatch` | Active only when matching files are in context | python-standards.md (triggers on `*.py`) |
| `manual` | Only when user explicitly includes via `#` in chat | project-config-template.md |

### Skills

Skills in `.kiro/skills/` are knowledge modules activated on demand when the conversation matches their keywords.

| Skill | Activates When |
|---|---|
| aws-cli | AWS infrastructure queries, resource management |
| aws-cost-explorer | Cost analysis, billing queries |
| aws-dev | Application coding, SDK usage, project scaffolding |
| mermaid-visualizer | Diagram generation, architecture visualization |
| testing-ci | Testing patterns, CI/CD pipelines, mocking |

Each skill has a `SKILL.md` (main instructions) and optional `references/` and `scripts/` folders.

### Hooks

Hooks in `.kiro/hooks/` automate actions based on events:

| Hook | Trigger | Action |
|---|---|---|
| lint-python-save | Python file saved | Runs `ruff check --fix` |
| lint-typescript-save | TypeScript file saved | Runs `npx eslint --fix` |
| security-scan-write | Before any file write | Scans for hardcoded credentials |
| run-tests-post-task | After spec task completes | Runs pytest or npm test |

### MCP Servers

MCP (Model Context Protocol) servers in `.kiro/settings/mcp.json` extend the agent with external tool access. All are disabled by default to save tokens.

See [MCP Servers](./mcp-servers.md) for details.

## Data Flow

```
User Request
    │
    ▼
┌─────────────────┐
│  Steering Files  │ ← Always-on rules (security, output format)
│  (behavioral)    │ ← Conditional rules (Python/TS standards when relevant)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Skills       │ ← Activated on demand by keyword matching
│  (knowledge)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MCP Servers    │ ← External tools (AWS docs, pricing, etc.)
│  (tools)         │ ← Only when enabled
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Hooks        │ ← Pre/post actions (lint, security scan, tests)
│  (automation)    │
└────────┬────────┘
         │
         ▼
    Agent Response
```
