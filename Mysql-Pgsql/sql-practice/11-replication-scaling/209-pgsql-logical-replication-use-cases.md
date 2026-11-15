---

# Q209. PgSQL Logical Replication Use Cases
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL

---

## ❓ Question
What is PostgreSQL logical replication (publications and subscriptions), when do you choose it over physical streaming replication, and what are its limitations?

---

## 💡 Quick Concept (2 lines only)
Logical replication decodes WAL into row changes (INSERT/UPDATE/DELETE) per table and ships them to subscribers; subscribers can be a different major version, have different indexes, and write their own tables.
हिंदी: Logical replication table-level row changes भेजता है — version/schema अलग हो सकते हैं, physical की तरह पूरा cluster copy नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run on PGlite; publications can be created there)
-- ============================================
CREATE TABLE orders (
  id       INT PRIMARY KEY,      -- PK (or REPLICA IDENTITY) required for UPDATE/DELETE
  user_id  INT,
  total    NUMERIC(10,2)
);
INSERT INTO orders VALUES (1, 1, 10), (2, 2, 20);

-- ============================================
-- PUBLISHER side
-- ============================================
-- Needs wal_level = logical + restart (NOT RUN as such: PGlite has 'replica')
-- ALTER SYSTEM SET wal_level = 'logical';

CREATE PUBLICATION pub_orders FOR TABLE orders;

SELECT pubname, puballtables, pubinsert FROM pg_publication;
-- Real PGlite output:
-- pubname    | puballtables | pubinsert
-- pub_orders | f            | t

SELECT pubname, schemaname, tablename FROM pg_publication_tables;
-- Real PGlite output:
-- pubname    | schemaname | tablename
-- pub_orders | public     | orders

-- Creating the slot failed on PGlite, as expected:
-- SELECT pg_create_logical_replication_slot('s1','pgoutput');
-- Real error: logical decoding requires "wal_level" >= "logical"

-- ============================================
-- SUBSCRIBER side (NOT RUN; needs two servers)
-- ============================================
-- Same table DDL must exist first (DDL is NOT replicated!)
CREATE SUBSCRIPTION sub_orders
  CONNECTION 'host=pub-host dbname=shop user=replicator password=...'
  PUBLICATION pub_orders;
-- initial table copy happens automatically, then streaming begins

SELECT subname, received_lsn, latest_end_lsn FROM pg_stat_subscription;

-- ============================================
-- Typical use cases
-- ============================================
-- 1. Zero-downtime major upgrade: PG13 -> PG16 (subscribe, catch up, switch app)
-- 2. Selective sync: only orders + customers to the analytics DB
-- 3. Row/column filtering (PG15+):
--    CREATE PUBLICATION pub_eu FOR TABLE orders (id, user_id) WHERE (total > 100);
-- 4. CDC to Kafka via Debezium (it uses a logical slot + pgoutput)
-- 5. Consolidating many small DBs into a central reporting DB
-- 6. Cross-region read copy with different indexes than primary
```

MySQL equivalent: row-based binlog replication with replicate-do-table filters, or Debezium reading the binlog.

---

## 🔍 Why This Works (3 lines max)
A logical slot on the publisher decodes WAL through the pgoutput plugin; the subscriber's apply worker replays the changes through normal SQL paths, so the target is a fully independent writable database. Physical replication cannot do any of that because it copies blocks.
हिंदी: Slot WAL को row changes में decode करता है; subscriber एक independent writable DB रहता है।

---

## ⚡ Alternative Solution

```sql
-- Whole-database copy and HA -> physical streaming replication (Q207): simpler,
-- replicates DDL, sequences, large objects, everything.

-- Include all tables in a schema (PG15+):
CREATE PUBLICATION pub_sales FOR TABLES IN SCHEMA sales;   -- NOT RUN

-- Tables without PK: use REPLICA IDENTITY FULL (heavier WAL)
ALTER TABLE audit_log REPLICA IDENTITY FULL;               -- NOT RUN
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Expecting DDL, sequences, and large objects to replicate. They don't.
--    After cutover, sequence values on the subscriber are stale -> duplicate key!
-- ✅ Apply schema changes on subscriber first; copy sequences (setval) at cutover.

-- ❌ Leaving an unused subscription/slot: publisher keeps WAL -> disk fills.
-- ✅ DROP SUBSCRIPTION sub_orders;  or  SELECT pg_drop_replication_slot('...');

-- ❌ Using it as a backup/HA replacement. It is not a byte-exact copy.
```

---

## 🎯 Interview Tip (1 line)
Say: "Physical replication is for HA and read scaling; logical replication is for selective, cross-version and CDC use cases, especially near-zero-downtime major upgrades, and I always handle DDL, sequences and replica identity by hand and monitor slot lag so it can't fill the publisher's disk."

---

## 🔗 Related Questions
→ Q207 (streaming replication) | Q208 (Patroni) | Q214 (Citus) | Q218 (PITR)
