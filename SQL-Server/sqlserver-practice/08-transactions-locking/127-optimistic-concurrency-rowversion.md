
---

# Q127. Optimistic Concurrency with rowversion
# Category: TRANSACTIONS + LOCKING
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL/PostgreSQL have no rowversion; use an integer `version` column or PostgreSQL `xmin`)

---

## ❓ Question
Two users open the same Product in an admin screen and both press Save. The second save must NOT silently overwrite the first. Implement optimistic concurrency with a `rowversion` column and show the UPDATE, the stored procedure, and the Node.js `mssql` call that returns HTTP 409 on conflict.

---

## 💡 Quick Concept (2 lines only)
`rowversion` is an 8-byte value SQL Server auto-changes on every INSERT/UPDATE of the row. Read it with the row, send it back in `WHERE ... AND RowVer = @RowVer`; if `@@ROWCOUNT = 0` someone else changed it.
हिंदी: rowversion हर update पर अपने-आप बदलता है। Update में WHERE RowVer = पुराना मान लगाओ; 0 rows affected = किसी और ने पहले बदल दिया।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Products (
  ProductId INT IDENTITY(1,1) PRIMARY KEY,
  Name      NVARCHAR(100) NOT NULL,
  Price     DECIMAL(10,2) NOT NULL,
  RowVer    ROWVERSION                -- auto-maintained, never insert/update it
);

INSERT INTO dbo.Products (Name, Price)
VALUES (N'Keyboard', 49.99), (N'Mouse', 19.99);
GO

-- ============================================
-- SOLUTION: stored procedure with version check
-- ============================================
CREATE OR ALTER PROCEDURE dbo.usp_UpdateProductPrice   -- CREATE OR ALTER: SQL Server 2016 SP1+
  @ProductId INT,
  @Price     DECIMAL(10,2),
  @RowVer    BINARY(8)
AS
BEGIN
  SET NOCOUNT ON;

  UPDATE dbo.Products
  SET    Price = @Price
  WHERE  ProductId = @ProductId
    AND  RowVer    = @RowVer;          -- the optimistic check

  IF @@ROWCOUNT = 0
  BEGIN
    -- row deleted OR changed by someone else
    THROW 50001, 'Concurrency conflict: the product was modified by another user.', 1;
  END

  SELECT ProductId, Name, Price, RowVer FROM dbo.Products WHERE ProductId = @ProductId;
END;
GO

-- Session A and B both read the row first:
DECLARE @v BINARY(8) = (SELECT RowVer FROM dbo.Products WHERE ProductId = 1);
EXEC dbo.usp_UpdateProductPrice @ProductId = 1, @Price = 59.99, @RowVer = @v;  -- A wins
EXEC dbo.usp_UpdateProductPrice @ProductId = 1, @Price = 39.99, @RowVer = @v;  -- B uses stale @v -> THROW 50001
```

```js
// Node.js (mssql) - map conflict to HTTP 409
const r = await pool.request()
  .input('ProductId', sql.Int, id)
  .input('Price', sql.Decimal(10, 2), price)
  .input('RowVer', sql.VarBinary(8), Buffer.from(rowVerHex, 'hex'))  // rowversion comes back as Buffer
  .execute('dbo.usp_UpdateProductPrice')
  .catch(e => { if (e.number === 50001) return null; throw e; });
if (!r) return res.status(409).json({ error: 'Modified by another user, reload' });
```

```sql
-- EXPECTED OUTPUT (rowversion values are opaque binaries, so only the logic is shown)
-- Result derived from equivalent query on SQLite using an INTEGER version column; not executed on SQL Server.
-- Equivalent: UPDATE ... SET Price=59.99, RowVer=RowVer+1 WHERE ProductId=1 AND RowVer=1
--   Session A: 1 row affected  -> row becomes (1, 'Keyboard', 59.99, RowVer=2)
--   Session B (stale RowVer=1): 0 rows affected -> app raises conflict
-- On SQL Server, B gets error 50001 from the THROW above (custom number >= 50000).
```

---

## 🔍 Why This Works (3 lines max)
No locks are held while the user thinks; the check happens atomically inside the UPDATE, so lost updates are impossible. Only the first writer matches the old RowVer; the second matches zero rows.
हिंदी: Lock नहीं रखते, बस UPDATE के अंदर ही version check होता है। पहला writer जीतता है, दूसरे का WHERE match नहीं करता।

---

## ⚡ Alternative Solution

```sql
-- Inline, no procedure: use OUTPUT to detect success without @@ROWCOUNT
UPDATE dbo.Products
SET    Price = @Price
OUTPUT inserted.RowVer AS NewRowVer
WHERE  ProductId = @ProductId AND RowVer = @RowVer;
-- no row returned => conflict

-- Pessimistic alternative (holds locks, bad for web UIs):
-- SELECT ... FROM dbo.Products WITH (UPDLOCK, HOLDLOCK) WHERE ProductId = @ProductId;
-- Manual version column (portable to MySQL/PG): Version INT NOT NULL DEFAULT 1, SET Version = Version + 1
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: last-writer-wins, no version check
UPDATE dbo.Products SET Price = @Price WHERE ProductId = @ProductId;

-- ❌ Wrong: comparing rowversion with = in the app after converting to string wrongly,
--    or trying to INSERT/UPDATE the rowversion column (error: cannot update a timestamp column).

-- ❌ Wrong: checking the version in a separate SELECT then updating (race window between the two statements)
-- ✅ Put the version predicate IN the UPDATE and test @@ROWCOUNT immediately
--    (any statement between UPDATE and @@ROWCOUNT, even PRINT/IF, can reset it).
```

---

## 🎯 Interview Tip (1 line)
Say: "I use optimistic concurrency with rowversion for web apps: no long locks, the UPDATE carries the version, and 0 rows maps to HTTP 409. rowversion is database-wide unique and monotonic, not a datetime, and the deprecated `timestamp` keyword is the same type. For hot rows with high conflict I would reconsider and use UPDLOCK."

---

## 🔗 Related Questions
→ Q033 (Sparse columns, rowversion) | Q121 (SNAPSHOT isolation) | Q125 (Lock hints) | Q020 (@@ROWCOUNT)
