# 180. Azure Subscriptions
# AWS: AWS Account (within AWS Organizations)
# Azure: Subscription (under Management Groups)
# हिंदी में: Azure subscription यानी billing और access की सीमा

---

## 🔵 Simple Definition
A subscription is the billing and access boundary where resources are created; it trusts one Entra tenant and has quotas.
हिंदी: Subscription वह इकाई है जिसके नाम पर bill बनता है और जिसमें resources बनते हैं।

---

## 🔴 Why it Exists
Separate billing, quotas and permissions for prod/dev/teams.
Management Groups let you apply policy and RBAC across many subscriptions.

---

## 🟢 How it Works
```
Entra Tenant
 +-- Management Group (root)
      +-- MG-Prod -> Sub-Prod -> Resource Groups -> resources
      +-- MG-NonProd -> Sub-Dev, Sub-Test
Azure Policy + RBAC inherit downward
```

---

## 💻 Code / Config Example
```bash
az account list -o table
az account set --subscription "Sub-Prod"

# list management groups
az account management-group list -o table

# assign RBAC at subscription scope
az role assignment create --assignee "<user-or-sp-id>" \
  --role "Reader" --scope "/subscriptions/<sub-id>"

# register a resource provider needed by a service
az provider register --namespace Microsoft.App
az provider show -n Microsoft.App --query registrationState -o tsv
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Boundary | Account | Subscription |
| Grouping | Organizations + OUs | Management Groups |
| Guardrails | SCPs | Azure Policy |
| Quotas | Service Quotas per account/region | Quotas per subscription/region (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting prod and dev in one subscription.
✅ Correct: Separate subscriptions for blast radius, billing and quotas.

❌ Mistake: Deployment fails "resource provider not registered".
✅ Correct: Register the provider (e.g. Microsoft.App) first.

---

## ⚫ Interview Q&A
Q1: [Easy] What does a subscription provide?
A1: Billing boundary, quota scope and access boundary.

Q2: [Medium] Subscription vs resource group?
A2: Subscription contains many resource groups; billing is at subscription level, lifecycle at group level.

Q3: [Hard] Design a landing zone.
A3: Management group hierarchy, separate platform/prod/non-prod subscriptions, Azure Policy and RBAC at MG, hub-spoke networking, centralized logging, budgets, IaC pipelines.

---

## ✅ Quick Checklist
□ Prod isolated
□ Budgets and policies set
□ Required providers registered

---

## ⚡ 1-Line Summary
Subscription is the billing and access boundary, like an AWS account | Subscription billing और access की सीमा है, AWS account जैसी।

## ➡️ Next: 181 (next topic in the series)
