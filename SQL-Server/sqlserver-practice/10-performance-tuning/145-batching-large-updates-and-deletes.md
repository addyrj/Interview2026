---

# Q145. Batching Large Updates and Deletes
# Category: Performance Tuning
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: DELETE ... LIMIT n | PostgreSQL: no LIMIT on DELETE, use ctid/CTE). Loop behaviour not executed on SQL Server.

---

## ❓ Question
Delete 50 million old `Orders` rows with Status = 'Pending'. One big DELETE blocks everyone and balloons the log. Write a batched delete loop and explain the lock escalation and log reasons.

---

## 💡 Quick Concept (2 lines only)
Delete in small chunks (1k-5k rows) in a WHILE loop so each transaction is short: locks stay row/page level (escalation to a table lock happens around 5,000 locks per statement), the log can truncate between batches, and others can get in.
हिंदी: एक बड़ा DELETE = बड़ा lock + बड़ा log। छोटे batches में loop चलाओ, हर batch अपना छोटा transaction।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  OrderDate  DATE NOT NULL
);

INSERT INTO Orders VALUES
  (1,1,'Pending',10,'2024-01-01'), (2,1,'Pending',20,'2024-01-02'),
  (3,2,'Shipped',30,'2024-01-03'), (4,1,'Pending',40,'2024-01-04'),
  (5,3,'Pending',50,'2024-01-05'), (6,1,'Pending',60,'2024-01-06'),
  (7,2,'Shipped',70,'2024-01-07'), (8,1,'Pending',80,'2024-01-08'),
  (9,4,'Pending',90,'2024-01-09'), (10,1,'Pending',100,'2024-01-10');

-- ============================================
-- BATCHED DELETE (batch size 3 only for the demo; use 1000-5000 in production)
-- ============================================
DECLARE @BatchSize INT = 3;
DECLARE @Rows INT = 1;

WHILE @Rows > 0
BEGIN
    DELETE TOP (@BatchSize)
    FROM Orders
    WHERE Status = 'Pending';

    SET @Rows = @@ROWCOUNT;          -- capture immediately

    PRINT CONCAT('Deleted: ', @Rows);
    WAITFOR DELAY '00:00:00.100';    -- breathing room for other sessions / log backups
END;

-- EXPECTED OUTPUT (batch sizes derived from equivalent loop on SQLite; not executed on SQL Server):
-- Deleted: 3
-- Deleted: 3
-- Deleted: 2
-- Deleted: 0
-- Remaining rows: OrderId 3 and 7 (both 'Shipped')
```

---

## 🔍 Why This Works (3 lines max)
Each DELETE TOP (n) is its own auto-commit transaction, so locks are released and log space becomes reusable after the next log backup (FULL) or checkpoint (SIMPLE). The loop ends when a batch affects 0 rows.
हिंदी: हर batch अलग transaction है -> lock जल्दी छूटता है, log reuse हो पाता है। 0 rows पर loop रुकता है।

---

## ⚡ Alternative Solution

```sql
-- Delete by key range using the clustered index (predictable, no repeated scans of Pending rows)
DECLARE @MinId INT = 0, @MaxId INT = 10, @Step INT = 3;
WHILE @MinId < @MaxId
BEGIN
    DELETE FROM Orders
    WHERE OrderId > @MinId AND OrderId <= @MinId + @Step AND Status = 'Pending';
    SET @MinId += @Step;
END;

-- If you delete most of the table: copy the keepers to a new table and swap, or
-- partition and TRUNCATE the old partition (Q150). Minimal logging is not available for DELETE.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ DELETE TOP (n) without a supporting index on Status re-scans the table
--    every iteration -> O(n^2). Index the filter (e.g. filtered index WHERE Status = 'Pending').
-- ❌ Wrapping the whole loop in BEGIN TRAN ... COMMIT: one giant transaction again
-- ❌ Reading @@ROWCOUNT after PRINT/other statement: it is reset by any statement
-- ❌ Ignoring log backups during a huge purge in FULL recovery: log fills the disk
-- ❌ Deleting with cascading FKs / triggers without checking their per-batch cost
```

---

## 🎯 Interview Tip (1 line)
Say: "I batch with TOP (n) or key ranges, 1k-5k rows, keep each batch its own transaction, index the filter, monitor log usage and blocking, and run off-peak. For purging most of a table I prefer partition switch/truncate."

---

## 🔗 Related Questions
→ Q012 (TRUNCATE vs DELETE vs DROP) | Q122 (Locks) | Q131 (Transaction log and recovery models) | Q150 (Partitioning for performance)
