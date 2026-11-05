# 389. AWS EC2 Deploy with GitHub Actions
# हिंदी में: GitHub Actions से AWS EC2 पर Deploy

---

## 🔵 Simple Definition (English)
Deploying to **EC2** with GitHub Actions means the pipeline connects to your virtual server (over **SSH** or **AWS SSM**), pulls the new Docker image or code, and restarts the app. EC2 is just a Linux machine, so the deploy is the same as your VPS flow, with AWS adding IAM, security groups and ECR.

## 🔵 सरल परिभाषा (Hindi)
GitHub Actions से **EC2** पर deploy का मतलब है कि pipeline आपके virtual server से (**SSH** या **AWS SSM** के ज़रिए) connect होती है, नई Docker image या code खींचती है, और app restart करती है। EC2 बस एक Linux machine है, इसलिए deploy आपके VPS जैसा ही है; AWS बस IAM, security groups और ECR जोड़ता है।

---

## 🔴 Problem it Solves
Manual deploy means: SSH in, `git pull`, `docker compose up -d`, hope you did not forget a step. It is slow, not repeatable, differs per person, and nobody knows who deployed what. Also, opening port 22 to the whole internet so GitHub can connect is a security hole (GitHub runner IPs change).

A pipeline makes the deploy repeatable, logged, tied to a commit, and (with SSM) needs no open SSH port at all.

## 🔴 यह क्यों बना? (Hindi)
Manual deploy: SSH करो, `git pull`, `docker compose up -d`, और उम्मीद कि कोई step नहीं भूला। यह धीमा है, repeatable नहीं, हर व्यक्ति अलग करता है, और पता नहीं चलता किसने क्या deploy किया। साथ ही GitHub को connect करने के लिए पूरे internet पर port 22 खोलना security hole है (runner IPs बदलते रहते हैं)।

Pipeline से deploy repeatable, logged, commit से जुड़ा होता है, और SSM के साथ SSH port खोलने की ज़रूरत ही नहीं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Push to main triggers the workflow
Step 2 → Job runs tests, builds Docker image, pushes to ECR (tag = SHA)
Step 3 → Job authenticates to AWS (OIDC role, topic 394)
Step 4A (SSH way)  → job opens SSH to EC2 with a deploy key, runs deploy script
Step 4B (SSM way)  → job calls "aws ssm send-command"; the SSM agent on EC2 runs the script
Step 5 → Script: docker login ECR -> docker compose pull -> up -d
Step 6 → Job polls the health URL; fails the workflow if not healthy
Step 7 → Old image is kept (tag) so you can roll back by redeploying previous SHA
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → main पर push होते ही workflow चलता है
Step 2 → Job tests चलाता है, Docker image बनाता है, ECR में push करता है (tag = SHA)
Step 3 → Job AWS में authenticate होता है (OIDC role, topic 394)
Step 4A (SSH तरीका) → job deploy key से EC2 में SSH करके deploy script चलाता है
Step 4B (SSM तरीका) → job "aws ssm send-command" call करता है; EC2 का SSM agent script चलाता है
Step 5 → Script: ECR login -> docker compose pull -> up -d
Step 6 → Job health URL check करता है; healthy न हो तो workflow fail
Step 7 → पुरानी image tag के साथ रहती है, पिछला SHA दोबारा deploy करके rollback
```

---

## 🟡 Real World Example
A SaaS billing product runs its FastAPI backend on two EC2 `t3.small` instances behind an ALB. Earlier, one engineer did all deploys over SSH and was a single point of failure (he went on leave). Now merging to `main` runs GitHub Actions, which pushes the image to ECR and uses SSM `send-command` against instances tagged `Env=prod`. Port 22 is closed, every deploy shows in CloudTrail, and any developer can ship.

## 🟡 Real Example Hindi mein
एक SaaS billing product का FastAPI backend ALB के पीछे दो EC2 `t3.small` पर चलता है। पहले सारे deploy एक engineer SSH से करता था और वही single point of failure था (छुट्टी पर गया तो सब रुका)। अब `main` पर merge होते ही GitHub Actions image ECR में push करता है और `Env=prod` tag वाले instances पर SSM `send-command` चलाता है। Port 22 बंद है, हर deploy CloudTrail में दिखता है, और कोई भी developer ship कर सकता है।

---

## 💻 Code / Config Example — Basic

Simple SSH deploy (works like your VPS; good for a single server). Secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`.

