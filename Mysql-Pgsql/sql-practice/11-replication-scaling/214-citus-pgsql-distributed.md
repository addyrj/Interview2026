---

# Q214. Citus — PgSQL Distributed
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL

---

## ❓ Question
How does Citus turn PostgreSQL into a distributed database? Explain distributed vs reference tables, co-location, and how queries are routed.

---

## 💡 Quick Concept (2 lines only)
Citus is a Postgres extension: a coordinator holds metadata, tables are hash-sharded by a distribution column into shards spread over worker nodes, and the planner pushes queries down to workers.
हिंदी: Citus एक Postgres extension है — coordinator metadata रखता है, tables distribution column से shards में बँटकर workers पर रहती हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: Citus is an extension that PGlite does not provide, so
-- create_distributed_table etc. were not executed. The in-server analogue
-- (HASH partitioning) WAS run on PGlite 18.6; see the end.
-- ============================================

-- Coordinator (NOT RUN):
CREATE EXTENSION citus;        -- needs shared_preload_libraries = 'citus'

SELECT citus_add_node('worker1', 5432);
SELECT citus_add_node('worker2', 5432);

CREATE TABLE tenants (
  tenant_id BIGINT PRIMARY KEY,
  name      TEXT
);
CREATE TABLE orders (
  tenant_id BIGINT,
  order_id  BIGINT,
  total     NUMERIC(10,2),
  PRIMARY KEY (tenant_id, order_id)        -- PK/unique must include distribution column
);
CREATE TABLE countries (code TEXT PRIMARY KEY, name TEXT);

SELECT create_distributed_table('orders',  'tenant_id');          -- 32 shards by default
SELECT create_distributed_table('tenants', 'tenant_id', colocate_with => 'orders');
SELECT create_reference_table('countries');                       -- full copy on every node

-- Routed to ONE worker (filter on distribution column):
SELECT * FROM orders WHERE tenant_id = 42;

-- Co-located join: executes locally on each worker, in parallel:
SELECT t.name, SUM(o.total)
FROM tenants t JOIN orders o USING (tenant_id)
GROUP BY t.name;

-- Parallel aggregate across all shards (partial agg on workers, final on coordinator):
SELECT COUNT(*), AVG(total) FROM orders;

-- Inspect (NOT RUN):
SELECT * FROM citus_shards LIMIT 5;
EXPLAIN SELECT * FROM orders WHERE tenant_id = 42;
-- Custom Scan (Citus Adaptive)  Task Count: 1  (single-shard fast path)

-- Rebalance after adding a worker (NOT RUN):
SELECT citus_rebalance_start();

-- ============================================
-- What WAS run: PGlite 18.6 native hash partitioning
-- ============================================
CREATE TABLE ev (id INT, tenant INT) PARTITION BY HASH (tenant);
CREATE TABLE ev_0 PARTITION OF ev FOR VALUES WITH (MODULUS 2, REMAINDER 0);
CREATE TABLE ev_1 PARTITION OF ev FOR VALUES WITH (MODULUS 2, REMAINDER 1);
INSERT INTO ev SELECT g, g % 5 FROM generate_series(1, 20) g;

SELECT tableoid::regclass AS shard, COUNT(*) FROM ev GROUP BY 1 ORDER BY 1;
-- shard | count
-- ev_0  | 12
-- ev_1  | 8
-- Citus does the same hashing idea, but each shard lives on a different server.
```

MySQL equivalent: Vitess (Q213).

---

## 🔍 Why This Works (3 lines max)
Rows with the same distribution-column value always land in the same shard, so any query filtered or joined on that column runs entirely on one worker. Small lookup tables become reference tables replicated everywhere so joins to them never cross nodes.
हिंदी: Distribution column की value से row हमेशा एक ही shard में जाती है; छोटी lookup tables हर node पर copy रहती हैं।

---

## ⚡ Alternative Solution

```sql
-- Schema-based sharding (Citus 12+): one schema per tenant, no code change (NOT RUN)
SELECT citus_schema_distribute('tenant_acme');

-- Columnar storage for analytics (NOT RUN):
CREATE TABLE events_archive (...) USING columnar;

-- Single node first: if data < ~1-2 TB, partitioning + read replicas is simpler.
-- Managed: Azure Cosmos DB for PostgreSQL (Citus).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Distributing by a non-join column, then joining on another: forces repartition/
--    shuffle joins (slow) or errors.
-- ❌ Forgetting the distribution column in PRIMARY KEY / UNIQUE -> create_distributed_table fails.
-- ❌ Running cross-shard multi-statement transactions at high rate: 2PC overhead.
-- ✅ Pick tenant_id (or the dominant join key), include it in every table and PK,
--    and make small dimension tables reference tables.
```

---

## 🎯 Interview Tip (1 line)
Say: "Citus is my pick when Postgres compatibility matters: multi-tenant SaaS shards by tenant_id with co-located tables for single-node joins, dimension tables as reference tables, and I know the cost is that queries without the distribution column fan out to every shard."

---

## 🔗 Related Questions
→ Q210 (shard key) | Q212 (cross-shard queries) | Q213 (Vitess) | Q209 (logical replication)
