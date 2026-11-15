
---

# Q128. Savepoints and Nested Transactions
# Category: TRANSACTIONS + LOCKING
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL/MySQL use `SAVEPOINT x` / `ROLLBACK TO x`; T-SQL uses `SAVE TRANSACTION x` / `ROLLBACK TRANSACTION x`)

---

## ❓ Question
Insert an Order, then try to insert its optional OrderItems; if the items part fails, keep the order and undo only the items. Also explain what `@@TRANCOUNT` does when a procedure calls another procedure that has its own BEGIN TRAN, and why "nested transactions" are not real.

---

## 💡 Quick Concept (2 lines only)
`SAVE TRANSACTION name` marks a point; `ROLLBACK TRANSACTION name` undoes work back to it and keeps the outer transaction alive. A nested `BEGIN TRAN` only increments `@@TRANCOUNT`; inner COMMIT just decrements, and any plain ROLLBACK rolls back everything.
हिंदी: SAVE TRANSACTION से बीच में point बनता है और उसी तक rollback हो सकता है। Nested BEGIN TRAN असल में सिर्फ counter बढ़ाता है, ROLLBACK पूरा उड़ा देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1,1) PRIMARY KEY,
  CustomerId INT NOT NULL,
  Total      DECIMAL(10,2) NOT NULL
);
CREATE TABLE dbo.OrderItems (
  ItemId  INT IDENTITY(1,1) PRIMARY KEY,
  OrderId INT NOT NULL REFERENCES dbo.Orders(OrderId),
  Sku     VARCHAR(20) NOT NULL,
  Qty     INT NOT NULL CHECK (Qty > 0)
);
GO

-- ============================================
-- SOLUTION: savepoint inside one transaction
-- ============================================
SET XACT_ABORT OFF;   -- with ON, any runtime error dooms the whole transaction, savepoint cannot help
BEGIN TRANSACTION;
  INSERT INTO dbo.Orders (CustomerId, Total) VALUES (10, 100.00);
  DECLARE @OrderId INT = SCOPE_IDENTITY();

  SAVE TRANSACTION sp_items;
  BEGIN TRY
    INSERT INTO dbo.OrderItems (OrderId, Sku, Qty) VALUES (@OrderId, 'SKU-A', 0);  -- violates CHECK
  END TRY
  BEGIN CATCH
    IF XACT_STATE() = 1                       -- 1 = still committable
      ROLLBACK TRANSACTION sp_items;          -- undo ONLY the items
  END CATCH;

  INSERT INTO dbo.OrderItems (OrderId, Sku, Qty) VALUES (@OrderId, 'SKU-B', 1);
COMMIT TRANSACTION;

SELECT * FROM dbo.Orders;  SELECT * FROM dbo.OrderItems;
GO

-- ============================================
-- NESTED "TRANSACTIONS" and @@TRANCOUNT
-- ============================================
BEGIN TRAN;            -- @@TRANCOUNT = 1
  BEGIN TRAN;          -- @@TRANCOUNT = 2  (not a new transaction!)
  COMMIT;              -- @@TRANCOUNT = 1  (nothing is committed yet)
ROLLBACK;              -- @@TRANCOUNT = 0  (everything rolled back, even the "committed" inner)
```

```sql
-- EXPECTED OUTPUT
-- Savepoint logic result derived from equivalent SAVEPOINT / ROLLBACK TO on SQLite; not executed on SQL Server.
-- Orders:     OrderId=1, CustomerId=10, Total=100.0   (order kept)
-- OrderItems: ItemId=2 (SQLite numbering; SQL Server IDENTITY would show 1 or 2: a rolled-back
--             insert still consumes the identity value), OrderId=1, Sku='SKU-B', Qty=1
-- SKU-A row is gone (rolled back to the savepoint).
-- @@TRANCOUNT behaviour per Microsoft docs; not executed.
```

---

## 🔍 Why This Works (3 lines max)
A savepoint records a position in the log, so rolling back to it undoes later work but leaves the transaction open for more work and a final COMMIT. SQL Server has a single physical transaction; `@@TRANCOUNT` is just a nesting counter, and only the outermost COMMIT makes data durable.
हिंदी: Savepoint तक rollback करने पर transaction खुली रहती है। असली transaction एक ही होती है, सिर्फ़ सबसे बाहरी COMMIT ही data को पक्का करता है।

---

## ⚡ Alternative Solution

```sql
-- Safe pattern for procedures that may be called with or without an outer transaction
CREATE OR ALTER PROCEDURE dbo.usp_AddItems @OrderId INT, @Sku VARCHAR(20), @Qty INT
AS
BEGIN
  SET NOCOUNT ON;
  DECLARE @own BIT = IIF(@@TRANCOUNT = 0, 1, 0);
  IF @own = 1 BEGIN TRAN; ELSE SAVE TRAN usp_AddItems_sp;
  BEGIN TRY
    INSERT INTO dbo.OrderItems (OrderId, Sku, Qty) VALUES (@OrderId, @Sku, @Qty);
    IF @own = 1 COMMIT;
  END TRY
  BEGIN CATCH
    IF @own = 1 ROLLBACK;
    ELSE IF XACT_STATE() = 1 ROLLBACK TRAN usp_AddItems_sp;
    THROW;
  END CATCH
END;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ROLLBACK inside the inner procedure when the caller owns the transaction
-- Error 266 (trancount mismatch) shows when the procedure exits with a different @@TRANCOUNT than it entered with.

-- ❌ Wrong: ROLLBACK TRANSACTION sp_name where the name does not exist -> error, and plain
--    ROLLBACK TRANSACTION (no name) inside a savepoint scope rolls back EVERYTHING.

-- ❌ Wrong: assuming a savepoint rollback releases locks or restores IDENTITY values (it does neither for IDENTITY).
-- ❌ Wrong: using savepoints with XACT_ABORT ON and expecting recovery.
```

---

## 🎯 Interview Tip (1 line)
Say: "T-SQL has no true nested transactions. I check @@TRANCOUNT on entry, start a transaction only if I am the outermost caller, otherwise use SAVE TRANSACTION, and I always check XACT_STATE() in CATCH (-1 means uncommittable, must roll back fully). Savepoint rollback does not release locks."

---

## 🔗 Related Questions
→ Q118 (BEGIN TRAN, XACT_ABORT) | Q072 (Procedures with transactions) | Q073 (TRY...CATCH in procedures) | Q132 (TRY...CATCH guide)
