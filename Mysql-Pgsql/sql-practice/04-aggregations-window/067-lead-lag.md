---

# Q067. LEAD() and LAG() — Window Functions
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Explain LEAD() and LAG() with real examples. Calculate day-over-day revenue change, detect gaps in sequences, and find consecutive login streaks using these functions.

---

## 💡 Quick Concept (2 lines only)
LAG(col, N) accesses the Nth row BEFORE the current row in the window. LEAD(col, N) accesses the Nth row AFTER. Both avoid self-joins for comparing adjacent rows — single pass over the data.
हिंदी: LAG = पिछले N row की value। LEAD = अगले N row की value। Self-join की जरूरत नहीं — single pass।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE daily_sales (
  sale_date DATE,
  product   VARCHAR(50),
  revenue   DECIMAL(12,2)
);

INSERT INTO daily_sales VALUES
  ('2024-01-01', 'App',  1000),
  ('2024-01-02', 'App',  1200),
  ('2024-01-03', 'App',   900),  -- revenue dropped
  ('2024-01-04', 'App',  1500),
  ('2024-01-05', 'App',  1400);

CREATE TABLE user_logins (
  user_id    INT,
  login_date DATE
);

INSERT INTO user_logins VALUES
  (1, '2024-01-01'),
  (1, '2024-01-02'),
  (1, '2024-01-03'),  -- 3-day streak
  (1, '2024-01-05'),  -- gap on Jan 4!
  (1, '2024-01-06'),
  (1, '2024-01-07');

-- ============================================
-- EXAMPLE 1: DAY-OVER-DAY REVENUE CHANGE
-- ============================================

SELECT
  sale_date,
  revenue,
  LAG(revenue, 1) OVER (ORDER BY sale_date) AS prev_day_revenue,
  revenue - LAG(revenue, 1) OVER (ORDER BY sale_date) AS daily_change,
  ROUND(
    (revenue - LAG(revenue, 1) OVER (ORDER BY sale_date)) /
    LAG(revenue, 1) OVER (ORDER BY sale_date) * 100,
    2
  ) AS pct_change
FROM daily_sales
WHERE product = 'App'
ORDER BY sale_date;

-- Output:
-- sale_date  | revenue | prev_day | daily_change | pct_change
-- 2024-01-01 | 1000    | NULL     | NULL         | NULL       ← no previous row
-- 2024-01-02 | 1200    | 1000     | +200         | +20.00
-- 2024-01-03 |  900    | 1200     | -300         | -25.00     ← revenue dropped!
-- 2024-01-04 | 1500    |  900     | +600         | +66.67
-- 2024-01-05 | 1400    | 1500     | -100         | -6.67

-- LAG with default value (replace NULL on first row):
LAG(revenue, 1, 0) OVER (ORDER BY sale_date)
-- ← 3rd arg = default when no previous row exists (first row returns 0 instead of NULL)

-- ============================================
-- EXAMPLE 2: PARTITION BY (per-product comparison)
-- ============================================

-- Multi-product table:
INSERT INTO daily_sales VALUES
  ('2024-01-01', 'API', 500),
  ('2024-01-02', 'API', 600),
  ('2024-01-03', 'API', 550);

SELECT
  sale_date,
  product,
  revenue,
  LAG(revenue) OVER (PARTITION BY product ORDER BY sale_date) AS prev_revenue,
  revenue - LAG(revenue) OVER (PARTITION BY product ORDER BY sale_date) AS change
FROM daily_sales
ORDER BY product, sale_date;

-- PARTITION BY product:
-- LAG() restarts for each product — App Jan 1 doesn't look back into API rows!
-- Output:
-- 2024-01-01 | App | 1000 | NULL  | NULL   ← first App row, no lookback
-- 2024-01-02 | App | 1200 | 1000  | +200
-- 2024-01-01 | API |  500 | NULL  | NULL   ← first API row, independent partition
-- 2024-01-02 | API |  600 |  500  | +100

-- ============================================
-- EXAMPLE 3: LEAD() — LOOK FORWARD
-- ============================================

-- Days until revenue exceeds 1400 again:
SELECT
  sale_date,
  revenue,
  LEAD(revenue, 1) OVER (ORDER BY sale_date) AS next_day,
  LEAD(revenue, 2) OVER (ORDER BY sale_date) AS two_days_later
FROM daily_sales
WHERE product = 'App'
ORDER BY sale_date;

-- Output:
-- 2024-01-01 | 1000 | 1200 | 900
-- 2024-01-02 | 1200 |  900 | 1500
-- 2024-01-03 |  900 | 1500 | 1400
-- 2024-01-04 | 1500 | 1400 | NULL  ← no +2 row
-- 2024-01-05 | 1400 | NULL | NULL  ← last row

-- Use case: detect upcoming drops — flag rows where next day < current:
SELECT sale_date, revenue,
  CASE WHEN LEAD(revenue) OVER (ORDER BY sale_date) < revenue
       THEN 'DROP EXPECTED TOMORROW'
       ELSE 'OK'
  END AS forecast
FROM daily_sales WHERE product = 'App';

-- ============================================
-- EXAMPLE 4: DETECT GAPS IN LOGIN SEQUENCE
-- ============================================

SELECT
  user_id,
  login_date,
  LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date) AS prev_login,
  DATEDIFF(login_date, LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)) AS days_gap
FROM user_logins
ORDER BY user_id, login_date;

-- MySQL DATEDIFF(later, earlier) → days between
-- PgSQL: login_date - LAG(login_date) OVER (...) → interval

