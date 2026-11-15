# 190. Azure Blueprints
# AWS: AWS Control Tower / Service Catalog
# Azure: Azure Blueprints (deprecated - being retired; use Template Specs + Deployment Stacks + Policy)
# हिंदी में: पुराना टेम्पलेट-पैकेज जो अब रिटायर हो रहा है; नया तरीका Template Specs और Policy

---

## 🔵 Simple Definition
Blueprints packaged ARM templates, policies, RBAC and resource groups into a versioned, assignable definition. Microsoft announced deprecation (planned retirement July 2026 - verify current docs).
Blueprints एक पैकेज था (template + policy + RBAC), जो अब deprecated है।

---

## 🔴 Why it Exists
Set up new subscriptions consistently (landing zones). Today the same goal is met with IaC.

---

## 🟢 How it Works
```
Old:  Blueprint = Artifacts(ARM, Policy, Role, RG) -> publish version -> assign to subscription (locks optional)
New:  Bicep/Terraform modules + Template Specs (versioned)
      + Azure Policy initiatives + Deployment Stacks (deny-delete locks)
      + CI/CD pipeline per subscription (subscription vending)
```

---

## 💻 Code / Config Example
```bash
# Replacement: publish a versioned Template Spec from Bicep
az ts create --name landing-zone --version 1.0 \
  --resource-group rg-templates --location centralindia \
  --template-file main.bicep
# Deploy it with a stack that prevents deletion of managed resources
az stack sub create --name lz-stack --location centralindia \
  --template-spec <templateSpecVersionId> \
  --deny-settings-mode DenyDelete --action-on-unmanage detachAll
```
(Flags per recent Azure CLI; confirm with `az stack sub create -h`.)

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Landing zone | Control Tower | Azure Landing Zones (Bicep/Terraform) |
| Catalog of templates | Service Catalog | Template Specs |
| Locking | SCPs / stack policies | Deployment Stacks deny settings |
| Status | Active | Blueprints deprecated |

---

## ⚠️ Common Mistakes
❌ Mistake: Starting a new project on Blueprints.
✅ Correct: Use Template Specs, Deployment Stacks and Policy.

❌ Mistake: Deleting a blueprint assignment and expecting cleanup.
✅ Correct: Plan resource lifecycle explicitly.

---

## ⚫ Interview Q&A
Q1: [Easy] What were Blueprints?
A1: A packaged, versioned set of templates, policies and RBAC for subscriptions.

Q2: [Medium] Why deprecated?
A2: Overlap with IaC tools and Policy; Microsoft recommends Template Specs and Deployment Stacks.

Q3: [Hard] How do you vend a compliant subscription now?
A3: Pipeline creates the subscription under a management group, which inherits policy; Bicep/Terraform deploys network, logging, RBAC.

---

## ✅ Quick Checklist
□ Not building on Blueprints
□ Landing zone in IaC repo
□ Policy at management group

---

## ⚡ 1-Line Summary
Blueprints are retiring; use IaC + Policy + Template Specs. | Blueprints रिटायर हो रहा है; IaC + Policy का उपयोग करें।

## ➡️ Next: Azure Virtual Machines
