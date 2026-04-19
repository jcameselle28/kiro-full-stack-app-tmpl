---
inclusion: fileMatch
fileMatchPattern: "**/*.tf,**/template.yaml,**/template.yml,**/cdk.json,**/samconfig.toml,**/*.template.json"
---

# Infrastructure as Code Conventions

## General Principles
- Infrastructure is code — same review, testing, and versioning standards apply
- Prefer declarative over imperative
- One stack/module per bounded context or service
- Separate stateful resources (databases, S3) from stateless (Lambda, ECS)
- Never hardcode account IDs, regions, or ARNs — use parameters/variables

## Naming Conventions

### Resources
- Pattern: `{project}-{environment}-{service}-{resource}`
- Example: `myapp-prod-api-lambda`, `myapp-dev-orders-table`
- Use lowercase with hyphens (no underscores in resource names)

### Tags (mandatory on all resources)
- `Environment`: prod | staging | dev
- `Team`: owning team name
- `Application`: application or service name
- `ManagedBy`: cdk | terraform | sam | cloudformation
- `CostCenter`: billing allocation code

### Files and Modules
- CDK: one stack per file, named `{service}-stack.ts`
- Terraform: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf` per module
- SAM: `template.yaml` at project root, nested stacks in `infrastructure/`

## CDK Conventions
- Use L2 constructs (higher-level) over L1 (Cfn*) when available
- Define props interfaces for all custom constructs
- Use `cdk.Tags.of(this).add()` for consistent tagging
- Enable removal policies explicitly (RETAIN for stateful, DESTROY for dev)
- Use `cdk.CfnOutput` for cross-stack references
- Run `cdk diff` before every deploy

## SAM Conventions
- Use `Globals` section for shared Lambda configuration
- Define `Parameters` for environment-specific values
- Use `AWS::Serverless::Function` over raw `AWS::Lambda::Function`
- Include `Metadata` for build configuration
- Use `samconfig.toml` for environment-specific deploy settings

## Terraform Conventions
- Use modules for reusable infrastructure patterns
- Lock provider versions in `versions.tf`
- Use `terraform fmt` and `terraform validate` in CI
- Remote state in S3 with DynamoDB locking
- Use workspaces or directory structure for environments
- Output all resource IDs and ARNs needed by other modules

## Security Requirements
- Encryption at rest: enabled on all storage resources
- Encryption in transit: TLS/HTTPS enforced
- No public access unless explicitly justified and documented
- Least-privilege IAM: scope to exact actions and resource ARNs
- No secrets in templates — use SSM Parameter Store or Secrets Manager references
- Enable logging: CloudTrail, VPC Flow Logs, access logs

## Environment Strategy
- `dev`: permissive, auto-deploy on merge, DESTROY removal policies
- `staging`: mirrors prod config, manual approval for deploy
- `prod`: strict, change sets reviewed, RETAIN removal policies, multi-AZ

## CI/CD Pipeline Conventions (GitLab CI)

### Pipeline Structure
```yaml
stages:
  - validate    # lint, format check, template validation
  - test        # unit tests, CDK assertions, security scan
  - build       # sam build, cdk synth, docker build
  - diff        # cdk diff / changeset preview (merge requests only)
  - deploy-dev  # auto on merge to main
  - deploy-stg  # auto or manual gate
  - deploy-prod # manual gate, requires approval
```

### GitLab CI Rules
- Use `rules:` syntax (not `only:/except:`)
- Use `id_tokens` with OIDC for AWS authentication — no stored access keys
- Use `environment:` blocks for deployment tracking
- Use `when: manual` for production deployments
- Cache `node_modules/`, `.pip/`, `.aws-sam/` across pipelines
- Store AWS role ARNs and config in GitLab CI/CD Variables (Settings → CI/CD → Variables)
- Use `dependencies:` to control artifact flow between stages
