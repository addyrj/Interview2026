---

# Q086. Bulk Insert and Batching Procedure
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: DELETE ... LIMIT n; PostgreSQL: DELETE ... WHERE ctid IN (SELECT ... LIMIT n) or a CTE)

---

## ❓ Question
You must archive and purge old orders (millions of rows) without blocking the system or blowing up the transaction log. Write a procedure that deletes orders older than a cutoff date in batches of N rows, one short transaction per batch, and returns the total deleted. Also: how do you bulk-load rows from Node.js efficiently?

---

## 💡 Quick Concept (2 lines only)
One giant DELETE holds locks for the whole run, can escalate to a table lock and grows the log. Loop with `DELETE TOP (@BatchSize)` until `@@ROWCOUNT = 0`, committing each batch.
हिंदी: एक बड़ा DELETE = lock escalation + log बड़ा। छोटे batches में loop करो, हर batch अलग transaction, `@@ROWCOUNT = 0` पर रुको।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1,1) PRIMARY KEY,
  CustomerId INT NOT NULL,
  OrderDate  DATE NOT NULL
);
CREATE INDEX IX_Orders_OrderDate ON dbo.Orders (OrderDate);   -- batch seeks by date

INSERT INTO dbo.Orders (CustomerId, OrderDate) VALUES
  (101,'2022-02-15'),(102,'2022-03-15'),(100,'2022-04-15'),(101,'2022-05-15'),
  (102,'2022-06-15'),(100,'2022-07-15'),(101,'2022-08-15'),
  (102,'2024-05-01'),(100,'2024-05-01'),(101,'2024-05-01');
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_PurgeOldOrders
  @CutoffDate DATE,
  @BatchSize  INT = 5000,
  @TotalDeleted INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;
  SET XACT_ABORT ON;

  DECLARE @Rows INT = 1;
  SET @TotalDeleted = 0;

  WHILE @Rows > 0
  BEGIN
    BEGIN TRANSACTION;

    DELETE TOP (@BatchSize) FROM dbo.Orders
    WHERE OrderDate < @CutoffDate;

    SET @Rows = @@ROWCOUNT;                 -- capture immediately
    SET @TotalDeleted = @TotalDeleted + @Rows;

    COMMIT TRANSACTION;                     -- short transaction per batch

    IF @Rows > 0 WAITFOR DELAY '00:00:00.100';  -- optional breathing room for log/replicas
  END
END;
GO

DECLARE @n INT;
EXEC dbo.usp_PurgeOldOrders @CutoffDate = '2023-01-01', @BatchSize = 3, @TotalDeleted = @n OUTPUT;
SELECT @n AS TotalDeleted;
SELECT COUNT(*) AS remaining FROM dbo.Orders;

-- EXPECTED OUTPUT (batch loop reproduced on SQLite with DELETE ... WHERE id IN (SELECT ... LIMIT 3);
-- not executed on SQL Server):
-- batches deleted: 3, 3, 1, then 0 -> loop stops
-- TotalDeleted
-- 7
-- remaining
-- 3
```

Bulk load from Node.js (`mssql`, uses the TDS bulk-copy protocol, far faster than looped INSERTs):

```javascript
const table = new sql.Table('dbo.Orders');
table.create = false;
table.columns.add('CustomerId', sql.Int, { nullable: false });
table.columns.add('OrderDate', sql.Date, { nullable: false });
rows.forEach(r => table.rows.add(r.customerId, r.orderDate));
await pool.request().bulk(table);          // chunk to e.g. 10k-50k rows per call
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
Each batch is a short transaction, so locks stay below the escalation threshold (about 5,000 locks per statement) and the log can be reused between batches in SIMPLE recovery or after log backups in FULL. The date index lets each iteration seek instead of scanning. `@@ROWCOUNT = 0` ends the loop naturally.
हिंदी: Chhote transactions = कम locks, log reuse हो पाता है। Date पर index ज़रूरी है वरना हर batch scan करेगा।

---

## ⚡ Alternative Solution

```sql
-- Partition switching / sliding window (Enterprise-era feature, any edition since 2016 SP1):
-- ALTER TABLE dbo.Orders SWITCH PARTITION 1 TO dbo.Orders_Archive PARTITION 1;
-- Metadata-only, near-instant for purging an entire old partition.
-- Not executed here; behaviour per Microsoft docs.

-- Bulk INSERT from a file (server must be able to read the path):
BULK INSERT dbo.Orders FROM 'C:\load\orders.csv'
WITH (FORMAT = 'CSV', FIRSTROW = 2, BATCHSIZE = 50000, TABLOCK);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: one giant statement
DELETE FROM dbo.Orders WHERE OrderDate < '2023-01-01';   -- lock escalation, huge log, long blocking

-- ❌ Wrong: no ORDER/index -> each batch scans the table; or batch loop with
--    an outer transaction wrapped around WHILE (defeats batching, log cannot clear).
-- ❌ Wrong: using @@ROWCOUNT after COMMIT/IF -> value reset. Capture it right after the DELETE.
-- ✅ Batch size 1k-10k, index on the filter column, transaction INSIDE the loop.
```

---

## 🎯 Interview Tip (1 line)
Say: "I batch deletes with TOP and a short transaction per batch, index the predicate, watch log growth and replica lag, and tune batch size so it stays under lock escalation. For recurring purges I prefer partition switching, and for loads from Node I use the mssql bulk API or a table-valued parameter rather than row-by-row INSERTs."

---

## 🔗 Related Questions
→ Q076 (Table-valued parameters) | Q034 (Partitioned tables) | Q118 (BEGIN TRAN, XACT_ABORT) | Q122 (Locks) | Q191 (Migrate 100M rows)
