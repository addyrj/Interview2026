---

# Q243. What Is a Materialized View?
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (native) | MySQL (emulated)

---

## ❓ Question
What is a materialized view, how does it differ from a normal view, and how do you refresh it? MySQL has no CREATE MATERIALIZED VIEW - show the emulation.

---

## 💡 Quick Concept (2 lines only)
A normal view re-runs its query every time; a materialized view stores the query result physically and must be refreshed, trading freshness for fast reads of expensive aggregates. PostgreSQL supports it natively; MySQL needs a summary table plus a refresh job.
हिंदी: Materialized view query का result store करके रखता है (तेज़ read), पर data पुराना हो सकता है जब तक refresh न करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL; MySQL uses DECIMAL instead of NUMERIC)
-- ============================================

CREATE TABLE orders (id INT PRIMARY KEY, product_id INT, amount NUMERIC(10,2), order_date DATE);
INSERT INTO orders VALUES
  (1,10,100,'2024-03-01'),(2,10,150,'2024-03-01'),(3,20,80,'2024-03-02'),
  (4,10,50,'2024-03-02'),(5,20,120,'2024-03-02');

-- ============================================
-- SOLUTION — PostgreSQL (ran on PGlite)
-- ============================================

-- Step 1: create and populate (runs the query once)
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT order_date, COUNT(*) AS order_count, SUM(amount) AS revenue
FROM orders GROUP BY order_date;

-- Step 2: unique index = required for REFRESH ... CONCURRENTLY, also speeds lookups
CREATE UNIQUE INDEX idx_mv_daily_sales_date ON mv_daily_sales (order_date);

SELECT * FROM mv_daily_sales ORDER BY order_date;
-- order_date | order_count | revenue
-- 2024-03-01 | 2           | 250.00
-- 2024-03-02 | 3           | 250.00

-- Step 3: base table changes - the view is now STALE
INSERT INTO orders VALUES (6,20,300,'2024-03-02'),(7,10,40,'2024-03-03');
SELECT * FROM mv_daily_sales ORDER BY order_date;
-- (unchanged) 03-01: 2/250.00 | 03-02: 3/250.00 -> still old data, 03-03 missing

-- Step 4: refresh (locks readers while rebuilding)
REFRESH MATERIALIZED VIEW mv_daily_sales;
SELECT * FROM mv_daily_sales ORDER BY order_date;
-- 2024-03-01 | 2 | 250.00
-- 2024-03-02 | 4 | 550.00
-- 2024-03-03 | 1 |  40.00

-- Step 5: refresh without blocking readers (needs the unique index)
INSERT INTO orders VALUES (8,10,60,'2024-03-03');
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
-- 2024-03-03 | 2 | 100.00

-- WITH NO DATA creates it empty; selecting fails until the first refresh:
CREATE MATERIALIZED VIEW mv_empty AS SELECT * FROM orders WHERE amount > 1000 WITH NO DATA;
SELECT * FROM mv_empty;
-- ERROR: materialized view "mv_empty" has not been populated

-- ============================================
-- SOLUTION — MySQL emulation (ran on MySQL 9.1.0)
-- ============================================

CREATE TABLE mv_daily_sales (
  order_date   DATE PRIMARY KEY,
  order_count  INT NOT NULL,
  revenue      DECIMAL(12,2) NOT NULL,
  refreshed_at DATETIME NOT NULL
);

INSERT INTO mv_daily_sales
SELECT order_date, COUNT(*), SUM(amount), NOW() FROM orders GROUP BY order_date;

-- After the same extra inserts, the table is stale: 03-02 still shows 3 / 250.00, 03-03 missing.

DELIMITER //
CREATE PROCEDURE refresh_mv_daily_sales()
BEGIN
  INSERT INTO mv_daily_sales (order_date, order_count, revenue, refreshed_at)
  SELECT order_date, COUNT(*), SUM(amount), NOW() FROM orders GROUP BY order_date
  ON DUPLICATE KEY UPDATE order_count = VALUES(order_count), revenue = VALUES(revenue),
                          refreshed_at = VALUES(refreshed_at);   -- upsert = readers never see an empty table
END//
DELIMITER ;

CALL refresh_mv_daily_sales();
-- order_date | order_count | revenue
-- 2024-03-01 | 2           | 250.00
-- 2024-03-02 | 4           | 550.00
-- 2024-03-03 | 1           | 40.00

-- Schedule it (event scheduler must be ON: SET GLOBAL event_scheduler = ON; creation succeeded, firing not tested):
CREATE EVENT ev_refresh_mv_daily_sales ON SCHEDULE EVERY 15 MINUTE DO CALL refresh_mv_daily_sales();

-- CREATE MATERIALIZED VIEW in MySQL -> ERROR 1064 syntax error (confirmed).
```

---

## 🔍 Why This Works (3 lines max)
The aggregate is computed once and stored like a table, so reads are an index lookup instead of a scan of millions of rows. The cost is staleness and refresh work: a full REFRESH recomputes everything, CONCURRENTLY diffs against the old copy so readers keep working.
हिंदी: Result एक बार compute होकर table की तरह store होता है; refresh तक data stale रहता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL vs PgSQL differences:
-- * MySQL: no native MV. Options: summary table + event/cron (above), triggers for real-time increments,
--          or a stream/ETL job. Upsert uses ON DUPLICATE KEY UPDATE (VALUES() is deprecated in 8.0.20+;
--          prefer INSERT ... AS new ON DUPLICATE KEY UPDATE col = new.col; alias form not run).
-- * PostgreSQL: no incremental refresh in core (full recompute only); pg_ivm extension or triggers for incremental.
-- * PostgreSQL has no auto-refresh: schedule with pg_cron/cron (extension, NOT run): SELECT cron.schedule('*/15 * * * *', 'REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales');
-- Plain view for comparison (always fresh, always recomputed):
CREATE VIEW v_daily_sales AS
SELECT order_date, COUNT(*) AS order_count, SUM(amount) AS revenue FROM orders GROUP BY order_date;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting to refresh -> dashboards show stale numbers
-- ❌ REFRESH ... CONCURRENTLY without a UNIQUE index (documented PostgreSQL behaviour, not run here):
--    ERROR: cannot refresh materialized view concurrently (needs unique index on all rows)
-- ❌ Using a materialized view for data that must be real-time (balances, stock)
-- ❌ MySQL: TRUNCATE + re-INSERT in a refresh job -> readers see an empty table mid-refresh
-- ✅ Upsert (MySQL) or REFRESH CONCURRENTLY (PostgreSQL), and show refreshed_at to consumers
```

---

## 🎯 Interview Tip (1 line)
Say: "A materialized view is a cached query result: great for expensive, read-heavy aggregates that tolerate staleness; I index it, refresh with CONCURRENTLY on PostgreSQL, and on MySQL emulate it with a summary table updated by an event, triggers or a pipeline, and I define the acceptable staleness up front."

---

## 🔗 Related Questions
→ Q238 (MySQL vs PostgreSQL) | Q237 (Covering index) | Q236 (Window functions) | Q244 (JSON vs relational)
