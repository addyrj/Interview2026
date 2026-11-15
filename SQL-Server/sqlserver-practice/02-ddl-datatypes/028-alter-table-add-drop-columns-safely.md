---

# Q028. ALTER TABLE — Add/Drop Columns Safely
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: ALGORITHM=INSTANT/INPLACE on 8.0; PostgreSQL: ADD COLUMN with constant DEFAULT is metadata-only since 11)

---

## ❓ Question
On a live Employees table with millions of rows, add a NOT NULL `IsActive` flag with a default, add a nullable `Notes` column, and drop the old `Phone` column. What can lock the table, what is metadata-only, and what must you remove before a column can be dropped?

---

## 💡 Quick Concept (2 lines only)
Adding a nullable column is a quick metadata change. Adding NOT NULL with a constant DEFAULT is also metadata-only on modern SQL Server (Enterprise since 2012, Azure SQL), but `ALTER COLUMN` to change a type or size can rewrite the table. DROP COLUMN fails while a default, check, index or FK depends on the column.
हिंदी: Nullable column जोड़ना तुरंत होता है। NOT NULL + constant DEFAULT भी modern version में metadata-only है। Type बदलना भारी हो सकता है; column drop से पहले उसके default/index/constraint हटाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Employees (
  EmployeeId INT           NOT NULL CONSTRAINT PK_Employees PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  Phone      VARCHAR(20)   NULL
);

INSERT INTO Employees (EmployeeId, Name, Phone) VALUES
  (1, N'Asha', '111'),
  (2, N'Ravi', '222');
GO

-- ============================================
-- SOLUTION
-- ============================================

-- 1) Add NOT NULL column with a NAMED default so existing rows get 1
ALTER TABLE Employees
  ADD IsActive BIT NOT NULL CONSTRAINT DF_Employees_IsActive DEFAULT (1);

-- 2) Add nullable column
ALTER TABLE Employees ADD Notes NVARCHAR(500) NULL;

SELECT EmployeeId, Name, Phone, IsActive, Notes FROM Employees ORDER BY EmployeeId;

-- Output:
-- EmployeeId | Name | Phone | IsActive | Notes
-- 1          | Asha | 111   | 1        | NULL
-- 2          | Ravi | 222   | 1        | NULL

-- 3) Drop a column (2016+: IF EXISTS makes scripts re-runnable)
ALTER TABLE Employees DROP COLUMN IF EXISTS Phone;

SELECT EmployeeId, Name, IsActive, Notes FROM Employees ORDER BY EmployeeId;

-- Output:
-- EmployeeId | Name | IsActive | Notes
-- 1          | Asha | 1        | NULL
-- 2          | Ravi | 1        | NULL

-- Outputs derived from the equivalent ALTER TABLE ADD/DROP COLUMN on SQLite 3.49 (it shows BIT as
-- 1); locking and metadata-only behaviour are per Microsoft docs and were not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
Because the default is a runtime constant, SQL Server records it in metadata and returns it for old rows without touching every page, so the ALTER is near-instant and the schema lock is brief. DROP COLUMN is also logical first: space is reclaimed later by an index rebuild. A named default lets you remove it cleanly (`DROP CONSTRAINT DF_Employees_IsActive`) before dropping the column.
हिंदी: Constant DEFAULT metadata में रखा जाता है, पुरानी rows छूती नहीं, इसलिए ALTER तेज़। DROP COLUMN भी पहले logical होता है; space rebuild पर मिलता है।

---

## ⚡ Alternative Solution

```sql
-- Dropping a column that has dependencies: remove them first, in order
ALTER TABLE Employees DROP CONSTRAINT DF_Employees_IsActive;   -- default
-- DROP INDEX IX_Employees_Phone ON Employees;                   -- indexes using the column
-- ALTER TABLE Employees DROP CONSTRAINT CK_Employees_Phone;     -- checks / FKs
ALTER TABLE Employees DROP COLUMN IsActive;

-- Safe "expand / migrate / contract" pattern for risky changes (no downtime):
-- 1) ADD the new nullable column, 2) backfill in small batches, 3) deploy code using it,
-- 4) add NOT NULL / default, 5) drop the old column in a later release.
ALTER TABLE Employees ADD FullName NVARCHAR(200) NULL;

-- Make an existing column NOT NULL (fails if NULLs exist - backfill first)
UPDATE Employees SET FullName = Name WHERE FullName IS NULL;
ALTER TABLE Employees ALTER COLUMN FullName NVARCHAR(200) NOT NULL;
-- Change of length/type: widening NVARCHAR(100) -> NVARCHAR(200) is metadata-only in many cases;
-- narrowing or changing type scans/rewrites. Test on a copy and check the plan/log impact.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: add a NOT NULL column without a default
ALTER TABLE Employees ADD Grade INT NOT NULL;
-- Fails on a non-empty table (existing rows would be NULL). Add a DEFAULT, or add NULL -> backfill -> NOT NULL.

-- ❌ Wrong: dropping a column and expecting it to just work
ALTER TABLE Employees DROP COLUMN Phone;
-- Fails if an index, CHECK, FK, computed column or schema-bound view still depends on it.

-- ❌ Wrong: unnamed defaults (auto name DF__Employees__IsAct__3A81B327) - scripts differ per environment
-- ❌ Wrong: running ALTER COLUMN on a 500M-row table during business hours without testing -
--           it can block everything behind a schema-modification lock; use ONLINE options where
--           supported (e.g. ALTER TABLE ... WITH (ONLINE = ON) for some operations on Enterprise/Azure SQL).
-- ❌ Wrong: SELECT * code or ORM models that break when a column disappears -> deploy code first.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use the expand-migrate-contract pattern: add nullable, backfill in batches, enforce NOT NULL, then drop later. I always name defaults, check dependencies in sys.sql_expression_dependencies/sys.default_constraints before DROP COLUMN, and rehearse on a restored copy for ALTER COLUMN type changes." Mention that queued schema-modification locks can block the whole table, so set `SET LOCK_TIMEOUT` for migrations.

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE with constraints) | Q027 (CHECK and DEFAULT) | Q082 (procedure versioning and deployment) | Q170 (migrations with Flyway/EF/dbmate)
