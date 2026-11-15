---

# 220. Azure SQL vs AWS RDS
# AWS: Amazon RDS (SQL Server, MySQL, PostgreSQL, Aurora...)
# Azure: Azure SQL Database / Managed Instance / Azure Database for PostgreSQL & MySQL
# हिंदी में: दोनों cloud के managed databases की तुलना

---

## 🔵 Simple Definition (2 lines)
Both are managed relational DB services; RDS is one service with many engines, Azure splits them into separate services per engine.
हिंदी: दोनों managed relational database हैं; RDS एक service में कई engines देता है, Azure हर engine की अलग service रखता है।

---

## 🔴 Why it Exists (2 lines)
Teams choosing a cloud must map DB options, HA models and cost drivers across providers.
Knowing the mapping avoids wrong sizing and migration surprises.

---

## 🟢 How it Works
```
Engine           AWS                          Azure
SQL Server       RDS for SQL Server           Azure SQL Database / Managed Instance
PostgreSQL       RDS PostgreSQL / Aurora PG   Azure Database for PostgreSQL - Flexible Server
MySQL            RDS MySQL / Aurora MySQL     Azure Database for MySQL - Flexible Server
HA               Multi-AZ standby             Zone-redundant HA (Flexible Server / SQL tiers)
Read scale       Read replicas                Read replicas / Hyperscale named replicas
```

---

## 💻 Code / Config Example
```bash
# AWS: RDS PostgreSQL, Multi-AZ
aws rds create-db-instance --db-instance-identifier api-db \
  --engine postgres --db-instance-class db.t3.micro --allocated-storage 20 \
  --master-username dbadmin --manage-master-user-password --multi-az

# Azure: PostgreSQL Flexible Server, zone-redundant HA
az postgres flexible-server create -g rg-demo -n api-pg-123 -l centralindia \
  --tier GeneralPurpose --sku-name Standard_D2s_v3 \
  --admin-user dbadmin --admin-password 'REPLACE_WITH_STRONG_SECRET' \
  --high-availability ZoneRedundant
```
Instance class/SKU availability varies by region; check current docs.

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Packaging | One service (RDS) many engines | Separate service per engine |
| HA | Multi-AZ | Zone-redundant HA / built-in SQL HA |
| Serverless | Aurora Serverless v2 | SQL DB serverless; PG Flexible has none comparable |
| Backups | Automated snapshots, PITR | Automated, PITR (retention configurable) |
| Auth | IAM DB auth, Secrets Manager | Entra ID auth, Key Vault |
| Pricing | Instance + storage + IOPS (approximate — check current docs) | vCore/DTU + storage (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Assuming Azure SQL DB equals full SQL Server instance.
✅ Correct: Use Managed Instance when you need SQL Agent, cross-DB queries, CLR.

❌ Mistake: Comparing only list prices.
✅ Correct: Include HA replicas, backup storage, licensing and egress.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] RDS equivalent in Azure? A1: Azure SQL Database or Azure Database for PostgreSQL/MySQL, depending on engine.
Q2: [Medium] Multi-AZ equivalent? A2: Zone-redundant high availability.
Q3: [Hard] Migrating RDS PostgreSQL to Azure? A3: Use pg_dump/restore for small, or Azure Database Migration Service / logical replication for near-zero downtime; then switch connection strings and test extensions compatibility.

---

## ✅ Quick Checklist
□ Engine mapped to right Azure service
□ HA mode chosen
□ Private networking planned
□ Cost compared incl. backups/egress

---

## ⚡ 1-Line Summary
RDS is one multi-engine service; Azure has one service per engine | RDS एक multi-engine service है, Azure में हर engine की अलग service है।

## ➡️ Next: 221. Azure Database for PostgreSQL / MySQL

---
