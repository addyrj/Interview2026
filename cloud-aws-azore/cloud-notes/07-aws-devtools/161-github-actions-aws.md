# 161. GitHub Actions + AWS
# AWS: CodePipeline/CodeBuild (native) — GitHub Actions deploys to AWS
# Azure: Azure Pipelines / GitHub Actions + azure/login
# हिंदी में: GitHub Actions से AWS पर CI/CD

---

## 🔵 Simple Definition
GitHub Actions runs your build/test/deploy workflows on GitHub-hosted or self-hosted runners and calls AWS APIs using official actions.
हिंदी: GitHub Actions आपके कोड को build/test करके AWS पर अपने-आप deploy करता है।

---

## 🔴 Why it Exists
Code already lives in GitHub, so CI/CD next to it avoids running a separate Jenkins or CodePipeline setup.
Official `aws-actions/*` make login, ECR push and ECS deploy a few lines of YAML.

---

## 🟢 How it Works
```
git push -> GitHub event -> runner (ubuntu-latest)
   |-> checkout -> test -> docker build
   |-> assume AWS role (OIDC, no stored keys)
   |-> push image to ECR -> update ECS / S3 / Lambda
```

---

## 💻 Code / Config Example
```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
    branches: [main]
  pull_request:

permissions:
  id-token: write   # needed for OIDC
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gha-deploy
          aws-region: ap-south-1
      - run: aws sts get-caller-identity   # proves auth works
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Native CI/CD | CodeBuild + CodePipeline | Azure Pipelines (Azure DevOps) |
| GitHub login action | aws-actions/configure-aws-credentials | azure/login |
| Keyless auth | OIDC to IAM role | OIDC to Entra app federated credential |
| Pricing | Runner minutes billed by GitHub (approximate — check current docs) | Same for GitHub; Pipelines has its own free tier |

---

## ⚠️ Common Mistakes
❌ Mistake: Storing `AWS_ACCESS_KEY_ID` long-lived keys in repo secrets.
✅ Correct: Use OIDC and a role with least privilege (see 162).

❌ Mistake: Deploying from pull requests from forks.
✅ Correct: Gate deploy with `if: github.ref == 'refs/heads/main'` and environments with approvals.

---

## ⚫ Interview Q&A
Q1: [Easy] What triggers a workflow?
A1: Events in `on:` such as push, pull_request, schedule, workflow_dispatch.

Q2: [Medium] How do you share artifacts between jobs?
A2: `actions/upload-artifact` and `download-artifact`, or push to ECR/S3; jobs run on separate machines.

Q3: [Hard] How do you secure deploys to production?
A3: OIDC role with trust condition on repo and branch, GitHub Environments with required reviewers, pinned action versions (SHA), minimal `permissions:`.

---

## ✅ Quick Checklist
□ OIDC instead of static keys
□ `permissions:` set minimal
□ Deploy job only on main + environment approval

---

## ⚡ 1-Line Summary
GitHub Actions is CI/CD in your repo that deploys to AWS with a role | GitHub Actions repo में ही CI/CD चलाता है और role से AWS पर deploy करता है।

## ➡️ Next: 162. OIDC Auth for GitHub Actions
