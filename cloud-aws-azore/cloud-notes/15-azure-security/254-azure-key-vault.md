---

# 254. Azure Key Vault (= AWS Secrets Manager)
# AWS: AWS Secrets Manager (+ KMS for keys, ACM for certs)
# Azure: Azure Key Vault (secrets, keys, certificates in one service)
# हिंदी में: Key Vault = पासवर्ड, API keys और सर्टिफ़िकेट रखने की सुरक्षित तिजोरी

---

## 🔵 Simple Definition (2 lines)
Key Vault stores secrets, encryption keys and certificates with access control and audit logs.
Key Vault में secrets कोड या .env में रखने की जगह सुरक्षित तरीके से रखे जाते हैं।

---

## 🔴 Why it Exists (2 lines)
Hardcoded secrets leak through Git and images.
Central, audited, rotatable storage removes secrets from code.

---

## 🟢 How it Works
```
App (Managed Identity) --Entra token--> Key Vault
        RBAC role: "Key Vault Secrets User"  -> get secret
Vault holds: Secrets | Keys (HSM-backed optional) | Certificates
Features: versions, soft delete, purge protection, rotation, private endpoint, diagnostic logs
```

---

## 💻 Code / Config Example
```bash
az keyvault create -g rg-demo -n kv-demo-12345 -l centralindia --enable-rbac-authorization true
az keyvault secret set --vault-name kv-demo-12345 -n DB-PASSWORD --value 's3cr3t'
az role assignment create --assignee <managed-identity-object-id> \
  --role "Key Vault Secrets User" \
  --scope $(az keyvault show -n kv-demo-12345 --query id -o tsv)
```
```javascript
// npm i @azure/keyvault-secrets @azure/identity
const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");

async function getDbPassword() {
  const client = new SecretClient("https://kv-demo-12345.vault.azure.net", new DefaultAzureCredential());
  const secret = await client.getSecret("DB-PASSWORD");
  return secret.value;
}
module.exports = { getDbPassword };
```
```yaml
# GitHub Actions: OIDC login, then read secret (no stored client secret)
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
- run: az keyvault secret show --vault-name kv-demo-12345 -n DB-PASSWORD --query value -o tsv
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Secrets | Secrets Manager / SSM Parameter Store | Key Vault secrets |
| Keys | KMS | Key Vault keys / Managed HSM |
| Certificates | ACM | Key Vault certificates |
| Auth | IAM role | Managed Identity + RBAC |
| Pricing | Per secret + per API call (approximate - check current docs) | Per operations; premium for HSM (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Using access policies and broad rights for everyone.
✅ Correct: Use RBAC and least privilege; one vault per app/environment.

❌ Mistake: Echoing secrets in CI logs.
✅ Correct: Mask values and pass via env vars to the step that needs them.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What can Key Vault store?
A1: Secrets, cryptographic keys and certificates.

Q2: [Medium] How does an app authenticate without a password?
A2: Managed Identity (or workload identity federation in CI) gets an Entra token; RBAC grants access.

Q3: [Hard] Protect against accidental deletion?
A3: Enable soft delete and purge protection; restrict network with private endpoints/firewall and log access to Log Analytics.

---

## ✅ Quick Checklist
□ RBAC mode, Managed Identity used
□ Soft delete + purge protection on
□ Diagnostic logs enabled

---

## ⚡ 1-Line Summary
Key Vault is the audited safe for secrets, keys and certs | Key Vault secrets, keys और certs की सुरक्षित तिजोरी है।

## ➡️ Next: 255. Azure Monitor

---
