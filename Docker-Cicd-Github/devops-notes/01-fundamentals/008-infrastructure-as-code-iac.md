# 8. Infrastructure as Code (IaC)
# हिंदी में: Infrastructure as Code (कोड के रूप में infrastructure)

---

## 🔵 Simple Definition (English)
**Infrastructure as Code (IaC)** means describing servers, networks, databases and permissions in text files (code), storing them in Git, and letting a tool (Terraform, CloudFormation, Ansible) create and update them automatically. Instead of clicking in the AWS console, you run a command and get the same result every time.

## 🔵 सरल परिभाषा (Hindi)
**Infrastructure as Code (IaC)** का मतलब है servers, networks, databases और permissions को text files (code) में लिखना, Git में रखना, और किसी tool (Terraform, CloudFormation, Ansible) से उन्हें अपने आप बनाना और update करना। AWS console में click करने की जगह आप एक command चलाते हैं और हर बार वही नतीजा मिलता है।

---

## 🔴 Problem it Solves
- **Click-ops:** someone creates a server by clicking; nobody remembers which settings were used.
- **Snowflake servers:** each server is slightly different, so bugs are unreproducible.
- **Slow recovery:** if a region fails you need days to rebuild by hand.
- **No review or history:** a risky firewall change has no pull request and no audit trail.
- **Environment mismatch:** staging does not match production.

## 🔴 यह क्यों बना? (Hindi)
- **Click-ops:** कोई click करके server बनाता है; किसी को याद नहीं कौन सी settings थीं।
- **Snowflake servers:** हर server थोड़ा अलग, इसलिए bugs दोहराए नहीं जा सकते।
- **धीमी recovery:** region fail हो तो हाथ से दोबारा बनाने में दिन लगते हैं।
- **कोई review या history नहीं:** risky firewall change का न PR, न audit trail।
- **Environment mismatch:** staging production जैसा नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 -> Write: describe desired infrastructure in files (main.tf)
Step 2 -> Version: commit to Git, open a Pull Request, teammates review
Step 3 -> Plan: tool compares desired state vs real state and shows the diff (terraform plan)
Step 4 -> Apply: tool creates/changes/deletes resources to match (terraform apply)
Step 5 -> State: tool records what it created (terraform.tfstate, stored remotely e.g. S3)
Step 6 -> Repeat: change the file, plan, apply (idempotent: same input, same result)
Step 7 -> Destroy: remove everything cleanly when not needed (terraform destroy)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 -> Write: चाहा हुआ infrastructure files (main.tf) में लिखो
Step 2 -> Version: Git में commit, Pull Request, teammates review करें
Step 3 -> Plan: tool चाहे हुए और असली state की तुलना करके diff दिखाता है (terraform plan)
Step 4 -> Apply: tool resources बनाता/बदलता/हटाता है (terraform apply)
Step 5 -> State: tool याद रखता है क्या बनाया (terraform.tfstate, S3 जैसी जगह remote)
Step 6 -> Repeat: file बदलो, plan, apply (idempotent: वही input, वही नतीजा)
Step 7 -> Destroy: ज़रूरत न हो तो साफ़ तरीके से सब हटाओ (terraform destroy)
```

---

## 🟡 Real World Example
**Swiggy launching in a new city region.** With IaC, the team copies a module, changes `region = "ap-south-2"` and `terraform apply` creates VPC, subnets, load balancer, database and autoscaling group in 15 minutes, identical to existing regions. Without IaC it takes weeks of tickets and manual clicks, with mistakes.

**Your AWS:** one `main.tf` creates a security group, an EC2 instance and an Elastic IP for your app. If the instance is lost, `terraform apply` recreates it identically.

## 🟡 Real Example Hindi mein
**Swiggy का नए city region में launch।** IaC के साथ team module copy करती है, `region = "ap-south-2"` बदलती है और `terraform apply` 15 मिनट में VPC, subnets, load balancer, database और autoscaling group बना देता है, बिल्कुल मौजूदा regions जैसा। IaC के बिना हफ्तों के tickets और manual clicks, और गलतियाँ।

**आपका AWS:** एक `main.tf` आपके app के लिए security group, EC2 instance और Elastic IP बनाती है। Instance खो जाए तो `terraform apply` उसे वैसा ही दोबारा बना देता है।

---

## 💻 Code / Config Example — Basic
Terraform (HCL) for one EC2 instance plus a security group. (Terraform is not installed here, so this was not run; example AMI id and region need your values.)

```hcl
# main.tf - minimal AWS server for a Node.js / FastAPI app
terraform {                                  # settings for Terraform itself
  required_version = ">= 1.5"                # minimum Terraform version
  required_providers {                       # plugins to download
    aws = {
      source  = "hashicorp/aws"              # official AWS provider
      version = "~> 5.0"                     # any 5.x version
    }
  }
}

