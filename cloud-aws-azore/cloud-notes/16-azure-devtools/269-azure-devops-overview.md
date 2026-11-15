---

# 269. AZURE DEVOPS OVERVIEW
# AWS: CodeCommit + CodeBuild + CodePipeline + CodeArtifact (CodeCommit closed to new customers in 2024)
# Azure: Azure DevOps Services
# हिंदी में: एज़्योर डेवऑप्स ओवरव्यू

---

## 🔵 Simple Definition (2 lines)
Azure DevOps is an integrated SaaS suite: Boards, Repos, Pipelines, Test Plans and Artifacts, organised as Organization > Project.
हिंदी: Azure DevOps एक ही जगह कोड, CI/CD, टास्क बोर्ड और पैकेज मैनेज करने वाला प्लेटफ़ॉर्म है।

---

## 🔴 Why it Exists (2 lines)
Teams stitched together separate tools for planning, code and delivery. Azure DevOps ties work items to commits to deployments.

---

## 🟢 How it Works
```
Organization (dev.azure.com/acme)
  └─ Project: shop-api
       ├─ Boards     work items, sprints, Kanban
       ├─ Repos      Git, PRs, branch policies
       ├─ Pipelines  YAML CI/CD, agents, environments
       ├─ Test Plans manual/exploratory testing
       └─ Artifacts  npm / PyPI / NuGet / Maven feeds
Auth: Entra ID; Service connections -> Azure (workload identity federation)
```

---

## 💻 Code / Config Example
```bash
# Azure DevOps CLI extension
az extension add --name azure-devops
az devops configure --defaults organization=https://dev.azure.com/acme project=shop-api

az devops project list -o table
az repos list -o table
az pipelines list -o table
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Planning | (none native; Jira etc.) | Boards |
| Git hosting | CodeCommit (no new customers) | Repos |
| CI/CD | CodeBuild/CodePipeline | Pipelines |
| Packages | CodeArtifact | Artifacts |
| Pricing | Per pipeline/build minute | Free for first 5 users; paid parallel jobs (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: One giant project for all teams.
✅ Correct: Project per product/team boundary, shared templates in a central repo.

❌ Mistake: Personal access tokens in pipelines.
✅ Correct: Use service connections with workload identity federation.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Name the five Azure DevOps services.
A1: Boards, Repos, Pipelines, Test Plans, Artifacts.

Q2: [Medium] Azure DevOps Services vs Server?
A2: Services is cloud SaaS (Microsoft-run); Server is self-hosted on-prem.

Q3: [Hard] How is a pipeline authorised to deploy to Azure securely?
A3: A service connection backed by an Entra app with federated credentials (no secret), RBAC scoped to the target resource group, environments with approvals and checks.

---

## ✅ Quick Checklist
□ Projects mapped to teams
□ Branch policies on main
□ Service connections via federation

---

## ⚡ 1-Line Summary
Azure DevOps = planning, code, CI/CD, packages in one suite | Azure DevOps = प्लानिंग से डिप्लॉय तक सब एक जगह।

## ➡️ Next: Azure Repos (Git)

---
