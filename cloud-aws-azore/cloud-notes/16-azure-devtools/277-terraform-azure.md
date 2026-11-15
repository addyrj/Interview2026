---

# 277. TERRAFORM + AZURE
# AWS: Terraform with the aws provider
# Azure: Terraform with the azurerm provider
# हिंदी में: टेराफॉर्म + एज़्योर

---

## 🔵 Simple Definition (2 lines)
Terraform provisions Azure through the `azurerm` provider using HCL and a state file that tracks real resources.
हिंदी: Terraform HCL कोड और state फ़ाइल से Azure रिसोर्स बनाता और ट्रैक करता है।

---

## 🔴 Why it Exists (2 lines)
Multi-cloud or multi-tool teams want one IaC workflow (plan/apply) with a big module ecosystem.

---

## 🟢 How it Works
```
*.tf  -> terraform init (providers, backend)
      -> terraform plan  (diff vs state)
      -> terraform apply
State: remote backend in Azure Storage (blob lease = lock)
Auth: az login | service principal | OIDC (CI) | managed identity
```

---

## 💻 Code / Config Example
```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.100" }
  }
  backend "azurerm" {
    resource_group_name  = "rg-tfstate"
    storage_account_name = "sttfstate001"
    container_name       = "tfstate"
    key                  = "prod.tfstate"
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-prod"
  location = "centralindia"
}

resource "azurerm_storage_account" "st" {
  name                     = "stprod001"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
}
```
```bash
terraform init && terraform plan -out tfplan && terraform apply tfplan
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Provider | hashicorp/aws | hashicorp/azurerm (and azapi) |
| Remote state | S3 (+ DynamoDB or native lock) | Azure Storage blob (lease lock) |
| Native alt | CloudFormation | Bicep/ARM |
| Pricing | Free CLI; HCP Terraform tiers | Same |

---

## ⚠️ Common Mistakes
❌ Mistake: Local state or committed tfstate.
✅ Correct: Remote backend with RBAC, versioning.

❌ Mistake: Provider version unpinned.
✅ Correct: Pin with `~>` and commit `.terraform.lock.hcl`.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is state?
A1: Mapping of config to real resources used to compute diffs.

Q2: [Medium] azurerm vs azapi?
A2: azurerm is curated resources; azapi calls any ARM API version, useful for new features.

Q3: [Hard] Drift or resource created manually?
A3: `terraform plan` shows drift; `terraform import` (or import block) to adopt, or apply to revert; restrict portal write access.

---

## ✅ Quick Checklist
□ Remote state with locking
□ Providers pinned
□ OIDC auth in CI

---

## ⚡ 1-Line Summary
Terraform = multi-cloud IaC with state | Terraform = state के साथ मल्टी-क्लाउड इन्फ्रा कोड।

## ➡️ Next: Azure SDK (Node.js + Python)

---
