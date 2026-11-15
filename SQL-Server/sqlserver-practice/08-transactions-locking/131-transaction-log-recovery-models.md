
---

# Q131. Transaction Log and Recovery Models
# Category: TRANSACTIONS + LOCKING
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (not executed on SQL Server; behaviour per Microsoft docs; Azure SQL Database manages recovery model for you)

---

## ❓ Question
The `.ldf` file of the Orders database has grown to 200 GB although data is 20 GB. Explain how the transaction log works, the three recovery models, why the log may not truncate, and how you diagnose and fix it.

---

## 💡 Quick Concept (2 lines only)
Every change is written to the log first (write-ahead logging); the log is what gives durability, rollback and crash recovery. SIMPLE reclaims log space at checkpoints, FULL keeps it until a log backup, BULK_LOGGED is FULL with minimal logging for bulk operations.
हिंदी: हर change पहले log में लिखा जाता है (WAL)। SIMPLE में checkpoint पर log साफ़ होता है, FULL में log backup के बाद ही।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SOLUTION: diagnose first
-- ============================================
-- 1) Which recovery model, and why can't the log truncate?
SELECT name, recovery_model_desc, log_reuse_wait_desc
FROM sys.databases
WHERE name = N'OrdersDb';
-- log_reuse_wait_desc values (documented): NOTHING, LOG_BACKUP, ACTIVE_TRANSACTION,
-- REPLICATION, AVAILABILITY_REPLICA, ACTIVE_BACKUP_OR_RESTORE ... The value tells you the blocker.

-- 2) Log size and usage
DBCC SQLPERF(LOGSPACE);

-- 3) Oldest open transaction (the classic culprit)
DBCC OPENTRAN (N'OrdersDb');

-- ============================================
-- FIX A: FULL recovery + no log backups  -> take log backups on a schedule
-- ============================================
BACKUP LOG OrdersDb TO DISK = N'D:\backup\OrdersDb_log.trn';
-- Log space inside the file is then reused; file size does not shrink by itself.

-- ============================================
-- FIX B: change model (only if point-in-time restore is NOT needed, e.g. dev/test)
-- ============================================
ALTER DATABASE OrdersDb SET RECOVERY SIMPLE;

-- ============================================
-- FIX C: one-time shrink after the cause is fixed (avoid routine shrinking)
-- ============================================
DBCC SHRINKFILE (N'OrdersDb_log', 8192);   -- target size in MB
```

| Model | Log truncates | Point-in-time restore | Typical use |
|---|---|---|---|
| SIMPLE | at checkpoint | no (only to last full/diff) | dev, staging, rebuildable data |
| FULL | only after log backup | yes | production OLTP |
| BULK_LOGGED | after log backup | yes except within bulk-logged ops | temporary, for big imports/index rebuilds |

```sql
-- EXPECTED OUTPUT
-- Not executed on SQL Server; no equivalent engine exists here. Illustrative shape only (values depend on server):
-- name     | recovery_model_desc | log_reuse_wait_desc
-- OrdersDb | FULL                | LOG_BACKUP        <- typical when log backups are missing
-- Fix: BACKUP LOG, after which the wait becomes NOTHING on the next truncation point.
```

---

## 🔍 Why This Works (3 lines max)
In FULL recovery the log is the chain needed for point-in-time restore, so SQL Server will not reuse space until a log backup captures it. Log backups free space inside the file; they do not shrink the file, which is why you fix the cause and size the file once.
हिंदी: FULL में log backup होने तक space reuse नहीं होता। Log backup file को छोटा नहीं करता, सिर्फ़ अंदर की जगह खाली करता है।

---

## ⚡ Alternative Solution

```sql
-- Stop an uncontrolled log from growing: set sensible growth + max size, monitor it
ALTER DATABASE OrdersDb MODIFY FILE (NAME = N'OrdersDb_log', FILEGROWTH = 512MB, MAXSIZE = 100GB);
-- Batch large DML (e.g. 5000-50000 rows per loop) so each batch commits and log can be reused.
-- Accelerated Database Recovery (2019+, default in Azure SQL) speeds up rollback/recovery; verify support for your version.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: switching FULL -> SIMPLE -> FULL to "fix" size without a new full backup. It breaks the log chain;
--    log backups fail until a new full (or differential) backup is taken.
-- ❌ Wrong: shrinking the log (or data file) daily; causes fragmentation of VLFs and regrowth stalls.
-- ❌ Wrong: leaving production in FULL without any log backup job (log grows forever).
-- ❌ Wrong: BACKUP LOG ... WITH TRUNCATE_ONLY (removed since SQL Server 2008).
-- ❌ Wrong: ignoring a long-running open transaction, which holds the log no matter how many backups run.
```

---

## 🎯 Interview Tip (1 line)
Say: "First query sys.databases for log_reuse_wait_desc rather than shrinking blindly. Production is FULL with log backups every 5-15 minutes to meet the RPO, an open transaction or replication can pin the log, and I never schedule shrink jobs. On Azure SQL Database backups and recovery are managed, with PITR retention configured."

---

## 🔗 Related Questions
→ Q117 (ACID in SQL Server) | Q141 (Backup and restore basics) | Q145 (Batching large updates/deletes) | Q166 (Backup, PITR and LTR)
