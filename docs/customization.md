# Customization

## Project-Specific Configuration

The most important customization is telling the agent about your project.

### Step 1: Create your project config

```bash
cp .kiro/steering/project-config-template.md .kiro/steering/project-config.md
```

### Step 2: Update the frontmatter

Change `inclusion: manual` to `inclusion: always`:

```yaml
---
inclusion: always
---
```

### Step 3: Fill in your values

Replace all `[placeholder]` values with your project specifics — runtime, framework, deployment strategy, team name, etc.

## Adding Steering Rules

Create a new `.md` file in `.kiro/steering/`:

### Always-on rule
```yaml
---
inclusion: always
---

# My Custom Rule
- Always use snake_case for database column names
- All API responses must include a `request_id` field
```

### Conditional rule (file-based)
```yaml
---
inclusion: fileMatch
fileMatchPattern: "**/*.go"
---

# Go Standards
- Use `go fmt` formatting
- Error handling: always check returned errors
```

### Manual rule (opt-in)
```yaml
---
inclusion: manual
---

# Migration Playbook
Steps for database migrations...
```

Use `#` in Kiro IDE chat to include manual steering files.

## Adding Skills

Create a new folder in `.kiro/skills/` with a `SKILL.md`:

```
.kiro/skills/my-skill/
├── SKILL.md              # Required — main instructions
└── references/           # Optional — supporting docs
    └── patterns.md
```

The `SKILL.md` must have frontmatter:

```yaml
---
name: my-skill
description: What this skill does and when it should activate.
---

# My Skill
Instructions and patterns...
```

## Adding Hooks

### Via Kiro IDE
Use the command palette: "Open Kiro Hook UI"

### Manually
Create a `.kiro.hook` file in `.kiro/hooks/`:

```json
{
  "name": "My Hook",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "runCommand",
    "command": "ruff check ${file}"
  }
}
```

### Available event types
- `fileEdited`, `fileCreated`, `fileDeleted` — file system events
- `promptSubmit` — when a message is sent
- `agentStop` — when agent execution completes
- `preToolUse`, `postToolUse` — before/after tool execution
- `preTaskExecution`, `postTaskExecution` — before/after spec tasks
- `userTriggered` — manual button click

## Modifying Agent Prompts

Edit the `-prompt.md` files in `.kiro/agents/` to change agent behavior:

- Add new capabilities or playbooks
- Change response formats
- Add domain-specific knowledge
- Adjust principles and priorities

The `.json` files control tools, MCP servers, and permissions — edit these to change what the agent can access.

## Removing Components You Don't Need

The setup is modular. Delete what you don't use:

- Don't use Python? Delete `.kiro/steering/python-standards.md`
- Don't need cost analysis? Delete the `aws-cost-explorer` skill
- Don't want auto-linting? Delete the lint hooks from `.kiro/hooks/`

Nothing will break — each component is independent.

## Sharing with Your Team

The entire `.kiro/` folder is designed to be committed to version control (GitLab, GitHub, etc.). When team members clone the repo, they get the same agent configuration.

Things to keep in mind:
- `.kiro/settings/mcp.json` — MCP servers are shared, but each person needs their own AWS credentials
- `.kiro/steering/project-config.md` — project-specific, should be committed
- `.kiro/steering/project-config-template.md` — the template, keep for reference

## CI/CD Integration

The testing-ci skill includes pipeline templates for:
- **GitLab CI** (primary) — `.gitlab-ci.yml` for SAM, CDK, and container deployments
- **GitHub Actions** — workflow files for SAM, CDK, and ECS
- **AWS CodePipeline** — CloudFormation-based pipeline definition

All templates use OIDC for AWS authentication — no long-lived access keys. See `.kiro/skills/testing-ci/references/cicd-templates.md` for the full set.
