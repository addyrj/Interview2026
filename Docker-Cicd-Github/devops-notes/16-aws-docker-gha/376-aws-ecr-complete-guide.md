# 376. AWS ECR — Complete Guide
# हिंदी में: AWS ECR (Elastic Container Registry) की पूरी गाइड

---

## 🔵 Simple Definition (English)
Amazon ECR is AWS's private Docker image registry. You push your built images there, and ECS, EKS, EC2 or your VPS pull them. Access is controlled by IAM, images can be scanned for vulnerabilities, and old images can be cleaned automatically.

## 🔵 सरल परिभाषा (Hindi)
Amazon ECR, AWS का private Docker image registry है। आप अपनी build की हुई images वहाँ push करते हो, और ECS, EKS, EC2 या आपका VPS उन्हें pull करता है। Access IAM से control होता है, images की vulnerability scanning हो सकती है, और पुरानी images अपने आप साफ हो सकती हैं।

---

## 🔴 Problem it Solves
- Docker Hub free tier has pull rate limits; a busy CI/CD or autoscaling cluster can hit them and deployments fail.
- Public registries are not suitable for private company code.
- Self-hosting a registry means you manage storage, TLS, auth and backups.
- Without a registry near the compute, image pulls are slow and cross the public internet.

## 🔴 यह क्यों बना? (Hindi)
- Docker Hub free tier पर pull rate limit है; busy CI/CD या autoscaling cluster इसे hit कर सकता है और deploy fail हो जाता है।
- Public registry company के private code के लिए ठीक नहीं।
- खुद registry चलाने पर storage, TLS, auth और backup आपकी ज़िम्मेदारी।
- Compute के पास registry न हो तो image pull धीमा होता है और public internet से गुज़रता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a repository (one repo per app, e.g. myapp-api)
Step 2 → Login: aws ecr get-login-password | docker login  (token valid 12 hours)
Step 3 → docker build, then docker tag with the full ECR URL
Step 4 → docker push -> image layers stored in S3 behind ECR
Step 5 → ECS/EKS/EC2 pull using IAM role (task execution role)
Step 6 → Scan on push finds known CVEs; lifecycle policy deletes old images
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repository बनाओ (हर app के लिए एक, जैसे myapp-api)
Step 2 → Login: aws ecr get-login-password | docker login  (token 12 घंटे valid)
Step 3 → docker build, फिर पूरे ECR URL से docker tag
Step 4 → docker push -> image layers ECR के पीछे S3 में store
Step 5 → ECS/EKS/EC2, IAM role (task execution role) से pull करते हैं
Step 6 → Scan on push पुराने CVEs ढूँढता है; lifecycle policy पुरानी images हटाती है
```

---

## 🟡 Real World Example
A startup runs 6 microservices (auth, orders, payments, search, notifications, web-api). Each has its own ECR repo: `shop/orders`, `shop/payments`, and so on. GitHub Actions pushes `shop/orders:4f2a9c1d8e3b` on each merge. ECS Fargate in the same region pulls it over AWS's private network (with VPC endpoints, never touching the internet). When a critical CVE appears in the Node base image, ECR's enhanced scanning flags the affected images.

## 🟡 Real Example Hindi mein
एक startup के 6 microservices हैं (auth, orders, payments, search, notifications, web-api)। हर का अपना ECR repo: `shop/orders`, `shop/payments` आदि। हर merge पर GitHub Actions `shop/orders:4f2a9c1d8e3b` push करता है। उसी region में ECS Fargate इसे AWS के private network से pull करता है (VPC endpoints के साथ internet छूता ही नहीं)। Node base image में critical CVE आए तो ECR का enhanced scanning प्रभावित images को flag कर देता है।

---

## 💻 Code / Config Example — Basic

```bash
# create-ecr-basic.sh  - create a repo and push once (AWS CLI v2 + Docker needed)
set -euo pipefail                                   # stop on first error
REGION=ap-south-1                                   # Mumbai region
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)   # your 12-digit account id
REG="$ACCOUNT.dkr.ecr.$REGION.amazonaws.com"        # registry host name

aws ecr create-repository --repository-name myapp-api --region $REGION \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability IMMUTABLE                  # scan new images; forbid overwriting tags

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $REG # token is a 12 hour password

docker build -t myapp-api:v1 .                      # build local image
docker tag myapp-api:v1 $REG/myapp-api:v1           # add the ECR name to the same image
docker push $REG/myapp-api:v1                       # upload layers
```

## 💻 Code / Config Example — Advanced
Repository as code (CloudFormation) with encryption, immutability, scanning, lifecycle and a repository policy.

```yaml
# ecr-repo.yml  - CloudFormation template (deploy with: aws cloudformation deploy)
AWSTemplateFormatVersion: "2010-09-09"             # template format version
Description: Private ECR repo for myapp-api        # human readable note
Resources:
  ApiRepo:
    Type: AWS::ECR::Repository                      # the registry repo resource
    Properties:
      RepositoryName: myapp-api                     # name used in the image URL
      ImageTagMutability: IMMUTABLE                 # a tag can never be re-pointed
      ImageScanningConfiguration:
        ScanOnPush: true                            # basic CVE scan each push
      EncryptionConfiguration:
        EncryptionType: AES256                      # encrypted at rest (KMS also possible)
      LifecyclePolicy:
        LifecyclePolicyText: |                      # JSON rules, see topic 380
          {"rules":[{"rulePriority":1,"description":"keep last 20",
          "selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":20},
          "action":{"type":"expire"}}]}
      RepositoryPolicyText:                         # who may pull/push besides IAM identity policies
        Version: "2012-10-17"
        Statement:
          - Sid: AllowPullFromProdAccount           # name of the rule
            Effect: Allow
            Principal:
              AWS: arn:aws:iam::222222222222:root   # example second account (prod)
            Action:
              - ecr:GetDownloadUrlForLayer          # read layers
              - ecr:BatchGetImage                   # read manifests
              - ecr:BatchCheckLayerAvailability     # check layers exist
