---

# Q065. GROUP BY with CUBE (PgSQL)
# Category: Aggregations & Window Functions
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL has NO CUBE) — verified on PGlite; MySQL 9.1 error and UNION ALL emulation also run

---

## ❓ Question
Produce totals for every combination of (region, product): per pair, per region, per product and the grand total. How do you do it in MySQL, which has no CUBE?

---

## 💡 Quick Concept (2 lines only)
CUBE(a,b) = all 2^n grouping combinations: (a,b), (a), (b), (). ROLLUP is only the hierarchical subset (a,b), (a), ().
हिंदी: CUBE सभी combinations के totals देता है (cross-tab जैसा); MySQL में CUBE नहीं है।

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
-- SOLUTION (PostgreSQL)
-- ============================================

SELECT region, product, SUM(amount) AS total
FROM sales
GROUP BY CUBE (region, product)
ORDER BY region NULLS LAST, product NULLS LAST;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- region | product | total
-- -------+---------+--------
-- North  | Laptop  | 1500.00
-- North  | Phone   | 300.00
-- North  | NULL    | 1800.00   <- region subtotal
-- South  | Laptop  | 700.00
-- South  | Phone   | 300.00
-- South  | NULL    | 1000.00
-- NULL   | Laptop  | 2200.00   <- product subtotal (only CUBE gives these)
-- NULL   | Phone   | 600.00
-- NULL   | NULL    | 2800.00   <- grand total

-- Label with GROUPING(a,b) bitmask: 0=detail, 1=product rolled up, 2=region rolled up, 3=grand total
SELECT COALESCE(region,'ALL') AS region, COALESCE(product,'ALL') AS product,
       SUM(amount) AS total, GROUPING(region, product) AS grp_id
FROM sales GROUP BY CUBE (region, product)
ORDER BY GROUPING(region, product), region, product;
-- (rows come out grouped by grp_id: 4 detail rows (0), 2 region rows (1), 2 product rows (2), 1 grand total (3))
```

---

## 🔍 Why This Works (3 lines max)
CUBE expands to GROUPING SETS ((region,product),(region),(product),()) and the planner aggregates them in one pass. GROUPING() bitmask identifies which columns were rolled up.
हिंदी: CUBE = GROUPING SETS की सारी combinations; GROUPING() bitmask बताता है कौन सा column roll up हुआ।

---

## ⚡ Alternative Solution

```sql
-- MySQL 9.1 (verified): CUBE is not supported
SELECT region, product, SUM(amount) FROM sales GROUP BY CUBE (region, product);
-- ERROR 3889 (HY000): Secondary engine operation failed ... (CUBE parsed as an unknown function)

-- MySQL emulation: UNION ALL of the 4 grouping levels (4 scans)
SELECT region, product, SUM(amount) AS total FROM sales GROUP BY region, product
UNION ALL SELECT region, NULL, SUM(amount) FROM sales GROUP BY region
UNION ALL SELECT NULL, product, SUM(amount) FROM sales GROUP BY product
UNION ALL SELECT NULL, NULL, SUM(amount) FROM sales
ORDER BY region IS NULL, region, product IS NULL, product;
-- Same 9 rows as the PostgreSQL output above (verified on MySQL 9.1).

-- PostgreSQL: pick exact combinations with GROUPING SETS
SELECT region, product, SUM(amount) AS total
FROM sales GROUP BY GROUPING SETS ((region, product), (product), ())
ORDER BY region NULLS LAST, product NULLS LAST;
-- 4 detail rows + 2 product rows + grand total (no region subtotals)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming WITH ROLLUP equals CUBE
SELECT region, product, SUM(amount) FROM sales GROUP BY region, product WITH ROLLUP;
-- Missing the "NULL | Laptop | 2200" and "NULL | Phone | 600" rows

-- ❌ Wrong: CUBE on many columns -- 2^n groups (10 columns = 1024 grouping sets)
-- ✅ Use GROUPING SETS to list only the combinations the report needs
```

---

## 🎯 Interview Tip (1 line)
Say: "CUBE is a PostgreSQL shortcut for all 2^n grouping combinations; I prefer explicit GROUPING SETS for wide reports because CUBE explodes, and in MySQL I emulate with UNION ALL or precompute in a summary table."

---

## 🔗 Related Questions
→ Q064 (ROLLUP) | Q061 (HAVING vs WHERE) | Q073 (PARTITION BY vs GROUP BY)
