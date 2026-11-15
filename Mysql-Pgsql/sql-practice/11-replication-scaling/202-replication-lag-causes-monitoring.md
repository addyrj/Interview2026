---

# Q202. Replication Lag — Causes + Monitoring
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Users update their profile and immediately see old data because reads go to a replica that is 40 seconds behind. What causes replication lag, how do you measure it in MySQL and PostgreSQL, and how do you reduce it?

---

## 💡 Quick Concept (2 lines only)
Lag = time (or bytes) between a commit on the primary and its replay on the replica. Typical causes: one big transaction, single-threaded apply, weak replica hardware, long queries or locks on the replica, network limits.
हिंदी: Lag मतलब primary पर commit और replica पर replay के बीच की देरी; कारण: बड़ी transaction, single-thread apply, कमज़ोर replica, replica पर लंबी queries।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
-- Lag needs a live primary + replica pair. NOT RUN: I only ran the commands on a
-- single MySQL 9.1 (no replication configured) and PGlite, so lag VALUES below are
-- illustrative. Verified facts: variable names/defaults and that commands parse.

-- ============================================
-- SOLUTION -- MySQL
-- ============================================

-- Step 1: quick number (on REPLICA)
SHOW REPLICA STATUS\G
--   Seconds_Behind_Source: 40      -- NULL = SQL thread not running / unknown. Not 0 !
--   Replica_IO_Running / Replica_SQL_Running: Yes/Yes
--   Retrieved_Gtid_Set vs Executed_Gtid_Set: gap = received-but-not-applied

-- Step 2: more accurate than Seconds_Behind_Source -- heartbeat table (pt-heartbeat idea)
CREATE TABLE heartbeat (id INT PRIMARY KEY, ts TIMESTAMP(6) NOT NULL);
-- primary, every second:  REPLACE INTO heartbeat VALUES (1, NOW(6));
-- replica:  SELECT TIMESTAMPDIFF(MICROSECOND, ts, NOW(6))/1e6 AS lag_seconds FROM heartbeat WHERE id = 1;

-- Step 3: where is the apply time going? (performance_schema, MySQL 8+)
SELECT WORKER_ID, LAST_APPLIED_TRANSACTION, APPLYING_TRANSACTION
FROM performance_schema.replication_applier_status_by_worker;

-- ============================================
-- SOLUTION -- PostgreSQL
-- ============================================
-- On the PRIMARY: bytes behind per standby
SELECT client_addr, state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
       write_lag, flush_lag, replay_lag                      -- intervals (PG10+)
FROM pg_stat_replication;

-- On the STANDBY: time since last replayed transaction
SELECT now() - pg_last_xact_replay_timestamp() AS replay_delay;
-- caveat: grows even when the primary is idle (no new transactions to replay)

-- ============================================
-- EXPECTED OUTPUT (illustrative -- NOT from a live pair)
-- ============================================
-- Seconds_Behind_Source: 40
-- replay_lag_bytes | replay_lag
-- 83886080         | 00:00:38.4
```

---

## 🔍 Why This Works (3 lines max)
Primary commits are parallel but classic replication replays them mostly serially, so write bursts, huge transactions (one 5-minute UPDATE takes 5 minutes to replay) and heavy replica reads all widen the gap. Measure both "received" (network) and "applied" (replay) to know which side is slow.
हिंदी: Primary पर commits parallel होते हैं पर replica पर replay कम parallel; बड़ी transaction और replica की भारी reads gap बढ़ाती हैं।

---

## ⚡ Alternative Solution

```sql
-- FIXES -- MySQL
SET GLOBAL replica_parallel_workers = 8;      -- default is 4 on 9.1 (verified); multi-threaded applier
SET GLOBAL replica_preserve_commit_order = 1; -- verified default 1; keeps order while parallel
-- binlog_transaction_dependency_tracking = WRITESET (source) improves parallelism
-- Break huge writes into batches of ~1000 rows with small sleeps:
--   DELETE FROM audit_log WHERE created_at < '2024-01-01' LIMIT 1000;   -- loop in app

-- FIXES -- PostgreSQL (standby)
-- max_standby_streaming_delay: replay waits for conflicting replica queries (up to this value)
-- hot_standby_feedback = on: fewer cancelled queries but may bloat primary
-- bigger/faster disks on standby; don't run reporting on the failover candidate

-- APP-LEVEL (the real answer to "stale read after write"):
--  read-your-writes: route the user's reads to primary for N seconds after a write,
--  or wait for GTID:  SELECT WAIT_FOR_EXECUTED_GTID_SET('uuid:123', 1);   -- MySQL, returns 0 when applied
--  PgSQL: compare pg_current_wal_lsn() captured at write with pg_last_wal_replay_lsn()
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Trusting Seconds_Behind_Source = 0 as "no lag"
-- It is computed from event timestamps; it can show 0 while IO thread is stalled or
-- NULL when broken. ✅ Also check thread states, GTID gaps, and a heartbeat table.

-- ❌ One giant "UPDATE ... WHERE" or ALTER on primary: replica is blocked for the same duration
-- ✅ batch it, or use online schema change tools (gh-ost / pt-osc)

-- ❌ Alerting only on average lag; alert on max and on "lag growing", and page on NULL
```

---

## 🎯 Interview Tip (1 line)
Say: "I measure lag with a heartbeat plus apply/receive gaps rather than Seconds_Behind_Source alone, cut it with parallel apply, batched writes and dedicated replica hardware, and design the app for read-your-writes instead of assuming replicas are instantly consistent."

---

## 🔗 Related Questions
→ Q201 (Replication setup) | Q203 (Read replica routing) | Q198 (PgSQL replication) | Q220 (Zero-downtime migration)
