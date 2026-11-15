---

# Q100. Cursors vs Set-Based Thinking
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (cursor syntax is T-SQL specific; MySQL/PostgreSQL cursors live inside procedures/PL-pgSQL)

---

## ❓ Question
Assign a loyalty `Tier` to every customer: Gold if total order amount >= 1000, Silver if >= 500, else Bronze. First write it with a CURSOR (row-by-row), then rewrite it as one set-based UPDATE. Explain why the second is preferred and when a cursor is still acceptable.

---

## 💡 Quick Concept (2 lines only)
A cursor processes one row per FETCH (RBAR - "row by agonizing row"), paying per-row overhead and blocking the optimizer from seeing the whole job. A set-based statement tells SQL Server WHAT you want, so it can pick one plan (joins, parallelism, batch mode).
हिंदी: Cursor = एक-एक row पर loop, slow। Set-based = एक statement में सारी rows, optimizer अपना best plan चुनता है।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Expected output derived from an
-- equivalent UPDATE ... CASE query on SQLite; not executed on SQL Server.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Customers (
  CustomerId INT PRIMARY KEY,
  Name       VARCHAR(50) NOT NULL,
  Tier       VARCHAR(10) NOT NULL DEFAULT 'Bronze'
);
CREATE TABLE Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL REFERENCES Customers(CustomerId),
  Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO Customers (CustomerId, Name) VALUES (1,'Asha'),(2,'Bilal'),(3,'Chen'),(4,'Divya'),(5,'Emeka');
INSERT INTO Orders VALUES (1,1,600),(2,1,500),(3,2,300),(4,2,250),(5,3,100),(6,4,1200),(7,4,50);
GO

-- ============================================
-- SOLUTION A: CURSOR (works, but slow at scale)
-- ============================================
DECLARE @id INT, @total DECIMAL(12,2);
DECLARE cur CURSOR LOCAL FAST_FORWARD FOR
  SELECT c.CustomerId, ISNULL(SUM(o.Amount), 0)
  FROM Customers c LEFT JOIN Orders o ON o.CustomerId = c.CustomerId
  GROUP BY c.CustomerId;
OPEN cur;
FETCH NEXT FROM cur INTO @id, @total;
WHILE @@FETCH_STATUS = 0
BEGIN
  UPDATE Customers
  SET Tier = CASE WHEN @total >= 1000 THEN 'Gold' WHEN @total >= 500 THEN 'Silver' ELSE 'Bronze' END
  WHERE CustomerId = @id;                      -- one UPDATE per customer
  FETCH NEXT FROM cur INTO @id, @total;
END
CLOSE cur;
DEALLOCATE cur;
GO

-- ============================================
-- SOLUTION B: SET-BASED (one statement)
-- ============================================
UPDATE c
SET c.Tier = CASE WHEN t.Total >= 1000 THEN 'Gold'
                  WHEN t.Total >= 500  THEN 'Silver'
                  ELSE 'Bronze' END
FROM Customers c
LEFT JOIN (SELECT CustomerId, SUM(Amount) AS Total FROM Orders GROUP BY CustomerId) t
       ON t.CustomerId = c.CustomerId;

SELECT CustomerId, Name, Tier FROM Customers ORDER BY CustomerId;

-- Output (same for A and B):
-- CustomerId | Name   | Tier
-- 1          | Asha   | Gold      (1100)
-- 2          | Bilal  | Silver    (550)
-- 3          | Chen   | Bronze    (100)
-- 4          | Divya  | Gold      (1250)
-- 5          | Emeka  | Bronze    (no orders)
```

---

## 🔍 Why This Works (3 lines max)
The set-based UPDATE computes all totals in one aggregate pass and updates matching rows in one operation, one plan and one log batch instead of N statements and N round trips inside the loop. The LEFT JOIN keeps customers without orders (Emeka) so they still get the default tier. The cursor gives the same answer but costs per-row CPU, locks and log writes.
हिंदी: Set-based में एक plan, एक pass। Cursor में हर row पर अलग UPDATE। LEFT JOIN से बिना orders वाले customers भी आ जाते हैं।

---

## ⚡ Alternative Solution

```sql
-- Cursor IS acceptable for: running an admin task per database/table, calling a stored
-- procedure per row (e.g. sp_rename, backup per DB), or genuinely order-dependent procedural logic.
DECLARE @sql NVARCHAR(400);
DECLARE c2 CURSOR LOCAL FAST_FORWARD FOR
  SELECT N'ALTER INDEX ALL ON ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N' REBUILD;'
  FROM sys.tables;
OPEN c2; FETCH NEXT FROM c2 INTO @sql;
WHILE @@FETCH_STATUS = 0 BEGIN EXEC sys.sp_executesql @sql; FETCH NEXT FROM c2 INTO @sql; END
CLOSE c2; DEALLOCATE c2;
-- For running totals, use SUM() OVER (ORDER BY ...) instead of a cursor.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: default (updatable, global, dynamic-ish) cursor - heavy and slow
DECLARE cur CURSOR FOR SELECT CustomerId FROM Customers;
-- ✅ Use LOCAL FAST_FORWARD (read-only, forward-only) when you must loop

-- ❌ Wrong: forgetting CLOSE/DEALLOCATE -> cursor leaks until the session ends (GLOBAL cursors persist)
-- ❌ Wrong: replacing a cursor with a WHILE loop over a temp table and calling it "set-based" - it is the same RBAR
-- ❌ Wrong: scalar UDF inside UPDATE to "avoid the cursor" - still row-by-row internally (see Q088)
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I think in sets first. A cursor means N round trips of the engine's per-statement overhead and it hides the work from the optimizer. I'll use one only for admin loops or when each row triggers a procedure that cannot be expressed as a set - and then LOCAL FAST_FORWARD. In migrations I batch large UPDATEs in chunks of 5-10k rows rather than looping row by row." Mention the numbers you saw: always measure with SET STATISTICS TIME rather than quoting a magic speed-up factor.

---

## 🔗 Related Questions
→ Q015 (Control flow - WHILE) | Q048 (Running totals) | Q088 (Scalar UDF cost) | Q145 (Batching large updates/deletes)
