---

# Q050. PIVOT and UNPIVOT
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PIVOT/UNPIVOT are T-SQL/Oracle keywords; MySQL and PostgreSQL use conditional aggregation, PostgreSQL also has crosstab() in tablefunc)

---

## ❓ Question
`Sales(Product, Quarter, Amount)` is in long format. Turn it into one row per product with columns Q1..Q4 (PIVOT), then turn a wide quarterly table back into rows (UNPIVOT). Show the portable conditional-aggregation alternative and how to pivot with a dynamic list of columns.

---

## 💡 Quick Concept (2 lines only)
`PIVOT` aggregates rows into columns, but you must list the new column names up front (`FOR Quarter IN ([Q1],[Q2],...)`). `UNPIVOT` does the reverse and silently drops NULLs; `CROSS APPLY (VALUES ...)` is the more flexible modern way to unpivot.
हिंदी: PIVOT = rows को columns बनाता है (column names पहले से लिखने पड़ते हैं)। UNPIVOT उल्टा करता है और NULL rows हटा देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Sales (
  Product VARCHAR(50) NOT NULL,
  Quarter CHAR(2)     NOT NULL,
  Amount  INT         NOT NULL
);

INSERT INTO Sales (Product, Quarter, Amount) VALUES
  ('Laptop', 'Q1', 100), ('Laptop', 'Q1', 50),   -- two Q1 rows: PIVOT aggregates them
  ('Laptop', 'Q2', 150), ('Laptop', 'Q3', 120),
  ('Mouse',  'Q1',  20), ('Mouse',  'Q2',  25), ('Mouse', 'Q4', 30);

-- ============================================
-- PIVOT
-- ============================================
SELECT Product, [Q1], [Q2], [Q3], [Q4]
FROM (SELECT Product, Quarter, Amount FROM Sales) AS src
PIVOT (
  SUM(Amount) FOR Quarter IN ([Q1], [Q2], [Q3], [Q4])
) AS p
ORDER BY Product;

-- EXPECTED OUTPUT (derived from the equivalent CASE-based query on SQLite; not executed on SQL Server):
-- Product | Q1  | Q2  | Q3   | Q4
-- Laptop  | 150 | 150 | 120  | NULL
-- Mouse   | 20  | 25  | NULL | 30

-- ============================================
-- UNPIVOT (wide table -> rows)
-- ============================================
CREATE TABLE SalesWide (Product VARCHAR(50), Q1 INT NULL, Q2 INT NULL, Q3 INT NULL, Q4 INT NULL);
INSERT INTO SalesWide VALUES ('Laptop', 150, 150, 120, NULL), ('Mouse', 20, 25, NULL, 30);

SELECT Product, Quarter, Amount
FROM SalesWide
UNPIVOT (Amount FOR Quarter IN (Q1, Q2, Q3, Q4)) AS u
ORDER BY Product, Quarter;

-- EXPECTED OUTPUT (derived from an equivalent UNION ALL query on SQLite; NULLs are dropped):
-- Product | Quarter | Amount
-- Laptop  | Q1      | 150
-- Laptop  | Q2      | 150
-- Laptop  | Q3      | 120
-- Mouse   | Q1      | 20
-- Mouse   | Q2      | 25
-- Mouse   | Q4      | 30

-- ============================================
-- DYNAMIC PIVOT (column list not known at design time)
-- ============================================
DECLARE @cols NVARCHAR(MAX), @sql NVARCHAR(MAX);

SELECT @cols = STRING_AGG(QUOTENAME(Quarter), ',') WITHIN GROUP (ORDER BY Quarter)   -- 2017+
FROM (SELECT DISTINCT Quarter FROM Sales) AS q;

SET @sql = N'SELECT Product, ' + @cols + N'
FROM (SELECT Product, Quarter, Amount FROM Sales) AS src
PIVOT (SUM(Amount) FOR Quarter IN (' + @cols + N')) AS p
ORDER BY Product;';

EXEC sys.sp_executesql @sql;
-- QUOTENAME protects against injection through the column values. Not executed on SQL Server here.
```

---

## 🔍 Why This Works (3 lines max)
PIVOT groups by every column not named in the aggregate or in `FOR`, applies the aggregate per listed value and puts each result in its own column (missing combinations become NULL). UNPIVOT generates one row per listed column and removes NULL values. Dynamic SQL is needed because the IN list must be static text at parse time.
हिंदी: PIVOT बाकी सब columns पर GROUP BY करता है और listed values को columns बनाता है। IN list static होती है, इसलिए dynamic columns के लिए dynamic SQL चाहिए।

---

## ⚡ Alternative Solution

```sql
-- Portable conditional aggregation (works in SQL Server, MySQL, PostgreSQL; easier to read and extend):
SELECT Product,
       SUM(CASE WHEN Quarter = 'Q1' THEN Amount END) AS Q1,
       SUM(CASE WHEN Quarter = 'Q2' THEN Amount END) AS Q2,
       SUM(CASE WHEN Quarter = 'Q3' THEN Amount END) AS Q3,
       SUM(CASE WHEN Quarter = 'Q4' THEN Amount END) AS Q4
FROM Sales
GROUP BY Product
ORDER BY Product;     -- same result as the PIVOT above (this is the query that was run on SQLite)

-- Modern unpivot that KEEPS NULLs if you want them (T-SQL):
SELECT w.Product, v.Quarter, v.Amount
FROM SalesWide AS w
CROSS APPLY (VALUES ('Q1', w.Q1), ('Q2', w.Q2), ('Q3', w.Q3), ('Q4', w.Q4)) AS v (Quarter, Amount);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: extra columns in the PIVOT source
SELECT * FROM (SELECT SaleId, Product, Quarter, Amount FROM Sales) AS src
PIVOT (SUM(Amount) FOR Quarter IN ([Q1],[Q2])) AS p;
-- SaleId is unique, so it becomes part of the implicit GROUP BY: one row per sale, mostly NULLs.
-- ✅ Select only the grouping columns, the pivot column and the value column in the source subquery.

-- ❌ Wrong: expecting UNPIVOT to keep NULLs (Mouse Q3 disappears). Use CROSS APPLY (VALUES ...) to keep them.

-- ❌ Wrong: building the dynamic list with plain string concatenation instead of QUOTENAME -> SQL injection.

-- ❌ Wrong: UNPIVOT on columns with different data types -- they must be the same type (cast first).
```

---

## 🎯 Interview Tip (1 line)
Say: "PIVOT needs a static column list, so for dynamic columns I build the list with STRING_AGG and QUOTENAME and run it through sp_executesql. Honestly I often prefer conditional aggregation because it is portable and lets me mix different aggregates. UNPIVOT drops NULLs, so I use CROSS APPLY VALUES when I need them."

---

## 🔗 Related Questions
→ Q017 (dynamic SQL) | Q006 (STRING_AGG) | Q038 (CROSS APPLY) | Q061 (ROLLUP, CUBE, GROUPING SETS)
