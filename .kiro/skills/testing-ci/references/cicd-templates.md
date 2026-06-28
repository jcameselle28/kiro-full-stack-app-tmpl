# CI/CD Pipeline Templates

For web apps deployed on **EC2 / Auto Scaling behind an ALB**. The pipeline builds one immutable container image, pushes it to ECR, runs DB migrations, and rolls it out. See the `deploy-release` skill for rollout strategy (rolling / blue-green) and migration ordering; this file is the concrete YAML.

All templates use **OIDC** for AWS auth — no long-lived access keys.

## GitHub Actions — Build, Push to ECR, Deploy to ASG

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: my-app

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_USER: test, POSTGRES_PASSWORD: test, POSTGRES_DB: test }
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
    env:
      TEST_DATABASE_URL: postgresql://test:test@localhost:5432/test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -m "not e2e" --cov=src --cov-report=xml

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}
      - uses: aws-actions/amazon-ecr-login@v2
        id: ecr

      - name: Build and push image (tagged with git SHA)
        env:
          REGISTRY: ${{ steps.ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Run database migrations (expand)
        run: ./scripts/migrate.sh   # alembic upgrade head / prisma migrate deploy

      - name: Roll out to Auto Scaling Group
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          # Update the launch template to the new image tag, then start an instance refresh.
          aws ec2 create-launch-template-version \
            --launch-template-name my-app \
            --source-version '$Latest' \
            --launch-template-data "{\"UserData\":\"$(./scripts/render-userdata.sh $IMAGE_TAG | base64 -w0)\"}"
          aws autoscaling start-instance-refresh \
            --auto-scaling-group-name my-app-asg \
            --preferences '{"MinHealthyPercentage":90,"InstanceWarmup":120}'

      - name: Smoke test
        run: ./scripts/smoke.sh https://app.example.com
```

## GitHub Actions — Infrastructure (CDK) on PRs and main

```yaml
name: Infrastructure

on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

permissions: { id-token: write, contents: read }

jobs:
  cdk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: "npm" }
      - run: npm ci
      - run: npm test            # CDK assertions
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      - if: github.event_name == 'pull_request'
        run: npx cdk diff
      - if: github.ref == 'refs/heads/main'
        run: npx cdk deploy --all --require-approval never
```

## GitLab CI — Build, Push, Deploy

```yaml
stages: [test, build, migrate, deploy]

variables:
  AWS_DEFAULT_REGION: us-east-1
  ECR_REPOSITORY: my-app

test:
  stage: test
  image: python:3.11-slim
  services:
    - name: postgres:16
      alias: postgres
  variables:
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    POSTGRES_DB: test
    TEST_DATABASE_URL: postgresql://test:test@postgres:5432/test
  script:
    - pip install -r requirements-dev.txt
    - ruff check .
    - pytest -m "not e2e" --cov=src --cov-report=xml
  artifacts:
    reports:
      coverage_report: { coverage_format: cobertura, path: coverage.xml }

build:
  stage: build
  image: docker:24
  services: ["docker:24-dind"]
  id_tokens:
    AWS_TOKEN: { aud: https://gitlab.example.com }
  before_script:
    - apk add --no-cache aws-cli
    - aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
  script:
    - docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$CI_COMMIT_SHA .
    - docker push $ECR_REGISTRY/$ECR_REPOSITORY:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

migrate:
  stage: migrate
  image: python:3.11-slim
  id_tokens:
    AWS_TOKEN: { aud: https://gitlab.example.com }
  script:
    - ./scripts/migrate.sh        # backward-compatible (expand) migrations
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-production:
  stage: deploy
  image: amazon/aws-cli:latest
  environment: { name: production }
  id_tokens:
    AWS_TOKEN: { aud: https://gitlab.example.com }
  script:
    - aws ec2 create-launch-template-version --launch-template-name my-app --source-version '$Latest'
      --launch-template-data "{\"UserData\":\"$(./scripts/render-userdata.sh $CI_COMMIT_SHA | base64 -w0)\"}"
    - aws autoscaling start-instance-refresh --auto-scaling-group-name my-app-asg
      --preferences '{"MinHealthyPercentage":90,"InstanceWarmup":120}'
    - ./scripts/smoke.sh https://app.example.com
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual            # manual gate for production
```

## Blue/Green Variant

For higher-risk releases, register the new image into a **green** target group, health-check and smoke-test it, then shift the ALB listener from blue → green (or weighted for canary). Roll back by shifting the listener back to blue. See `deploy-release/references/patterns.md` for the target-group mechanics.

## Best Practices

- **OIDC** for AWS auth (GitHub `id-token`, GitLab `id_tokens`) — no stored keys
- Build the image **once**, tag with the git SHA, and promote that same image across environments
- Run **expand** (backward-compatible) migrations before the rollout; contract in a later release
- New instances must pass **ALB target group health checks** before old ones drain
- Separate test / build / migrate / deploy stages for clear failure isolation
- Manual gate (`environment` protection / `when: manual`) for production
- Run `cdk diff` on PRs/MRs so reviewers see infrastructure changes
- Pin action/image versions; scan images (Trivy/Snyk) before push
- Store role ARNs and config in CI/CD variables, never in the YAML
