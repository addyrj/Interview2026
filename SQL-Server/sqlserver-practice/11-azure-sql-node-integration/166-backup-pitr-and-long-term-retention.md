---

# Q166. Backup, PITR and Long-Term Retention
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (Azure SQL Database). On-prem SQL Server: you schedule BACKUP DATABASE yourself (see Q141). MySQL/PostgreSQL managed services also offer PITR but with their own retention rules.

---

## ❓ Question
Someone ran `DELETE FROM Orders` without a WHERE clause at 14:07 in production on Azure SQL Database. How do you recover? Explain automated backups, point-in-time restore (PITR), and long-term retention (LTR), and what you can and cannot do with them.

---

## 💡 Quick Concept (2 lines only)
Azure SQL takes automated full, differential and transaction-log backups for you; PITR restores to any second inside the retention window (default 7 days, configurable up to 35) as a NEW database. LTR keeps weekly/monthly/yearly full backups for compliance, up to 10 years.
हिंदी: Backup automatic है। PITR = किसी भी second पर restore, पर नया database बनता है। LTR = सालों तक compliance backup।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER / AZURE (no Azure instance available here).
-- Syntax parsed with sqlglot (tsql); behaviour per Microsoft docs.
-- ============================================

-- There is no BACKUP DATABASE to schedule in Azure SQL Database: it is managed.
-- Restore is done via portal / CLI / PowerShell, producing a NEW database:
--   az sql db restore --resource-group rg-shop --server sql-shop-prod ^
--       --name ShopDb --dest-name ShopDb_restore_1405 --time "2026-11-14T08:36:00Z"
--   (time is UTC; pick a moment just BEFORE the bad DELETE)

-- Step 1: confirm the damage in production
SELECT COUNT(*) AS OrderRows FROM dbo.Orders;     -- expected: 0 after the bad DELETE

-- Step 2: after restoring to ShopDb_restore_1405, copy rows back (cross-database queries are
-- not allowed in Azure SQL Database; use an external table / bcp / Data Factory / app code,
-- or swap the databases by renaming).
-- Option: rename-swap (needs an outage window; connection string name stays the same)
ALTER DATABASE ShopDb MODIFY NAME = ShopDb_damaged;      -- run in master
ALTER DATABASE ShopDb_restore_1405 MODIFY NAME = ShopDb; -- run in master

-- Check backup/restore history from master (view exists in Azure SQL DB; columns per docs)
SELECT TOP (5) * FROM sys.dm_database_backups;
-- Expected per docs: rows describing available backups; exact output depends on server.

-- LONG-TERM RETENTION policy (CLI; ISO 8601 durations):
--   az sql db ltr-policy set -g rg-shop -s sql-shop-prod -n ShopDb ^
--       --weekly P4W --monthly P12M --yearly P5Y --week-of-year 1
-- Set PITR retention days:
--   az sql db str-policy set -g rg-shop -s sql-shop-prod -n ShopDb --retention-days 14
```

```javascript
// Node.js: protect against the accident in the first place
// Wrap risky manual maintenance in an explicit transaction and verify before committing.
const tx = new sql.Transaction(pool);
await tx.begin();
const r = await new sql.Request(tx).query("DELETE FROM dbo.Orders WHERE Status = 'Cancelled'");
if (r.rowsAffected[0] > 10000) { await tx.rollback(); throw new Error('Unexpected row count'); }
await tx.commit();
```

---

## 🔍 Why This Works (3 lines max)
Full backups plus frequent log backups let the service replay the log to any chosen second, so you restore to just before the DELETE. The restore creates a separate database, which means production is untouched until you decide how to merge or swap. Backups also live in separate storage, so they survive a corrupted database.
हिंदी: Log replay से सही second तक जा सकते हैं। Restore नया DB बनाता है, production को नहीं छूता।

---

## ⚡ Alternative Solution

```sql
-- Deleted the whole database? Azure SQL keeps backups of a dropped database for its retention period:
--   az sql db list-deleted -g rg-shop -s sql-shop-prod
--   az sql db restore --deleted-time <value> ...
-- Prevent accidents: temporal tables (Q030) keep row history without any restore.
-- Cross-region recovery: geo-restore from geo-redundant backups (see Q165 for lower RPO).
-- Backup storage redundancy (LRS / ZRS / GRS) is chosen at database creation or changed later.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: believing PITR restores "in place". It never overwrites; it makes a new database,
--    so plan connection strings, permissions and the rename/swap step.
-- ❌ Wrong: assuming the default 7 days covers audit needs. Compliance usually means LTR.
-- ❌ Wrong: never testing a restore. An untested backup is a hope, not a plan.
-- ❌ Wrong: restoring to the "time of the complaint" instead of just before the bad statement;
--    find the exact time from app logs or Query Store first.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I express it as RPO/RTO. PITR gives minutes of RPO within the retention window; LTR is for compliance, not fast recovery. I rehearse the restore and the rename-swap runbook, and I add guardrails like least-privilege access, transactions with row-count checks, and temporal tables for critical tables." Mention that restore time grows with database size and cannot be assumed to be instant.

---

## 🔗 Related Questions
→ Q141 (backup and restore basics) | Q131 (transaction log and recovery models) | Q030 (temporal tables) | Q165 (geo-replication and failover groups) | Q118 (BEGIN TRAN, COMMIT, ROLLBACK)
