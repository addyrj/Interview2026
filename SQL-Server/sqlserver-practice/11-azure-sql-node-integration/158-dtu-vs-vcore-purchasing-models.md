---

# Q158. DTU vs vCore Purchasing Models
# Category: AZURE SQL + NODE.JS INTEGRATION
# Difficulty: ⭐⭐ Medium
# DB: Azure SQL Database (not applicable on-prem; MySQL/PostgreSQL managed services use vCore-style sizing)

---

## ❓ Question
Explain DTU and vCore purchasing models for Azure SQL Database, how to choose, how to scale a database between tiers with T-SQL, and what you monitor to decide it is undersized.

---

## 💡 Quick Concept (2 lines only)
DTU is a bundled, opaque blend of CPU, memory and I/O in tiers (Basic/Standard/Premium) — simple but coarse. vCore lets you choose compute, memory and storage separately (General Purpose, Business Critical, Hyperscale; provisioned or serverless) and supports Azure Hybrid Benefit and reserved capacity.
हिंदी: DTU = CPU+memory+IO का एक पैकेज, आसान पर कम पारदर्शी। vCore = अलग-अलग चुनाव, serverless/Hybrid Benefit/reservation का फ़ायदा; production में आम तौर पर यही पसंद है।

---

## ✅ Answer / Solution

NOTE: Azure-specific; not executed on SQL Server. Tier names, limits and pricing change - verify in current docs. No result sets are shown.

```sql
-- ============================================
-- CURRENT SIZE / TIER
-- ============================================
SELECT DATABASEPROPERTYEX(DB_NAME(), 'Edition')          AS Edition,
       DATABASEPROPERTYEX(DB_NAME(), 'ServiceObjective') AS ServiceObjective;

-- ============================================
-- SCALE UP / DOWN (online operation; brief connection drop possible at the switch -> retry logic, Q160)
-- ============================================
ALTER DATABASE OrdersDb MODIFY (EDITION = 'Standard', SERVICE_OBJECTIVE = 'S3');       -- DTU model
ALTER DATABASE OrdersDb MODIFY (EDITION = 'GeneralPurpose', SERVICE_OBJECTIVE = 'GP_Gen5_4'); -- vCore model

-- ============================================
-- IS IT UNDERSIZED? recent resource usage (about 1 hour at 15 s granularity, per docs)
-- ============================================
SELECT TOP (20) end_time, avg_cpu_percent, avg_data_io_percent, avg_log_write_percent
FROM sys.dm_db_resource_stats
ORDER BY end_time DESC;
-- Sustained values near 100% in any column = that resource is the limiter.
-- Longer history: sys.resource_stats (master db) or Azure Monitor metrics.
```

| | DTU | vCore |
|---|---|---|
| Unit | blended DTUs | vCores + GB RAM tied to generation + storage |
| Transparency | low | high |
| Serverless / auto-pause | no | yes (General Purpose) |
| Hybrid Benefit, reservations | no | yes |
| Hyperscale | no | yes |
| Good for | small/simple, predictable workloads | most production, cost optimisation |

---

## 🔍 Why This Works (3 lines max)
Both models bill for reserved capacity; the question is how much control and transparency you need. `sys.dm_db_resource_stats` shows which dimension (CPU, data I/O, log) is saturating, which tells you whether to scale up, tune queries, or change tier.
हिंदी: दोनों में reserved capacity का पैसा लगता है। कौन-सा resource 100% छू रहा है यह `sys.dm_db_resource_stats` बताता है, तभी scale करो या query tune करो।

---

## ⚡ Alternative Solution

```sql
-- Serverless vCore for spiky/dev workloads: compute auto-scales between min/max vCores and can auto-pause
-- (configured via portal/CLI/ARM, not T-SQL). Many small databases with uneven peaks -> elastic pool (Q167).
-- Cheaper than scaling: fix the top CPU queries first (Query Store, Q142).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: scaling up to hide a missing index (cost grows every month, problem stays)
-- ❌ Wrong: assuming DTU numbers map 1:1 to vCores across tiers
-- ❌ Wrong: running scale operations during peak without retry-capable clients
-- ❌ Wrong: forgetting the log-rate / max-sessions / max-workers limits are tied to the tier
-- ✅ Right: measure (resource stats, Query Store), tune, then size; revisit after each release
```

---

## 🎯 Interview Tip (1 line)
Say: "DTU is a bundled shortcut; I prefer vCore for visibility and levers like serverless, Hybrid Benefit and reservations. Before scaling I check which resource is saturated and whether a query/index fix is cheaper, and I make the app tolerate the brief reconnect that a tier change can cause."

---

## 🔗 Related Questions
→ Q157 (Azure SQL flavours) | Q167 (Elastic pools and scaling) | Q168 (Azure SQL monitoring) | Q160 (Pooling and retries)
