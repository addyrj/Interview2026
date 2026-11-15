# 225. Azure Database for PostgreSQL
# AWS: RDS for PostgreSQL / Aurora PostgreSQL
# Azure: Azure Database for PostgreSQL - Flexible Server
# हिंदी में: Azure का मैनेज्ड PostgreSQL, बैकअप, पैचिंग और HA अपने-आप

---

## 🔵 Simple Definition (2 lines)
A managed PostgreSQL service (Flexible Server) that handles backups, patching, HA and scaling while you keep full Postgres compatibility.
हिंदी: आप सिर्फ़ SQL और ऐप पर ध्यान दें, सर्वर की देखभाल Azure करता है।

---

## 🔴 Why it Exists (2 lines)
Running Postgres on a VPS means you own backups, failover, upgrades and security.
Managed service gives point-in-time restore, zone-redundant HA and private networking out of the box.

---

## 🟢 How it Works
```
FastAPI/NestJS (App Service / Container Apps / VPS)
        |  TLS (sslmode=require), port 5432
        v
Flexible Server (Burstable | General Purpose | Memory Optimized)
   |-- Primary (AZ1) <-sync-> Standby (AZ2)   [zone-redundant HA, optional]
   |-- Read replicas (async)
   |-- Automated backups (PITR, retention configurable)
Access: public (firewall rules) or private (VNet integration)
Note: the older "Single Server" has been retired; use Flexible Server.
```

---

## 💻 Code / Config Example
```bash
az postgres flexible-server create \
  --resource-group rg-app --name myapp-pg --location centralindia \
  --admin-user pgadmin --admin-password "$PG_PASSWORD" \
  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 16 \
  --public-access 0.0.0.0     # dev only; prefer VNet/private access in prod
az postgres flexible-server db create -g rg-app -s myapp-pg -d appdb
```
```python
# FastAPI + SQLAlchemy connection string
# DATABASE_URL=postgresql+psycopg://pgadmin:***@myapp-pg.postgres.database.azure.com:5432/appdb?sslmode=require
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
with engine.connect() as c:
    print(c.execute(text("select version()")).scalar())
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | RDS PostgreSQL / Aurora | Flexible Server |
| HA | Multi-AZ | Zone-redundant HA |
| Extensions | Supported list | Allow-list via server parameter |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Opening the firewall to 0.0.0.0-255.255.255.255.
✅ Correct: Use VNet integration or Private Endpoint, and specific IP rules.

❌ Mistake: No connection pooling from many app replicas.
✅ Correct: Use the built-in PgBouncer option or an app-side pool.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which Postgres deployment option should new projects use?
A1: Flexible Server (Single Server is retired).

Q2: [Medium] How do you get HA and DR?
A2: Zone-redundant HA for in-region failover, read replicas or geo-redundant backup for cross-region recovery.

Q3: [Hard] Slow queries after migration from VPS?
A3: Check pg_stat_statements/Query Performance Insight, missing indexes, connection storms (pooling), IOPS tied to storage size, and region latency between app and DB.

---

## ✅ Quick Checklist
□ sslmode=require, secrets in Key Vault
□ Private access, HA enabled for prod
□ PITR retention and restore tested

---

## ⚡ 1-Line Summary
Managed Postgres with HA and PITR | HA और PITR वाला मैनेज्ड Postgres

## ➡️ Next: Azure Database for MySQL

---
