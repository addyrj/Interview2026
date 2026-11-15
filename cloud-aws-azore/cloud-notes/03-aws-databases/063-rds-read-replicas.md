# 63. RDS READ REPLICAS
# AWS: RDS Read Replicas
# Azure: Read replicas (Azure Database for PostgreSQL/MySQL Flexible Server)
# हिंदी में: रीड रेप्लिका से पढ़ने का लोड बाँटना

---

## 🔵 Simple Definition (2 lines)
A read replica is an asynchronously updated copy of the primary that serves SELECT queries only.
हिंदी: रीड रेप्लिका प्राइमरी की एसिंक्रोनस कॉपी है जो सिर्फ़ पढ़ने के क्वेरी चलाती है।

---

## 🔴 Why it Exists (2 lines)
Reporting and read-heavy traffic slows the primary that also takes writes.
Replicas scale reads horizontally and can live in another Region for DR or lower latency.

---

## 🟢 How it Works
```
 writes --> PRIMARY ==async replication==> REPLICA-1 (own endpoint)
 reads  -------------------------------> REPLICA-2 (own endpoint)
 NestJS: write pool -> primary, read pool -> replica
 Lag: replica can be seconds behind -> monitor ReplicaLag metric
 Disaster: promote replica -> becomes standalone writable DB
```

---

## 💻 Code / Config Example
```bash
# Create a replica (AWS CLI v2)
aws rds create-db-instance-read-replica \
  --db-instance-identifier app-pg-ro1 \
  --source-db-instance-identifier app-pg

# Promote it in an emergency
aws rds promote-read-replica --db-instance-identifier app-pg-ro1
```
```python
# FastAPI/SQLAlchemy: split read and write engines
from sqlalchemy import create_engine
writer = create_engine("postgresql://u:p@app-pg.xxxx.rds.amazonaws.com/app")
reader = create_engine("postgresql://u:p@app-pg-ro1.xxxx.rds.amazonaws.com/app")
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Replication | Async (engine native) | Async (engine native) |
| Max replicas | Up to 15 for MySQL/PostgreSQL/MariaDB (approximate - check current docs) | Around 5-10 depending on engine (approximate - check current docs) |
| Cross-region | Yes | Yes |
| Pricing | Billed like a full instance | Billed like a full server |

---

## ⚠️ Common Mistakes
❌ Mistake: Reading your own write immediately from a replica.
✅ Correct: Read-after-write goes to the primary, or tolerate lag.

❌ Mistake: Treating a replica as HA.
✅ Correct: Use Multi-AZ for HA; promotion is manual and may lose recent writes.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is a read replica for?
A1: Offloading read queries from the primary.

Q2: [Medium] Why might a user not see data they just saved?
A2: Async replication lag; the read hit a replica that is behind.

Q3: [Hard] Design read scaling for an analytics-heavy API.
A3: Replicas per workload, route reports to a dedicated replica, monitor ReplicaLag, cache hot queries in Redis, and use a cross-region replica for DR.

---

## ✅ Quick Checklist
□ App routes reads and writes separately
□ ReplicaLag alarm set
□ Replica SG allows only app tier

---

## ⚡ 1-Line Summary
Read replicas scale reads asynchronously; they are not HA. | रीड रेप्लिका रीड स्केल करती हैं (एसिंक); यह HA का विकल्प नहीं है।

## ➡️ Next: RDS Backup + Snapshots

---
