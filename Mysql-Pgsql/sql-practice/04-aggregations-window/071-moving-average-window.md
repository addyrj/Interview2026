---

# Q071. Moving Average with Window Function
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
Compute a 3-day moving average of a stock's closing price. Make the first two days return NULL (incomplete window) instead of a partial average.

---

## 💡 Quick Concept (2 lines only)
AVG(x) OVER (ORDER BY d ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) averages the current row and the 2 before it. The frame counts rows, not calendar days.
हिंदी: ROWS BETWEEN 2 PRECEDING AND CURRENT ROW = पिछली 2 rows + current, यानी 3-row moving average।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE stock_prices (
  trade_date  DATE PRIMARY KEY,
  close_price DECIMAL(8,2)
);

INSERT INTO stock_prices VALUES      -- note: weekend gap between 01-05 and 01-08
 ('2024-01-01',100),('2024-01-02',102),('2024-01-03',101),('2024-01-04',105),
 ('2024-01-05',110),('2024-01-08',108),('2024-01-09',112);

-- ============================================
-- SOLUTION
-- ============================================

SELECT trade_date, close_price,
  CASE WHEN COUNT(*) OVER w = 3                 -- only full 3-row windows
       THEN ROUND(AVG(close_price) OVER w, 2) END AS ma_3
FROM stock_prices
WINDOW w AS (ORDER BY trade_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
ORDER BY trade_date;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- trade_date | close_price | ma_3
-- -----------+-------------+-------
-- 2024-01-01 | 100.00      | NULL
-- 2024-01-02 | 102.00      | NULL
-- 2024-01-03 | 101.00      | 101.00
-- 2024-01-04 | 105.00      | 102.67
-- 2024-01-05 | 110.00      | 105.33
-- 2024-01-08 | 108.00      | 107.67
-- 2024-01-09 | 112.00      | 110.00
-- Without the CASE, rows 1-2 show partial averages 100.00 and 101.00.
```

---

## 🔍 Why This Works (3 lines max)
The frame slides one row at a time: [row-2, row]. COUNT(*) over the same frame tells how many rows the window really has, so we hide incomplete ones.
हिंदी: Frame हर row के साथ खिसकता है; COUNT(*) से पता चलता है window पूरी है या नहीं।

---

## ⚡ Alternative Solution

```sql
-- Centered 3-row average (previous, current, next)
SELECT trade_date,
  ROUND(AVG(close_price) OVER (ORDER BY trade_date
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING), 2) AS centered_ma
FROM stock_prices;
-- 101.00, 101.00, 102.67, 105.33, 107.67, 110.00, 110.00

-- Calendar-based (3 calendar days) via self-join -- differs around the weekend!
SELECT s.trade_date, ROUND(AVG(p.close_price), 2) AS ma_3
FROM stock_prices s
JOIN stock_prices p ON p.trade_date BETWEEN s.trade_date - INTERVAL 2 DAY AND s.trade_date
GROUP BY s.trade_date ORDER BY s.trade_date;
-- 01-08 shows 108.00 (only itself in the last 3 calendar days) vs 107.67 with the ROWS frame
-- MySQL vs PgSQL: PostgreSQL needs INTERVAL '2 days' (quoted); MySQL uses INTERVAL 2 DAY.
-- Both also support RANGE BETWEEN INTERVAL ... PRECEDING (see Q074).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming ROWS = days -- missing dates (weekends) make the window wider in time
-- ❌ Wrong: no ORDER BY in OVER -> "preceding" rows have no defined order (arbitrary window)
AVG(close_price) OVER (ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)   -- nondeterministic (not run)
-- ❌ Wrong: reporting partial windows as real averages (first rows)
-- ✅ Use COUNT(*) OVER same frame (or ROW_NUMBER() >= 3) to null them out
```

---

## 🎯 Interview Tip (1 line)
Say: "A moving average is AVG over a ROWS frame; I clarify whether the window is N rows or N calendar days (use RANGE with INTERVAL or a date spine for gaps) and what to do with the incomplete leading window."

---

## 🔗 Related Questions
→ Q070 (running total) | Q074 (ROWS vs RANGE) | Q067 (LEAD/LAG)
