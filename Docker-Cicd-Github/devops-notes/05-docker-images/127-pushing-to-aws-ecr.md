# 127. Pushing to AWS ECR
# हिंदी में: AWS ECR पर image push करना

---

## 🔵 Simple Definition (English)
Amazon ECR (Elastic Container Registry) is AWS's private, managed Docker/OCI registry. You authenticate with IAM (a 12-hour login token), push to `<account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>`, and ECS, EKS or EC2 pull from it using IAM roles.

## 🔵 सरल परिभाषा (Hindi)
Amazon ECR (Elastic Container Registry) AWS की private, managed Docker/OCI registry है। आप IAM से authenticate करते हैं (12 घंटे का login token), `<account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>` पर push करते हैं, और ECS, EKS या EC2 IAM roles से उसे pull करते हैं।

---

## 🔴 Problem it Solves
- Storing private images on Docker Hub means managing separate credentials and facing pull limits.
- Servers inside AWS need fast, secure pulls without public internet and without long-lived passwords.
- You want per-repo IAM policies, encryption, scan on push and automatic cleanup of old images.

## 🔴 यह क्यों बना? (Hindi)
- Private images Docker Hub पर रखने से अलग credentials और pull limits की झंझट होती है।
- AWS के अंदर के servers को public internet और लंबे समय वाले passwords के बिना तेज़, सुरक्षित pull चाहिए।
- आप हर repo पर IAM policy, encryption, push पर scan और पुरानी images की automatic सफाई चाहते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Create a repository: aws ecr create-repository --repository-name myapp/api
Step 2 → Authenticate: aws ecr get-login-password | docker login --username AWS --password-stdin <registry>
         (token valid 12 hours)
Step 3 → Tag: docker tag api:1.0.0 <account>.dkr.ecr.<region>.amazonaws.com/myapp/api:1.0.0
Step 4 → Push: docker push <that name>
Step 5 → Optional: scan on push, tag immutability, lifecycle policy (expire old images), KMS encryption
Step 6 → Pull: ECS task execution role / EC2 instance role with ecr:GetAuthorizationToken + BatchGetImage
Step 7 → In GitHub Actions: use OIDC role (no AWS keys stored) + aws-actions/amazon-ecr-login
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Repository बनाएँ: aws ecr create-repository --repository-name myapp/api
Step 2 → Authenticate: aws ecr get-login-password | docker login --username AWS --password-stdin <registry>
         (token 12 घंटे valid)
