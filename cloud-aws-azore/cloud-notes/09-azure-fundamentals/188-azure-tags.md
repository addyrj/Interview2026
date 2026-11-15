# 188. Azure Tags
# AWS: Resource tags / Tag Policies
# Azure: Resource tags
# हिंदी में: रिसोर्स पर लगे key-value लेबल, खर्च और मालिकाना ट्रैक करने के लिए

---

## 🔵 Simple Definition
Tags are name/value pairs on resources, resource groups and subscriptions used for cost allocation, ownership and automation.
टैग key-value लेबल होते हैं जिनसे खर्च, मालिक और environment पता चलता है।

---

## 🔴 Why it Exists
Without labels you cannot answer "who owns this VM and which project pays for it?"

---

## 🟢 How it Works
```
Resource Group tag: env=prod, owner=team-api, costcenter=1234
Resources do NOT inherit tags automatically -> use Policy "Inherit a tag from the resource group" (Modify effect)
Cost analysis -> Group by tag
```
Limit is about 50 tags per resource (approximate - check docs). Tag names are case-insensitive, values case-sensitive.

---

## 💻 Code / Config Example
```bash
az group create -n rg-orders-prod -l centralindia \
  --tags env=prod owner=team-api costcenter=1234
# Add/merge tags on an existing resource
az tag update --resource-id <resource-id> --operation merge --tags tier=backend
# Find by tag
az resource list --tag env=prod -o table
```
```json
{
  "if": { "field": "tags['costcenter']", "exists": "false" },
  "then": { "effect": "deny" }
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Tagging | Per resource | Per resource, RG, subscription |
| Inheritance | No (except via tooling) | No by default; Policy Modify |
| Enforcement | Tag Policies / SCP / Config | Azure Policy |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming RG tags flow to resources.
✅ Correct: Use the inherit-tag policy.

❌ Mistake: Free-text values (`Prod`, `prod`, `production`).
✅ Correct: Fixed allowed values enforced by policy.

---

## ⚫ Interview Q&A
Q1: [Easy] Why tag?
A1: Cost allocation, ownership, automation.

Q2: [Medium] Do tags inherit?
A2: No; use a Modify policy to copy them.

Q3: [Hard] Enforce `env` tag on all new resources?
A3: Policy with deny (or modify to add a default) assigned at management group; remediation task for existing resources.

---

## ✅ Quick Checklist
□ Mandatory tags defined (env, owner, costcenter)
□ Inherit policy assigned
□ Cost report grouped by tag

---

## ⚡ 1-Line Summary
Tags = metadata for cost and ownership; enforce with Policy. | Tags = खर्च और मालिक का लेबल; Policy से अनिवार्य करें।

## ➡️ Next: Azure Policy
