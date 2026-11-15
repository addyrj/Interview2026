---

# Q043. Recursive CTE — Hierarchies and Org Chart
# Category: Joins, Subqueries & CTEs
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL 8 / PostgreSQL need `WITH RECURSIVE`; T-SQL does not use the word RECURSIVE)

---

## ❓ Question
Table `Employees(EmployeeId, Name, ManagerId, Title)` stores an org chart (CEO has `ManagerId = NULL`). Print the full tree with level and path ("Meera > Rohan > Vikram"), then count all direct + indirect reports of Rohan (id 2). Protect against infinite loops in bad data.

---

## 💡 Quick Concept (2 lines only)
A recursive CTE = anchor member (the root rows) + `UNION ALL` + recursive member that joins back to the CTE itself; SQL Server repeats until no new rows. The default recursion limit is 100 levels — raise or remove it with `OPTION (MAXRECURSION n)`.
हिंदी: Anchor = शुरुआती (root) rows, recursive part = हर level के बच्चे ढूंढता है। Loop में फंसने से बचने के लिए MAXRECURSION (default 100) है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Employees (
  EmployeeId INT          NOT NULL PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL,
  ManagerId  INT          NULL REFERENCES Employees(EmployeeId),
  Title      VARCHAR(50)  NOT NULL
);

INSERT INTO Employees (EmployeeId, Name, ManagerId, Title) VALUES
  (1, 'Meera',  NULL, 'CEO'),
  (2, 'Rohan',  1,    'CTO'),
  (3, 'Anita',  1,    'CFO'),
  (4, 'Vikram', 2,    'Eng Manager'),
  (5, 'Sneha',  2,    'Eng Manager'),
  (6, 'Arjun',  4,    'Developer'),
  (7, 'Pooja',  4,    'Developer'),
  (8, 'Karan',  5,    'Developer'),
  (9, 'Divya',  3,    'Accountant');

-- ============================================
-- FULL ORG CHART WITH LEVEL AND PATH
-- ============================================

WITH OrgChart AS (
  -- Anchor: the root(s)
  SELECT EmployeeId, Name, ManagerId, 0 AS Lvl,
         CAST(Name AS VARCHAR(400)) AS Path
  FROM Employees
  WHERE ManagerId IS NULL

  UNION ALL

  -- Recursive member: children of rows found in the previous step
  SELECT e.EmployeeId, e.Name, e.ManagerId, o.Lvl + 1,
         CAST(o.Path + ' > ' + e.Name AS VARCHAR(400))
  FROM Employees AS e
  INNER JOIN OrgChart AS o ON e.ManagerId = o.EmployeeId
)
SELECT EmployeeId, Name, Lvl, Path
FROM OrgChart
ORDER BY Path
OPTION (MAXRECURSION 50);

-- EXPECTED OUTPUT (result derived from equivalent query on SQLite; not executed on SQL Server):
-- EmployeeId | Name   | Lvl | Path
-- 1          | Meera  | 0   | Meera
-- 3          | Anita  | 1   | Meera > Anita
-- 9          | Divya  | 2   | Meera > Anita > Divya
-- 2          | Rohan  | 1   | Meera > Rohan
-- 5          | Sneha  | 2   | Meera > Rohan > Sneha
-- 8          | Karan  | 3   | Meera > Rohan > Sneha > Karan
-- 4          | Vikram | 2   | Meera > Rohan > Vikram
-- 6          | Arjun  | 3   | Meera > Rohan > Vikram > Arjun
-- 7          | Pooja  | 3   | Meera > Rohan > Vikram > Pooja
-- (ORDER BY Path uses the database collation; with a case-insensitive default collation
--  the order of these names is the same.)

-- ============================================
-- ALL REPORTS (DIRECT + INDIRECT) OF ROHAN
-- ============================================

WITH Subtree AS (
  SELECT EmployeeId, Name, 0 AS Lvl FROM Employees WHERE EmployeeId = 2
  UNION ALL
  SELECT e.EmployeeId, e.Name, s.Lvl + 1
  FROM Employees AS e
  INNER JOIN Subtree AS s ON e.ManagerId = s.EmployeeId
)
SELECT COUNT(*) - 1 AS TotalReports   -- minus Rohan himself
FROM Subtree;

-- EXPECTED OUTPUT (derived on SQLite):
-- TotalReports
-- 5          -- Vikram, Sneha, Arjun, Pooja, Karan
```

---

## 🔍 Why This Works (3 lines max)
The anchor runs once and produces level 0; each recursion step joins `Employees` to only the rows produced by the previous step, so the tree is walked level by level. `UNION ALL` is required (no `UNION`) and recursion stops when a step returns zero rows. `Path` and `Lvl` are carried as extra columns, and the path must be CAST in the anchor to a wide enough type or the types will not match.
हिंदी: Anchor level 0 देता है, फिर हर step पिछले step के बच्चों को join करता है। `UNION ALL` ज़रूरी है, और anchor में Path को CAST कर के चौड़ा रखो।

---

## ⚡ Alternative Solution

```sql
-- Cycle protection: stop if an id is already in the path (bad data: A reports to B, B to A).
-- MAXRECURSION only aborts with an error; this version skips the cycle quietly.
WITH OrgChart AS (
  SELECT EmployeeId, Name, ManagerId, 0 AS Lvl,
         CAST('/' + CAST(EmployeeId AS VARCHAR(10)) + '/' AS VARCHAR(400)) AS IdPath
  FROM Employees WHERE ManagerId IS NULL
  UNION ALL
  SELECT e.EmployeeId, e.Name, e.ManagerId, o.Lvl + 1,
         CAST(o.IdPath + CAST(e.EmployeeId AS VARCHAR(10)) + '/' AS VARCHAR(400))
  FROM Employees AS e
  INNER JOIN OrgChart AS o ON e.ManagerId = o.EmployeeId
  WHERE o.IdPath NOT LIKE '%/' + CAST(e.EmployeeId AS VARCHAR(10)) + '/%'
)
SELECT * FROM OrgChart;

-- Native alternative for static, read-heavy trees: the hierarchyid type (see Q051).
-- MySQL / PostgreSQL: same idea but written WITH RECURSIVE ... and || for string concat.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: no CAST in the anchor
SELECT ..., Name AS Path FROM Employees WHERE ManagerId IS NULL
-- Path becomes VARCHAR(100) (type of Name). The recursive part appends text,
-- the type no longer matches and SQL Server raises a type/length mismatch error
-- between the anchor and recursive members. Fix: CAST(Name AS VARCHAR(400)).

-- ❌ Wrong: relying on the default limit with deep or cyclic data
-- Default MAXRECURSION is 100. Level 101 stops the query with an error.
-- OPTION (MAXRECURSION 0) = unlimited -> a cycle then loops forever. Use a cycle check instead.

-- ❌ Wrong: expecting ORDER BY inside the CTE to sort the tree
-- Sort in the final SELECT (by Path), never inside the CTE definition.
```

---

## 🎯 Interview Tip (1 line)
Say: "Anchor plus recursive member with UNION ALL, carrying level and path columns. I set MAXRECURSION deliberately and add a path-based cycle check for user-edited data. For millions of nodes or frequent subtree queries I would consider hierarchyid or a materialized path column instead, since each recursion step is a join."

---

## 🔗 Related Questions
→ Q042 (CTE basics) | Q051 (hierarchyid) | Q037 (self join) | Q049 (gaps and islands)
