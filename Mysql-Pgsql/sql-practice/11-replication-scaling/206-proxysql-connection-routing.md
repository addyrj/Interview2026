---

# Q206. ProxySQL — Connection Routing
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL

---

## ❓ Question
How do you use ProxySQL to split reads and writes across a MySQL primary and replicas without changing application code? Show hostgroups, query rules, and how to verify routing.

---

## 💡 Quick Concept (2 lines only)
ProxySQL sits between app and MySQL, speaks the MySQL protocol, and routes each query to a hostgroup using regex rules (writes to HG 10, reads to HG 20), with pooling and failover.
हिंदी: ProxySQL app और MySQL के बीच बैठकर query rules से writes को primary और reads को replicas पर भेजता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: ProxySQL is not installed here. Config is the standard admin-
-- interface syntax (connect: mysql -uadmin -padmin -h127.0.0.1 -P6032).
-- ============================================

-- Step 1: Define backend servers in hostgroups
--   HG 10 = writer, HG 20 = readers
INSERT INTO mysql_servers (hostgroup_id, hostname, port, weight, max_connections)
VALUES (10, 'db-primary', 3306, 1,    200),
       (20, 'db-replica1', 3306, 100, 200),
       (20, 'db-replica2', 3306, 100, 200),
       (20, 'db-primary',  3306, 1,   200);   -- primary also readable at low weight

-- Step 2: Auto-move servers between HG10/HG20 based on read_only flag
INSERT INTO mysql_replication_hostgroups (writer_hostgroup, reader_hostgroup, comment)
VALUES (10, 20, 'main cluster');

-- Step 3: Monitoring + app users
UPDATE global_variables SET variable_value='proxymon' WHERE variable_name='mysql-monitor_username';
UPDATE global_variables SET variable_value='MonPass!' WHERE variable_name='mysql-monitor_password';
INSERT INTO mysql_users (username, password, default_hostgroup, transaction_persistent)
VALUES ('app', 'AppPass!', 10, 1);    -- default = writer; txn stays on one backend

-- Step 4: Query rules (evaluated in rule_id order, first match with apply=1 wins)
INSERT INTO mysql_query_rules (rule_id, active, match_digest, destination_hostgroup, apply)
VALUES (1, 1, '^SELECT .* FOR UPDATE', 10, 1),   -- locking reads MUST hit primary
       (2, 1, '^SELECT',               20, 1);   -- other SELECTs -> replicas
-- Everything else (INSERT/UPDATE/DELETE/DDL) falls to default_hostgroup 10.

-- Step 5: Persist and activate (ProxySQL has 3 layers: MEMORY -> RUNTIME -> DISK)
LOAD MYSQL SERVERS TO RUNTIME;      SAVE MYSQL SERVERS TO DISK;
LOAD MYSQL USERS TO RUNTIME;        SAVE MYSQL USERS TO DISK;
LOAD MYSQL QUERY RULES TO RUNTIME;  SAVE MYSQL QUERY RULES TO DISK;
LOAD MYSQL VARIABLES TO RUNTIME;    SAVE MYSQL VARIABLES TO DISK;

-- ============================================
-- VERIFY (NOT RUN; typical shape of results)
-- ============================================
SELECT hostgroup, srv_host, status, ConnUsed, Queries, Latency_us
FROM stats_mysql_connection_pool;
-- hostgroup | srv_host    | status | ConnUsed | Queries | Latency_us
-- 10        | db-primary  | ONLINE | 3        | 18200   | 310
-- 20        | db-replica1 | ONLINE | 5        | 91000   | 290
-- 20        | db-replica2 | ONLINE | 4        | 90500   | 330

SELECT hostgroup, digest_text, count_star, sum_time
FROM stats_mysql_query_digest ORDER BY sum_time DESC LIMIT 5;

-- App connects to ProxySQL port 6033 instead of 3306:
--   mysql -uapp -pAppPass! -h127.0.0.1 -P6033
```

PgSQL equivalent: ProxySQL does not speak Postgres (a v3 PG mode is experimental). Use PgBouncer for pooling (Q215) and Pgpool-II or HAProxy + Patroni REST health checks for read/write split.

---

## 🔍 Why This Works (3 lines max)
Rules match the query digest, so the app keeps one connection string while ProxySQL decides the backend. Replication hostgroups watch read_only, so after a failover the new primary moves into HG 10 automatically.
हिंदी: Rules query देखकर hostgroup चुनते हैं; failover में read_only flag देखकर writer अपने-आप बदल जाता है।

---

## ⚡ Alternative Solution

```sql
-- Route by user instead of by regex (simple, safer):
INSERT INTO mysql_users (username, password, default_hostgroup)
VALUES ('app_rw', 'x', 10), ('app_ro', 'y', 20);   -- reporting service uses app_ro

-- Or keep split logic in the app (two DSNs) -> no proxy hop, but every
-- service must implement failover and lag awareness.

-- Replica lag guard: shun replicas lagging > 5s
UPDATE mysql_servers SET max_replication_lag = 5 WHERE hostgroup_id = 20;
LOAD MYSQL SERVERS TO RUNTIME;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Rule "^SELECT" without a FOR UPDATE rule above it -> locking reads go to a
--    replica and fail / lock nothing.
-- ❌ Read-your-writes breaks: INSERT then immediate SELECT lands on a lagging replica.
-- ✅ Wrap in a transaction (transaction_persistent=1), or add a rule that pins
--    the session to HG10 for some seconds, or use GTID-based causal reads.
-- ❌ Editing tables but forgetting LOAD ... TO RUNTIME / SAVE ... TO DISK:
--    change is invisible, or lost on restart.
```

---

## 🎯 Interview Tip (1 line)
Say: "ProxySQL gives read/write split, pooling/multiplexing, query rewrite, mirroring and fast failover without touching app code, but it's another tier to run in HA (a Keepalived pair or a sidecar per app host) and I handle read-your-writes explicitly with transaction pinning."

---

## 🔗 Related Questions
→ Q205 (Group Replication) | Q215 (PgBouncer) | Q216 (database proxy) | Q213 (Vitess)
