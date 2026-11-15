---

# 275. ARM TEMPLATES
# AWS: CloudFormation
# Azure: ARM Templates (Azure Resource Manager, JSON)
# हिंदी में: एआरएम टेम्पलेट्स

---

## 🔵 Simple Definition (2 lines)
ARM templates are declarative JSON files describing Azure resources; Azure Resource Manager creates or updates them idempotently.
हिंदी: ARM टेम्पलेट JSON में लिखा हुआ इन्फ्रा-विवरण है जिसे Azure अपने आप बना देता है।

---

## 🔴 Why it Exists (2 lines)
Portal clicking is not repeatable. Templates give version-controlled, repeatable infrastructure.

---

## 🟢 How it Works
```
template.json (parameters, variables, resources, outputs)
   -> az deployment group create (scope: RG / sub / mgmt group / tenant)
   -> ARM validates, orders by dependsOn, deploys in parallel
   Modes: Incremental (default, keeps others) | Complete (deletes extras)
   what-if preview before deploying
```

---

## 💻 Code / Config Example
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "storageName": { "type": "string", "minLength": 3, "maxLength": 24 }
  },
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2023-01-01",
      "name": "[parameters('storageName')]",
      "location": "[resourceGroup().location]",
      "sku": { "name": "Standard_LRS" },
      "kind": "StorageV2",
      "properties": {
        "allowBlobPublicAccess": false,
        "minimumTlsVersion": "TLS1_2",
        "supportsHttpsTrafficOnly": true
      }
    }
  ],
  "outputs": {
    "id": { "type": "string", "value": "[resourceId('Microsoft.Storage/storageAccounts', parameters('storageName'))]" }
  }
}
```
```bash
az deployment group what-if -g rg-prod -f template.json -p storageName=stprod001
az deployment group create  -g rg-prod -f template.json -p storageName=stprod001
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| IaC native | CloudFormation (YAML/JSON) | ARM (JSON) / Bicep |
| Preview | Change sets | what-if |
| State | Managed by service (stacks) | Managed by ARM (deployments, no state file) |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Using Complete mode casually.
✅ Correct: Use Incremental; run what-if first.

❌ Mistake: Hand-writing big JSON.
✅ Correct: Author in Bicep, compile to ARM.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] ARM template sections?
A1: parameters, variables, resources, outputs (plus functions).

Q2: [Medium] Incremental vs Complete mode?
A2: Incremental adds/updates only listed resources; Complete deletes resources in the group not in the template.

Q3: [Hard] How to avoid secrets in templates?
A3: Use `securestring` params, Key Vault references in parameter files, and managed identities.

---

## ✅ Quick Checklist
□ what-if before deploy
□ Parameter files per environment
□ Prefer Bicep for authoring

---

## ⚡ 1-Line Summary
ARM = JSON-based declarative Azure infra | ARM = JSON में Azure इन्फ्रा की घोषणा।

## ➡️ Next: Bicep (IaC for Azure)

---
