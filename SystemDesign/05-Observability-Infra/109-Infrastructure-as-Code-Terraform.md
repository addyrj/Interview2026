# 109. Infrastructure as Code (Terraform)
# हिंदी में: Infrastructure as Code — सर्वर, database, network, load balancer जैसी cloud चीज़ें हाथ से console में बनाने की जगह code (Terraform) में लिखना, जिसे Git में रखकर review, दोहराया और अपने आप लागू किया जा सके

---

## 🔵 Simple Definition (English)
**Infrastructure as Code (IaC)** means defining and managing infrastructure (VPCs, subnets, security groups, load balancers, databases, Kubernetes clusters, DNS, IAM roles, S3 buckets, queues) through **declarative code files** stored in **version control**, instead of clicking in cloud consoles.
**Terraform** (HashiCorp; open-source fork **OpenTofu**) is the most popular multi-cloud IaC tool. You write **HCL** describing the desired resources, run **`terraform plan`** to preview changes, and **`terraform apply`** to make reality match. Terraform tracks what it manages in a **state file**.
Alternatives: AWS CloudFormation/CDK, Pulumi (real programming languages), Crossplane, Ansible (configuration management).

## 🔵 सरल परिभाषा (Hindi)
IaC में cloud की हर चीज़ (VPC, सर्वर, DB, load balancer, DNS, permissions) हाथ से console में बनाने की जगह code में लिखते हो और Git में रखते हो।
Terraform सबसे लोकप्रिय टूल है: code लिखो → `terraform plan` से देखो क्या बदलेगा → `terraform apply` से बना दो। हर environment (dev, staging, prod, दूसरा region) एक जैसा बनता है।

---

## 🔴 Problem it Solves
"ClickOps" (manual console changes) leads to:
- **Snowflake environments:** staging differs from prod in mysterious ways ("works in staging!").
- **No history or review:** who opened port 5432 to 0.0.0.0/0, and when?
- **Slow, error-prone setup:** building a new region or environment takes weeks and is never identical.
- **Disaster recovery impossible** to do quickly (Topic 105): you can't remember 400 settings.
- **Drift:** someone changes something manually and nobody knows.

IaC gives **repeatability, version history, code review, automation, documentation-as-code and fast rebuilds**.

## 🔴 यह क्यों बना? (Hindi)
Console में हाथ से बदलाव (ClickOps) से: staging और prod अलग, पता नहीं किसने DB port पूरे इंटरनेट पर खोला, नया region बनाने में हफ़्ते, आपदा के बाद 400 settings याद नहीं।
IaC से सब कुछ दोहराने लायक, इतिहास के साथ, review होकर, और मिनटों में दोबारा बनने लायक होता है।

---

## 🟢 How it Works — Step by Step

### Workflow

```
1. Write HCL (main.tf, variables.tf, outputs.tf)
2. terraform init     → download providers (aws, cloudflare, datadog...), configure backend (state)
3. terraform plan     → compare code vs state vs real cloud → show + / ~ / − changes
4. Review the plan in a Pull Request (CI posts plan output)  ← the safety net
5. terraform apply    → create/update/delete resources via provider APIs
6. State updated (stored remotely with locking)
```

### Key concepts

```
Provider   → plugin talking to an API (aws, google, azurerm, kubernetes, cloudflare, github)
Resource   → a managed object: aws_db_instance, aws_s3_bucket, aws_security_group
Data source→ read existing info: data "aws_ami", data "aws_vpc"
Variable / Output → inputs & exported values
Module     → reusable package of resources (e.g. "service" module: ECS service + ALB rule + alarms)
State      → JSON mapping code ↔ real resource IDs + attributes (terraform.tfstate)
             MUST be remote (S3 + DynamoDB lock / Terraform Cloud), encrypted, access-controlled —
             it can contain secrets!
Workspace / per-env dirs → separate state per environment (dev / staging / prod)
Dependency graph → Terraform infers order from references (subnet → instance)
Plan / Apply / Destroy, import (bring existing resources under management), moved/removed blocks
```

### Declarative vs imperative
```
Declarative (Terraform, CloudFormation): describe the END STATE; tool computes the steps
Imperative (scripts, aws cli): list the STEPS; you handle ordering, idempotency, drift
Terraform is idempotent: apply twice → second run says "No changes".
```

### Drift
```
Someone edits a security group in the console → reality ≠ code
terraform plan shows the diff → either revert (apply) or update code
Schedule drift detection (CI nightly `terraform plan -detailed-exitcode`)
```

### Recommended structure
```
infra/
  modules/
    vpc/  ecs-service/  rds-postgres/  redis/  s3-bucket/
  envs/
    dev/      main.tf (uses modules, small sizes)   backend.tf (state key: dev)
    staging/  main.tf
    prod/     main.tf (multi-AZ, bigger instances)  backend.tf (state key: prod)
Same modules → environments differ only in variables → "staging is like prod".
```

