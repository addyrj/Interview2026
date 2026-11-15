# 240. SAS Tokens
# AWS: S3 Presigned URLs
# Azure: Shared Access Signature (SAS)
# हिंदी में: सीमित समय और अधिकार वाला अस्थायी एक्सेस लिंक

---

## 🔵 Simple Definition (2 lines)
A SAS is a signed URL query string that grants specific permissions on a resource for a limited time without sharing account keys.
हिंदी: SAS से आप किसी को सिर्फ़ तय फ़ाइल पर, तय समय के लिए, तय अधिकार देते हैं।

---

## 🔴 Why it Exists (2 lines)
Browsers and partners need direct upload/download without proxying large files or exposing keys.
Scoped, expiring tokens minimize damage if leaked.

---

## 🟢 How it Works
```
Client -> API: "I want to upload photo.png"
API (managed identity) -> signs SAS (blob path, perms=cw, expiry=10 min)
API -> Client: https://acct.blob.core.windows.net/uploads/photo.png?sv=...&sp=cw&se=...&sig=...
Client -> Blob: PUT directly using the URL
Types: User delegation SAS (signed w/ Entra ID, best) | Service SAS | Account SAS (account key)
```

---

## 💻 Code / Config Example
```javascript
// Node.js: generate a write SAS (account-key based; for user delegation use getUserDelegationKey)
const { StorageSharedKeyCredential, generateBlobSASQueryParameters, BlobSASPermissions } = require("@azure/storage-blob");

function makeSasUrl(account, key, container, blobName) {
  const cred = new StorageSharedKeyCredential(account, key);
  const sas = generateBlobSASQueryParameters({
    containerName: container,
    blobName,
    permissions: BlobSASPermissions.parse("cw"),          // create + write only
    expiresOn: new Date(Date.now() + 10 * 60 * 1000),     // 10 minutes
  }, cred).toString();
  return `https://${account}.blob.core.windows.net/${container}/${blobName}?${sas}`;
}
module.exports = { makeSasUrl };
```
```bash
# User delegation SAS via Azure CLI
az storage blob generate-sas --account-name myappstore --container-name uploads \
  --name photo.png --permissions r --expiry 2026-12-31T00:00Z \
  --https-only --auth-mode login --as-user --full-uri
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Temp URL | Presigned URL | SAS token |
| Signed by | IAM credentials | Account key or Entra ID (user delegation) |
| Revoke | Revoke signer / expire | Stored access policy, rotate key, or revoke delegation key |
| Pricing | Free feature | Free feature |

---

## ⚠️ Common Mistakes
❌ Mistake: Long-lived (years) account SAS with full permissions.
✅ Correct: Short expiry, minimum permissions, HTTPS only, per-blob scope.

❌ Mistake: Putting SAS in logs or public repos.
✅ Correct: Treat SAS as a secret; log only the path.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a SAS?
A1: Signed URL token granting limited access to storage resources.

Q2: [Medium] Why prefer user delegation SAS?
A2: Signed with Entra ID credentials, not the account key; works with RBAC and can be revoked by revoking the delegation key.

Q3: [Hard] How to revoke a leaked service SAS?
A3: If bound to a stored access policy, delete or modify the policy; otherwise rotate the account key (breaks all keyed access) - hence use short expiries and user delegation SAS.

---

## ✅ Quick Checklist
□ Short expiry, minimal permissions
□ HTTPS only
□ User delegation SAS where possible

---

## ⚡ 1-Line Summary
SAS = Azure's presigned URL | SAS = Azure का presigned URL

## ➡️ Next: Azure CDN

---