Outputs:
  RepoUri:
    Value: !GetAtt ApiRepo.RepositoryUri            # print full repo URL after deploy
```

---

## 🟠 My Stack Integration
Node.js / FastAPI images go to ECR; ECS (or your VPS) pulls them. React builds as static files to S3 and does not need ECR. On a plain VPS with Docker Compose you can also pull from ECR using the login command in a cron job (token expires every 12 hours).

```yaml
# docker-compose.prod.yml on VPS (after: aws ecr get-login-password | docker login ...)
services:
  api:
    image: 123456789012.dkr.ecr.ap-south-1.amazonaws.com/myapp-api:4f2a9c1d8e3b   # pinned immutable tag
    restart: unless-stopped                          # restart after crash or reboot
    env_file: .env                                   # secrets live outside the image
    ports:
      - "127.0.0.1:8000:8000"                        # only Nginx on the same host can reach it
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `latest` as the only tag.
✅ Correct: Tag with git SHA and make the repo IMMUTABLE.

❌ Mistake 2: Giving `ecr:*` on `*` to CI.
✅ Correct: Allow only push actions on the one repo ARN, plus `ecr:GetAuthorizationToken` (which needs `Resource: "*"`).

❌ Mistake 3: Never cleaning old images.
✅ Correct: Add a lifecycle policy; storage is billed per GB-month.

❌ Mistake 4: Logging in once on the VPS and forgetting the 12-hour expiry.
✅ Correct: Use a credential helper (`amazon-ecr-credential-helper`) or cron relogin.

---

## 🧠 Tricky Interview Question
`docker push` to ECR fails with "no basic auth credentials" even though `aws ecr get-login-password` worked a moment ago. Why?

Answer: The token is per registry and per region. You probably logged in to `ap-south-1` but pushed to a `us-east-1` URL (or the login used a different profile/account). Check that `--region`, the account id in the URL and the credentials match.

---

## ⚫ Interview Questions + Answers

Q1: ECR vs Docker Hub?
A1: ECR is private by default, IAM integrated, no pull rate limit for in-AWS pulls, near your compute. Docker Hub is bigger public ecosystem and easier to share.

Q2: How does ECS authenticate to ECR?
A2: The task execution role has `AmazonECSTaskExecutionRolePolicy` (includes ECR pull permissions). No docker login is needed in the task.

Q3: Basic vs enhanced scanning?
A3: Basic uses the open-source Clair-style database on push. Enhanced uses Amazon Inspector for continuous scanning of OS and language packages.

Q4: What is tag immutability?
A4: A pushed tag cannot be overwritten. Guarantees `:v1.2.3` always means the same bytes; rollback is reliable.

Q5: How to reduce ECR pull cost and latency in private subnets?
A5: Create VPC interface endpoints for `ecr.api`, `ecr.dkr` and a gateway endpoint for S3, so pulls avoid the NAT gateway.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Your compute is on AWS (ECS, EKS, Lambda containers, EC2)
- You need private images with IAM control and scanning

❌ Avoid when:
- You deploy mainly outside AWS and want one neutral registry (GHCR or Docker Hub may be simpler)
- Open-source images meant for everyone

---

## 📊 Visual Diagram
```
 Dev/CI --docker push--> [ ECR repo: myapp-api ] --pull--> ECS Fargate task
                           |  scan on push                   (task execution role)
                           |  lifecycle policy (cleanup)
                           |  replication (other regions)
                           v
                        layers stored in S3 (managed by AWS)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Registry | Account-level image host | Images का host |
| Repository | Folder of tags for one app | एक app की images का folder |
| Tag | Human label for an image version | Image version का नाम |
| Digest | sha256 fingerprint of the image | Image की unique पहचान |
| Lifecycle policy | Auto-delete rules | पुरानी images हटाने के नियम |
| Immutable tag | Tag that cannot be overwritten | जो tag बदला नहीं जा सकता |

---

## ⚡ 3-Line Summary
English: ECR is a private, IAM-secured Docker registry close to your AWS compute.
Use immutable SHA tags, scan on push and lifecycle rules for cleanup.
ECS pulls with its execution role; other hosts need a fresh 12-hour token.

Hindi: ECR एक private, IAM-secured Docker registry है जो AWS compute के पास रहती है।
Immutable SHA tags, scan on push और cleanup के लिए lifecycle rules इस्तेमाल करो।
ECS execution role से pull करता है; बाकी hosts को हर 12 घंटे नया token चाहिए।

---

## ➡️ Next Topic
377. Authenticate to ECR: login methods (CLI, GitHub Actions OIDC, credential helper) in detail.
