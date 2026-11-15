---

# Q203. Read Replica — Connection Routing in App
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL; routing is app/proxy level)

---

## ❓ Question
You have one primary and two read replicas. How do you route writes to the primary and reads to replicas from the application, and how do you avoid users seeing stale data right after their own write?

---

## 💡 Quick Concept (2 lines only)
Send writes (and reads inside a transaction) to the primary, other reads to a replica pool, either via app-level routing, a driver feature, or a proxy (ProxySQL, PgBouncer+HAProxy, pgpool). Because replicas lag, add read-your-writes rules.
हिंदी: Writes primary पर, बाकी reads replica pool पर (app, driver या proxy से); replica lag की वजह से अपनी write के बाद read primary से करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
-- Routing lives in the application/proxy, so NOT RUN as SQL on a cluster here.
-- Verified on MySQL 9.1 only the SQL-level guards used by the pattern (read_only flag).

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: replicas must refuse writes (safety net against mis-routing)
SET GLOBAL read_only = 1;                 -- MySQL (verified); add super_read_only = 1
-- PostgreSQL standbys are read-only automatically (hot_standby = on)

-- Step 2: let the app discover role at connect time
SELECT @@read_only;                        -- MySQL:  0 = primary, 1 = replica
SELECT pg_is_in_recovery();                -- PgSQL:  false = primary, true = standby

-- Step 3: app-level routing rules (pseudo-code, NOT RUN)
--   def get_connection(sql, *, in_tx=False, user_wrote_recently=False):
--       is_write = sql.lstrip().split()[0].upper() in {"INSERT","UPDATE","DELETE","REPLACE","ALTER"}
--       if is_write or in_tx or user_wrote_recently:   # read-your-writes
--           return primary_pool.get()
--       return replica_pool.get_round_robin_healthy()
--   after each write: cache.set(f"wrote:{user_id}", 1, ttl=5)   # > typical lag

-- Step 4: proxy-level (ProxySQL) rules, not run
--   INSERT INTO mysql_query_rules (rule_id, active, match_digest, destination_hostgroup, apply)
--   VALUES (1, 1, '^SELECT .* FOR UPDATE', 10, 1),   -- hostgroup 10 = primary
--          (2, 1, '^SELECT',               20, 1);   -- hostgroup 20 = replicas
--   ProxySQL also removes replicas from hostgroup 20 when Seconds_Behind_Source > max_replication_lag.

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Verified on MySQL 9.1.0 : SET GLOBAL read_only=1; SELECT @@read_only; -> 1  (then reset to 0)
-- Everything else here (pools, ProxySQL, tracking recent writes) is illustrative, NOT executed.
-- Expected behaviour: user updates profile -> next 5 s of their reads hit primary -> then replicas.
```

---

## 🔍 Why This Works (3 lines max)
Reads scale horizontally across replicas while a single primary keeps write ordering. The "recently wrote" flag (or GTID wait) hides replication lag from the user without sending all traffic to the primary.
हिंदी: Reads कई replicas में बंट जाती हैं और writes एक primary पर; recent-write flag से user को पुराना data नहीं दिखता।

---

## ⚡ Alternative Solution

```sql
-- Driver-level (no custom code), examples not run:
--  PostgreSQL JDBC/libpq multi-host: jdbc:postgresql://p:5432,r1:5432,r2:5432/db?targetServerType=preferSecondary
--  libpq: host=p,r1,r2 target_session_attrs=read-write   (finds primary)  | =standby (finds a replica)
--  Django: DATABASES = {'default': {...}, 'replica': {...}} + DATABASE_ROUTERS
--  Rails 6+: connects_to database: { writing: :primary, reading: :replica }
--  Spring: AbstractRoutingDataSource keyed on @Transactional(readOnly = true)

-- Strong read-after-write option, MySQL: after a write, capture the GTID, then on the replica
--   SELECT WAIT_FOR_EXECUTED_GTID_SET('3E11FA47-...:1-5', 0.5);  -- 0 = caught up, 1 = timed out -> fall back to primary
-- PostgreSQL: record pg_current_wal_lsn() after write; check pg_last_wal_replay_lsn() >= that LSN on replica.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Routing all SELECTs to replicas, including ones inside a write transaction or right after a write
-- (insert order, then SELECT order -> "not found")
-- ✅ Read-your-writes rules; reads in a transaction go to primary

-- ❌ Using replicas for SELECT ... FOR UPDATE / counters / uniqueness checks
-- ❌ No health check or lag threshold: a broken replica keeps receiving traffic
-- ❌ Sending 100% of reads to replicas for data that must be strongly consistent (payments, inventory)
```

---

## 🎯 Interview Tip (1 line)
Say: "I route writes and transactional reads to the primary, lag-tolerant reads to health-checked replicas via a proxy or driver, enforce read-your-writes with a recent-write window or GTID/LSN wait, and treat strongly consistent data (payments, inventory) as primary-only."

---

## 🔗 Related Questions
→ Q201 (Replication setup) | Q202 (Replication lag) | Q204 (Failover) | Q241 (Sharding)
