---

# 261. MANAGED IDENTITIES
# AWS: IAM Roles (instance profile / task role / Lambda execution role)
# Azure: Managed Identities (system-assigned / user-assigned)
# हिंदी में: मैनेज्ड आइडेंटिटी

---

## 🔵 Simple Definition (2 lines)
A Managed Identity is an Entra ID identity that Azure creates and rotates for your resource (VM, App Service, Container App), so code gets tokens without any stored secret.
हिंदी: Managed Identity Azure द्वारा दी गई ऑटो-रोटेट होने वाली पहचान है, जिससे कोड बिना पासवर्ड/की के दूसरी सर्विस से बात करता है।

---

## 🔴 Why it Exists (2 lines)
Connection strings and client secrets in env files leak and expire. Managed identity removes the secret entirely.

---

## 🟢 How it Works
```
App Service (identity enabled)
   |  1. asks local IMDS/identity endpoint for token (resource=storage)
   v
Entra ID  --> 2. returns short-lived JWT
   |
   v
Storage / Key Vault / SQL  3. checks RBAC role of that identity -> allow/deny

system-assigned: lifecycle tied to the resource (deleted with it)
user-assigned  : separate resource, reusable across many apps
```

---

## 💻 Code / Config Example
```bash
# Enable system-assigned identity on a web app
az webapp identity assign -g rg-prod -n api-prod

# Give it read access to blobs (RBAC, least privilege)
PRINCIPAL=$(az webapp identity show -g rg-prod -n api-prod --query principalId -o tsv)
az role assignment create --assignee-object-id "$PRINCIPAL" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/<sub-id>/resourceGroups/rg-prod/providers/Microsoft.Storage/storageAccounts/stprod001"
```
```javascript
// Node.js: DefaultAzureCredential uses the managed identity in Azure,
// and your `az login` locally. No secret in code.
const { DefaultAzureCredential } = require("@azure/identity");
const { BlobServiceClient } = require("@azure/storage-blob");
const svc = new BlobServiceClient(
  "https://stprod001.blob.core.windows.net",
  new DefaultAzureCredential()
);
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | IAM role attached to EC2/ECS/Lambda | Managed Identity |
| Token source | STS temp credentials via IMDS | Entra ID token via IMDS/identity endpoint |
| Reusable identity | One role, many resources | User-assigned identity |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Putting storage account keys in App Settings.
✅ Correct: Enable managed identity and assign a data-plane RBAC role.

❌ Mistake: Assigning Owner/Contributor at subscription scope.
✅ Correct: Narrow role (e.g. Blob Data Reader) at resource scope.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a managed identity?
A1: An Azure-managed Entra ID identity for a resource, giving tokens without secrets.

Q2: [Medium] System-assigned vs user-assigned?
A2: System-assigned is 1:1 with the resource and deleted with it. User-assigned is a standalone resource shareable by many resources, good for blue/green slots and pre-provisioned RBAC.

Q3: [Hard] RBAC role was assigned but the app still gets 403. Why?
A3: Role assignments can take minutes to propagate and tokens are cached (up to ~24h by the identity platform); also check scope, data-plane vs control-plane role (Contributor does not grant blob data access), and firewall rules on the target.

---

## ✅ Quick Checklist
□ Identity enabled on every compute resource
□ Data-plane RBAC role at narrowest scope
□ No keys/connection strings left in settings

---

## ⚡ 1-Line Summary
Managed identity = secretless auth for Azure resources | मैनेज्ड आइडेंटिटी = बिना सीक्रेट के सुरक्षित लॉगिन।

## ➡️ Next: Azure Policy Compliance

---
