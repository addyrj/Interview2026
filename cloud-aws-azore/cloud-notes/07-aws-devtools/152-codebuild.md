# 152. CodeBuild
# AWS: AWS CodeBuild
# Azure: Azure Pipelines (build agents) / GitHub Actions runners
# हिंदी में: कोडबिल्ड - मैनेज्ड बिल्ड सर्वर जो कोड को कंपाइल, टेस्ट और पैकेज करता है

---

## 🔵 Simple Definition
CodeBuild runs your build commands in a fresh container, configured by `buildspec.yml`, and bills per build minute. No build servers to maintain.
हिंदी: हर बिल्ड नए कंटेनर में चलता है; सर्वर संभालने की जरूरत नहीं, सिर्फ चले हुए मिनट का पैसा।

## 🔴 Why it Exists
Jenkins-style always-on build servers waste money and need patching. CodeBuild scales to many parallel builds on demand.

## 🟢 How it Works
```
Source (GitHub/S3/CodeCommit) --> CodeBuild container
   phases: install -> pre_build -> build -> post_build
   --> artifacts (S3), image push (ECR), logs (CloudWatch)
```

## 💻 Code / Config Example
```yaml
# buildspec.yml - Node.js app, build Docker image, push to ECR
version: 0.2
env:
  variables:
    REPO: 111122223333.dkr.ecr.ap-south-1.amazonaws.com/my-api
phases:
  install:
    runtime-versions:
      nodejs: 20
  pre_build:
    commands:
      - npm ci
      - npm test
      - aws ecr get-login-password | docker login --username AWS --password-stdin ${REPO%%/*}
  build:
    commands:
      - docker build -t $REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION .
  post_build:
    commands:
      - docker push $REPO:$CODEBUILD_RESOLVED_SOURCE_VERSION
cache:
  paths:
    - node_modules/**/*
```

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | CodeBuild | Azure Pipelines / GitHub Actions |
| Config | buildspec.yml | azure-pipelines.yml |
| Docker builds | Needs privileged mode | Hosted agents have Docker |
| Pricing | Per build minute by instance size (check current docs) | Parallel jobs / minutes (check current docs) |

## ⚠️ Common Mistakes
❌ Docker build fails: "cannot connect to daemon". ✅ Enable privileged mode on the project.
❌ Secrets in buildspec. ✅ Use `env.secrets-manager` or `parameter-store`.

## ⚫ Interview Q&A
Q1 [Easy]: What file configures CodeBuild? A1: buildspec.yml.
Q2 [Medium]: How to speed builds? A2: Cache dependencies (S3 or local cache), smaller images, Docker layer caching.
Q3 [Hard]: Build inside a VPC to reach private RDS? A3: Configure VPC, subnets and security groups on the project; ensure NAT or VPC endpoints for internet/ECR.

## ✅ Quick Checklist
□ Privileged mode for Docker
□ Secrets from Secrets Manager
□ Cache configured

## ⚡ 1-Line Summary
CodeBuild = pay-per-minute containerised builds | कोडबिल्ड मिनट के हिसाब से कंटेनर में बिल्ड चलाता है।

## ➡️ Next: CodeDeploy
