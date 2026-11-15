---

# Q105. Filtered Indexes
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL calls them partial indexes; MySQL has no equivalent)

---

## ❓ Question
Only 5% of `Orders` are `Pending` but the fulfilment screen queries them constantly. Create a filtered index for pending orders, enforce "one active subscription per customer" with a filtered UNIQUE index, and explain when the optimizer cannot use a filtered index (parameters!).

---

## 💡 Quick Concept (2 lines only)
A filtered index is a non-clustered index with a WHERE clause, so it stores only the matching rows: smaller, cheaper to maintain and more accurate statistics. The optimizer uses it only when the query's predicate provably implies the index filter.
हिंदी: Filtered index = index जिसमें सिर्फ WHERE से match होने वाली rows होती हैं। छोटी और तेज़, पर query का predicate index के filter से match होना चाहिए।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Result sets derived from equivalent
-- queries on SQLite; index selection behaviour per Microsoft docs.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  OrderDate  DATE NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders VALUES
  (1,101,'2024-01-05','Shipped',120.00),
  (2,101,'2024-02-11','Shipped', 80.00),
  (3,102,'2024-02-15','Pending', 45.50),
  (4,103,'2024-03-02','Shipped',300.00),
  (5,101,'2024-03-20','Pending', 60.00),
  (6,102,'2024-03-25','Cancelled',15.00),
  (7,103,'2024-04-01','Pending', 99.00);
GO

-- ============================================
-- 1) Filtered index: pending orders only
-- ============================================
CREATE NONCLUSTERED INDEX IX_Orders_Pending
  ON dbo.Orders (CustomerId, OrderDate)
  INCLUDE (Amount)
  WHERE Status = 'Pending';
GO

SELECT OrderId, CustomerId, Amount
FROM dbo.Orders
WHERE Status = 'Pending'           -- literal matches the index filter
ORDER BY OrderId;

-- Output:
-- OrderId | CustomerId | Amount
-- 3       | 102        | 45.50
-- 5       | 101        | 60.00
-- 7       | 103        | 99.00
-- (3 of 7 rows are in the index here; in a real table with ~5% pending the index is ~5% of the size)

-- ============================================
-- 2) Filtered UNIQUE index: one active subscription per customer
-- ============================================
CREATE TABLE dbo.Subscriptions (
  SubId INT PRIMARY KEY, CustomerId INT NOT NULL, IsActive BIT NOT NULL
);
CREATE UNIQUE NONCLUSTERED INDEX UX_Subscriptions_OneActive
  ON dbo.Subscriptions (CustomerId) WHERE IsActive = 1;

INSERT INTO dbo.Subscriptions VALUES (1, 101, 1);
INSERT INTO dbo.Subscriptions VALUES (2, 101, 0);   -- OK: inactive rows are outside the index
INSERT INTO dbo.Subscriptions VALUES (3, 101, 1);   -- FAILS: duplicate active row for customer 101 (unique index violation)
-- Many inactive rows per customer are fine; only ONE active row each. (MySQL has no such feature.)
```

---

## 🔍 Why This Works (3 lines max)
Rows with `Status <> 'Pending'` are never inserted into the index, so it stays tiny and writes on shipped orders do not touch it. The unique filtered index enforces uniqueness only among rows matching `IsActive = 1`, giving a "unique where" constraint that a plain UNIQUE cannot express.
हिंदी: Filter से बाहर की rows index में जाती ही नहीं, इसलिए यह छोटी रहती है। Filtered UNIQUE से "सिर्फ active rows में unique" वाला rule लग जाता है।

---

## ⚡ Alternative Solution

```sql
-- Parameterised queries: the optimizer cannot prove @s = 'Pending' at compile time, so the filtered index is skipped.
DECLARE @s VARCHAR(20) = 'Pending';
SELECT OrderId FROM dbo.Orders WHERE Status = @s;            -- may NOT use IX_Orders_Pending
SELECT OrderId FROM dbo.Orders WHERE Status = @s OPTION (RECOMPILE);   -- can use it (embeds the value)
-- With sp_executesql the same issue applies unless you add OPTION (RECOMPILE) or hardcode the literal.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: filtered index with OR / functions / complex expressions - the filter predicate allows only simple comparisons (AND of simple predicates)
CREATE INDEX IX_Bad ON dbo.Orders (CustomerId) WHERE Status = 'Pending' OR Status = 'Shipped';   -- not allowed (OR)
-- ❌ Wrong: assuming it always gets picked for parameterised procs (see above)
-- ❌ Wrong: ignoring SET options - filtered indexes need standard ANSI settings (QUOTED_IDENTIFIER ON, ANSI_NULLS ON) in the session that modifies the table,
--           otherwise INSERT/UPDATE fails; Node `mssql`/tedious uses the safe defaults, but legacy tools may not.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "Filtered indexes shine on skewed columns (Status = 'Pending', IsDeleted = 0, NULL-able 'unique if present' columns). The trap is parameterisation: a filtered index is matched against the query predicate at compile time, so I either use literals, OPTION (RECOMPILE), or design the proc so the filter is a constant." Soft-delete uniqueness (`UNIQUE WHERE IsDeleted = 0`) is the classic real-world use.

---

## 🔗 Related Questions
→ Q085 (Soft delete and audit) | Q103 (Covering index) | Q114 (Parameter sniffing and fixes) | Q109 (Statistics)