```yaml
name: deploy-ec2-ssh                             # workflow name

on:
  push:
    branches: [main]                             # run on merge to main

jobs:
  deploy:
    runs-on: ubuntu-latest                       # GitHub runner
    steps:
      - uses: actions/checkout@v4                # fetch code (needed if you copy compose file)

      - name: Prepare SSH key                    # write the private key to disk
        run: |                                   # shell block
          mkdir -p ~/.ssh                        # ssh config folder
          echo "${{ secrets.EC2_SSH_KEY }}" > ~/.ssh/id_ed25519   # private key from secret
          chmod 600 ~/.ssh/id_ed25519            # ssh refuses keys with open permissions
          ssh-keyscan -H "${{ secrets.EC2_HOST }}" >> ~/.ssh/known_hosts   # trust host (better: pin the fingerprint)

      - name: Deploy over SSH                    # run commands on the server
        run: |
          ssh -i ~/.ssh/id_ed25519 "${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }}" '
            set -e                               # stop on first error
            cd /opt/app                          # app folder on the server
            git pull origin main                 # get the new code
            docker compose up -d --build         # rebuild and restart containers
            docker image prune -f                # remove dangling images to save disk
          '
```

## 💻 Code / Config Example — Advanced

Production way: image from ECR, deploy via **SSM** (no open port 22), health check, and rollback hint. Requires SSM Agent + an instance profile with `AmazonSSMManagedInstanceCore` on EC2.

```yaml
name: deploy-ec2-ssm                             # workflow name

on:
  push:
    branches: [main]                             # trigger on main

permissions:
  id-token: write                                # OIDC token for AWS login
  contents: read                                 # checkout permission

env:
  AWS_REGION: ap-south-1                         # region
  ECR_REPO: billing-api                          # ECR repository name

jobs:
  build:
    runs-on: ubuntu-latest                       # build job runner
    outputs:
      image: ${{ steps.push.outputs.image }}     # pass image URI to deploy job
    steps:
      - uses: actions/checkout@v4                # get code
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-ec2-deploy
          aws-region: ${{ env.AWS_REGION }}
      - id: login                                # ECR login step
        uses: aws-actions/amazon-ecr-login@v2
      - id: push                                 # build and push
        run: |
          IMAGE="${{ steps.login.outputs.registry }}/${ECR_REPO}:${{ github.sha }}"
          docker build -t "$IMAGE" .
          docker push "$IMAGE"
          echo "image=$IMAGE" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build                                 # wait for build
    runs-on: ubuntu-latest
    environment: production                      # protection rules / approvals
    steps:
      - uses: aws-actions/configure-aws-credentials@v4   # login again in this job
        with:
          role-to-assume: arn:aws:iam::111122223333:role/gha-ec2-deploy
          aws-region: ${{ env.AWS_REGION }}

      - name: Send deploy command via SSM        # run script on tagged instances
        id: ssm
        env:
          IMAGE: ${{ needs.build.outputs.image }}   # image URI from build job
        run: |
          CMD_ID=$(aws ssm send-command \
            --document-name "AWS-RunShellScript" \
            --targets "Key=tag:Env,Values=prod" \
            --parameters "commands=[\"aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${IMAGE%%/*}\",\"cd /opt/app\",\"echo IMAGE=${IMAGE} > .env\",\"docker compose pull\",\"docker compose up -d\"]" \
            --max-concurrency 1 --max-errors 0 \
            --query "Command.CommandId" --output text)
          echo "cmd=$CMD_ID" >> "$GITHUB_OUTPUT"

      - name: Wait for command to finish         # block until SSM reports result
        run: |
          sleep 10                               # let SSM register the invocations
          for ID in $(aws ssm list-command-invocations --command-id "${{ steps.ssm.outputs.cmd }}" --query "CommandInvocations[].InstanceId" --output text); do
            aws ssm wait command-executed --command-id "${{ steps.ssm.outputs.cmd }}" --instance-id "$ID"   # fails if command failed
          done

      - name: Smoke test                         # public health check
        run: curl --fail --retry 10 --retry-delay 5 --retry-connrefused https://api.example.com/health
```

`--max-concurrency 1 --max-errors 0` gives a rolling deploy across the instances: one at a time, stop on the first failure.

---

## 🟠 My Stack Integration
- **Node.js / FastAPI**: `/opt/app/docker-compose.yml` references `image: ${IMAGE}`; the pipeline only changes the `.env` value. Health endpoint `/health` for the smoke test.
- **React**: build in CI, upload to S3/CloudFront instead of serving from EC2 (topic 397).
- **Nginx**: runs on the same EC2 as a container or system service, proxying to the app container; reload (not restart) after config change: `docker compose exec nginx nginx -s reload`.
- **VPS to EC2**: your VPS flow (SSH + compose) maps 1:1 to the Basic example. Move to SSM when you add a second server or a compliance need.
- **AWS**: EC2 instance profile (role) pulls from ECR, so no AWS keys are stored on the server.

