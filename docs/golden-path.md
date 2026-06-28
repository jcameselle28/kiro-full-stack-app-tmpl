# Golden Path: From Clone to a Deployed v1.0

This is the recommended, end-to-end path for building and shipping a first version (v1.0) of a full-stack app with Kiro — written so that a junior developer or a non-developer can follow it.

You drive by **describing what you want in plain language**. Kiro writes the code, follows the project's standards automatically (from the steering files and skills in `.kiro/`), and explains each step. You review and approve.

> New to the pieces involved? Read [Architecture](./architecture.md) for a one-page overview of how `.kiro/` shapes Kiro's behavior. You don't need to understand it to follow this path.

---

## Before You Start (one-time setup)

1. **Install the tools** (see [Getting Started](./getting-started.md) for details):
   - Kiro (IDE or CLI)
   - `git` and the GitHub CLI (`gh`)
   - `uv` (for MCP servers): `brew install uv`
   - AWS CLI, configured with credentials: `aws sts get-caller-identity`
2. **Have access to**:
   - A GitHub account/org where you can create a repo
   - An AWS account where you can deploy (see [Deployment](./deployment.md) for what's needed)

If you don't have AWS access yet, you can still complete Steps 1–6 (build and test locally) and come back for Step 7 (deploy).

---

## Step 1 — Create your project from this template

This repo is a **template repository** — you create a *new* repo from it and work there. This template stays clean and untouched; you never push your project back to it.

The easiest way is GitHub's "Use this template" feature, which gives your new repo a fresh history (none of the template's commits come along):

```bash
# Creates a new private repo from the template and clones it
gh repo create my-app --template jcameselle28/kiro-full-stack-app-tmpl --private --clone
cd my-app
```

Or click **"Use this template" → "Create a new repository"** on the template's GitHub page.

Then open the folder in Kiro. The `.kiro/` configuration is detected automatically.

---

## Step 2 — Tell Kiro about your project

This is the single most important step. It teaches Kiro your stack and conventions.

```bash
cp .kiro/steering/project-config-template.md .kiro/steering/project-config.md
```

Open `.kiro/steering/project-config.md`, change `inclusion: manual` to `inclusion: always`, and fill in the `[placeholder]` values. **Not sure what to pick?** Ask Kiro in chat:

> Help me fill in project-config.md. I'm building [describe your app in a sentence]. Recommend a stack and explain the tradeoffs.

Sensible v1.0 defaults if you have no preference:

| Choice | Default for v1.0 | Why |
|---|---|---|
| Language | Python (FastAPI) **or** TypeScript (Next.js + API) | Both are first-class in this template |
| Database | RDS PostgreSQL | Most broadly supported |
| Frontend | Next.js (App Router) | Covered by the `frontend-web` skill |
| IaC | CDK (TypeScript) | Higher-level constructs, less boilerplate |
| Auth | Amazon Cognito | Managed; least code to own (see `auth-security`) |
| CI/CD | GitHub Actions | Template ships a ready workflow |

If you settle on a single language, delete the standards file you don't need (`python-standards.md` or `typescript-standards.md`).

---

## Step 3 — Scaffold the application

Ask Kiro to create the project skeleton. Example prompt:

> Scaffold a full-stack app per project-config.md: a [FastAPI / Express] backend with `/healthz` and `/readyz` endpoints, a Next.js frontend, a local docker-compose with Postgres, and the standard project structure. Include a sample "accounts" resource end to end.

Kiro will generate the backend, frontend, database models/migrations, and local dev setup following the project's standards. Review what it creates and ask questions like "why is this structured this way?" — it will explain.

**Verify it runs locally:**

> Start the app locally with docker-compose and show me how to open it in the browser.

You should be able to load the frontend and hit the health endpoint.

---

## Step 4 — Build your first feature

Work one small feature at a time. For each feature, start a branch (Kiro follows GitHub Flow automatically — see `git-workflow.md`):

> Create a branch for a signup feature, then add: a `users` table + migration, a `POST /v1/users` endpoint with validation, and a signup form on the frontend. Include tests.

Kiro will:
- Create a correctly named branch (e.g. `feat/user-signup`)
- Write the code following the API, security, database, and frontend conventions
- Add tests and run them

Review the changes, ask for adjustments, and iterate until you're happy.

---

## Step 5 — Test and review

Before opening a pull request:

> Run the full test suite and the linter, and fix anything that fails.

For a quality check on the change:

> Review this branch for security and accessibility issues against our standards.

The `security-guardrails`, `accessibility-standards`, and `api-conventions` steering rules are applied automatically, but an explicit review pass is good practice for a v1.0.

---

## Step 6 — Open a pull request

> Commit my changes and open a pull request to main.

Kiro pushes the branch and opens a PR using the project's template. Then:
- A teammate reviews and approves (GitHub Flow requires ≥1 approval — see `git-workflow.md`)
- CI runs automatically (tests + lint)
- Once green and approved, **squash merge** into `main` and delete the branch

> First time setting up the repo? Enable branch protection on `main` so the workflow is enforced. Ask Kiro: *"Set up branch protection on main"*, or run it yourself (note: send a JSON body — the `-f` string form is rejected by the API):
> ```bash
> gh api -X PUT repos/<owner>/<repo>/branches/main/protection \
>   -H "Accept: application/vnd.github+json" \
>   --input - <<'JSON'
> { "required_status_checks": null, "enforce_admins": true,
>   "required_pull_request_reviews": { "required_approving_review_count": 1 },
>   "restrictions": null }
> JSON
> ```
> This requires a PR with ≥1 approval and blocks direct/force pushes.

---

## Step 7 — Deploy v1.0

Deployment has a one-time infrastructure setup, then repeatable releases. The human-facing details (AWS prerequisites, what gets created, costs to watch) are in **[Deployment](./deployment.md)**.

**One-time — create the infrastructure:**

> Using CDK, create the infrastructure for this app per iac-conventions.md: VPC, RDS Postgres, an EC2 Auto Scaling Group behind an ALB, CloudFront, and WAF. Walk me through deploying it to my dev environment.

**Set up automated releases:**

> Add the GitHub Actions deploy workflow from the testing-ci CI/CD templates, wired to my ECR repo and Auto Scaling Group, using OIDC for AWS auth.

(The ready-to-use pipeline lives in `.kiro/skills/testing-ci/references/cicd-templates.md`.)

**Ship it:** merge to `main`. The pipeline builds one immutable image, runs database migrations safely (expand/contract), and rolls out with zero downtime. The `deploy-release` skill handles rollout strategy and rollback. See [Deployment](./deployment.md) for how to confirm it's live and how to roll back.

---

## The Loop After v1.0

For every change from here on, repeat Steps 4–7: branch → build → test → PR → merge → deploy. Keep changes small and let CI and review be the safety net.

## When You Get Stuck

- Ask Kiro directly: *"This failed with [paste the error]. What's wrong and how do I fix it?"*
- Ask it to explain: *"Explain what this code does and why."*
- For AWS specifics, enable the AWS MCP: *"Enable the AWS MCP"* (see [MCP Servers](./mcp-servers.md)).
- Keep prompts small and specific — one feature or one fix at a time.
