# MCP Servers

MCP (Model Context Protocol) servers extend the agent with external tool access — AWS documentation search, pricing lookups, cost analysis, and more.

All servers are disabled by default to avoid consuming tokens when not needed.

## Available Servers

| Server | Package | Purpose |
|---|---|---|
| aws-documentation | `awslabs.aws-documentation-mcp-server` | Search and retrieve AWS documentation |
| aws-pricing | `awslabs.aws-pricing-mcp-server` | Real-time pricing, cost estimates, IaC cost analysis |
| billing-cost-management | `awslabs.billing-cost-management-mcp-server` | Historical spend, forecasting, budgets, anomaly detection |
| aws-iac | `awslabs.aws-iac-mcp-server` | CDK/CloudFormation guidance and best practices |
| aws-serverless | `awslabs.sam-mcp-server` | SAM CLI lifecycle (build, deploy, local invoke) |
| aws-lambda-tools | `awslabs.lambda-tool-mcp-server` | Execute and test Lambda functions |
| aws-cloudwatch | `awslabs.cloudwatch-mcp-server` | Metrics, alarms, logs analysis |

## Enabling/Disabling

### Via Chat (Kiro IDE)

```
Enable the AWS docs MCP
Disable the AWS pricing MCP
What MCP servers are enabled?
```

The agent will toggle the `disabled` flag in `.kiro/settings/mcp.json` for you.

### Manually

Edit `.kiro/settings/mcp.json`:

```json
"aws-documentation": {
  "disabled": false    ← ON (consuming tokens)
}
```

```json
"aws-documentation": {
  "disabled": true     ← OFF (not consuming tokens)
}
```

Kiro auto-reconnects when the config changes — no restart needed.

### Via Kiro IDE UI

1. Open the MCP Server view in the Kiro feature panel
2. Toggle servers on/off with the switch

## Prerequisites

- `uv` must be installed: `brew install uv`
- AWS credentials must be valid for AWS-related servers
- Some servers require specific IAM permissions (see below)

## IAM Permissions by Server

### aws-documentation
No AWS permissions required — reads public documentation.

### aws-pricing
- `pricing:DescribeServices`
- `pricing:GetAttributeValues`
- `pricing:GetProducts`

### billing-cost-management
- `ce:*` (Cost Explorer)
- `budgets:ViewBudget`
- `cost-optimization-hub:*`
- `compute-optimizer:Get*`
- `freetier:GetFreeTierUsage`

### aws-cloudwatch
- `cloudwatch:GetMetricData`
- `cloudwatch:DescribeAlarms`
- `logs:GetLogEvents`
- `logs:DescribeLogGroups`

### aws-serverless (SAM)
- Requires SAM CLI installed locally
- Deployment permissions depend on your stack resources

### aws-lambda-tools
- `lambda:InvokeFunction`
- `lambda:GetFunction`

## Adding New Servers

Add an entry to `.kiro/settings/mcp.json`:

```json
"new-server": {
  "command": "uvx",
  "args": ["package-name@latest"],
  "env": {
    "FASTMCP_LOG_LEVEL": "ERROR"
  },
  "disabled": true,
  "autoApprove": []
}
```

Browse available AWS MCP servers at: https://awslabs.github.io/mcp/servers

## Performance Tip

Using `@latest` checks for updates on every start. For faster startup, remove `@latest` and manage updates manually:

```bash
# Refresh a specific server
uvx awslabs.aws-documentation-mcp-server@latest

# Clear cache for a server
uv cache clean awslabs.aws-documentation-mcp-server
```
