---

# Q037. CROSS JOIN and Self Join
# Category: Joins, Subqueries + CTEs
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (syntax identical in MySQL/PostgreSQL)

---

## ❓ Question
(a) Generate every Size x Color combination for a product catalog with CROSS JOIN. (b) Show each employee with their manager's name using a self join. (c) Find pairs of employees who share the same manager without listing the same pair twice.

---

## 💡 Quick Concept (2 lines only)
CROSS JOIN returns the Cartesian product (rows A x rows B) with no ON condition. A self join joins a table to itself using two different aliases, typically for hierarchies (employee-manager) or pair comparisons.
हिंदी: CROSS JOIN = सब combinations (m x n rows)। Self join = एक ही table को दो alias से join करना, जैसे employee और उसका manager।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Sizes  (Size  VARCHAR(5));
CREATE TABLE Colors (Color VARCHAR(20));
INSERT INTO Sizes  VALUES ('S'), ('M'), ('L');
INSERT INTO Colors VALUES ('Red'), ('Blue');

CREATE TABLE Employees (
    EmpId INT PRIMARY KEY, Name VARCHAR(50), ManagerId INT NULL
);
INSERT INTO Employees VALUES (1,'Priya',NULL),(2,'Arjun',1),(3,'Neha',1),(4,'Vikram',2);

-- ============================================
-- SOLUTION
-- ============================================
-- (a) 3 sizes x 2 colors = 6 rows
SELECT s.Size, c.Color
FROM Sizes s CROSS JOIN Colors c
ORDER BY c.Color DESC, s.Size DESC;   -- deterministic ordering

-- (b) Employee -> Manager (LEFT JOIN keeps the top boss who has no manager)
SELECT e.Name AS Employee, m.Name AS Manager
FROM Employees e
LEFT JOIN Employees m ON m.EmpId = e.ManagerId
ORDER BY e.EmpId;

-- (c) Colleague pairs: a.EmpId < b.EmpId avoids (A,B) and (B,A) and (A,A)
SELECT a.Name AS A, b.Name AS B
FROM Employees a
JOIN Employees b ON a.ManagerId = b.ManagerId AND a.EmpId < b.EmpId;

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent queries on SQLite; not executed on SQL Server)
-- ============================================
-- (a) Red : S, M, L   then   Blue : S, M, L   (6 rows; Color DESC puts Red before Blue,
--     Size DESC sorts S, M, L alphabetically descending)
-- (b) Employee | Manager
--     Priya    | NULL
--     Arjun    | Priya
--     Neha     | Priya
--     Vikram   | Arjun
-- (c) A     | B
--     Arjun | Neha
```

---

## 🔍 Why This Works (3 lines max)
With no ON clause every row of A pairs with every row of B, so use it only on tiny sets (or with a number table to generate series). A self join needs distinct aliases so each reference to the table is unambiguous; the LEFT join keeps the root of the hierarchy. The `<` condition turns a symmetric pairing into a unique one.
हिंदी: CROSS JOIN में ON नहीं होता, इसलिए rows गुणा होती हैं। Self join में अलग-अलग alias ज़रूरी हैं। `a.EmpId < b.EmpId` से duplicate pairs हटते हैं।

---

## ⚡ Alternative Solution

```sql
-- Old-style comma join = CROSS JOIN (avoid; forgetting the WHERE silently produces a Cartesian product)
SELECT s.Size, c.Color FROM Sizes s, Colors c;

-- Multi-level hierarchy: a self join only goes one level; use a recursive CTE (Q043) for the full chain.
-- Row generator with CROSS JOIN (calendar/number table):
-- SELECT TOP (100) ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) FROM sys.all_objects a CROSS JOIN sys.all_objects b;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Accidental Cartesian product: missing join condition
SELECT * FROM Orders o, Customers c;          -- 6 x 4 = 24 rows, all wrong

-- ❌ INNER self join for employee-manager drops the CEO (ManagerId is NULL)
SELECT e.Name, m.Name FROM Employees e JOIN Employees m ON m.EmpId = e.ManagerId;
-- Priya (no manager) is missing; use LEFT JOIN.

-- ❌ Pair query with <> instead of <: returns (Arjun,Neha) AND (Neha,Arjun)
```

---

## 🎯 Interview Tip (1 line)
Say: "CROSS JOIN is a deliberate tool — building combination grids or generating date/number series — and I always know its row count is m x n. For employee-manager I use a LEFT self join for one level and a recursive CTE for the whole tree." Mention spotting accidental Cartesian products in execution plans as a classic cause of runaway queries.

---

## 🔗 Related Questions
→ Q036 (INNER/LEFT/RIGHT/FULL) | Q043 (Recursive CTE) | Q051 (hierarchyid) | Q054 (Date-range overlap queries)
