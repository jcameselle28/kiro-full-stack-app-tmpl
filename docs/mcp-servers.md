# MCP Servers

This template uses a single AWS MCP entry: the **MCP Proxy for AWS**. It's a lightweight, local bridge that signs requests with your AWS credentials (SigV4) and connects to the managed **AWS MCP Server** — AWS's consolidated endpoint for multi-service guidance and access (docs, infrastructure, and service interactions). It replaces the older per-service AWS Labs servers (one for documentation, one for IaC).

The server is **disabled by default** to avoid consuming tokens when not needed.

## The Server

| Name | Package | Endpoint | Purpose |
|---|---|---|---|
| `aws` | `mcp-proxy-for-aws` | `https://aws-mcp.us-east-1.api.aws/mcp` | AWS documentation, IaC/CDK/CloudFormation guidance, and multi-service AWS access through one IAM-secured endpoint |

Configured in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "aws": {
      "command": "uvx",
      "args": [
        "mcp-proxy-for-aws@1.6.3",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--read-only",
        "--region",
        "us-east-1"
      ],
      "env": {},
      "disabled": true,
      "autoApprove": []
    }
  }
}
```

## Why the Proxy (vs. the old per-service servers)

- **One entry instead of many** — the managed AWS MCP Server consolidates documentation, IaC guidance, and service access.
- **IAM-secured and auditable** — calls are signed with your AWS credentials and governed by IAM, with CloudWatch metrics and CloudTrail logging on the AWS side.
- **AWS maintains the server** — you track one pinned proxy version instead of several individual server packages.

Tradeoff: unlike the old documentation server (which needed no credentials), **every call now requires valid AWS credentials**, because requests are SigV4-signed.

## Key Flags

| Flag | What it does | Default here |
|---|---|---|
| `--read-only` | Disables mutating/write tools — the agent can read and advise but not change AWS resources | **On** (safe default) |
| `--region` | Target AWS region for operations | `us-east-1` |
| `--profile` | AWS profile(s) to use; list several to enable per-call switching | unset (default chain) |
| `--tool-timeout` | Max seconds a tool call may run before a graceful error | unset |

To let the agent **provision or modify** AWS resources (e.g. deploy infrastructure), remove `--read-only`. Do this deliberately — it widens what the agent can change in your account.

## Enabling / Disabling

### Via Chat (Kiro IDE)

```
Enable the AWS MCP
Disable the AWS MCP
What MCP servers are enabled?
```

The agent toggles the `disabled` flag in `.kiro/settings/mcp.json` for you.

### Manually

Edit `.kiro/settings/mcp.json`:

```json
"aws": {
  "disabled": false    // ON (active; signs requests with your AWS credentials)
}
```

```json
"aws": {
  "disabled": true     // OFF (not consuming tokens)
}
```

Kiro auto-reconnects when the config changes — no restart needed.

### Via Kiro IDE UI

1. Open the MCP Server view in the Kiro feature panel
2. Toggle the server on/off with the switch

## Prerequisites

- `uv` installed: `brew install uv` (provides `uvx`)
- Valid AWS credentials on the machine — via `aws configure`, `aws configure sso`, environment variables, or an instance role. Verify with `aws sts get-caller-identity`.
- The proxy reads fresh credentials on every request, so `aws sso login` refreshes take effect without a restart.

## IAM Permissions

Because requests are IAM-signed, the identity you run as needs permission to call the AWS MCP Server (and, when not in `--read-only` mode, the underlying services it acts on). Scope this to least privilege:

- Start in `--read-only` mode with read/describe-level permissions.
- Grant write permissions only for the specific services you intend the agent to provision, and prefer a dedicated profile/role for that.
- Never use long-lived root or admin credentials. Prefer IAM Identity Center (SSO) sessions.

If you hit an authentication error, confirm your credentials are valid and that the service was detected correctly (the proxy infers it from the endpoint; you can set it explicitly with `--service`).

## Multi-Account / Multi-Role

The proxy supports per-call profile switching so the agent can work across accounts without restarting:

```json
{
  "mcpServers": {
    "aws": {
      "command": "uvx",
      "args": ["mcp-proxy-for-aws@1.6.3", "https://aws-mcp.us-east-1.api.aws/mcp", "--read-only"],
      "env": { "AWS_MCP_PROXY_PROFILES": "prod-readonly dev staging" },
      "disabled": true,
      "autoApprove": []
    }
  }
}
```

The first profile is the default; the agent can route a call through another by passing the `aws_profile` parameter. Invalid profiles are rejected.

## Version Pinning

Pin the proxy to a specific version (`mcp-proxy-for-aws@1.6.3`, the current latest from the official `aws-mcp-team` PyPI project) rather than `@latest`. AWS notes that `@latest` may pull in breaking changes. Check [PyPI](https://pypi.org/project/mcp-proxy-for-aws/) for the current stable version and bump deliberately. The package has no `2.x` release — if you see a `2.x` "latest" elsewhere, verify it links back to `github.com/aws/mcp-proxy-for-aws` before trusting it (possible look-alike).

## Adding Other MCP Servers

You can still add other servers (including individual AWS Labs servers, or community/third-party ones) alongside the `aws` entry:

```json
"server-name": {
  "command": "uvx",
  "args": ["package-name@<version>"],
  "env": {},
  "disabled": true,
  "autoApprove": []
}
```

## References

- MCP Proxy for AWS: https://github.com/aws/mcp-proxy-for-aws
- Agent Toolkit for AWS (AWS MCP Server): https://docs.aws.amazon.com/agent-toolkit/latest/userguide/

> Content rephrased from AWS documentation and the project README for licensing compliance.
