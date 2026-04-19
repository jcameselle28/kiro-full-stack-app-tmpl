# AWS Cloud Operations Agent — Documentation

A portable Kiro agent foundation for AWS cloud operations and application development. Copy the `.kiro/` folder into any project to get a fully configured AI assistant with specialized knowledge across CloudOps, SRE, FinOps, Security, Networking, and Application Development.

## Table of Contents

- [Quick Start](./docs/getting-started.md) — Get up and running in 5 minutes
- [Architecture](./docs/architecture.md) — How the agent system is structured
- [MCP Servers](./docs/mcp-servers.md) — Managing external tool integrations
- [Customization](./docs/customization.md) — Adapting the agent to your project

## What's Included

| Component | Count | Description |
|---|---|---|
| Agents | 7 | aws-ops (orchestrator), cloudops, sre, finops, security-ops, network-ops, aws-dev |
| Skills | 5 | aws-cli, aws-cost-explorer, aws-dev, mermaid-visualizer, testing-ci |
| Steering | 8 | Security guardrails, output format, ops guidelines, language standards, IaC conventions, MCP instructions, project config template |
| Hooks | 4 | Python lint, TypeScript lint, security scan on write, post-task test runner |
| MCP Servers | 7 | AWS docs, pricing, billing, IaC, serverless, Lambda tools, CloudWatch (all disabled by default) |

## Prerequisites

- [Kiro IDE](https://kiro.dev) or [Kiro CLI](https://kiro.dev/docs/cli)
- [uv](https://docs.astral.sh/uv/) — Python package manager (for MCP servers): `brew install uv`
- AWS CLI configured with valid credentials
- Node.js 20+ (for TypeScript projects)
- Python 3.11+ (for Python projects)
