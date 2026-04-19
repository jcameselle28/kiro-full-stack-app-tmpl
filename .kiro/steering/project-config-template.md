---
inclusion: manual
---

# Project Configuration

> Copy this file, rename it to `project-config.md`, change `inclusion` to `always`,
> and fill in the values for your specific project.

## Project Identity
- **Name**: [project-name]
- **Description**: [one-line description]
- **Team**: [team-name]
- **AWS Account(s)**: [account-id(s)]
- **Primary Region**: [us-east-1]
- **DR Region**: [us-west-2 or none]

## Tech Stack
- **Runtime**: [Python 3.11 | Node.js 20 | Go 1.21]
- **Framework**: [FastAPI | CDK | SAM | Express | none]
- **IaC Tool**: [CDK (TypeScript) | SAM | Terraform]
- **Database**: [DynamoDB | RDS PostgreSQL | Aurora | none]
- **Messaging**: [SQS | EventBridge | SNS | Kafka | none]
- **Compute**: [Lambda | ECS Fargate | EKS | EC2]

## Conventions
- **Branch Strategy**: [trunk-based | gitflow | github-flow]
- **Main Branch**: [main | master]
- **Commit Style**: [conventional commits | free-form]
- **PR Requirements**: [1 approval | 2 approvals | auto-merge on green]

## Deployment
- **CI/CD**: [GitLab CI | GitHub Actions | CodePipeline]
- **Environments**: [dev → staging → prod | dev → prod]
- **Deploy Trigger**: [merge to main | manual | tag-based]
- **Rollback Strategy**: [automatic | manual | canary]

## Observability
- **Logging**: [CloudWatch Logs | Datadog | ELK]
- **Metrics**: [CloudWatch Metrics | Prometheus/Grafana | Datadog]
- **Tracing**: [X-Ray | OpenTelemetry | Datadog APM]
- **Alerting**: [CloudWatch Alarms | PagerDuty | Opsgenie]

## Security
- **Auth**: [Cognito | IAM | custom JWT | none]
- **Secrets Management**: [Secrets Manager | SSM Parameter Store]
- **Encryption**: [AWS-managed KMS | customer-managed KMS]
- **Compliance**: [SOC2 | PCI-DSS | HIPAA | none]

## Cost Constraints
- **Monthly Budget**: [$X,XXX]
- **Cost Alerts**: [at 50%, 80%, 100% of budget]
- **Commitment Strategy**: [Savings Plans | Reserved Instances | on-demand only]
