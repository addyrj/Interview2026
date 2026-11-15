---

# Q116. Connection Pooling — PgBouncer, Why Needed
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (MySQL equivalent noted)

---

## ❓ Question
Your 40 app pods each open 20 connections to PostgreSQL (`max_connections = 100`) and the database falls over with "too many clients" even though CPU is idle. Why does PostgreSQL need a connection pooler like PgBouncer, which pool mode should you choose, and what breaks in transaction mode?

---

## 💡 Quick Concept (2 lines only)
Each PostgreSQL connection is a separate OS process (several MB of RAM plus planner/backend overhead), so thousands of mostly idle connections hurt. PgBouncer multiplexes many client connections onto a few real server connections.
हिंदी: Postgres में हर connection एक अलग process है (भारी); PgBouncer हज़ारों client connections को कुछ ही असली server connections पर चलाता है।

---

## ✅ Answer / Solution

```sql
-- NOT RUN: PgBouncer is a separate daemon; there is no server in this sandbox.
-- Only the SHOW/SELECT checks marked "verified" were executed (PGlite 18.6 / MySQL 9.1.0).

-- ============================================
-- SETUP (run this first) - measure what you have
-- ============================================

SHOW max_connections;                                   -- verified: 100 (PGlite default)
SELECT count(*) FROM pg_stat_activity;                  -- verified: 1 (PGlite = single connection)

-- On a real server, see who is wasting slots:
SELECT state, count(*)
FROM pg_stat_activity
WHERE backend_type = 'client backend'
GROUP BY state
ORDER BY count(*) DESC;
-- typical bad picture: 'idle' = 380, 'active' = 6

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: install PgBouncer between app and DB; app points to port 6432.
-- /etc/pgbouncer/pgbouncer.ini  (config, not run)
-- [databases]
-- shopdb = host=10.0.1.10 port=5432 dbname=shopdb
--
-- [pgbouncer]
-- listen_addr         = 0.0.0.0
-- listen_port         = 6432
-- auth_type           = scram-sha-256
-- auth_file           = /etc/pgbouncer/userlist.txt
-- pool_mode           = transaction     ; session | transaction | statement
-- max_client_conn     = 2000            ; app side can be huge
-- default_pool_size   = 20              ; REAL connections per db/user pair
-- reserve_pool_size   = 5
-- server_idle_timeout = 600
-- max_prepared_statements = 100         ; PgBouncer 1.21+: lets prepared statements work in transaction mode

-- Step 2: app connection string
--   postgresql://app_user:***@pgbouncer-host:6432/shopdb

-- Step 3: observe the pool (connect to the special 'pgbouncer' db)
-- psql -p 6432 pgbouncer -c "SHOW POOLS;"
-- psql -p 6432 pgbouncer -c "SHOW STATS;"

-- Step 4: size the pool: connections ~ (CPU cores x 2) + effective spindles (rule of thumb)
-- 8-core DB -> default_pool_size 16-30 is usually plenty.

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- SHOW POOLS (illustrative shape, NOT real output):
-- database | user     | cl_active | cl_waiting | sv_active | sv_idle | pool_mode
-- shopdb   | app_user | 18        | 0          | 18        | 2       | transaction
-- 800 app connections share 20 real ones; cl_waiting > 0 for long = pool too small.
```

---

## 🔍 Why This Works (3 lines max)
Most application connections are idle most of the time; in transaction mode PgBouncer hands a server connection to a client only for the duration of one transaction, then returns it to the pool. Fewer backend processes means less memory, less context switching and lower lock-table / snapshot overhead.
हिंदी: Transaction mode में server connection सिर्फ़ transaction के दौरान client को मिलता है, फिर pool में वापस; इससे memory और process overhead घटता है।

---

## ⚡ Alternative Solution

```sql
-- Pool modes
--   session     : client keeps server conn until disconnect (safest, least savings)
--   transaction : best ratio; breaks session state (see mistakes)
--   statement   : only autocommit single statements; no multi-statement transactions

-- Alternatives to PgBouncer: PgCat, Odyssey, pgpool-II (more features, more complexity),
-- or application pool only (HikariCP, SQLAlchemy QueuePool) - good for ONE service, but
-- 40 pods x pool size still multiplies, which is why a central pooler helps.

-- MySQL difference: threads (not processes) are cheaper, so max_connections is often 150-2000.
-- Verified on 9.1.0: @@max_connections = 151, @@thread_cache_size = 9.
-- Poolers for MySQL: ProxySQL (query routing + multiplexing), or app-level pools.
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Max_used_connections';    -- high-water mark; tune max_connections from this
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Raising max_connections to 2000 as the "fix": more backends = more RAM (work_mem x
--    connections), more contention; throughput usually gets WORSE.
-- ❌ Transaction mode + session features: these do not survive between transactions
SET search_path = tenant_42;           -- lost on the next transaction (use SET LOCAL inside a txn)
SELECT pg_advisory_lock(1);            -- session-level advisory lock may unlock on another backend
LISTEN order_events;                   -- LISTEN/NOTIFY needs session mode
-- Also: WITH HOLD cursors, temp tables across transactions, old-style named prepared statements.
-- ✅ Use SET LOCAL, pg_advisory_xact_lock, or keep those clients on a session-mode pool.
```

---

## 🎯 Interview Tip (1 line)
Say: "PostgreSQL forks a process per connection, so I keep real connections near cores x 2-4 and put PgBouncer in transaction mode in front; I audit for session state (SET, advisory locks, LISTEN, prepared statements) before switching modes."

---

## 🔗 Related Questions
→ Q113 (Prepared statements) | Q115 (Bloat / idle-in-transaction) | Q129 (Deadlock example) | Q121 (Isolation levels)
