# 68. AURORA VS RDS
# AWS: Aurora vs standard RDS (PostgreSQL/MySQL)
# Azure: Azure SQL Hyperscale vs PostgreSQL/MySQL Flexible Server
# हिंदी में: Aurora या RDS, कौन-सा चुनें

---

## 🔵 Simple Definition (2 lines)
Standard RDS runs stock engines on EBS volumes; Aurora runs a modified engine on a distributed cluster volume with up to 15 readers.
हिंदी: RDS में सामान्य इंजन EBS पर चलता है; Aurora में बदला हुआ इंजन डिस्ट्रीब्यूटेड स्टोरेज पर चलता है।

---

## 🔴 Why it Exists (2 lines)
Teams outgrow one RDS instance: they need faster failover, more replicas and no storage planning.
But Aurora costs more and ties you to AWS, so the choice is a trade-off.

---

## 🟢 How it Works
```
Criteria            RDS (Postgres)            Aurora (Postgres)
Storage             EBS, you size it          Auto-grow, 6 copies/3 AZ
Replicas            up to 15, async           up to 15, shared storage (low lag)
Failover            typically 60-120 s        typically faster (about 30 s or less)
Cost (small)        cheaper                   usually higher base cost
Portability         high (stock engine)       lower (AWS-specific)
Rule of thumb: start RDS, move to Aurora when HA/scale needs justify cost
```

---

## 💻 Code / Config Example
```bash
# Migrate RDS Postgres -> Aurora: create an Aurora read replica of the RDS instance
aws rds create-db-cluster \
  --db-cluster-identifier app-aurora \
  --engine aurora-postgresql \
  --replication-source-identifier arn:aws:rds:ap-south-1:123456789012:db:app-pg

# Later: promote the cluster to standalone
aws rds promote-read-replica-db-cluster --db-cluster-identifier app-aurora
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Standard | RDS PostgreSQL/MySQL | Flexible Server |
| Premium cloud-native | Aurora | Azure SQL Hyperscale (SQL Server engine; not PostgreSQL) |
| Failover | Aurora typically faster | Zone-redundant HA |
| Pricing | Aurora higher base; I/O-Optimized option exists (approximate - check current docs) | Varies by tier (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Choosing Aurora for a 5 GB side project.
✅ Correct: Use a small RDS instance; revisit at scale.

❌ Mistake: Ignoring Aurora's I/O billing model.
✅ Correct: Compare Standard vs I/O-Optimized for your IO pattern.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] One benefit of Aurora over RDS?
A1: Faster failover and auto-scaling storage with up to 15 low-lag readers.

Q2: [Medium] Is Aurora always better?
A2: No, it costs more and is less portable; RDS fits small or portability-sensitive workloads.

Q3: [Hard] Migrate a live RDS Postgres to Aurora with minimal downtime?
A3: Create an Aurora read replica cluster from the RDS instance, wait for lag near zero, stop writes, promote, switch the app endpoint.

---

## ✅ Quick Checklist
□ Measured need for failover time and read scale
□ Cost compared for both
□ Extension compatibility checked

---

## ⚡ 1-Line Summary
Start with RDS; pick Aurora when scale and failover justify the cost. | पहले RDS से शुरू करें; स्केल और फेलओवर की ज़रूरत हो तो Aurora लें।

## ➡️ Next: Aurora Serverless

---
