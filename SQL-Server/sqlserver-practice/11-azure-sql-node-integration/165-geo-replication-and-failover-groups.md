---

# Q165. Geo-Replication and Failover Groups
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (Azure SQL Database). MySQL/PostgreSQL: read replicas / cross-region replicas exist but have no failover-group listener equivalent in the same form.

---

## ❓ Question
Your order system runs in Central India and must survive a regional outage. Compare active geo-replication with auto-failover groups, show how to set them up, and show how the Node.js app should connect so a failover does not need a code change.

---

## 💡 Quick Concept (2 lines only)
Active geo-replication = asynchronous readable secondary(ies) of a single database in another region, failed over per database. An auto-failover group wraps one or more databases on a server pair and gives two stable listener DNS names (read-write and read-only), so apps keep the same connection string after failover.
हिंदी: Geo-replication = दूसरे region में async copy। Failover group = listener endpoint, तो failover के बाद भी connection string वही रहती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER / AZURE (no Azure instance available here).
-- Syntax parsed with sqlglot (tsql); behaviour per Microsoft docs.
-- ============================================

-- ACTIVE GEO-REPLICATION: run on the PRIMARY server's master database
ALTER DATABASE ShopDb
  ADD SECONDARY ON SERVER [sql-shop-southindia]
  WITH (ALLOW_CONNECTIONS = ALL);

-- Manual planned failover: run on the SECONDARY database (no data loss when in sync)
ALTER DATABASE ShopDb FAILOVER;

-- Forced failover (disaster; async replication means recent commits CAN be lost)
ALTER DATABASE ShopDb FORCE_FAILOVER_ALLOW_DATA_LOSS;

-- Monitor replication state (run in the primary database)
SELECT * FROM sys.dm_geo_replication_link_status;
-- Expected per docs: one row per replica link, with replication lag and state columns.
-- Exact columns: check your Azure SQL version; not reproduced here.

-- AUTO-FAILOVER GROUP is created via portal / CLI / PowerShell, not T-SQL:
--   az sql failover-group create --name fog-shop --resource-group rg-shop ^
--       --server sql-shop-centralindia --partner-server sql-shop-southindia ^
--       --add-db ShopDb --failover-policy Automatic --grace-period 1
-- Listener endpoints (per docs):
--   fog-shop.database.windows.net            -> always the current PRIMARY (read-write)
--   fog-shop.secondary.database.windows.net  -> always the current SECONDARY (read-only)
```

```javascript
// Node.js: connect to the listener, not to an individual server
const sql = require('mssql');

const writePool = await new sql.ConnectionPool({
  server: 'fog-shop.database.windows.net',
  database: 'ShopDb',
  authentication: { type: 'azure-active-directory-default' },
  options: { encrypt: true }
}).connect();

// Reporting/read-only traffic: secondary listener or ApplicationIntent=ReadOnly
const reportPool = await new sql.ConnectionPool({
  server: 'fog-shop.database.windows.net',
  database: 'ShopDb',
  authentication: { type: 'azure-active-directory-default' },
  options: { encrypt: true, readOnlyIntent: true }   // read-only routing (Business Critical / Premium)
}).connect();
```

---

## 🔍 Why This Works (3 lines max)
Replication is asynchronous, so the primary does not wait for the secondary: low commit latency but a non-zero RPO on forced failover. The failover group repoints its listener DNS names to whichever server is primary, so the app needs no change, only reconnect logic. Logins/users must exist on both sides (contained Entra users replicate with the database; server-level logins do not).
हिंदी: Async copy = commit fast, पर disaster में थोड़ा data loss possible (RPO > 0)। Listener DNS बदलता है, app code नहीं।

---

## ⚡ Alternative Solution

```sql
-- Same-region high availability is separate: zone-redundant configuration protects against a
-- datacenter/zone failure inside one region, with no manual failover.
-- Geo-replication/failover groups protect against a whole REGION failure.
-- Cheapest DR option: geo-restore from geo-redundant backups (higher RPO/RTO, hours not minutes).
-- Check which you actually need from the business RTO/RPO, not from the feature list.
```

---

## ⚠️ Common Mistake

```javascript
// ❌ Wrong: hard-coding the primary server name in the connection string
//    server: 'sql-shop-centralindia.database.windows.net'  -> breaks after failover
// ✅ Use the failover-group listener name.

// ❌ Wrong: no retry logic. During failover, existing connections drop and new ones fail
//    briefly (transient errors). Pool must discard dead connections and retry with backoff.
// ❌ Wrong: forgetting that the DNS TTL / client DNS cache can delay the switch for a short time.
// ❌ Wrong: never testing a failover drill -- do it in a maintenance window before you need it.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I start from RTO and RPO. Failover groups give me listener endpoints and group-level failover for several databases, and replication is async, so I accept a small RPO. The app connects to the listener with transient-fault retry, long-running work is idempotent, and we run a failover drill each quarter." Note that failover groups are for a database set that must fail over together, and that a forced failover can lose recent commits.

---

## 🔗 Related Questions
→ Q166 (backup, PITR and LTR) | Q160 (pooling and retries with mssql) | Q130 (retry logic for deadlock victims) | Q157 (Azure SQL DB vs MI vs VM) | Q156 (monitoring and baselines)
