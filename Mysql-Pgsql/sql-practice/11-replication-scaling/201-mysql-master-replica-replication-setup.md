---

# Q201. MySQL Master-Replica Replication Setup
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (8.0.23+ / 9.x syntax; older names in comments)

---

## ❓ Question
Set up an asynchronous MySQL source (master) to replica (slave) replication using GTIDs, from creating the replication user to verifying `Replica_IO_Running` and `Replica_SQL_Running`.

---

## 💡 Quick Concept (2 lines only)
The source writes changes to its binary log; the replica's IO thread copies them into a relay log, and the SQL thread replays them. GTIDs give every transaction a global ID so the replica can auto-position instead of tracking file+offset.
हिंदी: Source binlog लिखता है, replica का IO thread उसे relay log में लाता है और SQL thread replay करता है; GTID से file/position याद रखना नहीं पड़ता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP -- MySQL  (needs TWO servers: the full end-to-end flow is NOT RUN here.
--   What I did run on a single MySQL 9.1.0: the user/grant, status commands,
--   variable checks, and a CHANGE REPLICATION SOURCE pointing at a dead port.)
-- ============================================

-- ---------- my.cnf on the SOURCE ----------
-- [mysqld]
-- server_id                = 1
-- log_bin                  = binlog           # default ON in 8.0+ (verified ON on 9.1)
-- binlog_format            = ROW              # verified default
-- gtid_mode                = ON
-- enforce_gtid_consistency = ON
-- sync_binlog              = 1                # verified default; durable
-- ---------- my.cnf on the REPLICA ----------
-- [mysqld]
-- server_id                = 2                # MUST differ
-- gtid_mode                = ON
-- enforce_gtid_consistency = ON
-- relay_log                = relay-bin
-- read_only                = ON
-- super_read_only          = ON
-- replica_parallel_workers = 4                # verified default is 4 on 9.1

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1 (SOURCE): replication account                      [RUN OK on 9.1]
CREATE USER 'repl'@'%' IDENTIFIED BY 'Repl#Pass123';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- Step 2 (SOURCE): seed the replica with a consistent snapshot  [not run]
--   mysqldump --all-databases --single-transaction --source-data=2 --set-gtid-purged=ON > seed.sql
--   (or MySQL Clone plugin / XtraBackup for big datasets); load seed.sql on the replica

-- Step 3 (REPLICA): point at the source                    [syntax RUN OK; target dead]
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST = '10.0.0.10',
  SOURCE_PORT = 3306,
  SOURCE_USER = 'repl',
  SOURCE_PASSWORD = 'Repl#Pass123',
  SOURCE_AUTO_POSITION = 1,            -- GTID mode
  SOURCE_SSL = 1;
-- Without GTID: SOURCE_LOG_FILE='binlog.000001', SOURCE_LOG_POS=4 instead of AUTO_POSITION

START REPLICA;                          -- pre-8.0.22: START SLAVE

-- Step 4: verify
SHOW REPLICA STATUS\G                   -- pre-8.0.22: SHOW SLAVE STATUS
-- On the SOURCE:
SHOW BINARY LOG STATUS;                 -- 8.4/9.x ; older: SHOW MASTER STATUS

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Healthy replica (documented values, NOT from a live pair):
--   Replica_IO_Running: Yes
--   Replica_SQL_Running: Yes
--   Seconds_Behind_Source: 0
--   Last_IO_Error:  (empty)
-- REAL output I got on MySQL 9.1.0 (single server):
--   SHOW BINARY LOG STATUS ->  File: binlog.000001 | Position: 690 | Executed_Gtid_Set: (empty, gtid_mode=OFF)
--   defaults: gtid_mode OFF, binlog_format ROW, sync_binlog 1, read_only 0, replica_parallel_workers 4,
--             binlog_expire_logs_seconds 2592000 (30 days)
--   Pointing REPLICA at an unreachable source -> after START REPLICA:
--     Replica_IO_Running: Connecting | Replica_SQL_Running: Yes | Seconds_Behind_Source: NULL
--     Last_IO_Error: Error connecting to source 'repl@127.0.0.1:33999'. This was attempt 1/10,
--                    with a delay of 60 seconds between attempts. Message: Can't connect ... (61)
```

---

## 🔍 Why This Works (3 lines max)
`SOURCE_AUTO_POSITION=1` makes the replica send its executed GTID set, and the source streams only the missing transactions, which makes re-pointing and failover simple. Replication is asynchronous: the source commits without waiting for any replica.
हिंदी: AUTO_POSITION में replica अपना GTID set भेजता है और source सिर्फ बाकी transactions भेजता है; replication async है, source इंतज़ार नहीं करता।

---

## ⚡ Alternative Solution

```sql
-- Semi-sync (a replica ACKs receipt before commit returns): less data loss on source crash
-- (8.0.26+ names)  INSTALL PLUGIN rpl_semi_sync_source SONAME 'semisync_source.so';
--                  SET GLOBAL rpl_semi_sync_source_enabled = 1;       -- not run
-- Group Replication / InnoDB Cluster: multi-node, automatic failover (Q204)

-- Replica hygiene:
SET GLOBAL read_only = 1;          -- verified works; super_read_only also blocks SUPER users
-- Skip nothing blindly; to fix an errant transaction in GTID mode inject an empty transaction:
--   SET GTID_NEXT='uuid:N'; BEGIN; COMMIT; SET GTID_NEXT='AUTOMATIC';

-- PostgreSQL equivalent: streaming replication via pg_basebackup -R (Q198)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Same server_id on source and replica -> replication refuses / loops
-- ❌ Replica writable (read_only=0): app writes there, data diverges, SQL thread breaks later
-- ✅ read_only + super_read_only on replicas

-- ❌ Using statement-based binlog with non-deterministic functions (UUID(), NOW() quirks)
-- ✅ binlog_format=ROW (default in 8.0+)

-- ❌ Passwords/'repl'@'%' open to the world: restrict host ('10.0.0.%') and use SOURCE_SSL
-- ❌ Purging binlogs the replica still needs (binlog_expire_logs_seconds too small) -> error 1236
```

---

## 🎯 Interview Tip (1 line)
Say: "I use GTID with ROW format, unique server_id, a least-privilege REPLICATION SLAVE user over TLS, read_only replicas, multithreaded apply, and I monitor IO/SQL thread state and lag; replication is async, so I would add semi-sync or Group Replication if zero data loss matters."

---

## 🔗 Related Questions
→ Q202 (Replication lag) | Q203 (Read replica routing) | Q204 (Failover) | Q198 (PgSQL replication)
