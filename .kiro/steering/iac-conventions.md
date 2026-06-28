---
inclusion: fileMatch
fileMatchPattern: "**/*.tf,**/cdk.json,**/*.template.json,**/*.template.yaml"
---

# Infrastructure as Code Conventions

## General Principles
- Infrastructure is code — same review, testing, and versioning standards apply
- Prefer declarative over imperative
- One stack/module per bounded context (network, data, app, edge)
- Separate stateful resources (RDS, S3) from stateless (EC2/ASG, ALB) so they can be replaced independently
- Never hardcode account IDs, regions, or ARNs — use parameters/variables/outputs

## Naming Conventions

### Resources
- Pattern: `{project}-{environment}-{component}`
- Example: `myapp-prod-alb`, `myapp-dev-rds`
- Use lowercase with hyphens

### Tags (mandatory on all resources)
- `Environment`: prod | staging | dev
- `Application`: {project}
- `ManagedBy`: cdk | terraform | cloudformation
- `Owner`: owning team

### Files and Modules
- CDK: one stack per file, named `{component}-stack.ts` (e.g., `network-stack.ts`, `app-stack.ts`)
- Terraform: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf` per module

## Reference Architecture (AWS web app)
Provision these layers as distinct stacks/modules:
- **Network**: VPC, public subnets (ALB), private subnets (EC2 + RDS), NAT, security groups
- **Data**: RDS (Multi-AZ in prod), subnet group, parameter group, automated backups
- **App**: EC2 launch template + Auto Scaling Group, target group, instance role (least privilege)
- **Edge**: ALB (HTTPS listener, ACM cert), CloudFront distribution, AWS WAF web ACL
- **DNS/Certs**: Route 53 records, ACM certificates

## CDK Conventions
- Use L2 constructs (higher-level) over L1 (Cfn*) when available
- Define props interfaces for all custom constructs
- Use `cdk.Tags.of(this).add()` for consistent tagging
- Set removal policies explicitly (RETAIN for RDS/S3, DESTROY for dev-only resources)
- Use `cdk.CfnOutput` for cross-stack references
- Run `cdk diff` before every deploy

## Terraform Conventions
- Use modules for reusable infrastructure patterns
- Lock provider versions in `versions.tf`
- Run `terraform fmt` and `terraform validate` in CI
- Remote state in S3 with DynamoDB locking
- Use workspaces or directory structure for environments
- Output all resource IDs and ARNs needed by other modules

## Security Requirements
- Encryption at rest enabled on RDS, S3, and EBS volumes
- TLS/HTTPS enforced at ALB and CloudFront (ACM certificates)
- RDS in private subnets; no public accessibility
- Security groups scoped to minimum ports/sources — no `0.0.0.0/0` on DB or admin ports
- AWS WAF attached to CloudFront/ALB with managed + rate-based rules
- Least-privilege EC2 instance role — scope to exact actions and resource ARNs
- No secrets in templates — reference SSM Parameter Store or Secrets Manager
- Enable access logs (ALB, CloudFront) and database logging

## Environment Strategy
- `dev`: permissive, single-AZ, DESTROY removal policies
- `staging`: mirrors prod config, manual approval for deploy
- `prod`: strict, change sets reviewed, RETAIN removal policies, Multi-AZ RDS
