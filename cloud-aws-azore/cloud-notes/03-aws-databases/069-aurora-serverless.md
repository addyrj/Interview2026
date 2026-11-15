# 69. AURORA SERVERLESS
# AWS: Aurora Serverless v2
# Azure: Azure SQL Database serverless tier (auto-pause)
# हिंदी में: Aurora Serverless यानी ज़रूरत के हिसाब से अपने-आप स्केल

---

## 🔵 Simple Definition (2 lines)
Aurora Serverless v2 scales database capacity up and down automatically in small steps measured in ACUs (Aurora Capacity Units).
हिंदी: Aurora Serverless v2 लोड के हिसाब से ACU में क्षमता अपने-आप घटाता-बढ़ाता है।

---

## 🔴 Why it Exists (2 lines)
Spiky or unpredictable workloads (dev, reports, new products) waste money on an always-large instance.
You set a min and max ACU and pay for what is used.

---

## 🟢 How it Works
```
Cluster -> instance class "db.serverless"
MinCapacity 0.5 ACU  <-- scales with load -->  MaxCapacity 8 ACU
Billed per ACU-hour used. Newer versions can scale to 0 ACU (auto-pause);
check docs for supported engine versions. Resume takes some seconds.
Note: Serverless v1 is legacy/being retired; use v2.
```

---

## 💻 Code / Config Example
```bash
# Serverless v2 cluster (AWS CLI v2)
aws rds create-db-cluster \
  --db-cluster-identifier app-sls \
  --engine aurora-postgresql \
  --master-username appadmin \
  --manage-master-user-password \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=4

aws rds create-db-instance \
  --db-instance-identifier app-sls-1 \
  --db-cluster-identifier app-sls \
  --engine aurora-postgresql \
  --db-instance-class db.serverless
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | Aurora Serverless v2 | Azure SQL Database serverless |
| Scaling unit | ACU (approx. 2 GiB RAM each) | vCores (min/max) |
| Auto-pause | Supported on newer versions (check docs) | Yes, after idle delay |
| Pricing | Per ACU-hour (approximate - check current docs) | Per vCore-second used (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Setting max ACU too high with no budget alarm.
✅ Correct: Cap MaxCapacity and set billing alerts.

❌ Mistake: Using serverless for steady 24x7 high load.
✅ Correct: Provisioned (with reserved pricing) is cheaper for steady load.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is an ACU?
A1: Aurora Capacity Unit, a bundle of compute and memory that serverless scales in.

Q2: [Medium] Best use case?
A2: Dev/test, variable or unpredictable traffic, multi-tenant with idle periods.

Q3: [Hard] Cold-start after auto-pause breaks your API timeouts. Fix?
A3: Keep a minimum capacity above zero in prod, add connection retries, or use provisioned for latency-critical paths.

---

## ✅ Quick Checklist
□ Min/Max ACU set
□ Billing alarm on
□ Connection pool tolerates scaling and resume

---

## ⚡ 1-Line Summary
Serverless v2 = pay for ACUs used, scaling automatically. | Serverless v2 = इस्तेमाल हुए ACU का भुगतान, ऑटोमैटिक स्केलिंग।

## ➡️ Next: DynamoDB - Complete Guide

---
