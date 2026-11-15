---

# Q116. Deadlock Graphs and Index Fixes
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL logs deadlocks in the server log; MySQL: SHOW ENGINE INNODB STATUS)

---

## ❓ Question
You see error 1205 (deadlock victim) on `UPDATE Orders ... WHERE CustomerId = @id`. How do you capture the deadlock graph and how can a missing index cause or worsen the deadlock?

---

## 💡 Quick Concept (2 lines only)
A deadlock graph shows processes, the resources (key/page/RID locks) they hold and wait for, and which one was chosen as the victim. A missing index makes statements scan and lock many rows, widening the lock footprint and making cycles far more likely.
हिंदी: Deadlock graph = कौन किस resource पर बैठा है और किसका इंतज़ार कर रहा है। Index न हो तो scan में बहुत rows lock होते हैं, इसलिए deadlock ज़्यादा होते हैं।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server; behaviour per Microsoft docs. No graph XML is shown because it cannot be generated here.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
    OrderId     INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId  INT           NOT NULL,
    Status      VARCHAR(20)   NOT NULL,
    Amount      DECIMAL(10,2) NOT NULL
);

CREATE TABLE dbo.OrderItems (
    ItemId   INT IDENTITY(1,1) PRIMARY KEY,
    OrderId  INT NOT NULL,
    Sku      VARCHAR(30) NOT NULL,
    Qty      INT NOT NULL
);
GO

-- ============================================
-- STEP 1: CAPTURE THE GRAPH
-- ============================================

-- Option A: the built-in system_health Extended Events session already records xml_deadlock_report
SELECT CAST(xet.target_data AS XML) AS target_xml
FROM sys.dm_xe_session_targets AS xet
JOIN sys.dm_xe_sessions AS xe ON xe.address = xet.event_session_address
WHERE xe.name = 'system_health' AND xet.target_name = 'ring_buffer';
-- Open the xml_deadlock_report event; save the <deadlock> XML as .xdl and open in SSMS to see the graph.

-- Option B (older, instance-wide): trace flag 1222 writes the report to the error log
DBCC TRACEON (1222, -1);

-- Azure SQL Database: use the portal / Extended Events (database-scoped session); trace flags are not available.

-- ============================================
-- STEP 2: READ IT
-- ============================================
-- <victim-list>          which process was killed (error 1205)
-- <process-list>         the statements (inputbuf) and isolation level of each session
-- <resource-list>        keylock / pagelock / ridlock objects, lock modes (X, U, S), owners and waiters
-- Look for: a RID/PAGE lock (heap or scan), or two sessions taking the same objects in opposite order.

-- ============================================
-- STEP 3: FIX WITH AN INDEX
-- ============================================

-- Without an index on CustomerId this statement scans the table and takes locks on rows it only inspects:
UPDATE dbo.Orders SET Status = 'Archived' WHERE CustomerId = 42;

CREATE INDEX IX_Orders_CustomerId ON dbo.Orders (CustomerId);
-- Now it seeks only the matching rows: smaller lock footprint, shorter lock duration, fewer cycles.

-- A foreign-key lookup without an index has the same effect:
CREATE INDEX IX_OrderItems_OrderId ON dbo.OrderItems (OrderId);
-- (SQL Server does not auto-index foreign key columns.)
```

---

## 🔍 Why This Works (3 lines max)
Locks are taken on every row the engine reads while searching, not only the rows it changes, so scans lock more and for longer. An index seek touches few keys, so two sessions are much less likely to hold what the other needs. The graph tells you which statement and which index to fix.
हिंदी: जितने rows पढ़े जाते हैं उतने पर lock लगता है। Index से कम rows touch होते हैं, इसलिए cycle बनने की संभावना घटती है। Graph से statement और index पता चलता है।

---

## ⚡ Alternative Solution

```sql
-- Covering index: the SELECT in one transaction no longer needs a key lookup into the clustered index,
-- which removes the classic "reader locks nonclustered key, then wants clustered key" cycle.
CREATE INDEX IX_Orders_Customer_Cover ON dbo.Orders (CustomerId) INCLUDE (Status, Amount);

-- Or turn on row versioning so readers do not take shared locks (see Q120):
ALTER DATABASE ShopDb SET READ_COMMITTED_SNAPSHOT ON;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "fixing" deadlocks by adding WITH (NOLOCK) everywhere
SELECT * FROM dbo.Orders WITH (NOLOCK) WHERE CustomerId = 42;   -- dirty reads, not a fix (Q125)

-- ❌ Wrong: only adding retry logic and never reading the graph
-- Retry (Q130) is a safety net, not a root-cause fix.

-- ❌ Wrong: assuming the victim statement is the cause
-- The victim is chosen by cost to roll back (DEADLOCK_PRIORITY, log used); the other side may be the real problem.
```

---

## 🎯 Interview Tip (1 line)
Say: "I pull the xml_deadlock_report from system_health, identify the two statements and the objects, check for scans or missing foreign key indexes, and fix by indexing, consistent access order, and shorter transactions. I add retry for 1205 as a safety net and consider RCSI to remove reader-writer deadlocks."

---

## 🔗 Related Questions
→ Q122 (locks) | Q123 (blocking vs deadlock) | Q124 (deadlock prevention patterns) | Q130 (retry for error 1205)
