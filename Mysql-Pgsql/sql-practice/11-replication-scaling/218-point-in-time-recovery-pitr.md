---

# Q218. Point-in-Time Recovery (PITR)
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both

---

## ❓ Question
At 14:05 someone ran `DELETE FROM orders` without a WHERE. Explain how to restore the database to 14:04:59 in MySQL and PostgreSQL, and what must be configured beforehand.

---

## 💡 Quick Concept (2 lines only)
PITR = restore a physical base backup, then replay the continuous log (MySQL binlog / PostgreSQL WAL archive) up to a chosen time, LSN or transaction, stopping before the bad statement.
हिंदी: PITR = पुराना base backup restore करो, फिर binlog/WAL को चुने हुए समय तक replay करो — गलती से ठीक पहले रुको।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 -- the binlog facts below were checked on the real server)
-- ============================================
SHOW VARIABLES LIKE 'log_bin';        -- Real: ON
SHOW VARIABLES LIKE 'binlog_format';  -- Real: ROW
SHOW BINARY LOGS;                     -- Real: binlog.000001 | 38537 | No (sizes vary)
SHOW BINARY LOG STATUS;               -- Real: File binlog.000001, Position 38537 (varies)
-- (MySQL 8.2+/9.x: SHOW BINARY LOG STATUS replaces SHOW MASTER STATUS)

-- ============================================
-- MySQL PITR (shell steps, NOT RUN -- standard procedure)
-- ============================================
-- Before incident: log_bin on, binlog_expire_logs_seconds >= backup interval + margin,
--   binlogs copied off-host continuously (mysqlbinlog --read-from-remote-server --raw --stop-never)
--   or at least every few minutes.
--
-- 1) Restore latest full backup to a NEW server (never on top of prod):
--      xtrabackup --prepare ... ; copy-back ; start mysqld
--    (or mysql < full_dump.sql, which recorded SOURCE_LOG_FILE/POS via --source-data=2)
-- 2) Find the exact position of the bad DELETE:
--      mysqlbinlog --base64-output=decode-rows -vv binlog.000042 | grep -n -B5 "DELETE FROM .orders."
-- 3) Replay from the backup coordinates to just before it:
--      mysqlbinlog --start-position=38537 --stop-datetime="2026-11-09 14:04:59" \
--                  binlog.000041 binlog.000042 | mysql -uroot
--    or by position: --stop-position=<pos before the DELETE>
--    GTID: --exclude-gtids='uuid:1234' to skip only the bad transaction and keep later ones
-- 4) Verify counts, then cut over or copy the lost rows back into prod.

-- ============================================
-- PostgreSQL PITR (NOT RUN: needs archiving + a base backup)
-- ============================================
-- Before incident (postgresql.conf):
--   wal_level = replica
--   archive_mode = on
--   archive_command = 'pgbackrest --stanza=main archive-push %p'   # or 'cp %p /arch/%f'
--   (and nightly: pg_basebackup / pgbackrest backup)
--
-- Restore:
--   1) stop PG on the NEW host, empty PGDATA, restore base backup
--   2) postgresql.conf:
--        restore_command = 'pgbackrest --stanza=main archive-get %f "%p"'
--        recovery_target_time = '2026-11-09 14:04:59+00'
--        recovery_target_action = 'pause'      # inspect before promote
--   3) touch $PGDATA/recovery.signal ; start PG
--   4) check data, then:
SELECT pg_is_in_recovery();       -- true while replaying
SELECT pg_wal_replay_resume();    -- or SELECT pg_promote(); when satisfied
-- Other targets: recovery_target_lsn, recovery_target_xid, recovery_target_name
-- Named marker (this DID run on PGlite 18.6, returns an LSN that varies):
SELECT pg_create_restore_point('before_bulk_delete');   -- real: 0/1726200
-- Timeline: after promote, a new timeline starts; archive keeps both histories.

-- Real PGlite fact: SHOW archive_mode;  -- off (default; must be enabled for PITR)
```

---

## 🔍 Why This Works (3 lines max)
The base backup gives a consistent past state; the log holds every later change in order, so replaying it up to a target recreates any moment in between. The recovery target is just where replay stops.
हिंदी: Base backup = पुरानी consistent state, log = उसके बाद के सारे changes; target तक replay करने से किसी भी पल की state मिलती है।

---

## ⚡ Alternative Solution

```sql
-- Managed: RDS "Restore to point in time" / Cloud SQL PITR (creates a NEW instance).
-- Fast logical fix for small mistakes: delayed replica (Q217), then copy rows back.
-- Flashback-style (MySQL, NOT RUN): reverse-apply binlog with tools like binlog2sql /
--   MyFlash on ROW format; PgSQL has no native flashback (use PITR or pg_surgery carefully).
-- Application-level: soft delete + audit table + transaction-time (temporal) tables.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Binlog / WAL archiving never enabled, or binlogs purged before the next backup:
--    gap in the chain -> PITR impossible.
-- ❌ Restoring over production, losing the evidence and any rows written after the target.
-- ✅ Restore to a side server, extract the missing rows, apply selectively.
-- ❌ Wrong timezone in --stop-datetime / recovery_target_time (server vs session TZ).
-- ✅ Prefer position / LSN / GTID targets found by inspecting the log.
-- ❌ Never rehearsing: first real PITR during an outage takes hours of fumbling.
```

---

## 🎯 Interview Tip (1 line)
Say: "PITR needs three things in place before the incident: a recent physical base backup, an unbroken, off-host log chain (binlog or WAL archive), and a rehearsed runbook; I restore to a side instance, stop just before the bad transaction by GTID/LSN, and merge the lost rows back, and I report measured RTO and RPO from drills."

---

## 🔗 Related Questions
→ Q217 (backup strategies) | Q207 (streaming replication) | Q208 (Patroni) | Q205 (Group Replication)
