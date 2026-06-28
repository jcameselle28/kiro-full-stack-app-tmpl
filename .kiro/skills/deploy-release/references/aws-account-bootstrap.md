# AWS Account Bootstrap — First-Time Setup

One-time setup to make a **new AWS account** deployable. Do this before the first `cdk deploy` / `terraform apply` and before CI can deploy. All recipes follow `security-guardrails.md`: no long-lived keys, least privilege, encryption on by default.

Order: **identity → OIDC deploy role → IaC backend → DNS/ACM → first infra deploy**.

---

## 1. Identity & Credentials

- Use **IAM Identity Center (SSO)** for human/CLI access. Avoid IAM users with long-lived access keys; never use the root user for daily work.
- Configure a local profile: `aws configure sso`, then verify: `aws sts get-caller-identity`.
- On EC2 and in other AWS compute, rely on the **instance role / default credential chain** — not stored keys.

---

## 2. GitHub → AWS OIDC Deploy Role

Lets GitHub Actions assume a role via short-lived OIDC tokens — no access keys in CI.

### 2a. Create the OIDC identity provider (once per account)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list ffffffffffffffffffffffffffffffffffffffff
```
> GitHub's OIDC thumbprint is validated by AWS automatically; the `--thumbprint-list` value is no longer security-critical but the argument is still required by older CLI versions.

### 2b. Trust policy — scope it tightly to your repo

`trust-policy.json` (replace `<ACCOUNT_ID>`, `<OWNER>`, `<REPO>`):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike": { "token.actions.githubusercontent.com:sub": "repo:<OWNER>/<REPO>:ref:refs/heads/main" }
    }
  }]
}
```
- Restrict `sub` as narrowly as possible: a specific branch (`ref:refs/heads/main`), tag, or a GitHub **environment** (`environment:production`) for prod deploys.
- Do **not** leave `sub` as `repo:<OWNER>/<REPO>:*` for a role that can touch prod.

### 2c. Create the role and attach least-privilege permissions

```bash
aws iam create-role \
  --role-name github-deploy \
  --assume-role-policy-document file://trust-policy.json

# Attach a scoped permissions policy (ECR push, ASG instance refresh, the specific
# resources the deploy touches). Avoid AdministratorAccess.
aws iam put-role-policy \
  --role-name github-deploy \
  --policy-name deploy-permissions \
  --policy-document file://deploy-permissions.json
```

Store the resulting role ARN as the `AWS_DEPLOY_ROLE_ARN` secret in the GitHub repo. The CI templates in `testing-ci/references/cicd-templates.md` consume it via `aws-actions/configure-aws-credentials` with `permissions: id-token: write`.

---

## 3. IaC Backend

### CDK — bootstrap (once per account + region)

```bash
cdk bootstrap aws://<ACCOUNT_ID>/<REGION>
```
Creates the CDK toolkit stack (assets bucket, ECR repo for assets, deploy roles). Re-run per additional region you deploy into.

### Terraform — remote state backend

Create an **encrypted, versioned** S3 bucket (public access blocked) and a DynamoDB table for state locking **before** `terraform init`:

```bash
aws s3api create-bucket --bucket <STATE_BUCKET> --region <REGION> \
  --create-bucket-configuration LocationConstraint=<REGION>
aws s3api put-bucket-versioning --bucket <STATE_BUCKET> \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket <STATE_BUCKET> \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}'
aws s3api put-public-access-block --bucket <STATE_BUCKET> \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws dynamodb create-table --table-name <LOCK_TABLE> \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

`backend.tf`:
```hcl
terraform {
  backend "s3" {
    bucket         = "<STATE_BUCKET>"
    key            = "app/terraform.tfstate"
    region         = "<REGION>"
    dynamodb_table = "<LOCK_TABLE>"
    encrypt        = true
  }
}
```

---

## 4. DNS & TLS

- Create (or delegate) the **Route 53 hosted zone** for your domain.
- Request an **ACM certificate** and validate it via DNS:
  - For **CloudFront**, the cert must be in **`us-east-1`** regardless of your app region.
  - For an **ALB**, the cert lives in the app's region.

```bash
aws acm request-certificate \
  --domain-name app.example.com \
  --validation-method DNS \
  --region us-east-1
```
Then add the CNAME validation record ACM returns to the hosted zone (CDK/Terraform can manage this for you).

---

## 5. Verify Before First Deploy

- [ ] `aws sts get-caller-identity` returns the expected account
- [ ] OIDC provider + `github-deploy` role exist; trust policy scoped to the repo/branch/environment
- [ ] `AWS_DEPLOY_ROLE_ARN` secret set in the GitHub repo
- [ ] CDK bootstrapped (or Terraform state bucket + lock table created)
- [ ] Hosted zone live and ACM cert **issued** (not just requested)
- [ ] No security group exposes DB/admin ports to `0.0.0.0/0`; encryption defaults confirmed

Once these pass, run the first infra deploy (`cdk deploy` / `terraform apply`), then proceed to the release pipeline in `SKILL.md`.

---

> When the AWS MCP is enabled, the agent can look up current AWS guidance and inspect the live account (read-only by default) to confirm these resources exist. Treat the MCP as verification/augmentation — this file is the source of truth for *how this template bootstraps an account*.
>
> Content rephrased from AWS documentation for licensing compliance.
