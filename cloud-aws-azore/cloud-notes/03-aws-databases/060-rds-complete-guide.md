# 60. RDS — Complete Guide
# AWS: Amazon RDS (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server; Aurora separately)
# Azure: Azure Database for PostgreSQL / MySQL Flexible Server (Azure SQL for SQL Server)
# हिंदी में: मैनेज्ड रिलेशनल डेटाबेस — बैकअप, पैचिंग, फेलओवर AWS संभालता है

---

## 🔵 Simple Definition (2 lines)
RDS runs a relational database for you: provisioning, backups, patching, monitoring and Multi-AZ failover are managed.
आप सिर्फ डेटा और क्वेरी संभालो; सर्वर, बैकअप और पैचिंग AWS देखता है।

---

## 🔴 Why it Exists (2 lines)
Self-hosting a DB on a VPS means you own backups, upgrades, replication and 3 a.m. outages.
RDS removes that toil, though you still manage schema, queries and tuning (no OS/SSH access).

---

## 🟢 How it Works
```
App (ECS/EC2, private subnet) --5432--> RDS endpoint
  Primary (AZ-a) ==sync standby==> Standby (AZ-b)   [Multi-AZ, auto failover]
  Read replicas (async) for read scaling
  Automated backups (retention 0-35 days) + PITR, manual snapshots
  Storage: gp3 / io1/io2; encryption with KMS (set at creation)
  Access: DB subnet group + security group (only app SG on port 5432)
```

---

## 💻 Code / Config Example
```bash
# AWS CLI v2: PostgreSQL, Multi-AZ, encrypted, private
aws rds create-db-instance \
  --db-instance-identifier myapp-prod \
  --engine postgres \
  --db-instance-class db.t4g.medium \
  --allocated-storage 50 --storage-type gp3 \
  --master-username appadmin --manage-master-user-password \
  --multi-az --storage-encrypted \
  --no-publicly-accessible \
  --db-subnet-group-name private-db-subnets \
  --vpc-security-group-ids sg-0123456789abcdef0 \
  --backup-retention-period 7 \
  --deletion-protection
# --manage-master-user-password stores the password in Secrets Manager.
# Node.js/FastAPI: read secret, connect with SSL (sslmode=require).
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | RDS (Aurora is AWS's cloud-native engine) | Azure Database for PostgreSQL/MySQL Flexible Server |
| HA | Multi-AZ | Zone-redundant HA |
| Read scale | Read replicas | Read replicas |
| Backup | Automated up to 35 days + PITR | Automated, PITR (retention up to 35 days) |
| Pricing | instance hours + storage + IO + backups beyond DB size (approximate — check current docs) | compute + storage + backup (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Publicly accessible DB with 0.0.0.0/0 in the security group.
✅ Correct: Private subnets; allow only the app's security group.

❌ Mistake: Thinking Multi-AZ is a read replica or a backup.
✅ Correct: Multi-AZ is for availability; replicas for reads; backups for recovery.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What does RDS manage that EC2-hosted DB does not?
A1: Provisioning, OS and engine patching, backups, monitoring and automated failover.

Q2: [Medium] Multi-AZ vs read replica?
A2: Multi-AZ uses a synchronous standby for failover (not readable in the classic single-standby setup); read replicas are asynchronous and serve reads.

Q3: [Hard] App connections spike and RDS runs out of connections; fix?
A3: Use RDS Proxy or PgBouncer, pool in the app, right-size `max_connections`, and cap Lambda/ECS concurrency.

---

## ✅ Quick Checklist
□ Private subnets, SG from app only
□ Multi-AZ and backups enabled
□ Encryption + Secrets Manager password
□ Deletion protection and snapshots before changes

---

## ⚡ 1-Line Summary
RDS is a managed relational DB; you focus on data, AWS handles operations. | RDS मैनेज्ड डेटाबेस है — ऑपरेशन्स AWS का, डेटा आपका।

## ➡️ Next: RDS Multi-AZ and Read Replicas
