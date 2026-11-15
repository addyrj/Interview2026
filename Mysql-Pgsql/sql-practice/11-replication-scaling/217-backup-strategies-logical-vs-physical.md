---

# Q217. Backup Strategies — Logical vs Physical
# Category: Replication & Scaling
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
Compare logical backups (mysqldump, pg_dump) with physical backups (Percona XtraBackup, pg_basebackup, snapshots). When do you use each, and how do you take a consistent logical backup without locking?

---

## 💡 Quick Concept (2 lines only)
Logical = SQL/rows exported (portable, slow restore); physical = copy of data files plus log (fast restore, same major version, enables PITR).
हिंदी: Logical = SQL export (portable पर restore धीमा); Physical = data files की copy (restore तेज़, PITR संभव)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0, run)
-- ============================================
CREATE TABLE orders (
  order_id  INT PRIMARY KEY,
  user_id   INT,
  tenant_id INT,
  amount    DECIMAL(10,2)
);
INSERT INTO orders VALUES (1,101,1,10),(2,101,1,20),(3,102,1,30);

-- ============================================
-- LOGICAL (MySQL) -- shell, RUN on 9.1.0
-- ============================================
-- mysqldump -uroot --single-transaction --routines --source-data=2 shop orders > shop.sql
--   --single-transaction : consistent snapshot via REPEATABLE READ, no table locks (InnoDB only)
--   --source-data=2      : writes the binlog coordinates as a comment (older: --master-data)
-- Real excerpt of the dump header and body:
-- -- CHANGE REPLICATION SOURCE TO SOURCE_LOG_FILE='binlog.000001', SOURCE_LOG_POS=38537;
-- DROP TABLE IF EXISTS `orders`;
-- CREATE TABLE `orders` ( `order_id` int NOT NULL, ... PRIMARY KEY (`order_id`) ) ENGINE=InnoDB ...;
-- INSERT INTO `orders` VALUES (1,101,1,10.00),(2,101,1,20.00),...;
-- (log file/position differ per server)
-- Restore: mysql shop < shop.sql        (single-threaded; hours for TB-scale)
-- Parallel logical: mysqlsh util.dumpInstance() / util.loadDump()  (NOT RUN)

-- ============================================
-- LOGICAL (PostgreSQL) -- shell, NOT RUN
-- ============================================
-- pg_dump -Fd -j 4 -f /backup/shop.dir shop     # directory format, 4 parallel jobs
-- pg_restore -j 4 -d shop_new /backup/shop.dir
-- pg_dumpall --globals-only > globals.sql       # roles, tablespaces (pg_dump skips them)
-- pg_dump uses one REPEATABLE READ snapshot -> consistent without blocking writers.

-- ============================================
-- PHYSICAL -- shell, NOT RUN
-- ============================================
-- MySQL : xtrabackup --backup --target-dir=/backup/full
--         xtrabackup --prepare --target-dir=/backup/full       (apply redo)
--         xtrabackup --backup --incremental-basedir=/backup/full --target-dir=/backup/inc1
--         (MySQL 8.0.17+/9.x also has CLONE plugin: CLONE LOCAL DATA DIRECTORY = '/backup/c1';)
-- PgSQL : pg_basebackup -h primary -U replicator -D /backup/base -X stream -Ft -z
--         or pgBackRest / Barman (incremental, parallel, retention, S3)
-- Storage snapshots (EBS/LVM): consistent only if DB is quiesced or WAL/redo is captured.

-- ============================================
-- Comparison
-- ============================================
-- Aspect           | Logical                   | Physical
-- Restore speed    | slow (replays INSERT+idx) | fast (copy files)
-- Portability      | cross-version, cross-OS   | same major version/arch
-- Size             | compresses well           | full data size (+indexes)
-- Granularity      | per table / schema        | whole instance (some tools: per table)
-- PITR             | no (alone)                | yes with binlog / WAL archive
-- Corruption check | rewrites clean pages      | copies corrupt pages too
-- Typical use      | small DBs, migrations, upgrade | production DR
```

---

## 🔍 Why This Works (3 lines max)
Logical tools read through SQL under a consistent snapshot, so output is version-neutral but needs rebuild of indexes on load. Physical tools copy pages and the log, so restore is bounded by disk speed and can roll forward with archived logs.
हिंदी: Logical snapshot से rows पढ़ता है, load में indexes दोबारा बनते हैं; Physical pages copy करता है इसलिए तेज़ restore।

---

## ⚡ Alternative Solution

```sql
-- Replica-based backup: take backups from a replica to spare the primary
--   (pause SQL thread or use --single-transaction; PgSQL: pg_basebackup from standby).
-- Delayed replica as an "oops" safety net:
--   MySQL: CHANGE REPLICATION SOURCE TO SOURCE_DELAY = 3600;      (NOT RUN)
--   PgSQL: recovery_min_apply_delay = '1h'                         (NOT RUN)
-- 3-2-1 rule: 3 copies, 2 media, 1 off-site (other region/account), immutable if possible.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ mysqldump without --single-transaction on InnoDB: either locks tables
--    (default --lock-tables) or yields inconsistent data across tables.
-- ❌ Never testing a restore. A backup is only proven by a restore drill + checksum.
-- ❌ pg_dump of one DB and assuming roles are included (they are not: pg_dumpall -g).
-- ❌ Treating a replica as a backup (Q207): DROP TABLE replicates instantly.
-- ❌ Copying live data files with cp/rsync while the server runs: torn pages.
-- ✅ Use the tool built for the job and verify: restore to a scratch host monthly.
```

---

## 🎯 Interview Tip (1 line)
Say: "I define RPO and RTO first: logical dumps for small data and cross-version moves, physical (XtraBackup, pgBackRest) plus archived binlog/WAL for production so I get fast restores and point-in-time recovery, with off-site copies and a scheduled restore test."

---

## 🔗 Related Questions
→ Q218 (PITR) | Q207 (streaming replication) | Q209 (logical replication) | Q220 (zero-downtime migration)
