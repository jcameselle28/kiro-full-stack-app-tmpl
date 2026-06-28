# Security Guardrails

These rules apply to all application code, configuration, and recommendations.

## Credentials and Secrets
- Never hardcode credentials, API keys, secrets, or database connection strings in code or configs
- Load secrets at runtime from AWS Secrets Manager or SSM Parameter Store
- On EC2, use the instance profile / default credential chain — do not store long-lived access keys
- Never log or print sensitive values, even in debug mode
- Rotate credentials on any suspected exposure

## Application Security
- Validate and sanitize all external input at the boundary (request bodies, query params, headers)
- Always use parameterized queries / ORM bindings — never build SQL by string concatenation
- Enforce authentication and authorization on every non-public endpoint; deny by default
- Set secure response headers (HSTS, CSP, X-Content-Type-Options, etc.)
- Protect against CSRF for cookie-based sessions; prefer same-site cookies
- Keep dependencies patched; pin versions and run vulnerability scans in CI
- Do not expose stack traces or internal error details to clients

## Data Protection
- Encrypt at rest by default (RDS, S3, EBS)
- Enforce TLS/HTTPS for all data in transit — terminate TLS at the ALB/CloudFront and use ACM-managed certificates
- Use AWS-managed KMS keys at minimum; customer-managed keys when compliance requires it
- Minimize collection and retention of personal data; mask sensitive fields in logs

## Edge & Network Protection
- Front public web traffic with CloudFront + AWS WAF (managed rule groups + rate-based rules)
- Restrict security groups to the minimum required ports and sources — no `0.0.0.0/0` on database or admin ports
- Keep RDS in private subnets; reachable only from the application tier
- Apply least privilege to the EC2 instance role — scope to the exact services and resources the app needs

## Operational Security
- Never run destructive commands without explicit user confirmation
- Verify the target resource and region before any mutation
- Flag any public S3 buckets, open security groups, or unencrypted storage
