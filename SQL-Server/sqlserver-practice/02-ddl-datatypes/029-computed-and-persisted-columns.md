---

# Q029. Computed Columns and Persisted Columns
# Category: DDL + Data Types
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL 5.7+ = GENERATED ... VIRTUAL/STORED; PostgreSQL 12+ = GENERATED ALWAYS AS ... STORED only)

---

## ❓ Question
An `OrderLines` table stores Qty and UnitPrice. Add a `LineTotal` column that is always `Qty * UnitPrice` without the app ever writing it. Then: (a) make it PERSISTED, (b) index it, (c) add `FullName` on Employees. What are the rules for PERSISTED and indexing?

---

## 💡 Quick Concept (2 lines only)
A computed column is defined by an expression over other columns of the same row. Non-persisted = calculated on every read; PERSISTED = stored physically, updated on write, and can be indexed (indexing needs a deterministic, precise expression).
हिंदी: Computed column = formula वाला column। PERSISTED में value disk पर store होती है, इसलिए index बन सकता है और read fast रहता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE OrderLines (
    LineId     INT IDENTITY(1,1) PRIMARY KEY,
    Product    VARCHAR(50)   NOT NULL,
    Qty        INT           NOT NULL,
    UnitPrice  DECIMAL(10,2) NOT NULL,
    LineTotal  AS (Qty * UnitPrice) PERSISTED      -- stored, maintained by engine
);

INSERT INTO OrderLines (Product, Qty, UnitPrice) VALUES
  ('Keyboard', 3,  25.00),
  ('Monitor',  2, 199.99),
  ('Mouse',    5,  12.50);

CREATE TABLE Employees (
    EmpId     INT IDENTITY(1,1) PRIMARY KEY,
    FirstName NVARCHAR(50) NOT NULL,
    LastName  NVARCHAR(50) NOT NULL,
    FullName  AS (FirstName + N' ' + LastName)     -- not persisted: computed at read time
);

INSERT INTO Employees (FirstName, LastName) VALUES (N'Asha', N'Verma'), (N'Rohan', N'Mehta');

-- ============================================
-- SOLUTION: query, filter and index the computed column
-- ============================================
SELECT LineId, Product, Qty, UnitPrice, LineTotal FROM OrderLines ORDER BY LineId;

-- Index on the persisted column (supports WHERE LineTotal > x without recomputing)
CREATE INDEX IX_OrderLines_LineTotal ON OrderLines (LineTotal);

SELECT Product, LineTotal FROM OrderLines WHERE LineTotal > 70 ORDER BY LineId;

-- Add a computed column to an existing table (metadata-only for non-persisted)
ALTER TABLE OrderLines ADD LineTotalWithTax AS (Qty * UnitPrice * 1.18);

-- Inspect which columns are computed / persisted
SELECT name, definition, is_persisted FROM sys.computed_columns WHERE object_id = OBJECT_ID('OrderLines');

-- ============================================
-- EXPECTED OUTPUT (result derived from equivalent query on SQLite generated columns;
-- not executed on SQL Server. Display formatting such as 75.00 may differ in SSMS.)
-- ============================================
-- LineId | Product  | Qty | UnitPrice | LineTotal
-- 1      | Keyboard | 3   | 25.00     | 75.00
-- 2      | Monitor  | 2   | 199.99    | 399.98
-- 3      | Mouse    | 5   | 12.50     | 62.50
--
-- Product  | LineTotal   (WHERE LineTotal > 70)
-- Keyboard | 75.00
-- Monitor  | 399.98
--
-- Employees.FullName -> 'Asha Verma', 'Rohan Mehta'
```

---

## 🔍 Why This Works (3 lines max)
The engine evaluates the expression per row; PERSISTED stores the result so reads and indexes cost nothing extra, at the price of a little write overhead and disk. An index on a computed column needs the expression to be deterministic and precise (no GETDATE(), no float-imprecise results unless PERSISTED).
हिंदी: Expression हर row पर चलता है। Deterministic (GETDATE जैसा नहीं) होना चाहिए तभी index बनेगा। Computed column में सीधे INSERT/UPDATE नहीं कर सकते।

---

## ⚡ Alternative Solution

```sql
-- Option 1: non-persisted computed column + index on it. SQL Server can index a
-- non-persisted column if the expression is deterministic and precise (index stores the value).
-- Option 2: a view (no storage, but cannot be updated through it freely).
CREATE VIEW dbo.vOrderLines AS
SELECT LineId, Product, Qty, UnitPrice, Qty * UnitPrice AS LineTotal FROM dbo.OrderLines;

-- Option 3: compute in the app / trigger (avoid — drifts out of sync when someone forgets).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Trying to write to a computed column
INSERT INTO OrderLines (Product, Qty, UnitPrice, LineTotal) VALUES ('Cable', 1, 5, 5);
-- Fails: you cannot insert/update a computed column.

-- ❌ Non-deterministic expression cannot be PERSISTED or indexed
ALTER TABLE OrderLines ADD AddedOn AS (GETDATE()) PERSISTED;   -- fails: nondeterministic
-- ❌ Assuming a computed column makes SELECT free: a non-persisted column using a
--    scalar UDF can block parallelism and be slow. Prefer inline expressions.
-- ✅ Use PERSISTED + index for hot filters; keep the expression simple and deterministic.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use computed columns to enforce a single source of truth for derived values — PERSISTED plus an index when I filter or sort on it often. I check ISDETERMINISTIC/IsPrecise via COLUMNPROPERTY, and I avoid scalar UDFs inside them because of the performance hit." Mention that persisted computed columns also help when you need a SARGable form of an expression (for example, a computed `OrderYear`).

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE with constraints) | Q028 (ALTER TABLE) | Q088 (Scalar UDF cost) | Q110 (SARGable predicates)
