# CI/CD Pipeline Templates

## GitHub Actions — SAM Serverless Deploy

```yaml
name: Deploy Serverless App

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: pytest -m "not e2e" --cov=src --cov-report=xml
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage.xml

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      - uses: aws-actions/setup-sam@v2
      - run: sam build
      - run: sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

## GitHub Actions — CDK Deploy

```yaml
name: Deploy CDK Stack

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage

  diff:
    needs: test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      - run: npx cdk diff

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1
      - run: npx cdk deploy --all --require-approval never
```

## GitHub Actions — Container (ECS)

```yaml
name: Build and Deploy to ECS

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

env:
  ECR_REPOSITORY: my-app
  ECS_CLUSTER: production
  ECS_SERVICE: my-app-service
  CONTAINER_NAME: app

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1

      - uses: aws-actions/amazon-ecr-login@v2
        id: login-ecr

      - name: Build and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Update ECS service
        env:
          IMAGE_TAG: ${{ github.sha }}
        run: |
          aws ecs update-service \
            --cluster $ECS_CLUSTER \
            --service $ECS_SERVICE \
            --force-new-deployment
```

## AWS CodePipeline (CloudFormation)

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Description: CI/CD Pipeline for serverless application

Resources:
  Pipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      Name: my-app-pipeline
      RoleArn: !GetAtt PipelineRole.Arn
      Stages:
        - Name: Source
          Actions:
            - Name: GitHubSource
              ActionTypeId:
                Category: Source
                Owner: ThirdParty
                Provider: GitHub
                Version: "1"
              Configuration:
                Owner: !Ref GitHubOwner
                Repo: !Ref GitHubRepo
                Branch: main
              OutputArtifacts:
                - Name: SourceOutput

        - Name: Build
          Actions:
            - Name: BuildAndTest
              ActionTypeId:
                Category: Build
                Owner: AWS
                Provider: CodeBuild
                Version: "1"
              Configuration:
                ProjectName: !Ref BuildProject
              InputArtifacts:
                - Name: SourceOutput
              OutputArtifacts:
                - Name: BuildOutput

        - Name: Deploy
          Actions:
            - Name: DeployToProduction
              ActionTypeId:
                Category: Deploy
                Owner: AWS
                Provider: CloudFormation
                Version: "1"
              Configuration:
                ActionMode: CREATE_UPDATE
                StackName: my-app-production
                TemplatePath: BuildOutput::packaged.yaml
                RoleArn: !GetAtt DeployRole.Arn
              InputArtifacts:
                - Name: BuildOutput
```

## Best Practices

- Use OIDC for AWS authentication (GitHub Actions id-token, GitLab CI OIDC) — no long-lived keys
- Separate test/build/deploy stages for clear failure isolation
- Run `cdk diff` on merge requests so reviewers see infrastructure changes
- Use environment protection rules for production deploys
- Pin action/image versions for supply chain security
- Cache dependencies (npm, pip) to speed up builds
- Run security scanning (Snyk, Trivy) in the pipeline

## GitLab CI — SAM Serverless Deploy

```yaml
stages:
  - test
  - build
  - deploy

variables:
  AWS_DEFAULT_REGION: us-east-1
  SAM_CLI_TELEMETRY: "0"

test:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r requirements-dev.txt
    - pytest -m "not e2e" --cov=src --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

build:
  stage: build
  image: amazon/aws-sam-cli-build-image-python3.11
  script:
    - sam build
  artifacts:
    paths:
      - .aws-sam/

deploy-staging:
  stage: deploy
  image: amazon/aws-sam-cli-build-image-python3.11
  environment:
    name: staging
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  script:
    - >
      export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s"
      $(aws sts assume-role-with-web-identity
      --role-arn $AWS_DEPLOY_ROLE_ARN
      --role-session-name "gitlab-${CI_PROJECT_ID}-${CI_PIPELINE_ID}"
      --web-identity-token $AWS_TOKEN
      --duration-seconds 3600
      --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]'
      --output text))
    - sam deploy --config-env staging --no-confirm-changeset
  dependencies:
    - build
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-production:
  stage: deploy
  image: amazon/aws-sam-cli-build-image-python3.11
  environment:
    name: production
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  script:
    - >
      export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s"
      $(aws sts assume-role-with-web-identity
      --role-arn $AWS_DEPLOY_ROLE_ARN
      --role-session-name "gitlab-${CI_PROJECT_ID}-${CI_PIPELINE_ID}"
      --web-identity-token $AWS_TOKEN
      --duration-seconds 3600
      --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]'
      --output text))
    - sam deploy --config-env production --no-confirm-changeset
  dependencies:
    - build
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## GitLab CI — CDK Deploy

```yaml
stages:
  - test
  - diff
  - deploy

variables:
  AWS_DEFAULT_REGION: us-east-1

test:
  stage: test
  image: node:20-slim
  script:
    - npm ci
    - npm run lint
    - npm test -- --coverage
  cache:
    key: ${CI_COMMIT_REF_SLUG}
    paths:
      - node_modules/

cdk-diff:
  stage: diff
  image: node:20-slim
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  script:
    - npm ci
    - npx cdk diff
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

deploy-production:
  stage: deploy
  image: node:20-slim
  environment:
    name: production
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  script:
    - npm ci
    - npx cdk deploy --all --require-approval never
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## GitLab CI — Container (ECS)

```yaml
stages:
  - build
  - deploy

variables:
  AWS_DEFAULT_REGION: us-east-1
  ECR_REPOSITORY: my-app
  ECS_CLUSTER: production
  ECS_SERVICE: my-app-service

build-and-push:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  before_script:
    - apk add --no-cache aws-cli
    - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
  script:
    - docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$CI_COMMIT_SHA .
    - docker push $ECR_REGISTRY/$ECR_REPOSITORY:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

deploy-ecs:
  stage: deploy
  image: amazon/aws-cli:latest
  environment:
    name: production
  id_tokens:
    AWS_TOKEN:
      aud: https://gitlab.example.com
  script:
    - aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## GitLab CI Best Practices

- Use `id_tokens` with OIDC for AWS authentication — no stored access keys
- Use `rules:` instead of `only:/except:` (modern syntax)
- Cache `node_modules/` and `.pip/` across pipelines
- Use `when: manual` for production deploys
- Use `dependencies:` to control artifact passing between stages
- Store secrets in GitLab CI/CD Variables (Settings → CI/CD → Variables), never in `.gitlab-ci.yml`
- Use `environment:` blocks for deployment tracking and rollback support
