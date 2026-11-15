---

# Q070. Running Total with SUM() OVER()
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
Show each day's revenue together with the cumulative revenue so far, restarting for every region.

---

## 💡 Quick Concept (2 lines only)
SUM(x) OVER (PARTITION BY g ORDER BY d) accumulates from the partition start to the current row. ORDER BY inside OVER is what turns SUM into a running total.
हिंदी: OVER में ORDER BY लगाने से SUM running total बन जाता है; PARTITION BY से हर group में restart होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE daily_sales (
  sale_date DATE,
  region    VARCHAR(20),
  revenue   DECIMAL(10,2)
);

INSERT INTO daily_sales VALUES
 ('2024-01-01','North',100),('2024-01-02','North',150),
 ('2024-01-03','North', 50),('2024-01-04','North',200),
 ('2024-01-01','South', 80),('2024-01-02','South', 20),('2024-01-03','South',120);

-- ============================================
-- SOLUTION
-- ============================================

SELECT region, sale_date, revenue,
       SUM(revenue) OVER (
         PARTITION BY region        -- restart per region
         ORDER BY sale_date         -- accumulation order
       ) AS running_total
FROM daily_sales
ORDER BY region, sale_date;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- region | sale_date  | revenue | running_total
-- -------+------------+---------+--------------
-- North  | 2024-01-01 | 100.00  | 100.00
-- North  | 2024-01-02 | 150.00  | 250.00
-- North  | 2024-01-03 |  50.00  | 300.00
-- North  | 2024-01-04 | 200.00  | 500.00
-- South  | 2024-01-01 |  80.00  |  80.00
-- South  | 2024-01-02 |  20.00  | 100.00
-- South  | 2024-01-03 | 120.00  | 220.00
```

---

## 🔍 Why This Works (3 lines max)
The window frame defaults to "start of partition through current row (and its ties)" once ORDER BY is present, so each row sums everything up to itself. PARTITION BY gives each region an independent accumulator.
हिंदी: Default frame partition की शुरुआत से current row तक होता है, इसलिए हर row तक का sum मिलता है।

---

## ⚡ Alternative Solution

```sql
-- Explicit ROWS frame (recommended: correct when ORDER BY values repeat)
SUM(revenue) OVER (PARTITION BY region ORDER BY sale_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
-- Same output as above (verified)

-- Pre-8.0 / no window functions: correlated subquery -- O(n^2), avoid on big tables
SELECT a.sale_date, a.revenue,
  (SELECT SUM(b.revenue) FROM daily_sales b
   WHERE b.region = a.region AND b.sale_date <= a.sale_date) AS running_total
FROM daily_sales a WHERE a.region = 'North' ORDER BY a.sale_date;
-- 100, 250, 300, 500 (verified)

-- MySQL vs PgSQL: identical syntax and results.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: forgetting ORDER BY inside OVER -> same grand total on every row
SUM(revenue) OVER (PARTITION BY region)
-- North rows all show 500.00, South rows all show 220.00

-- ❌ Wrong: ordering only the outer query -- OVER's own ORDER BY defines the accumulation
-- ❌ Wrong: duplicate sale_date values with the default RANGE frame -> tied rows get the same total
-- ✅ Add a tiebreaker (ORDER BY sale_date, id) or use ROWS BETWEEN ...
```

---

## 🎯 Interview Tip (1 line)
Say: "Running total is SUM() OVER (PARTITION BY ... ORDER BY ...) and I specify ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW - the default RANGE frame treats duplicate dates as peers (see Q074)."

---

## 🔗 Related Questions
→ Q071 (moving average) | Q074 (ROWS vs RANGE) | Q072 (percent of total) | Q078 (cumulative distinct count)
