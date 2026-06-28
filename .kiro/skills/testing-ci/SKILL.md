---
name: testing-ci
description: This skill provides testing patterns, mocking strategies, and CI/CD pipeline templates for web applications on AWS. Covers pytest, Jest/Vitest, local database integration testing, aws-sdk-client-mock, GitHub Actions, GitLab CI, and CodePipeline. Triggers on requests about testing, mocking, CI/CD, coverage, or deployment pipelines.
---

# Testing & CI/CD Skill

This skill provides testing patterns, mocking strategies, and CI/CD pipeline templates for AWS application development.

## Activation Keywords
- test, testing, unit test, integration test, e2e
- mock, moto, aws-sdk-client-mock, fixture
- CI, CD, pipeline, GitHub Actions, CodePipeline, deploy
- coverage, pytest, jest, vitest

## Testing Philosophy

### Test Pyramid for Web Apps on AWS
- **Unit tests (70%)** — Business logic, pure functions, no I/O
- **Integration tests (20%)** — Database access and AWS service interactions (real local DB; mocks for auxiliary services)
- **E2E tests (10%)** — Deployed stack behind the ALB, smoke tests against real endpoints

### What to Test
- Business logic in isolation (service layer)
- Data access / repository layer against a real local database
- API request/response contracts, including validation and error paths
- Error handling paths (what happens when the DB is unavailable or a query times out?)
- Input validation and edge cases
- AuthN/AuthZ enforcement on protected endpoints

### What NOT to Unit Test
- AWS SDK internals (trust the SDK)
- ORM/driver internals
- Third-party library behavior

## Framework Selection

| Language | Framework | DB / AWS Mocking |
|---|---|---|
| Python | pytest | Docker Postgres/MySQL for DB; moto for auxiliary AWS services |
| TypeScript | Vitest (preferred) or Jest | Docker DB; aws-sdk-client-mock for AWS SDK v3 |
| IaC (CDK) | CDK assertions | Template.fromStack() |

## Coverage Targets
- Business logic: 80%+
- API / controller layer: 70%+
- Infrastructure (CDK): assertions on critical resources
- Overall project: 75%+ (don't chase 100%)

## References
- `references/pytest-patterns.md` — Python: local-DB integration, service/API tests, moto for auxiliary services
- `references/jest-patterns.md` — TypeScript: Vitest/Jest, real-DB repository tests, supertest API tests, component tests
- `references/cicd-templates.md` — GitHub Actions & GitLab CI: build → ECR → migrate → roll out to EC2/ASG
