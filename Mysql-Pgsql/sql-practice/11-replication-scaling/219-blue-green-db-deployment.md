---

# Q219. Blue-Green Database Deployment
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
How do you do a blue-green deployment for a database (major version upgrade or risky schema change) with minimal downtime and a rollback path? Walk through building the green copy, keeping it in sync, verifying it, switching traffic, and rolling back. Show the SQL-level verification and swap you can actually run.

---

## 💡 Quick Concept (2 lines only)
Blue = live database, green = a copy that is upgraded/changed while kept in sync by replication; after verifying data parity you cut traffic over in a short write-freeze and keep blue as an instant rollback target. The hard parts are keeping green in sync, replication in the reverse direction for rollback, and sequences/auto-increments.
हिंदी: Blue = चालू DB, green = replication से sync रखी नई copy; verify करके traffic switch करो और blue को rollback के लिए रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — a single-server SIMULATION of the cut-over mechanics (MySQL 9.1 and PGlite)
-- ============================================
-- Real blue-green uses two SERVERS joined by replication (steps listed under "Alternative").
-- Below, two schemas stand in for the two environments so the verification and swap SQL is really executed.

-- MySQL:
CREATE DATABASE shop_blue;      -- live ("blue")
CREATE DATABASE shop_green;     -- candidate ("green")

CREATE TABLE shop_blue.orders (
  id          INT PRIMARY KEY,
  customer_id INT NOT NULL,
  total       DECIMAL(10,2) NOT NULL,
  status      VARCHAR(20) NOT NULL
);

INSERT INTO shop_blue.orders VALUES
  (1, 101,  49.99, 'paid'),
  (2, 102, 120.00, 'paid'),
  (3, 103,  15.50, 'pending');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: build green = copy of blue (replication / snapshot restore in real life)
CREATE TABLE shop_green.orders LIKE shop_blue.orders;
INSERT INTO shop_green.orders SELECT * FROM shop_blue.orders;

-- Step 2: verify parity
CHECKSUM TABLE shop_blue.orders, shop_green.orders;
-- Result:
-- Table             | Checksum
-- shop_blue.orders  | 987140046
-- shop_green.orders | 987140046        <- identical content

-- Step 3: apply the risky change ONLY on green (online DDL, blue untouched)
ALTER TABLE shop_green.orders
  ADD COLUMN currency CHAR(3) NOT NULL DEFAULT 'INR',
  ADD INDEX idx_customer (customer_id),
  ALGORITHM=INPLACE, LOCK=NONE;

-- Step 4: blue keeps taking writes while green is being prepared -> drift
INSERT INTO shop_blue.orders VALUES (4, 104, 75.00, 'paid');

SELECT (SELECT COUNT(*) FROM shop_blue.orders)  AS blue_rows,
       (SELECT COUNT(*) FROM shop_green.orders) AS green_rows;
-- Result: blue_rows = 4, green_rows = 3      <- green is behind (this is what replication closes)

SELECT b.id AS missing_in_green
FROM shop_blue.orders b
LEFT JOIN shop_green.orders g ON g.id = b.id
WHERE g.id IS NULL;
-- Result: 4

-- Step 5: catch-up (replication does this continuously; here a manual delta copy)
INSERT INTO shop_green.orders (id, customer_id, total, status)
SELECT id, customer_id, total, status
FROM shop_blue.orders b
WHERE NOT EXISTS (SELECT 1 FROM shop_green.orders g WHERE g.id = b.id);

SELECT (SELECT SUM(total) FROM shop_blue.orders)  AS blue_sum,
       (SELECT SUM(total) FROM shop_green.orders) AS green_sum;
-- Result: blue_sum = 260.49, green_sum = 260.49     <- business-level reconciliation passes

-- Step 6: atomic swap (in real life: stop writes on blue, wait for lag = 0, repoint DNS/proxy)
RENAME TABLE shop_blue.orders TO shop_blue.orders_old,   -- keep old data = rollback copy
             shop_green.orders TO shop_blue.orders;       -- ONE atomic statement for all renames

SELECT table_schema, table_name FROM information_schema.tables
WHERE table_schema IN ('shop_blue', 'shop_green') ORDER BY 1, 2;
-- Result: shop_blue.orders, shop_blue.orders_old        (shop_green now empty)

SELECT id, currency FROM shop_blue.orders ORDER BY id;
-- Result: ids 1-4 all with currency = 'INR'             <- clients now see the new schema

