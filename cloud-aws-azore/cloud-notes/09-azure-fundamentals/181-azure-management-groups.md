# 181. Azure Management Groups
# AWS: AWS Organizations (Organizational Units + SCPs)
# Azure: Management Groups
# हिंदी में: कई सब्सक्रिप्शन को एक पेड़ (hierarchy) में रखकर एक साथ policy/access लगाना

---

## 🔵 Simple Definition
A container above subscriptions that lets you group many subscriptions and apply Azure Policy and RBAC once; it inherits down the tree.
मैनेजमेंट ग्रुप सब्सक्रिप्शन्स का ग्रुप है, जिस पर लगाई policy/RBAC नीचे सब पर अपने-आप लागू होती है।

---

## 🔴 Why it Exists
Companies have dozens of subscriptions (dev, test, prod, per team). Configuring each one by hand causes drift and gaps.

---

## 🟢 How it Works
```
Tenant Root Management Group (id = Entra tenant id)
 ├── mg-platform
 │     └── sub-connectivity
 └── mg-landingzones
       ├── mg-prod  ── sub-prod-api
       └── mg-nonprod ── sub-dev, sub-test
Policy/RBAC assigned at mg-landingzones -> inherited by all below.
```
Up to 6 levels of depth (excluding root) and 10,000 groups per tenant (approximate, check current docs). A subscription belongs to exactly one management group.

---

## 💻 Code / Config Example
```bash
# Azure CLI (az account management-group ...)
az account management-group create --name mg-prod --display-name "Production"
az account management-group subscription add \
  --name mg-prod --subscription "<subscription-id>"
# Give a group Reader on everything under mg-prod
az role assignment create --assignee "<group-object-id>" \
  --role "Reader" --scope "/providers/Microsoft.Management/managementGroups/mg-prod"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Organizations, OUs | Management Groups |
| Guardrails | SCPs (deny-ceiling only) | Azure Policy + RBAC (can deny, audit, deploy) |
| Unit of isolation | Account | Subscription |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Assigning Owner at the Tenant Root group to many people.
✅ Correct: Assign at a narrow management group; keep root access to a break-glass group.

❌ Mistake: Putting a subscription directly under root.
✅ Correct: Create a default management group and design the hierarchy by environment/workload.

---

## ⚫ Interview Q&A
Q1: [Easy] What is a management group?
A1: A scope above subscriptions for applying policy and access control to many subscriptions.

Q2: [Medium] How does inheritance work?
A2: Policy assignments and role assignments at a parent scope flow to all child management groups, subscriptions, resource groups and resources.

Q3: [Hard] How would you structure it for a Node.js/FastAPI SaaS on Azure?
A3: Root -> platform (shared networking/logging) and landing-zones (prod, nonprod). Apply "allowed regions" and "require tags" policy on landing-zones, stricter policy on prod; one subscription per environment limits blast radius and quota contention.

---

## ✅ Quick Checklist
□ Hierarchy designed by environment, not org chart
□ Policies at management-group level, not per subscription
□ Root access restricted and monitored

---

## ⚡ 1-Line Summary
Management Groups = Organizations for Azure subscriptions, with inherited policy and RBAC. | मैनेजमेंट ग्रुप = सब्सक्रिप्शन्स पर एक साथ नियम लगाने का तरीका।

## ➡️ Next: Azure Active Directory (AAD)
