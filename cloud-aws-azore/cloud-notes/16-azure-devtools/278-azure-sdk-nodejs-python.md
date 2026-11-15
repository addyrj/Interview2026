---

# 278. AZURE SDK (NODE.JS + PYTHON)
# AWS: AWS SDK v3 (JS) / boto3 (Python)
# Azure: Azure SDK for JavaScript (@azure/*) / Python (azure-*)
# हिंदी में: एज़्योर SDK (Node.js + Python)

---

## 🔵 Simple Definition (2 lines)
Per-service client libraries to call Azure from code, all authenticating through `azure-identity` (DefaultAzureCredential).
हिंदी: Azure सर्विस को कोड से बुलाने की लाइब्रेरी, जो DefaultAzureCredential से लॉगिन करती है।

---

## 🔴 Why it Exists (2 lines)
Raw REST calls need auth, retries and paging. SDKs provide that consistently with typed clients.

---

## 🟢 How it Works
```
npm: @azure/identity, @azure/storage-blob, @azure/keyvault-secrets
pip: azure-identity, azure-storage-blob, azure-keyvault-secrets
Credential chain (DefaultAzureCredential): env vars -> workload identity ->
   managed identity -> Azure CLI / azd login -> ...
Client(endpoint, credential) -> operation -> built-in retry/paging
```

---

## 💻 Code / Config Example
```javascript
// Node.js (npm i @azure/identity @azure/storage-blob)
const { DefaultAzureCredential } = require("@azure/identity");
const { BlobServiceClient } = require("@azure/storage-blob");

async function main() {
  const svc = new BlobServiceClient(
    `https://${process.env.STORAGE_ACCOUNT}.blob.core.windows.net`,
    new DefaultAzureCredential()
  );
  const container = svc.getContainerClient("uploads");
  await container.createIfNotExists();
  await container.getBlockBlobClient("hello.txt").upload("hi", 2);
  for await (const b of container.listBlobsFlat()) console.log(b.name);
}
main().catch(console.error);
```
```python
# Python (pip install azure-identity azure-keyvault-secrets)
import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

client = SecretClient(vault_url=os.environ["VAULT_URL"], credential=DefaultAzureCredential())
client.set_secret("db-password", "s3cret")
print(client.get_secret("db-password").value)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| JS SDK | @aws-sdk/client-* | @azure/* |
| Python SDK | boto3 | azure-* |
| Auth | Default credential chain | DefaultAzureCredential |
| Mgmt vs data plane | Same client | Separate: azure-mgmt-* (ARM) vs data clients |
| Pricing | Free | Free |

---

## ⚠️ Common Mistakes
❌ Mistake: Connection strings/keys in code.
✅ Correct: DefaultAzureCredential + RBAC.

❌ Mistake: Creating a client per request.
✅ Correct: Reuse clients (they pool connections).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is DefaultAzureCredential?
A1: A credential chain that works locally and in Azure without code changes.

Q2: [Medium] Management vs data-plane SDK?
A2: azure-mgmt-* creates resources via ARM; data SDKs use them (blobs, secrets).

Q3: [Hard] Slow auth in production?
A3: DefaultAzureCredential tries many sources; use ManagedIdentityCredential directly in prod, and cache the credential object.

---

## ✅ Quick Checklist
□ RBAC role for the identity
□ Single reused client
□ Specific credential in prod

---

## ⚡ 1-Line Summary
Azure SDKs = typed clients with one passwordless auth chain | Azure SDK = एक ही सुरक्षित लॉगिन से सारी सर्विस।

## ➡️ Next: Deploy Node.js to App Service

---
