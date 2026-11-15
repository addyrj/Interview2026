---

# 276. BICEP (IaC FOR AZURE)
# AWS: CloudFormation / AWS CDK
# Azure: Bicep
# हिंदी में: बाइसेप (एज़्योर के लिए IaC)

---

## 🔵 Simple Definition (2 lines)
Bicep is a concise domain-specific language that compiles to ARM JSON, with type safety, modules and no state file.
हिंदी: Bicep ARM का आसान भाषा-रूप है जो कंपाइल होकर ARM JSON बनता है।

---

## 🔴 Why it Exists (2 lines)
ARM JSON is verbose and hard to review. Bicep gives the same power with readable syntax and reusable modules.

---

## 🟢 How it Works
```
main.bicep (+ modules/*.bicep, main.bicepparam)
   -> bicep build -> ARM JSON (automatic in az deployment)
   -> ARM deploys (idempotent) ; what-if for preview
Symbolic names: reference resources directly, dependencies inferred
```

---

## 💻 Code / Config Example
```bicep
// main.bicep : App Service for a Node.js API with managed identity
param location string = resourceGroup().location
param appName string
@allowed([ 'B1', 'P0v3' ])
param skuName string = 'B1'

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: 'plan-${appName}'
  location: location
  kind: 'linux'
  sku: { name: skuName }
  properties: { reserved: true }
}

resource app 'Microsoft.Web/sites@2023-01-01' = {
  name: appName
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      minTlsVersion: '1.2'
      appSettings: [
        { name: 'NODE_ENV', value: 'production' }
      ]
    }
  }
}

output principalId string = app.identity.principalId
```
```bash
az bicep install
az deployment group what-if -g rg-prod -f main.bicep -p appName=api-prod
az deployment group create  -g rg-prod -f main.bicep -p appName=api-prod
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Language | CFN YAML or CDK (TS/Python) | Bicep |
| Preview | Change set | what-if |
| State file | None (service stacks) | None |
| Multi-cloud | No | No (use Terraform) |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: One huge main.bicep.
✅ Correct: Split into modules.

❌ Mistake: Hardcoded passwords.
✅ Correct: `@secure()` params or Key Vault reference.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does Bicep compile to?
A1: ARM JSON.

Q2: [Medium] Bicep vs Terraform?
A2: Bicep is Azure-only, day-0 API support, no state; Terraform is multi-cloud with state and a large provider ecosystem.

Q3: [Hard] How to deploy in CI safely?
A3: Lint + build, what-if on PR, deploy on merge via federated identity, deployment stacks or locks to prevent drift.

---

## ✅ Quick Checklist
□ Modules per concern
□ @secure on secrets
□ what-if in PR pipeline

---

## ⚡ 1-Line Summary
Bicep = readable Azure-native IaC | Bicep = पढ़ने में आसान Azure इन्फ्रा कोड।

## ➡️ Next: Terraform + Azure

---
