---

# Q018. Collation and Case Sensitivity
# Category: T-SQL FUNDAMENTALS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: default utf8mb4 collations are case-insensitive `_ci`; PostgreSQL: text comparison is case-sensitive by default, use ILIKE/CITEXT)

---

## ❓ Question
A login lookup `WHERE Name = 'ravi'` returns rows `Ravi`, `RAVI` and `ravi`. Why? How do you make one query case-sensitive without changing the column, how do you set a column's collation, and what is a collation conflict?

---

## 💡 Quick Concept (2 lines only)
A collation defines sort order and comparison rules (case `CI/CS`, accent `AI/AS`, binary `BIN2`). Default for most installs, and for new Azure SQL databases, is `SQL_Latin1_General_CP1_CI_AS` (case-insensitive, accent-sensitive), so `'ravi' = 'RAVI'` is true.
हिंदी: Collation तय करता है कि comparison/sort कैसे होगा। Default CI_AS में 'ravi' = 'RAVI' true आता है; case-sensitive चाहिए तो COLLATE CS_AS लगाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Customers (
  CustomerId INT PRIMARY KEY,
  Name       VARCHAR(50) NOT NULL
);

INSERT INTO Customers (CustomerId, Name) VALUES
  (1, 'Ravi'),
  (2, 'RAVI'),
  (3, 'ravi'),
  (4, 'Ravi Kumar');
GO

-- ============================================
-- SOLUTION
-- ============================================

-- 1) Default (case-insensitive) collation: all three spellings match
SELECT CustomerId, Name FROM Customers WHERE Name = 'ravi';

-- Output (with a *_CI_* database collation):
-- CustomerId | Name
-- 1          | Ravi
-- 2          | RAVI
-- 3          | ravi

-- 2) Force case-sensitive comparison for this query only
SELECT CustomerId, Name
FROM Customers
WHERE Name = 'ravi' COLLATE SQL_Latin1_General_CP1_CS_AS;

-- Output:
-- CustomerId | Name
-- 3          | ravi

-- Results derived from SQLite 3.49 using COLLATE NOCASE and COLLATE BINARY as stand-ins for
-- CI and CS; not executed on SQL Server (assumes a case-insensitive database collation).

-- 3) Set a collation on a column at creation time or later
ALTER TABLE Customers
  ALTER COLUMN Name VARCHAR(50) COLLATE Latin1_General_100_CS_AS NOT NULL;

-- 4) Inspect collations
SELECT name, collation_name FROM sys.databases WHERE name = DB_NAME();
SELECT name, collation_name FROM sys.columns
WHERE object_id = OBJECT_ID('dbo.Customers') AND collation_name IS NOT NULL;
-- (Values depend on your server; not shown.)
```

---

## 🔍 Why This Works (3 lines max)
Comparison uses the collation of the operands: column collation if the column is involved, else the database default. `COLLATE` on the literal makes the explicit collation win, so the compare becomes case-sensitive for that predicate. Note it can make the predicate non-SARGable on an index built with a different collation.
हिंदी: Column का collation compare तय करता है; literal पर COLLATE लगाने से वही चलता है। पर index का collation अलग हो तो seek नहीं मिलता।

---

## ⚡ Alternative Solution

```sql
-- Case-sensitive match without changing collation: compare binary representation too
SELECT CustomerId, Name
FROM Customers
WHERE Name = 'ravi'                                  -- uses the index (CI)
  AND CAST(Name AS VARBINARY(50)) = CAST('ravi' AS VARBINARY(50));   -- filters to exact case

-- Database / column level choice for a case-sensitive app: create the DB with a _CS_ collation
CREATE DATABASE AppDb COLLATE Latin1_General_100_CS_AS;
-- Azure SQL Database: collation is chosen at database creation and cannot be changed afterwards.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: comparing columns with different collations (e.g., after a migration or with #temp)
-- tempdb uses the SERVER default collation; a database with a different collation hits
-- "Cannot resolve the collation conflict ..." when joining a user table to a #temp table.
CREATE TABLE #Names (Name VARCHAR(50));
SELECT c.CustomerId FROM Customers c JOIN #Names n ON n.Name = c.Name;   -- may fail on mismatch
-- ✅ Fix: define the temp table column with COLLATE DATABASE_DEFAULT
CREATE TABLE #Names2 (Name VARCHAR(50) COLLATE DATABASE_DEFAULT);

-- ❌ Wrong: assuming UNIQUE on Email blocks 'A@x.com' and 'a@x.com' in a CS database (it will not)
-- ❌ Wrong: wrapping the column in LOWER()/UPPER() to "ignore case" -> non-SARGable and unnecessary under CI
```

---

## 🎯 Interview Tip (1 line)
Say: "Default is case-insensitive, accent-sensitive, so unique emails and logins are already case-insensitive. I use COLLATE only per query, set collation at database creation (it is hard to change later, especially in Azure SQL), and I use DATABASE_DEFAULT for temp tables to avoid collation conflicts. Unicode-friendly `_100_` or `_UTF8` (2019+) collations are worth knowing."

---

## 🔗 Related Questions
→ Q009 (LIKE and wildcard pitfalls) | Q022 (VARCHAR vs NVARCHAR) | Q110 (SARGable predicates) | Q184 (SQL Server vs MySQL vs PostgreSQL)
