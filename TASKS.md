# Agent Enhancement Tasks

## 1. Hooks (Automation)

- [x] **1.1** Create a lint-on-save hook for Python files (`.py`) — runs `ruff check` on save
- [x] **1.2** Create a lint-on-save hook for TypeScript files (`.ts`, `.tsx`) — runs `eslint`
- [x] **1.3** Create a security scan hook (preToolUse on write) — checks for hardcoded secrets, AWS keys, or credentials before writing code
- [x] **1.4** Create a post-task-execution hook — runs `npm test` or `pytest` after a spec task completes

## 2. Conditional Steering Files

- [x] **2.1** Create `python-standards.md` — Python coding conventions, activated only when `.py` files are in context (`fileMatch` inclusion)
- [x] **2.2** Create `typescript-standards.md` — TypeScript conventions, activated only when `.ts`/`.tsx` files are in context
- [x] **2.3** Create `iac-conventions.md` — IaC naming, tagging, and structure conventions, activated when CDK/SAM/Terraform files are read

## 3. Review & Enhance Agent Prompts

- [x] **3.1** Review and enhance `sre-prompt.md` — ensure it covers incident response, SLO management, runbooks, observability setup
- [x] **3.2** Review and enhance `finops-prompt.md` — ensure it covers cost analysis workflows, rightsizing, Savings Plans, unit economics
- [x] **3.3** Review and enhance `security-ops-prompt.md` — ensure it covers IAM reviews, compliance checks, vulnerability triage, encryption audits
- [x] **3.4** Review and enhance `network-ops-prompt.md` — ensure it covers VPC design, DNS, load balancing, connectivity troubleshooting, transit gateway

## 4. Testing & CI Skill

- [x] **4.1** Create `.kiro/skills/testing-ci/SKILL.md` — test scaffolding rules, framework selection guidance
- [x] **4.2** Create `.kiro/skills/testing-ci/references/pytest-patterns.md` — pytest fixtures, moto mocking, conftest patterns for AWS
- [x] **4.3** Create `.kiro/skills/testing-ci/references/jest-patterns.md` — Jest/Vitest setup, aws-sdk-client-mock patterns
- [x] **4.4** Create `.kiro/skills/testing-ci/references/cicd-templates.md` — GitHub Actions and CodePipeline templates for AWS deployments

## 5. Project-Specific Steering (Template)

- [x] **5.1** Create a `project-config-template.md` in steering — a template file with placeholders for project-specific decisions (runtime, naming, deployment targets, branch strategy) that can be copied and filled in per project

---

## Priority Suggestion

| Priority | Tasks | Rationale |
|---|---|---|
| High | 1.1, 1.3, 2.1, 2.2 | Immediate productivity gains and guardrails |
| Medium | 3.1–3.4, 4.1–4.4 | Depth and quality of agent responses |
| Low | 1.2, 1.4, 2.3, 5.1 | Nice-to-have, depends on project stack |


## 6. GitLab CI/CD Integration

- [x] **6.1** Add GitLab CI templates to `.kiro/skills/testing-ci/references/cicd-templates.md` — `.gitlab-ci.yml` for SAM, CDK, and container deployments
- [x] **6.2** Update `docs/getting-started.md` — Include GitLab as the primary repo/CI option alongside GitHub
- [x] **6.3** Update `.kiro/steering/iac-conventions.md` — Add GitLab CI runner conventions and pipeline structure
- [x] **6.4** Update `.kiro/steering/project-config-template.md` — List GitLab CI as a CI/CD option
