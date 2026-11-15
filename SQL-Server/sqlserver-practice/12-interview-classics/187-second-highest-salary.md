---

# Q187. Second Highest Salary
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL/PostgreSQL: use LIMIT 1 OFFSET 1 instead of TOP/OFFSET FETCH)

---

## ❓ Question
From `Employees`, return the second highest distinct salary (NULL if it does not exist). Then return the second highest per department, with ties.

---

## 💡 Quick Concept (2 lines only)
Rank distinct salaries: DENSE_RANK() = 2, or MAX(Salary) below the overall MAX, or OFFSET 1 over DISTINCT salaries. Ties must not consume a rank, so DENSE_RANK or DISTINCT is the correct choice, not ROW_NUMBER.
हिंदी: Distinct salary पर 2nd rank चाहिए। Ties के लिए DENSE_RANK या DISTINCT use करो, ROW_NUMBER नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Employees (
  EmployeeId INT PRIMARY KEY,
  Name       VARCHAR(100),
  Dept       VARCHAR(50),
  Salary     DECIMAL(10,2)
);
INSERT INTO dbo.Employees VALUES
  (1,'Alice','Engineering',120000),(2,'Bob','Engineering',95000),(3,'Carol','Engineering',95000),
  (4,'Dave','Sales',90000),(5,'Eve','Sales',75000),
  (6,'Frank','Marketing',75000),(7,'Grace','Marketing',60000);
GO

-- 1) Subquery: MAX below the MAX (returns NULL automatically if no 2nd value)
SELECT MAX(Salary) AS SecondHighest
FROM dbo.Employees
WHERE Salary < (SELECT MAX(Salary) FROM dbo.Employees);

-- EXPECTED: SecondHighest = 95000.00

-- 2) DENSE_RANK
SELECT DISTINCT Salary AS SecondHighest
FROM (SELECT Salary, DENSE_RANK() OVER (ORDER BY Salary DESC) AS dr FROM dbo.Employees) t
WHERE dr = 2;

-- EXPECTED: 95000.00 (one row; zero rows if only one distinct salary)

-- 3) Per department, ties included
SELECT Dept, Name, Salary
FROM (SELECT Dept, Name, Salary,
             DENSE_RANK() OVER (PARTITION BY Dept ORDER BY Salary DESC) AS dr
      FROM dbo.Employees) t
WHERE dr = 2
ORDER BY Dept, Name;

-- EXPECTED:
-- Dept        | Name  | Salary
-- Engineering | Bob   | 95000.00
-- Engineering | Carol | 95000.00
-- Marketing   | Grace | 60000.00
-- Sales       | Eve   | 75000.00

-- Results derived from equivalent queries on SQLite (same data, same window syntax);
-- salary shown as 95000 there, DECIMAL(10,2) displays 95000.00. Not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
The subquery removes the top salary, so the remaining MAX is the second distinct value; an aggregate over zero rows returns NULL, which satisfies "NULL if missing". DENSE_RANK gives equal salaries the same rank without gaps, so rank 2 is always the second distinct value.
हिंदी: Top हटाकर बचे हुए में MAX = दूसरा। DENSE_RANK में ties को same rank मिलता है, gap नहीं।

---

## ⚡ Alternative Solution

```sql
-- OFFSET FETCH on distinct salaries (SQL Server 2012+)
SELECT Salary
FROM (SELECT DISTINCT Salary FROM dbo.Employees) d
ORDER BY Salary DESC
OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY;

-- Always return one row, NULL if missing:
SELECT (SELECT DISTINCT Salary FROM dbo.Employees
        ORDER BY Salary DESC OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY) AS SecondHighest;

-- TOP twice (old style, works on any version)
SELECT TOP (1) Salary FROM (SELECT DISTINCT TOP (2) Salary FROM dbo.Employees ORDER BY Salary DESC) t ORDER BY Salary ASC;
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: no DISTINCT -> returns the top salary again when it has ties
SELECT Salary FROM dbo.Employees ORDER BY Salary DESC OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY;
-- (here it would return 95000 only by luck; with two 120000 rows it returns 120000)

-- Wrong: ROW_NUMBER() = 2 counts a duplicate of the top salary as "second"
-- Wrong: TOP 2 ... ORDER BY ... then MIN()  -> fails with ties and returns wrong value if fewer than 2 distinct
-- Wrong: forgetting NULL requirement: plain OFFSET returns an empty set, not NULL
```

---

## 🎯 Interview Tip (1 line)
Say: "I clarify distinct vs row-based and the no-second-value case first. Then I give the subquery for portability, DENSE_RANK to generalize to Nth and per group, and OFFSET FETCH as the short one." Mention that for large tables an index on Salary makes the MAX/TOP forms cheap.

---

## 🔗 Related Questions
→ Q045 (Nth highest salary - 5 ways) | Q056 (ROW_NUMBER/RANK/DENSE_RANK) | Q047 (Top N per group) | Q002 (OFFSET FETCH)
