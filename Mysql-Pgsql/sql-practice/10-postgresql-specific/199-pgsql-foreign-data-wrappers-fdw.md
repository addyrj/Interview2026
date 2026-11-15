---

# Q199. PgSQL Foreign Data Wrappers (FDW)
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL contrast: FEDERATED engine)

---

## ❓ Question
The reporting database needs to query the `customers` table living in another PostgreSQL server (and ideally a CSV file) without copying data. How do FDWs work and how do you set one up with `postgres_fdw`?

---

## 💡 Quick Concept (2 lines only)
An FDW lets you query external data as if it were a local table: define a SERVER, a USER MAPPING, then a FOREIGN TABLE. The planner can push WHERE/JOIN/aggregates down to the remote side.
हिंदी: FDW से बाहर का data (दूसरा Postgres, CSV वगैरह) local table की तरह query होता है: SERVER, USER MAPPING, फिर FOREIGN TABLE।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP -- PostgreSQL
-- postgres_fdw / file_fdw are contrib extensions: NOT available in PGlite
-- (CREATE EXTENSION postgres_fdw -> "extension is not available"), so the
-- postgres_fdw block below is NOT RUN. The generic DDL objects were run (see output).
-- ============================================

-- ============================================
-- SOLUTION (postgres_fdw)  [not run]
-- ============================================

-- Step 1: extension (superuser or trusted)
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Step 2: describe the remote server
CREATE SERVER crm_server
  FOREIGN DATA WRAPPER postgres_fdw
  OPTIONS (host 'crm-db.internal', port '5432', dbname 'crm');

-- Step 3: map local role -> remote credentials
CREATE USER MAPPING FOR reporting_user
  SERVER crm_server
  OPTIONS (user 'readonly_report', password 'S3cret!');

-- Step 4: expose remote tables (all at once, or one by one)
CREATE SCHEMA crm_remote;
IMPORT FOREIGN SCHEMA public LIMIT TO (customers)
  FROM SERVER crm_server INTO crm_remote;

-- Step 5: query it, even join with local tables
SELECT o.id, o.amount, c.name
FROM orders o
JOIN crm_remote.customers c ON c.id = o.customer_id
WHERE o.created_at >= current_date - 7;

-- Check pushdown: look for "Remote SQL:" in the plan
EXPLAIN (VERBOSE, COSTS OFF)
SELECT * FROM crm_remote.customers WHERE id = 42;
-- Foreign Scan on crm_remote.customers
--   Remote SQL: SELECT id, name, ... FROM public.customers WHERE ((id = 42))   <- illustrative

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Real PGlite run of the generic objects (a dummy wrapper with no handler):
--   CREATE FOREIGN DATA WRAPPER dummy_fdw;                     -> ok
--   CREATE SERVER remote_srv FOREIGN DATA WRAPPER dummy_fdw OPTIONS (host 'x');  -> ok
--   SELECT srvname, srvoptions FROM pg_foreign_server;         -> remote_srv | {host=x}
--   CREATE FOREIGN TABLE ft (id INT) SERVER remote_srv;        -> ok (listed in information_schema.foreign_tables)
--   SELECT * FROM ft;  -> ERROR: foreign-data wrapper "dummy_fdw" has no handler
-- i.e. the catalog objects exist, but a real wrapper (the .so handler) does the actual IO.
-- The postgres_fdw query results are NOT verified.
```

---

## 🔍 Why This Works (3 lines max)
A wrapper is a handler library that implements scan callbacks; `postgres_fdw` opens a connection per (server, user) and ships generated SQL. With `use_remote_estimate` and pushdown of filters/joins/sorts, only the needed rows cross the network.
हिंदी: Wrapper एक handler library है; postgres_fdw remote को SQL भेजता है और filters pushdown होने से सिर्फ ज़रूरी rows आती हैं।

---

## ⚡ Alternative Solution

```sql
-- file_fdw: query a CSV as a table (read-only)  [not run]
CREATE EXTENSION file_fdw;
CREATE SERVER csv_srv FOREIGN DATA WRAPPER file_fdw;
CREATE FOREIGN TABLE price_feed (sku TEXT, price NUMERIC)
  SERVER csv_srv OPTIONS (filename '/data/prices.csv', format 'csv', header 'true');

-- Tuning postgres_fdw
ALTER SERVER crm_server OPTIONS (ADD use_remote_estimate 'true', ADD fetch_size '10000');

-- Persist a remote result locally when the join is heavy:
CREATE MATERIALIZED VIEW local_customers AS SELECT * FROM crm_remote.customers;

-- MySQL: FEDERATED engine (disabled by default; needs --federated) maps ONE remote MySQL table:
--   CREATE TABLE customers_fed (...) ENGINE=FEDERATED CONNECTION='mysql://user:pw@host:3306/crm/customers';
-- Weak pushdown, MySQL-to-MySQL only. Not run here.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Joining a huge local table with a huge foreign table and expecting it to be fast
-- The join may run locally after pulling every remote row over the network.
-- ✅ Filter remotely (WHERE on foreign table), check EXPLAIN VERBOSE for "Remote SQL",
--    or materialize/replicate the data

-- ❌ Storing the remote password in plain USER MAPPING options without restricting access
-- ✅ Restrict who can read pg_user_mappings, use a least-privilege read-only remote role,
--    and prefer certificate/scram auth

-- ❌ Using FDW in OLTP hot paths: each query has network latency + remote failure modes
```

---

## 🎯 Interview Tip (1 line)
Say: "FDW is great for migrations, cross-database reporting and ad-hoc access, but I verify pushdown via EXPLAIN VERBOSE and avoid it on hot OLTP paths; for continuous sync I would use logical replication or CDC instead."

---

## 🔗 Related Questions
→ Q198 (Logical vs physical replication) | Q193 (Materialized views) | Q245 (100M-row migration)
