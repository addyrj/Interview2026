---

# Q139. WAL (Write-Ahead Log) — What and Why
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL InnoDB redo log + binlog | PostgreSQL WAL) — settings queried on MySQL 9.1.0 and PGlite; crash recovery itself NOT run

---

## ❓ Question
What is the write-ahead log, why does a database write the log before the data pages, how does it give the "D" in ACID, and which settings control the durability vs speed trade-off in MySQL and PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
Changes are first appended sequentially to a log and fsynced at COMMIT; the heavy random writes to data pages happen later in the background. After a crash the log is replayed to restore committed work.
हिंदी: पहले log में sequential लिखो और COMMIT पर fsync करो; data pages बाद में लिखे जाते हैं, और crash के बाद log replay करके committed data वापस मिल जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL / PGlite)
-- ============================================

CREATE TABLE payments (
  id     SERIAL PRIMARY KEY,
  amount NUMERIC(10,2)
);

-- ============================================
-- SOLUTION: watch the WAL position move (PostgreSQL)
-- ============================================

-- Step 1: note current WAL position (LSN = Log Sequence Number)
SELECT pg_current_wal_lsn() AS lsn_before;

-- Step 2: do some writes
INSERT INTO payments (amount) SELECT 10 FROM generate_series(1, 1000);

-- Step 3: position moved forward -> every change was logged first
SELECT pg_current_wal_lsn() AS lsn_after;

-- Step 4: how many bytes of WAL did 1000 inserts generate?
-- pg_wal_lsn_diff(lsn_after, lsn_before)

-- Step 5: look at the knobs
SELECT name, setting FROM pg_settings
WHERE name IN ('wal_level','synchronous_commit','fsync','full_page_writes',
               'wal_segment_size','max_wal_size','checkpoint_timeout')
ORDER BY name;

-- ============================================
-- EXPECTED OUTPUT (real PGlite; LSN values differ each run)
-- ============================================

-- lsn_before = 0/1722C10
-- lsn_after  = 0/1743510            -> 0x20900 = 133,376 bytes of WAL for 1000 rows
-- checkpoint_timeout | 300          (seconds)
-- fsync              | off          <- PGlite only! A real server must keep fsync = on
-- full_page_writes   | on
-- max_wal_size       | 1024         (MB)
-- synchronous_commit | on
-- wal_level          | replica
-- wal_segment_size   | 16777216     (16 MB files)

-- ============================================
-- MySQL (InnoDB): the same idea, two logs
-- ============================================

SHOW VARIABLES WHERE Variable_name IN
  ('innodb_flush_log_at_trx_commit','sync_binlog','innodb_redo_log_capacity',
   'innodb_doublewrite','log_bin');

-- Real MySQL 9.1.0 output:
-- innodb_doublewrite             | ON
-- innodb_flush_log_at_trx_commit | 1          <- fsync redo log at every COMMIT (full ACID)
-- innodb_redo_log_capacity       | 104857600  (100 MB)
-- log_bin                        | ON
-- sync_binlog                    | 1          <- fsync binary log at every COMMIT

SHOW STATUS LIKE 'Innodb_redo_log_current_lsn';   -- LSN, grows with writes (20475741 in our run)
```

---

## 🔍 Why This Works (3 lines max)
Appending to a log is sequential I/O (fast) and one fsync per commit makes the transaction durable; data pages can be flushed lazily because the log can recreate them. Checkpoints bound how much log must be replayed after a crash.
हिंदी: Log में append करना sequential और तेज़ है; एक fsync से commit durable हो जाता है और checkpoint तय करता है crash के बाद कितना log replay करना पड़ेगा।

---

## ⚡ Alternative Solution

```sql
-- Durability vs latency knobs (configs - not benchmarked here)

-- PostgreSQL: relax durability for one non-critical transaction (loses up to ~3x wal_writer_delay
-- of commits on a crash, but NEVER corrupts the database):
SET LOCAL synchronous_commit = off;

-- MySQL: group commit lowers cost; trade-off setting:
-- innodb_flush_log_at_trx_commit = 1  -> fsync every commit (safe, default)
--                                  = 2  -> write to OS cache each commit, fsync ~1/sec (OS crash loses 1s)
--                                  = 0  -> write+fsync ~1/sec (mysqld crash loses 1s)

-- WAL also powers replication and PITR:
-- PgSQL : wal_level = replica/logical, archive_command, streaming replication, pg_basebackup + WAL replay
-- MySQL : the BINLOG (server-level, logical) drives replication; the REDO log (InnoDB) is only for crash recovery.
--         Two logs are kept consistent with an internal 2-phase commit between them.

-- Inspect WAL with pg_waldump (CLI) on a real server:
--   pg_waldump -p $PGDATA/pg_wal 000000010000000000000001
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: turning off fsync / setting innodb_flush_log_at_trx_commit=0 in production
--    "for speed" - a power cut can lose committed transactions (PgSQL fsync=off can corrupt the cluster).
-- ✅ Use synchronous_commit=off (PgSQL) or =2 (MySQL) for specific cases, keep fsync on,
--    and put WAL/redo on fast storage (NVMe, battery-backed cache).

-- ❌ Wrong: believing the redo log and binlog are the same thing.
--    Redo = physical, InnoDB-only, crash recovery. Binlog = logical, server-level, replication/PITR.

-- ❌ Wrong: ignoring WAL growth - an inactive replication slot or failing archive_command
--    makes pg_wal fill the disk. Monitor: SELECT slot_name, active, restart_lsn FROM pg_replication_slots;
```

---

## 🎯 Interview Tip (1 line)
Say: "WAL turns random writes into one sequential fsynced append at commit, gives crash recovery by replay from the last checkpoint, and doubles as the stream for replication and PITR; MySQL splits that into InnoDB redo plus the binlog."

---

## 🔗 Related Questions
→ Q138 (Two-phase commit) | Q134 (MVCC) | Q135 (Long-running transactions) | Q121 (Isolation levels)
