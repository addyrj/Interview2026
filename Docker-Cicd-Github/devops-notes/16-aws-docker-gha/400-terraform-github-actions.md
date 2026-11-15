# 400. Terraform + GitHub Actions
# हिंदी में: Terraform + GitHub Actions

---

## 🔵 Simple Definition (English)
**Terraform** describes infrastructure in declarative **HCL** files (`.tf`). You run `terraform plan` to preview changes and `terraform apply` to make them. It stores what it created in a **state file**. With GitHub Actions, a pull request runs `plan` and shows the result for review, and merging to `main` runs `apply`.

## 🔵 सरल परिभाषा (Hindi)
**Terraform** infrastructure को declarative **HCL** files (`.tf`) में describe करता है। बदलाव preview करने के लिए `terraform plan` और लागू करने के लिए `terraform apply` चलाते हैं। जो कुछ बनाया वह **state file** में store होता है। GitHub Actions के साथ pull request `plan` चलाकर review के लिए नतीजा दिखाता है, और `main` पर merge होने पर `apply` चलता है।

---

## 🔴 Problem it Solves
Infra changed by hand in the console cannot be reviewed, repeated, or rolled back, and different environments slowly differ ("works in staging"). Running Terraform from a laptop is risky too: two engineers apply at once, local state is lost, and nobody knows who changed what.

Terraform in CI gives: reviewed plans in PRs, one place that applies, remote state with locking, an audit trail in git, and the same code for dev/staging/prod with different variables.

## 🔴 यह क्यों बना? (Hindi)
Console में हाथ से बदला infra review, दोहराया या rollback नहीं किया जा सकता, और environments धीरे-धीरे अलग हो जाते हैं ("staging में चलता है")। Laptop से Terraform चलाना भी जोखिम भरा है: दो engineers एक साथ apply करते हैं, local state खो जाती है, और पता नहीं किसने क्या बदला।

CI में Terraform से मिलता है: PR में reviewed plan, apply करने की एक ही जगह, locking वाली remote state, git में audit trail, और dev/staging/prod के लिए वही code अलग variables के साथ।

---

## 🟢 How it Works — Step by Step

```
Step 1 → One-time: create S3 bucket for state (versioned, encrypted) [+ lock]
Step 2 → Write main.tf, variables.tf, outputs.tf, versions with a pinned provider
Step 3 → PR opened -> workflow: fmt -check, init, validate, plan -out=tfplan
Step 4 → Post plan summary as a PR comment; reviewers read it
Step 5 → Merge to main -> workflow: init, plan, then apply (environment approval)
Step 6 → Terraform takes the state lock, calls AWS APIs, updates state in S3
Step 7 → Outputs (URLs, ARNs) are printed; drift is detected by scheduled plan
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → एक बार: state के लिए S3 bucket बनाएँ (versioned, encrypted) [+ lock]
Step 2 → main.tf, variables.tf, outputs.tf लिखें, provider version pinned
Step 3 → PR खुलने पर workflow: fmt -check, init, validate, plan -out=tfplan
Step 4 → Plan का summary PR comment में दिखाएँ; reviewers पढ़ें
Step 5 → main पर merge -> workflow: init, plan, फिर apply (environment approval)
Step 6 → Terraform state lock लेता है, AWS APIs call करता है, S3 में state update करता है
Step 7 → Outputs (URLs, ARNs) print होते हैं; scheduled plan से drift पकड़ा जाता है
```

---

## 🟡 Real World Example
A fintech manages VPC, RDS, ECS and IAM with Terraform in a `infra` repo. An engineer opens a PR changing the DB instance class; the PR comment shows `~ aws_db_instance.main (instance_class: db.t3.medium -> db.t3.large)` with "1 to change, 0 to destroy". The lead approves, merges, and a protected `production` environment waits for a second approval before `apply`. Once a week a scheduled `plan` runs; when someone changes a security group in the console, the plan shows drift and alerts the team.

