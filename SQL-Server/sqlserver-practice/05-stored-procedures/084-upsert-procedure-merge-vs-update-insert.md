---

# Q084. Upsert Procedure (MERGE vs UPDATE/INSERT)
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: INSERT ... ON DUPLICATE KEY UPDATE; PostgreSQL: INSERT ... ON CONFLICT DO UPDATE)

---

## ❓ Question
Write `dbo.usp_UpsertInventory @ProductId, @Name, @QtyDelta` that adds stock if the product exists, otherwise inserts it — correctly under concurrent calls from many Node.js workers. Compare `MERGE` with the UPDATE-then-INSERT pattern. Which would you pick and why?

---

## 💡 Quick Concept (2 lines only)
SQL Server has no `ON CONFLICT`. Either use `MERGE` (one statement, but needs `HOLDLOCK` and has a history of bugs) or `UPDATE ... ; IF @@ROWCOUNT = 0 INSERT ...` inside a transaction with `UPDLOCK, SERIALIZABLE` hints to prevent two sessions inserting the same key.
हिंदी: SQL Server में `ON CONFLICT` नहीं है। `MERGE` + `HOLDLOCK` या UPDATE फिर `@@ROWCOUNT=0` पर INSERT (locking hints के साथ)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Inventory (
  ProductId INT          NOT NULL PRIMARY KEY,
  Name      VARCHAR(100) NOT NULL,
  Qty       INT          NOT NULL
);
INSERT INTO dbo.Inventory (ProductId, Name, Qty) VALUES (1, 'Keyboard', 10), (2, 'Mouse', 5);
GO

-- ============================================
-- SOLUTION A: UPDATE then INSERT (my default)
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_UpsertInventory
    @ProductId INT,
    @Name      VARCHAR(100),
    @QtyDelta  INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRANSACTION;

        UPDATE dbo.Inventory WITH (UPDLOCK, SERIALIZABLE)       -- locks the key RANGE, so a concurrent insert waits
        SET    Qty = Qty + @QtyDelta
        WHERE  ProductId = @ProductId;

        IF @@ROWCOUNT = 0
            INSERT INTO dbo.Inventory (ProductId, Name, Qty)
            VALUES (@ProductId, @Name, @QtyDelta);

    COMMIT TRANSACTION;
END;
GO

EXEC dbo.usp_UpsertInventory @ProductId = 2, @Name = 'Mouse',   @QtyDelta = 7;    -- exists -> Qty 5 + 7
EXEC dbo.usp_UpsertInventory @ProductId = 3, @Name = 'Monitor', @QtyDelta = 20;   -- new -> insert
SELECT ProductId, Name, Qty FROM dbo.Inventory ORDER BY ProductId;
-- Expected (same logic run as UPDATE + conditional INSERT on SQLite; not executed on SQL Server,
-- the locking hints have no equivalent there):
-- ProductId | Name     | Qty
-- 1         | Keyboard | 10
-- 2         | Mouse    | 12
-- 3         | Monitor  | 20
```

---

## 🔍 Why This Works (3 lines max)
UPDATE touches the row if it exists; `@@ROWCOUNT = 0` tells us it did not, so we INSERT. `UPDLOCK, SERIALIZABLE` takes a range lock on the key even when no row exists, so two concurrent callers cannot both decide "missing" and both insert (which would raise a primary key violation).
हिंदी: पहले UPDATE, 0 rows हुईं तो INSERT। Range lock की वजह से दो sessions एक साथ same key insert नहीं कर पाते।

---

## ⚡ Alternative Solution

```sql
-- SOLUTION B: MERGE (needs HOLDLOCK to be safe under concurrency)
CREATE OR ALTER PROCEDURE dbo.usp_UpsertInventory_Merge
    @ProductId INT, @Name VARCHAR(100), @QtyDelta INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    MERGE dbo.Inventory WITH (HOLDLOCK) AS tgt
    USING (SELECT @ProductId AS ProductId, @Name AS Name, @QtyDelta AS Qty) AS src
          ON tgt.ProductId = src.ProductId
    WHEN MATCHED THEN
        UPDATE SET Qty = tgt.Qty + src.Qty
    WHEN NOT MATCHED BY TARGET THEN
        INSERT (ProductId, Name, Qty) VALUES (src.ProductId, src.Name, src.Qty)
    OUTPUT $action AS Action, inserted.ProductId, inserted.Qty;     -- tell the caller what happened
END;                                                                -- MERGE must end with a semicolon
GO
-- OUTPUT / MERGE behaviour: not executed on SQL Server; per Microsoft docs.
-- MERGE is fine for set-based sync (many rows from a staging table), but many teams avoid it for single-row
-- upserts because of documented bugs/edge cases (concurrency without HOLDLOCK, triggers, filtered indexes).
-- Review the current list of known MERGE issues before using it in a critical path.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Race condition (check-then-act):
IF EXISTS (SELECT 1 FROM dbo.Inventory WHERE ProductId = @ProductId)
    UPDATE dbo.Inventory SET Qty = Qty + @QtyDelta WHERE ProductId = @ProductId;
ELSE
    INSERT INTO dbo.Inventory VALUES (@ProductId, @Name, @QtyDelta);
-- Two sessions both see "not exists" -> second INSERT fails with a primary key violation.

-- ❌ MERGE without HOLDLOCK (or SERIALIZABLE) under concurrent load -> same duplicate-key race.
-- ❌ Forgetting the transaction: UPDATE lock is released at statement end, so the range lock protects nothing.
-- ❌ Using @@IDENTITY/@@ROWCOUNT after another statement -- @@ROWCOUNT must be read immediately after the UPDATE.
-- ❌ Catching error 2627 (PK violation) and retrying is also a valid pattern, but design it deliberately.
```

---

## 🎯 Interview Tip (1 line)
Say: "For single-row upserts I use UPDATE with UPDLOCK/SERIALIZABLE then INSERT if `@@ROWCOUNT = 0` inside a transaction; I use MERGE with HOLDLOCK for set-based loads from staging and test it carefully because of its known quirks." Mention the Postgres/MySQL equivalents (`ON CONFLICT`, `ON DUPLICATE KEY`) to show breadth.

---

## 🔗 Related Questions
→ Q011 (MERGE statement and its gotchas) | Q072 (Procedures with transactions) | Q010 (INSERT, UPDATE, DELETE and OUTPUT) | Q086 (Bulk insert and batching procedure)
