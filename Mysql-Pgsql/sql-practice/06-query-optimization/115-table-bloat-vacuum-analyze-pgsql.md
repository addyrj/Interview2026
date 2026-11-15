---

# Q115. Table Bloat — VACUUM ANALYZE (PgSQL)
# Category: Query Optimization
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL difference noted)

---

## ❓ Question
A `sessions` table in PostgreSQL has 50,000 rows, you delete 80% of them, and the table file does not shrink. Why? Show the difference between `VACUUM`, `VACUUM ANALYZE` and `VACUUM FULL`, and how to detect bloat.

---

## 💡 Quick Concept (2 lines only)
MVCC means UPDATE/DELETE leave dead row versions behind; plain `VACUUM` marks that space reusable inside the file (it rarely shrinks the file), while `VACUUM FULL` rewrites the table and returns space to the OS but takes an ACCESS EXCLUSIVE lock.
हिंदी: DELETE/UPDATE पुरानी row versions छोड़ते हैं; `VACUUM` जगह reuse के लिए free करता है, file छोटी नहीं करता; `VACUUM FULL` file छोटी करता है पर table lock करता है।

---

## ✅ Answer / Solution

```sql
-- Verified on PGlite (PostgreSQL 18.6). Sizes are for this exact data; page layout may differ by version.

-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE sessions (
  id        SERIAL PRIMARY KEY,
  user_id   INT,
  payload   TEXT,
  last_seen TIMESTAMPTZ DEFAULT now()
);

INSERT INTO sessions (user_id, payload)
SELECT g, repeat('x', 100) FROM generate_series(1, 50000) g;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: baseline size
SELECT pg_size_pretty(pg_relation_size('sessions')) AS heap;

-- Step 2: delete 80% (ids 1..40000). Rows are dead, pages are still allocated.
DELETE FROM sessions WHERE id <= 40000;
SELECT pg_size_pretty(pg_relation_size('sessions')) AS heap_after_delete, count(*) AS live_rows
FROM sessions;

-- Step 3: plain VACUUM + refresh planner stats in one pass
VACUUM (ANALYZE) sessions;
SELECT pg_size_pretty(pg_relation_size('sessions')) AS heap_after_vacuum;

-- Step 4: freed space is REUSED by new inserts (file does not grow)
INSERT INTO sessions (user_id, payload) SELECT g, repeat('y', 100) FROM generate_series(1, 30000) g;
SELECT pg_size_pretty(pg_relation_size('sessions')) AS heap_after_reinsert;

-- Step 5: shrink for real (rewrite; blocks reads AND writes while it runs)
DELETE FROM sessions WHERE id <= 70000;
VACUUM FULL sessions;
SELECT pg_size_pretty(pg_relation_size('sessions')) AS heap_after_vacuum_full, count(*) FROM sessions;

-- Step 6: detect bloat on a real server
SELECT relname, n_live_tup, n_dead_tup,
       round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct,
       last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 10;
-- (PGlite did not populate n_dead_tup - it showed 0 - so that query is NOT verified here.)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- heap                  7280 kB
-- heap_after_delete     7280 kB | live_rows 10000      <- no shrink
-- heap_after_vacuum     7280 kB                        <- still no shrink: live rows sit at the end of the file
-- heap_after_reinsert   7280 kB                        <- 30,000 new rows reused dead space
-- heap_after_vacuum_full 1456 kB | count 10000         <- file rewritten
--
-- Autovacuum defaults (real SHOW): autovacuum_vacuum_scale_factor = 0.2, autovacuum_vacuum_threshold = 50
```

---

## 🔍 Why This Works (3 lines max)
Postgres never overwrites rows in place: UPDATE writes a new version and DELETE only marks the old one dead, so old versions pile up until VACUUM reclaims them. Plain VACUUM can only truncate EMPTY pages at the END of the file, so deleting early rows frees space for reuse but not for the OS; VACUUM FULL builds a new compact file.
हिंदी: Postgres rows को in-place नहीं बदलता, पुराने versions dead बनकर जमा होते हैं; VACUUM उन्हें reuse लायक बनाता है, FULL file compact करता है।

---

## ⚡ Alternative Solution

```sql
-- Online alternatives to VACUUM FULL (no long exclusive lock) - extensions, not run here:
--   pg_repack -t sessions -d mydb           (needs extension + brief locks)
--   pg_squeeze

-- Tune autovacuum per hot table instead of globally (syntax only, not run):
ALTER TABLE sessions SET (
  autovacuum_vacuum_scale_factor = 0.02,     -- vacuum at 2% dead rows, not 20%
  autovacuum_vacuum_threshold    = 1000
);

-- Prevent bloat: fillfactor leaves room for HOT updates (no new index entries)
ALTER TABLE sessions SET (fillfactor = 80);

-- Manual commands
VACUUM sessions;                  -- reclaim for reuse, no exclusive lock
VACUUM (VERBOSE, ANALYZE) sessions;
VACUUM FULL sessions;             -- ACCESS EXCLUSIVE lock, needs ~2x disk temporarily

-- MySQL InnoDB difference: old versions live in undo logs (purged in background), the table
-- file does not accumulate dead tuples the same way. Free space inside tablespace is
-- reclaimed with OPTIMIZE TABLE (recreate + analyze; ran OK on 9.1.0, but I could not get
-- clear size numbers from information_schema so no output is claimed).
OPTIMIZE TABLE sessions;
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Running VACUUM FULL on a busy production table during business hours
--    -> every query on that table queues behind the ACCESS EXCLUSIVE lock.
-- ❌ Expecting plain VACUUM to make "du" smaller. It makes space reusable, not smaller.
-- ❌ Long-running transactions / forgotten idle-in-transaction sessions hold back the
--    "oldest xmin", so even autovacuum cannot remove dead rows -> endless bloat.
-- ✅ Keep autovacuum healthy, kill idle-in-transaction sessions, set
--    idle_in_transaction_session_timeout, and use pg_repack for rare shrink jobs.
```

---

## 🎯 Interview Tip (1 line)
Say: "Bloat comes from MVCC dead tuples; I rely on tuned autovacuum per hot table, watch n_dead_tup and oldest-xmin blockers like idle-in-transaction sessions, and use pg_repack rather than VACUUM FULL when I must shrink a live table."

---

## 🔗 Related Questions
→ Q114 (ANALYZE) | Q116 (Connection pooling) | Q121 (Isolation levels) | Q109 (Slow query diagnosis)
