# Getting Started

## 1. Clone the Repository

```bash
git clone <repo-url> my-aws-webapp
cd my-aws-webapp
```

Or copy just the `.kiro/` folder into an existing project:

```bash
cp -r /path/to/template/.kiro /path/to/your-project/.kiro
```

## 2. Install Prerequisites

```bash
# Install uv (required for MCP servers)
brew install uv

# Verify AWS CLI is configured (for deploys / SDK calls)
aws sts get-caller-identity
```

## 3. Choose Your Interface

### Option A: Kiro IDE

1. Open the project folder in Kiro IDE
2. The `.kiro/` folder is detected automatically
3. Steering files and skills activate immediately
4. Start chatting — the agent is ready

Kiro IDE provides the full experience: steering rules shape every conversation, skills activate on demand, and MCP servers can be toggled on/off.

### Option B: Kiro CLI

1. Navigate to your project directory:

```bash
cd /path/to/your-project
```

2. Start a Kiro CLI session:

```bash
kiro chat
```

3. The CLI picks up the `.kiro/` configuration from the current directory. Steering files and skills are available.

For non-interactive use (scripting, CI):

```bash
# Ask a single question
kiro chat --message "Scaffold a FastAPI service with a health endpoint"

# Pipe input
echo "Add a SQLAlchemy model and Alembic migration for an Account table" | kiro chat
```

## 4. Verify It's Working

In either Kiro IDE or CLI, try a development task:

```
Scaffold a minimal API endpoint with a /healthz route and a unit test
```

The agent should generate code that follows the project's standards — type hints/strict TypeScript, structured logging, and a matching test. Output follows the format defined in the `output-format.md` steering file.

## 5. Create Your Project Config

Create your project config from the template, then make it always-on:

```bash
cp .kiro/steering/project-config-template.md .kiro/steering/project-config.md
```

Edit `project-config.md`:
- Change `inclusion: manual` to `inclusion: always` in the frontmatter
- Fill in the `[placeholder]` values:
  - Backend framework (FastAPI / Flask / Django, or Express / Fastify / NestJS)
  - Database engine (PostgreSQL / MySQL) and ORM
  - IaC tool (CDK / Terraform)
  - Project name, team, AWS account ID, CI/CD, and auth approach

This tells the agent about your specific stack and conventions. If you settle on a single language, you can also delete the standards file you don't need (`python-standards.md` or `typescript-standards.md`).

## 6. Enable the AWS MCP (Optional)

The AWS MCP server is disabled by default to save tokens. It uses the MCP Proxy for AWS and requires valid AWS credentials when enabled.

In chat:
```
Enable the AWS MCP
```

Or manually edit `.kiro/settings/mcp.json` and change `"disabled": true` to `"disabled": false`.

See [MCP Servers](./mcp-servers.md) for the full usage guide, including read-only vs. write access and multi-account setup.

## 7. Next Steps

With Kiro set up and your project config in place, follow the [Golden Path](./golden-path.md) — a step-by-step walkthrough that takes you from this point to a deployed v1.0 app (scaffold → build a feature → open a PR → deploy). When you're ready to ship, the [Deployment](./deployment.md) guide covers AWS prerequisites, infrastructure setup, releases, and rollback.
