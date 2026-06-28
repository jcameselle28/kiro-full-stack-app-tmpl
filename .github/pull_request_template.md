<!--
Title: use Conventional Commits, e.g. "feat(auth): add Cognito JWT verification"
This becomes the squash commit message on main. See .kiro/steering/git-workflow.md
-->

## What & Why
<!-- What does this change do, and why is it needed? Keep it short. -->


## How It Was Tested
<!-- Tests added/updated, manual checks, local run. -->
- [ ] Unit/integration tests added or updated
- [ ] Lint and tests pass locally
- [ ] Verified the change manually (describe how)

## Checklist
- [ ] Scoped to one change; PR is small and reviewable
- [ ] No secrets, credentials, or `.env` files committed
- [ ] API changes follow `api-conventions.md` (status codes, error envelope, pagination)
- [ ] Security reviewed against `security-guardrails.md` (input validation, authz, parameterized queries)
- [ ] UI changes meet `accessibility-standards.md` (keyboard, labels, contrast) — or N/A
- [ ] DB changes use expand/contract migrations (backward-compatible) — or N/A
- [ ] Docs updated if behavior or setup changed — or N/A

## Related Issues
<!-- Closes #123 -->

## Follow-ups / Notes
<!-- Anything intentionally left out, deferred, or worth flagging to reviewers. -->
