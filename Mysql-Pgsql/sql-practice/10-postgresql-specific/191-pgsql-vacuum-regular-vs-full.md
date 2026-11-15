---

# Q191. PgSQL VACUUM — Regular vs VACUUM FULL
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL

---

## ❓ Question
Our `order_events` table has 10,000 rows and we delete half of them. Disk usage does not drop. Explain what plain `VACUUM` does vs `VACUUM FULL`, prove it with table sizes, and say which one is safe to run in production.

---

## 💡 Quick Concept (2 lines only)
PgSQL MVCC leaves dead tuples after UPDATE/DELETE. Plain VACUUM marks that space reusable inside the file (no exclusive lock, file rarely shrinks); VACUUM FULL rewrites the whole table into a new file (shrinks, but takes ACCESS EXCLUSIVE lock).
हिंदी: VACUUM dead rows की जगह दोबारा use के लिए खाली करता है, file छोटी नहीं करता; VACUUM FULL file rewrite करके छोटी करता है पर table lock कर देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- PostgreSQL
-- ============================================

-- autovacuum disabled ONLY so the demo is deterministic. Never do this in prod.
CREATE TABLE order_events (
  id       SERIAL PRIMARY KEY,
  order_id INT,
  status   TEXT,
  payload  TEXT
) WITH (autovacuum_enabled = false);

INSERT INTO order_events (order_id, status, payload)
SELECT g, 'new', repeat('x', 200) FROM generate_series(1, 10000) g;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: size right after load
SELECT pg_size_pretty(pg_relation_size('order_events')) AS size_initial;

-- Step 2: delete every even id -> 5000 dead tuples, file does NOT shrink
DELETE FROM order_events WHERE id % 2 = 0;
SELECT pg_size_pretty(pg_relation_size('order_events')) AS size_after_delete;

-- Step 3: plain VACUUM -> dead space becomes reusable, file size unchanged
VACUUM order_events;
SELECT pg_size_pretty(pg_relation_size('order_events')) AS size_after_vacuum;

-- Step 4: new inserts REUSE the freed space (file does not grow)
INSERT INTO order_events (order_id, status, payload)
SELECT g, 'new', repeat('x', 200) FROM generate_series(1, 5000) g;
SELECT pg_size_pretty(pg_relation_size('order_events')) AS size_after_reinsert;

-- Step 5: delete again, then VACUUM FULL -> table rewritten, file shrinks
DELETE FROM order_events WHERE id % 2 = 0;
VACUUM FULL order_events;   -- ACCESS EXCLUSIVE lock: reads AND writes blocked
SELECT pg_size_pretty(pg_relation_size('order_events')) AS size_after_full;
SELECT count(*) FROM order_events;

-- ============================================
-- EXPECTED OUTPUT (real, PGlite = PostgreSQL 18)
-- ============================================

-- size_initial        = 2432 kB
-- size_after_delete   = 2432 kB   <- DELETE alone frees nothing
-- size_after_vacuum   = 2432 kB   <- plain VACUUM does not return space to the OS
-- size_after_reinsert = 2432 kB   <- but 5000 new rows fit in the freed space
-- size_after_full     = 1824 kB   <- VACUUM FULL rewrote the table
-- count               = 7500
-- (exact sizes vary by version/platform; the PATTERN is what matters)
```

---

## 🔍 Why This Works (3 lines max)
DELETE only stamps a row with xmax; the bytes stay on the page until VACUUM proves no transaction can see them. Plain VACUUM updates the free-space map so INSERTs reuse pages, and only truncates trailing empty pages. VACUUM FULL builds a fresh compact copy, hence the exclusive lock and 2x temporary disk.
हिंदी: DELETE सिर्फ row को dead mark करता है; VACUUM जगह reuse के लिए तैयार करता है; FULL नई compact file बनाता है।

---

## ⚡ Alternative Solution

```sql
-- Look at vacuum health in production (PostgreSQL):
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC LIMIT 10;
-- NOTE: in my PGlite run these counters were 0 right after DELETE (stats are
-- flushed lazily), so do not rely on them inside a single short session.

-- Online alternatives to VACUUM FULL (extension, not run here):
--   pg_repack -t order_events mydb      -- rewrites table with only a brief lock
-- Per-table autovacuum tuning for hot tables:
ALTER TABLE order_events SET (autovacuum_vacuum_scale_factor = 0.02);
-- default scale_factor is 0.2 (verified: pg_settings) = vacuum after 20% churn + 50 rows

-- MySQL (InnoDB) has no VACUUM. Space is reclaimed by purge threads; to shrink the file:
-- OPTIMIZE TABLE order_events;   -- rebuilds table (online DDL for InnoDB), same idea as FULL
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Running VACUUM FULL on a busy table during business hours
VACUUM FULL order_events;   -- blocks every SELECT/INSERT until done, needs 2x disk
-- ✅ Let autovacuum handle bloat; tune its thresholds; use pg_repack if you must shrink online

-- ❌ Turning autovacuum off because "it uses IO"
-- Result: bloat grows, and eventually transaction ID wraparound forces an emergency vacuum
-- ✅ Make autovacuum more aggressive per table instead

-- ❌ Expecting plain VACUUM to shrink the file
-- ✅ It only truncates empty pages at the END of the file; middle holes are just reused
```

---

## 🎯 Interview Tip (1 line)
Say: "Plain VACUUM is non-blocking and reclaims space for reuse; VACUUM FULL rewrites the table under ACCESS EXCLUSIVE lock, so in production I tune autovacuum, watch long-running transactions that hold back the xmin horizon, and use pg_repack when I truly need to shrink."

---

## 🔗 Related Questions
→ Q192 (TOAST) | Q196 (pg_stat_activity — find long transactions blocking vacuum) | Q193 (Materialized views)
