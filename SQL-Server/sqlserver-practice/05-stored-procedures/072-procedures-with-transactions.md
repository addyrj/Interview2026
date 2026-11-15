---

# Q072. Procedures with Transactions
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: START TRANSACTION; PostgreSQL: BEGIN inside procedures with COMMIT allowed from v11)

---

## ❓ Question
Write `dbo.usp_TransferStock` that moves quantity between two warehouses atomically. It must roll back everything on failure, and it must work correctly whether or not the caller already opened a transaction (nested calls). What are `XACT_ABORT`, `@@TRANCOUNT` and `XACT_STATE()` for?

---

## 💡 Quick Concept (2 lines only)
`BEGIN TRAN ... COMMIT` makes a unit of work atomic; `SET XACT_ABORT ON` makes any runtime error abort and roll back the transaction automatically. `@@TRANCOUNT` tells you the nesting depth — a `ROLLBACK` always rolls back ALL levels, so a procedure should only start/commit a transaction if it is the outermost one.
हिंदी: `XACT_ABORT ON` = error पर auto rollback। `@@TRANCOUNT` से पता चलता है caller ने पहले से transaction खोली है या नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.WarehouseStock (
  WarehouseId INT NOT NULL,
  ProductId   INT NOT NULL,
  Qty         INT NOT NULL CONSTRAINT CK_WarehouseStock_Qty CHECK (Qty >= 0),
  CONSTRAINT PK_WarehouseStock PRIMARY KEY (WarehouseId, ProductId)
);
GO

INSERT INTO dbo.WarehouseStock (WarehouseId, ProductId, Qty) VALUES
  (1, 500, 40),
  (2, 500, 10);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_TransferStock
    @FromWarehouse INT,
    @ToWarehouse   INT,
    @ProductId     INT,
    @Qty           INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;                       -- any run-time error -> rollback + abort batch

    DECLARE @startedTran BIT = 0;
    IF @@TRANCOUNT = 0
    BEGIN
        BEGIN TRANSACTION;                   -- only the outermost caller owns the transaction
        SET @startedTran = 1;
    END;

    BEGIN TRY
        UPDATE dbo.WarehouseStock SET Qty = Qty - @Qty
        WHERE WarehouseId = @FromWarehouse AND ProductId = @ProductId;   -- CHECK blocks negative qty

        UPDATE dbo.WarehouseStock SET Qty = Qty + @Qty
        WHERE WarehouseId = @ToWarehouse AND ProductId = @ProductId;

        IF @startedTran = 1 COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @startedTran = 1 AND XACT_STATE() <> 0 ROLLBACK TRANSACTION;
        THROW;                               -- re-raise original error to the caller (SQL Server 2012+)
    END CATCH;
END;
GO

EXEC dbo.usp_TransferStock @FromWarehouse = 1, @ToWarehouse = 2, @ProductId = 500, @Qty = 15;
SELECT WarehouseId, Qty FROM dbo.WarehouseStock ORDER BY WarehouseId;
-- Expected (hand-checked arithmetic: 40-15 and 10+15; not executed on SQL Server):
-- WarehouseId | Qty
-- 1           | 25
-- 2           | 25

EXEC dbo.usp_TransferStock 1, 2, 500, 100;
-- Fails: the CHECK constraint (Qty >= 0) rejects 25 - 100. Both updates are rolled back, error is re-thrown.
-- (Exact error number/text not shown here; it is a CHECK constraint violation per Microsoft docs.)
SELECT WarehouseId, Qty FROM dbo.WarehouseStock ORDER BY WarehouseId;
-- WarehouseId | Qty     <- unchanged
-- 1           | 25
-- 2           | 25
```

Note: transaction/rollback behaviour is not executed on SQL Server; behaviour per Microsoft docs. No equivalent-engine run was possible for TRY/CATCH.

---

## 🔍 Why This Works (3 lines max)
Both UPDATEs sit in one transaction, so either both are committed or neither. `XACT_ABORT ON` guarantees rollback even for errors TRY/CATCH would not catch cleanly, and `@startedTran` keeps nested calls safe because only the owner commits or rolls back.
हिंदी: दोनों UPDATE एक transaction में — या दोनों होंगे या कोई नहीं। सिर्फ outermost procedure commit/rollback करता है।

---

## ⚡ Alternative Solution

```sql
-- Savepoint pattern: nested procedure can undo only its own work
CREATE OR ALTER PROCEDURE dbo.usp_TransferStock_Sp
    @FromWarehouse INT, @ToWarehouse INT, @ProductId INT, @Qty INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT OFF;                      -- savepoint rollback needs the transaction to stay alive
    DECLARE @wasOpen BIT = CASE WHEN @@TRANCOUNT > 0 THEN 1 ELSE 0 END;

    IF @wasOpen = 1 SAVE TRANSACTION TransferSp; ELSE BEGIN TRANSACTION;

    BEGIN TRY
        UPDATE dbo.WarehouseStock SET Qty = Qty - @Qty WHERE WarehouseId = @FromWarehouse AND ProductId = @ProductId;
        UPDATE dbo.WarehouseStock SET Qty = Qty + @Qty WHERE WarehouseId = @ToWarehouse   AND ProductId = @ProductId;
        IF @wasOpen = 0 COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF XACT_STATE() = 1 AND @wasOpen = 1 ROLLBACK TRANSACTION TransferSp;
        ELSE IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;   -- XACT_STATE() = -1: doomed, full rollback only
        THROW;
    END CATCH;
END;
GO
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: no XACT_ABORT, no TRY/CATCH -> a failed statement may leave the transaction OPEN
BEGIN TRANSACTION;
  UPDATE dbo.WarehouseStock SET Qty = Qty - 100 WHERE WarehouseId = 1 AND ProductId = 500;  -- fails
  UPDATE dbo.WarehouseStock SET Qty = Qty + 100 WHERE WarehouseId = 2 AND ProductId = 500;  -- still runs!
COMMIT;
-- Statement-level error does not abort the batch by default -> half-applied transfer, open locks.

-- ❌ Wrong: ROLLBACK in a nested procedure when the caller owns the transaction
--    -> rolls back ALL levels, @@TRANCOUNT mismatch error (procedure exits with different count).
-- ❌ Wrong: COMMIT inside CATCH without checking XACT_STATE() (-1 = uncommittable).
```

---

## 🎯 Interview Tip (1 line)
Say: "Every write procedure of mine uses `SET XACT_ABORT ON`, owns a transaction only when `@@TRANCOUNT = 0`, checks `XACT_STATE()` in CATCH and re-throws with `THROW` — and I keep transactions short so locks are released quickly." Add that the Node.js layer should not hold a transaction open across HTTP calls.

---

## 🔗 Related Questions
→ Q073 (TRY...CATCH inside procedures) | Q074 (SET NOCOUNT ON) | Q084 (Upsert procedure)
