---

# Q179. mysqldump vs xtrabackup
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (8.0+ / 9.x); XtraBackup is a Percona tool

---

## ❓ Question
Compare logical backups (`mysqldump`) with physical hot backups (Percona XtraBackup). When do you use each, how do you get a consistent snapshot and a point-in-time-recovery position, and how do restore times compare?

---

## 💡 Quick Concept (2 lines only)
`mysqldump` writes SQL (CREATE/INSERT) text: portable and human-readable but slow to restore on big data. XtraBackup copies InnoDB data files plus the redo log while the server runs and then "prepares" them: much faster backup/restore for large databases, but same-version-family and file-level.
हिंदी: mysqldump SQL text बनाता है (portable पर restore धीमा); XtraBackup data files hot copy करता है (बड़े DB में तेज़)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOTE: what was run
-- ============================================
-- mysqldump was run for real (MySQL 9.1.0 client/server); output lines below are real.
-- XtraBackup is NOT installed here: its commands are standard usage, NOT run.

-- ============================================
-- SETUP: a tiny table to dump
-- ============================================
CREATE TABLE g (i INT);
INSERT INTO g VALUES (1),(2),(3),(4);

-- ============================================
-- SOLUTION 1: mysqldump (logical)  - shell commands
-- ============================================
--   mysqldump -uroot --single-transaction --source-data=2 --routines --triggers --events \
--             --set-gtid-purged=OFF t g > t_g.sql
--
-- --single-transaction  : consistent snapshot via REPEATABLE READ, no table locks (InnoDB only)
-- --source-data=2       : writes the binlog coordinates as a COMMENT (8.2+; older: --master-data=2)
-- --set-gtid-purged=OFF : omit GTID_PURGED when you are not seeding a replica

-- Real excerpt of the dump:
-- -- CHANGE REPLICATION SOURCE TO SOURCE_LOG_FILE='binlog.000004', SOURCE_LOG_POS=1808;
-- DROP TABLE IF EXISTS `g`;
-- CREATE TABLE `g` (`i` int DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ...;
-- LOCK TABLES `g` WRITE;
-- INSERT INTO `g` VALUES (1),(2),(3),(4);
-- UNLOCK TABLES;

-- Restore (single-threaded replay of every INSERT):
--   mysql -uroot t < t_g.sql

-- Point-in-time recovery = dump + binlogs after the recorded position:
--   mysqlbinlog --start-position=1808 binlog.000004 binlog.000005 | mysql -uroot

-- Real side-effect I observed: with GTID_MODE=ON a PARTIAL dump prints
--   "Warning: A partial dump from a server that has GTIDs will by default include
--    the GTIDs of all transactions ..."  and emits
--   SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ 'ba64da22-...:1-6';
-- Restoring that on a non-replica can block later replication setup -> use --set-gtid-purged=OFF.

-- ============================================
-- SOLUTION 2: XtraBackup (physical)  - NOT run
-- ============================================
--   xtrabackup --backup --user=backup --password=*** --target-dir=/backups/full_2026-11-09
--   xtrabackup --prepare --target-dir=/backups/full_2026-11-09      # apply redo log -> crash-consistent -> consistent
--
-- Incremental (needs a base):
--   xtrabackup --backup --target-dir=/backups/inc1 --incremental-basedir=/backups/full_2026-11-09
--   xtrabackup --prepare --apply-log-only --target-dir=/backups/full_2026-11-09
--   xtrabackup --prepare --target-dir=/backups/full_2026-11-09 --incremental-dir=/backups/inc1
--
-- Restore: stop mysqld, empty datadir, then
--   xtrabackup --copy-back --target-dir=/backups/full_2026-11-09
--   chown -R mysql:mysql /var/lib/mysql && systemctl start mysql
-- Binlog position for PITR / new replica: file xtrabackup_binlog_info inside the backup dir.
-- (MySQL 8.4+/9.x needs the matching XtraBackup 8.4 / "Percona XtraBackup 9.x" release.)

-- ============================================
-- Comparison
-- ============================================
-- Aspect            | mysqldump                | XtraBackup
-- Type              | logical (SQL)            | physical (files)
-- Locks             | none w/ single-trans (InnoDB) | none for InnoDB (brief for non-InnoDB / metadata)
-- Backup speed      | slow, CPU bound          | disk-speed
-- Restore speed     | slow (replays INSERTs, rebuilds indexes) | fast (copy files)
-- Portability       | cross-version, cross-engine, partial tables | same major family, whole instance
-- Incremental       | no                       | yes
-- Good size         | < ~50-100 GB             | hundreds of GB - TB
```

---

## 🔍 Why This Works (3 lines max)
`--single-transaction` opens one consistent read view so rows are read as of one instant without blocking writers; XtraBackup instead copies pages while tailing the redo log, then `--prepare` replays that log so the copy matches a single point in time. Recording binlog position (or GTID set) with either lets you roll forward to any moment.
हिंदी: single-transaction एक consistent snapshot देता है; XtraBackup pages copy करके redo log replay करता है, binlog position से PITR होता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL Shell dump utilities (parallel, compressed, logical) - 8.0.21+, not run:
--   mysqlsh -- util dump-instance /backups/dump --threads=8
--   mysqlsh -- util load-dump /backups/dump --threads=8
-- Much faster than mysqldump while still logical.

-- Per-table "dump" via SQL (no tool): SELECT ... INTO OUTFILE / LOAD DATA INFILE
-- Cloud snapshots (EBS / RDS snapshots): fast physical copy, still enable binlogs for PITR.

-- PostgreSQL equivalents: pg_dump (logical) vs pg_basebackup / pgBackRest (physical) + WAL archiving for PITR.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ mysqldump without --single-transaction on a live InnoDB DB  -> default LOCK TABLES blocks writes
-- ✅ --single-transaction (and never rely on it for MyISAM tables or DDL during the dump)

-- ❌ Never testing a restore. "Backups succeed" is not "backups restore".
-- ✅ Restore weekly to a scratch host; verify row counts and run CHECK TABLE.

-- ❌ Taking only a physical backup with no binlogs -> restore recovers to the backup instant only.
-- ✅ Keep binlogs (binlog_expire_logs_seconds=2592000 default = 30 days) for point-in-time recovery.

-- ❌ Forgetting xtrabackup --prepare before --copy-back -> data dir is crash-inconsistent.
```

---

## 🎯 Interview Tip (1 line)
Say: "Under ~100 GB I use mysqldump or MySQL Shell dump for portability; beyond that XtraBackup (or snapshots) with binlogs for PITR, and I judge the strategy by tested restore time against the RTO, not by backup time."

---

## 🔗 Related Questions
→ Q164 (Binary log) | Q175 (GTID, GTID_PURGED) | Q176 (Galera SST uses xtrabackup) | Q163 (Redo log)
