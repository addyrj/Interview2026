# 342. Deploy to AWS EC2
# हिंदी में: AWS EC2 पर Deploy करना

---

## 🔵 Simple Definition (English)
EC2 is AWS's virtual server. To deploy there from GitHub Actions you either SSH in (like a VPS) or, better, use **AWS Systems Manager (SSM) Run Command**, which runs your deploy script on the instance through the AWS API with IAM auth, no open port 22 and no SSH keys.

## 🔵 सरल परिभाषा (Hindi)
EC2 AWS का virtual server है। GitHub Actions से वहाँ deploy करने के लिए आप SSH कर सकते हैं (VPS की तरह) या बेहतर, **AWS Systems Manager (SSM) Run Command** इस्तेमाल करें, जो AWS API से IAM auth के साथ instance पर script चलाता है; port 22 खोलने या SSH keys की ज़रूरत नहीं।

---

## 🔴 Problem it Solves
SSH to EC2 needs port 22 open to GitHub's huge IP ranges (or to the internet), plus key management. A leaked key means server access. SSM removes inbound access entirely; every command is audited in CloudTrail and controlled by IAM.

## 🔴 यह क्यों बना? (Hindi)
EC2 में SSH के लिए port 22 को GitHub की बड़ी IP ranges (या पूरे internet) के लिए खोलना पड़ता है और keys संभालनी पड़ती हैं। Key leak होने का मतलब server access। SSM inbound access पूरी तरह हटा देता है; हर command CloudTrail में audit होती है और IAM से control होती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → EC2 instance has an instance profile with AmazonSSMManagedInstanceCore
Step 2 → SSM Agent (preinstalled on Amazon Linux 2023/Ubuntu AMIs) registers it
Step 3 → GitHub OIDC role has ssm:SendCommand on that instance (by tag)
Step 4 → Workflow: build+push image to ECR/GHCR
Step 5 → aws ssm send-command --document-name AWS-RunShellScript
Step 6 → Instance pulls image, restarts container, reports status
Step 7 → Workflow waits (aws ssm wait command-executed) and checks output
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → EC2 instance पर `AmazonSSMManagedInstanceCore` वाला instance profile हो।
Step 2 → SSM Agent (Amazon Linux 2023/Ubuntu AMI में पहले से) instance register करता है।
Step 3 → GitHub OIDC role को tag के आधार पर उस instance पर `ssm:SendCommand` मिलता है।
Step 4 → Workflow image को ECR/GHCR पर build+push करता है।
Step 5 → `aws ssm send-command --document-name AWS-RunShellScript` चलता है।
Step 6 → Instance image pull करता है, container restart करता है और status लौटाता है।
Step 7 → Workflow `aws ssm wait command-executed` से इंतज़ार करके output जाँचता है।

---

## 🟡 Real World Example
A fintech runs its Node.js API on two EC2 instances in an Auto Scaling group behind an ALB, tagged `Role=api`. The pipeline targets instances by tag, so new instances are covered automatically. Security group has no inbound 22 at all; auditors can see every deploy command in CloudTrail.

## 🟡 Real Example Hindi mein
एक fintech का Node.js API ALB के पीछे Auto Scaling group की दो EC2 instances पर चलता है, tag `Role=api`। Pipeline tag से instances चुनता है, इसलिए नई instances अपने आप cover होती हैं। Security group में inbound 22 है ही नहीं; auditors CloudTrail में हर deploy command देख सकते हैं।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/deploy-ec2-ssh.yml (basic: SSH to EC2)
name: deploy-ec2-ssh                   # workflow name
on:
  workflow_dispatch:                   # manual trigger
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Prepare key              # write key and trust host
        run: |
          install -m 700 -d ~/.ssh                           # ssh dir
          echo "${{ secrets.EC2_SSH_KEY }}" > ~/.ssh/key.pem # private key
          chmod 600 ~/.ssh/key.pem                           # required perms
          echo "${{ secrets.EC2_KNOWN_HOSTS }}" > ~/.ssh/known_hosts
      - name: Run deploy               # ec2-user is default on Amazon Linux
        run: |
          ssh -i ~/.ssh/key.pem ec2-user@${{ secrets.EC2_HOST }} \
            "docker pull ghcr.io/myorg/api:latest && docker rm -f api; \
             docker run -d --name api -p 3000:3000 --env-file /etc/api.env ghcr.io/myorg/api:latest"
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/deploy-ec2-ssm.yml (OIDC + SSM, no SSH)
name: deploy-ec2-ssm
on:
  push:
    branches: [main]
permissions:
  id-token: write                      # OIDC
  contents: read
