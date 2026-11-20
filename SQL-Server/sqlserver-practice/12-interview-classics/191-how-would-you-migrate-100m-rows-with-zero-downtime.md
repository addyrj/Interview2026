---

# Q191. How Would You Migrate 100M Rows with Zero Downtime
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (MySQL: pt-online-schema-change / gh-ost; PostgreSQL: logical replication + batched backfill)

---

## ❓ Question
Orders (100M rows) must move to a new table with a changed schema (e.g. Total widened, new Status column, clustered on a new key) while the application keeps reading and writing. Describe the approach and show the T-SQL for the batched backfill and the cutover.

---

## 💡 Quick Concept (2 lines only)
Expand/contract: create the new table, capture ongoing changes (dual-write or trigger), backfill old rows in small keyed batches, verify counts/checksums, then cut over with a quick rename in a short transaction. Never one giant INSERT...SELECT.
हिंदी: नई table बनाओ, नए changes capture करो (trigger/dual-write), पुरानी rows छोटे batches में copy करो, verify करो, फिर rename से cutover। एक बड़ा INSERT...SELECT कभी नहीं।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server; behaviour per Microsoft docs. Table sizes below are tiny placeholders.

-- ============================================
-- 1) EXPAND: new table + capture ongoing changes
-- ============================================
CREATE TABLE dbo.Orders_New (
    OrderId    BIGINT        NOT NULL PRIMARY KEY,
    CustomerId INT           NOT NULL,
    OrderDate  DATE          NOT NULL,
    Total      DECIMAL(14,2) NOT NULL,
    Status     VARCHAR(20)   NOT NULL DEFAULT 'completed'
);
GO

CREATE OR ALTER TRIGGER dbo.trg_Orders_Sync ON dbo.Orders
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DELETE n FROM dbo.Orders_New n JOIN deleted d ON d.OrderId = n.OrderId;   -- covers delete + update
    INSERT INTO dbo.Orders_New (OrderId, CustomerId, OrderDate, Total)
    SELECT OrderId, CustomerId, OrderDate, Total FROM inserted;
END;
GO

-- ============================================
-- 2) BACKFILL in small keyed batches (short locks, small log, resumable)
-- ============================================
DECLARE @From BIGINT = 0, @Batch INT = 50000, @MaxId BIGINT, @Rows INT = 1;

SELECT @MaxId = MAX(OrderId) FROM dbo.Orders;

WHILE @From < @MaxId
BEGIN
    INSERT INTO dbo.Orders_New (OrderId, CustomerId, OrderDate, Total)
    SELECT o.OrderId, o.CustomerId, o.OrderDate, o.Total
    FROM dbo.Orders o
    WHERE o.OrderId > @From AND o.OrderId <= @From + @Batch
      AND NOT EXISTS (SELECT 1 FROM dbo.Orders_New n WHERE n.OrderId = o.OrderId);  -- idempotent vs trigger

    SET @From = @From + @Batch;
    WAITFOR DELAY '00:00:00.200';      -- breathe: let log backups / replicas / users catch up
END;
GO

-- ============================================
-- 3) VERIFY before cutover
-- ============================================
SELECT (SELECT COUNT_BIG(*) FROM dbo.Orders)     AS OldRows,
       (SELECT COUNT_BIG(*) FROM dbo.Orders_New) AS NewRows;     -- must match (after traffic pause/lag = 0)
-- Optionally compare SUM(Total) and CHECKSUM_AGG(CHECKSUM(*)) per key range.

-- ============================================
-- 4) CUTOVER: metadata-only, seconds long
-- ============================================
BEGIN TRAN;
    DROP TRIGGER dbo.trg_Orders_Sync;
    EXEC sp_rename 'dbo.Orders',     'Orders_Old';
    EXEC sp_rename 'dbo.Orders_New', 'Orders';
COMMIT;
-- Keep Orders_Old for the rollback window, drop it later (CONTRACT step).
```

```js
// Node.js: deploy order that keeps zero downtime
// 1) deploy app that tolerates BOTH schemas (new column nullable/defaulted)
// 2) run migration (Flyway/dbmate) steps 1-3
// 3) cutover in a quiet minute; 4) deploy cleanup release; 5) drop old table days later
```

---

## 🔍 Why This Works (3 lines max)
Each batch is a short transaction, so locks are brief, the log can truncate between batches, and the job can be stopped and resumed by key. The trigger keeps new writes flowing into the new table, and sp_rename is metadata-only so the final switch takes seconds, not hours.
हिंदी: छोटे batches = छोटे locks और छोटा log। Trigger नए changes sync रखता है। sp_rename सिर्फ metadata बदलता है, इसलिए cutover सेकंडों में होता है।

---

## ⚡ Alternative Solution

```sql
-- Simple column changes: do them online instead of copying
-- Adding a NOT NULL column with a default is metadata-only on modern SQL Server (2012+ Enterprise; broadly in later versions)
ALTER TABLE dbo.Orders ADD Status VARCHAR(20) NOT NULL CONSTRAINT DF_Orders_Status DEFAULT 'completed';

-- Index rebuild without blocking (edition-dependent: Enterprise / Azure SQL):
CREATE INDEX IX_Orders_CustomerId ON dbo.Orders (CustomerId) WITH (ONLINE = ON);

-- Other options: partition SWITCH for bulk moves, Azure Data Factory / bcp for cross-server copies,
-- transactional replication or Azure DMS for cross-database migrations.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: INSERT INTO New SELECT * FROM Old (100M rows in one transaction)
--    -> log explosion, lock escalation to table lock, long blocking, hard rollback
-- ❌ Wrong: batching with OFFSET/ORDER BY instead of a key range -> each batch slower than the last
-- ❌ Wrong: no capture of changes during the copy -> new table is stale at cutover
-- ❌ Wrong: cutover without verification or a rollback path (keep the old table!)
-- ❌ Wrong: ignoring log backups, AG/replica lag and Azure log-rate limits while backfilling
-- ✅ Watch log space and replica lag, throttle batch size, and rehearse on a restored copy first
```

---

## 🎯 Interview Tip (1 line)
Say: "I use expand/contract — create, sync, backfill in keyed batches, verify, rename, then clean up — and I rehearse on a restored backup to measure timing. Every step is reversible, and the app is deployed to tolerate both schemas first." Mention alternatives (partition switch, online index, Azure DMS) to show range.

---

## 🔗 Related Questions
→ Q028 (ALTER TABLE safely) | Q034 (Partitioned tables) | Q145 (Batching large updates/deletes) | Q131 (Transaction log and recovery models) | Q170 (Migrations with Flyway/EF/dbmate) | Q171 (CI/CD for database changes)
