# 179. Azure Resource Groups
# AWS: N/A (AWS-only gap); closest: CloudFormation stack / Resource Groups & Tag Editor
# Azure: Resource Group
# हिंदी में: संबंधित resources का एक logical folder

---

## 🔵 Simple Definition
A resource group is a logical container holding related Azure resources that share a lifecycle, access control and tags.
हिंदी: Resource group एक folder जैसा है जिसमें एक project के सारे resources साथ रहते हैं।

---

## 🔴 Why it Exists
Managing, billing and deleting dozens of resources one by one is error-prone.
Delete the group and everything inside goes; assign RBAC once at group scope.

---

## 🟢 How it Works
```
Subscription
 +-- rg-myapp-prod (centralindia)
 |     +-- Container App, ACR, Key Vault, Postgres
 +-- rg-myapp-dev
Rules: each resource is in exactly one group; groups cannot be nested;
resources may be in a different region than the group's metadata location.
```

---

## 💻 Code / Config Example
```bash
az group create --name rg-myapp-prod --location centralindia \
  --tags env=prod app=myapp owner=aditya

az group list -o table
az resource list -g rg-myapp-prod -o table

# lock against accidental delete
az lock create --name nodelete --lock-type CanNotDelete -g rg-myapp-prod

# delete everything inside
az group delete --name rg-myapp-dev --yes --no-wait
```
```bicep
// main.bicep deployed at resource group scope
param location string = resourceGroup().location
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stmyappprod001'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Container | N/A (AWS-only gap); CloudFormation stack, tags | Resource Group |
| Bulk delete | Delete stack | Delete group |
| Access | IAM policies with tags/ARNs | RBAC at group scope |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: One giant group for everything.
✅ Correct: Group by lifecycle and environment (rg-app-prod, rg-app-dev).

❌ Mistake: Deleting a group containing shared resources (e.g. a shared VNet).
✅ Correct: Put shared infra in its own group and add a CanNotDelete lock.

---

## ⚫ Interview Q&A
Q1: [Easy] Can a resource be in two groups?
A1: No, exactly one.

Q2: [Medium] Can you move resources between groups?
A2: Yes for most types (`az resource move`), with some limitations by type.

Q3: [Hard] How do you structure groups for a multi-env app?
A3: One group per environment per app tier or lifecycle, naming and tag standards, RBAC and policy assigned at group/subscription, Bicep/Terraform per group, locks on prod.

---

## ✅ Quick Checklist
□ Naming convention
□ Tags for cost tracking
□ Locks on production groups

---

## ⚡ 1-Line Summary
Resource group = lifecycle, access and billing folder | Resource group lifecycle, access और billing का folder है।

## ➡️ Next: 180. Azure Subscriptions
