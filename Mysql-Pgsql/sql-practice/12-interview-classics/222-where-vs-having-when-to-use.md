---

# Q222. WHERE vs HAVING — When to Use
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the difference between WHERE and HAVING? Using a `sales_orders` table, find customers whose total spend on **completed** orders is above 400. Show what changes if you put the condition in the wrong clause.

---

## 💡 Quick Concept (2 lines only)
WHERE filters individual rows BEFORE grouping (cannot use aggregates). HAVING filters groups AFTER GROUP BY (can use aggregates like SUM/COUNT). Logical order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY.
हिंदी: WHERE = group बनने से पहले rows filter करता है; HAVING = group बनने के बाद aggregate पर filter करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE sales_orders (
  id          INT PRIMARY KEY,
  customer_id INT NOT NULL,
  region      VARCHAR(20) NOT NULL,
  status      VARCHAR(20) NOT NULL,
  amount      DECIMAL(10,2) NOT NULL
);

INSERT INTO sales_orders VALUES
  (1, 101, 'North', 'completed', 500.00),
  (2, 101, 'North', 'completed', 700.00),
  (3, 101, 'North', 'cancelled', 900.00),
  (4, 102, 'South', 'completed', 200.00),
  (5, 102, 'South', 'completed', 150.00),
  (6, 103, 'North', 'completed', 1200.00),
  (7, 103, 'South', 'cancelled', 300.00),
  (8, 104, 'South', 'completed', 50.00);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: WHERE removes cancelled rows first (row-level, before grouping)
-- Step 2: GROUP BY collapses to one row per customer
-- Step 3: HAVING keeps only groups whose SUM is above 400

SELECT customer_id,
       SUM(amount) AS total_spent,
       COUNT(*)    AS completed_orders
FROM sales_orders
WHERE status = 'completed'          -- row filter (no aggregate allowed here)
GROUP BY customer_id
HAVING SUM(amount) > 400            -- group filter (aggregate allowed)
ORDER BY customer_id;

-- ============================================
-- EXPECTED OUTPUT (verified on MySQL 9.1 and PostgreSQL via PGlite)
-- ============================================

-- Result:
-- customer_id | total_spent | completed_orders
-- ------------+-------------+-----------------
-- 101         | 1200.00     | 2
-- 103         | 1200.00     | 1

-- ============================================
-- WHAT IF WE ONLY USE HAVING (cancelled rows leak into the SUM)?
-- ============================================

SELECT customer_id, SUM(amount) AS total_spent
FROM sales_orders
GROUP BY customer_id
HAVING SUM(amount) > 400
ORDER BY customer_id;

-- Result (different answer!):
-- customer_id | total_spent
-- ------------+------------
-- 101         | 2100.00     -- includes the 900 cancelled order
-- 103         | 1500.00     -- includes the 300 cancelled order

-- ============================================
-- HAVING ON A GROUPING COLUMN (legal but wasteful)
-- ============================================

SELECT region, COUNT(*) AS n
FROM sales_orders
GROUP BY region
HAVING region = 'North';     -- works, but WHERE region='North' filters earlier = less work

-- Result:
-- region | n
-- -------+---
-- North  | 4

-- ============================================
-- MySQL vs PostgreSQL DIFFERENCE: alias in HAVING
-- ============================================

-- MySQL allows the SELECT alias in HAVING:
SELECT customer_id, SUM(amount) AS total_spent
FROM sales_orders
GROUP BY customer_id
HAVING total_spent > 400;
-- Works in MySQL (verified): 101 -> 2100.00, 103 -> 1500.00

-- PostgreSQL rejects it:
--   ERROR: column "total_spent" does not exist
-- Portable form: HAVING SUM(amount) > 400
```

---

## 🔍 Why This Works (3 lines max)
WHERE runs before GROUP BY so the aggregate does not exist yet — that is why `WHERE SUM(amount) > 400` fails (MySQL: "Invalid use of group function", PgSQL: "aggregate functions are not allowed in WHERE"). Filtering rows with WHERE first also shrinks the data the GROUP BY must process, and it can use indexes.
हिंदी: WHERE पहले चलता है, तब SUM बना ही नहीं होता; इसलिए aggregate condition HAVING में जाती है।

---

## ⚡ Alternative Solution

```sql
-- Conditional aggregation: keep all rows, count only what you need.
-- Useful when you need several different filters in the same query.
SELECT customer_id,
       SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS completed_total,
       SUM(CASE WHEN status = 'cancelled' THEN amount ELSE 0 END) AS cancelled_total
FROM sales_orders
GROUP BY customer_id
HAVING SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) > 400;

-- PostgreSQL only: FILTER clause (cleaner, ANSI)
SELECT customer_id,
       COUNT(*) FILTER (WHERE status = 'completed') AS completed_orders
FROM sales_orders
GROUP BY customer_id;
-- Verified on PGlite: 101->2, 102->2, 103->1, 104->1
-- MySQL has no FILTER; use SUM(CASE ...) as above.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: aggregate inside WHERE
SELECT customer_id, SUM(amount) FROM sales_orders
WHERE SUM(amount) > 400 GROUP BY customer_id;
-- MySQL:  ERROR 1111 (HY000): Invalid use of group function
-- PgSQL:  ERROR: aggregate functions are not allowed in WHERE

-- ❌ Wrong: putting a row condition (status) only in HAVING / forgetting it
--   -> cancelled amounts get summed (see 2100 vs 1200 above)

-- ✅ Correct: row conditions in WHERE, aggregate conditions in HAVING
-- Edge case: aggregate with no GROUP BY and empty input still returns ONE row
SELECT SUM(amount) AS total FROM sales_orders WHERE 1 = 0;
-- Result: total = NULL (1 row), because no GROUP BY = one implicit group
```

---

## 🎯 Interview Tip (1 line)
Say: "WHERE filters rows before aggregation and can use indexes; HAVING filters groups after aggregation — I push every non-aggregate predicate into WHERE for performance and keep HAVING strictly for aggregates, and I remember MySQL lets me reuse the alias in HAVING while PostgreSQL does not."

---

## 🔗 Related Questions
→ Q235 (INNER vs LEFT JOIN) | Q239 (find duplicates — uses HAVING) | Q075 (top N per group) | Q020 (GROUP BY basics)
