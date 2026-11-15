---

# Q102. Clustered vs Non-Clustered Index
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL InnoDB: PK is always clustered; PostgreSQL tables are heaps, no clustered index)

---

## ❓ Question
Explain the difference between a clustered and a non-clustered index on an `Orders` table. Create both, show how to list them, and explain what a table without a clustered index (a heap) is and why `CustomerId` lookups still need a non-clustered index.

---

## 💡 Quick Concept (2 lines only)
A clustered index IS the table: leaf pages hold the full rows sorted by the key (only one per table). A non-clustered index is a separate B-tree whose leaves hold the index key plus a row locator (the clustering key, or a RID in a heap).
हिंदी: Clustered index = table का data खुद उसी order में रखा होता है (सिर्फ एक)। Non-clustered = अलग sorted सूची जो असली row की तरफ pointer रखती है।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available); behaviour per Microsoft docs.
-- Catalog view output below is what you should expect, kept minimal.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId    INT           NOT NULL,
  CustomerId INT           NOT NULL,
  OrderDate  DATE          NOT NULL,
  Status     VARCHAR(20)   NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (OrderId)   -- PK defaults to CLUSTERED
);

INSERT INTO dbo.Orders VALUES
  (1,101,'2024-01-05','Shipped',120.00),
  (2,101,'2024-02-11','Shipped', 80.00),
  (3,102,'2024-02-15','Pending', 45.50),
  (4,103,'2024-03-02','Shipped',300.00);
GO

-- ============================================
-- NON-CLUSTERED index for lookups by customer
-- ============================================
CREATE NONCLUSTERED INDEX IX_Orders_CustomerId ON dbo.Orders (CustomerId);
GO

-- ============================================
-- List the indexes on the table
-- ============================================
SELECT i.name, i.type_desc, i.is_primary_key
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID('dbo.Orders')
ORDER BY i.index_id;

-- Output:
-- name                 | type_desc    | is_primary_key
-- PK_Orders            | CLUSTERED    | 1
-- IX_Orders_CustomerId | NONCLUSTERED | 0

-- Query that uses the non-clustered index (key lookup for Status/Amount comes from the clustered index):
SELECT OrderId, CustomerId, Status, Amount FROM dbo.Orders WHERE CustomerId = 101;

-- Output (result derived by hand from the sample rows; not executed on SQL Server):
-- OrderId | CustomerId | Status  | Amount
-- 1       | 101        | Shipped | 120.00
-- 2       | 101        | Shipped | 80.00

-- ============================================
-- Heap: table with NO clustered index
-- ============================================
CREATE TABLE dbo.AuditLog (LogId INT NOT NULL, Msg VARCHAR(200));   -- heap; sys.indexes shows type_desc = HEAP
```

---

## 🔍 Why This Works (3 lines max)
Because the clustered key defines physical (logical-chain) order, range queries on `OrderId` read adjacent pages and no second structure is needed. A non-clustered index on `CustomerId` stores `(CustomerId, OrderId)` pairs, so it finds matches fast and then does a key lookup into the clustered index for any extra columns. Every non-clustered index silently carries the clustering key, so a wide clustering key bloats all of them.
हिंदी: Clustered key हर non-clustered index में copy होती है, इसलिए छोटी, unique, बढ़ती हुई key चुनो। Extra columns चाहिए तो key lookup होता है।

---

## ⚡ Alternative Solution

```sql
-- Cluster on something other than the PK when range scans dominate (e.g. time-series reads):
CREATE TABLE dbo.Events (
  EventId BIGINT IDENTITY NOT NULL,
  EventTime DATETIME2 NOT NULL,
  Payload VARCHAR(200),
  CONSTRAINT PK_Events PRIMARY KEY NONCLUSTERED (EventId)
);
CREATE CLUSTERED INDEX CX_Events_Time ON dbo.Events (EventTime, EventId);  -- ensure uniqueness via EventId
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: random GUID as clustered key -> page splits and fragmentation on every insert
CREATE TABLE dbo.Bad (Id UNIQUEIDENTIFIER DEFAULT NEWID() PRIMARY KEY, X INT);
-- ✅ Use INT/BIGINT IDENTITY, or NEWSEQUENTIALID(), or make the GUID PK NONCLUSTERED

-- ❌ Wrong: "I made the PK so it is indexed for CustomerId lookups" - a PK on OrderId does nothing for WHERE CustomerId = 101
-- ❌ Wrong: 15 non-clustered indexes "just in case" - each one slows INSERT/UPDATE/DELETE and costs storage
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "The clustering key should be narrow, unique, static and ever-increasing, because every non-clustered index repeats it. I only leave a table as a heap for staging/bulk-load tables. Then I explain key lookups and fix hot ones with INCLUDE columns (Q103)." If asked about MySQL: InnoDB always clusters on the PK; PostgreSQL has CLUSTER but it is a one-time physical sort, not maintained.

---

## 🔗 Related Questions
→ Q024 (GUID vs INT keys) | Q103 (Covering index and INCLUDE) | Q107 (Reading an execution plan) | Q173 (Clustered vs non-clustered - phone book)
