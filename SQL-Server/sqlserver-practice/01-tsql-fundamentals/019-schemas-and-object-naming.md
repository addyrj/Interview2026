---

# Q019. Schemas and Object Naming
# Category: T-SQL FUNDAMENTALS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: "schema" = database; PostgreSQL: schemas exist, resolved via search_path)

---

## ❓ Question
Organize an app into `sales` and `hr` schemas, create tables in them, grant a role access to one schema only, and explain the 4-part name, the default `dbo` schema, and why you should always schema-qualify object names.

---

## 💡 Quick Concept (2 lines only)
A schema is a namespace and security boundary inside a database: `server.database.schema.object`. Unqualified names resolve to the user's default schema, then `dbo`, which costs lookups and can pick the wrong object.
हिंदी: Schema = database के अंदर namespace + security boundary। हमेशा `dbo.Orders` जैसा qualified नाम लिखो, वरना गलत object या extra lookup हो सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE SCHEMA sales AUTHORIZATION dbo;
GO
CREATE SCHEMA hr AUTHORIZATION dbo;
GO

CREATE TABLE sales.Orders (
  OrderId INT PRIMARY KEY,
  Amount  DECIMAL(10,2) NOT NULL
);

CREATE TABLE hr.Employees (
  EmployeeId INT PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL
);

INSERT INTO sales.Orders (OrderId, Amount) VALUES (1, 500.00), (2, 300.00);
INSERT INTO hr.Employees (EmployeeId, Name) VALUES (1, 'Asha');
GO

-- ============================================
-- SOLUTION
-- ============================================

-- Always schema-qualify
SELECT o.OrderId, o.Amount FROM sales.Orders AS o;

-- Output:
-- OrderId | Amount
-- 1       | 500.00
-- 2       | 300.00

-- List objects per schema
SELECT s.name AS SchemaName, t.name AS TableName
FROM sys.tables AS t
JOIN sys.schemas AS s ON s.schema_id = t.schema_id
WHERE s.name IN ('sales', 'hr')
ORDER BY s.name;

-- Output:
-- SchemaName | TableName
-- hr         | Employees
-- sales      | Orders

-- Security at schema level: reporting role may read sales only
CREATE ROLE ReportingReader;
GRANT SELECT ON SCHEMA::sales TO ReportingReader;
DENY  SELECT ON SCHEMA::hr    TO ReportingReader;

-- Move an object to another schema
ALTER SCHEMA hr TRANSFER sales.Orders;   -- (just shows syntax; permissions on the object are reset)

-- Result of the first SELECT derived from SQLite 3.49 with ATTACH DATABASE as stand-in schemas;
-- sys.* catalog views, roles and GRANT are not available there: not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
Objects belong to a schema, not to a user, so ownership changes do not break code. Granting on `SCHEMA::sales` covers every current and future table, view and procedure in it. Qualified names let the engine reuse one plan per object instead of resolving per-user.
हिंदी: Object schema का होता है, user का नहीं। GRANT ON SCHEMA से उस schema की सारी present/future objects पर permission मिलती है।

---

## ⚡ Alternative Solution

```sql
-- Default schema per user (what unqualified names resolve to)
CREATE USER AppUser WITHOUT LOGIN WITH DEFAULT_SCHEMA = sales;
SELECT SCHEMA_NAME() AS CurrentSchema;      -- run as dbo -> dbo
-- Cross-database / linked server: 3- and 4-part names
-- SELECT * FROM OtherDb.sales.Orders;
-- SELECT * FROM [LinkedServer].OtherDb.sales.Orders;   -- not available in Azure SQL Database
-- Bracket identifiers that are reserved or contain spaces:
SELECT 1 AS [Order], 2 AS [Total Amount];
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: unqualified names in production code
SELECT * FROM Orders;          -- resolves to default schema first, then dbo; ambiguity when both exist
-- ✅ SELECT ... FROM dbo.Orders;

-- ❌ Wrong: prefixing procedures with sp_  (SQL Server looks in master first, adds lookups,
--          and a future system proc can hijack the name)
CREATE PROCEDURE dbo.sp_GetOrders AS SELECT 1;   -- ✅ name it usp_/proc_ or no prefix

-- ❌ Wrong: putting everything in dbo forever - you lose schema-level permission and organisation
-- ❌ Wrong: SELECT * FROM sys.objects WHERE name = 'Orders' -> ignores schema; filter on schema_id too
```

---

## 🎯 Interview Tip (1 line)
Say: "I use schemas as bounded contexts (sales, hr, audit) and for permissions with GRANT ... ON SCHEMA. All code is schema-qualified, no sp_ prefix, and I set a non-dbo DEFAULT_SCHEMA for app users so they cannot accidentally create objects in dbo." Contrast MySQL, where schema just means database.

---

## 🔗 Related Questions
→ Q099 (synonyms and sequences) | Q135 (logins, users and roles) | Q136 (least-privilege permissions) | Q079 (procedure vs function vs view)