-- ============================================
-- POSTGRESQL — same swap, transactional DDL (verified on PGlite)
-- ============================================
-- (shop_blue / shop_green created as SCHEMAS; green built with CREATE TABLE ... (LIKE ... INCLUDING ALL),
--  ALTER TABLE ... ADD COLUMN currency CHAR(3) NOT NULL DEFAULT 'INR', delta-copied: blue_sum = green_sum = 260.49)

BEGIN;
ALTER SCHEMA shop_blue  RENAME TO shop_old;
ALTER SCHEMA shop_green RENAME TO shop_blue;
COMMIT;                                    -- both renames become visible together, or neither

SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'shop%' ORDER BY 1;
-- Result: shop_blue, shop_old
SELECT id, currency FROM shop_blue.orders ORDER BY id;
-- Result: 1-4, all 'INR'
```

---

## 🔍 Why This Works (3 lines max)
The expensive, risky work (copy, upgrade, DDL, index builds) happens on green while blue keeps serving; the cut-over itself is only a catch-up plus an atomic switch (renames, DNS, or proxy repoint) taking seconds. Because blue remains intact and can be synced backwards, rollback is a switch, not a restore.
हिंदी: भारी काम green पर होता है और blue चलता रहता है; switch सिर्फ कुछ सेकंड का होता है और blue rollback के लिए तैयार रहता है।

---

## ⚡ Alternative Solution

```sql
-- REAL two-server blue-green (commands/flows - NOT RUN here, no second server):

-- AWS RDS / Aurora Blue/Green Deployments (managed):
--   aws rds create-blue-green-deployment --blue-green-deployment-name shop-upgrade \
--       --source <blue-arn> --target-engine-version 8.0.36 [--target-db-parameter-group-name ...]
--   -> green is a replica with logical/binlog replication, green is read-only until switchover
--   aws rds switchover-blue-green-deployment --blue-green-deployment-identifier bgd-xxxx --switchover-timeout 300
--   -> blocks writes, waits for replica catch-up, renames endpoints (usually < 1 minute)

-- Self-managed MySQL:
--   1. Build green from a backup/clone of blue, upgrade it (8.0 -> 8.4/9.x) while replicating from blue (GTID)
--   2. Test: replay production traffic (ProxySQL mirroring / pt-upgrade), compare results
--   3. Cut-over: SET GLOBAL super_read_only=ON on blue; wait until green executed GTID set = blue's;
--      repoint ProxySQL/DNS to green; green read_only=OFF
--   4. Rollback path: before opening writes, set up REVERSE replication green -> blue (blue as replica of green)

-- Self-managed PostgreSQL major upgrade:
--   logical replication: CREATE PUBLICATION on blue, CREATE SUBSCRIPTION on green (new major version);
--   sequences are NOT replicated -> copy their values at cut-over:
--     SELECT setval('orders_id_seq', (SELECT last_value FROM orders_id_seq));   -- on green, from blue's value
--   DDL is not replicated either -> apply schema changes to both sides (pg_dump --schema-only first)
--   Alternative: pg_upgrade --link on a clone, or pglogical.

-- Application side: feature flag / connection string switch; keep old connections draining; run smoke tests.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: switching without a write freeze / lag = 0 check -> last transactions lost on green
-- ❌ Wrong: forgetting sequences/AUTO_INCREMENT (PG logical replication does not copy sequence values)
--           -> first insert on green fails with duplicate key
-- ❌ Wrong: no reverse replication, so rollback after green accepted writes loses those writes
-- ❌ Wrong: green tested only with empty/synthetic data; cold caches (buffer pool) cause latency spike after switch
--           -> warm green with replayed read traffic first
-- ❌ Wrong: replication-incompatible changes on green (dropping columns blue still writes, different collation)
-- ✅ Correct: compatible changes only, parity checks (checksums/row counts/sums), rehearsed runbook, rollback plan
```

---

## 🎯 Interview Tip (1 line)
Say: "Blue-green for databases means a replicated green copy where I do the upgrade or DDL, verify parity and replay real traffic, then freeze writes, wait for zero lag, switch the endpoint, and keep reverse replication so rollback is just switching back — and I explicitly handle sequences, caches warm-up and replication-incompatible schema changes."

---

## 🔗 Related Questions
→ Q220 (zero-downtime migration) | Q224 (adding index to running table) | Q233 (how replication works) | Q204 (failover automatic vs manual)
