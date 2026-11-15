# 233. Blob vs S3 Comparison
# AWS: Amazon S3
# Azure: Azure Blob Storage
# हिंदी में: S3 और Blob की सीधी तुलना

---

## 🔵 Simple Definition (2 lines)
Both are durable object stores; they differ mainly in naming, access control model and tier names.
हिंदी: काम लगभग एक जैसा है, बस शब्दावली, permissions और tiers के नाम अलग हैं।

---

## 🔴 Why it Exists (2 lines)
Teams moving between clouds (or multi-cloud) must map concepts correctly.
Misreading the differences causes security and cost mistakes.

---

## 🟢 How it Works
```
S3:  Bucket -> Object                  Blob: Storage Account -> Container -> Blob
S3:  IAM policy / bucket policy / ACL  Blob: RBAC / SAS / (ACLs on ADLS Gen2)
S3:  Presigned URL                     Blob: SAS token
S3:  Lifecycle rules                   Blob: Lifecycle management policy
S3:  Versioning, Object Lock           Blob: Versioning, Immutability policies
S3:  Replication (CRR/SRR)             Blob: Object replication, GRS/GZRS
S3:  Standard/IA/Glacier               Blob: Hot/Cool/Cold/Archive
```

---

## 💻 Code / Config Example
```python
# Same operation in both SDKs (Python)
import boto3
s3 = boto3.client("s3")
s3.put_object(Bucket="myapp-uploads", Key="a.txt", Body=b"hi")

from azure.storage.blob import BlobServiceClient
svc = BlobServiceClient.from_connection_string("<AZURE_STORAGE_CONNECTION_STRING>")
svc.get_blob_client("uploads", "a.txt").upload_blob(b"hi", overwrite=True)
```
```bash
aws s3 cp ./a.txt s3://myapp-uploads/a.txt
az storage blob upload --account-name myappstore -c uploads -n a.txt -f ./a.txt --auth-mode login
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Max single object | ~5 TB | ~190 TB for block blob (approximate — check docs) |
| Temp access | Presigned URL | SAS (user delegation SAS) |
| Redundancy | Within region by default (multi-AZ); CRR | LRS/ZRS/GRS/GZRS chosen per account |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming "bucket" equals "storage account".
✅ Correct: Account holds Blob, Files, Queue, Table; container is the bucket analogue.

❌ Mistake: Forgetting redundancy is a choice in Azure.
✅ Correct: Pick LRS/ZRS/GRS deliberately per data criticality.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] S3 bucket equals what in Azure?
A1: A Blob container inside a storage account.

Q2: [Medium] Presigned URL equals what?
A2: A SAS token (best: user delegation SAS signed with Entra ID).

Q3: [Hard] Migrate S3 to Blob?
A3: Use AzCopy (supports S3 source) or Data Factory, map lifecycle/tiers and IAM to RBAC/SAS, validate checksums, then switch app SDK and endpoints.

---

## ✅ Quick Checklist
□ Terminology map done
□ Redundancy option chosen
□ Auth model translated (IAM to RBAC)

---

## ⚡ 1-Line Summary
Same idea, different names: bucket=container, presigned=SAS | वही आइडिया, अलग नाम: bucket=container, presigned=SAS

## ➡️ Next: Blob Storage Tiers

---
