---

# Q233. How Does Replication Work?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Explain how replication works in MySQL and in PostgreSQL: what is shipped (binlog vs WAL), how the replica applies it, sync vs async, replication lag, and what you must watch in production. Show the log that replication is built from.

---

## 💡 Quick Concept (2 lines only)
The primary writes every change to a sequential log (MySQL binlog, PostgreSQL WAL); replicas stream that log and replay it. MySQL replicates logical row events via an IO thread + SQL/applier thread; PostgreSQL streams physical WAL (or logical decoding for selected tables); default is asynchronous, so replicas can lag.
हिंदी: Primary हर बदलाव log में लिखता है, replica वह log stream करके दोबारा चलाता है; default async है इसलिए lag हो सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE ledger (id INT PRIMARY KEY, note VARCHAR(20));

-- ============================================
-- PART 1 — MySQL: look at the replication source (RUN on MySQL 9.1 single server; binlog is ON by default)
-- ============================================

SELECT @@log_bin, @@binlog_format, @@server_id, @@gtid_mode, @@binlog_row_image;
-- Result:
-- log_bin | binlog_format | server_id | gtid_mode | binlog_row_image
-- 1       | ROW           | 1         | OFF       | FULL
-- (ROW = ship the changed row images, the safe default; STATEMENT replays SQL text and can diverge)

INSERT INTO ledger VALUES (1, 'hello');
UPDATE ledger SET note = 'world' WHERE id = 1;

SHOW BINARY LOG STATUS;                  -- 9.x name (8.0: SHOW MASTER STATUS)
-- Result: File = binlog.000001, Position = 19957913 (position grows with every write; yours will differ)

SHOW BINLOG EVENTS IN 'binlog.000001' FROM 19957389;
-- Result (what a replica receives):
-- Pos      | Event_type | Info
-- 19957389 | Query      | BEGIN
-- 19957464 | Table_map  | table_id: 155 (t233.ledger)
-- 19957524 | Write_rows | table_id: 155 flags: STMT_END_F        <- the INSERT
-- 19957570 | Xid        | COMMIT /* xid=695 */
-- ...        Query BEGIN, Table_map, Update_rows, Xid COMMIT      <- the UPDATE

-- Decoded row event (mysqlbinlog --base64-output=decode-rows -v):
-- ### UPDATE `t233`.`ledger`
-- ###   WHERE @1=1 @2='hello'        <- before image
-- ###   SET   @1=1 @2='world'        <- after image

-- ============================================
-- PART 2 — MySQL replica setup (commands only; NOT RUN: needs a second server)
-- ============================================

-- primary my.cnf:   server_id=1  log_bin=binlog  gtid_mode=ON  enforce_gtid_consistency=ON
-- replica my.cnf:   server_id=2  relay_log=relay-bin  read_only=ON  super_read_only=ON  gtid_mode=ON  enforce_gtid_consistency=ON

-- On primary:
CREATE USER 'repl'@'%' IDENTIFIED BY '********';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

-- On replica (MySQL 8.0.23+ syntax):
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='10.0.0.11', SOURCE_USER='repl', SOURCE_PASSWORD='********',
  SOURCE_AUTO_POSITION=1;                -- GTID based, no file/position bookkeeping
START REPLICA;
SHOW REPLICA STATUS\G
-- Watch: Replica_IO_Running=Yes, Replica_SQL_Running=Yes, Seconds_Behind_Source, Last_Error
-- Flow: primary binlog -> [IO thread] -> relay log on replica -> [SQL/applier threads] -> data
-- (On our single test server SHOW REPLICA STATUS returns an empty set - it is not a replica.)

-- ============================================
-- PART 3 — PostgreSQL (physical streaming replication; NOT RUN: PGlite is one embedded instance)
-- ============================================

