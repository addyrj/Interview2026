---

# Q207. PgSQL Streaming Replication
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL

---

## ❓ Question
Set up PostgreSQL physical streaming replication (primary + hot standby). Explain sync vs async, replication slots, how to monitor lag, and how to promote a standby.

---

## 💡 Quick Concept (2 lines only)
The standby connects to the primary and streams WAL records (byte-for-byte physical copy) and continuously replays them; hot standby allows read-only queries.
हिंदी: Standby primary से WAL stream लेकर replay करता है — पूरा physical copy, standby पर read-only queries चलती हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: needs two real servers. Only the PGlite checks below were run
-- (PGlite = single-process Postgres 18.6 on WASM, no walsender).
-- ============================================

-- ============================================
-- PRIMARY: postgresql.conf  (NOT RUN)
-- ============================================
-- wal_level = replica                 # default, enough for physical
-- max_wal_senders = 10
-- max_replication_slots = 10
-- hot_standby = on
-- wal_keep_size = 1GB                 # extra safety if no slot
-- synchronous_commit = on
-- # synchronous_standby_names = 'FIRST 1 (standby1, standby2)'   # for sync

-- pg_hba.conf:
-- host replication replicator 10.0.0.0/24 scram-sha-256

CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'Str0ng!Pass';
SELECT pg_create_physical_replication_slot('standby1_slot');

-- ============================================
-- STANDBY: clone primary, create standby.signal  (NOT RUN, shell)
-- ============================================
-- pg_basebackup -h 10.0.0.1 -U replicator -D /var/lib/postgresql/data \
--   -R -X stream -S standby1_slot -C --progress
-- -R writes standby.signal + primary_conninfo into postgresql.auto.conf:
--   primary_conninfo = 'host=10.0.0.1 user=replicator password=... application_name=standby1'
--   primary_slot_name = 'standby1_slot'
-- systemctl start postgresql

-- ============================================
-- MONITOR on primary (NOT RUN, typical result)
-- ============================================
SELECT application_name, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS replay_lag_bytes,
       replay_lag
FROM pg_stat_replication;
-- application_name | state     | sync_state | replay_lag_bytes | replay_lag
-- standby1         | streaming | async      | 0                | 00:00:00.001

-- On standby:
SELECT pg_is_in_recovery(),                    -- true
       pg_last_wal_replay_lsn(),
       now() - pg_last_xact_replay_timestamp() AS time_lag;

-- Slots that retain too much WAL (disk-full risk):
SELECT slot_name, active,
       pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained
FROM pg_replication_slots;

-- ============================================
-- PROMOTE (NOT RUN)
-- ============================================
SELECT pg_promote();            -- or: pg_ctl promote
-- After promotion the old primary must be rebuilt, or rewound with pg_rewind.

-- ============================================
-- What WAS run on PGlite 18.6 (real output)
-- ============================================
SHOW wal_level;          -- replica
SHOW max_wal_senders;    -- 10
SELECT * FROM pg_stat_replication;      -- 0 rows (no standby attached)
SELECT pg_current_wal_lsn();            -- e.g. 0/16EF9D0 (changes per run)
```

MySQL equivalent: binlog-based async/semi-sync replication (logical row events), not byte-level physical copy (see Q205 for Group Replication).

---

## 🔍 Why This Works (3 lines max)
Every change is already written to WAL for crash recovery; the standby just replays the same stream, so it is an exact block-level copy. Sync mode (synchronous_standby_names) makes COMMIT wait for the standby's flush/apply, trading latency for zero data loss.
हिंदी: WAL पहले से बनता है, standby वही replay करता है। Sync में commit standby का इंतज़ार करता है — data loss zero, latency ज़्यादा।

---

## ⚡ Alternative Solution

```sql
-- Tune the sync level per transaction (NOT RUN):
SET synchronous_commit = remote_apply;   -- standby visible-to-readers before ack
-- values: off | local | remote_write | on (=flush on standby) | remote_apply

-- Cascading replication: standby2 streams from standby1 (reduces primary load)
-- primary_conninfo = 'host=standby1 ...'

-- Avoid query cancellations on standby by long reads:
-- hot_standby_feedback = on  (primary keeps old row versions -> bloat risk)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Creating a slot and then forgetting a dead standby -> primary retains WAL
--    forever -> disk full -> primary outage.
-- ✅ Set max_slot_wal_keep_size = 50GB and alert on retained bytes above.

-- ❌ Thinking a replica is a backup. DROP TABLE replicates in milliseconds.
-- ✅ Replication = HA / read scaling; backups + PITR = recovery (Q217, Q218).

-- ❌ Reading from async standby right after write -> stale data.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use physical streaming replication with slots (capped by max_slot_wal_keep_size), async for read replicas and `synchronous_standby_names = ANY 1 (...)` quorum sync for the HA pair, monitor replay lag from pg_stat_replication, and let Patroni handle promotion plus pg_rewind."

---

## 🔗 Related Questions
→ Q208 (Patroni HA) | Q209 (logical replication) | Q218 (PITR) | Q205 (MySQL Group Replication)
