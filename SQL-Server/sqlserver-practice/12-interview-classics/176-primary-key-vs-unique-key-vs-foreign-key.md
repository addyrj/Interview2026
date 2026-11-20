---

# Q176. Primary Key vs Unique Key vs Foreign Key
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: SQL Server (MySQL/PostgreSQL differ on NULLs in UNIQUE: both allow many NULLs; SQL Server allows only ONE NULL in a unique constraint/index)

---

## ❓ Question
Explain the difference between primary key, unique key and foreign key with a Customers/Orders example. Include NULL behaviour, clustered index behaviour, and what happens on violations.

---

## 💡 Quick Concept (2 lines only)
Primary key = the row's identity: unique, NOT NULL, one per table (by default backed by a clustered index in SQL Server). Unique key = another uniqueness rule, many allowed per table, and in SQL Server only one NULL. Foreign key = a link to a parent key that stops orphan rows.
हिंदी: PK = row की पहचान (NOT NULL, एक ही)। UNIQUE = और uniqueness, कई हो सकते हैं, SQL Server में सिर्फ एक NULL। FK = parent से link, orphan रोकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Customers (
  CustomerId INT IDENTITY(1,1) NOT NULL,
  Email      VARCHAR(100) NULL,
  Phone      VARCHAR(20)  NULL,
  CONSTRAINT PK_Customers PRIMARY KEY CLUSTERED (CustomerId),   -- identity of the row
  CONSTRAINT UQ_Customers_Email UNIQUE NONCLUSTERED (Email)     -- business rule
);

CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1,1) NOT NULL,
  CustomerId INT NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  CONSTRAINT PK_Orders PRIMARY KEY CLUSTERED (OrderId),
  CONSTRAINT FK_Orders_Customers FOREIGN KEY (CustomerId)
      REFERENCES dbo.Customers (CustomerId)
);
CREATE INDEX IX_Orders_CustomerId ON dbo.Orders (CustomerId);   -- SQL Server does NOT auto-index FKs

SET IDENTITY_INSERT dbo.Customers ON;
INSERT INTO dbo.Customers (CustomerId, Email, Phone) VALUES
  (1, 'asha@shop.in', '999'),
  (2, 'ravi@shop.in', NULL);
SET IDENTITY_INSERT dbo.Customers OFF;

-- ============================================
-- VIOLATIONS (each statement fails; messages follow the pattern in the docs)
-- ============================================
SET IDENTITY_INSERT dbo.Customers ON;   -- explicit id needed to demonstrate a duplicate PK
INSERT INTO dbo.Customers (CustomerId, Email) VALUES (1, 'x@shop.in');
SET IDENTITY_INSERT dbo.Customers OFF;
-- duplicate PK  -> error 2627 (violation of PRIMARY KEY constraint)
INSERT INTO dbo.Customers (Email) VALUES ('asha@shop.in');
-- duplicate email -> error 2627 (violation of UNIQUE KEY constraint 'UQ_Customers_Email')
INSERT INTO dbo.Orders (CustomerId, Amount) VALUES (99, 10);
-- no such customer -> error 547 (INSERT conflicted with the FOREIGN KEY constraint)

-- Result of the three failing statements checked on SQLite 3 (equivalent schema):
--   duplicate PK      -> rejected
--   duplicate email   -> rejected
--   orphan order      -> rejected (FOREIGN KEY constraint failed)
-- Error numbers 2627 and 547 are from Microsoft docs; not executed on SQL Server.

-- NULL behaviour (UNIQUE):
INSERT INTO dbo.Customers (Email, Phone) VALUES (NULL, '1');   -- first NULL: OK
INSERT INTO dbo.Customers (Email, Phone) VALUES (NULL, '2');   -- second NULL: FAILS in SQL Server (2627)
-- SQLite/MySQL/PostgreSQL accept both rows (verified on SQLite 3). SQL Server's rule is per Microsoft docs;
-- not executed on SQL Server. Workaround: a FILTERED unique index:
CREATE UNIQUE INDEX UX_Customers_Email_NotNull ON dbo.Customers (Email) WHERE Email IS NOT NULL;
-- (use this INSTEAD of the UNIQUE constraint above if many NULL emails must be allowed)
```

---

## 🔍 Why This Works (3 lines max)
PK and UNIQUE are both enforced by a unique index; the PK additionally forbids NULL and by default becomes the clustered index, deciding physical row order. The FK check makes SQL Server look up the parent key on insert/update of the child, and the referenced side must be a PK or UNIQUE. SQL Server treats NULLs as equal inside a unique index, hence only one NULL.
हिंदी: PK और UNIQUE दोनों के पीछे unique index होता है। FK parent में lookup करता है। SQL Server unique index में NULL को equal मानता है, इसलिए सिर्फ एक NULL।

---

## ⚡ Alternative Solution

```sql
-- Filtered unique index = "unique among non-NULL values" (the usual real-world answer)
-- Composite keys
ALTER TABLE dbo.Orders ADD CONSTRAINT UQ_Orders_Customer_Ref UNIQUE (CustomerId, Amount);
-- Cascading rules: choose deliberately
-- ALTER TABLE dbo.Orders ADD CONSTRAINT FK_x ... ON DELETE CASCADE;  -- or NO ACTION (default), SET NULL
-- Disabled/untrusted FK: WITH NOCHECK adds the FK without validating old rows -> optimizer ignores it
-- Surrogate (IDENTITY) vs natural keys: see Q024 and Q035.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming SQL Server indexes FK columns automatically (it does not; MySQL InnoDB does).
--    Result: slow joins and long locks when deleting a parent. Create the index yourself.
-- ❌ Wrong: PK on a random GUID with the default CLUSTERED option -> page splits.
--    Use NEWSEQUENTIALID(), or make the PK NONCLUSTERED and cluster on another column.
-- ❌ Wrong: relying on application checks instead of FKs, then finding orphans in production.
-- ❌ Wrong: adding FKs WITH NOCHECK and forgetting to re-validate (WITH CHECK CHECK CONSTRAINT).
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "PK is identity plus the clustering key by default, so I keep it narrow, static and ever-increasing. UNIQUE enforces business rules; SQL Server allows one NULL, so for optional unique columns I use a filtered unique index. FKs give integrity and help the optimizer, but I index the FK columns myself and think about cascade and lock behaviour on big parent deletes." Mention trusted vs untrusted constraints (`is_not_trusted` in `sys.foreign_keys`).

---

## 🔗 Related Questions
→ Q026 (PRIMARY KEY, UNIQUE and FOREIGN KEY with cascade) | Q025 (CREATE TABLE with constraints) | Q024 (GUID vs INT keys) | Q102 (clustered vs non-clustered index) | Q105 (filtered indexes)
