# 293. CI/CD Comparison
# AWS: CodeCommit/CodeBuild/CodeDeploy/CodePipeline (+ GitHub Actions)
# Azure: Azure DevOps (Repos/Pipelines/Artifacts) (+ GitHub Actions)
# हिंदी में: CI/CD सर्विसेज की तुलना

---

## 🔵 Simple Definition
Both clouds have native pipelines, but many teams use GitHub Actions to deploy to either.
हिंदी: दोनों क्लाउड के अपने पाइपलाइन टूल हैं, पर ज्यादातर टीमें GitHub Actions से डिप्लॉय करती हैं।

---

## 🔴 Why it Exists
Automating build, test, deploy removes manual error and speeds releases.

---

## 🟢 How it Works
```
push -> build/test -> docker image -> registry (ECR | ACR)
     -> deploy (ECS/Lambda | App Service/AKS) using OIDC, no stored keys
```

---

## 💻 Code / Config Example
```yaml
# GitHub Actions, keyless OIDC login (use one of the two jobs)
name: deploy
on: { push: { branches: [main] } }
permissions: { id-token: write, contents: read }
jobs:
  aws:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with: { role-to-assume: "arn:aws:iam::123456789012:role/gha-deploy", aws-region: ap-south-1 }
  azure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/login@v2
        with: { client-id: "${{ secrets.AZURE_CLIENT_ID }}", tenant-id: "${{ secrets.AZURE_TENANT_ID }}", subscription-id: "${{ secrets.AZURE_SUBSCRIPTION_ID }}" }
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Pipeline | CodePipeline | Azure Pipelines |
| Build | CodeBuild (buildspec.yml) | Pipelines agents (azure-pipelines.yml) |
| Deploy | CodeDeploy | Release/deploy tasks |
| Registry | ECR | ACR |
| Note | CodeCommit closed to new customers (verify in docs) | Azure Repos available |

---

## ⚠️ Common Mistakes
❌ Mistake: Long-lived cloud keys in GitHub secrets.
✅ Correct: OIDC federation with least-privilege role.

❌ Mistake: Deploying `latest` image.
✅ Correct: Immutable tags (git SHA) and rollback plan.

---

## ⚫ Interview Q&A
Q1: [Easy] CodeBuild equivalent?
A1: Azure Pipelines build jobs.

Q2: [Medium] Why GitHub Actions on both?
A2: One workflow style, huge marketplace, OIDC to both clouds.

Q3: [Hard] Safe production deploy?
A3: Staged environments with approvals, blue-green/canary, health checks, automated rollback.

---

## ✅ Quick Checklist
□ OIDC, no static keys
□ Immutable image tags
□ Approval gate for prod

---

## ⚡ 1-Line Summary
Native tools map 1:1, but GitHub Actions + OIDC works for both. | नेटिव टूल लगभग बराबर हैं, GitHub Actions + OIDC दोनों पर चलता है।

## ➡️ Next: 294. Serverless Comparison
