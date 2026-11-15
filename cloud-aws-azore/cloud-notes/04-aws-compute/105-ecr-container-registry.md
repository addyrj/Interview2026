# 105. ECR - Container Registry
# AWS: Amazon Elastic Container Registry (ECR)
# Azure: Azure Container Registry (ACR)
# हिंदी में: Docker images रखने की private AWS गोदाम

---

## 🔵 Simple Definition
ECR is a managed private Docker/OCI registry with IAM access control, image scanning and lifecycle policies.
ECR आपके Docker images का सुरक्षित private भंडार है।

---

## 🔴 Why it Exists
Docker Hub has rate limits and public exposure; you need a private registry integrated with IAM, in your region, with cleanup and scanning.

---

## 🟢 How it Works
```
aws ecr get-login-password | docker login  (token valid ~12h)
docker tag app <acct>.dkr.ecr.<region>.amazonaws.com/app:v1
docker push -> repository (immutable tags optional, scan on push)
Lifecycle policy deletes old untagged/aged images.
```

---

## 💻 Code / Config Example
```bash
REGION=ap-south-1; ACCT=123456789012
aws ecr create-repository --repository-name api \
  --image-tag-mutability IMMUTABLE \
  --image-scanning-configuration scanOnPush=true --region $REGION

aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCT.dkr.ecr.$REGION.amazonaws.com

docker build -t api:v1 .
docker tag api:v1 $ACCT.dkr.ecr.$REGION.amazonaws.com/api:v1
docker push $ACCT.dkr.ecr.$REGION.amazonaws.com/api:v1
```
```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 20 images",
      "selection": { "tagStatus": "any", "countType": "imageCountMoreThan", "countNumber": 20 },
      "action": { "type": "expire" }
    }
  ]
}
```
Apply with `aws ecr put-lifecycle-policy --repository-name api --lifecycle-policy-text file://policy.json`.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Registry | ECR | ACR |
| Scanning | Basic / Enhanced (Inspector) | Defender for Containers |
| Cleanup | Lifecycle policies | Retention / ACR tasks purge |
| Geo-replication | Cross-region replication rules | Premium SKU geo-replication |
| Pricing | Storage + data transfer (approximate - check current docs) | SKU daily fee + storage (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: No lifecycle policy; storage grows forever.
✅ Correct: Expire old images.

❌ Mistake: Mutable tags like `latest` in production.
✅ Correct: Immutable tags or deploy by digest.

---

## ⚫ Interview Q&A
Q1: [Easy] How do you authenticate Docker to ECR?
A1: `aws ecr get-login-password` piped to `docker login`.
Q2: [Medium] How do you stop deploying tampered tags?
A2: Immutable tag setting plus deploy by digest.
Q3: [Hard] Share images across accounts?
A3: Repository policy granting the other account pull actions, plus IAM permission in that account; or cross-account replication.

---

## ✅ Quick Checklist
□ Scan on push enabled
□ Lifecycle policy attached
□ Immutable tags

---

## ⚡ 1-Line Summary
ECR is IAM-secured private image storage | ECR IAM से सुरक्षित private image storage है।

## ➡️ Next: 106. EKS - Kubernetes Service
