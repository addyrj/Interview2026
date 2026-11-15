---

# Q098. Triggers — When NOT to Use Them
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (same guidance applies to MySQL and PostgreSQL triggers)

---

## ❓ Question
A colleague proposes a trigger on Orders that updates Customers.TotalSpent, sends email via a linked server and recalculates inventory. Explain why this is risky, give the trigger-free alternatives, and show a correct set-based version if a trigger is truly needed.

---

## 💡 Quick Concept (2 lines only)
Triggers run invisibly inside the caller's transaction: they add latency, extend locks, cascade into other triggers, break bulk loads and surprise developers. Prefer constraints, procedures, computed columns, OUTPUT, indexed views or temporal tables; use triggers only for logic that must hold for every writer.
हिंदी: Trigger छुपा हुआ चलता है, उसी transaction में: latency, locks, cascade, surprise। पहले constraint/procedure/OUTPUT/computed column सोचो, trigger आख़िरी option।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Customers (CustomerId INT PRIMARY KEY, Name NVARCHAR(100) NOT NULL, TotalSpent DECIMAL(12,2) NOT NULL DEFAULT 0);
CREATE TABLE dbo.Orders (OrderId INT IDENTITY(1,1) PRIMARY KEY, CustomerId INT NOT NULL, Amount DECIMAL(10,2) NOT NULL);

INSERT INTO dbo.Customers (CustomerId, Name) VALUES (1, N'Asha Rao'), (2, N'Vikram Shah');
GO

-- ============================================
-- SOLUTION
-- ============================================

-- ❌ The risky version (row-assumptions, side effects)
-- CREATE TRIGGER dbo.trg_Bad ON dbo.Orders AFTER INSERT AS
-- BEGIN
--   DECLARE @c INT, @a DECIMAL(10,2);
--   SELECT @c = CustomerId, @a = Amount FROM inserted;     -- one row only!
--   UPDATE dbo.Customers SET TotalSpent += @a WHERE CustomerId = @c;
--   EXEC msdb.dbo.sp_send_dbmail ...;                       -- external call inside the transaction
-- END;

-- ✅ If a trigger is justified: tiny, set-based, no external side effects
CREATE OR ALTER TRIGGER dbo.trg_Orders_UpdateTotal
ON dbo.Orders
AFTER INSERT
AS
BEGIN
  SET NOCOUNT ON;

  UPDATE c
  SET c.TotalSpent = c.TotalSpent + s.Total
  FROM dbo.Customers c
  JOIN (SELECT CustomerId, SUM(Amount) AS Total FROM inserted GROUP BY CustomerId) s
    ON s.CustomerId = c.CustomerId;
END;
GO

INSERT INTO dbo.Orders (CustomerId, Amount) VALUES (1, 100), (1, 250), (2, 80);

SELECT CustomerId, Name, TotalSpent FROM dbo.Customers ORDER BY CustomerId;

-- EXPECTED OUTPUT (hand-checked: customer 1 = 100 + 250, customer 2 = 80; the trigger is not
-- executed on SQL Server; behaviour per Microsoft docs):
-- CustomerId | Name        | TotalSpent
-- 1          | Asha Rao    | 350.00
-- 2          | Vikram Shah | 80.00
```

Use something else when:
- Business rule across rows: a CHECK/FOREIGN KEY/UNIQUE constraint or filtered unique index.
- Derived value: computed column (Q029) or an indexed view instead of maintaining TotalSpent by hand.
- Audit/history: temporal tables (Q030) or OUTPUT.
- Workflow, email, queues: write to an outbox table in the same transaction and let a worker send it.
- Multi-step business logic: a stored procedure the application calls explicitly.

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The set-based trigger aggregates `inserted` per customer so multi-row inserts are handled correctly, and it touches only local tables. Side effects such as email or linked-server calls are removed because they extend the transaction, can fail the original INSERT and cannot be rolled back. Better still, replace the trigger with a view or computed total.
हिंदी: Set-based trigger multi-row सही संभालता है। Email/linked server जैसी बाहरी calls हटाओ वरना original INSERT fail हो सकता है। बेहतर: trigger की जगह view/computed value।

---

## ⚡ Alternative Solution

```sql
-- Derive the total instead of storing it: no trigger, no drift
CREATE OR ALTER VIEW dbo.vCustomerTotals
AS
SELECT c.CustomerId, c.Name, COALESCE(SUM(o.Amount), 0) AS TotalSpent
FROM dbo.Customers c
LEFT JOIN dbo.Orders o ON o.CustomerId = c.CustomerId
GROUP BY c.CustomerId, c.Name;

-- Outbox pattern for notifications (same transaction as the order):
-- INSERT INTO dbo.Outbox (EventType, Payload) VALUES ('OrderCreated', @json);  -- worker sends the email
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: trigger chains (A updates B, whose trigger updates C ...) -> recursion, deadlocks, impossible debugging.
-- ❌ Wrong: slow code, cursors or external calls in triggers -> every INSERT pays and holds locks longer.
-- ❌ Wrong: forgetting bulk operations: BULK INSERT/bcp skip triggers unless FIRE_TRIGGERS is set,
--    so logic silently does not run; also triggers fire on zero-row statements.
-- ❌ Wrong: business rules only in a trigger that developers do not know about.
-- ✅ Prefer explicit code paths; if you keep a trigger, document and test multi-row + bulk cases.
```

---

## 🎯 Interview Tip (1 line)
Say: "My rule: constraints first, procedures second, triggers last. I use triggers only for invariants that must hold for every writer, keep them set-based and side-effect free, and move email or integration work to an outbox. I also remember bulk loads can bypass triggers, and that triggers hide cost from application developers."

---

## 🔗 Related Questions
→ Q094 (AFTER triggers) | Q095 (INSTEAD OF triggers) | Q097 (Audit trigger pattern) | Q029 (Computed columns) | Q030 (Temporal tables)
