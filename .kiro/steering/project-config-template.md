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

## Tech Stack
- **Languages**: [Python 3.11+ | TypeScript (Node.js 20+) | both]
- **Backend framework**: [FastAPI / Flask / Django  |  Express / Fastify / NestJS]
- **Frontend**: [React / Next.js | none]
- **Database**: RDS ([PostgreSQL | MySQL]) accessed via [SQLAlchemy | Prisma | TypeORM]
- **IaC Tool**: [CDK (TypeScript) | Terraform]

## Target AWS Architecture
- **Compute**: EC2 (Auto Scaling Group) behind an Application Load Balancer (ALB)
- **Edge / CDN**: CloudFront
- **Web security**: AWS WAF (managed + rate-based rules)
- **Database**: RDS in private subnets (Multi-AZ in prod)
- **Static assets**: S3 (served via CloudFront)
- **Config & secrets**: Secrets Manager / SSM Parameter Store
- **Observability**: CloudWatch Logs & Metrics
- **DNS / TLS**: Route 53 + ACM

## Conventions
- **Branch Strategy**: [trunk-based | github-flow | gitflow]
- **Main Branch**: [main | master]
- **Commit Style**: [conventional commits | free-form]
- **PR Requirements**: [1 approval | 2 approvals]

## Deployment
- **CI/CD**: [GitHub Actions | GitLab CI | CodePipeline]
- **Environments**: [dev → staging → prod | dev → prod]
- **Deploy Trigger**: [merge to main | tag-based | manual]
- **Rollback Strategy**: [ALB target group swap | redeploy previous AMI/image | manual]

## Security
- **Auth**: [Cognito | custom JWT | session-based | none]
- **Secrets Management**: [Secrets Manager | SSM Parameter Store]
- **Encryption**: [AWS-managed KMS | customer-managed KMS] (at rest on RDS/S3/EBS); TLS at ALB + CloudFront
- **Compliance**: [SOC2 | PCI-DSS | HIPAA | none]
