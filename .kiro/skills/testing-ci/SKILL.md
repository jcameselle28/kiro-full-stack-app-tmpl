---
name: testing-ci
description: This skill provides testing patterns, mocking strategies for AWS services, and CI/CD pipeline templates. Covers pytest, Jest/Vitest, moto, aws-sdk-client-mock, GitHub Actions, and CodePipeline. Triggers on requests about testing, mocking, CI/CD, coverage, or deployment pipelines.
---

# Testing & CI/CD Skill

This skill provides testing patterns, mocking strategies, and CI/CD pipeline templates for AWS application development.

## Activation Keywords
- test, testing, unit test, integration test, e2e
- mock, moto, aws-sdk-client-mock, fixture
- CI, CD, pipeline, GitHub Actions, CodePipeline, deploy
- coverage, pytest, jest, vitest

## Testing Philosophy

### Test Pyramid for AWS Apps
- **Unit tests (70%)** — Business logic, pure functions, no AWS calls
- **Integration tests (20%)** — AWS service interactions with mocks (moto, localstack)
- **E2E tests (10%)** — Deployed stack, real AWS services, smoke tests

### What to Test
- Business logic in isolation (service layer)
- AWS SDK call parameters (are you sending the right request?)
- Error handling paths (what happens when DynamoDB throttles?)
- Input validation and edge cases
- IAM policy correctness (via integration tests)

### What NOT to Unit Test
- AWS SDK internals (trust the SDK)
- Infrastructure provisioning (test with CDK assertions instead)
- Third-party library behavior

## Framework Selection

| Language | Framework | AWS Mocking |
|---|---|---|
| Python | pytest | moto, localstack |
| TypeScript | Vitest (preferred) or Jest | aws-sdk-client-mock |
| Go | go test + testify | aws-sdk-go-v2/service/*/mock |
| CDK | CDK assertions | Template.fromStack() |

## Coverage Targets
- Business logic: 80%+
- Lambda handlers: 70%+
- Infrastructure (CDK): assertions on critical resources
- Overall project: 75%+ (don't chase 100%)