provider "aws" {                             # how to talk to AWS
  region = "ap-south-1"                      # Mumbai region
}

resource "aws_security_group" "web" {        # firewall rules
  name        = "web-sg"                     # name in AWS
  description = "Allow HTTP, HTTPS and SSH"  # shown in console

  ingress {                                  # inbound rule: HTTP
    from_port   = 80                         # start port
    to_port     = 80                         # end port
    protocol    = "tcp"                      # TCP only
    cidr_blocks = ["0.0.0.0/0"]              # from anywhere
  }
  ingress {                                  # inbound rule: HTTPS
    from_port   = 443                        # start port
    to_port     = 443                        # end port
    protocol    = "tcp"                      # TCP only
    cidr_blocks = ["0.0.0.0/0"]              # from anywhere
  }
  ingress {                                  # inbound rule: SSH
    from_port   = 22                         # start port
    to_port     = 22                         # end port
    protocol    = "tcp"                      # TCP only
    cidr_blocks = ["203.0.113.10/32"]        # ONLY your office/home IP (example), never 0.0.0.0/0
  }
  egress {                                   # outbound: allow everything
    from_port   = 0                          # all ports
    to_port     = 0                          # all ports
    protocol    = "-1"                       # all protocols
    cidr_blocks = ["0.0.0.0/0"]              # to anywhere
  }
}

resource "aws_instance" "app" {              # the server
  ami                    = "ami-0123456789abcdef0"   # example AMI id: replace with Ubuntu AMI for your region
  instance_type          = "t3.small"        # size
  vpc_security_group_ids = [aws_security_group.web.id]   # attach firewall
  tags = {
    Name = "app-server"                      # visible name
  }
}
```

## 💻 Code / Config Example — Advanced
Remote state in S3 with locking, variables, outputs, and a CI workflow that plans on PRs. (YAML parsed locally; HCL not validated.)

```hcl
# backend.tf - store state remotely so the team shares it and locks it
terraform {
  backend "s3" {                             # state lives in S3
    bucket         = "mycompany-tf-state"    # example bucket (create it first, enable versioning)
    key            = "prod/app.tfstate"      # path of this state file
    region         = "ap-south-1"            # bucket region
    dynamodb_table = "tf-locks"              # DynamoDB table prevents two applies at once
    encrypt        = true                    # encrypt state (it can contain secrets)
  }
}

# variables.tf - inputs, no hard-coded values
variable "instance_type" {
  type    = string                           # value type
  default = "t3.small"                       # default size
}

# outputs.tf - values shown after apply
output "public_ip" {
  value = aws_instance.app.public_ip         # print server IP for DNS / SSH
}
```

```yaml
# .github/workflows/terraform.yml
name: Terraform                                  # workflow name
on:
  pull_request:                                  # plan on PRs
    paths: ["infra/**"]                          # only when infra files change
permissions:
  id-token: write                                # OIDC to AWS (no stored keys)
  contents: read                                 # read code
  pull-requests: write                           # allow plan comments (if you add them)
jobs:
  plan:
    runs-on: ubuntu-latest                       # runner
    defaults:
      run:
        working-directory: infra                 # all run steps use this folder
    steps:
      - uses: actions/checkout@v4                # code
      - uses: hashicorp/setup-terraform@v3       # install Terraform
      - uses: aws-actions/configure-aws-credentials@v4   # temporary AWS credentials via OIDC
        with:
          role-to-assume: arn:aws:iam::123456789012:role/terraform-plan   # example role, replace
          aws-region: ap-south-1                 # region
      - run: terraform fmt -check                # style check
      - run: terraform init                      # download providers, connect backend
      - run: terraform validate                  # syntax check
      - run: terraform plan -no-color            # show the diff (apply happens after merge, with approval)