Step 3 → Tag: docker tag api:1.0.0 <account>.dkr.ecr.<region>.amazonaws.com/myapp/api:1.0.0
Step 4 → Push: docker push <वही नाम>
Step 5 → वैकल्पिक: push पर scan, tag immutability, lifecycle policy (पुरानी images expire), KMS encryption
Step 6 → Pull: ECS task execution role / EC2 instance role में ecr:GetAuthorizationToken + BatchGetImage
Step 7 → GitHub Actions में: OIDC role (AWS keys सहेजने की ज़रूरत नहीं) + aws-actions/amazon-ecr-login
```

---

## 🟡 Real World Example
An e-commerce team runs its FastAPI orders service on ECS Fargate. GitHub Actions assumes an IAM role through OIDC, pushes `orders-api:<sha>` to ECR, and updates the ECS service. ECR scan-on-push flags a critical CVE, a lifecycle rule keeps only the last 20 images to control cost, and tag immutability stops anyone from overwriting `1.4.0`.

## 🟡 Real Example Hindi mein
एक e-commerce team अपनी FastAPI orders service ECS Fargate पर चलाती है। GitHub Actions OIDC से IAM role assume करता है, `orders-api:<sha>` ECR पर push करता है और ECS service update करता है। ECR scan-on-push critical CVE पकड़ता है, lifecycle rule सिर्फ आखिरी 20 images रखती है ताकि खर्च कम रहे, और tag immutability `1.4.0` को overwrite होने से रोकती है।

---

## 💻 Code / Config Example — Basic
```bash
# Variables used below (replace with your values)
export AWS_REGION=ap-south-1                           # region of the registry (Mumbai here)
export ACCOUNT_ID=123456789012                         # your 12 digit AWS account id
export REGISTRY=${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com   # registry host

# 1. Create the repository once, with scanning and immutable tags
aws ecr create-repository \
  --repository-name myapp/api \
  --image-scanning-configuration scanOnPush=true \
  --image-tag-mutability IMMUTABLE \
  --region "$AWS_REGION"                               # fails if it already exists

# 2. Log Docker in to ECR (token lasts 12 hours)
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"    # password comes via stdin

# 3. Build, tag with the full ECR name, push
docker build -t myapp/api:1.0.0 .                      # local build
docker tag myapp/api:1.0.0 "$REGISTRY/myapp/api:1.0.0" # add the registry name
docker push "$REGISTRY/myapp/api:1.0.0"                # upload to ECR

# 4. Check what is stored and scan status
aws ecr describe-images --repository-name myapp/api --region "$AWS_REGION"    # list images
aws ecr describe-image-scan-findings --repository-name myapp/api --image-id imageTag=1.0.0 --region "$AWS_REGION"
```

## 💻 Code / Config Example — Advanced
```yaml
# .github/workflows/ecr.yml  (example versions: verify before use)
name: build-push-ecr                           # workflow name
on:
  push:
    branches: [main]                           # run on main
permissions:
  id-token: write                              # REQUIRED for OIDC to AWS
  contents: read                               # read code
env:
  AWS_REGION: ap-south-1                       # region
  ECR_REPOSITORY: myapp/api                    # repo created earlier
jobs:
  push:
    runs-on: ubuntu-latest                     # hosted runner
    steps:
      - uses: actions/checkout@v4              # get source
      - name: Assume AWS role via OIDC (no stored keys)
        uses: aws-actions/configure-aws-credentials@v4   # exchanges GitHub token for AWS creds
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-ecr-push   # your role ARN
          aws-region: ${{ env.AWS_REGION }}    # region
      - name: Log in to ECR
        id: ecr                                # exposes registry URL output
        uses: aws-actions/amazon-ecr-login@v2  # runs docker login for you
      - uses: docker/setup-buildx-action@v3    # buildx
      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: ./api                       # Dockerfile folder
          push: true                           # upload
          tags: ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}   # full ECR name with SHA
          cache-from: type=gha                 # reuse cache
          cache-to: type=gha,mode=max          # save cache
```

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep only the last 20 images",
      "selection": {
        "tagStatus": "any",
        "countType": "imageCountMoreThan",
        "countNumber": 20
      },
      "action": { "type": "expire" }
    }
  ]
}
```

```bash
# Apply the lifecycle policy above (saved as lifecycle.json)
aws ecr put-lifecycle-policy --repository-name myapp/api --lifecycle-policy-text file://lifecycle.json --region ap-south-1
```

---

## 🟠 My Stack Integration
- **Node.js / FastAPI / React:** one ECR repo per service (`myapp/api`, `myapp/web`).
- **VPS (non-AWS):** pulling from ECR needs a login every 12 hours; use a cron with `aws ecr get-login-password`, or a credential helper (`amazon-ecr-credential-helper`) with an IAM user limited to pull.
- **AWS EC2 / ECS:** attach an instance/task execution role with `AmazonEC2ContainerRegistryReadOnly`; no password handling.
- **Nginx:** a custom Nginx image (`myapp/nginx`) can be in ECR as well.
- **Security:** least privilege IAM, OIDC instead of access keys, immutable tags, scan on push, repository policy to restrict accounts.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PushPullMyAppApi",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload", "ecr:PutImage", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "arn:aws:ecr:ap-south-1:123456789012:repository/myapp/api"
    },
    {
      "Sid": "LoginToken",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    }
  ]
}
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Login token expired ("no basic auth credentials") in a long-running server or cron.
✅ Correct: Re-run `get-login-password` before each push/pull, or use the ECR credential helper.

