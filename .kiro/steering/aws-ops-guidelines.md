---
inclusion: always
---

# AWS Ops Operational Guidelines

## Agent Architecture

The `aws-ops` agent is the principal orchestrator for all AWS cloud operations. It routes requests to specialized sub-agents:

- **cloudops** → Infrastructure, deployments, IaC, resource management
- **aws-dev** → Application code, AWS SDK integrations, Lambda handlers, API development, testing
- **sre** → Observability, reliability, incidents, SLOs, runbooks
- **finops** → Cost optimization, billing, rightsizing, unit economics
- **security-ops** → IAM, compliance, vulnerabilities, data protection
- **network-ops** → VPC, DNS, load balancing, connectivity, CDN

## Cross-Cutting Concerns

These principles apply across ALL sub-agents:

### Change Management
- All changes require a rollback plan
- Destructive operations need explicit user confirmation
- Prefer dry-run / plan mode before apply
- Document blast radius for every change

### Well-Architected Alignment
Map recommendations to AWS Well-Architected pillars:
- Operational Excellence
- Security
- Reliability
- Performance Efficiency
- Cost Optimization
- Sustainability

### Tagging Strategy
Enforce consistent tagging:
- `Environment` (prod/staging/dev)
- `Team` / `Owner`
- `CostCenter`
- `Application`
- `ManagedBy` (terraform/cdk/manual)

### Incident Severity Levels
- **SEV1**: Customer-facing outage, all hands on deck
- **SEV2**: Degraded service, active mitigation required
- **SEV3**: Non-critical issue, fix within business hours
- **SEV4**: Minor issue, fix in next sprint

## Common Workflows

### 1. Incident Response
`aws-ops` → `sre` (triage) → `cloudops` (infra check) → `network-ops` (connectivity) → `security-ops` (if breach suspected)

### 2. Cost Review
`aws-ops` → `finops` (analysis) → `cloudops` (rightsizing implementation) → `sre` (validate SLOs maintained)

### 3. Security Audit
`aws-ops` → `security-ops` (audit) → `network-ops` (network security) → `cloudops` (remediation)

### 4. New Service Deployment
`aws-ops` → `aws-dev` (application code) → `cloudops` (infra) → `network-ops` (networking) → `security-ops` (security review) → `sre` (observability) → `finops` (cost estimate)
