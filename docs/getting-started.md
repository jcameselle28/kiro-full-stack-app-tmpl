# Getting Started

## 1. Clone the Repository

From GitLab (internal):
```bash
git clone https://gitlab.example.com/your-group/aicloudops.git my-aws-project
cd my-aws-project
```

From GitHub:
```bash
git clone <repo-url> my-aws-project
cd my-aws-project
```

Or copy just the `.kiro/` folder into an existing project:

```bash
cp -r /path/to/aicloudops/.kiro /path/to/your-project/.kiro
```

## 2. Install Prerequisites

```bash
# Install uv (required for MCP servers)
brew install uv

# Verify AWS CLI is configured
aws sts get-caller-identity
```

## 3. Choose Your Interface

### Option A: Kiro IDE

1. Open your project folder in Kiro IDE
2. The `.kiro/` folder is detected automatically
3. Steering files, skills, and hooks activate immediately
4. Start chatting — the agent is ready

Kiro IDE provides the full experience: steering rules shape every conversation, skills activate on demand, hooks automate linting and security checks, and MCP servers can be toggled on/off.

### Option B: Kiro CLI

1. Navigate to your project directory:

```bash
cd /path/to/your-project
```

2. Start a Kiro CLI session:

```bash
kiro chat
```

3. The CLI picks up the `.kiro/` configuration from the current directory. Steering files and skills are available. Hooks that use `runCommand` will execute in your terminal.

For non-interactive use (scripting, CI):

```bash
# Ask a single question
kiro chat --message "What EC2 instances are running in us-east-1?"

# Pipe input
echo "Analyze my S3 costs for the last 30 days" | kiro chat
```

## 4. Verify It's Working

In either Kiro IDE or CLI, try:

```
Check if my AWS credentials are valid
```

You should see the agent run `aws sts get-caller-identity` and report your account info. The output will follow the format defined in the `output-format.md` steering file.

## 5. Configure for Your Project

Copy and customize the project config template:

```bash
cp .kiro/steering/project-config-template.md .kiro/steering/project-config.md
```

Edit `project-config.md`:
- Change `inclusion: manual` to `inclusion: always` in the frontmatter
- Fill in your project-specific values (runtime, framework, deployment strategy, etc.)

This tells the agent about your specific stack and conventions.

## 6. Enable MCP Servers (Optional)

MCP servers are disabled by default to save tokens. Enable them when needed:

In chat:
```
Enable the AWS docs MCP
```

Or manually edit `.kiro/settings/mcp.json` and change `"disabled": true` to `"disabled": false` for the server you need.

See [MCP Servers](./mcp-servers.md) for the full list and usage guide.
