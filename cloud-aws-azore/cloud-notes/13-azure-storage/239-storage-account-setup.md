# 239. Storage Account Setup
# AWS: S3 bucket creation (+ bucket policies, Block Public Access)
# Azure: Azure Storage Account
# हिंदी में: सुरक्षित Storage Account बनाने के स्टेप्स

---

## 🔵 Simple Definition (2 lines)
A storage account is the top-level namespace that holds Blob, Files, Queue and Table services with shared redundancy, networking and keys.
हिंदी: Storage Account वह कंटेनर है जिसके अंदर आपकी सारी स्टोरेज सर्विसेज़ रहती हैं।

---

## 🔴 Why it Exists (2 lines)
Settings like redundancy, region, tier and network rules are defined once per account.
Wrong defaults (public access, old TLS) become security issues.

---

## 🟢 How it Works
```
Choose: name (3-24 lowercase letters/digits, globally unique)
        region, kind = StorageV2, performance = Standard/Premium
        redundancy = LRS | ZRS | GRS | GZRS (RA- variants for read access)
        security = min TLS 1.2, no public blob access, disable shared key if possible
        network = public + firewall rules, or private endpoint
Then: containers, RBAC roles, lifecycle policy, diagnostics
```

---

## 💻 Code / Config Example
```bash
az group create -n rg-app -l centralindia
az storage account create -n myappstore2026 -g rg-app -l centralindia \
  --sku Standard_ZRS --kind StorageV2 --access-tier Hot \
  --min-tls-version TLS1_2 --allow-blob-public-access false \
  --https-only true
az storage container create -n uploads --account-name myappstore2026 --auth-mode login
# Grant your app's managed identity data access (replace <principal-id>)
az role assignment create --assignee <principal-id> \
  --role "Storage Blob Data Contributor" \
  --scope $(az storage account show -n myappstore2026 -g rg-app --query id -o tsv)
```
```yaml
# GitHub Actions step (OIDC login assumed)
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
- run: az storage blob upload-batch -d uploads -s ./dist --account-name myappstore2026 --auth-mode login
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Unit | Bucket (per region) | Storage account (many containers) |
| Public block | Block Public Access | allow-blob-public-access false |
| Redundancy | Multi-AZ by default | LRS/ZRS/GRS/GZRS choice |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Using LRS for critical data.
✅ Correct: Use ZRS or GZRS for zone/region failure tolerance.

❌ Mistake: One account for everything (shared limits, blast radius).
✅ Correct: Split by environment and workload.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Recommended account kind?
A1: StorageV2 (general purpose v2).

Q2: [Medium] LRS vs ZRS vs GRS?
A2: LRS = copies in one datacenter; ZRS = across zones in one region; GRS = also replicated to a paired region.

Q3: [Hard] Lock down an account for production.
A3: Disable public blob access and ideally shared-key auth, use Entra ID RBAC with managed identities, private endpoints + firewall, TLS 1.2, soft delete, diagnostics logs, and Defender for Storage.

---

## ✅ Quick Checklist
□ Redundancy chosen consciously
□ Public access off, TLS 1.2
□ RBAC and managed identity

---

## ⚡ 1-Line Summary
Set redundancy and security correctly at account creation | account बनाते समय redundancy और security सही चुनें

## ➡️ Next: SAS Tokens

---
