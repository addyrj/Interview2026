# 232. Azure Blob Storage
# AWS: Amazon S3
# Azure: Azure Blob Storage
# हिंदी में: फ़ाइलों, इमेज, बैकअप के लिए ऑब्जेक्ट स्टोरेज

---

## 🔵 Simple Definition (2 lines)
Blob Storage is Azure's object store for unstructured data (images, videos, logs, backups) accessed over HTTPS inside a storage account container.
हिंदी: असीमित फ़ाइलें सस्ते में रखने की जगह, जो URL या SDK से मिलती है।

---

## 🔴 Why it Exists (2 lines)
App servers and VPS disks are not durable or scalable for user uploads.
Blob gives redundant, durable storage with tiers, lifecycle rules and CDN integration.

---

## 🟢 How it Works
```
Storage Account (myappstore)
   +-- Container (uploads)          <- like an S3 bucket
         +-- Blob (users/42/a.png)  <- block blob (default), append blob, page blob
URL: https://myappstore.blob.core.windows.net/uploads/users/42/a.png
Auth: Entra ID (RBAC) | SAS token | account key (avoid)
```

---

## 💻 Code / Config Example
```javascript
// Node.js: @azure/storage-blob - upload and download
const { BlobServiceClient } = require("@azure/storage-blob");

async function main(connStr) {
  const service = BlobServiceClient.fromConnectionString(connStr);
  const container = service.getContainerClient("uploads");
  await container.createIfNotExists();

  const blob = container.getBlockBlobClient("users/42/hello.txt");
  const data = "hello azure";
  await blob.upload(data, Buffer.byteLength(data), {
    blobHTTPHeaders: { blobContentType: "text/plain" },
  });
  const buf = await blob.downloadToBuffer();
  console.log(buf.toString());
}
module.exports = { main };
```
```bash
az storage blob upload --account-name myappstore --container-name uploads \
  --name report.pdf --file ./report.pdf --auth-mode login
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | S3 | Blob Storage |
| Container | Bucket | Storage account + container |
| Namespace | Flat | Flat (hierarchical with ADLS Gen2) |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Public container access for user files.
✅ Correct: Keep it private; give short-lived SAS or proxy through the API.

❌ Mistake: Using the account key in the app.
✅ Correct: Use managed identity + RBAC (Storage Blob Data Contributor).

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Types of blobs?
A1: Block (files), append (logs), page (VM disks).

Q2: [Medium] How do browsers upload without exposing keys?
A2: API issues a short-lived SAS URL scoped to one blob; the browser PUTs directly.

Q3: [Hard] Protect against accidental deletion?
A3: Enable soft delete, blob versioning, and resource locks; add immutability policies for compliance.

---

## ✅ Quick Checklist
□ Private containers, RBAC
□ Soft delete + versioning on
□ Lifecycle management for tiers

---

## ⚡ 1-Line Summary
Blob = Azure's S3 for durable object storage | Blob = टिकाऊ ऑब्जेक्ट स्टोरेज, Azure का S3

## ➡️ Next: Blob vs S3 Comparison

---
