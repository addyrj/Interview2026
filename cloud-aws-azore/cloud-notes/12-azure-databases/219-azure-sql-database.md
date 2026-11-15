---

# 219. Azure SQL Database
# AWS: Amazon RDS for SQL Server (closest) / Aurora
# Azure: Azure SQL Database
# हिंदी में: Microsoft SQL Server का fully managed cloud version

---

## 🔵 Simple Definition (2 lines)
Azure SQL Database is a fully managed PaaS relational database based on the SQL Server engine with built-in HA, backups and patching.
हिंदी: Azure SQL Database SQL Server पर आधारित fully managed database है, जिसमें backup, patching और HA अपने-आप होता है।

---

## 🔴 Why it Exists (2 lines)
Running SQL Server yourself means patching, backups and failover work.
PaaS gives pay-as-you-go scaling, point-in-time restore and 99.99% SLA options (verify tier SLA in docs).

---

## 🟢 How it Works
```
Logical server (myserver.database.windows.net) -> databases
   Purchase: vCore (General Purpose / Business Critical / Hyperscale) or DTU
   Serverless compute auto-pauses when idle (General Purpose)
   Backups: automatic, PITR (default retention approx 7 days, configurable)
   Network: firewall rules / Private Endpoint; auth: SQL login or Entra ID
```

---

## 💻 Code / Config Example
```bash
az sql server create -g rg-demo -n myapisql123 -l centralindia \
  --admin-user sqladmin --admin-password 'REPLACE_WITH_STRONG_SECRET'

az sql db create -g rg-demo -s myapisql123 -n appdb \
  --edition GeneralPurpose --family Gen5 --capacity 2 \
  --compute-model Serverless --auto-pause-delay 60

# Allow only your IP (documentation address)
az sql server firewall-rule create -g rg-demo -s myapisql123 -n office \
  --start-ip-address 203.0.113.10 --end-ip-address 203.0.113.10
```
```js
// Node.js (npm i mssql)
const sql = require('mssql');
const pool = await sql.connect({
  server: 'myapisql123.database.windows.net',
  database: 'appdb', user: 'sqladmin', password: process.env.DB_PASS,
  options: { encrypt: true }
});
console.log((await pool.request().query('SELECT 1 AS ok')).recordset);
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | RDS for SQL Server | Azure SQL Database |
| Serverless | Aurora Serverless (MySQL/PG only) | SQL DB serverless |
| Engine access | Near full SQL Server (instance) | Database-scoped (use Managed Instance for full) |
| Pricing | Instance-hour + storage (approximate — check current docs) | vCore/DTU + storage (approximate — check current docs) |

---

## ⚠️ Common Mistakes
❌ Mistake: Opening firewall to 0.0.0.0-255.255.255.255.
✅ Correct: Use specific IPs, VNet rules or Private Endpoint.

❌ Mistake: Password auth in code.
✅ Correct: Entra ID managed identity token auth where possible.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] What is Azure SQL Database? A1: Managed SQL Server-engine database PaaS.
Q2: [Medium] vCore vs DTU? A2: vCore lets you pick CPU/memory/storage separately; DTU is a bundled blended unit.
Q3: [Hard] SQL Database vs Managed Instance vs SQL on VM? A3: DB is single-database PaaS; MI has near-full SQL Server compatibility (agent, cross-db); VM gives full OS control with your own ops.

---

## ✅ Quick Checklist
□ Firewall/Private Endpoint
□ Entra ID auth
□ Backup retention reviewed
□ Serverless auto-pause for dev

---

## ⚡ 1-Line Summary
Azure SQL Database is managed SQL Server in the cloud | Azure SQL Database cloud में managed SQL Server है।

## ➡️ Next: 220. Azure SQL vs AWS RDS

---
