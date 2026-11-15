---

# Q027. CHECK and DEFAULT Constraints
# Category: DDL + DATA TYPES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: CHECK enforced from 8.0.16; PostgreSQL: CHECK + DEFAULT same idea, NOT VALID instead of NOCHECK)

---

## ❓ Question
Add business rules to a Products table: price is not negative, discount is between 0 and 100, status defaults to `Active`, stock defaults to 0. What does a CHECK do with NULL? What happens with `WITH NOCHECK` and why is the constraint then "not trusted"?

---

## 💡 Quick Concept (2 lines only)
CHECK rejects a row only when its expression is FALSE; if the result is UNKNOWN (NULL) the row is accepted. DEFAULT supplies a value only when the column is omitted from the INSERT (or `DEFAULT` is written), never when NULL is explicitly inserted.
हिंदी: CHECK सिर्फ FALSE पर reject करता है; NULL (UNKNOWN) पास हो जाता है। DEFAULT तभी लगता है जब column INSERT में दिया ही नहीं; explicit NULL देने पर NULL जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Products (
  ProductId INT           NOT NULL CONSTRAINT PK_Products PRIMARY KEY,
  Price     DECIMAL(10,2) NOT NULL CONSTRAINT CK_Products_Price CHECK (Price >= 0),
  Discount  DECIMAL(5,2)  NULL     CONSTRAINT CK_Products_Discount CHECK (Discount BETWEEN 0 AND 100),
  Status    VARCHAR(10)   NOT NULL CONSTRAINT DF_Products_Status DEFAULT ('Active'),
  Stock     INT           NOT NULL CONSTRAINT DF_Products_Stock  DEFAULT (0),
  CreatedAt DATETIME2(0)  NOT NULL CONSTRAINT DF_Products_CreatedAt DEFAULT (SYSUTCDATETIME())
);

INSERT INTO Products (ProductId, Price)           VALUES (1, 99.50);
INSERT INTO Products (ProductId, Price, Discount) VALUES (2, 50.00, NULL);  -- NULL passes the CHECK
GO

-- ============================================
-- SOLUTION
-- ============================================

SELECT ProductId, Price, Discount, Status, Stock FROM Products ORDER BY ProductId;

-- Output:
-- ProductId | Price | Discount | Status | Stock
-- 1         | 99.50 | NULL     | Active | 0
-- 2         | 50.00 | NULL     | Active | 0

-- These are rejected by the CHECK constraints:
INSERT INTO Products (ProductId, Price)           VALUES (3, -5);      -- CK_Products_Price
INSERT INTO Products (ProductId, Price, Discount) VALUES (4, 10, 150); -- CK_Products_Discount
-- Expected: error 547 "The INSERT statement conflicted with the CHECK constraint ..." (per docs)

-- Results (accepted rows with defaults, NULL passing the check, two CHECK failures) derived from the
-- equivalent schema on SQLite 3.49; error text and number per Microsoft docs; CreatedAt is omitted
-- because SYSUTCDATETIME() has no SQLite equivalent; not executed on SQL Server.

-- Explicit NULL does NOT trigger the DEFAULT:
-- INSERT INTO Products (ProductId, Price, Status) VALUES (5, 1, NULL);   -- fails: Status is NOT NULL
-- Use DEFAULT keyword instead:
INSERT INTO Products (ProductId, Price, Status) VALUES (5, 1, DEFAULT);   -- Status = 'Active'
```

---

## 🔍 Why This Works (3 lines max)
A CHECK predicate evaluates to TRUE, FALSE or UNKNOWN; only FALSE blocks the write, so a nullable `Discount` bypasses the rule when NULL (add `NOT NULL` or `AND Discount IS NOT NULL` if that is not intended). A DEFAULT is a column-level fallback used when the column is missing from the insert list; it never overrides an explicit NULL.
हिंदी: CHECK = TRUE/FALSE/UNKNOWN में सिर्फ FALSE reject। Nullable column पर rule NULL से bypass हो जाता है। DEFAULT तभी जब column omit हो।

---

## ⚡ Alternative Solution

```sql
-- Add a rule to an existing table with live data
-- 1) WITH CHECK (default for new constraints) validates existing rows and creates a TRUSTED constraint
ALTER TABLE Products WITH CHECK ADD CONSTRAINT CK_Products_Stock CHECK (Stock >= 0);

-- 2) WITH NOCHECK skips validation of old rows (fast, but constraint becomes NOT TRUSTED)
ALTER TABLE Products WITH NOCHECK ADD CONSTRAINT CK_Products_Status
    CHECK (Status IN ('Active', 'Inactive', 'Discontinued'));

-- Find untrusted constraints
SELECT name, is_not_trusted, is_disabled FROM sys.check_constraints WHERE is_not_trusted = 1;

-- Re-validate old data and make the constraint trusted again
ALTER TABLE Products WITH CHECK CHECK CONSTRAINT CK_Products_Status;

-- Temporarily disable / enable (bulk loads)
ALTER TABLE Products NOCHECK CONSTRAINT CK_Products_Stock;
ALTER TABLE Products CHECK CONSTRAINT CK_Products_Stock;
-- Catalog views, NOCHECK and trust behaviour: not executed on SQL Server; per Microsoft docs.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: believing CHECK (Discount BETWEEN 0 AND 100) blocks NULL
INSERT INTO Products (ProductId, Price, Discount) VALUES (6, 10, NULL);   -- accepted

-- ❌ Wrong: WITH NOCHECK and then forgetting about it
--    An untrusted constraint is ignored by the optimizer (no contradiction detection / join
--    elimination), so queries can get slower.
-- ❌ Wrong: ALTER TABLE ... ADD CONSTRAINT ... CHECK on a huge table in peak hours -
--    validation scans the whole table while holding a schema lock.
-- ❌ Wrong: DEFAULT with a function that is non-deterministic where you expect a constant, e.g.
--    DEFAULT GETDATE() is evaluated per row at insert time (that is usually what you want, but a
--    constant like '2024-01-01' stays the same forever).
```

---

## 🎯 Interview Tip (1 line)
Say: "CHECK passes on UNKNOWN, so I pair it with NOT NULL when the rule must always hold. Adding it WITH NOCHECK leaves it untrusted, which hurts plans, so I re-validate with WITH CHECK CHECK CONSTRAINT. I name defaults too (DF_) because dropping a column fails while its default constraint exists." Check `is_not_trusted` in `sys.check_constraints` during reviews.

---

## 🔗 Related Questions
→ Q025 (CREATE TABLE with constraints) | Q026 (PK, UNIQUE, FK) | Q028 (ALTER TABLE) | Q062 (aggregate functions with NULL)
