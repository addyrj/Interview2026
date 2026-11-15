---

# Q074. ROWS BETWEEN vs RANGE BETWEEN
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL 11+) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
Explain the difference between ROWS and RANGE window frames using duplicate dates, and show a "last 2 days" sum using RANGE.

---

## 💡 Quick Concept (2 lines only)
ROWS counts physical rows from the current one; RANGE works on the ORDER BY VALUE and includes all peer rows (equal ORDER BY value) and value offsets. The default frame with ORDER BY is RANGE UNBOUNDED PRECEDING to CURRENT ROW.
हिंदी: ROWS physical row गिनता है, RANGE ORDER BY की value देखता है और बराबर value वाली सब rows (peers) शामिल करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE daily_orders (
  id         INT PRIMARY KEY,
  order_date DATE,
  amount     INT
);

INSERT INTO daily_orders VALUES
 (1,'2024-01-01',10),
 (2,'2024-01-02',20),
 (3,'2024-01-02',30),     -- same date as id 2 (peer rows)
 (4,'2024-01-03',40),
 (5,'2024-01-05',50);     -- gap: no 01-04

-- ============================================
-- SOLUTION
-- ============================================

SELECT id, order_date, amount,
  SUM(amount) OVER (ORDER BY order_date ROWS  BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rows_total,
  SUM(amount) OVER (ORDER BY order_date RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS range_total
FROM daily_orders
ORDER BY order_date, id;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- id | order_date | amount | rows_total | range_total
-- ---+------------+--------+------------+------------
-- 1  | 2024-01-01 | 10     | 10         | 10
-- 2  | 2024-01-02 | 20     | 30         | 60    <- RANGE includes peer id 3
-- 3  | 2024-01-02 | 30     | 60         | 60
-- 4  | 2024-01-03 | 40     | 100        | 100
-- 5  | 2024-01-05 | 50     | 150        | 150
-- Plain SUM(amount) OVER (ORDER BY order_date) equals range_total (the default frame is RANGE).
-- ROWS result for ids 2 and 3 depends on how ties are ordered; add id to ORDER BY to make it stable.

-- "Last 2 calendar days" (current day + previous day) vs "last 2 rows":
SELECT id, order_date, amount,
  SUM(amount) OVER (ORDER BY order_date ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS rows_last_2_rows,
  SUM(amount) OVER (ORDER BY order_date RANGE BETWEEN INTERVAL 1 DAY PRECEDING AND CURRENT ROW) AS range_last_2_days   -- MySQL
FROM daily_orders ORDER BY order_date, id;
-- (PostgreSQL: INTERVAL '1 day' PRECEDING)
-- id | rows_last_2_rows | range_last_2_days
-- 1  | 10               | 10
-- 2  | 30               | 60
-- 3  | 50               | 60
-- 4  | 70               | 90      <- 01-02 peers (20+30) + 40
-- 5  | 90               | 50      <- 01-04 missing, so only 01-05 itself
```

---

## 🔍 Why This Works (3 lines max)
ROWS is positional so it is exact but ignores values; RANGE compares the ORDER BY value (needs a single numeric/date ORDER BY column for offsets), so gaps and ties are handled by value.
हिंदी: ROWS = position, RANGE = value; gaps और duplicates में RANGE value के हिसाब से चलता है।

---

## ⚡ Alternative Solution

```sql
-- Numeric RANGE offset: sum of amounts within +-10 of each amount (works in both)
SELECT id, amount, SUM(amount) OVER (ORDER BY amount RANGE BETWEEN 10 PRECEDING AND 10 FOLLOWING) AS sum_within_10
FROM daily_orders ORDER BY amount;
-- 10->30, 20->60, 30->90, 40->120, 50->90

-- Deterministic running total with duplicates: ROWS + unique tiebreaker
SUM(amount) OVER (ORDER BY order_date, id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
-- 10, 30, 60, 100, 150

-- MySQL vs PgSQL: INTERVAL literal syntax differs (INTERVAL 1 DAY vs INTERVAL '1 day'); PostgreSQL also has GROUPS frames (not run).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: expecting a plain running total to separate duplicate dates
SUM(amount) OVER (ORDER BY order_date)      -- ids 2 and 3 both show 60
-- ✅ Use ROWS ... with a unique ORDER BY (order_date, id)

-- ❌ Wrong: RANGE with a value offset and multiple ORDER BY columns -> error (needs exactly one)
-- ❌ Wrong: using ROWS 1 PRECEDING for "yesterday" when days are missing (gaps)
```

---

## 🎯 Interview Tip (1 line)
Say: "ROWS is physical offsets, RANGE is logical value offsets that include peers; the default frame is RANGE, which is why running totals show duplicates - I set ROWS explicitly unless I truly want value-based windows."

---

## 🔗 Related Questions
→ Q070 (running total) | Q071 (moving average) | Q068 (FIRST_VALUE/LAST_VALUE)
