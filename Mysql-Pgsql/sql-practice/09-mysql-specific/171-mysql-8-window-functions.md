---

# Q171. MySQL 8.0 Window Functions
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (8.0+) — PostgreSQL syntax is identical

---

## ❓ Question
MySQL 5.7 had no window functions. What does 8.0 give us? Using a `sales` table, show per-region ranking (ROW_NUMBER / RANK / DENSE_RANK), a running total, month-over-month delta with LAG, a 2-row moving average, NTILE, and a named WINDOW clause. What are the restrictions?

---

## 💡 Quick Concept (2 lines only)
A window function computes over a set of rows related to the current row WITHOUT collapsing them like GROUP BY. MySQL 8.0 added them (OVER, PARTITION BY, ORDER BY, frames, named WINDOW).
हिंदी: Window function rows collapse नहीं करता, हर row के साथ calculation देता है; MySQL 8.0 से available है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (verified on MySQL 9.1.0; same on 8.0)
-- ============================================

CREATE TABLE sales (
  id        INT PRIMARY KEY,
  region    VARCHAR(20),
  rep       VARCHAR(30),
  sale_date DATE,
  amount    DECIMAL(10,2)
);

INSERT INTO sales VALUES
(1,'North','Asha', '2024-01-05',1000),(2,'North','Ravi', '2024-01-12',1500),
(3,'North','Asha', '2024-02-03',1500),(4,'South','Meera','2024-01-20', 800),
(5,'South','Kabir','2024-02-11',1200),(6,'South','Meera','2024-03-02', 950),
(7,'North','Ravi', '2024-03-15',2000);

-- ============================================
-- 1) Ranking functions + NAMED WINDOW (MySQL 8.0 supports WINDOW clause)
-- ============================================

SELECT id, region, amount,
       ROW_NUMBER() OVER w AS rn,      -- 1,2,3,4 (no ties)
       RANK()       OVER w AS rnk,     -- ties share rank, gap after
       DENSE_RANK() OVER w AS drnk     -- ties share rank, no gap
FROM sales
WINDOW w AS (PARTITION BY region ORDER BY amount DESC)
ORDER BY region, rn;

-- Result:
-- id | region | amount  | rn | rnk | drnk
-- 7  | North  | 2000.00 | 1  | 1   | 1
-- 2  | North  | 1500.00 | 2  | 2   | 2
-- 3  | North  | 1500.00 | 3  | 2   | 2     <- tie: rank 2, next is 4
-- 1  | North  | 1000.00 | 4  | 4   | 3
-- 5  | South  | 1200.00 | 1  | 1   | 1
-- 6  | South  |  950.00 | 2  | 2   | 2
-- 4  | South  |  800.00 | 3  | 3   | 3
-- (rn for the tied 2/3 rows is arbitrary unless you add a tiebreaker)

-- ============================================
-- 2) Running total + LAG (previous row) + delta
-- ============================================

SELECT id, sale_date, amount,
       SUM(amount) OVER (ORDER BY sale_date, id)        AS running_total,
       LAG(amount) OVER (ORDER BY sale_date, id)        AS prev_amt,
       amount - LAG(amount, 1, 0) OVER (ORDER BY sale_date, id) AS delta  -- 3rd arg = default
FROM sales ORDER BY sale_date, id;

-- Result:
-- id | sale_date  | amount  | running_total | prev_amt | delta
-- 1  | 2024-01-05 | 1000.00 | 1000.00       | NULL     | 1000.00
-- 2  | 2024-01-12 | 1500.00 | 2500.00       | 1000.00  | 500.00
-- 4  | 2024-01-20 |  800.00 | 3300.00       | 1500.00  | -700.00
-- 3  | 2024-02-03 | 1500.00 | 4800.00       |  800.00  | 700.00
-- 5  | 2024-02-11 | 1200.00 | 6000.00       | 1500.00  | -300.00
-- 6  | 2024-03-02 |  950.00 | 6950.00       | 1200.00  | -250.00
-- 7  | 2024-03-15 | 2000.00 | 8950.00       |  950.00  | 1050.00

-- ============================================
-- 3) Moving average with an explicit frame
-- ============================================

SELECT id, region, amount,
       ROUND(AVG(amount) OVER (
         PARTITION BY region ORDER BY sale_date, id
         ROWS BETWEEN 1 PRECEDING AND CURRENT ROW), 2) AS mov_avg2
FROM sales ORDER BY region, sale_date;

-- Result:
-- id | region | amount  | mov_avg2
-- 1  | North  | 1000.00 | 1000.00
-- 2  | North  | 1500.00 | 1250.00
-- 3  | North  | 1500.00 | 1500.00
-- 7  | North  | 2000.00 | 1750.00
-- 4  | South  |  800.00 |  800.00
-- 5  | South  | 1200.00 | 1000.00
-- 6  | South  |  950.00 | 1075.00

-- ============================================
-- 4) NTILE — split into 2 buckets
-- ============================================

SELECT id, amount, NTILE(2) OVER (ORDER BY amount DESC, id) AS half
FROM sales ORDER BY half, id;

-- Result: half=1 -> ids 2,3,5,7 (the 4 biggest amounts); half=2 -> ids 1,4,6
-- (7 rows / 2 buckets: first bucket gets the extra row)
```

---

## 🔍 Why This Works (3 lines max)
The window is evaluated after WHERE/GROUP BY/HAVING and before the final ORDER BY, so each row keeps its identity but sees its partition. PARTITION BY = groups, ORDER BY inside OVER = sequence, frame (ROWS/RANGE) = which neighbours count. Without a frame, an ORDER BY aggregate defaults to RANGE UNBOUNDED PRECEDING TO CURRENT ROW (peers included).
हिंदी: PARTITION BY = group, ORDER BY = क्रम, frame = कौन सी rows गिननी हैं।

---

## ⚡ Alternative Solution

```sql
-- MySQL 5.7 (no windows): correlated subquery for running total — O(n^2)
SELECT s.id, s.amount,
       (SELECT SUM(x.amount) FROM sales x
        WHERE x.sale_date < s.sale_date OR (x.sale_date = s.sale_date AND x.id <= s.id)) AS running_total
FROM sales s ORDER BY s.sale_date, s.id;

-- PostgreSQL: identical window syntax, plus FILTER and GROUPS frames:
-- SELECT SUM(amount) FILTER (WHERE region='North') OVER (ORDER BY sale_date) ...
-- MySQL has NO FILTER clause on windows -> use SUM(CASE WHEN ... END) OVER (...)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Window function in WHERE (verified, MySQL says:
--    ERROR 1054 (42S22): Unknown column 'rn' in 'where clause')
SELECT id, ROW_NUMBER() OVER (ORDER BY id) rn FROM sales WHERE rn <= 2;
-- ✅ Wrap in a derived table / CTE, then filter:
SELECT * FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY id) rn FROM sales) t WHERE rn <= 2;

-- ❌ ORDER BY with ties but no tiebreaker -> ROW_NUMBER / running total non-deterministic
-- ✅ Add a unique column: ORDER BY sale_date, id
```

---

## 🎯 Interview Tip (1 line)
Mention that frames matter: the default RANGE frame treats ties as peers (running total jumps for equal dates), so use `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` plus a unique tiebreaker for a true row-by-row running total; and that MySQL lacks FILTER/GROUPS/some frame options that PostgreSQL has.

---

## 🔗 Related Questions
→ Q066 (ROW_NUMBER vs RANK vs DENSE_RANK) | Q075 (Top N per group) | Q172 (MySQL 8.0 CTEs)
