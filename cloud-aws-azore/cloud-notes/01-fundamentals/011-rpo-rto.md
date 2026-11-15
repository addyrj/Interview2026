---

# 11. RPO + RTO
# AWS: RDS PITR, AWS Backup, Elastic Disaster Recovery
# Azure: Azure SQL PITR, Azure Backup, Site Recovery
# हिंदी में: RPO = कितना डेटा खो सकते हैं, RTO = कितनी देर में वापस चालू करना है

---

## 🔵 Simple Definition (2 lines)
RPO (Recovery Point Objective) is the maximum acceptable data loss measured in time. RTO (Recovery Time Objective) is the maximum acceptable downtime.
हिंदी: RPO = पीछे कितने समय का डेटा खोना मंज़ूर, RTO = सर्विस वापस आने में कितना समय मंज़ूर।

---

## 🔴 Why it Exists (2 lines)
Without targets you cannot choose backup frequency or DR design, and cost becomes guesswork.
RPO/RTO translate business tolerance into technical requirements.

---

## 🟢 How it Works
```
 last good backup        disaster         service restored
        |<------ RPO ------>|<------ RTO ------>|
 ---------------------------X--------------------------> time
 data lost = up to RPO        downtime = up to RTO

 RPO 24h  -> daily backup OK
 RPO ~5m  -> continuous log backup / PITR / async replica
 RPO ~0   -> synchronous replication
 RTO min  -> warm standby/active-active, automated failover
```

---

## 💻 Code / Config Example
```bash
# AWS: restore an RDS instance to a point in time (shrinks data loss to ~minutes)
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier prod-db \
  --target-db-instance-identifier prod-db-restored \
  --restore-time 2026-11-09T10:15:00Z

# Azure: restore an Azure SQL database to a point in time
az sql db restore --resource-group demo-rg --server my-sql-server \
  --name proddb --dest-name proddb-restored --time "2026-11-09T10:15:00"
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| DB point-in-time restore | RDS PITR | Azure SQL / Flexible Server PITR |
| Backup retention default | Configurable (check docs) | Configurable (check docs) |
| Replication across regions | Aurora Global / read replicas | Geo-replication / failover groups |
| Pricing | Storage beyond free backup allowance (check docs) | Similar (check docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Mixing up RPO and RTO.
✅ Correct: P = Point (data), T = Time (downtime).

❌ Mistake: Promising RTO of 5 minutes while the restore takes 2 hours.
✅ Correct: Measure real restore time in drills.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does RPO of 15 minutes mean?
A1: You can lose at most the last 15 minutes of data.

Q2: [Medium] How does lower RPO/RTO affect cost?
A2: Cost rises sharply: more replication, standby capacity and automation.

Q3: [Hard] Design for RPO 1 min, RTO 15 min.
A3: Cross-region async replica (or global DB), infra as code for rapid environment bring-up, health-checked DNS failover, runbook plus regular failover tests.

---

## ✅ Quick Checklist
□ RPO/RTO agreed with business per system
□ Backup frequency matches RPO
□ Restore time measured

---

## ⚡ 1-Line Summary
RPO is data you can lose, RTO is time you can be down | RPO = खोने लायक डेटा, RTO = बंद रहने लायक समय।

## ➡️ Next: 12. SLA in Cloud

---