## 🟡 Real Example Hindi mein
एक fintech `infra` repo में Terraform से VPC, RDS, ECS और IAM manage करता है। एक engineer PR में DB instance class बदलता है; PR comment दिखाता है `~ aws_db_instance.main (instance_class: db.t3.medium -> db.t3.large)` और "1 to change, 0 to destroy"। Lead approve करके merge करता है, और protected `production` environment `apply` से पहले दूसरी approval का इंतज़ार करता है। हफ़्ते में एक बार scheduled `plan` चलता है; किसी ने console में security group बदला तो plan drift दिखाकर टीम को alert करता है।

---

## 💻 Code / Config Example — Basic

```hcl
# main.tf : one S3 bucket as the smallest working example
terraform {
  required_version = ">= 1.6.0"                  # minimum Terraform CLI version
  required_providers {
    aws = {
      source  = "hashicorp/aws"                  # official AWS provider
      version = "~> 5.0"                         # allow 5.x only (pin major; update deliberately)
    }
  }
}

provider "aws" {
  region = "ap-south-1"                          # Mumbai
}

resource "aws_s3_bucket" "logs" {
  bucket = "myco-prod-app-logs-111122223333"     # globally unique bucket name
  tags = {
    ManagedBy = "terraform"                      # tag so humans know not to edit by hand
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id   # attach to the bucket above
  block_public_acls       = true                 # block public ACLs
  block_public_policy     = true                 # block public bucket policies
  ignore_public_acls      = true                 # ignore any public ACLs
  restrict_public_buckets = true                 # restrict public access
}
```

```bash
# local flow (what CI automates)
terraform fmt -check -recursive    # fail if files are not formatted
terraform init                     # download providers, configure backend
terraform validate                 # syntax and reference check
terraform plan -out=tfplan         # preview and save the plan file
terraform apply tfplan             # apply exactly the reviewed plan
```

## 💻 Code / Config Example — Advanced

Remote state in S3 with locking, plus plan-on-PR and apply-on-merge workflows using OIDC. The `use_lockfile` option needs Terraform 1.10 or newer; older versions use a DynamoDB table (`dynamodb_table`). Both are version-dependent; check your CLI version.

```hcl
# backend.tf : remote state so CI and humans share one source of truth
terraform {
  backend "s3" {
    bucket       = "myco-tfstate-111122223333"   # pre-created, versioned, encrypted, private bucket
    key          = "prod/app/terraform.tfstate"  # path of this state file
    region       = "ap-south-1"                  # bucket region
    encrypt      = true                          # encrypt state at rest (state may contain secrets)
    use_lockfile = true                          # S3 native locking (Terraform >= 1.10); else use dynamodb_table
  }
}
```

