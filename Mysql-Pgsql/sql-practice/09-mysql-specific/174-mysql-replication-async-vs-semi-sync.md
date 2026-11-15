---

# Q174. MySQL Replication — Async vs Semi-Sync
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (8.0+ / 9.x)

---

## ❓ Question
Explain the difference between asynchronous and semi-synchronous replication in MySQL. When does a commit return to the client in each mode? How do you enable semi-sync, what happens if the replica disappears, and what data-loss guarantee do you actually get?

---

## 💡 Quick Concept (2 lines only)
Async: the source commits, writes the binlog and returns immediately; replicas pull the binlog later, so a crash can lose committed rows. Semi-sync: the commit waits until at least one replica has ACKed that it has received (not applied) the binlog event, or a timeout elapses.
हिंदी: Async में source commit करके तुरंत return करता है, replica बाद में लेता है; semi-sync में कम से कम एक replica के ACK का इंतज़ार होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOTE: what was actually run
-- ============================================
-- Verified on a SINGLE MySQL 9.1.0 server (no replica attached): plugin install,
-- variables, status counters and the timeout fallback below are real output.
-- A real source+replica pair (CHANGE REPLICATION SOURCE TO ..., START REPLICA)
-- was NOT run here; those commands are standard syntax but unverified.

-- ============================================
-- SETUP (run on SOURCE, then on each REPLICA)
-- ============================================

-- Source:
INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';
SET GLOBAL rpl_semi_sync_source_enabled = 1;
SET GLOBAL rpl_semi_sync_source_timeout = 1000;          -- ms to wait for an ACK

-- Replica (names differ before 8.0.26: rpl_semi_sync_master / _slave):
INSTALL PLUGIN rpl_semi_sync_replica SONAME 'semisync_replica.so';
SET GLOBAL rpl_semi_sync_replica_enabled = 1;
STOP REPLICA IO_THREAD; START REPLICA IO_THREAD;          -- re-handshake so semi-sync is negotiated

-- Persist in my.cnf, otherwise it is lost on restart:
--   plugin-load-add = semisync_source.so
--   rpl_semi_sync_source_enabled = 1

-- ============================================
-- SOLUTION: inspect semi-sync state
-- ============================================

SHOW VARIABLES LIKE 'rpl_semi_sync_source%';

-- Result (real output, MySQL 9.1.0):
-- rpl_semi_sync_source_enabled                | ON
-- rpl_semi_sync_source_timeout                | 1000
-- rpl_semi_sync_source_trace_level            | 32
-- rpl_semi_sync_source_wait_for_replica_count | 1
-- rpl_semi_sync_source_wait_no_replica        | ON
-- rpl_semi_sync_source_wait_point             | AFTER_SYNC     <- lossless mode (default since 5.7)

SHOW STATUS LIKE 'Rpl_semi_sync_source_status';
SHOW STATUS LIKE 'Rpl_semi_sync_source_clients';
-- Rpl_semi_sync_source_status  | ON   <- ON = semi-sync active, OFF = degraded to async
-- Rpl_semi_sync_source_clients | 0    <- number of semi-sync replicas connected (0 here: none attached)

-- ============================================
-- WHAT HAPPENS WHEN NO REPLICA ACKs (timed on the test server)
-- ============================================

-- Commit #1 with semi-sync ON and zero replicas: blocked ~1008 ms (= the 1000 ms timeout)
-- Commit #2 immediately after: ~1 ms, because the source already fell back to async
INSERT INTO g VALUES (3);   -- 11:16:40.341 -> 11:16:41.349  (waited for timeout)
INSERT INTO g VALUES (4);   -- 11:16:41.349 -> 11:16:41.350  (no wait)

SHOW STATUS LIKE 'Rpl_semi_sync_source_status';   -- OFF  (auto-degraded)
SHOW STATUS LIKE 'Rpl_semi_sync_source_no_tx';    -- 2    (commits NOT acknowledged by a replica)

-- Semi-sync re-enables itself automatically once a replica catches up and ACKs again.

-- ============================================
-- ASYNC vs SEMI-SYNC at a glance
-- ============================================
-- Mode       Client gets OK when...                    Data-loss window on source crash
-- Async      binlog written + flushed on source         Replica may be missing recent commits
-- Semi-sync  >=1 replica has RECEIVED the event         Near zero (replica has it in relay log)
-- Group Repl majority of members certified the txn      None for committed txns (needs quorum)
```

---

## 🔍 Why This Works (3 lines max)
With `AFTER_SYNC` the source waits for the replica ACK before the storage engine commits, so no other session can see a row that a replica might not have; a crash cannot expose a "phantom" commit. The ACK only means the event reached the replica's relay log, not that it is applied, so replica lag is still possible. If no ACK arrives within `rpl_semi_sync_source_timeout`, the source silently degrades to async.
हिंदी: AFTER_SYNC में replica का relay-log ACK आने के बाद ही commit visible होता है; timeout पर यह चुपचाप async बन जाता है।

---

## ⚡ Alternative Solution

```sql
-- Require 2 ACKs (stronger durability, higher commit latency):
SET GLOBAL rpl_semi_sync_source_wait_for_replica_count = 2;

-- Never degrade silently: huge timeout (writes then BLOCK if replicas die -> availability risk)
SET GLOBAL rpl_semi_sync_source_timeout = 4294967295;

-- Older wait point (5.5/5.6 style): commit in engine FIRST, then wait for ACK.
-- Other sessions can read the row before replica has it -> can see data that is lost on failover.
SET GLOBAL rpl_semi_sync_source_wait_point = AFTER_COMMIT;

-- Pre-8.0.26 names (MySQL 5.7 / early 8.0):
--   INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
--   SET GLOBAL rpl_semi_sync_master_enabled = 1;

-- PostgreSQL equivalent: synchronous_commit = on/remote_write/remote_apply
--   + synchronous_standby_names = 'FIRST 1 (replica1, replica2)';
```

---

## ⚠️ Common Mistake

```sql
-- ❌ "Semi-sync means replicas are always up to date"
-- It only guarantees the event was RECEIVED. SQL thread can still be minutes behind.
-- ✅ Monitor lag separately (Seconds_Behind_Source / performance_schema.replication_applier_status).

-- ❌ "Semi-sync = zero data loss, period"
-- Not true: after timeout it silently becomes async (Rpl_semi_sync_source_status = OFF).
-- ✅ Alert on Rpl_semi_sync_source_status = OFF and on Rpl_semi_sync_source_no_tx increasing.

-- ❌ Enabling the plugin on the replica but not restarting the IO thread
-- Replica keeps connecting as plain async until STOP/START REPLICA IO_THREAD.
```

---

## 🎯 Interview Tip (1 line)
Say: "Semi-sync with AFTER_SYNC gives lossless failover for acknowledged commits as long as it has not degraded; I alert on Rpl_semi_sync_source_status going OFF, and for true consensus I would move to Group Replication or InnoDB Cluster."

---

## 🔗 Related Questions
→ Q164 (Binary log) | Q175 (GTID replication) | Q176 (Galera Cluster) | Q163 (Redo vs undo log)
