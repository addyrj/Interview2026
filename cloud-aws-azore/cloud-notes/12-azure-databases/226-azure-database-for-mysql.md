# 226. Azure Database for MySQL
# AWS: RDS for MySQL / Aurora MySQL
# Azure: Azure Database for MySQL - Flexible Server
# हिंदी में: Azure का मैनेज्ड MySQL, अपने-आप बैकअप और HA

---

## 🔵 Simple Definition (2 lines)
Managed MySQL (community edition) with automated backups, patching, optional zone-redundant HA and read replicas.
हिंदी: MySQL चलाने की सारी ऑपरेशनल मेहनत Azure संभालता है।

---

## 🔴 Why it Exists (2 lines)
WordPress, Laravel and many legacy apps need MySQL, and self-hosting adds backup and failover burden.
Flexible Server gives control over maintenance windows and server parameters.

---

## 🟢 How it Works
```
App --TLS 3306--> MySQL Flexible Server
                    |-- Primary + Standby (zone-redundant HA, optional)
                    |-- Read replicas
                    |-- Backups (PITR)
 require_secure_transport = ON (default) -> use SSL in the client
```

---

## 💻 Code / Config Example
```bash
az mysql flexible-server create \
  --resource-group rg-app --name myapp-mysql --location centralindia \
  --admin-user dbadmin --admin-password "$MYSQL_PASSWORD" \
  --tier Burstable --sku-name Standard_B1ms --storage-size 32 --version 8.0.21
az mysql flexible-server db create -g rg-app -s myapp-mysql -d appdb
```
```javascript
// Node.js (mysql2) with TLS
const mysql = require("mysql2/promise");
async function main() {
  const conn = await mysql.createConnection({
    host: "myapp-mysql.mysql.database.azure.com",
    user: "dbadmin", password: process.env.MYSQL_PASSWORD, database: "appdb",
    ssl: { rejectUnauthorized: true },   // add the CA bundle if your OS lacks it
  });
  const [rows] = await conn.query("SELECT VERSION() AS v");
  console.log(rows);
  await conn.end();
}
main();
```

---

## 📊 AWS vs Azure Quick Compare
| Feature | AWS | Azure |
|---------|-----|-------|
| Service | RDS MySQL / Aurora MySQL | MySQL Flexible Server |
| HA | Multi-AZ | Zone-redundant / same-zone HA |
| Cloud-native engine | Aurora | N/A (community MySQL only) |
| Pricing | Approximate — check current docs | Approximate — check current docs |

---

## ⚠️ Common Mistakes
❌ Mistake: Disabling SSL to "fix" connection errors.
✅ Correct: Supply the CA certificate and keep require_secure_transport ON.

❌ Mistake: Using a Burstable tier for steady production load.
✅ Correct: Use General Purpose; Burstable credits get exhausted.

---

## ⚫ Interview Q&A (3 questions)
Q1: [Easy] Which MySQL versions does it offer?
A1: Community MySQL 5.7 (legacy) and 8.x; check the docs for what is currently supported.

Q2: [Medium] How do you scale reads?
A2: Add read replicas and route read-only queries from the app.

Q3: [Hard] Migrate a VPS MySQL with minimal downtime?
A3: Use Azure Database Migration Service or replication (binlog / data-in replication), sync, then cut over DNS/connection string and verify.

---

## ✅ Quick Checklist
□ SSL enforced, CA configured
□ HA + backups configured
□ Parameters (max_connections, timezone) reviewed

---

## ⚡ 1-Line Summary
Managed community MySQL with HA | HA वाला मैनेज्ड MySQL

## ➡️ Next: Azure Cache for Redis

---
