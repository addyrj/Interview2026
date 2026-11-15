# 238. Azure Data Lake Storage
# AWS: S3 + Lake Formation (data lake pattern)
# Azure: Azure Data Lake Storage Gen2 (ADLS Gen2)
# हिंदी में: Blob Storage पर बना analytics-अनुकूल डेटा लेक

---

## 🔵 Simple Definition (2 lines)
ADLS Gen2 is Blob Storage with the hierarchical namespace enabled, giving real directories, POSIX-style ACLs and fast atomic renames for big data.
हिंदी: असली फ़ोल्डर और permissions के साथ analytics के लिए अनुकूल स्टोरेज।

---

## 🔴 Why it Exists (2 lines)
Flat object stores make directory rename/delete slow (copy each object) for Spark/Hive jobs.
Hierarchical namespace makes them metadata operations.

---

## 🟢 How it Works
```
Storage account (isHnsEnabled = true)
  filesystem (container) / raw / orders / 2026 / 11 / part-0001.parquet
  Endpoint: abfss://curated@myapplake.dfs.core.windows.net/...
  Access: RBAC + POSIX ACLs per directory
Medallion layout: raw (bronze) -> cleaned (silver) -> curated (gold)
Used by Synapse, Databricks, Data Factory, HDInsight
```

---

## 💻 Code / Config Example
```bash
az storage account create -n myapplake -g rg-data -l centralindia \
  --sku Standard_LRS --kind StorageV2 --hns true
az storage fs create -n curated --account-name myapplake --auth-mode login
az storage fs directory create -n orders/2026 -f curated --account-name myapplake --auth-mode login
```
```python
# Python: azure-storage-file-datalake
from azure.storage.filedatalake import DataLakeServiceClient
from azure.identity import DefaultAzureCredential

svc = DataLakeServiceClient("https://myapplake.dfs.core.windows.net", credential=DefaultAzureCredential())
fs = svc.get_file_system_client("curated")
f = fs.get_file_client("orders/2026/data.json")
f.upload_data(b'{"id":1}', overwrite=True)
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Storage | S3 | ADLS Gen2 (Blob + HNS) |
| Directory ops | Prefix-based (slow rename) | True directories, atomic rename |
| Permissions | IAM + Lake Formation | RBAC + POSIX ACLs |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Forgetting HNS must be chosen at account creation.
✅ Correct: Enable --hns true at creation (an upgrade path exists but check docs and limits).

❌ Mistake: Giving broad account-level roles to everyone.
✅ Correct: Use RBAC for coarse and ACLs for fine-grained directory access.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What makes it "Gen2"?
A1: Blob Storage plus hierarchical namespace.

Q2: [Medium] Which URI scheme for Spark?
A2: abfss:// (TLS) against the dfs endpoint.

Q3: [Hard] Design a lake layout.
A3: Separate containers or folders for raw/cleaned/curated, partition by date, store Parquet, apply ACLs per zone, lifecycle old raw data to Cool/Archive.

---

## ✅ Quick Checklist
□ HNS enabled
□ Zones (raw/curated) with ACLs
□ Parquet, partitioned

---

## ⚡ 1-Line Summary
ADLS Gen2 = Blob + real folders for analytics | ADLS Gen2 = Blob + असली फ़ोल्डर, analytics के लिए

## ➡️ Next: Storage Account Setup

---
