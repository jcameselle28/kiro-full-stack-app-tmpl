---
inclusion: always
---

# MCP Server Management Instructions

## Quick Reference Commands (for Kiro chat)

| What you want | What to say |
|---|---|
| Enable AWS Docs MCP | "Enable the AWS docs MCP" |
| Disable AWS Docs MCP | "Disable the AWS docs MCP" |
| Enable AWS Pricing MCP | "Enable the AWS pricing MCP" |
| Disable AWS Pricing MCP | "Disable the AWS pricing MCP" |
| Enable Billing & Cost Mgmt MCP | "Enable the billing cost management MCP" |
| Disable Billing & Cost Mgmt MCP | "Disable the billing cost management MCP" |
| Enable AWS IaC MCP | "Enable the AWS IaC MCP" |
| Disable AWS IaC MCP | "Disable the AWS IaC MCP" |
| Enable AWS Serverless MCP | "Enable the AWS serverless MCP" |
| Disable AWS Serverless MCP | "Disable the AWS serverless MCP" |
| Enable AWS Lambda Tools MCP | "Enable the AWS Lambda tools MCP" |
| Disable AWS Lambda Tools MCP | "Disable the AWS Lambda tools MCP" |
| Enable AWS CloudWatch MCP | "Enable the AWS CloudWatch MCP" |
| Disable AWS CloudWatch MCP | "Disable the AWS CloudWatch MCP" |
| Check MCP status | "What MCP servers are enabled?" |

## How It Works

- MCP servers are defined in `.kiro/settings/mcp.json`
- Each server has a `"disabled"` flag: `true` = off, `false` = on
- Kiro auto-connects/disconnects when the config changes — no restart needed
- Keep servers disabled when not in use to avoid unnecessary token consumption

## Manual Toggle

Edit `.kiro/settings/mcp.json` and change the `disabled` flag:

```json
"disabled": true   ← server is OFF (not consuming tokens)
"disabled": false  ← server is ON (active and available)
```

## Currently Defined Servers

| Server | Command | Purpose |
|---|---|---|
| aws-documentation | `uvx awslabs.aws-documentation-mcp-server@latest` | Search and retrieve AWS documentation |
| aws-pricing | `uvx awslabs.aws-pricing-mcp-server@latest` | Real-time AWS pricing, cost estimates, and IaC cost analysis |
| billing-cost-management | `uvx awslabs.billing-cost-management-mcp-server@latest` | Historical spend analysis, forecasting, budgets, anomaly detection, Savings Plans, Compute Optimizer |
| aws-iac | `uvx awslabs.aws-iac-mcp-server@latest` | CDK and CloudFormation guidance, construct patterns, best practices |
| aws-serverless | `uvx awslabs.sam-mcp-server@latest` | SAM CLI lifecycle — build, deploy, local invoke, logs |
| aws-lambda-tools | `uvx awslabs.lambda-tool-mcp-server@latest` | Execute Lambda functions as AI tools, test invocations |
| aws-cloudwatch | `uvx awslabs.cloudwatch-mcp-server@latest` | Metrics, alarms, logs analysis, operational troubleshooting |

## Adding New MCP Servers

Add a new entry under `mcpServers` in `.kiro/settings/mcp.json`:

```json
"server-name": {
  "command": "uvx",
  "args": ["package-name@latest"],
  "env": {},
  "disabled": true,
  "autoApprove": []
}
```

## Prerequisites

- `uv` must be installed (`brew install uv`) — provides the `uvx` command
- AWS credentials must be valid for AWS-related MCP servers