```

---

## 🟠 My Stack Integration
- **VPS:** use Ansible to harden a fresh VPS (create `deploy` user, disable root SSH, install Docker, set UFW firewall). **AWS:** use Terraform for EC2/ECS, RDS, S3, ECR, IAM.
- **Nginx:** keep `nginx.conf` in Git and deliver it with Ansible or your deploy pipeline.
- **Node/FastAPI/React:** app config via environment variables injected by IaC (Secrets Manager), not baked into images.

```yaml
# ansible-playbook.yml - configure a new VPS for your stack (idempotent)
- hosts: vps                                     # inventory group
  become: true                                   # use sudo
  tasks:
    - name: Install Docker and Nginx             # task label
      ansible.builtin.apt:                       # apt module
        name: [docker.io, nginx]                 # packages
        state: present                           # ensure installed
        update_cache: true                       # apt update first
    - name: Allow only needed ports              # firewall
      community.general.ufw:                     # UFW module
        rule: allow                              # allow rule
        port: "{{ item }}"                       # each port in the loop
      loop: ["22", "80", "443"]                  # SSH, HTTP, HTTPS
    - name: Enable firewall                      # turn UFW on
      community.general.ufw:
        state: enabled                           # enable
        policy: deny                             # default deny incoming
```
Security: state files can contain secrets: encrypt, restrict access, never commit `terraform.tfstate`. Run `tfsec`/`checkov` in CI. Use least-privilege IAM for the pipeline role. Never open SSH to the world.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Committing `terraform.tfstate` or `.tfvars` with secrets to Git.
✅ Correct: Use remote encrypted backend and `.gitignore` those files.

❌ Mistake 2: Changing resources by hand in the console (drift).
✅ Correct: Make all changes through code; use `terraform plan` to detect drift.

❌ Mistake 3: One giant state file for everything.
✅ Correct: Split by environment/component to limit blast radius.

❌ Mistake 4: Running `apply` without reading the plan.
✅ Correct: Review the plan in PR; protect production applies with approval.

---

## 🧠 Tricky Interview Question
**"Someone changed a security group in the AWS console. What happens at your next `terraform apply`?"**

Answer: Terraform compares code and state to real infrastructure during plan; it detects the manual change (drift) and plans to revert it to what the code says. This may remove a rule someone added for urgent reasons, so teams alert on drift and forbid console edits. If the manual change is correct, update the code (or `terraform import` for new resources) instead.

---

## ⚫ Interview Questions + Answers

Q1: Declarative vs imperative IaC?
A1: Declarative (Terraform, CloudFormation) says what end state you want; the tool works out steps. Imperative (shell scripts) lists the steps. Declarative is easier to keep consistent.

Q2: What is idempotency?
A2: Running the same operation many times gives the same result with no extra changes. Applying the same Terraform or Ansible code twice changes nothing the second time.

Q3: What is Terraform state and why remote?
A3: State maps your code to real resources. Remote storage (S3 + locking) lets the team share it, prevents concurrent applies, and avoids losing it with a laptop.

Q4: Terraform vs CloudFormation?
A4: Terraform is multi-cloud with HCL and a big provider ecosystem. CloudFormation is AWS-only, JSON/YAML, with no state file to manage (AWS holds it).

Q5: What is configuration drift?
A5: Real infrastructure differing from its code because of manual edits. Detect it with plan and prevent it by banning manual changes.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You manage more than a couple of servers or environments.
- You need repeatable, reviewable, recoverable infrastructure.

❌ Avoid when:
- A single throwaway test server (IaC is overhead).
- The team cannot yet maintain it (start with a small module and grow).

---

## 📊 Visual Diagram
```
  main.tf (Git)         terraform plan            terraform apply
 +-------------+      +------------------+      +------------------+
 | desired     | ---> | diff: desired vs | ---> | create / change  |
 | state       |      | real (state)     |      | / delete         |
 +-------------+      +--------+---------+      +---------+--------+
        ^                      |                          |
        |                 remote state (S3 + lock)        v
   PR review                                        AWS: EC2, RDS, S3
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| IaC | Infrastructure defined in code | Code में infrastructure |
| State | Record of resources a tool manages | Tool द्वारा संभाले resources का record |
| Drift | Real infra differs from code | असली infra का code से अलग होना |
| Idempotent | Same result if repeated | दोहराने पर भी वही नतीजा |
| Provider | Plugin to talk to a platform | किसी platform से बात करने वाला plugin |
| Module | Reusable group of resources | Resources का दोबारा इस्तेमाल होने वाला समूह |

---

## ⚡ 3-Line Summary
English: IaC describes infrastructure in files kept in Git and applied by tools.
It gives repeatability, review, history and fast recovery.
Protect state, avoid console changes, review every plan.

Hindi: IaC infrastructure को files में लिखता है जो Git में रहती हैं और tools से apply होती हैं।
इससे दोहराव, review, history और तेज़ recovery मिलती है।
State सुरक्षित रखें, console से बदलाव न करें, हर plan review करें।

---

## ➡️ Next Topic
**9. Shift Left Testing** — if infrastructure and code are both in Git, tests can run earlier too.
