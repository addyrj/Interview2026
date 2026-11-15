---

# Q030. Temporal Tables (System-Versioned)
# Category: DDL + Data Types
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server 2016+ / Azure SQL (MySQL has no equivalent; MariaDB has system-versioned tables; PostgreSQL needs an extension or triggers)

---

## ❓ Question
Keep a full history of every price change on a `Products` table without writing audit triggers. Show how to create a system-versioned temporal table, query the table "as of" a past time, see all versions of a row, and turn versioning off to alter or drop it.

---

## 💡 Quick Concept (2 lines only)
A temporal table has two hidden-able datetime2 period columns (SYSTEM_TIME) and a linked history table; every UPDATE or DELETE copies the old row into history automatically. Query history with FOR SYSTEM_TIME AS OF / BETWEEN / ALL.
हिंदी: Temporal table में हर UPDATE/DELETE पर पुरानी row अपने आप history table में चली जाती है। Trigger लिखने की ज़रूरत नहीं।

---

## ✅ Answer / Solution

```sql
-- NOT EXECUTED ON SQL SERVER: no SQL Server and no equivalent engine here.
-- Behaviour per Microsoft docs. Period timestamps are set by the engine (UTC),
-- so exact timestamps below are placeholders, not real output.

-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Products (
    ProductId  INT           NOT NULL PRIMARY KEY CLUSTERED,
    Name       NVARCHAR(100) NOT NULL,
    Price      DECIMAL(10,2) NOT NULL,
    ValidFrom  DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN NOT NULL,
    ValidTo    DATETIME2 GENERATED ALWAYS AS ROW END   HIDDEN NOT NULL,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.ProductsHistory));

INSERT INTO dbo.Products (ProductId, Name, Price) VALUES (1, N'Keyboard', 25.00);

UPDATE dbo.Products SET Price = 30.00 WHERE ProductId = 1;   -- old row (25.00) goes to history
UPDATE dbo.Products SET Price = 35.00 WHERE ProductId = 1;   -- old row (30.00) goes to history

-- ============================================
-- SOLUTION
-- ============================================

-- 1) Current data only (period columns hidden, so SELECT * does not show them)
SELECT ProductId, Name, Price FROM dbo.Products;

-- 2) Time travel: what was the price at a given moment? (times are UTC)
SELECT ProductId, Name, Price
FROM dbo.Products FOR SYSTEM_TIME AS OF '2025-01-15T10:00:00';

-- 3) Every version of one row, oldest first
SELECT ProductId, Price, ValidFrom, ValidTo
FROM dbo.Products FOR SYSTEM_TIME ALL
WHERE ProductId = 1
ORDER BY ValidFrom;

-- 4) To change schema / drop: turn versioning off first
ALTER TABLE dbo.Products SET (SYSTEM_VERSIONING = OFF);
-- ... ALTER / DROP ...
DROP TABLE dbo.Products;
DROP TABLE dbo.ProductsHistory;

-- ============================================
-- EXPECTED OUTPUT (by design, per docs; timestamps omitted on purpose)
-- ============================================
-- Query 1:  1 | Keyboard | 35.00
-- Query 3:  3 rows for ProductId 1 with Price 25.00, 30.00, 35.00 in that order;
--           the first two have ValidTo = the next row's ValidFrom,
--           the current row has ValidTo = 9999-12-31 23:59:59.9999999.
```

---

## 🔍 Why This Works (3 lines max)
The engine writes the old row version to the history table in the same transaction as the change, stamping the period with the transaction's start time in UTC. Reads with FOR SYSTEM_TIME union current and history rows transparently. History is append-only and cannot be edited while versioning is ON.
हिंदी: Engine खुद period columns भरता है और history एक ही transaction में लिखता है। Versioning ON होने पर history table edit नहीं हो सकती।

---

## ⚡ Alternative Solution

```sql
-- Audit trigger pattern (works on any version, but you maintain it):
CREATE TABLE dbo.ProductPriceAudit (
    AuditId    INT IDENTITY PRIMARY KEY,
    ProductId  INT, OldPrice DECIMAL(10,2), NewPrice DECIMAL(10,2),
    ChangedAt  DATETIME2 DEFAULT SYSUTCDATETIME(), ChangedBy SYSNAME DEFAULT SUSER_SNAME()
);
GO
CREATE TRIGGER dbo.trg_Products_Audit ON dbo.Products AFTER UPDATE AS
INSERT INTO dbo.ProductPriceAudit (ProductId, OldPrice, NewPrice)
SELECT d.ProductId, d.Price, i.Price
FROM deleted d JOIN inserted i ON i.ProductId = d.ProductId
WHERE d.Price <> i.Price;
GO
-- Trade-off: trigger audit records WHO changed it; temporal tables record WHEN, not WHO.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Dropping or altering a temporal table without turning versioning off
DROP TABLE dbo.Products;   -- fails while SYSTEM_VERSIONING = ON

-- ❌ Comparing against local time: period columns are UTC
-- ❌ Forgetting history grows forever: set retention (Azure SQL / 2017+)
ALTER TABLE dbo.Products SET (SYSTEM_VERSIONING = ON (HISTORY_RETENTION_PERIOD = 6 MONTHS));
-- (retention requires the database-level temporal retention setting to be enabled)
-- ❌ Expecting it to capture who/why: it only stores row versions + period.
```

---

## 🎯 Interview Tip (1 line)
Say: "For audit and point-in-time questions I use system-versioned temporal tables because the history is consistent and tamper-resistant; I add a clustered columnstore or proper index on the history table, set a retention policy, and pair it with a column like ModifiedBy when WHO matters." Also mention that period columns are UTC and that it is not a substitute for backups.

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE with constraints) | Q097 (Audit trigger pattern) | Q085 (Soft delete and audit logging procedure) | Q023 (DATETIME2)
