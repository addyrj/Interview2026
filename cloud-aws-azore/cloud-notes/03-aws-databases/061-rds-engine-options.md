# 61. RDS ENGINE OPTIONS
# AWS: Amazon RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2) + Aurora
# Azure: Azure Database for MySQL / PostgreSQL (Flexible Server), Azure SQL Database / Managed Instance
# हिंदी में: RDS में कौन-सा डेटाबेस इंजन चुनें

---

## 🔵 Simple Definition (2 lines)
RDS is a managed relational database: AWS handles patching, backups, failover and hardware, you handle schema and queries.
हिंदी: RDS एक मैनेज्ड डेटाबेस है जिसमें पैचिंग, बैकअप और फेलओवर AWS संभालता है।

---

## 🔴 Why it Exists (2 lines)
Running Postgres/MySQL on a VPS means you own backups, upgrades, replication and 3 AM failures.
RDS removes that ops work; the engine choice decides features, licence cost and portability.

---

## 🟢 How it Works
```
Engine choice
  Open source  -> PostgreSQL, MySQL, MariaDB   (no licence fee, most startups)
  Commercial   -> Oracle, SQL Server, Db2      (licence included or BYOL)
  Cloud-native -> Aurora MySQL / Aurora PG     (see notes 67-69)

App (NestJS/FastAPI) --TCP 5432--> RDS endpoint (DNS name, never a fixed IP)
                                      |
                              DB instance class (db.t4g.micro ... db.r6g.*)
                              + EBS storage (gp3 / io1 / io2)
```

---

## 💻 Code / Config Example
```bash
# Create a small PostgreSQL RDS instance (AWS CLI v2)
aws rds create-db-instance \
  --db-instance-identifier app-pg \
  --engine postgres \
  --db-instance-class db.t4g.micro \
  --allocated-storage 20 \
  --storage-type gp3 \
  --master-username appadmin \
  --manage-master-user-password \
  --backup-retention-period 7 \
  --no-publicly-accessible
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Postgres | RDS for PostgreSQL | Azure Database for PostgreSQL Flexible Server |
| MySQL | RDS for MySQL | Azure Database for MySQL Flexible Server |
| SQL Server | RDS for SQL Server | Azure SQL Database / Managed Instance |
| Oracle | RDS for Oracle | N/A as managed service (Oracle Database@Azure is separate) |
| Pricing | Instance-hours + storage + IO (approximate - check current docs) | vCore/compute + storage (approximate - check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Picking SQL Server/Oracle "because the team knows it" and paying licence cost.
✅ Correct: Default to PostgreSQL unless you have a hard compatibility need.

❌ Mistake: Hard-coding the IP of the DB.
✅ Correct: Always use the endpoint DNS name; it changes target on failover.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which engines does RDS support?
A1: MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2, plus Aurora (MySQL/PostgreSQL compatible).

Q2: [Medium] RDS or self-managed Postgres on EC2?
A2: RDS for managed backups, Multi-AZ, patching. EC2 only if you need superuser/OS access or unsupported extensions.

Q3: [Hard] What do you lose with RDS compared to a VPS install?
A3: No OS/SSH access, no superuser (rds_superuser instead), only allow-listed extensions, and parameters changed via parameter groups.

---

## ✅ Quick Checklist
□ Engine matches app ORM/driver (TypeORM, SQLAlchemy)
□ Not publicly accessible; SG allows only the app
□ Backups and storage autoscaling decided

---

## ⚡ 1-Line Summary
Pick PostgreSQL on RDS by default; engine choice drives cost and features. | डिफ़ॉल्ट रूप से RDS पर PostgreSQL चुनें; इंजन से लागत और फ़ीचर तय होते हैं।

## ➡️ Next: RDS Multi-AZ

---