### Best practices
```
✓ Remote state + locking; one state per env (and per large component) → smaller blast radius
✓ PR-based workflow: plan in CI, human review, apply from CI (Atlantis, Terraform Cloud, GitHub Actions)
✓ No secrets in code: reference Secrets Manager/SSM; mark outputs sensitive
✓ Pin provider & module versions; use `prevent_destroy` lifecycle on databases/buckets
✓ Tag everything (env, team, cost-center); policy-as-code checks (tflint, Checkov, tfsec, OPA)
✓ Avoid manual console changes in prod (read-only console access)
✓ Separate infra (Terraform) from app deploys (CI/CD pipeline updating image tags) — or GitOps for K8s
```

## 🟢 कैसे काम करता है? (Hindi)
1. HCL में लिखो कि क्या चाहिए (VPC, RDS, ECS service, S3 bucket); `terraform init` से provider डाउनलोड।
2. `terraform plan` दिखाता है क्या बनेगा (+), बदलेगा (~), हटेगा (−) — इसे Pull Request में review करो।
3. `terraform apply` cloud में बदलाव करता है; state फ़ाइल याद रखती है कि कौन-सा code किस असली resource से जुड़ा है।
4. State हमेशा remote (S3 + lock) और सुरक्षित रखो; हर environment की अलग state; modules से dev/staging/prod एक जैसे।
5. Console में हाथ से बदलाव मत करो (drift); secrets code में नहीं; DB पर `prevent_destroy`।

---

## 🟡 Real World Example

**Most modern companies (Uber, Airbnb, Slack, Swiggy, Razorpay)** — manage cloud infrastructure with Terraform or equivalents, with PR-based plans (often via Atlantis or Terraform Cloud) and policy checks for security (no public buckets, encryption required).

**Disaster recovery & new regions** — teams with IaC can stand up a full environment in a new region in hours by applying the same modules with different variables. Teams with ClickOps take weeks.

**Accidental destroys** — there are real incidents where a mis-scoped `terraform apply` or wrong workspace deleted production resources. This is why teams use separate states, `prevent_destroy`, plan review and least-privilege CI roles.

**Capital One / security compliance** — policy-as-code (e.g. Cloud Custodian, Checkov) and IaC scanning prevent misconfigurations like public S3 buckets before they reach production.

## 🟡 Real Example Hindi में
Uber, Airbnb, Swiggy, Razorpay जैसी कंपनियाँ Terraform से infrastructure संभालती हैं — हर बदलाव PR में plan के साथ review होता है।
IaC वाली टीमें नया region कुछ घंटों में बना लेती हैं, हाथ से बनाने वाली हफ़्तों में। कुछ कंपनियों में ग़लत workspace पर `apply` से production delete हो गया — इसलिए अलग state और `prevent_destroy` ज़रूरी है।

---

## 🟠 My Stack Example

### Remote state backend (S3 + DynamoDB lock)
```hcl
terraform {
  required_version = ">= 1.6"
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.60" } }
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "prod/core.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
provider "aws" {
  region = var.region
  default_tags { tags = { env = var.env, team = "platform", managed_by = "terraform" } }
}
```

### VPC + RDS Postgres (prod-grade defaults)
```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"
  name = "${var.env}-vpc"
  cidr = "10.0.0.0/16"
  azs             = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true
  one_nat_gateway_per_az = var.env == "prod"
}

resource "aws_db_instance" "orders" {
  identifier              = "${var.env}-orders"
  engine                  = "postgres"
  engine_version          = "16.4"
  instance_class          = var.env == "prod" ? "db.r7g.large" : "db.t4g.micro"
  allocated_storage       = 100
  storage_encrypted       = true
  multi_az                = var.env == "prod"
  backup_retention_period = var.env == "prod" ? 14 : 1
  db_subnet_group_name    = aws_db_subnet_group.private.name
  vpc_security_group_ids  = [aws_security_group.db.id]
  username                = "app"
  manage_master_user_password = true                  # password in Secrets Manager, not in code/state
  deletion_protection     = var.env == "prod"
  lifecycle { prevent_destroy = true }
}

resource "aws_security_group" "db" {
  name   = "${var.env}-db"
  vpc_id = module.vpc.vpc_id
  ingress { from_port = 5432 to_port = 5432 protocol = "tcp" security_groups = [aws_security_group.app.id] }  # only app
}
```

### Reusable "service" module (ECS Fargate + ALB rule + autoscaling)
```hcl
module "order_api" {
  source        = "../../modules/ecs-service"
  name          = "order-api"
  image         = "${var.ecr_repo}/order-api:${var.order_api_tag}"
  cpu           = 512
  memory        = 1024
  desired_count = 3
  min_count     = 3
  max_count     = 30
  path_pattern  = "/api/v1/orders*"
  env_vars      = { NODE_ENV = "production" }
  secrets       = { DATABASE_URL = aws_secretsmanager_secret.orders_db_url.arn }
}
```