-- What PGlite does confirm: WAL position advances with each write
SHOW wal_level;                           -- replica
SELECT pg_current_wal_lsn();              -- e.g. 0/171D788 (before INSERT)
INSERT INTO ledger VALUES (1, 'hello');
SELECT pg_current_wal_lsn();              -- e.g. 0/171D898 (advanced: the change is in WAL)
CREATE PUBLICATION pub_ledger FOR TABLE ledger;   -- logical replication object is created fine
-- But logical slots fail: ERROR: logical decoding requires "wal_level" >= "logical"

-- primary postgresql.conf:   wal_level=replica (logical for logical repl)  max_wal_senders=10  hot_standby=on
-- primary pg_hba.conf:       host replication repl 10.0.0.0/24 scram-sha-256
-- standby bootstrap:         pg_basebackup -h primary -U repl -D /var/lib/postgresql/data -R -X stream
--                            (-R writes standby.signal + primary_conninfo)
-- Monitoring on primary:
SELECT client_addr, state, sent_lsn, replay_lsn, replay_lag FROM pg_stat_replication;
-- On standby:  SELECT pg_is_in_recovery();  SELECT now() - pg_last_xact_replay_timestamp() AS lag;
-- Synchronous: synchronous_standby_names = 'FIRST 1 (replica1, replica2)'; synchronous_commit = on|remote_apply
-- Logical (per table, cross-version, selective):
--   primary: CREATE PUBLICATION p FOR TABLE ledger;    subscriber: CREATE SUBSCRIPTION s CONNECTION '...' PUBLICATION p;
```

---

## 🔍 Why This Works (3 lines max)
Both engines already write a durable ordered log for crash recovery; replication just ships that same log to another server and replays it in order. Physical (WAL) replicas are byte-identical copies; MySQL's logical row events allow different versions/engines but replay is slower when single-threaded.
हिंदी: Crash recovery वाला log ही replica को भेजा जाता है, इसलिए replica उसी क्रम में बदलाव दोहराकर primary जैसा बन जाता है।

---

## ⚡ Alternative Solution

```sql
-- Modes
--   Async (default): commit returns before replica receives it -> fast, but failover can lose last transactions.
--   Semi-sync (MySQL plugin) / synchronous_commit (PG): wait for >=1 replica ack -> no loss, higher latency.
--   Group Replication / InnoDB Cluster (MySQL), Patroni + etcd (PostgreSQL): automatic failover + consensus.
-- Lag causes: single-threaded apply (use replica_parallel_workers / binlog_transaction_dependency_tracking),
--   big transactions, long queries on a PG standby conflicting with replay (hot_standby_feedback / max_standby_streaming_delay),
--   network, slow replica disks.
-- Read scaling pattern: writes -> primary, reads -> replicas; read-your-own-writes needs routing to primary
--   (or wait for GTID: WAIT_FOR_EXECUTED_GTID_SET()) for a short time after a write.
-- Replication is NOT a backup: a DROP TABLE replicates instantly. Keep PITR (binlog / WAL archive) backups.
-- (None of the replica-side commands above were executed here.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: reading from a replica right after a write and assuming it is there (async lag)
-- ❌ Wrong: STATEMENT-based binlog with non-deterministic functions (UUID(), NOW() subtleties) -> replica drift
-- ❌ Wrong: leaving replicas writable (writes on replica break replication or diverge data)
-- ❌ Wrong: tables without a primary key in ROW format -> replica scans whole table per row change
-- ❌ Wrong: treating replication as backup, or not monitoring lag / Replica_SQL_Running
-- ✅ Correct: GTID + ROW format, read_only replicas, lag alerts, PKs everywhere, tested failover and real backups
```

---

## 🎯 Interview Tip (1 line)
Say: "MySQL ships ROW binlog events through an IO thread to a relay log applied by SQL workers, PostgreSQL streams WAL byte-for-byte (or logical decoding for per-table); it is async by default so I design for replica lag, use semi-sync or synchronous_commit where RPO must be zero, monitor lag, and never treat replication as a backup."

---

## 🔗 Related Questions
→ Q219 (blue-green DB deployment) | Q220 (zero-downtime migration) | Q226 (MVCC) | Q234 (connection pooling)
