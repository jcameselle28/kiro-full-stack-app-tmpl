---
inclusion: manual
---

# MCP Server Management Instructions

This template uses a single AWS MCP entry — the **MCP Proxy for AWS** (`mcp-proxy-for-aws`) — which signs requests with local AWS credentials and connects to the managed **AWS MCP Server**. It replaces the older per-service AWS Labs servers.

## Quick Reference Commands (for Kiro chat)

| What you want | What to say |
|---|---|
| Enable the AWS MCP | "Enable the AWS MCP" |
| Disable the AWS MCP | "Disable the AWS MCP" |
| Check MCP status | "What MCP servers are enabled?" |

## How It Works

- The server is defined in `.kiro/settings/mcp.json` under the name `aws`.
- It has a `"disabled"` flag: `true` = off, `false` = on.
- When enabled, every call is **SigV4-signed with your AWS credentials** — valid credentials are required.
- Kiro auto-connects/disconnects when the config changes — no restart needed.
- Keep it disabled when not in use to avoid unnecessary token consumption.

## Manual Toggle

Edit `.kiro/settings/mcp.json` and change the `disabled` flag:

```json
"disabled": true   // server is OFF (not consuming tokens)
"disabled": false  // server is ON (active; uses your AWS credentials)
```

## Currently Defined Server

| Server | Command | Purpose |
|---|---|---|
| `aws` | `uvx mcp-proxy-for-aws@1.6.3 https://aws-mcp.us-east-1.api.aws/mcp --read-only --region us-east-1` | AWS documentation, IaC/CDK/CloudFormation guidance, and multi-service AWS access through one IAM-secured endpoint |

## Read-Only vs. Write Access

- The server ships with `--read-only`, so the agent can read and advise but **cannot mutate AWS resources**.
- To allow provisioning/modifying resources (e.g. deploying infrastructure), remove `--read-only` from the args. Do this deliberately and pair it with least-privilege IAM.

## Multi-Account / Multi-Role

To work across accounts without restarting, set profiles via the `env` block:

```json
"env": { "AWS_MCP_PROXY_PROFILES": "prod-readonly dev staging" }
```

The first profile is the default; the agent can route a call through another by passing the `aws_profile` parameter.

## Version Pinning

Pin to a specific version (`mcp-proxy-for-aws@1.6.3`, the current latest from the official `aws-mcp-team` PyPI project), not `@latest` — `@latest` may introduce breaking changes. Bump deliberately after checking the release. Note: there is no official `2.x`; treat any `2.x` "latest" as a look-alike until verified against `github.com/aws/mcp-proxy-for-aws`.

## Adding New MCP Servers

Add another entry under `mcpServers` in `.kiro/settings/mcp.json`:

```json
"server-name": {
  "command": "uvx",
  "args": ["package-name@<version>"],
  "env": {},
  "disabled": true,
  "autoApprove": []
}
```

## Prerequisites

- `uv` installed (`brew install uv`) — provides the `uvx` command
- Valid AWS credentials (`aws configure` / `aws configure sso` / instance role); verify with `aws sts get-caller-identity`

See `docs/mcp-servers.md` for the full guide.
