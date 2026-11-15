---

# Q064. GROUP BY with ROLLUP
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ `WITH ROLLUP` | PostgreSQL `ROLLUP(...)`) — verified on MySQL 9.1 and PGlite

---

## ❓ Question
From a `sales` table produce total per (region, product), a subtotal per region, and a grand total in ONE query. Label the subtotal rows.

---

## 💡 Quick Concept (2 lines only)
ROLLUP adds hierarchical subtotals: for (a, b) it yields groups (a,b), (a), and (). The extra rows show NULL in the rolled-up columns; GROUPING() tells a real NULL from a subtotal NULL.
हिंदी: ROLLUP हर level का subtotal और grand total देता है; NULL पहचानने के लिए GROUPING() use करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE sales (
  id      INT PRIMARY KEY,
  region  VARCHAR(20),
  product VARCHAR(20),
  amount  DECIMAL(10,2)
);

INSERT INTO sales VALUES
 (1,'North','Laptop',1000),(2,'North','Laptop',500),(3,'North','Phone',300),
 (4,'South','Laptop', 700),(5,'South','Phone',200),(6,'South','Phone',100);

-- ============================================
-- SOLUTION  (MySQL syntax)
-- ============================================

SELECT
  CASE WHEN GROUPING(region)  = 1 THEN 'ALL REGIONS'  ELSE region  END AS region,
  CASE WHEN GROUPING(product) = 1 THEN 'ALL PRODUCTS' ELSE product END AS product,
  SUM(amount) AS total
FROM sales
GROUP BY region, product WITH ROLLUP;

-- PostgreSQL syntax (same query otherwise; add ORDER BY, rows are not ordered by itself):
--   GROUP BY ROLLUP (region, product)
--   ORDER BY GROUPING(region), region, GROUPING(product), product;

-- ============================================
-- EXPECTED OUTPUT (identical in both engines)
-- ============================================

-- region      | product      | total
-- ------------+--------------+--------
-- North       | Laptop       | 1500.00
-- North       | Phone        | 300.00
-- North       | ALL PRODUCTS | 1800.00     <- region subtotal
-- South       | Laptop       | 700.00
-- South       | Phone        | 300.00
-- South       | ALL PRODUCTS | 1000.00     <- region subtotal
-- ALL REGIONS | ALL PRODUCTS | 2800.00     <- grand total

-- Raw NULL version (no CASE): subtotal rows show NULL
--   North | NULL | 1800.00   ...   NULL | NULL | 2800.00
-- GROUPING(col) = 1 on those rolled-up rows, 0 on normal rows.
```

---

## 🔍 Why This Works (3 lines max)
ROLLUP(a,b) = GROUPING SETS ((a,b),(a),()) computed in a single pass. GROUPING(col) returns 1 when the NULL is a subtotal placeholder, so you can relabel it without confusing it with genuine NULL data.
हिंदी: ROLLUP = (a,b), (a), () तीनों levels एक query में; GROUPING() से subtotal NULL अलग पहचानो।

---

## ⚡ Alternative Solution

```sql
-- Portable fallback (any version): UNION ALL, scans the table once per level
SELECT region, SUM(amount) AS total FROM sales GROUP BY region
UNION ALL
SELECT NULL, SUM(amount) FROM sales;
-- region | total        (MySQL / PgSQL row order of UNION ALL is not guaranteed)
-- North  | 1800.00
-- South  | 1000.00
-- NULL   | 2800.00

-- PostgreSQL: partial rollup, keep region as a plain group key
SELECT region, product, SUM(amount) AS total
FROM sales GROUP BY region, ROLLUP (product) ORDER BY region, product;
-- no grand-total row: only (region,product) and (region)

-- Syntax difference: MySQL has ONLY "WITH ROLLUP" (no ROLLUP(...) form, no GROUPING SETS).
-- PostgreSQL has ROLLUP(...), CUBE(...), GROUPING SETS(...); not "WITH ROLLUP".
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: detecting subtotals with "region IS NULL" -- breaks if region has real NULLs
SELECT COALESCE(region, 'ALL') FROM sales GROUP BY region, product WITH ROLLUP;

-- ✅ Correct: GROUPING(region) = 1
-- ❌ Wrong: column order is meaningless -- ROLLUP(region, product) != ROLLUP(product, region)
--    the FIRST column is the top of the hierarchy (it gets the subtotals)
-- ❌ Wrong (PostgreSQL): no ORDER BY -> subtotal rows can appear anywhere
```

---

## 🎯 Interview Tip (1 line)
Say: "ROLLUP gives hierarchical subtotals in one scan instead of UNION ALL of several GROUP BYs; I use GROUPING() to label total rows, and I know MySQL only supports WITH ROLLUP while PostgreSQL also has CUBE and GROUPING SETS."

---

## 🔗 Related Questions
→ Q065 (CUBE) | Q061 (HAVING) | Q072 (percent of total)
