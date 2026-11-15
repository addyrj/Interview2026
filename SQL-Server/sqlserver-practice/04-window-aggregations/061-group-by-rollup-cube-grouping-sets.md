# Q061. GROUP BY ROLLUP, CUBE, GROUPING SETS
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (2008+) — PostgreSQL supports all three; MySQL only supports `GROUP BY a, b WITH ROLLUP`

---

## ❓ Question
From a `Sales` table (Region, Product, Amount) produce, in one query: totals per Region+Product, subtotals per Region, and a grand total. Then show CUBE (every combination) and GROUPING SETS (only the combinations you choose). Label the NULL subtotal rows properly.

---

## 💡 Quick Concept (2 lines only)
ROLLUP(a,b) = (a,b), (a), () — hierarchical subtotals. CUBE(a,b) = (a,b), (a), (b), () — every combination. GROUPING SETS lists exactly the groupings you want. GROUPING(col) = 1 tells you a NULL is a subtotal marker, not real data.
हिंदी: ROLLUP = ऊपर की तरफ subtotals, CUBE = सारे combinations, GROUPING SETS = जो चाहो वही। GROUPING() से असली NULL और subtotal NULL में फ़र्क करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Sales (
    SaleId  INT IDENTITY(1,1) PRIMARY KEY,
    Region  VARCHAR(10) NOT NULL,
    Product VARCHAR(10) NOT NULL,
    Amount  INT         NOT NULL
);

INSERT INTO Sales (Region, Product, Amount) VALUES
 ('North', 'Laptop', 1000), ('North', 'Laptop', 500), ('North', 'Phone', 300),
 ('South', 'Laptop',  700), ('South', 'Phone',  200), ('South', 'Phone', 100);

-- ============================================
-- SOLUTION 1: ROLLUP with readable labels
-- ============================================
SELECT
    CASE WHEN GROUPING(Region)  = 1 THEN 'ALL REGIONS'  ELSE Region  END AS RegionLabel,
    CASE WHEN GROUPING(Product) = 1 THEN 'ALL PRODUCTS' ELSE Product END AS ProductLabel,
    SUM(Amount) AS Total
FROM Sales
GROUP BY ROLLUP (Region, Product)
ORDER BY GROUPING(Region), Region, GROUPING(Product), Product;

-- EXPECTED OUTPUT (result derived from equivalent query on PostgreSQL (PGlite); not executed on SQL Server):
-- RegionLabel | ProductLabel | Total
-- North       | Laptop       | 1500
-- North       | Phone        | 300
-- North       | ALL PRODUCTS | 1800
-- South       | Laptop       | 700
-- South       | Phone        | 300
-- South       | ALL PRODUCTS | 1000
-- ALL REGIONS | ALL PRODUCTS | 2800

-- ============================================
-- SOLUTION 2: CUBE adds the per-Product subtotals
-- ============================================
SELECT Region, Product, SUM(Amount) AS Total
FROM Sales
GROUP BY CUBE (Region, Product)
ORDER BY GROUPING(Region), Region, GROUPING(Product), Product;

-- EXPECTED OUTPUT (PostgreSQL (PGlite); not executed on SQL Server):
-- North | Laptop | 1500      South | Phone | 300      NULL  | Laptop | 2200
-- North | Phone  | 300       South | NULL  | 1000     NULL  | Phone  | 600
-- North | NULL   | 1800                              NULL  | NULL   | 2800   (9 rows total)

-- ============================================
-- SOLUTION 3: GROUPING SETS — only what you ask for
-- ============================================
SELECT Region, Product, SUM(Amount) AS Total
FROM Sales
GROUP BY GROUPING SETS ((Region), (Product), ());

-- EXPECTED OUTPUT (same engine; row order not guaranteed without ORDER BY):
-- North | NULL   | 1800
-- South | NULL   | 1000
-- NULL  | Laptop | 2200
-- NULL  | Phone  | 600
-- NULL  | NULL   | 2800
```

---

## 🔍 Why This Works (3 lines max)
One scan of the table computes several GROUP BY levels at once; the engine emits a NULL in each column that is "rolled up" in that row. GROUPING(col) returns 1 for those generated NULLs and 0 for real values, so a genuine NULL region is not confused with a subtotal. ROLLUP produces n+1 groupings, CUBE 2^n, and GROUPING SETS exactly the list you give.
हिंदी: एक ही scan में कई levels के totals। GROUPING() = 1 मतलब ये NULL subtotal का है, data का नहीं।

---

## ⚡ Alternative Solution

```sql
-- The old way: UNION ALL of separate GROUP BYs (scans the table 3 times)
SELECT Region, Product, SUM(Amount) AS Total FROM Sales GROUP BY Region, Product
UNION ALL
SELECT Region, NULL, SUM(Amount) FROM Sales GROUP BY Region
UNION ALL
SELECT NULL, NULL, SUM(Amount) FROM Sales;

-- Compact flag column: GROUPING_ID(Region, Product) -> 0 detail row, 1 = Product rolled up (region subtotal), 3 = grand total
SELECT Region, Product, SUM(Amount) AS Total, GROUPING_ID(Region, Product) AS Lvl
FROM Sales GROUP BY ROLLUP (Region, Product);
-- GROUPING_ID is bit-mask of GROUPING() values; not executed here (no equivalent engine), semantics per Microsoft docs.

-- MySQL 8 equivalent of ROLLUP:  GROUP BY Region, Product WITH ROLLUP
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using ISNULL(Region, 'Total') to label subtotals: a real NULL Region is mislabelled as "Total"
SELECT ISNULL(Region, 'Total'), SUM(Amount) FROM Sales GROUP BY ROLLUP (Region);

-- ❌ Forgetting that ROLLUP is order-sensitive: ROLLUP(Product, Region) gives per-Product subtotals, not per-Region
-- ❌ Using CUBE on many columns: 2^n grouping sets (10 columns = 1,024 sets) -> huge result and slow
-- ❌ Expecting sorted output without ORDER BY; rows come out in grouping order only by accident
```

---

## 🎯 Interview Tip (1 line)
Say: "For report-style subtotals I use ROLLUP with GROUPING() to label rows, GROUPING SETS when I need a specific mix, and I avoid CUBE on wide column lists. One pass over the table beats three UNION ALLs, and I always use GROUPING() instead of ISNULL so real NULLs are not hidden."

---

## 🔗 Related Questions
→ Q003 (DISTINCT, GROUP BY and HAVING) | Q044 (UNION, UNION ALL, INTERSECT, EXCEPT) | Q050 (Pivot and UNPIVOT) | Q062 (Aggregate functions with NULL)
