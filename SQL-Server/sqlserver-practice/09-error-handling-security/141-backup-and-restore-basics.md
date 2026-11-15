---

# Q141. Backup and Restore Basics — Full, Differential, Log
# Category: Error Handling + Security
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: mysqldump/binlog | PostgreSQL: pg_dump/WAL + PITR). Not executed on SQL Server; behaviour per Microsoft docs.

---

## ❓ Question
Database `ShopDB` (FULL recovery model) must survive a crash at 14:37 with at most a few minutes of data loss. Design the backup schedule and show the restore sequence to recover to 14:30:00. Why does the transaction log keep growing if no log backups are taken?

---

## 💡 Quick Concept (2 lines only)
FULL = whole database, DIFFERENTIAL = pages changed since the last full, LOG = transactions since the last log backup (needed for point-in-time restore and to let the log truncate). Restore = full (NORECOVERY) -> latest diff (NORECOVERY) -> log chain -> RECOVERY.
हिंदी: Full = पूरा backup, Differential = last full के बाद का बदलाव, Log = transactions का backup। Restore में NORECOVERY लगाओ, आख़िरी step पर RECOVERY।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (not executed on SQL Server; behaviour per Microsoft docs)
-- ============================================
-- Recovery model must be FULL (or BULK_LOGGED) for log backups / PITR
ALTER DATABASE ShopDB SET RECOVERY FULL;

-- ============================================
-- BACKUP SCHEDULE (typical)
--   Sunday 01:00  FULL
--   Daily  01:00  DIFFERENTIAL
--   Every 5 min   LOG   -> RPO ~ 5 minutes
-- ============================================

BACKUP DATABASE ShopDB
  TO DISK = N'D:\backup\ShopDB_full.bak'
  WITH COMPRESSION, CHECKSUM, INIT, STATS = 10;

BACKUP DATABASE ShopDB
  TO DISK = N'D:\backup\ShopDB_diff.bak'
  WITH DIFFERENTIAL, COMPRESSION, CHECKSUM, INIT;

BACKUP LOG ShopDB
  TO DISK = N'D:\backup\ShopDB_log_1430.trn'
  WITH COMPRESSION, CHECKSUM;

-- Always verify (does not prove restorability, only readability)
RESTORE VERIFYONLY FROM DISK = N'D:\backup\ShopDB_full.bak' WITH CHECKSUM;

-- ============================================
-- RESTORE to 14:30:00 (on the same or another server)
-- ============================================

RESTORE DATABASE ShopDB_Restored
  FROM DISK = N'D:\backup\ShopDB_full.bak'
  WITH NORECOVERY, REPLACE,
       MOVE N'ShopDB'     TO N'E:\data\ShopDB_Restored.mdf',
       MOVE N'ShopDB_log' TO N'F:\log\ShopDB_Restored.ldf';

RESTORE DATABASE ShopDB_Restored
  FROM DISK = N'D:\backup\ShopDB_diff.bak'
  WITH NORECOVERY;

-- Restore every log backup in order; STOPAT on the last needed one
RESTORE LOG ShopDB_Restored
  FROM DISK = N'D:\backup\ShopDB_log_1430.trn'
  WITH STOPAT = N'2024-06-10T14:30:00', RECOVERY;

-- EXPECTED OUTPUT (conceptual, not executed):
--   RESTORE ... WITH NORECOVERY -> database shows "Restoring..." state
--   Final RESTORE LOG ... WITH RECOVERY -> database ONLINE, data as of 14:30:00

-- Check backup history
SELECT TOP 5 database_name, type, backup_start_date
FROM msdb.dbo.backupset
ORDER BY backup_start_date DESC;
-- type: D = full, I = differential, L = log
```

---

## 🔍 Why This Works (3 lines max)
The differential shortens the chain (you skip many logs), and each log backup continues the LSN chain, so the server can replay up to STOPAT. In FULL recovery the log is only truncated after a log backup, which is why a missing log-backup job makes the .ldf grow until the disk is full.
हिंदी: Log backup के बिना FULL recovery में log file बढ़ती रहती है। Chain टूटी तो point-in-time restore नहीं होगा।

---

## ⚡ Alternative Solution

```sql
-- Copy-only full backup: does NOT reset the differential base (ad-hoc dev copy)
BACKUP DATABASE ShopDB TO DISK = N'D:\backup\ShopDB_adhoc.bak' WITH COPY_ONLY, COMPRESSION;

-- Azure SQL Database: no BACKUP DATABASE command. Backups are automatic
-- (full weekly, diff every 12-24h, log ~5-10 min) with PITR and LTR - see Q166.
-- Managed Instance: only COPY_ONLY full backups to URL are allowed manually.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Restoring the full backup WITH RECOVERY, then trying to add diff/logs
RESTORE DATABASE ShopDB_Restored FROM DISK = N'D:\backup\ShopDB_full.bak' WITH RECOVERY;
-- DB comes online; further RESTORE DIFFERENTIAL / LOG is refused. Start over.
-- ✅ Use NORECOVERY on every step except the last

-- ❌ Database in FULL recovery but no log backup job
-- Log grows forever; or someone flips to SIMPLE to "fix" it -> loses PITR silently.

-- ❌ "We have backups" but never test a restore. A backup you have not restored is a hope.
```

---

## 🎯 Interview Tip (1 line)
Say: "I define RPO/RTO first. FULL weekly, DIFF daily, LOG every 5 minutes with CHECKSUM and compression, backups copied off-box, and a scheduled restore test. Restore is full+diff+logs WITH NORECOVERY and STOPAT for point-in-time. On Azure SQL it is managed PITR, so I tune retention rather than run BACKUP."

---

## 🔗 Related Questions
→ Q131 (Transaction log and recovery models) | Q166 (Backup, PITR and LTR on Azure) | Q140 (Always Encrypted and TDE) | Q165 (Geo-replication)
