---

# Q042. CTE Basics
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (CTEs supported in MySQL 8.0+ and PostgreSQL; SQL Server requires the previous statement to end with a semicolon)

---

## ❓ Question
Compute each customer's total order amount and count in a named step, then list customers whose total is above the average customer total using two chained CTEs. Is a CTE materialized in SQL Server? Can you UPDATE/DELETE through one?

---

## 💡 Quick Concept (2 lines only)
A CTE (WITH name AS (query)) is a named, single-statement result set that makes complex queries readable and can be chained. SQL Server inlines it like a view, so it is NOT cached; if you reference it twice it can run twice.
हिंदी: CTE = query के अंदर नाम वाला temporary result set, सिर्फ़ उसी statement के लिए। SQL Server इसे store नहीं करता, view की तरह inline करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (CustomerId INT PRIMARY KEY, Name VARCHAR(50), City VARCHAR(50));
CREATE TABLE Orders (
    OrderId INT PRIMARY KEY, CustomerId INT NULL, OrderDate DATE, Amount DECIMAL(10,2)
);
INSERT INTO Customers VALUES (1,'Asha','Pune'),(2,'Rohan','Delhi'),(3,'Meera','Mumbai'),(4,'Kabir','Pune');
INSERT INTO Orders VALUES
  (101,1,'2024-01-05',250.00),(102,1,'2024-02-10',120.00),(103,2,'2024-02-11',99.50),
  (104,NULL,'2024-03-01',75.00),(105,3,'2024-03-15',410.00),(106,2,'2024-04-01',60.00);

-- ============================================
-- SOLUTION
-- ============================================
-- Single CTE: totals per customer
;WITH CustTotals AS (
    SELECT CustomerId, SUM(Amount) AS Total, COUNT(*) AS Cnt
    FROM Orders
    WHERE CustomerId IS NOT NULL
    GROUP BY CustomerId
)
SELECT c.Name, t.Total, t.Cnt
FROM CustTotals t
JOIN Customers c ON c.CustomerId = t.CustomerId
ORDER BY t.Total DESC;

-- Chained CTEs: above-average customers
;WITH CustTotals AS (
    SELECT CustomerId, SUM(Amount) AS Total
    FROM Orders
    WHERE CustomerId IS NOT NULL
    GROUP BY CustomerId
),
AvgTotal AS (
    SELECT AVG(Total) AS AvgTotal FROM CustTotals
)
SELECT c.Name, t.Total
FROM CustTotals t
CROSS JOIN AvgTotal a
JOIN Customers c ON c.CustomerId = t.CustomerId
WHERE t.Total > a.AvgTotal
ORDER BY c.Name;

-- Data modification through a CTE (the CTE must be updatable: single base table)
;WITH Old AS (SELECT * FROM Orders WHERE OrderDate < '2024-02-01')
DELETE FROM Old;                                   -- deletes the rows of Orders it selects

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent queries on SQLite; not executed on SQL Server)
-- Run these before the DELETE statement above.
-- ============================================
-- First query:           Second query (average of totals = 313.1667):
-- Meera | 410.00 | 1     Asha  | 370.00
-- Asha  | 370.00 | 2     Meera | 410.00
-- Rohan | 159.50 | 2
```

---

## 🔍 Why This Works (3 lines max)
The CTE is substituted into the outer query at compile time, so the optimizer sees one big query and can push predicates in. Chained CTEs may reference earlier ones only. The semicolon before WITH is needed because WITH is also used for table hints, so the prior statement must be terminated.
हिंदी: CTE compile के समय outer query में मिल जाता है, इसलिए optimizer पूरी query देखता है। पिछला statement `;` से ख़त्म होना चाहिए वरना WITH error देता है।

---

## ⚡ Alternative Solution

```sql
-- Derived table (same plan, less readable when nested)
SELECT c.Name, t.Total
FROM (SELECT CustomerId, SUM(Amount) AS Total FROM Orders WHERE CustomerId IS NOT NULL GROUP BY CustomerId) t
JOIN Customers c ON c.CustomerId = t.CustomerId;

-- Temp table when the intermediate result is reused several times or is large (materialized, can be indexed):
SELECT CustomerId, SUM(Amount) AS Total INTO #CustTotals FROM Orders GROUP BY CustomerId;
-- (Q016, Q179 compare CTE vs temp table vs table variable)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting the semicolon before WITH
SELECT 1
WITH x AS (SELECT 2 AS n) SELECT n FROM x;     -- Incorrect syntax near 'WITH'

-- ❌ Assuming the CTE is computed once and cached: referenced twice, an expensive CTE can run twice
-- ❌ Using ORDER BY inside a CTE without TOP/OFFSET: not allowed and would not guarantee outer ordering anyway
-- ❌ Using a CTE in a later statement: its scope is the ONE statement that follows it
-- ❌ Default recursion limit is 100 for recursive CTEs (see Q043; override with OPTION (MAXRECURSION n))
```

---

## 🎯 Interview Tip (1 line)
Say: "I use CTEs for readability and for recursion; they are not materialized in SQL Server, so if a step is expensive and used twice I switch to a temp table, which also gives me statistics and indexes. I start the statement with ; WITH or end every statement with a semicolon."

---

## 🔗 Related Questions
→ Q043 (Recursive CTE) | Q016 (Temp tables vs table variables vs CTEs) | Q179 (CTE vs temp table vs table variable) | Q047 (Top N per group)
