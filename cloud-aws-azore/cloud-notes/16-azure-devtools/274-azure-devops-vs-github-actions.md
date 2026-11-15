---

# 274. AZURE DEVOPS VS GITHUB ACTIONS
# AWS: CodePipeline vs GitHub Actions (OIDC to AWS)
# Azure: Azure Pipelines vs GitHub Actions (OIDC to Azure)
# हिंदी में: एज़्योर डेवऑप्स बनाम गिटहब एक्शन्स

---

## 🔵 Simple Definition (2 lines)
Both run YAML CI/CD. Azure DevOps is an all-in-one suite (Boards, Repos, Pipelines); GitHub Actions is CI/CD built into GitHub with a huge marketplace.
हिंदी: दोनों CI/CD हैं; Azure DevOps पूरा सूट है, GitHub Actions GitHub के अंदर बना है और आपके स्टैक में आम है।

---

## 🔴 Why it Exists (2 lines)
Teams must choose a delivery platform. Knowing differences prevents painful migrations.

---

## 🟢 How it Works
```
Azure Pipelines : stages > jobs > steps | environments + approvals
                  service connection | agent pools
GitHub Actions  : workflow > jobs > steps | environments + reviewers
                  secrets/OIDC | runners
Both: deploy to Azure with federated identity (no stored secret)
```

---

## 💻 Code / Config Example
```yaml
# GitHub Actions equivalent: build + deploy to Azure App Service with OIDC
name: deploy
on:
  push:
    branches: [main]
permissions:
  id-token: write      # needed for OIDC
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci && npm test && npm run build
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - uses: azure/webapps-deploy@v3
        with:
          app-name: api-prod
          package: .
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | Azure Pipelines | GitHub Actions |
|---------|-----------------|----------------|
| Source | Azure Repos or GitHub | GitHub |
| Work tracking | Boards native | GitHub Issues/Projects |
| Reuse | Templates | Reusable workflows, marketplace actions |
| Release gates | Environments, approvals, checks | Environments, required reviewers |
| Pricing | Parallel-job based | Minutes based; free for public repos (approximate — check current docs) |
(AWS side: CodePipeline is rarely chosen over either; both can federate into AWS via OIDC.)

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing by hype.
✅ Correct: Choose by where the code lives, compliance needs and existing Boards usage.

❌ Mistake: Storing Azure client secrets in repo secrets.
✅ Correct: Federated credentials (OIDC) on the Entra app.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Key difference?
A1: DevOps is a full suite; Actions is CI/CD inside GitHub.

Q2: [Medium] When pick Azure DevOps?
A2: Need Boards/Test Plans, strict enterprise permissions, on-prem Server, or existing org investments.

Q3: [Hard] Migrate Pipelines to Actions?
A3: Map stages to jobs with `needs`, service connections to OIDC, variable groups to environment secrets, templates to reusable workflows; GitHub Actions Importer can help.

---

## ✅ Quick Checklist
□ Decide per org, not per repo
□ OIDC for cloud auth
□ Approval gates on prod

---

## ⚡ 1-Line Summary
Pick Actions for GitHub-centric teams, DevOps for full-suite needs | GitHub में कोड हो तो Actions, पूरा सूट चाहिए तो Azure DevOps।

## ➡️ Next: ARM Templates

---
