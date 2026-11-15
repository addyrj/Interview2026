---

# Q215. Connection Pooling — PgBouncer Modes
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL

---

## ❓ Question
Why does PostgreSQL need an external connection pooler, and how do PgBouncer's session, transaction and statement pooling modes differ? Which features break in transaction mode?

---

## 💡 Quick Concept (2 lines only)
Each Postgres connection is a full OS process (several MB), so thousands of app connections hurt; PgBouncer multiplexes many client connections onto a small pool of server connections.
हिंदी: हर Postgres connection एक process है (महंगा); PgBouncer हज़ारों client connections को कुछ ही server connections पर multiplex करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: PgBouncer is not installed here. The SQL checks below WERE run
-- on PGlite 18.6 (single connection, so counts are trivially small).
-- ============================================

-- Server limits and current usage
SHOW max_connections;                         -- Real PGlite: 100
SELECT COUNT(*) FROM pg_stat_activity;        -- Real PGlite: 1
-- On a real server:
SELECT state, COUNT(*) FROM pg_stat_activity GROUP BY state;
-- state               | count
-- active              | 12
-- idle                | 380       <- the waste PgBouncer removes
-- idle in transaction | 5

-- ============================================
-- pgbouncer.ini (NOT RUN)
-- ============================================
-- [databases]
-- shop = host=10.0.0.1 port=5432 dbname=shop
--
-- [pgbouncer]
-- listen_port        = 6432
-- auth_type          = scram-sha-256
-- auth_file          = /etc/pgbouncer/userlist.txt
-- pool_mode          = transaction        # session | transaction | statement
-- max_client_conn    = 5000               # app-side connections accepted
-- default_pool_size  = 20                 # server connections per (db,user)
-- reserve_pool_size  = 5
-- server_idle_timeout = 600
-- max_prepared_statements = 100           # 1.21+: prepared stmts in txn mode

-- Admin console:  psql -p 6432 -U pgbouncer pgbouncer
SHOW POOLS;
-- database | user | cl_active | cl_waiting | sv_active | sv_idle | pool_mode
-- shop     | app  | 20        | 0          | 20        | 0       | transaction  (illustrative)
SHOW STATS;

-- ============================================
-- Modes
-- ============================================
-- session     : server conn pinned for the whole client session. Safest; least
--               multiplexing (good for apps with long sessions / migrations).
-- transaction : server conn held only between BEGIN and COMMIT. Best ratio (typical).
-- statement   : returned after every statement; multi-statement txns NOT allowed.
--
-- BREAKS in transaction mode (state lives on the server connection):
--   SET / RESET (use SET LOCAL inside a txn), session advisory locks,
--   LISTEN/NOTIFY, WITH HOLD cursors, temp tables across txns,
--   protocol-level PREPARE (older PgBouncer), session_replication_role.

BEGIN;
SET LOCAL statement_timeout = '5s';   -- ✅ scoped to this transaction, pool-safe
SELECT pg_advisory_xact_lock(42);     -- ✅ xact lock released at COMMIT
COMMIT;
-- ❌ SELECT pg_advisory_lock(42);    -- session lock: may be held by another client's slot
```

MySQL equivalent: ProxySQL multiplexing (Q206) or the app-side pool (HikariCP); MySQL threads are lighter, so pooling matters less, but ProxySQL helps at high fan-in.

---

## 🔍 Why This Works (3 lines max)
Most app connections are idle most of the time, so in transaction mode a few dozen server connections can serve thousands of clients. The price is that anything session-scoped is no longer reliable between transactions.
हिंदी: ज़्यादातर connections idle रहते हैं, इसलिए transaction mode में कुछ दर्जन server connections हज़ारों clients संभाल लेते हैं; session state भरोसेमंद नहीं रहती।

---

## ⚡ Alternative Solution

```sql
-- App-side pool only (HikariCP/pgx pool): fine for few app instances; breaks down when
-- 200 pods x 20 conns = 4000 connections. Put PgBouncer between.
-- Pgpool-II: pooling + load balancing + failover, heavier than PgBouncer.
-- Odyssey / PgCat: multithreaded poolers (PgBouncer is single-threaded: ~1 core cap).
-- Managed: RDS Proxy, Supavisor.

-- Size the pool by cores, not by clients: default_pool_size ~ (cores * 2) + spindles
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Setting max_connections = 5000 on Postgres instead of pooling: memory per backend,
--    snapshot/lock-table overhead, performance drops.
-- ❌ Transaction mode + session-level SET search_path / SET ROLE: next client inherits it
--    or loses it. ✅ Use SET LOCAL, or per-role defaults: ALTER ROLE app SET search_path = shop;
-- ❌ Using LISTEN/NOTIFY or session advisory locks through transaction pooling.
--    ✅ Give those clients a direct connection or a session-mode pool.
-- ❌ Forgetting 'idle in transaction' clients pin a server connection: set
--    idle_in_transaction_session_timeout.
```

---

## 🎯 Interview Tip (1 line)
Say: "Postgres is process-per-connection, so I cap server connections near cores x 2-4 and front it with PgBouncer in transaction mode, using SET LOCAL and xact-level advisory locks, a direct or session-mode path for LISTEN/migrations, and watch cl_waiting and avg_wait_time to size the pool."

---

## 🔗 Related Questions
→ Q206 (ProxySQL) | Q216 (database proxy) | Q208 (Patroni) | Q207 (streaming replication)
