# 67. AURORA - WHAT + WHY
# AWS: Amazon Aurora (MySQL- and PostgreSQL-compatible)
# Azure: N/A (AWS-only concept); closest: Azure SQL Database Hyperscale
# हिंदी में: Aurora क्या है और क्यों

---

## 🔵 Simple Definition (2 lines)
Aurora is AWS's cloud-built relational database, compatible with MySQL/PostgreSQL, that separates compute from a shared, distributed storage layer.
हिंदी: Aurora AWS का क्लाउड-नेटिव डेटाबेस है जिसमें कंप्यूट और स्टोरेज अलग रहते हैं।

---

## 🔴 Why it Exists (2 lines)
Classic RDS replicates whole EBS volumes between instances, which is slow to fail over and scale.
Aurora's shared storage gives faster failover, quick replicas and auto-growing storage.

---

## 🟢 How it Works
```
 Writer instance  Reader-1  Reader-2   (up to 15 readers)
        \            |         /
   ===== Shared cluster volume =====
   6 copies of data across 3 AZs, grows automatically (up to 128 TiB)
Endpoints:
  cluster endpoint -> writer     reader endpoint -> load-balanced readers
```

---

## 💻 Code / Config Example
```bash
# Aurora PostgreSQL cluster + one writer (AWS CLI v2)
aws rds create-db-cluster \
  --db-cluster-identifier app-aurora \
  --engine aurora-postgresql \
  --master-username appadmin \
  --manage-master-user-password

aws rds create-db-instance \
  --db-instance-identifier app-aurora-1 \
  --db-cluster-identifier app-aurora \
  --engine aurora-postgresql \
  --db-instance-class db.r6g.large
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Aurora | N/A (AWS-only); closest Azure SQL Hyperscale or PostgreSQL Flexible Server |
| Storage | Shared, 6 copies / 3 AZ | Hyperscale: page servers, separate storage |
| Replicas | Up to 15 | Hyperscale named replicas |
| Pricing | Instance + storage + IO (approximate - check current docs) | vCore + storage (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Expecting 100% PostgreSQL/MySQL behaviour and extensions.
✅ Correct: Check compatibility and supported extensions first.

❌ Mistake: Pointing everything to the writer endpoint.
✅ Correct: Send reads to the reader endpoint.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Aurora?
A1: AWS-built MySQL/PostgreSQL-compatible database with distributed shared storage.

Q2: [Medium] Why is Aurora failover faster?
A2: Replicas share the same storage volume, so no data copy is needed; a reader is promoted.

Q3: [Hard] When would you not use Aurora?
A3: Small/cheap workloads where a t4g RDS is enough, strict portability or non-supported extensions, or need for a different engine.

---

## ✅ Quick Checklist
□ Engine version supported by Aurora
□ Reader endpoint used for reads
□ Cost vs plain RDS estimated

---

## ⚡ 1-Line Summary
Aurora = MySQL/Postgres compatible engine on shared 6-copy storage. | Aurora = शेयर्ड 6-कॉपी स्टोरेज पर MySQL/Postgres कम्पैटिबल इंजन।

## ➡️ Next: Aurora vs RDS

---
