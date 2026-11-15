---

# Q013. IDENTITY, SCOPE_IDENTITY, @@IDENTITY and SEQUENCE
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (SEQUENCE 2012+; MySQL: AUTO_INCREMENT + LAST_INSERT_ID(), PostgreSQL: SERIAL/IDENTITY + sequences)

---

## ❓ Question
An `Orders` table uses `IDENTITY(1000,1)`. How do you safely read the new id after an INSERT, why is `@@IDENTITY` dangerous, why do gaps appear, how do you insert an explicit id, and when would you choose a `SEQUENCE` instead?

---

## 💡 Quick Concept (2 lines only)
`SCOPE_IDENTITY()` = last identity in the current session AND scope (safe); `@@IDENTITY` = last in the session across ALL scopes (may come from a trigger); `IDENT_CURRENT('tbl')` = last for the table in ANY session. A `SEQUENCE` is a standalone number generator shared by many tables.
हिंदी: नया id पढ़ने के लिए SCOPE_IDENTITY() या OUTPUT use करो, @@IDENTITY नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1000, 1) PRIMARY KEY,
  CustomerId INT           NOT NULL,
  Note       NVARCHAR(100) NULL
);

-- ============================================
-- 1. Read the generated id
-- ============================================

INSERT INTO dbo.Orders (CustomerId, Note) VALUES (1, N'first');
SELECT SCOPE_IDENTITY() AS NewOrderId;           -- 1000

INSERT INTO dbo.Orders (CustomerId, Note) VALUES (2, N'second');
SELECT SCOPE_IDENTITY() AS NewOrderId;           -- 1001

-- Best for APIs: one round trip, works for multi-row inserts too
INSERT INTO dbo.Orders (CustomerId, Note)
OUTPUT inserted.OrderId
VALUES (3, N'third');                             -- 1002

-- ============================================
-- 2. Gaps: a rolled-back insert still consumes an identity value
-- ============================================

BEGIN TRANSACTION;
  INSERT INTO dbo.Orders (CustomerId, Note) VALUES (4, N'will rollback');   -- takes 1003
ROLLBACK TRANSACTION;

INSERT INTO dbo.Orders (CustomerId, Note) OUTPUT inserted.OrderId VALUES (5, N'after rollback');  -- 1004 (gap at 1003)

-- ============================================
-- 3. Explicit id insert + reseed
-- ============================================

SET IDENTITY_INSERT dbo.Orders ON;
INSERT INTO dbo.Orders (OrderId, CustomerId, Note) VALUES (500, 9, N'imported');   -- column list is required
SET IDENTITY_INSERT dbo.Orders OFF;

DBCC CHECKIDENT ('dbo.Orders', NORESEED);        -- reports current identity and max column value

-- ============================================
-- 4. SEQUENCE (SQL Server 2012+): shared, can be fetched before the INSERT
-- ============================================

CREATE SEQUENCE dbo.InvoiceNo AS INT START WITH 5000 INCREMENT BY 1 CACHE 50;

SELECT NEXT VALUE FOR dbo.InvoiceNo AS InvoiceNo;   -- 5000
SELECT NEXT VALUE FOR dbo.InvoiceNo AS InvoiceNo;   -- 5001

CREATE TABLE dbo.Invoices (
  InvoiceNo INT NOT NULL PRIMARY KEY DEFAULT (NEXT VALUE FOR dbo.InvoiceNo),
  OrderId   INT NOT NULL
);

-- Note: ids 1000/1001 and the post-rollback id are the documented behaviour of IDENTITY;
-- only the "ids keep counting after DELETE" part was checked on SQLite (AUTOINCREMENT gave 1,2).
-- SCOPE_IDENTITY, OUTPUT, IDENTITY_INSERT, DBCC CHECKIDENT and SEQUENCE are not
-- executed on SQL Server; behaviour per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
Identity values are allocated outside the transaction for concurrency, so a rollback never gives the number back and gaps are normal. Scope matters because triggers run in their own scope: a trigger that inserts into an audit table with an identity changes `@@IDENTITY` but not `SCOPE_IDENTITY()`.
हिंदी: Identity में gaps normal हैं (rollback, crash, cache)। Gap-free numbering identity से नहीं मिलती।

---

## ⚡ Alternative Solution

```sql
-- Get the id before inserting (e.g. to write parent and child rows with the same key)
DECLARE @InvoiceNo INT = NEXT VALUE FOR dbo.InvoiceNo;
INSERT INTO dbo.Invoices (InvoiceNo, OrderId) VALUES (@InvoiceNo, 1000);

-- Several ids in one call:
DECLARE @first SQL_VARIANT;
EXEC sys.sp_sequence_get_range @sequence_name = N'dbo.InvoiceNo', @range_size = 100, @range_first_value = @first OUTPUT;

-- Use SEQUENCE when: one counter feeds many tables, ids are needed client-side before insert,
-- or you need CYCLE / MAXVALUE / restart without table rebuild.
-- Use UNIQUEIDENTIFIER (NEWSEQUENTIALID) when ids must be generated across distributed nodes.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: @@IDENTITY after an insert on a table with an audit trigger
INSERT INTO dbo.Orders (CustomerId) VALUES (7);
SELECT @@IDENTITY;      -- may return the identity created by the trigger's insert into another table
-- ✅ SCOPE_IDENTITY() or OUTPUT.

-- ❌ Wrong: IDENT_CURRENT('dbo.Orders') for "my" id -> another session may have inserted in between.

-- ❌ Wrong: expecting gap-free, ordered invoice numbers from IDENTITY/SEQUENCE.
-- ✅ Legal requirements for gap-free numbers need a counter table updated inside the transaction.

-- ❌ Wrong: running SET IDENTITY_INSERT ON for two tables in one session (only one at a time),
--    or inserting explicit ids without a column list.
-- ❌ Wrong: TRUNCATE to "reset" a table that is referenced by FKs.
-- Note: after an instance restart, SEQUENCE/IDENTITY cached values can be skipped (larger gaps) - by design.
```

---

## 🎯 Interview Tip (1 line)
Say: "I read new keys with OUTPUT inserted.Id (or SCOPE_IDENTITY for single rows), never @@IDENTITY, and I don't rely on identity being contiguous. I'd pick a SEQUENCE when several tables share a counter or the app needs the id before inserting, and from Node's mssql I return the id from the same batch."

---

## 🔗 Related Questions
→ Q010 (OUTPUT clause) | Q012 (TRUNCATE vs DELETE vs DROP) | Q024 (UNIQUEIDENTIFIER vs INT keys) | Q099 (Synonyms and sequences) | Q096 (inserted and deleted tables)
