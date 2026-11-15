---

# Q213. Vitess — MySQL Sharding (YouTube)
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL

---

## ❓ Question
What is Vitess, what problem did it solve at YouTube, and how do VSchema, vindexes, VTGate and resharding work?

---

## 💡 Quick Concept (2 lines only)
Vitess is a sharding and connection-management layer for MySQL: apps talk to VTGate over the MySQL protocol, VTGate routes to per-shard VTTablet+MySQL pairs using a VSchema that defines the shard key (vindex).
हिंदी: Vitess MySQL के ऊपर sharding layer है — app VTGate से बात करता है, वह VSchema के vindex से सही shard चुनता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT RUN: Vitess is not installed here. Configs follow the documented
-- VSchema JSON format; check field names against your Vitess version.
-- ============================================

-- Architecture
--  app --(MySQL protocol)--> VTGate (stateless router)
--        --> VTTablet + mysqld  (one per shard replica, protects MySQL: pooling,
--            query killer, row limits, schema tracking)
--  topology (etcd/ZooKeeper/Consul): which shard owns which keyspace range
--  vtctld / vtctldclient: admin; VReplication: data copy engine for resharding

-- VSchema for keyspace "commerce" (sharded by user_id with a hash vindex)
-- {
--   "sharded": true,
--   "vindexes": { "hash": { "type": "hash" } },
--   "tables": {
--     "orders": {
--       "column_vindexes": [ { "column": "user_id", "name": "hash" } ]
--     },
--     "order_items": {
--       "column_vindexes": [ { "column": "user_id", "name": "hash" } ]  -- co-located
--     }
--   }
-- }
-- Shards are keyspace-id ranges: -80 and 80-  (2 shards), later -40, 40-80, 80-c0, c0-

-- ============================================
-- Application SQL stays plain SQL
-- ============================================
SELECT * FROM orders WHERE user_id = 42;       -- routed to exactly ONE shard
SELECT COUNT(*) FROM orders;                   -- scatter-gather, VTGate merges
SELECT o.id, i.sku FROM orders o JOIN order_items i ON i.user_id = o.user_id
WHERE o.user_id = 42;                          -- single-shard join (same vindex)

EXPLAIN FORMAT=vitess SELECT * FROM orders WHERE user_id = 42;
-- Typical plan shape (illustrative, not captured):
-- Route  Variant: EqualUnique  Keyspace: commerce  Query: select ... where user_id = :user_id

-- ============================================
-- Online resharding 1 -> 2 shards (shell, NOT RUN)
-- ============================================
-- vtctldclient Reshard --workflow reshard1 --target-keyspace commerce create \
--     --source-shards '0' --target-shards '-80,80-'
-- vtctldclient Reshard ... show / status          # watch VReplication copy + catch-up
-- vtctldclient VDiff ... create                   # verify source vs target data
-- vtctldclient Reshard ... switchtraffic --tablet-types=rdonly,replica
-- vtctldclient Reshard ... switchtraffic --tablet-types=primary   # brief write pause
-- vtctldclient Reshard ... complete
```

PgSQL equivalent: Citus (Q214). Vitess is MySQL-only.

---

## 🔍 Why This Works (3 lines max)
A vindex maps a column value to a keyspace id, and shards own contiguous keyspace-id ranges, so routing is a lookup and resharding is a range split. VReplication copies and then streams binlog changes, making the cutover near-zero downtime.
हिंदी: Vindex value को keyspace id में बदलता है, shard एक range का मालिक है; resharding में VReplication copy करके traffic switch करता है।

---

## ⚡ Alternative Solution

```sql
-- Lookup vindex for non-shard-key lookups (e.g. find order by order_id without user_id):
-- "vindexes": { "order_lookup": { "type": "consistent_lookup_unique",
--     "params": { "table": "commerce.order_lookup", "from": "order_id", "to": "keyspace_id" } } }
-- Costs an extra table + write amplification, avoids scatter queries.

-- Managed: PlanetScale (Vitess as a service), or app-level sharding with your own router.
-- Smaller scale: stop at read replicas + ProxySQL (Q206).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Choosing a skewed vindex column (tenant_id with one giant tenant): hot shard.
-- ❌ Expecting full MySQL compatibility: some SQL (cross-shard subqueries, certain
--    locking reads, multi-shard transactions) is limited or slower; check docs.
-- ❌ Using a multi-shard transaction casually: default is best-effort, not 2PC
--    (twopc is opt-in via transaction_mode).
-- ✅ Keep the hot path single-shard; test queries with EXPLAIN FORMAT=vitess.
```

---

## 🎯 Interview Tip (1 line)
Say: "Vitess came out of YouTube's MySQL scaling pain: it keeps MySQL as storage, adds VTGate routing, VTTablet connection protection and VReplication-based online resharding, and the real design work is choosing vindexes so important queries stay single-shard."

---

## 🔗 Related Questions
→ Q210 (shard key) | Q211 (consistent hashing) | Q212 (cross-shard queries) | Q214 (Citus)
