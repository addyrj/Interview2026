---

# Q189. Table Partitioning in PgSQL (Declarative)
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL 10+ (verified on PostgreSQL 18.6 via PGlite)

---

## ❓ Question
Create a RANGE-partitioned `events` table by month in PostgreSQL. Show row routing, partition pruning in EXPLAIN, a DEFAULT partition, ATTACH/DETACH for zero-downtime lifecycle, partitioned indexes, and the primary-key restriction. Mention HASH and LIST.

---

## 💡 Quick Concept (2 lines only)
`PARTITION BY RANGE|LIST|HASH (col)` makes the parent a virtual table; each partition is a real table created with `PARTITION OF`, rows are routed automatically and the planner prunes partitions that cannot match. Old data is removed by `DETACH`/`DROP` of a partition instead of a huge DELETE.
हिंदी: Parent virtual table होती है और हर partition असली table; rows अपने-आप सही partition में जाती हैं और planner बेकार partitions skip करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE events (
  id         BIGINT GENERATED ALWAYS AS IDENTITY,
  user_id    INT NOT NULL,
  event_type TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  region     TEXT,
  PRIMARY KEY (id, created_at)               -- partition key must be part of the PK / any UNIQUE
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024_01 PARTITION OF events FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');  -- upper bound EXCLUSIVE
CREATE TABLE events_2024_02 PARTITION OF events FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE events_default PARTITION OF events DEFAULT;                                           -- catch-all

INSERT INTO events (user_id, event_type, created_at, region) VALUES
 (1,'login',   '2024-01-10 08:00+00','eu'),
 (2,'login',   '2024-01-31 23:59:59+00','us'),
 (1,'purchase','2024-02-01 00:00:00+00','eu'),   -- boundary: goes to Feb
 (3,'logout',  '2024-02-15 12:00+00','us'),
 (4,'login',   '2024-05-05 09:00+00','eu');      -- no May partition -> default

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: routing
SELECT tableoid::regclass AS partition, id, user_id, created_at FROM events ORDER BY id;
-- partition      | id | user_id | created_at
-- events_2024_01 | 1  | 1       | 2024-01-10 08:00:00+00
-- events_2024_01 | 2  | 2       | 2024-01-31 23:59:59+00
-- events_2024_02 | 3  | 1       | 2024-02-01 00:00:00+00   <- exclusive upper bound of Jan
-- events_2024_02 | 4  | 3       | 2024-02-15 12:00:00+00
-- events_default | 5  | 4       | 2024-05-05 09:00:00+00

-- Step 2: pruning with a plain range
EXPLAIN (COSTS OFF) SELECT * FROM events WHERE created_at >= '2024-02-01' AND created_at < '2024-03-01';
-- Seq Scan on events_2024_02 events             <- ONE partition only
--   Filter: (created_at >= ... AND created_at < ...)

-- Step 3: wrapping the key in a function defeats pruning
EXPLAIN (COSTS OFF) SELECT * FROM events WHERE date_trunc('month', created_at) = '2024-02-01';
-- Append -> Seq Scan on events_2024_01, events_2024_02, events_default   (all partitions)

-- Step 4: filter on a non-key column also scans all
EXPLAIN (COSTS OFF) SELECT * FROM events WHERE user_id = 1;
-- Append -> all 3 partitions

-- Step 5: an index on the parent is created on every partition (and future ones)
CREATE INDEX idx_events_user ON events (user_id, created_at);
SELECT relname, relkind FROM pg_class
WHERE relname LIKE 'idx_events_user%' OR relname LIKE 'events_%_user_id_created_at_idx' ORDER BY 1;
-- events_2024_01_user_id_created_at_idx | i
-- events_2024_02_user_id_created_at_idx | i
-- events_default_user_id_created_at_idx | i
-- idx_events_user                       | I   <- 'I' = partitioned index (metadata only)

-- Step 6: lifecycle - load offline, then ATTACH (brief lock only)
CREATE TABLE events_2024_03 (LIKE events INCLUDING DEFAULTS INCLUDING CONSTRAINTS);
ALTER TABLE events_2024_03 ADD CONSTRAINT chk_mar
  CHECK (created_at >= '2024-03-01' AND created_at < '2024-04-01');   -- lets ATTACH skip the validation scan
ALTER TABLE events ATTACH PARTITION events_2024_03 FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- Step 7: overlap is rejected
CREATE TABLE events_2024_02_dup PARTITION OF events FOR VALUES FROM ('2024-02-15') TO ('2024-02-20');
-- ERROR: partition "events_2024_02_dup" would overlap partition "events_2024_02"

-- Step 8: retire a month
ALTER TABLE events DETACH PARTITION events_2024_01;    -- (PG14+: DETACH ... CONCURRENTLY)
SELECT count(*) FROM events;                           -- 3  (the 2 Jan rows left with the partition)
SELECT count(*) FROM events_2024_01;                   -- 2  (still a normal table -> archive, then DROP)
DROP TABLE events_2024_01;

-- ============================================
-- ERRORS you will meet (real messages)
-- ============================================
CREATE TABLE events_nodefault (id INT, created_at DATE NOT NULL) PARTITION BY RANGE (created_at);
CREATE TABLE events_nd_jan PARTITION OF events_nodefault FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
INSERT INTO events_nodefault VALUES (1,'2024-06-01');
-- ERROR: no partition of relation "events_nodefault" found for row

CREATE TABLE bad_pk (id INT PRIMARY KEY, created_at DATE NOT NULL) PARTITION BY RANGE (created_at);
-- ERROR: unique constraint on partitioned table must include all partitioning columns

-- ============================================
-- HASH and LIST
-- ============================================
CREATE TABLE users_h (id INT, name TEXT) PARTITION BY HASH (id);
CREATE TABLE users_h0 PARTITION OF users_h FOR VALUES WITH (MODULUS 2, REMAINDER 0);
CREATE TABLE users_h1 PARTITION OF users_h FOR VALUES WITH (MODULUS 2, REMAINDER 1);
INSERT INTO users_h SELECT i, 'u'||i FROM generate_series(1,10) i;
SELECT tableoid::regclass, count(*) FROM users_h GROUP BY 1 ORDER BY 1;
-- users_h0 | 2
-- users_h1 | 8       <- hash split is NOT guaranteed even on 10 rows

CREATE TABLE regions_l (id INT, region TEXT NOT NULL) PARTITION BY LIST (region);
CREATE TABLE regions_eu PARTITION OF regions_l FOR VALUES IN ('eu','uk');
INSERT INTO regions_l VALUES (1,'eu'),(2,'uk');         -- both land in regions_eu
```

---

## 🔍 Why This Works (3 lines max)
Partition bounds are stored in the catalog, so at plan time (and at run time for parameters) PostgreSQL compares the WHERE clause to the bounds and drops non-matching partitions from the Append. Unique indexes are enforced per partition, hence the PK must include the partition key. ATTACH with a matching CHECK constraint avoids a full scan, making new-period rollout nearly instant.
हिंदी: Bounds catalog में रहते हैं, इसलिए planner मेल न खाने वाले partitions हटा देता है; uniqueness per-partition है, इसलिए PK में partition key चाहिए।

---

## ⚡ Alternative Solution

```sql
-- Automate partition creation: pg_partman extension, or a monthly cron:
--   CREATE TABLE IF NOT EXISTS events_2024_04 PARTITION OF events FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');
-- (pg_partman not available in PGlite - not run.)

-- Sub-partitioning: PARTITION BY RANGE (created_at) then each partition PARTITION BY HASH (user_id).

-- MySQL contrast (Q177): PARTITION BY RANGE (YEAR(created_at)) inside CREATE TABLE; partitions are not separate attachable tables,
-- no FOREIGN KEYs on partitioned InnoDB tables, no ATTACH/DETACH - but EXCHANGE PARTITION and DROP PARTITION exist.

-- Sharding across servers is a different thing (postgres_fdw / Citus) - partitioning is single-server.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Filtering with a function on the key
WHERE date_trunc('month', created_at) = '2024-02-01'     -- verified: scans all partitions
-- ✅ WHERE created_at >= '2024-02-01' AND created_at < '2024-03-01'

-- ❌ No DEFAULT partition and no job creating future partitions  -> inserts fail at midnight of a new month
-- ✅ Pre-create partitions (pg_partman / cron) and keep a DEFAULT to catch strays - but watch it:
--    a DEFAULT partition holding rows blocks creating a new partition whose range covers those rows.

-- ❌ Too many tiny partitions (thousands) -> planning time grows; keep dozens to a few hundred.
-- ❌ Expecting partitioning to help queries that do not use the key (user_id = 1 scanned all 3).
-- ❌ DELETE FROM events WHERE created_at < ... for retention -> bloat + WAL; use DETACH + DROP.
```

---

## 🎯 Interview Tip (1 line)
Say: "I partition by time for retention and pruning, include the key in the primary key, keep pre-created future partitions plus a DEFAULT, filter on the raw key, and retire data with DETACH CONCURRENTLY and DROP rather than DELETE."

---

## 🔗 Related Questions
→ Q177 (MySQL RANGE partitioning) | Q188 (Table inheritance) | Q241 (Sharding) | Q245 (Zero-downtime migration)
