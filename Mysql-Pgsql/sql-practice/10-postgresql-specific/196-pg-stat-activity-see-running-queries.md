---

# Q196. pg_stat_activity — See Running Queries
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: Both (PostgreSQL pg_stat_activity | MySQL PROCESSLIST)

---

## ❓ Question
The API is slow. Find (a) currently running queries sorted by runtime, (b) sessions "idle in transaction", (c) who is blocking whom, and then cancel or kill the culprit.

---

## 💡 Quick Concept (2 lines only)
`pg_stat_activity` has one row per backend with its state, current query, start times and wait event. Pair it with `pg_blocking_pids()`, `pg_cancel_backend()` (cancel query) and `pg_terminate_backend()` (kill connection).
हिंदी: pg_stat_activity में हर connection की state, चल रही query और wait info मिलती है; cancel से query रुकती है, terminate से connection कटता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- PostgreSQL
-- ============================================
-- No tables needed. Needs a role with pg_read_all_stats (or superuser) to see OTHER users' queries.

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: longest-running active queries
SELECT pid, usename, state, wait_event_type, wait_event,
       now() - query_start AS runtime,
       left(query, 80)     AS query_snippet
FROM pg_stat_activity
WHERE state = 'active'
  AND pid <> pg_backend_pid()          -- exclude myself
ORDER BY runtime DESC;

-- Step 2: "idle in transaction" -- holds locks, blocks VACUUM, classic outage cause
SELECT pid, usename, now() - xact_start AS tx_age, left(query, 80) AS last_query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY tx_age DESC;

-- Step 3: who is blocking whom
SELECT pid,
       pg_blocking_pids(pid) AS blocked_by,     -- array of blocker pids
       wait_event_type, left(query, 60) AS waiting_query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;

-- Step 4: act (nicest first)
-- SELECT pg_cancel_backend(12345);      -- cancels current query, keeps connection
-- SELECT pg_terminate_backend(12345);   -- kills the connection, rolls back its tx

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Verified on PGlite (PostgreSQL 18, ONE connection): the view returns exactly 1 row
-- (pid 42, state 'active', backend_type 'standalone backend'), blockers = 0, and the
-- column list is: datid, datname, pid, leader_pid, usesysid, usename, application_name,
-- client_addr, client_hostname, client_port, backend_start, xact_start, query_start,
-- state_change, wait_event_type, wait_event, state, backend_xid, backend_xmin, query_id,
-- query, backend_type.
-- NOT VERIFIED: a real multi-session blocking scenario (needs 2+ connections).
-- On a real server you would see e.g.:
-- pid  | usename | state  | wait_event_type | runtime  | query_snippet
-- 8812 | app     | active | Lock            | 00:02:11 | UPDATE accounts SET balance = ...
-- 8790 | app     | idle in transaction | ... (this one is the blocker: pg_blocking_pids = {8790})
```

---

## 🔍 Why This Works (3 lines max)
Each backend publishes its state into shared memory, and the view reads it live (needs `track_activities = on`, which is the default and was `on` in my run). `wait_event_type = Lock` plus `pg_blocking_pids` points straight at the head of the blocking chain.
हिंदी: हर backend अपनी state shared memory में लिखता है, view उसे live पढ़ता है; Lock wait + blocking_pids से blocker मिल जाता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL 9.1 (verified): classic and sys schema
SHOW FULL PROCESSLIST;
-- Id | User            | Host      | db   | Command | Time | State                  | Info
-- 5  | event_scheduler | localhost | NULL | Daemon  | 308  | Waiting on empty queue | NULL
-- 17 | root            | localhost | NULL | Query   | 0    | init                   | SHOW PROCESSLIST

SELECT ID, USER, COMMAND, TIME, STATE, LEFT(INFO, 80)
FROM information_schema.PROCESSLIST
WHERE COMMAND <> 'Sleep' ORDER BY TIME DESC;       -- information_schema.PROCESSLIST is deprecated
SELECT * FROM sys.processlist;                      -- richer, uses performance_schema
KILL QUERY 17;       -- cancel statement  (PgSQL: pg_cancel_backend)
KILL CONNECTION 17;  -- kill session      (PgSQL: pg_terminate_backend)
-- Blockers in MySQL 8+: SELECT * FROM sys.innodb_lock_waits;

-- Safety net in PostgreSQL, set per role/db:
ALTER ROLE app SET idle_in_transaction_session_timeout = '30s';   -- default is 0 = off (verified)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Killing the BLOCKED session (the one you see complaining)
-- ✅ Follow pg_blocking_pids to the root blocker -- usually an 'idle in transaction' app session

-- ❌ Reaching for pg_terminate_backend first
-- ✅ pg_cancel_backend first; terminate only if cancel doesn't work (terminate rolls back everything)

-- ❌ Reading `query` of an idle session as "what's running"
-- For state = 'idle' / 'idle in transaction', `query` is the LAST statement, not a current one
```

---

## 🎯 Interview Tip (1 line)
Say: "I check pg_stat_activity for active and idle-in-transaction sessions, use pg_blocking_pids to find the root blocker, cancel before terminate, and prevent recurrence with idle_in_transaction_session_timeout and statement_timeout."

---

## 🔗 Related Questions
→ Q195 (Advisory locks) | Q197 (pg_stat_statements) | Q191 (VACUUM held back by long tx) | Q017 (SELECT FOR UPDATE)
