---

# Q167. Elastic Pools and Scaling
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (Azure SQL Database). MySQL/PostgreSQL managed services scale compute per server; there is no elastic pool concept across databases.

---

## ❓ Question
Your SaaS has 200 tenant databases. Most are idle, a few spike at month-end. Explain when an elastic pool is cheaper than single databases, how to move a database into a pool, how to scale up/down with T-SQL, and what your Node.js app must tolerate while scaling.

---

## 💡 Quick Concept (2 lines only)
An elastic pool shares one set of resources (eDTUs or vCores) among many databases whose peaks do not coincide, so you pay for the pool, not for each database's worst case. Scaling a database or pool is an online operation, but connections are dropped briefly at the end of it.
हिंदी: Elastic pool = बहुत databases के बीच shared resources। Peaks अलग-अलग समय पर हों तो सस्ता। Scale करते समय connection थोड़ी देर टूटता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER / AZURE (no Azure instance available here).
-- Syntax parsed with sqlglot (tsql); behaviour per Microsoft docs.
-- ============================================

-- Which tier / pool is each database on? (run in master or in a database)
SELECT d.name, dso.edition, dso.service_objective, dso.elastic_pool_name
FROM sys.databases AS d
JOIN sys.database_service_objectives AS dso
  ON dso.database_id = d.database_id;
-- Expected per docs: elastic_pool_name is NULL for single databases and the pool name for pooled ones.

-- Move a single database into an existing pool (run in master)
ALTER DATABASE [tenant_0042]
  MODIFY (SERVICE_OBJECTIVE = ELASTIC_POOL(name = [pool-tenants]));

-- Move it back out to a standalone size
ALTER DATABASE [tenant_0042]
  MODIFY (SERVICE_OBJECTIVE = 'S3');

-- Scale a single DB up before a known peak (DTU model example; vCore uses names like 'GP_Gen5_4')
ALTER DATABASE [ShopDb] MODIFY (SERVICE_OBJECTIVE = 'S4');

-- Scaling is asynchronous: check progress/result
SELECT TOP (3) * FROM sys.dm_operation_status ORDER BY start_time DESC;
-- Expected per docs: rows showing operation, state_desc and percent_complete (values vary).

-- Pool size / per-database min-max settings are changed via portal/CLI:
--   az sql elastic-pool update -g rg-saas -s sql-saas-prod -n pool-tenants ^
--       --capacity 200 --db-min-capacity 0 --db-max-capacity 50
```

```javascript
// Node.js: scale-up causes a short connection drop -> retry transient errors with backoff
async function withRetry(fn, attempts = 5) {
  for (let i = 1; ; i++) {
    try { return await fn(); }
    catch (err) {
      if (i >= attempts || !['ECONNCLOSED', 'ESOCKET', 'ETIMEOUT'].includes(err.code)) throw err;
      await new Promise(r => setTimeout(r, 2 ** i * 200));   // 400ms, 800ms, ...
    }
  }
}
```

---

## 🔍 Why This Works (3 lines max)
Pools win when the sum of individual peaks is much higher than the pool's peak, because tenants rarely spike together. Per-database min/max settings stop one noisy tenant from starving others or being starved. Scale operations copy/attach underneath, so the switchover is quick but not zero, hence the retry logic.
हिंदी: Sab tenants एक साथ peak नहीं करते, इसलिए pool सस्ता। Per-DB max noisy neighbour को रोकता है। Scale के बाद retry ज़रूरी।

---

## ⚡ Alternative Solution

```sql
-- Serverless compute tier (single DB): auto-scales between min/max vCores and can auto-pause when idle.
-- Good for dev/test or spiky low-traffic DBs; the first connection after pause is slow
-- (resume delay), so the app needs a longer connect timeout.
-- Hyperscale: storage-heavy workloads, fast scale and read replicas (different trade-offs).
-- Choose: steady load -> provisioned single DB; many idle tenants -> pool; sporadic single DB -> serverless.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: putting databases with synchronized peaks (all tenants run billing at 1st of month)
--    into one pool. The pool saturates and everyone slows down together.
-- ❌ Wrong: no per-database max in a pool, so one runaway tenant takes all eDTUs/vCores.
-- ❌ Wrong: scaling up to hide a missing index. Fix the query first (see Q180), then size.
-- ❌ Wrong: scaling during peak hours without retry logic in the app.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I decide with data: DTU/CPU percentages per database over weeks from Azure Monitor and `sys.dm_db_resource_stats`, check whether peaks overlap, then pick pool, serverless or single. I always set per-database limits, scale ahead of known peaks, and make the app retry transient connection errors." Mention that pooling per-tenant databases also eases per-tenant restore and data isolation compared with one shared database.

---

## 🔗 Related Questions
→ Q158 (DTU vs vCore) | Q157 (Azure SQL DB vs MI vs VM) | Q168 (Azure SQL monitoring) | Q160 (pooling and retries) | Q156 (monitoring and baselines)
