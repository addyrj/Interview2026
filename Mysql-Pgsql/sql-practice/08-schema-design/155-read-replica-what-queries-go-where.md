---

# Q155. Read Replica — What Queries Go Where
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both — replication itself was NOT run (needs 2 servers); only the session checks were run on MySQL 9.1 / PGlite

---

## ❓ Question
You added a read replica. Which queries can safely go to the replica and which must stay on the primary? How do you deal with replication lag and read-your-own-writes?

---

## 💡 Quick Concept (2 lines only)
Replicas replay the primary's log asynchronously, so they are slightly behind. Send lag-tolerant reads (reports, search, dashboards, listing pages) to replicas; send all writes and anything that must see the latest data to the primary.
हिंदी: Replica थोड़ा पीछे रहता है — report/listing जैसी reads replica पर, writes और "अभी लिखा वही पढ़ना" वाली reads primary पर।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (conceptual routing table; verified only: the session-state queries below)
-- ============================================

-- Route to PRIMARY:
--   INSERT / UPDATE / DELETE / DDL
--   SELECT ... FOR UPDATE, SELECT ... FOR SHARE (they take locks)
--   Reads inside a write transaction
--   Read-your-own-writes: user just placed an order -> show "My orders" from primary
--   Critical checks: stock/balance validation, unique-username check, payment status
-- Route to REPLICA:
--   Product listing, search, public profile pages
--   Analytics / BI / export / long-running reports (protects primary)
--   Background jobs that tolerate seconds of staleness
--   Backups (run mysqldump / pg_dump against the replica)

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: know which node you are on
-- MySQL:
SELECT @@read_only, @@super_read_only;
-- Real output on my standalone test server: 0 | 0    (a replica should show 1 | 1)

-- PostgreSQL:
SELECT pg_is_in_recovery();
-- Real output on PGlite (a primary): false     (a streaming replica returns true)

-- Step 2: measure lag (NOT run here: needs a configured replica)
-- MySQL 8.0.22+ (on the replica):
SHOW REPLICA STATUS\G          -- look at Seconds_Behind_Source, Replica_IO_Running, Replica_SQL_Running
-- PostgreSQL (on the replica):
SELECT now() - pg_last_xact_replay_timestamp() AS replay_lag;
-- PostgreSQL (on the primary):
SELECT client_addr, state, replay_lag FROM pg_stat_replication;

-- Step 3: setup commands (NOT run)
-- MySQL replica:
--   CHANGE REPLICATION SOURCE TO SOURCE_HOST='primary', SOURCE_USER='repl', SOURCE_PASSWORD='***',
--     SOURCE_AUTO_POSITION=1;     -- GTID based
--   START REPLICA;
--   SET PERSIST super_read_only = ON;
-- PostgreSQL replica:
--   pg_basebackup -h primary -D /var/lib/postgresql/data -R -X stream
--   (the -R flag writes standby.signal + primary_conninfo)

-- Step 4: application-level read-your-own-writes patterns
-- a) After a write, pin that user's reads to the primary for ~5 seconds (cookie/session flag)
-- b) Or wait for the replica to catch up to a GTID (MySQL):
SELECT WAIT_FOR_EXECUTED_GTID_SET('3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5', 1);   -- returns 0 on success, 1 on timeout
-- c) Or PgSQL: compare pg_current_wal_lsn() (primary) with pg_last_wal_replay_lsn() (replica)
```

---

## 🔍 Why This Works (3 lines max)
Asynchronous replication means a replica may be milliseconds to minutes behind, so only queries that tolerate stale data are safe there. Locking reads and read-after-write flows need the primary's truth. Offloading heavy reads shrinks primary load and lets you scale reads horizontally.
हिंदी: Async replication में replica पीछे हो सकता है, इसलिए सिर्फ stale-tolerant reads वहां भेजो; locking और read-after-write primary पर।

---

## ⚡ Alternative Solution

```sql
-- Routing in the app or a proxy:
--   ProxySQL (MySQL): rule "^SELECT .* FOR UPDATE" -> hostgroup 10 (primary), "^SELECT" -> hostgroup 20 (replicas)
--   PgBouncer + HAProxy / pgpool-II / Patroni endpoints (primary vs replica ports) for PostgreSQL
--   ORMs: Django DATABASES['replica'] + router, Rails connected_to(role: :reading), Spring AbstractRoutingDataSource

-- Stricter consistency options (NOT run):
--   MySQL semi-sync replication / Group Replication: primary waits for at least one replica ack
--   PostgreSQL: synchronous_commit = remote_apply  (commit returns only after replica applied it)
--   Aurora/RDS: reader endpoint load-balances; lag is typically < 100 ms but not zero
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: write then immediately read from a replica
INSERT INTO orders ...;           -- primary
SELECT * FROM orders WHERE id = ?; -- replica: row "doesn't exist" yet -> user sees 404 on their own order
-- ✅ Read from the primary (or pin the session) for a short window after writes

-- ❌ Wrong: SELECT ... FOR UPDATE on a replica (error: replica is read-only) or using it for decisions
-- ❌ Wrong: running a 2-hour report on a replica with hot_standby_feedback off (PgSQL: query cancelled by recovery conflict)
-- ❌ Wrong: assuming replicas help write throughput — they don't; every replica replays every write
-- ❌ Wrong: no lag monitoring/alerting; a stalled replica silently serves stale data
```

---

## 🎯 Interview Tip (1 line)
Say: "Replicas scale reads, not writes: I route lag-tolerant reads and reports to replicas, keep writes, locking reads and read-your-own-writes on the primary, monitor replication lag, and add session pinning or GTID waits when the product can't tolerate staleness."

---

## 🔗 Related Questions
→ Q154 (Sharding) | Q164 (Binary log) | Q242 (SELECT FOR UPDATE) | Q157 (Zero-downtime migrations)
