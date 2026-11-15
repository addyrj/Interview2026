---

# Q095. INSTEAD OF Triggers
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (INSTEAD OF works on tables and views; SQLite/PostgreSQL allow it only on views; MySQL has none)

---

## ❓ Question
Make `DELETE FROM Customers` perform a soft delete instead of removing rows, and show how an INSTEAD OF trigger can make a complex view updatable.

---

## 💡 Quick Concept (2 lines only)
An INSTEAD OF trigger replaces the triggering statement: the original DML never runs, only your trigger body does (using `inserted`/`deleted`). Use it for soft deletes, updatable multi-table views and pre-validation.
हिंदी: INSTEAD OF trigger original statement की जगह चलता है, असली DELETE होता ही नहीं। Soft delete और complex views को updatable बनाने में काम आता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Customers (
  CustomerId INT PRIMARY KEY,
  Name       NVARCHAR(100) NOT NULL,
  IsDeleted  BIT NOT NULL DEFAULT 0
);

INSERT INTO dbo.Customers (CustomerId, Name) VALUES
  (1, N'Asha Rao'), (2, N'Vikram Shah'), (3, N'Meera Iyer');
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER TRIGGER dbo.trg_Customers_SoftDelete
ON dbo.Customers
INSTEAD OF DELETE
AS
BEGIN
  SET NOCOUNT ON;

  UPDATE c
  SET c.IsDeleted = 1
  FROM dbo.Customers c
  JOIN deleted d ON d.CustomerId = c.CustomerId;   -- set-based: handles many rows
END;
GO

DELETE FROM dbo.Customers WHERE CustomerId IN (1, 2);

SELECT CustomerId, Name, IsDeleted FROM dbo.Customers ORDER BY CustomerId;

-- EXPECTED OUTPUT (derived from an equivalent INSTEAD OF DELETE trigger on a view in SQLite,
-- since SQLite allows INSTEAD OF only on views; the table-level trigger is not executed on
-- SQL Server; behaviour per Microsoft docs):
-- CustomerId | Name        | IsDeleted
-- 1          | Asha Rao    | 1
-- 2          | Vikram Shah | 1
-- 3          | Meera Iyer  | 0
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The trigger fires before any change; since the DELETE is replaced, constraints and the physical delete are bypassed and only the UPDATE runs. `deleted` holds the rows the statement targeted, so the join processes all of them at once. Only one INSTEAD OF trigger per action per table is allowed.
हिंदी: Trigger पहले चलता है और DELETE की जगह ले लेता है। `deleted` में target rows होती हैं। एक table पर हर action के लिए एक ही INSTEAD OF trigger।

---

## ⚡ Alternative Solution

```sql
-- Updatable multi-table view: INSTEAD OF INSERT splits the row into two tables
CREATE VIEW dbo.vCustomerAddress AS
SELECT c.CustomerId, c.Name, a.City
FROM dbo.Customers c JOIN dbo.Addresses a ON a.CustomerId = c.CustomerId;
GO
CREATE TRIGGER dbo.trg_vCustomerAddress_Ins ON dbo.vCustomerAddress INSTEAD OF INSERT AS
BEGIN
  INSERT INTO dbo.Customers (CustomerId, Name) SELECT CustomerId, Name FROM inserted;
  INSERT INTO dbo.Addresses (CustomerId, City) SELECT CustomerId, City FROM inserted;
END;
-- Cleaner and more explicit alternative: a stored procedure (usp_AddCustomer) with a transaction.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: expecting the original DML to still happen -> rows are NOT deleted unless the trigger does it.
-- ❌ Wrong: trying to use INSTEAD OF on a table AND inspecting inserted values for IDENTITY
--    (identity values are not assigned yet inside INSTEAD OF INSERT).
-- ❌ Wrong: callers have no idea DELETE is intercepted -> "rows affected" can mislead and
--    maintenance DELETEs for GDPR do not erase anything.
-- ✅ Document it, test multi-row statements, offer an explicit purge procedure.
```

---

## 🎯 Interview Tip (1 line)
Say: "INSTEAD OF triggers are useful for making views updatable and for transparent soft delete, but they hide behaviour, so I prefer procedures or explicit APIs for business logic, keep INSTEAD OF to compatibility cases, and always write them for multi-row statements."

---

## 🔗 Related Questions
→ Q094 (AFTER triggers) | Q096 (inserted and deleted tables) | Q093 (Updatable views, WITH CHECK OPTION) | Q085 (Soft delete procedure) | Q098 (When NOT to use triggers)