-- Output:
-- user_id | login_date | prev_login | days_gap
-- 1       | 2024-01-01 | NULL       | NULL
-- 1       | 2024-01-02 | 2024-01-01 | 1         ← consecutive
-- 1       | 2024-01-03 | 2024-01-02 | 1         ← consecutive
-- 1       | 2024-01-05 | 2024-01-03 | 2         ← GAP! skipped Jan 4
-- 1       | 2024-01-06 | 2024-01-05 | 1         ← consecutive
-- 1       | 2024-01-07 | 2024-01-06 | 1         ← consecutive

-- Find rows where a gap exists:
SELECT * FROM (
  SELECT
    user_id,
    login_date,
    DATEDIFF(login_date, LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)) AS gap
  FROM user_logins
) gapped
WHERE gap > 1;
-- Output: user 1, 2024-01-05, gap=2 ← first day after the break

-- ============================================
-- EXAMPLE 5: CONSECUTIVE STREAK LENGTH (GAP AND ISLAND)
-- ============================================

-- Strategy: consecutive dates have (date - row_number) = constant
-- Group by that constant → each island = one streak

SELECT user_id, MIN(login_date) AS streak_start, MAX(login_date) AS streak_end,
  COUNT(*) AS streak_length
FROM (
  SELECT user_id, login_date,
    -- MySQL:
    DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY) AS grp
    -- PgSQL:
    -- login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) || ' days')::interval AS grp
  FROM user_logins
) grouped
GROUP BY user_id, grp
ORDER BY user_id, streak_start;

-- Output:
-- user_id | streak_start | streak_end  | streak_length
-- 1       | 2024-01-01   | 2024-01-03  | 3   ← first streak (Jan 1-3)
-- 1       | 2024-01-05   | 2024-01-07  | 3   ← second streak (Jan 5-7)

-- How the grp trick works:
-- Jan 1 = row 1 → Jan 1 - 1 day = Dec 31 → grp = 2023-12-31
-- Jan 2 = row 2 → Jan 2 - 2 days = Dec 31 → grp = 2023-12-31  ← same group!
-- Jan 3 = row 3 → Jan 3 - 3 days = Dec 31 → grp = 2023-12-31  ← same group!
-- Jan 5 = row 4 → Jan 5 - 4 days = Jan 1  → grp = 2024-01-01  ← new group!
-- Consecutive dates → same (date - rownum) → same group!

-- ============================================
-- PgSQL SYNTAX DIFFERENCES
-- ============================================

-- PgSQL uses interval arithmetic:
SELECT
  sale_date,
  revenue,
  LAG(revenue) OVER (ORDER BY sale_date) AS prev_revenue,
  revenue - LAG(revenue) OVER (ORDER BY sale_date) AS change
FROM daily_sales
WHERE product = 'App';
-- Same syntax — LAG/LEAD work identically in PgSQL

-- Date arithmetic in PgSQL (for gap detection):
login_date - LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)
-- Returns INTERVAL type in PgSQL (not integer)
-- Extract days: EXTRACT(EPOCH FROM (login_date - prev_login)) / 86400
-- Or: (login_date - LAG(login_date) OVER (...))::int  (for date type, no time)
```

---

## 🔍 Why This Works (3 lines max)
LAG/LEAD work within a defined window (ORDER BY + optional PARTITION BY) to access adjacent rows without a self-join. The window function runs after the FROM/WHERE/GROUP BY stages, so it sees the filtered and grouped dataset. The gap-and-island trick works because for consecutive dates, subtracting an incrementing row number produces the same constant value for each unbroken sequence.
हिंदी: LAG/LEAD window frame में adjacent rows access करते हैं — self-join नहीं। Gap detection: consecutive dates में (date - rownum) constant रहता है।

---

## ⚡ Alternative Solution

```sql
-- SELF JOIN equivalent (old way — what LAG replaced):
SELECT
  t1.sale_date,
  t1.revenue,
  t2.revenue AS prev_revenue,
  t1.revenue - t2.revenue AS change
FROM daily_sales t1
LEFT JOIN daily_sales t2
  ON t1.product = t2.product
  AND t2.sale_date = (
    SELECT MAX(sale_date) FROM daily_sales
    WHERE sale_date < t1.sale_date AND product = t1.product
  )
WHERE t1.product = 'App'
ORDER BY t1.sale_date;
-- Complex and slow (correlated subquery)! LAG() is far cleaner
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Using LAG without PARTITION BY for multi-group data
SELECT user_id, login_date,
  LAG(login_date) OVER (ORDER BY login_date) AS prev_login
FROM user_logins;
-- User 1's last row looks back to User 2's last row — incorrect!
-- ✅ Fix: PARTITION BY user_id so each user's window is independent:
LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)

-- ❌ Wrong: Forgetting NULL on first row of each partition
-- LAG() returns NULL for the first row (no previous row exists)
-- Always handle NULL: use COALESCE or IS NOT NULL filter:
WHERE LAG(login_date) OVER (...) IS NOT NULL  -- skip first rows
-- OR: LAG(login_date, 1, login_date) OVER (...)  -- default = same date (gap = 0)

-- ❌ Wrong: LEAD/LAG without ORDER BY
LAG(revenue) OVER (PARTITION BY product)  -- ← ERROR! ORDER BY required
-- ORDER BY is mandatory for LAG/LAG — the order defines "previous" and "next"
```

---

## 🎯 Interview Tip (1 line)
Say: "LAG and LEAD replace self-joins for adjacent-row comparisons — single pass, much faster. For day-over-day change: `revenue - LAG(revenue) OVER (ORDER BY date)`. For gap detection: compare `login_date - LAG(login_date) > 1`. For consecutive streaks: the gap-and-island trick — `date - ROW_NUMBER() day` is constant for each unbroken sequence."

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER/RANK/DENSE_RANK) | Q068 (FIRST_VALUE/LAST_VALUE) | Q075 (top N per group) | Q021 (running total)
