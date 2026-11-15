---

# Q056. Running Total With JOIN
# Category: Joins
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
Compute a running (cumulative) total of daily sales using a self join, then show the modern window-function equivalent and the per-group version.

---

## 💡 Quick Concept (2 lines only)
Self join each row to all rows up to and including itself (`b.sale_date <= a.sale_date`) and SUM the right side. It works everywhere but is O(n^2); `SUM() OVER (ORDER BY ...)` does the same in one pass.
हिंदी: हर row को अपने से पहले की सभी rows से self join करो और SUM लो। यह O(n^2) है; window SUM() OVER एक pass में करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE daily_sales (
  sale_date DATE PRIMARY KEY,
  store_id  INT,
  revenue   DECIMAL(10,2)
);

INSERT INTO daily_sales VALUES
  ('2024-03-01', 1, 1000.00),
  ('2024-03-02', 1,  500.00),
  ('2024-03-03', 1,  750.00),
  ('2024-03-04', 1,  250.00),
  ('2024-03-05', 1, 1500.00);

-- ============================================
-- SOLUTION: running total via self join
-- ============================================

-- Step 1: for each day a, join all days b that are on or before a
-- Step 2: SUM(b.revenue) per a = cumulative revenue up to a
SELECT a.sale_date,
       a.revenue,
       SUM(b.revenue) AS running_total
FROM daily_sales a
JOIN daily_sales b
  ON b.sale_date <= a.sale_date          -- non-equi join: the "triangle"
GROUP BY a.sale_date, a.revenue
ORDER BY a.sale_date;
-- Output:
-- sale_date  | revenue | running_total
-- 2024-03-01 | 1000.00 | 1000.00
-- 2024-03-02 | 500.00  | 1500.00
-- 2024-03-03 | 750.00  | 2250.00
-- 2024-03-04 | 250.00  | 2500.00
-- 2024-03-05 | 1500.00 | 4000.00

-- ============================================
-- PER-STORE RUNNING TOTAL (join on store, then date)
-- ============================================

CREATE TABLE store_sales (
  store_id  INT,
  sale_date DATE,
  revenue   DECIMAL(10,2),
  PRIMARY KEY (store_id, sale_date)
);

INSERT INTO store_sales VALUES
  (1, '2024-03-01', 100.00), (1, '2024-03-02', 200.00), (1, '2024-03-03', 300.00),
  (2, '2024-03-01',  50.00), (2, '2024-03-02',  50.00), (2, '2024-03-03', 400.00);

SELECT a.store_id, a.sale_date, a.revenue, SUM(b.revenue) AS running_total
FROM store_sales a
JOIN store_sales b
  ON b.store_id  = a.store_id            -- stay inside the same store
 AND b.sale_date <= a.sale_date
GROUP BY a.store_id, a.sale_date, a.revenue
ORDER BY a.store_id, a.sale_date;
-- Output:
-- store_id | sale_date  | revenue | running_total
-- 1        | 2024-03-01 | 100.00  | 100.00
-- 1        | 2024-03-02 | 200.00  | 300.00
-- 1        | 2024-03-03 | 300.00  | 600.00
-- 2        | 2024-03-01 | 50.00   | 50.00
-- 2        | 2024-03-02 | 50.00   | 100.00
-- 2        | 2024-03-03 | 400.00  | 500.00

-- ============================================
-- THE WINDOW FUNCTION VERSION (MySQL 8+, PostgreSQL) - prefer this
-- ============================================

SELECT sale_date,
       revenue,
       SUM(revenue) OVER (ORDER BY sale_date) AS running_total
FROM daily_sales
ORDER BY sale_date;
-- Output:
-- sale_date  | revenue | running_total
-- 2024-03-01 | 1000.00 | 1000.00
-- 2024-03-02 | 500.00  | 1500.00
-- 2024-03-03 | 750.00  | 2250.00
-- 2024-03-04 | 250.00  | 2500.00
-- 2024-03-05 | 1500.00 | 4000.00

SELECT store_id, sale_date, revenue,
       SUM(revenue) OVER (PARTITION BY store_id ORDER BY sale_date) AS running_total
FROM store_sales
ORDER BY store_id, sale_date;
-- Output:
-- store_id | sale_date  | revenue | running_total
-- 1        | 2024-03-01 | 100.00  | 100.00
-- 1        | 2024-03-02 | 200.00  | 300.00
-- 1        | 2024-03-03 | 300.00  | 600.00
-- 2        | 2024-03-01 | 50.00   | 50.00
-- 2        | 2024-03-02 | 50.00   | 100.00
-- 2        | 2024-03-03 | 400.00  | 500.00
```

---

## 🔍 Why This Works (3 lines max)
The non-equi join `b.sale_date <= a.sale_date` gives row N exactly N partner rows, so grouping by a and summing b.revenue yields the cumulative sum (5 rows -> 15 joined rows, 1M rows -> 500 billion). The window version sorts once and carries a running accumulator, so it is linear.
हिंदी: `b.date <= a.date` से row N को N partners मिलते हैं, SUM = cumulative total। Window function एक pass में करता है, join O(n^2) है।

---

## ⚡ Alternative Solution

```sql
-- Correlated subquery version (also O(n^2), same idea)
SELECT d.sale_date, d.revenue,
       (SELECT SUM(x.revenue) FROM daily_sales x WHERE x.sale_date <= d.sale_date) AS running_total
FROM daily_sales d
ORDER BY d.sale_date;
-- Output:
-- sale_date  | revenue | running_total
-- 2024-03-01 | 1000.00 | 1000.00
-- 2024-03-02 | 500.00  | 1500.00
-- 2024-03-03 | 750.00  | 2250.00
-- 2024-03-04 | 250.00  | 2500.00
-- 2024-03-05 | 1500.00 | 4000.00

-- Window frame matters when the ORDER BY key has ties.
-- Default frame is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW: peers (same date) share one total.
-- Use ROWS to get a strict row-by-row total:
SELECT sale_date, revenue,
       SUM(revenue) OVER (ORDER BY sale_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM daily_sales
ORDER BY sale_date;
-- Output:
-- sale_date  | revenue | running_total
-- 2024-03-01 | 1000.00 | 1000.00
-- 2024-03-02 | 500.00  | 1500.00
-- 2024-03-03 | 750.00  | 2250.00
-- 2024-03-04 | 250.00  | 2500.00
-- 2024-03-05 | 1500.00 | 4000.00

-- MySQL 5.7 (no windows): user variables  SET @t := 0; SELECT sale_date, (@t := @t + revenue) ...
-- works but is order-dependent and deprecated; use the self join there. (Not run: 5.7 is not installed here.)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using < instead of <= in the self join -> every total misses the current row
--          and the first day vanishes entirely (no rows with an earlier date)
JOIN daily_sales b ON b.sale_date < a.sale_date

-- ❌ Wrong: window SUM without ORDER BY -> every row shows the grand total
SUM(revenue) OVER ()

-- ❌ Wrong: forgetting the partition key in the self join -> store 2 totals include store 1 sales
-- ❌ Wrong: running total on a big table via self join -> quadratic blow-up; use the window function
-- ❌ Wrong: ties on the ORDER BY key with the default RANGE frame -> duplicate-looking running totals
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd write SUM() OVER (PARTITION BY ... ORDER BY ... ROWS UNBOUNDED PRECEDING) - linear and index-friendly; I can also show the self-join version to prove I understand it, and I mention it is O(n^2) and that I'd specify ROWS to avoid RANGE tie behaviour."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q075 (Top N per group) | Q054 (Most recent per group) | Q067 (LEAD/LAG)
