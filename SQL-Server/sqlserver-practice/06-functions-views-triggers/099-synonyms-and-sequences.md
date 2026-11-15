---

# Q099. Synonyms and Sequences
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL has AUTO_INCREMENT only; PostgreSQL has CREATE SEQUENCE + nextval())

---

## ❓ Question
Your app reads `Customers` that is being moved from the `dbo` schema to a new `crm` schema (and later to another database). Keep old code working without editing every query, using a SYNONYM. Also, generate order numbers (1000, 1001, ...) shared by two tables using a SEQUENCE, and explain how a sequence differs from IDENTITY.

---

## 💡 Quick Concept (2 lines only)
A SYNONYM is just an alias for another object (table, view, proc, function, even in another database or linked server); a SEQUENCE is a schema-level number generator you call with `NEXT VALUE FOR`, usable by many tables and settable before insert (SQL Server 2012+).
हिंदी: Synonym = object का दूसरा नाम (alias), Sequence = अलग number generator जिसे कई tables share कर सकती हैं, IDENTITY सिर्फ एक table-column की होती है।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available); behaviour per Microsoft docs.
-- ============================================
-- SETUP
-- ============================================
CREATE SCHEMA crm;
GO
CREATE TABLE crm.Customers (
  CustomerId INT          NOT NULL PRIMARY KEY,
  Name       VARCHAR(100) NOT NULL
);
INSERT INTO crm.Customers (CustomerId, Name) VALUES (1, 'Asha'), (2, 'Bilal');
GO

-- ============================================
-- SOLUTION 1: SYNONYM keeps legacy name dbo.Customers alive
-- ============================================
CREATE SYNONYM dbo.Customers FOR crm.Customers;
GO

SELECT CustomerId, Name FROM dbo.Customers;   -- old code, unchanged

-- Output:
-- CustomerId | Name
-- 1          | Asha
-- 2          | Bilal

-- Later, point it elsewhere WITHOUT touching callers (drop + create; ALTER SYNONYM does not exist):
DROP SYNONYM dbo.Customers;
CREATE SYNONYM dbo.Customers FOR ArchiveDb.crm.Customers;  -- cross-database
GO

-- ============================================
-- SOLUTION 2: SEQUENCE shared by two tables
-- ============================================
CREATE SEQUENCE dbo.OrderNumberSeq
  AS INT
  START WITH 1000
  INCREMENT BY 1
  NO CYCLE
  CACHE 50;                                   -- cached in memory; gaps possible after restart
GO

CREATE TABLE dbo.OnlineOrders (
  OrderNo INT NOT NULL DEFAULT (NEXT VALUE FOR dbo.OrderNumberSeq) PRIMARY KEY,
  Item    VARCHAR(50) NOT NULL
);
CREATE TABLE dbo.StoreOrders (
  OrderNo INT NOT NULL DEFAULT (NEXT VALUE FOR dbo.OrderNumberSeq) PRIMARY KEY,
  Item    VARCHAR(50) NOT NULL
);

INSERT INTO dbo.OnlineOrders (Item) VALUES ('Keyboard');
INSERT INTO dbo.StoreOrders  (Item) VALUES ('Mouse');
INSERT INTO dbo.OnlineOrders (Item) VALUES ('Monitor');

SELECT OrderNo, Item FROM dbo.OnlineOrders ORDER BY OrderNo;
SELECT OrderNo, Item FROM dbo.StoreOrders  ORDER BY OrderNo;

-- Output (single session, fresh sequence):
-- OnlineOrders: 1000 Keyboard | 1002 Monitor
-- StoreOrders : 1001 Mouse
-- (numbers never repeat across both tables)

-- Get the number BEFORE inserting (impossible with IDENTITY):
DECLARE @n INT = NEXT VALUE FOR dbo.OrderNumberSeq;   -- 1003
```

---

## 🔍 Why This Works (3 lines max)
A synonym is resolved at name-binding time, so callers keep using `dbo.Customers` while the real object moves; it stores no data and no permissions of the target. A sequence is its own object, so the DEFAULT on each table asks the same counter for the next value. Values are not rolled back on transaction rollback, so gaps are normal.
हिंदी: Synonym सिर्फ pointer है, data नहीं रखता। Sequence एक shared counter है; rollback होने पर भी number वापस नहीं आता, इसलिए gaps normal हैं।

---

## ⚡ Alternative Solution

```sql
-- IDENTITY: simplest when one table owns the number and you only need it AFTER insert
CREATE TABLE dbo.Invoices (
  InvoiceId INT IDENTITY(1000,1) PRIMARY KEY,
  Amount    DECIMAL(10,2) NOT NULL
);

-- Reserve a block of numbers for bulk loads (sequence only):
DECLARE @first SQL_VARIANT;
EXEC sys.sp_sequence_get_range
     @sequence_name = N'dbo.OrderNumberSeq',
     @range_size    = 100,
     @range_first_value = @first OUTPUT;
SELECT @first AS FirstReserved;   -- next 100 numbers are yours; no one else will get them
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: expecting gap-free numbers (invoice law!) from SEQUENCE or IDENTITY
BEGIN TRAN;
  INSERT INTO dbo.OnlineOrders (Item) VALUES ('Cable');   -- consumes 1004
ROLLBACK;                                                 -- 1004 is gone for good
-- ✅ If the business needs gap-free numbers, use a counter row updated with UPDLOCK inside the same transaction

-- ❌ Wrong: ALTER SYNONYM (does not exist) and forgetting synonyms break silently
-- SQL Server does not validate the target at CREATE SYNONYM time; a typo shows up only at runtime.
-- ❌ Wrong: using a synonym as the target of DDL (ALTER TABLE dbo.Customers ...) - not allowed; use the real name.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I use synonyms for zero-downtime refactors (moving a table to another schema or database) and for hiding cross-database names behind environment-specific deployment. I pick SEQUENCE over IDENTITY when I need the key before insert, a number shared across tables, or a range pre-reserved for batch loads - and I always call out that neither is gap-free." Note Azure SQL Database does not allow cross-database synonyms with three-part names to other databases (use elastic query instead) - verify against current docs.

---

## 🔗 Related Questions
→ Q013 (IDENTITY, SCOPE_IDENTITY and SEQUENCE) | Q019 (Schemas and object naming) | Q024 (GUID vs INT keys) | Q101 (User-defined table types)
