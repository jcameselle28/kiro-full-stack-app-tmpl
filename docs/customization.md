# Customization

## Project-Specific Configuration

The most important customization is telling the agent about your project. This template ships a blank `project-config-template.md`; create your project's config from it:

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

## Modifying Agent Prompts

Edit the `-prompt.md` files in `.kiro/agents/` to change agent behavior:

- Add new capabilities or playbooks
- Change response formats
- Add domain-specific knowledge
- Adjust principles and priorities

The `.json` files control tools, MCP servers, and permissions — edit these to change what the agent can access.

## Removing Components You Don't Need

The setup is modular. Delete what you don't use:

- Building only in Python? Delete `.kiro/steering/typescript-standards.md`
- Building only in TypeScript? Delete `.kiro/steering/python-standards.md`
- Not writing IaC in this repo? Delete `.kiro/steering/iac-conventions.md`

Nothing will break — each component is independent.

## Sharing with Your Team

The entire `.kiro/` folder is designed to be committed to version control (GitLab, GitHub, etc.). When team members clone the repo, they get the same agent configuration.

Things to keep in mind:
- `.kiro/settings/mcp.json` — MCP servers are shared, but each person needs their own AWS credentials
- `.kiro/steering/project-config.md` — project-specific, should be committed
- `.kiro/steering/project-config-template.md` — the template, keep for reference

## CI/CD Integration

The testing-ci skill includes pipeline templates for:
- **GitLab CI** — `.gitlab-ci.yml` for container build/push to ECR and EC2/ECS deployment
- **GitHub Actions** — workflow files for build, test, and deploy
- **AWS CodePipeline** — CloudFormation-based pipeline definition

All templates use OIDC for AWS authentication — no long-lived access keys. See `.kiro/skills/testing-ci/references/cicd-templates.md` for the full set.
