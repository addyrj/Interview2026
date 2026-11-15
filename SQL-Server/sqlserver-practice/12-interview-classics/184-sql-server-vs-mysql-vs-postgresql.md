---

# Q184. SQL Server vs MySQL vs PostgreSQL
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (compared with MySQL 8+ and PostgreSQL)

---

## ❓ Question
You know MySQL/PostgreSQL and are moving to a SQL Server + Azure SQL project. Show how the same everyday tasks differ in T-SQL, and explain the architectural differences an interviewer expects.

Table used: `Employees(EmployeeId, Name, Dept, Salary)` and `Orders(OrderId, CustomerId, Amount)`.

---

## 💡 Quick Concept (2 lines only)
All three speak SQL, but T-SQL has its own syntax (TOP, `+` concat, IDENTITY, procedural batches, `@` variables) and its own engine behaviour (locking by default, tempdb, plan cache). PostgreSQL is MVCC-first and extensible; MySQL is simple and InnoDB-centric; SQL Server is a tightly integrated enterprise platform (SSMS, SSIS/SSRS, Azure).
हिंदी: Syntax थोड़ा अलग है (TOP, IDENTITY, @var)। SQL Server में default locking है, PostgreSQL में MVCC। Azure integration SQL Server की ताकत है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (T-SQL)
-- ============================================
CREATE TABLE dbo.Employees (
  EmployeeId INT IDENTITY(1,1) PRIMARY KEY,   -- MySQL: AUTO_INCREMENT | PgSQL: GENERATED ... AS IDENTITY / SERIAL
  Name       NVARCHAR(100) NOT NULL,
  Dept       VARCHAR(50)   NOT NULL,
  Salary     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Employees (Name, Dept, Salary) VALUES
  (N'Alice', 'Engineering', 120000), (N'Bob', 'Sales', 90000), (N'Carol', 'Sales', 75000);
GO

-- 1) Limit rows
SELECT TOP (2) Name, Salary FROM dbo.Employees ORDER BY Salary DESC;          -- MySQL/PgSQL: ... LIMIT 2
SELECT Name FROM dbo.Employees ORDER BY Salary DESC
  OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY;                                      -- ORDER BY is mandatory; MySQL/PgSQL: LIMIT 1 OFFSET 1

-- 2) String concat, current time, null default
SELECT Name + ' (' + Dept + ')' AS Label,        -- MySQL: CONCAT() | PgSQL: ||   (CONCAT() works in T-SQL too)
       GETDATE()                AS Now_,          -- MySQL: NOW() | PgSQL: now()
       ISNULL(NULL, 'n/a')      AS Fallback       -- MySQL: IFNULL | PgSQL: COALESCE
FROM dbo.Employees;

-- 3) Upsert
-- T-SQL: MERGE (has known gotchas) or UPDATE-then-INSERT inside a transaction
-- MySQL: INSERT ... ON DUPLICATE KEY UPDATE | PgSQL: INSERT ... ON CONFLICT DO UPDATE

-- 4) Return the inserted row
INSERT INTO dbo.Employees (Name, Dept, Salary)
OUTPUT inserted.EmployeeId, inserted.Name
VALUES (N'Dan', 'Sales', 60000);                                              -- PgSQL: RETURNING | MySQL 8: no equivalent (LAST_INSERT_ID)

-- 5) Procedural code: T-SQL stored procedure
CREATE PROCEDURE dbo.usp_GetEmployeesByDept @Dept VARCHAR(50)
AS
BEGIN
  SET NOCOUNT ON;
  SELECT EmployeeId, Name, Salary FROM dbo.Employees WHERE Dept = @Dept;
END;
GO
EXEC dbo.usp_GetEmployeesByDept @Dept = 'Sales';

-- EXPECTED (query 1, TOP 2 by Salary DESC):
-- Name  | Salary
-- Alice | 120000.00
-- Bob   | 90000.00
-- Syntax comparison is documentation-level; not executed on SQL Server.
-- Result hand-checked from the 3 inserted rows (top 2 salaries).
```

| Area | SQL Server | MySQL (InnoDB) | PostgreSQL |
|---|---|---|---|
| Concurrency default | Locking (READ COMMITTED); RCSI optional (ON in Azure SQL DB) | MVCC, REPEATABLE READ default | MVCC, READ COMMITTED default |
| Procedural language | T-SQL | SQL/PSM | PL/pgSQL + many others |
| Plans/tuning | Plan cache, Query Store, rich DMVs | EXPLAIN / EXPLAIN ANALYZE | EXPLAIN ANALYZE |
| Clustered index | Table is the clustered index (if defined) | PK is always clustered | Heap + indexes (CLUSTER is one-off) |
| JSON | JSON functions on NVARCHAR (native json type only in newer versions) | native JSON | jsonb with GIN indexes |
| Cloud | Azure SQL DB / MI / VM | RDS, Cloud SQL | RDS, Azure Flexible Server, etc. |

Check the native `json` type availability against your target version in Microsoft docs.

---

## 🔍 Why This Works (3 lines max)
Most differences are dialect (TOP vs LIMIT, `+` vs `||`) plus engine defaults (locking vs MVCC). Learn the dialect once, then think about isolation, plan caching and tempdb, because those cause the production problems. In SQL Server a stored procedure is the normal API for application code; in PostgreSQL/MySQL apps more often send parameterized SQL.
हिंदी: Dialect सीखना आसान है, असली फर्क isolation और engine behaviour का है। SQL Server में stored procedure आम तौर पर app की API होती है।

---

## ⚡ Alternative Solution

```sql
-- ANSI-portable versions that run on all three engines (SQL Server 2012+):
SELECT Name FROM dbo.Employees
ORDER BY Salary DESC
OFFSET 0 ROWS FETCH FIRST 2 ROWS ONLY;     -- MySQL does not support FETCH FIRST; use LIMIT there

SELECT COALESCE(NULL, 'n/a');              -- portable, unlike ISNULL / IFNULL
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: MySQL/PgSQL habits in T-SQL
SELECT * FROM dbo.Employees LIMIT 5;                 -- LIMIT does not exist in T-SQL
SELECT 'a' || 'b';                                   -- || is not concatenation in T-SQL
-- Wrong: assuming string comparison is case-sensitive; the common default collation is case-insensitive,
--        so 'alice' = 'Alice' is TRUE (depends on database collation).
-- Wrong: assuming reads never block writers (true in PgSQL MVCC, NOT by default in SQL Server).
```

---

## 🎯 Interview Tip (1 line)
Say: "Coming from PostgreSQL/MySQL, I map syntax quickly, but I watch three engine differences: locking vs MVCC (RCSI), clustered index design on every table, and plan cache/parameter sniffing. In Azure SQL I rely on Query Store." Avoid bashing either engine; give a use-case-based comparison.

---

## 🔗 Related Questions
→ Q120 (RCSI) | Q102 (Clustered vs non-clustered) | Q157 (Azure SQL options) | Q084 (Upsert) | Q002 (TOP / OFFSET FETCH)