```yaml
# /opt/app/docker-compose.yml on the EC2 server (IMAGE comes from the .env written by the pipeline)
services:
  api:
    image: ${IMAGE}                              # exact SHA image deployed by the pipeline
    restart: unless-stopped                      # restart after crash or reboot
    env_file: .env.prod                          # app secrets live only on the server
    ports:
      - "127.0.0.1:3000:3000"                    # bind to localhost; Nginx is the public door
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]   # container-level health
      interval: 15s                              # check every 15 seconds
      retries: 3                                 # 3 failures = unhealthy
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Port 22 open to `0.0.0.0/0` so GitHub can reach it.
✅ Correct: Use SSM (no inbound port), or restrict to a bastion/VPN.

❌ Mistake 2: Long-lived `AWS_ACCESS_KEY_ID` in secrets.
✅ Correct: OIDC role (topic 394).

❌ Mistake 3: `ssh-keyscan` blindly in CI (man-in-the-middle risk).
✅ Correct: Store the host's known_hosts line/fingerprint as a secret and use that.

❌ Mistake 4: Deploying `latest`, then not knowing what is running.
✅ Correct: Deploy the SHA tag; record it in `.env` on the server.

❌ Mistake 5: Not checking health after deploy, so a crashed container looks like "success".
✅ Correct: Smoke-test and fail the job; consider auto-rollback script to the previous SHA.

---

## 🧠 Tricky Interview Question
Your SSH deploy step succeeded (exit code 0), but the site is down. How is that possible and how do you prevent it?

Answer: `docker compose up -d` returns 0 as soon as containers are *started*, not when the app is *healthy*. The Node process may crash at boot (missing env var, DB unreachable) a second later. Prevent it with a `healthcheck` plus `docker compose up -d --wait` (Compose v2.1+), and with a post-deploy `curl --fail` smoke test in the workflow.

---

## ⚫ Interview Questions + Answers

Q1: SSH vs SSM for deployment, what is the difference?
A1: SSH needs an inbound port 22 and key management. SSM uses an agent that calls out to AWS, authorised by IAM, so no inbound port, full audit in CloudTrail, and no key rotation.

Q2: How does EC2 pull images from ECR without credentials?
A2: Attach an IAM instance profile with ECR read permissions; `aws ecr get-login-password` then uses the instance role automatically.

Q3: How do you deploy to many EC2 instances without downtime?
A3: Put them behind an ALB, deploy one at a time (`--max-concurrency 1`), and rely on health checks to take each out of rotation during restart; or use CodeDeploy (topic 390).

Q4: How do you roll back?
A4: Re-run the deploy with the previous commit SHA (workflow_dispatch input) because every image is tagged by SHA and still in ECR.

Q5: Where do runtime secrets live?
A5: Not in the repo or image. Use `.env.prod` on the server, Secrets Manager or Parameter Store fetched at start (topics 395/396).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have a few servers and a simple compose-based app
- You are moving from VPS to AWS and want the same mental model
- Cost matters more than managed orchestration

❌ Avoid when:
- You have many services needing autoscaling and self-healing (use ECS/EKS)
- You need blue-green with traffic shifting out of the box (use CodeDeploy/ECS)

---

## 📊 Visual Diagram
```
 git push --> GitHub Actions
                 |  build + test
                 v
              +-------+        OIDC role         +-----------+
              |  ECR  | <----------------------- | AWS IAM   |
              +-------+                          +-----------+
                 ^                                     |
                 | docker pull                         | ssm send-command
        +--------+----------+                          v
        | EC2 (SSM agent)   | <------------------ AWS SSM service
        |  docker compose   |
        |  Nginx -> app     |
        +-------------------+
                 ^
              ALB :443  <--- users
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| EC2 | Virtual server in AWS | AWS का virtual server |
| SSM | Systems Manager, remote command service | बिना SSH remote command चलाने की service |
| Instance profile | IAM role attached to EC2 | EC2 से जुड़ा IAM role |
| ECR | AWS container registry | AWS की image registry |
| Security group | Instance firewall | Instance का firewall |
| Smoke test | Quick post-deploy check | deploy के बाद तेज़ जाँच |

---

## ⚡ 3-Line Summary
English: EC2 deploy = pipeline builds an image, pushes to ECR, and runs compose on the server.
English: Prefer SSM over SSH so no inbound port or long-lived key is needed.
English: Always health-check after deploy and deploy SHA tags for easy rollback.
Hindi: EC2 deploy में pipeline image बनाकर ECR में push करती है और server पर compose चलाती है।
Hindi: SSH की जगह SSM चुनें ताकि inbound port या लंबी उम्र वाली key न चाहिए।
Hindi: Deploy के बाद हमेशा health check करें और आसान rollback के लिए SHA tag deploy करें।

---

## ➡️ Next Topic
**390. AWS CodeDeploy Basics**: when you have a fleet of EC2 instances, hand-written SSM loops get fragile, so CodeDeploy gives managed rolling and blue-green with hooks.
