---

# Q061. GROUP BY + HAVING — Difference from WHERE
# Category: Aggregations & Window Functions
# Difficulty: ⭐ Easy
# DB: Both (MySQL 8.0+ | PostgreSQL) — verified on MySQL 9.1 and PGlite (PostgreSQL)

---

## ❓ Question
From an `orders` table, show regions whose total *completed* revenue is above 500. Explain why the status filter goes in WHERE and the revenue filter goes in HAVING.

---

## 💡 Quick Concept (2 lines only)
WHERE filters individual rows BEFORE grouping; HAVING filters whole groups AFTER aggregation (so it can use SUM/COUNT/MAX).
हिंदी: WHERE group बनने से पहले rows filter करता है, HAVING group बनने के बाद aggregate result पर filter करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE orders (
  id          INT PRIMARY KEY,
  customer_id INT,
  region      VARCHAR(20),
  amount      DECIMAL(10,2),
  status      VARCHAR(20)
);

INSERT INTO orders VALUES
 (1,101,'North',500.00,'completed'),(2,101,'North',300.00,'completed'),
 (3,102,'North',150.00,'cancelled'),(4,103,'South',900.00,'completed'),
 (5,103,'South',100.00,'completed'),(6,104,'South', 50.00,'cancelled'),
 (7,105,'East',  70.00,'completed'),(8,106,'East',  80.00,'completed'),
 (9,107,'West', 400.00,'completed'),(10,107,'West',650.00,'completed');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: WHERE drops cancelled orders (row-level, before grouping)
-- Step 2: GROUP BY region builds one group per region
-- Step 3: HAVING keeps groups whose SUM > 500 (group-level)

SELECT region, COUNT(*) AS order_cnt, SUM(amount) AS total
FROM orders
WHERE status = 'completed'
GROUP BY region
HAVING SUM(amount) > 500
ORDER BY region;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Result:
-- region | order_cnt | total
-- -------+-----------+--------
-- North  | 2         | 800.00
-- South  | 2         | 1000.00
-- West   | 2         | 1050.00
-- (East = 150.00 total -> removed by HAVING)

-- HAVING can combine several aggregates:
SELECT region, COUNT(*) AS order_cnt, SUM(amount) AS total
FROM orders
GROUP BY region
HAVING COUNT(*) >= 3 AND MAX(amount) > 600
ORDER BY region;
-- Result:
-- region | order_cnt | total
-- South  | 3         | 1050.00      (cancelled order counted: no WHERE here)
```

---

## 🔍 Why This Works (3 lines max)
Logical order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY. WHERE never sees aggregates because groups do not exist yet; HAVING runs after they do.
हिंदी: Execution order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY — इसलिए WHERE में SUM() नहीं चलता।

---

## ⚡ Alternative Solution

```sql
-- Same result with a subquery (useful when you need to reuse the aggregate)
SELECT region, total
FROM (
  SELECT region, SUM(amount) AS total
  FROM orders WHERE status = 'completed'
  GROUP BY region
) t
WHERE total > 500
ORDER BY region;

-- MySQL vs PgSQL difference (both verified):
-- MySQL accepts a SELECT alias in HAVING:
--   ... GROUP BY region HAVING total > 500;      -- works in MySQL 9.1
-- PostgreSQL rejects it:
--   ERROR: column "total" does not exist
-- Portable: repeat the expression, HAVING SUM(amount) > 500.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: aggregate inside WHERE -> error in both engines
SELECT region, SUM(amount) FROM orders WHERE SUM(amount) > 500 GROUP BY region;

-- ❌ Slow/wasteful: row-level condition in HAVING
SELECT region, SUM(amount) AS total FROM orders GROUP BY region HAVING region <> 'East';
-- Works (same result), but groups East first, then throws it away.

-- ✅ Correct: non-aggregate filters in WHERE (can use indexes, fewer rows to group)
SELECT region, SUM(amount) AS total FROM orders WHERE region <> 'East' GROUP BY region;
-- Result: North 950.00 | South 1050.00 | West 1050.00
```

---

## 🎯 Interview Tip (1 line)
Say: "Row conditions go in WHERE so they shrink the input before grouping (and can use an index); HAVING is only for conditions on aggregates — and I never put a plain column filter there."

---

## 🔗 Related Questions
→ Q062 (COUNT(*) vs COUNT(col)) | Q063 (aggregates with NULL) | Q064 (ROLLUP) | Q073 (PARTITION BY vs GROUP BY)
