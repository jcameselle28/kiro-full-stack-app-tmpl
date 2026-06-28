---
inclusion: always
---

# Git & GitHub Workflow

This project uses **GitHub Flow**. Standard git/GitHub mechanics are assumed — this file states only the project's conventions and guardrails.

## Conventions
- `main` is always deployable. Never commit directly to `main` — changes land via PR.
- Short-lived branches off the latest `main`, named `<type>/<short-description>` in kebab-case. Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test` (e.g. `feat/account-signup`).
- Commits and PR titles follow **Conventional Commits** (`feat(auth): add JWT verification`); the PR title becomes the squash commit message.
- Merge via **squash**, then delete the branch. Require ≥1 approval and green CI.
- Use the PR template; link issues with `Closes #123`.

## Guardrails (when driving git via Kiro)
- Commit only when explicitly asked; use `gh` to open PRs against `main`.
- Stage specific files by name — never `git add -A` / `git add .`.
- Never commit secrets, `.env`, or credentials — flag them before staging.
- No force-push, `reset --hard`, or skipping hooks unless explicitly requested. Leave `git config` unchanged.

One-time repo setup (branch protection on `main`) is covered in [docs/golden-path.md](../../docs/golden-path.md).
