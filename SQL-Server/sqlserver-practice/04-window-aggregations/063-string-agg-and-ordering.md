# Q063. STRING_AGG and Ordering
# Category: WINDOW FUNCTIONS + AGGREGATIONS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server 2017+ (Azure SQL yes; WITHIN GROUP ordering supported from 2017) — MySQL: GROUP_CONCAT; PostgreSQL: STRING_AGG(x, ',' ORDER BY x)

---

## ❓ Question
Return one row per department with a comma-separated list of employee names in alphabetical order. Then show how to remove duplicates (STRING_AGG has no DISTINCT) and how to avoid the 8000-byte limit.

---

## 💡 Quick Concept (2 lines only)
`STRING_AGG(expr, separator) WITHIN GROUP (ORDER BY ...)` concatenates rows of a group into one string. Without WITHIN GROUP the order is not guaranteed; NULL values are skipped.
हिंदी: STRING_AGG = group की rows को एक string में जोड़ना। Order चाहिए तो WITHIN GROUP (ORDER BY) ज़रूर लिखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE DeptEmployees (
    RowId   INT IDENTITY(1,1) PRIMARY KEY,
    Dept    VARCHAR(20) NOT NULL,
    EmpName VARCHAR(20) NOT NULL
);

INSERT INTO DeptEmployees (Dept, EmpName) VALUES
 ('IT', 'Ravi'), ('IT', 'Asha'), ('IT', 'Meena'),
 ('HR', 'Karan'), ('HR', 'Divya'), ('IT', 'Asha');   -- Asha appears twice (duplicate)

-- ============================================
-- SOLUTION 1: ordered list per department
-- ============================================
SELECT
    Dept,
    STRING_AGG(EmpName, ', ') WITHIN GROUP (ORDER BY EmpName) AS Names,
    COUNT(*) AS N
FROM DeptEmployees
GROUP BY Dept
ORDER BY Dept;

-- EXPECTED OUTPUT (result derived from equivalent STRING_AGG ... ORDER BY on PostgreSQL (PGlite); not executed on SQL Server):
-- Dept | Names                    | N
-- HR   | Divya, Karan             | 2
-- IT   | Asha, Asha, Meena, Ravi  | 4

-- ============================================
-- SOLUTION 2: DISTINCT names (T-SQL has no STRING_AGG(DISTINCT ...))
-- ============================================
SELECT Dept, STRING_AGG(EmpName, ', ') WITHIN GROUP (ORDER BY EmpName) AS DistinctNames
FROM (SELECT DISTINCT Dept, EmpName FROM DeptEmployees) AS d
GROUP BY Dept
ORDER BY Dept;

-- EXPECTED OUTPUT (PostgreSQL (PGlite) with STRING_AGG(DISTINCT ...); not executed on SQL Server):
-- HR | Divya, Karan
-- IT | Asha, Meena, Ravi

-- ============================================
-- SOLUTION 3: avoid the 8000-byte limit
-- ============================================
SELECT Dept,
       STRING_AGG(CAST(EmpName AS VARCHAR(MAX)), ', ') WITHIN GROUP (ORDER BY EmpName) AS Names
FROM DeptEmployees
GROUP BY Dept;
-- Without the CAST, a VARCHAR/NVARCHAR(n<=8000) input produces a VARCHAR(8000) / NVARCHAR(4000) result;
-- exceeding it raises an error. Behaviour per Microsoft docs; not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
STRING_AGG is an aggregate, so the GROUP BY collapses each Dept to one row, and WITHIN GROUP (ORDER BY ...) sorts the values before they are glued together. Deduplicating in a derived table first is the standard replacement for DISTINCT. The result type follows the input type, which is why casting to VARCHAR(MAX) removes the length cap.
हिंदी: Duplicate हटाने के लिए पहले DISTINCT subquery, फिर STRING_AGG। लम्बी list के लिए VARCHAR(MAX) cast करो।

---

## ⚡ Alternative Solution

```sql
-- Pre-2017 trick: FOR XML PATH (verbose, needs TYPE/.value() to un-escape &amp; and < >)
SELECT d.Dept,
       STUFF((SELECT ', ' + e.EmpName
              FROM DeptEmployees AS e
              WHERE e.Dept = d.Dept
              ORDER BY e.EmpName
              FOR XML PATH(''), TYPE).value('.', 'VARCHAR(MAX)'), 1, 2, '') AS Names
FROM (SELECT DISTINCT Dept FROM DeptEmployees) AS d;
-- Same strings as Solution 1 except duplicates are not removed. Not executed (no XML support in the available engines).

-- MySQL: SELECT Dept, GROUP_CONCAT(EmpName ORDER BY EmpName SEPARATOR ', ') FROM DeptEmployees GROUP BY Dept;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using STRING_AGG without WITHIN GROUP and trusting the order (it follows scan order, can change with a new index)
SELECT Dept, STRING_AGG(EmpName, ', ') FROM DeptEmployees GROUP BY Dept;

-- ❌ STRING_AGG(DISTINCT EmpName, ', ')  -> syntax error in T-SQL (valid in PostgreSQL)
-- ❌ Putting ORDER BY after the aggregate parentheses like PostgreSQL: STRING_AGG(EmpName, ', ' ORDER BY EmpName) -> T-SQL needs WITHIN GROUP
-- ❌ Using it on SQL Server 2016 or older (compat level < 140) -> "not a recognized built-in function"
-- ❌ Expecting NULL names to appear: they are skipped; use ISNULL(EmpName, '?') if they must show
```

---

## 🎯 Interview Tip (1 line)
Say: "STRING_AGG needs 2017 / compat level 140; I always add WITHIN GROUP for deterministic output, dedupe in a subquery since there is no DISTINCT, and cast to VARCHAR(MAX) when the list can pass 8000 bytes. On older servers I fall back to FOR XML PATH."

---

## 🔗 Related Questions
→ Q006 (String functions — LEN, SUBSTRING, CHARINDEX, STRING_AGG, STRING_SPLIT) | Q003 (DISTINCT, GROUP BY and HAVING) | Q031 (JSON in SQL Server) | Q032 (XML basics)