❌ Mistake 2: Logging in to the wrong region or account.
✅ Correct: The registry host includes account and region; they must match the repo.

❌ Mistake 3: Storing `AWS_ACCESS_KEY_ID` secrets in GitHub for CI.
✅ Correct: Use OIDC with a role limited to this repo and branch.

❌ Mistake 4: Never cleaning old images; ECR charges per GB-month.
✅ Correct: Add a lifecycle policy.

❌ Mistake 5: Using `IMMUTABLE` tags and then pushing `latest` twice, which fails.
✅ Correct: With immutable tags only push unique tags (SHA/version).

---

## 🧠 Tricky Interview Question
Your ECS service in a private subnet cannot pull its image from ECR, although the task role has full ECR permissions. What is missing?

Answer: Pulls use the TASK EXECUTION role (not the task role) and need network access. A private subnet without a NAT gateway needs VPC endpoints: `com.amazonaws.<region>.ecr.api`, `ecr.dkr`, and an S3 gateway endpoint (layers are stored in S3), plus CloudWatch Logs endpoint if used. Check the execution role and endpoints/security groups.

---

## ⚫ Interview Questions + Answers

Q1: How does Docker authenticate to ECR?
A1: `aws ecr get-login-password | docker login --username AWS --password-stdin <registry>`; the token expires in 12 hours.

Q2: What is the registry URL format?
A2: `<account-id>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>`.

Q3: How do you stop people overwriting a release tag?
A3: Set the repository tag mutability to IMMUTABLE.

Q4: How do you control ECR cost?
A4: Lifecycle policies to expire untagged or old images, and avoid storing huge images.

Q5: Why prefer OIDC for GitHub Actions to ECR?
A5: No long-lived AWS keys in GitHub; the role trust policy can limit by repo and branch; credentials are short-lived.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Workloads run on ECS, EKS, EC2 or Lambda containers.
- You need IAM-based access, encryption and scan on push.

❌ Avoid when:
- Everything is on a small non-AWS VPS (GHCR/Hub is simpler).
- You need public distribution with no AWS account for users (use Hub/GHCR or ECR Public).

---

## 📊 Visual Diagram
```
 GitHub Actions --OIDC--> IAM Role (gha-ecr-push)
        |
        | docker push
        v
 +---------------------------------------------+
 | ECR  123456789012.dkr.ecr.ap-south-1...     |
 |   myapp/api:<sha>   scanOnPush, immutable   |
 |   lifecycle: keep last 20                   |
 +---------------------------------------------+
        |  pull (execution role / instance role)
        +--------------> ECS Fargate / EKS / EC2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ECR | AWS private container registry | AWS की private registry |
| IAM role | Identity with permissions | अनुमतियों वाली पहचान |
| OIDC | Keyless auth from GitHub to AWS | GitHub से AWS तक keyless auth |
| Lifecycle policy | Rule to expire images | पुरानी images हटाने का नियम |
| Immutable tags | Tags cannot be overwritten | tag overwrite नहीं हो सकते |
| Execution role | Role ECS uses to pull images | image pull करने वाला ECS role |

---

## ⚡ 3-Line Summary
English: ECR is AWS's private registry; log in with `aws ecr get-login-password` (12 hour token).
English: Push to `<account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>` and use OIDC in CI.
English: Turn on scan on push, immutable tags and lifecycle policies.
Hindi: ECR AWS की private registry है; `aws ecr get-login-password` से login करें (12 घंटे का token)।
Hindi: `<account>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>` पर push करें और CI में OIDC इस्तेमाल करें।
Hindi: Scan on push, immutable tags और lifecycle policies चालू रखें।

---

## ➡️ Next Topic
**128. Private Registry Setup** — run your own registry on a VPS when you do not want any cloud provider.