```yaml
name: terraform                                  # workflow name
on:
  pull_request:
    paths: ['infra/**']                          # plan on infra PRs
  push:
    branches: [main]
    paths: ['infra/**']                          # apply on merge
permissions:
  id-token: write                                # OIDC
  contents: read                                 # checkout
  pull-requests: write                           # post plan comment
defaults:
  run:
    working-directory: infra                     # Terraform folder
concurrency:
  group: terraform-prod                          # never two runs against the same state
  cancel-in-progress: false                      # do not kill a running apply
jobs:
  plan:
    runs-on: ubuntu-latest                       # runner
    steps:
      - uses: actions/checkout@v4                # code
      - uses: hashicorp/setup-terraform@v3       # installs Terraform CLI
        with:
          terraform_version: 1.9.8               # pin CLI version (example; update deliberately)
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: ${{ vars.TF_PLAN_ROLE_ARN }}   # read-only role for PRs
          aws-region: ap-south-1
      - run: terraform fmt -check -recursive     # style gate
      - run: terraform init -input=false         # init without prompts
      - run: terraform validate                  # static validation
      - id: plan
        run: terraform plan -input=false -no-color -out=tfplan   # create plan; -no-color for clean comments
        continue-on-error: true                  # still comment on failure
      - name: Comment plan on PR                 # show reviewers what will change
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const { execSync } = require('child_process');
            const out = execSync('terraform show -no-color tfplan', { cwd: 'infra', maxBuffer: 10*1024*1024 }).toString().slice(0, 60000);
            await github.rest.issues.createComment({
              owner: context.repo.owner, repo: context.repo.repo, issue_number: context.issue.number,
              body: '#### Terraform plan\n```\n' + out + '\n```'
            });
      - if: steps.plan.outcome == 'failure'      # fail the job after commenting
        run: exit 1
      - uses: actions/upload-artifact@v4         # keep the plan for apply
        with:
          name: tfplan
          path: infra/tfplan
  apply:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'   # only on main
    needs: plan                                  # after a successful plan
    runs-on: ubuntu-latest
    environment: production                      # required reviewers gate
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.9.8
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.TF_APPLY_ROLE_ARN }}   # powerful role, only assumable from this environment
          aws-region: ap-south-1
      - run: terraform init -input=false
      - uses: actions/download-artifact@v4       # get the reviewed plan
        with:
          name: tfplan
          path: infra
      - run: terraform apply -input=false tfplan # apply exactly that plan (fails if state changed since)
```

Not executed against a real AWS account here. Pin versions shown are examples; the `github-script` snippet is a common pattern, trim output if it exceeds comment size limits.

---

## 🟠 My Stack Integration
- **AWS pieces from this section**: ECR repo, ECS cluster and service, ALB, S3 + CloudFront, IAM OIDC provider and CI roles can all be Terraform resources.
- **Node.js / FastAPI**: Terraform creates infra; the app pipeline (topics 386-392) only deploys images. Use `lifecycle { ignore_changes = [task_definition] }` on the ECS service so Terraform does not fight the app deploys.
- **React**: bucket, distribution and OAC in Terraform; build upload stays in the frontend pipeline.
- **Nginx / VPS**: Terraform can also manage VPS providers (DigitalOcean, Hetzner), DNS (Route 53/Cloudflare) and EC2 with user-data that installs Docker and Nginx.
- **Secrets**: never hard-code. Use variables from `TF_VAR_*` (GitHub environment secrets) or reference Secrets Manager with `data` sources; remember the value still lands in state.
- **Choice**: Terraform (HCL, multi-cloud) vs CDK (code, AWS-only, topic 399); pick one per repo, not both.

