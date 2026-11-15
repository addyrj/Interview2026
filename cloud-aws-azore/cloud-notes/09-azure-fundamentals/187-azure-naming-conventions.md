# 187. Azure Naming Conventions
# AWS: Naming/tagging standards (no enforced scheme)
# Azure: Cloud Adoption Framework naming convention
# हिंदी में: रिसोर्स के नाम का एक तय पैटर्न ताकि नाम देखकर ही पता चले क्या है

---

## 🔵 Simple Definition
A consistent pattern like `<type>-<workload>-<env>-<region>-<instance>` so resources are identifiable and sortable.
एक जैसा नाम-पैटर्न रखने से रिसोर्स पहचानना और ढूँढना आसान होता है।

---

## 🔴 Why it Exists
Many Azure names are immutable and some must be globally unique (storage, web apps). Bad names are painful to fix.

---

## 🟢 How it Works
```
rg-orders-prod-cin-001      resource group
app-orders-api-prod-cin     App Service
st ordersprodcin001         storage (3-24 chars, lowercase alnum only, global)
kv-orders-prod-cin          Key Vault (3-24 chars, global)
Common abbreviations (CAF): rg, vnet, snet, nsg, vm, app, func, aks, kv, st, sql
```
Rules differ per type (length, allowed chars, scope uniqueness) - check the resource-name rules doc.

---

## 💻 Code / Config Example
```bicep
param workload string = 'orders'
param env string = 'prod'
param loc string = 'cin' // Central India short code

var rgName = 'rg-${workload}-${env}-${loc}'
// storage: no hyphens, lowercase, max 24; uniqueString makes it globally unique
var stName = toLower('st${workload}${env}${take(uniqueString(resourceGroup().id), 6)}')
output storageName string = stName
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Official guide | Tagging best practices | CAF abbreviations list |
| Rename resources | Mostly via tags (Name) | Most cannot be renamed |
| Global uniqueness | S3 buckets | Storage, Web App, Key Vault, ACR |

---

## ⚠️ Common Mistakes
❌ Mistake: `myapp1` / `test2` names with no env or region.
✅ Correct: Follow one documented pattern.

❌ Mistake: Putting secrets or PII in names.
✅ Correct: Names appear in URLs and logs; keep them non-sensitive.

---

## ⚫ Interview Q&A
Q1: [Easy] Why use abbreviations?
A1: Short prefixes show resource type and keep names within length limits.

Q2: [Medium] Can you rename a resource group?
A2: No; you recreate or move resources.

Q3: [Hard] How do you enforce naming?
A3: Azure Policy with a `match`/`like` condition on `name` in deny mode, plus IaC modules that build names centrally.

---

## ✅ Quick Checklist
□ Pattern documented
□ Global-unique names use uniqueString
□ Policy enforces it

---

## ⚡ 1-Line Summary
Name by type-workload-env-region; most names are permanent. | नाम में type-workload-env-region रखें, बाद में बदलना मुश्किल है।

## ➡️ Next: Azure Tags
