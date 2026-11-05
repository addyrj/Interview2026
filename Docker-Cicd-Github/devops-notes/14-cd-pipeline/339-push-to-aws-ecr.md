# 339. Push to AWS ECR
# हिंदी में: AWS ECR पर Image Push करना

---

## 🔵 Simple Definition (English)
Amazon ECR (Elastic Container Registry) is AWS's private image registry. In GitHub Actions you authenticate with **OIDC** (assume an IAM role, no long-lived keys), log in via `aws-actions/amazon-ecr-login`, and push. ECS, EKS and EC2 then pull from ECR using their own IAM roles.

## 🔵 सरल परिभाषा (Hindi)
Amazon ECR (Elastic Container Registry) AWS की private image registry है। GitHub Actions में आप **OIDC** से IAM role assume करते हैं (कोई लंबे समय वाली keys नहीं), `amazon-ecr-login` से login करते हैं और push करते हैं। फिर ECS, EKS और EC2 अपने IAM roles से ECR से pull करते हैं।

---

## 🔴 Problem it Solves
Storing `AWS_ACCESS_KEY_ID/SECRET` in GitHub secrets means permanent keys that can leak and never expire. Public registries are outside your AWS account and policies. ECR keeps images inside your account with IAM, encryption, scanning and lifecycle rules; OIDC removes static keys completely.

## 🔴 यह क्यों बना? (Hindi)
GitHub secrets में `AWS_ACCESS_KEY_ID/SECRET` रखने का मतलब है स्थायी keys जो leak हो सकती हैं और कभी expire नहीं होतीं। Public registries आपके AWS account और policies के बाहर होती हैं। ECR images को आपके account में IAM, encryption, scanning और lifecycle rules के साथ रखता है; OIDC static keys पूरी तरह हटा देता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create ECR repo (aws ecr create-repository --repository-name api)
Step 2 → Create IAM OIDC provider for token.actions.githubusercontent.com
Step 3 → Create IAM role trusted only for repo:myorg/myrepo:ref:refs/heads/main
Step 4 → Attach ECR push policy to that role
Step 5 → Workflow: configure-aws-credentials (role-to-assume) → ecr-login
Step 6 → build-push-action pushes <acct>.dkr.ecr.<region>.amazonaws.com/api:sha
Step 7 → ECS/EC2 pull via task/instance role
```

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → ECR repo बनाओ (`aws ecr create-repository --repository-name api`)।
Step 2 → `token.actions.githubusercontent.com` के लिए IAM OIDC provider बनाओ।
Step 3 → ऐसा IAM role बनाओ जो सिर्फ `repo:myorg/myrepo:ref:refs/heads/main` पर भरोसा करे।
Step 4 → उस role पर ECR push policy लगाओ।
Step 5 → Workflow: `configure-aws-credentials` (role-to-assume), फिर `ecr-login`।
Step 6 → `build-push-action` image push करता है।
Step 7 → ECS/EC2 अपने task/instance role से pull करते हैं।

---

## 🟡 Real World Example
Zomato-like backend on ECS Fargate: each service has an ECR repo. A merge to `main` assumes role `gha-ecr-push`, pushes `orders:sha-ab12cd3`, and a lifecycle rule keeps only the last 20 images to save storage cost. ECR image scanning flags a critical CVE before deploy.

## 🟡 Real Example Hindi mein
Zomato जैसा backend ECS Fargate पर: हर service का अपना ECR repo। `main` पर merge होने से role `gha-ecr-push` assume होता है, `orders:sha-ab12cd3` push होता है और lifecycle rule सिर्फ आखिरी 20 images रखती है ताकि storage cost बचे। ECR scan deploy से पहले critical CVE पकड़ लेता है।

---

## 💻 Code / Config Example — Basic

```yaml
# .github/workflows/push-ecr.yml (basic)
name: push-ecr                         # workflow name
on:
  push:
    branches: [main]                   # main only
permissions:
  id-token: write                      # required to request the OIDC token
  contents: read                       # checkout
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      # get code
      - uses: aws-actions/configure-aws-credentials@v4   # OIDC login to AWS
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push  # example ARN
          aws-region: ap-south-1       # Mumbai region
      - id: ecr                        # login step, exposes registry URL
        uses: aws-actions/amazon-ecr-login@v2
      - name: Build and push
        run: |                         # plain docker commands
          IMAGE=${{ steps.ecr.outputs.registry }}/api:${{ github.sha }}  # full image name
          docker build -t "$IMAGE" .   # build
          docker push "$IMAGE"         # push
```

## 💻 Code / Config Example — Advanced

```yaml
# .github/workflows/push-ecr-advanced.yml
name: push-ecr-advanced
on:
  push:
    branches: [main]
permissions:
  id-token: write                      # OIDC
  contents: read
env:
  AWS_REGION: ap-south-1               # region of the registry
  ECR_REPOSITORY: api                  # repo name in ECR
jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}   # role ARN kept in repo variable
          aws-region: ${{ env.AWS_REGION }}
          role-session-name: gha-${{ github.run_id }}  # traceable in CloudTrail
      - id: ecr
        uses: aws-actions/amazon-ecr-login@v2
      - uses: docker/setup-buildx-action@v3
      - id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true                   # push to ECR
          tags: |                      # one tag per line
            ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
            ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Show scan findings       # basic scan result (needs scanOnPush)
        run: |
          aws ecr wait image-scan-complete --repository-name "$ECR_REPOSITORY" \
            --image-id imageTag=${{ github.sha }} --region "$AWS_REGION" || true
          aws ecr describe-image-scan-findings --repository-name "$ECR_REPOSITORY" \
            --image-id imageTag=${{ github.sha }} --region "$AWS_REGION" \
            --query 'imageScanFindings.findingSeverityCounts'
```

IAM trust policy for the role (copy-paste, replace account/repo):

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"}
    }
  }]
}
```

---

## 🟠 My Stack Integration
Create the repository once with scanning and immutable tags, and a lifecycle rule:

```bash
# create repo with scan-on-push and immutable tags (prevents overwriting a SHA)
aws ecr create-repository --repository-name api --region ap-south-1 \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability IMMUTABLE
# keep only the newest 20 images
aws ecr put-lifecycle-policy --repository-name api --region ap-south-1 --lifecycle-policy-text '{
 "rules":[{"rulePriority":1,"description":"keep last 20","selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":20},"action":{"type":"expire"}}]}'
```

Note: with `IMMUTABLE` you cannot push `latest` twice, so use only SHA tags in that case. An EC2/VPS outside AWS can pull with `aws ecr get-login-password | docker login --username AWS --password-stdin <registry>` (token valid 12 hours).

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Missing `id-token: write` so the OIDC step fails.
✅ Correct: Add it under `permissions`.

❌ Mistake 2: Trust policy with `sub: repo:myorg/*:*` (any repo/branch can assume).
✅ Correct: Restrict to exact repo and branch or environment.

❌ Mistake 3: Never expiring images, causing growing storage cost.
✅ Correct: Add a lifecycle policy.

❌ Mistake 4: Using IMMUTABLE tags and also pushing `latest` repeatedly.
✅ Correct: Choose one strategy (SHA-only immutable, or mutable with latest).

---

## 🧠 Tricky Interview Question
`docker login` to ECR worked locally this morning and fails in the deploy script in the evening. Why?

Answer: The ECR authorization token is valid only **12 hours**. Scripts must fetch a fresh token each run (`aws ecr get-login-password`), and long-running hosts (Kubernetes nodes outside EKS) need a refresh mechanism.

---

## ⚫ Interview Questions + Answers

Q1: Why OIDC instead of access keys?
A1: No long-lived secret; the role is assumed with a short-lived token tied to repo/branch claims.

Q2: What does the `sub` claim contain?
A2: `repo:<owner>/<repo>:ref:refs/heads/<branch>` (or `environment:<name>`), used in the trust policy condition.

Q3: Which IAM actions are needed to push?
A3: `ecr:GetAuthorizationToken` (on `*`) and, on the repo, `BatchCheckLayerAvailability`, `InitiateLayerUpload`, `UploadLayerPart`, `CompleteLayerUpload`, `PutImage`.

Q4: ECR vs Docker Hub?
A4: ECR: IAM, private by default, no pull limits within AWS, scanning, lifecycle. Docker Hub: public ecosystem, rate limits.

Q5: How does ECS pull from ECR?
A5: The task execution role has `AmazonECSTaskExecutionRolePolicy`, which includes the ECR pull permissions.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You run on ECS, EKS, EC2 or Lambda containers.
- Compliance needs images inside your AWS account.

❌ Avoid when:
- You run only on a non-AWS VPS (extra token refresh work).
- You need free public image distribution.

---

## 📊 Visual Diagram
```
GitHub Actions ──(OIDC JWT)──► AWS STS ──► temp credentials (role)
      │                                         │
      │ ecr-login + docker push                 ▼
      └──────────────────────────────►  ┌───────────────┐
                                        │ ECR repo: api │ scanOnPush
                                        └───────┬───────┘
                         pull via task role     │
                         ┌──────────────────────┼───────────────┐
                         ▼                      ▼               ▼
                       ECS                    EKS             EC2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ECR | AWS private registry | AWS की private registry |
| OIDC | Federated identity, no static keys | बिना keys के पहचान |
| IAM role | Set of permissions to assume | अस्थायी अधिकारों का set |
| STS | Issues temporary credentials | अस्थायी credentials देता है |
| Lifecycle policy | Auto-delete old images | पुरानी images हटाना |
| Immutable tag | Tag cannot be overwritten | tag बदला नहीं जा सकता |

---

## ⚡ 3-Line Summary
English: Use OIDC to assume an IAM role, log in to ECR, push SHA tags. Lock the trust policy to repo and branch. Add scanning and lifecycle rules.
Hindi: OIDC से IAM role assume करो, ECR में login करके SHA tag push करो। Trust policy को repo और branch तक सीमित रखो। Scanning और lifecycle rules लगाओ।

---

## ➡️ Next Topic
**340. Deploy to VPS (SSH)** - now that the image is in a registry, ship it to your own server over SSH.