env:
  AWS_REGION: ap-south-1
  ECR_REPO: 123456789012.dkr.ecr.ap-south-1.amazonaws.com/api   # example account
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_DEPLOY_ROLE }}   # role with ssm:SendCommand
          aws-region: ${{ env.AWS_REGION }}
      - name: Send deploy command to instances tagged Role=api
        id: send
        run: |
          REG="${ECR_REPO%%/*}"                          # registry host part
          IMG="${ECR_REPO}:${GITHUB_SHA}"                # full image URI
          # build the parameters JSON safely with jq (avoids quoting bugs)
          jq -n --arg reg "$REG" --arg img "$IMG" '{commands: [
            "set -e",
            ("aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin " + $reg),
            ("docker pull " + $img),
            "docker rm -f api || true",
            ("docker run -d --name api --restart unless-stopped -p 3000:3000 --env-file /etc/api.env " + $img),
            "sleep 8",
            "curl -fsS http://127.0.0.1:3000/health"
          ]}' > params.json
          CMD_ID=$(aws ssm send-command \
            --document-name "AWS-RunShellScript" \
            --targets "Key=tag:Role,Values=api" \
            --comment "deploy ${GITHUB_SHA::7}" \
            --timeout-seconds 600 \
            --parameters file://params.json \
            --query "Command.CommandId" --output text)
          echo "cmd_id=$CMD_ID" >> "$GITHUB_OUTPUT"      # save for the next step
      - name: Wait for result          # wait for each targeted instance
        run: |
          for ID in $(aws ssm list-command-invocations --command-id "${{ steps.send.outputs.cmd_id }}" \
                       --query "CommandInvocations[].InstanceId" --output text); do
            aws ssm wait command-executed --command-id "${{ steps.send.outputs.cmd_id }}" --instance-id "$ID"
          done
          aws ssm list-command-invocations --command-id "${{ steps.send.outputs.cmd_id }}" \
            --query "CommandInvocations[].[InstanceId,Status]" --output table
```

The CLI flags above follow the AWS CLI `ssm` reference (not run against a real account here). `--parameters file://...` avoids shell-quoting bugs; for long scripts use an SSM Document instead.

---

## 🟠 My Stack Integration
Terraform-free minimum IAM pieces:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect":"Allow","Action":["ssm:SendCommand"],
     "Resource":["arn:aws:ssm:ap-south-1::document/AWS-RunShellScript",
                 "arn:aws:ec2:ap-south-1:123456789012:instance/*"],
     "Condition":{"StringEquals":{"ssm:resourceTag/Role":"api"}}},
    {"Effect":"Allow","Action":["ssm:GetCommandInvocation","ssm:ListCommandInvocations","ssm:DescribeInstanceInformation"],
     "Resource":"*"}
  ]
}
```

The instance profile also needs `AmazonSSMManagedInstanceCore` and ECR read (`AmazonEC2ContainerRegistryReadOnly`). Nginx on the instance (or ALB) fronts Node.js/FastAPI; React goes to S3+CloudFront or an Nginx container.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Opening port 22 to `0.0.0.0/0` for CI.
✅ Correct: Use SSM, or restrict to a bastion/VPN.

❌ Mistake 2: Instance not appearing as "Managed" in SSM.
✅ Correct: Attach the instance profile and ensure outbound HTTPS to SSM endpoints (NAT or VPC endpoints).

❌ Mistake 3: Hard-coding instance IDs.
✅ Correct: Target by tag or use CodeDeploy for fleets.

❌ Mistake 4: Putting secrets into the SSM command text (visible in history).
✅ Correct: Read them on the instance from SSM Parameter Store / Secrets Manager.

---

## 🧠 Tricky Interview Question
`send-command` returns success but the deployment failed. How?

Answer: `send-command` only means the command was **accepted**. The execution status is separate; you must wait (`aws ssm wait command-executed`) and inspect the invocation `Status` and output. Also with multiple targets, one instance can fail while others succeed.

---

## ⚫ Interview Questions + Answers

Q1: SSM vs SSH?
A1: SSM needs no inbound port or key, uses IAM and CloudTrail, and works on private subnets. SSH needs key management and an open port.

Q2: How do you do rolling deploy on many instances?
A2: SSM `--max-concurrency 1` and `--max-errors 0`, or CodeDeploy with an ALB.

Q3: How does EC2 pull a private ECR image?
A3: The instance role has ECR read; the script runs `aws ecr get-login-password | docker login`.

Q4: What is an instance profile?
A4: A container that attaches an IAM role to an EC2 instance, providing temporary credentials via metadata.

Q5: Why IMDSv2?
A5: It blocks SSRF-based credential theft by requiring a session token.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You already run on EC2 and want auditable deploys.
- Private instances with no public SSH.

❌ Avoid when:
- You want less operations work (use ECS Fargate).
- You need blue/green with automated rollback (use CodeDeploy).

---

## 📊 Visual Diagram
```
GitHub Actions ─OIDC─► IAM role ─► SSM API (SendCommand, tag Role=api)
                                         │ (HTTPS, outbound from instance)
                                         ▼
            ┌───────────── VPC (no inbound 22) ──────────────┐
            │  ALB ─► EC2 #1 [SSM agent → docker run api]    │
            │      └► EC2 #2 [SSM agent → docker run api]    │
            └─────────────────────┬──────────────────────────┘
                                  ▼
                         ECR (image pull via instance role)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EC2 | Virtual server on AWS | AWS का virtual server |
| SSM | Systems Manager, remote ops | बिना SSH remote चलाना |
| Instance profile | IAM role attached to EC2 | EC2 से जुड़ा IAM role |
| Run Command | Execute scripts remotely | दूर से script चलाना |
| ALB | Application Load Balancer | traffic बाँटने वाला |
| IMDSv2 | Secure metadata service | सुरक्षित metadata |

---

## ⚡ 3-Line Summary
English: Deploy to EC2 over SSH or, better, SSM Run Command with OIDC. No open port 22, IAM-controlled and audited. Always wait for and check the invocation status.
Hindi: EC2 पर SSH से या बेहतर SSM Run Command + OIDC से deploy करो। Port 22 बंद, IAM control और audit। Invocation status का इंतज़ार करके जाँचो।

---

## ➡️ Next Topic
**343. Deploy to AWS ECS** - let AWS run and heal containers for you, no servers to patch.