```hcl
# ECS service managed by Terraform but deployed by the app pipeline
resource "aws_ecs_service" "api" {
  name            = "orders-api"                 # service name
  cluster         = aws_ecs_cluster.main.id      # cluster reference
  task_definition = aws_ecs_task_definition.api.arn   # initial revision
  desired_count   = 2                            # baseline tasks
  lifecycle {
    ignore_changes = [task_definition]           # app pipeline owns the revision, avoid constant drift
  }
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Local state or committing `terraform.tfstate` to git.
✅ Correct: Remote encrypted state with locking; add `*.tfstate*` and `.terraform/` to `.gitignore`.

❌ Mistake 2: `terraform apply -auto-approve` on every push, with no plan review.
✅ Correct: PR plan + protected environment; apply the saved plan file.

❌ Mistake 3: Unpinned provider/CLI versions, so a surprise upgrade changes behaviour.
✅ Correct: Pin versions and commit `.terraform.lock.hcl`.

❌ Mistake 4: One giant state for everything.
✅ Correct: Split by environment and domain (network, data, app) to shrink blast radius and plan time.

❌ Mistake 5: Same admin role for plan on PRs and apply on main.
✅ Correct: Read-only role for plans, write role only for the protected apply job.

---

## 🧠 Tricky Interview Question
Two merges happen a minute apart and both start `terraform apply`. What prevents corrupted state, and what if the first job gets cancelled mid-apply?

Answer: State locking (S3 lockfile or DynamoDB) lets only one run hold the lock; the second waits or fails with "Error acquiring the state lock". `concurrency` in GitHub Actions with `cancel-in-progress: false` queues runs and avoids killing an apply. If a job is killed, the lock may remain; check that no apply is running, then `terraform force-unlock <ID>`. A half-applied change is fine in principle because Terraform records what it created; the next plan shows what remains.

---

## ⚫ Interview Questions + Answers

Q1: What is Terraform state and why does it matter?
A1: A mapping between your code and real resources (IDs, attributes). Terraform uses it to compute diffs. Lose it and Terraform wants to recreate everything; leak it and secrets inside may be exposed, so encrypt and restrict.

Q2: `plan` vs `apply`?
A2: `plan` computes and shows the diff without changing anything. `apply` executes changes. Applying a saved plan file guarantees you apply exactly what was reviewed.

Q3: What is drift and how do you handle it?
A3: Real infra changed outside Terraform. Detect with scheduled `terraform plan -detailed-exitcode` (exit code 2 means changes). Fix by reverting the manual change or updating the code, or `terraform import` for resources made by hand.

Q4: `count` vs `for_each`?
A4: `count` indexes by number (removing item 0 shifts the others and may recreate them). `for_each` keys by name/map key, which is safer for stable identity.

Q5: Terraform vs CloudFormation/CDK?
A5: Terraform is cloud-agnostic with its own state and a large provider ecosystem. CloudFormation/CDK are AWS-native with state managed by AWS and tight service coverage. Teams choose based on multi-cloud needs and skills.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Infra must be reviewable, repeatable, and consistent across environments
- You use multiple clouds or providers (AWS + Cloudflare + GitHub)
- Several engineers change infrastructure

❌ Avoid when:
- A single throwaway resource
- No one will maintain state and pipelines (unmanaged IaC becomes a risk)
- The team is already fully on CDK with no multi-cloud need

---

## 📊 Visual Diagram
```
 Developer --PR--> GitHub
                    |  fmt, init, validate, plan   (read-only OIDC role)
                    v
              PR comment: "1 to add, 1 to change, 0 to destroy"
                    |  review + merge
                    v
              main --> apply job (environment approval, write OIDC role)
                    |
        +-----------+-------------------------+
        v                                     v
  S3 backend (state + lock)             AWS APIs: VPC, ECS, S3, IAM ...
  prod/app/terraform.tfstate            (resources created/updated)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| HCL | Terraform's config language | Terraform की config भाषा |
| Provider | Plugin for a platform (AWS) | किसी platform (AWS) का plugin |
| State | Record of managed resources | manage हो रहे resources का record |
| Backend | Where state is stored | state कहाँ रखी जाए |
| Plan | Preview of changes | बदलावों का preview |
| Drift | Reality differs from code | असलियत का code से अलग होना |
| Lock | Prevents concurrent state changes | एक साथ state बदलने से रोकता है |

---

## ⚡ 3-Line Summary
English: Terraform describes infrastructure in HCL and tracks it in a state file with plan and apply steps.
English: In GitHub Actions run plan on pull requests and apply on merge, with OIDC roles and remote locked state.
English: Pin versions, split states, review plans, and detect drift on a schedule.
Hindi: Terraform infrastructure को HCL में describe करता है और state file में track करता है, plan और apply steps के साथ।
Hindi: GitHub Actions में PR पर plan और merge पर apply चलाएँ, OIDC roles और locked remote state के साथ।
Hindi: Versions pin करें, states बाँटें, plans review करें और schedule पर drift पकड़ें।

---

## ➡️ Next Topic
**401. Nginx in Docker**: the AWS deployment section is done; next section covers running Nginx in containers as the front door for your Node.js and FastAPI apps.
