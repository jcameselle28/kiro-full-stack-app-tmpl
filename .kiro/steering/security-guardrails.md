---
inclusion: always
---

# Security Guardrails

These rules apply to all operations, scripts, and recommendations.

## Credentials and Secrets
- Never hardcode credentials, API keys, or secrets in code or configs
- Use AWS Secrets Manager, SSM Parameter Store, or environment variables
- Never log or print sensitive values, even in debug mode
- Rotate credentials on any suspected exposure

## IAM and Access
- Always follow least-privilege principle
- Prefer IAM roles over access keys
- No wildcard (`*`) actions or resources in IAM policies unless explicitly justified
- Use conditions (source IP, MFA, tags) to restrict policy scope
- Review and flag any `iam:PassRole` or `sts:AssumeRole` with broad trust

## Encryption
- Encrypt at rest by default (S3, EBS, RDS, DynamoDB, EFS)
- Enforce TLS/HTTPS for data in transit
- Use AWS-managed KMS keys minimum, customer-managed when compliance requires it
- Never disable default encryption on any service

## Network Security
- No security group rules with `0.0.0.0/0` on sensitive ports (SSH, RDP, DB ports)
- Use VPC endpoints for AWS service access where possible
- Prefer private subnets for workloads, public only for load balancers
- Log all VPC flow logs for production environments

## Operational Security
- Never run destructive commands without explicit user confirmation
- Always verify target resource and region before mutations
- Tag all resources with `Environment`, `Owner`, and `ManagedBy`
- Audit trail: prefer CloudTrail-logged API calls over direct console actions

## Compliance Flags
- Flag any public S3 buckets, open security groups, or unencrypted storage
- Flag any IAM users with console access but no MFA
- Flag any cross-account access without explicit trust policy review
