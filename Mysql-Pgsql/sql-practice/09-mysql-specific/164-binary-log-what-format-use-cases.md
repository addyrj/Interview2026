---

# Q164. Binary Log — What, Format, Use Cases
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL

---

## ❓ Question
What is the MySQL binary log, what are STATEMENT / ROW / MIXED formats, and what is it used for? How do you inspect it?

---

## 💡 Quick Concept (2 lines only)
The binlog is a server-level sequence of committed data changes (and DDL) used for replication, point-in-time recovery, and CDC (Debezium). ROW format (default since 5.7.7) logs the changed rows; STATEMENT logs the SQL text.
हिंदी: Binlog में committed changes क्रम से लिखे जाते हैं - replication, PITR और CDC के लिए; default format ROW है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 verified)
-- ============================================

CREATE TABLE wallet (id INT PRIMARY KEY, bal DECIMAL(10,2));
INSERT INTO wallet VALUES (1,100),(2,200);
UPDATE wallet SET bal = bal - 10 WHERE id = 1;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: configuration
SHOW VARIABLES LIKE 'log_bin';            -- ON (default ON since 8.0)
SHOW VARIABLES LIKE 'binlog_format';      -- ROW
SHOW VARIABLES LIKE 'binlog_row_image';   -- FULL (before+after of every column)
SHOW VARIABLES LIKE 'gtid_mode';          -- OFF by default; ON in most replicated production setups

-- Step 2: files and current position
SHOW BINARY LOGS;
SHOW BINARY LOG STATUS;                   -- 8.4+ ; older: SHOW MASTER STATUS (removed in 8.4)

-- Step 3: events
SHOW BINLOG EVENTS IN 'binlog.000001' LIMIT 10;

-- Step 4 (shell, not SQL): decode ROW events as pseudo-SQL
--   mysqlbinlog --base64-output=DECODE-ROWS -vv binlog.000001      (not run here)

-- ============================================
-- EXPECTED OUTPUT (real run, abridged)
-- ============================================
-- log_bin ON | binlog_format ROW | binlog_row_image FULL | gtid_mode OFF
-- Log_name      | File_size | Encrypted
-- binlog.000001 | 7388      | No
-- Event_type     | Info
-- Format_desc    | Server ver: 9.1.0, Binlog ver: 4
-- Anonymous_Gtid | SET @@SESSION.GTID_NEXT= 'ANONYMOUS'
-- Query          | use `t1`; CREATE TABLE ... /* xid=12 */     <- DDL is logged as a statement
-- Query          | BEGIN
-- Table_map      | table_id: 105 (t1.users_svc)
-- Write_rows     | table_id: 105 flags: STMT_END_F             <- ROW format: rows, not SQL text
-- Xid            | COMMIT /* xid=14 */
```

---

## 🔍 Why This Works (3 lines max)
Every committed transaction is appended to the binlog (after InnoDB prepare, before InnoDB commit - two-phase commit), so replicas replay it in order and point-in-time recovery replays it on top of a backup. ROW is deterministic; STATEMENT is smaller but unsafe for NOW()/UUID()/LIMIT without ORDER BY.
हिंदी: हर commit binlog में जाता है; replica इसे replay करता है और backup के ऊपर PITR भी इसी से होता है।

---

## ⚡ Alternative Solution

```sql
-- Format comparison
-- STATEMENT: small log, human readable, non-deterministic functions can diverge on replicas
-- ROW      : exact, safe, required for CDC; large for bulk UPDATE/DELETE (every row image)
-- MIXED    : statement by default, switches to row when unsafe (rarely chosen today)
-- Reduce size: SET GLOBAL binlog_row_image = 'MINIMAL';  (only PK + changed columns; CDC tools may need FULL)

-- Retention: 
SET GLOBAL binlog_expire_logs_seconds = 604800;         -- 7 days (default 30 days = 2592000)
-- PURGE BINARY LOGS BEFORE NOW() - INTERVAL 3 DAY;      -- manual, never rm files by hand

-- Point-in-time recovery (shell, not run): restore full backup, then
--   mysqlbinlog --start-position=... --stop-datetime="2026-11-06 10:00:00" binlog.000* | mysql
-- PostgreSQL equivalent: WAL archiving + logical decoding (wal_level=logical) for CDC. Not run here.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Disk fills up because binlogs are never purged (or expire is too long on a write-heavy server)
-- ❌ Using STATEMENT format with non-deterministic functions - replica data drifts
-- ❌ Mixing up binlog with the redo log: redo = crash recovery inside InnoDB; binlog = replication/PITR/CDC
-- ❌ Setting sync_binlog=0 for speed on a primary: committed transactions can be lost from binlog on crash (replicas miss them)
-- ✅ ROW + sync_binlog=1 + innodb_flush_log_at_trx_commit=1 for durability; GTID for easy failover
```

---

## 🎯 Interview Tip (1 line)
Say: "The binlog is the logical, server-level change stream that powers replication, PITR and CDC; I run ROW format with GTIDs and sync_binlog=1, set an explicit retention, and keep it distinct from InnoDB's redo log which only serves crash recovery."

---

## 🔗 Related Questions
→ Q163 (Redo vs undo) | Q157 (Zero-downtime migrations - gh-ost reads binlog) | Q156 (Outbox/CDC)
