---

# Q094. AFTER Triggers
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (statement-level triggers; MySQL/SQLite triggers are FOR EACH ROW with OLD/NEW; PostgreSQL supports both levels)

---

## ❓ Question
Whenever an order's Status changes, record the old and new status in OrderStatusHistory. The trigger must work correctly when one UPDATE changes many rows.

---

## 💡 Quick Concept (2 lines only)
An AFTER (FOR) trigger fires once per statement, after the data change and constraint checks, inside the same transaction. It sees all affected rows at once in the `inserted`/`deleted` pseudo-tables, so write it set-based.
हिंदी: AFTER trigger statement के बाद एक बार चलता है, उसी transaction में। सारी बदली rows `inserted`/`deleted` में मिलती हैं, इसलिए set-based लिखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1,1) PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);

CREATE TABLE dbo.OrderStatusHistory (
  HistoryId INT IDENTITY(1,1) PRIMARY KEY,
  OrderId   INT NOT NULL,
  OldStatus VARCHAR(20) NOT NULL,
  NewStatus VARCHAR(20) NOT NULL,
  ChangedAt DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME()
);

INSERT INTO dbo.Orders (CustomerId, Status, Amount) VALUES
  (10, 'Pending', 100), (10, 'Pending', 200), (11, 'Shipped', 300);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER TRIGGER dbo.trg_Orders_StatusChange
ON dbo.Orders
AFTER UPDATE
AS
BEGIN
  SET NOCOUNT ON;
  IF NOT UPDATE(Status) RETURN;          -- cheap exit when the column was not in the SET list

  INSERT INTO dbo.OrderStatusHistory (OrderId, OldStatus, NewStatus)
  SELECT i.OrderId, d.Status, i.Status
  FROM inserted i
  JOIN deleted  d ON d.OrderId = i.OrderId
  WHERE d.Status <> i.Status;            -- only real changes
END;
GO

UPDATE dbo.Orders SET Status = 'Shipped' WHERE Status = 'Pending';   -- 2 rows, ONE trigger run
UPDATE dbo.Orders SET Status = 'Shipped' WHERE OrderId = 3;          -- no change -> no history row

SELECT HistoryId, OrderId, OldStatus, NewStatus FROM dbo.OrderStatusHistory;

-- EXPECTED OUTPUT (derived from an equivalent row-level AFTER UPDATE trigger on SQLite; in SQL
-- Server the trigger runs once with both rows in inserted/deleted, result is the same;
-- not executed on SQL Server):
-- HistoryId | OrderId | OldStatus | NewStatus
-- 1         | 1       | Pending   | Shipped
-- 2         | 2       | Pending   | Shipped
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The trigger joins `inserted` (new values) with `deleted` (old values) on the key, so one INSERT...SELECT handles any number of rows. The WHERE filter skips rows whose status did not change. Because it runs inside the original transaction, a ROLLBACK also undoes the history rows.
हिंदी: `inserted` (नए values) और `deleted` (पुराने values) को key पर join करो। एक INSERT...SELECT कितनी भी rows संभाल लेता है। Rollback पर history भी रद्द।

---

## ⚡ Alternative Solution

```sql
-- OUTPUT clause in the stored procedure that performs the update (explicit, no hidden logic):
UPDATE dbo.Orders
SET Status = @NewStatus
OUTPUT inserted.OrderId, deleted.Status, inserted.Status
INTO dbo.OrderStatusHistory (OrderId, OldStatus, NewStatus)
WHERE OrderId = @OrderId AND Status <> @NewStatus;
-- Not executed on SQL Server; behaviour per Microsoft docs. Or use a system-versioned temporal table.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming the trigger sees one row
DECLARE @id INT, @new VARCHAR(20);
SELECT @id = OrderId, @new = Status FROM inserted;   -- multi-row UPDATE: only one arbitrary row is captured
INSERT INTO dbo.OrderStatusHistory (OrderId, OldStatus, NewStatus) VALUES (@id, '?', @new);

-- ❌ Wrong: forgetting SET NOCOUNT ON -> extra "rows affected" messages confuse some clients/ORMs.
-- ❌ Wrong: slow logic or calls to other servers inside a trigger -> the user's transaction waits.
-- ✅ Set-based, minimal work, no PRINT/side effects.
```

---

## 🎯 Interview Tip (1 line)
Say: "SQL Server triggers are per statement, not per row, so I always write them set-based using inserted and deleted, guard with UPDATE(column) and a real-change filter, SET NOCOUNT ON, and keep them tiny because they run inside the caller's transaction. Where possible I prefer explicit OUTPUT or temporal tables."

---

## 🔗 Related Questions
→ Q095 (INSTEAD OF triggers) | Q096 (inserted and deleted tables) | Q097 (Audit trigger pattern) | Q098 (When NOT to use triggers) | Q030 (Temporal tables)