### CI: plan on PR, apply on merge (GitHub Actions + OIDC, no static keys)
```yaml
name: terraform
on:
  pull_request: { paths: ["infra/**"] }
  push: { branches: [main], paths: ["infra/**"] }
permissions: { id-token: write, contents: read, pull-requests: write }
jobs:
  tf:
    runs-on: ubuntu-latest
    defaults: { run: { working-directory: infra/envs/prod } }
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: arn:aws:iam::123456789012:role/terraform-ci, aws-region: ap-south-1 }
      - uses: hashicorp/setup-terraform@v3
      - run: terraform init -input=false
      - run: terraform fmt -check && terraform validate
      - run: terraform plan -input=false -out=tfplan
      - if: github.event_name == 'push'
        run: terraform apply -input=false tfplan
# + checkov / tflint steps for security & style
```

### Small team on a VPS?
```
Even for a single VPS: Terraform (provider: digitalocean / hetzner / aws lightsail) for the server,
firewall, DNS (Cloudflare provider), and S3 backup bucket; Ansible or cloud-init for packages/Docker.
→ rebuild your whole setup with one command after a disaster.
```

---

## ⚫ Interview Questions + Answers

**Q1: What is Infrastructure as Code and why use it?**
A1: Managing infrastructure through machine-readable, version-controlled definition files instead of manual console changes. Benefits: reproducible, consistent environments (staging matches prod); code review and audit history for every change; automation in CI/CD; fast recovery and new-region builds; less drift and fewer human errors; and documentation of the system as code. It also enables policy-as-code security checks.

**Q2: What is Terraform state and why is it important?**
A2: A file mapping Terraform resources in code to real infrastructure IDs and their attributes. Terraform uses it to compute diffs (plan) and to know what it manages. It must be stored remotely (S3, GCS, Terraform Cloud) with locking (DynamoDB) to prevent concurrent corruption, encrypted and access-restricted (it can contain sensitive values), backed up, and split per environment or component to limit blast radius. Never edit it by hand except through `terraform state` commands.

**Q3: Declarative vs imperative IaC?**
A3: Declarative tools (Terraform, CloudFormation, Kubernetes manifests) describe the desired end state, and the tool figures out the operations, handles ordering via the dependency graph, and is idempotent. Imperative approaches (shell scripts with the cloud CLI, some SDK code) specify step-by-step commands, so you must handle ordering, retries, idempotency and drift yourself. Pulumi and CDK use general-purpose languages but still produce a declarative desired state.

**Q4: How do you safely manage Terraform changes in a team?**
A4: A Git PR workflow where CI runs fmt, validate, lint, security scans and `terraform plan`, posting the plan for review. Apply only from CI after approval, using a least-privilege role (OIDC, no long-lived keys). Use remote state with locking and separate states per environment, pin provider and module versions, use reusable modules, and protect critical resources (`prevent_destroy`, deletion protection). Run drift detection and restrict manual console write access in production.

**Q5: What is configuration drift and how do you handle it?**
A5: Drift is when real infrastructure diverges from the code and state, usually because of manual changes or other tools. Detect it with scheduled `terraform plan` (detailed exit codes) or drift-detection features. Resolve it by either re-applying the code to restore the declared state, or updating the code to adopt an intentional change (with `import` if needed). Prevent it by limiting console permissions and making IaC the only change path.

---

## 🔷 Trade-offs
✅ Advantages:
- Repeatable environments, reviewable history, automation, fast DR/new regions, security policy checks.

❌ Disadvantages:
- Learning curve; state management pitfalls; risk of large destructive applies.
- Provider/API quirks; long plans for big monoliths of state; secrets handling care.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IaC | Infrastructure defined in code | code में लिखा infrastructure |
| Terraform | Declarative multi-cloud IaC tool | IaC टूल |
| HCL | HashiCorp Configuration Language | Terraform की भाषा |
| Provider | Plugin for a cloud/API | cloud से बात करने वाला plugin |
| Resource / Module | Managed object / reusable group | चीज़ / दोबारा इस्तेमाल होने वाला समूह |
| State | Mapping of code to real resources | code और असली चीज़ों का नक्शा |
| Plan / Apply | Preview / execute changes | बदलाव देखना / लागू करना |
| Drift | Reality differs from code | असलियत और code में फ़र्क़ |
| Remote backend + lock | Shared state with locking | साझा state, ताले के साथ |
| Policy as code | Automated compliance rules | नियमों की अपने आप जाँच |

---

## ⚡ 3-Line Summary
**English:**
1. IaC defines infrastructure in version-controlled declarative code; Terraform plans and applies changes via providers.
2. Keep state remote, locked, encrypted and split per environment; reuse modules so dev/staging/prod/DR regions are consistent.
3. PR workflow with CI plan + review + apply, policy scans, pinned versions, prevent_destroy, and no manual console changes.

**Hindi:**
1. IaC = infrastructure को Git में रखे code से बनाना; Terraform plan करके apply करता है।
2. State remote, locked, encrypted, हर environment की अलग; modules से सब environments एक जैसे।
3. PR में plan + review + CI से apply, security जाँच, और console में हाथ से बदलाव नहीं।

---

## ➡️ Next Topic Suggestion
**110. Capacity Planning** — The last infrastructure topic: how many servers, DB size, Redis memory, Kafka partitions and bandwidth do you need for next quarter's growth or the next sale? Next: forecasting, load testing and headroom.
