---

# Q193. Materialized Views — Create + Refresh
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (MySQL has no native materialized views)

---

## ❓ Question
A dashboard runs a heavy monthly-revenue aggregation on every page load. Create a materialized view for it, show that it goes stale, refresh it, and explain `REFRESH ... CONCURRENTLY`.

---

## 💡 Quick Concept (2 lines only)
A materialized view stores the query RESULT on disk (unlike a normal view that re-runs the query); it is only updated when you REFRESH it. CONCURRENTLY refreshes without blocking readers but needs a UNIQUE index.
हिंदी: Materialized view query का result save रखता है और सिर्फ REFRESH पर update होता है; CONCURRENTLY में readers block नहीं होते पर UNIQUE index चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- PostgreSQL
-- ============================================

CREATE TABLE orders (
  id          SERIAL PRIMARY KEY,
  customer_id INT,
  amount      NUMERIC(10,2),
  created_at  DATE
);

INSERT INTO orders (customer_id, amount, created_at) VALUES
  (1, 100, '2024-01-05'), (1, 50, '2024-01-20'),
  (2, 200, '2024-01-21'), (2, 75, '2024-02-02'),
  (3, 300, '2024-02-10');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: create + populate
CREATE MATERIALIZED VIEW monthly_revenue AS
SELECT date_trunc('month', created_at)::date AS month,
       SUM(amount) AS revenue,
       COUNT(*)    AS orders
FROM orders
GROUP BY 1
WITH DATA;

-- Step 2: unique index (required for CONCURRENTLY, also speeds lookups)
CREATE UNIQUE INDEX idx_monthly_revenue_month ON monthly_revenue (month);

SELECT * FROM monthly_revenue ORDER BY month;

-- Step 3: new order arrives -> the MV is STALE
INSERT INTO orders (customer_id, amount, created_at) VALUES (4, 500, '2024-02-15');
SELECT * FROM monthly_revenue ORDER BY month;      -- Feb still shows 375

-- Step 4: refresh (blocks readers while it runs)
REFRESH MATERIALIZED VIEW monthly_revenue;
SELECT * FROM monthly_revenue ORDER BY month;

-- Step 5: refresh without blocking readers
INSERT INTO orders (customer_id, amount, created_at) VALUES (5, 40, '2024-03-01');
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
SELECT * FROM monthly_revenue ORDER BY month;

-- ============================================
-- EXPECTED OUTPUT (real, PGlite = PostgreSQL 18)
-- ============================================

-- After create (and still after step 3 insert = stale):
-- month      | revenue | orders
-- 2024-01-01 | 350.00  | 3
-- 2024-02-01 | 375.00  | 2
--
-- After REFRESH:
-- 2024-01-01 | 350.00  | 3
-- 2024-02-01 | 875.00  | 3
--
-- After CONCURRENTLY refresh:
-- 2024-01-01 | 350.00  | 3
-- 2024-02-01 | 875.00  | 3
-- 2024-03-01 | 40.00   | 1
```

---

## 🔍 Why This Works (3 lines max)
The result set is physically stored, so reads are as cheap as a small table (and indexable). Plain REFRESH takes an ACCESS EXCLUSIVE lock and rebuilds; CONCURRENTLY builds a new copy and diffs it against the old one (hence the unique index), so SELECTs keep working.
हिंदी: Result physically store होता है इसलिए read तेज़; CONCURRENTLY नया copy बनाकर diff apply करता है।

---

## ⚡ Alternative Solution

```sql
-- Create empty now, populate later:
CREATE MATERIALIZED VIEW mv_empty AS SELECT * FROM orders WITH NO DATA;
SELECT * FROM mv_empty;
-- ERROR: materialized view "mv_empty" has not been populated
SELECT matviewname, ispopulated FROM pg_matviews;   -- monthly_revenue t | mv_empty f
-- REFRESH ... CONCURRENTLY on it -> ERROR: CONCURRENTLY cannot be used when the materialized view is not populated
-- (verified: do the first refresh normally)

-- MySQL: no CREATE MATERIALIZED VIEW. Emulate with a summary table refreshed by a job:
--   CREATE TABLE monthly_revenue AS SELECT DATE_FORMAT(created_at,'%Y-%m-01') AS month, SUM(amount) revenue FROM orders GROUP BY 1;
--   CREATE EVENT ev_refresh ON SCHEDULE EVERY 1 HOUR DO REPLACE INTO monthly_revenue ...;   (not run here)
-- PgSQL has no auto-refresh either: schedule REFRESH with pg_cron or an external cron.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ CONCURRENTLY without a unique index
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue;
-- ERROR: cannot refresh materialized view "public.m" concurrently  (HINT: create a unique index with no WHERE clause)
-- ✅ CREATE UNIQUE INDEX first (not partial, no expressions)

-- ❌ Assuming the MV updates itself when base tables change
-- ✅ It does not. Decide acceptable staleness and schedule REFRESH (pg_cron / app job)

-- ❌ Plain REFRESH during peak traffic: readers wait on the exclusive lock
```

---

## 🎯 Interview Tip (1 line)
Say: "Materialized view is a cached query result with explicit refresh; I add a unique index so I can REFRESH CONCURRENTLY, schedule it based on tolerated staleness, and use a summary table maintained by triggers or a job when I need near-real-time."

---

## 🔗 Related Questions
→ Q243 (What is a materialized view?) | Q191 (VACUUM) | Q200 (TimescaleDB continuous aggregates)
