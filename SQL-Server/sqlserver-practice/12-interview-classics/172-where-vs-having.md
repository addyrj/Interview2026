---

# Q172. WHERE vs HAVING
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: SQL Server (same semantics in MySQL/PostgreSQL; MySQL also lets HAVING use SELECT aliases, T-SQL does not)

---

## ❓ Question
Using an Orders table, return customers whose total of SHIPPED orders is above 200. Explain when a condition goes in WHERE and when in HAVING, and show why filtering in HAVING what belongs in WHERE is a performance smell.

---

## 💡 Quick Concept (2 lines only)
WHERE filters rows before grouping (cannot use aggregates); HAVING filters groups after aggregation (can use aggregates). Logical order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY.
हिंदी: WHERE = grouping से पहले rows filter। HAVING = grouping के बाद groups filter (aggregate allowed)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Orders (
    OrderId    INT PRIMARY KEY,
    CustomerId INT,
    Status     VARCHAR(20),
    Amount     DECIMAL(10,2)
);

INSERT INTO Orders VALUES
  (1, 101, 'Shipped',   500),
  (2, 101, 'Cancelled', 200),
  (3, 102, 'Shipped',   150),
  (4, 102, 'Shipped',   900),
  (5, 103, 'Pending',   300),
  (6, 103, 'Shipped',    50),
  (7, 104, 'Cancelled', 700),
  (8, 101, 'Shipped',   100);

-- ============================================
-- SOLUTION: row filter in WHERE, group filter in HAVING
-- ============================================

SELECT CustomerId, SUM(Amount) AS Total, COUNT(*) AS Cnt
FROM Orders
WHERE Status = 'Shipped'          -- row-level: runs BEFORE grouping
GROUP BY CustomerId
HAVING SUM(Amount) > 200          -- group-level: needs the aggregate
ORDER BY CustomerId;

-- EXPECTED OUTPUT (derived from equivalent query on SQLite; not executed on SQL Server):
-- CustomerId | Total | Cnt
-- 101        | 600   | 2
-- 102        | 1050  | 2
-- (103 has only 50 shipped -> filtered by HAVING; 104 has no shipped rows -> filtered by WHERE)

-- ============================================
-- HAVING without WHERE: group-level condition on ALL rows
-- ============================================

SELECT CustomerId, SUM(Amount) AS Total
FROM Orders
GROUP BY CustomerId
HAVING COUNT(*) >= 2
ORDER BY CustomerId;

-- EXPECTED OUTPUT (SQLite-derived; not executed on SQL Server):
-- CustomerId | Total
-- 101        | 800
-- 102        | 1050
-- 103        | 350
```

---

## 🔍 Why This Works (3 lines max)
WHERE runs early and shrinks the data before the expensive GROUP BY, and can use indexes on Status. HAVING can only evaluate after the aggregate exists, so it is the only place for `SUM(...) > 200`. In T-SQL you cannot reference the alias `Total` in HAVING, repeat the expression.
हिंदी: WHERE पहले rows घटाता है (index use हो सकता है)। Aggregate condition सिर्फ HAVING में। T-SQL में HAVING में alias नहीं चलता।

---

## ⚡ Alternative Solution

```sql
-- Same result with a derived table / CTE: filter the aggregate in an outer WHERE
WITH ShippedTotals AS (
    SELECT CustomerId, SUM(Amount) AS Total, COUNT(*) AS Cnt
    FROM Orders
    WHERE Status = 'Shipped'
    GROUP BY CustomerId
)
SELECT CustomerId, Total, Cnt
FROM ShippedTotals
WHERE Total > 200          -- alias usable here, readable for stacked conditions
ORDER BY CustomerId;
-- Same two rows as above (equivalent logic).
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: aggregate in WHERE
SELECT CustomerId FROM Orders WHERE SUM(Amount) > 200 GROUP BY CustomerId;
-- Error: an aggregate may not appear in the WHERE clause (SQL Server raises an error)

-- Wrong (works but wasteful): row filter pushed into HAVING
SELECT CustomerId, SUM(Amount) FROM Orders
GROUP BY CustomerId, Status
HAVING Status = 'Shipped';
-- The optimizer often rewrites this, but do not rely on it; write it in WHERE.

-- Wrong: HAVING alias (works in MySQL, fails in T-SQL)
-- HAVING Total > 200   -- Invalid column name 'Total'
```

---

## 🎯 Interview Tip (1 line)
Say: "WHERE is for row predicates and is sargable, so it reduces rows before aggregation; HAVING is only for conditions on aggregates. I also mention the logical processing order, which explains why you cannot use SELECT aliases in WHERE or HAVING in T-SQL, only in ORDER BY."

---

## 🔗 Related Questions
→ Q003 (DISTINCT, GROUP BY, HAVING) | Q062 (aggregates with NULL) | Q110 (SARGable predicates) | Q175 (UNION vs UNION ALL)
