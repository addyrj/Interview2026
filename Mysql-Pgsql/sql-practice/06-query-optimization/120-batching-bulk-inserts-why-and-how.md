---

# Q120. Batching Bulk Inserts — Why and How
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
An analytics service inserts 3,000 page-view rows one `INSERT` at a time and takes ages. Show why single-row autocommit inserts are slow, and compare: one transaction, multi-row `VALUES`, and the bulk loaders (`LOAD DATA` / `COPY`). What batch size is sensible?

---

## 💡 Quick Concept (2 lines only)
Each autocommit INSERT pays a network round trip, a parse, and a durable commit (log flush/fsync). Grouping rows into one transaction removes the per-row commit, and multi-row `VALUES` also removes per-row round trips and parsing.
हिंदी: हर अलग INSERT में round trip, parse और commit (disk flush) लगता है; एक transaction और multi-row VALUES से यह खर्च 1000 गुना कम हो जाता है।

---

## ✅ Answer / Solution

```sql
-- Timings verified on MySQL 9.1.0 (local socket, 3,000 rows, macOS laptop SSD, via mysql client).
-- PostgreSQL syntax verified on PGlite 18.6 (functional check only; its timing is NOT meaningful - single in-process WASM).

-- ============================================
-- SETUP (MySQL)
-- ============================================

CREATE TABLE page_views (
  id        BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id   INT,
  url       VARCHAR(200),
  viewed_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================
-- SOLUTION
-- ============================================

-- A) Worst: 3,000 separate autocommit statements
INSERT INTO page_views (user_id, url) VALUES (0, '/p/0');
INSERT INTO page_views (user_id, url) VALUES (1, '/p/1');
-- ... x 3000

-- B) Same statements inside ONE transaction (one commit)
START TRANSACTION;
INSERT INTO page_views (user_id, url) VALUES (0, '/p/0');
INSERT INTO page_views (user_id, url) VALUES (1, '/p/1');
-- ... x 3000
COMMIT;

-- C) Multi-row VALUES, 1000 rows per statement (3 statements, autocommit)
INSERT INTO page_views (user_id, url) VALUES
  (0, '/p/0'), (1, '/p/1'), (2, '/p/2');   -- ... up to ~1000 tuples
-- Keep each statement below max_allowed_packet (67108864 here) and ~1-5k rows.

-- D) Bulk loaders
-- MySQL:      LOAD DATA LOCAL INFILE '/data/views.csv' INTO TABLE page_views
--             FIELDS TERMINATED BY ',' (user_id, url);      (needs local_infile=1; not run)
-- PostgreSQL: COPY page_views (user_id, url) FROM STDIN WITH (FORMAT csv);   (not run)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Real wall-clock, mysql client piping a file, row count 3000 each time:
-- A) 3000 autocommit INSERTs    : 0.27 s
-- B) one transaction            : 0.08 s   (~3x faster)
-- C) 3 x multi-row 1000 tuples  : 0.02 s   (~13x faster)
-- Settings: autocommit=1, innodb_flush_log_at_trx_commit=1 (fsync per commit; macOS fsync is
-- cheap, on cloud disks or over a network the gap is usually far larger).
-- Timings vary by machine; the ORDER A > B > C is the point.
```

---

## 🔍 Why This Works (3 lines max)
With `innodb_flush_log_at_trx_commit=1` every commit forces the redo log to disk, and each statement also costs a client-server round trip and a parse. Batching amortizes those fixed costs across many rows; multi-row `VALUES` also lets the engine build index pages in bigger steps.
हिंदी: Fixed cost (commit, round trip, parse) बहुत सारी rows में बँट जाता है, इसलिए batching तेज़ है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (verified on PGlite 18.6): multi-row VALUES, unnest arrays, INSERT ... SELECT
CREATE TABLE page_views (
  id        BIGSERIAL PRIMARY KEY,
  user_id   INT,
  url       VARCHAR(200),
  viewed_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO page_views (user_id, url) VALUES (1,'/home'),(2,'/pricing'),(3,'/docs');

-- Driver-friendly: two arrays unnested into rows (one parameterized statement for N rows)
INSERT INTO page_views (user_id, url)
SELECT * FROM unnest(ARRAY[4,5,6], ARRAY['/a','/b','/c']);

-- Generated test data
INSERT INTO page_views (user_id, url) SELECT g, '/p/' || g FROM generate_series(7, 1000) g;
-- count = 1000, min(id) = 1, max(id) = 1000 (verified)

-- Idempotent batches (retry safe)
INSERT INTO page_views (id, user_id, url) VALUES (1, 1, '/dup') ON CONFLICT (id) DO NOTHING;
-- MySQL: INSERT IGNORE ... or INSERT ... ON DUPLICATE KEY UPDATE

-- Faster loads: drop/disable secondary indexes and rebuild after (huge loads);
--   MySQL:  SET unique_checks=0, foreign_key_checks=0 (only for trusted data), then restore.
--   PgSQL:  COPY, UNLOGGED table for staging, raise maintenance_work_mem before CREATE INDEX.
-- Application drivers: JDBC reWriteBatchedInserts=true, MySQL rewriteBatchedStatements=true,
--   psycopg2 execute_values / psycopg3 executemany pipeline.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ One giant 5-million-row transaction: huge undo/WAL, long locks, replica lag, huge rollback on failure.
-- ❌ Looping in application code with autocommit on: INSERT per row (the N+1 of writes).
-- ❌ Putting 500k tuples in one statement -> exceeds max_allowed_packet / driver parameter limits
--    (PostgreSQL protocol caps bind parameters at 65535 per statement).
-- ✅ Batch 1,000-10,000 rows per statement, commit every batch or few batches, make batches
--    idempotent (ON CONFLICT / ON DUPLICATE KEY) so a retry after failure is safe.
```

---

## 🎯 Interview Tip (1 line)
Say: "Per-row autocommit pays a round trip and an fsync each time, so I batch 1k-10k rows per multi-row INSERT inside a transaction, use COPY or LOAD DATA for true bulk loads, and keep batches idempotent and bounded so replication lag and rollback cost stay under control."

---

## 🔗 Related Questions
→ Q108 (N+1 problem) | Q109 (Slow query diagnosis) | Q115 (Bloat / VACUUM) | Q121 (Isolation levels)
