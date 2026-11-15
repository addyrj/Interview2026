---

# Q175. MySQL GTID Replication
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (5.6+; syntax shown for 8.0+ / 9.x)

---

## ❓ Question
What is a GTID in MySQL replication? How is it different from file+position replication, how do you enable it online without downtime, and how do you skip a bad transaction on a replica?

---

## 💡 Quick Concept (2 lines only)
A GTID (`source_uuid:transaction_id`) uniquely names every committed transaction cluster-wide, so a replica says "I have executed set X, send me the rest" instead of tracking a binlog file name and offset. Failover and re-pointing a replica to a new source become automatic (`SOURCE_AUTO_POSITION=1`).
हिंदी: GTID हर transaction का unique नाम है (uuid:number); replica खुद पता कर लेता है कि कौन से transactions बाकी हैं, file/position नहीं चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOTE: what was actually run
-- ============================================
-- The online enable steps and the local GTID counters below were run on a single
-- MySQL 9.1.0 server. CHANGE REPLICATION SOURCE / START REPLICA need a second
-- server and were NOT run (marked "not run").

-- ============================================
-- SETUP: enable GTID online (no restart), on every server, in this order
-- ============================================

SET GLOBAL enforce_gtid_consistency = WARN;      -- step 1: watch the error log for unsafe statements
SET GLOBAL enforce_gtid_consistency = ON;        -- step 2: reject statements that cannot be GTID-logged
SET GLOBAL gtid_mode = OFF_PERMISSIVE;           -- step 3..5: must move ONE step at a time
SET GLOBAL gtid_mode = ON_PERMISSIVE;
-- (wait until all replicas/servers accept GTID, anonymous txns drained)
SET GLOBAL gtid_mode = ON;

-- Persist in my.cnf: gtid_mode=ON, enforce_gtid_consistency=ON, log_bin, server_id=<unique>
-- (jumping straight between OFF and ON fails with ERROR 1788; each step is a separate statement - verified.)

SELECT @@gtid_mode;
-- Result (real):
-- @@gtid_mode
-- ON

-- ============================================
-- SOLUTION: see GTIDs being assigned
-- ============================================

CREATE TABLE g (i INT);
INSERT INTO g VALUES (1);
INSERT INTO g VALUES (2);

SELECT @@global.gtid_executed, @@server_uuid\G
-- Result (real, uuid differs on every server):
-- @@global.gtid_executed: ba64da22-dc00-11f1-8364-eea87e7f028a:1-3
--           @@server_uuid: ba64da22-dc00-11f1-8364-eea87e7f028a
-- 3 statements (CREATE + 2 INSERT) = 3 GTIDs: 1,2,3 (each autocommit statement is its own txn)

CREATE TABLE g2 AS SELECT 1 x;       -- allowed under ON in 8.0.21+ (atomic DDL, row-based)
SHOW BINARY LOG STATUS;              -- 8.2+. On 8.0 / 5.7: SHOW MASTER STATUS
-- File          | Position | Executed_Gtid_Set
-- binlog.000004 | 1276     | ba64da22-dc00-11f1-8364-eea87e7f028a:1-4   <- now 1-4

-- ============================================
-- POINT A REPLICA AT THE SOURCE (not run - needs 2 servers)
-- ============================================

CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = 'db-primary.internal',
  SOURCE_USER = 'repl',
  SOURCE_PASSWORD = '********',
  SOURCE_AUTO_POSITION = 1;          -- no file / pos needed - this is the GTID benefit
START REPLICA;
SHOW REPLICA STATUS\G                -- Retrieved_Gtid_Set vs Executed_Gtid_Set shows lag

-- ============================================
-- SKIP ONE BAD TRANSACTION ON A REPLICA (not run)
-- ============================================
-- SQL thread stopped with error on GTID 3E11FA47-...:23
STOP REPLICA;
SET GTID_NEXT = '3E11FA47-71CA-11E1-9E33-C80AA9429562:23';
BEGIN; COMMIT;                       -- empty transaction "consumes" that GTID
SET GTID_NEXT = 'AUTOMATIC';
START REPLICA;

-- file+position equivalent was: SET GLOBAL sql_replica_skip_counter = 1;  (documented as incompatible with GTID auto-position; not run)
```

---

## 🔍 Why This Works (3 lines max)
Each replica stores `gtid_executed`; on connect it sends that set and the source streams only transactions not in it, so duplicates and gaps are detected automatically. An empty transaction under the same GTID marks it as executed, which is how a poison transaction is skipped safely. File+position needs you to compute the exact offset by hand after every failover.
हिंदी: Replica अपना executed GTID set भेजता है, source सिर्फ़ बाकी transactions भेजता है; bad transaction को empty txn से skip किया जाता है।

---

## ⚡ Alternative Solution

```sql
-- Classic file + position (works without GTID, error-prone on failover):
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='db-primary', SOURCE_USER='repl', SOURCE_PASSWORD='***',
  SOURCE_LOG_FILE='binlog.000004', SOURCE_LOG_POS=1276;

-- Seeding a new replica from a dump (real mysqldump output includes this):
--   SET @@GLOBAL.GTID_PURGED='ba64da22-dc00-11f1-8364-eea87e7f028a:1-6';
-- mysqldump --set-gtid-purged=ON  writes it; =OFF omits it (use for partial dumps / non-replication restores).

-- MySQL <= 8.0.22 syntax: CHANGE MASTER TO ... MASTER_AUTO_POSITION=1; START SLAVE;
-- PostgreSQL has no GTID; it uses LSNs (pg_current_wal_lsn / pg_last_wal_replay_lsn).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Setting gtid_mode=ON in one jump on a live cluster
SET GLOBAL gtid_mode = OFF;      -- (run from ON) ERROR 1788: ...can only be changed one step at a time: OFF <-> OFF_PERMISSIVE <-> ON_PERMISSIVE <-> ON
-- ✅ OFF -> OFF_PERMISSIVE -> ON_PERMISSIVE -> ON

-- ❌ Writing directly on a replica (errant transaction)
-- Replica gets its own GTID (replica_uuid:1) that the source does not have.
-- After failover/promotion these errant GTIDs break replication.
-- ✅ super_read_only=ON on replicas; detect with GTID_SUBTRACT(replica_set, source_set).

-- ❌ Using sql_replica_skip_counter with GTID on  -> documented as incompatible, use the empty-transaction trick.
```

---

## 🎯 Interview Tip (1 line)
Say: "I run GTID with enforce_gtid_consistency and super_read_only on replicas, because failover becomes `SOURCE_AUTO_POSITION=1` plus a GTID_SUBTRACT check for errant transactions instead of hand-computing binlog coordinates."

---

## 🔗 Related Questions
→ Q164 (Binary log formats) | Q174 (Async vs semi-sync) | Q176 (Galera Cluster) | Q179 (mysqldump vs xtrabackup)
