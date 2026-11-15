---

# Q089. Inline Table-Valued Functions
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: no table-valued functions; PostgreSQL: RETURNS TABLE / SETOF functions + LATERAL)

---

## ❓ Question
Create a parameterised "view" that returns a customer's orders above a minimum amount, then use it to get the 2 most recent qualifying orders for every customer, including customers who have none.

---

## 💡 Quick Concept (2 lines only)
An inline TVF is `RETURNS TABLE AS RETURN (SELECT ...)`: a view that accepts parameters. The optimizer expands it into the calling query, so it is as fast as hand-written SQL, and CROSS/OUTER APPLY calls it per outer row.
हिंदी: Inline TVF = parameter वाला view। Optimizer इसे query में expand कर देता है, इसलिए fast। Per-row call के लिए CROSS/OUTER APPLY।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Customers (CustomerId INT PRIMARY KEY, Name NVARCHAR(100) NOT NULL);
CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY, CustomerId INT NOT NULL,
  OrderDate DATE NOT NULL, Amount DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Customers VALUES (1, N'Asha Rao'), (2, N'Vikram Shah'), (3, N'Meera Iyer');
INSERT INTO dbo.Orders VALUES
  (1, 1, '2024-01-05', 500), (2, 1, '2024-02-10', 300), (3, 1, '2024-03-15', 700),
  (4, 2, '2024-01-20', 200), (5, 2, '2024-02-25', 900);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER FUNCTION dbo.itvf_CustomerOrders (@CustomerId INT, @MinAmount DECIMAL(10,2), @TopN INT)
RETURNS TABLE
AS
RETURN
(
  SELECT TOP (@TopN) OrderId, OrderDate, Amount
  FROM dbo.Orders
  WHERE CustomerId = @CustomerId AND Amount >= @MinAmount
  ORDER BY OrderDate DESC
);
GO

-- Two most recent orders >= 200 per customer (customers without orders are dropped):
SELECT c.Name, t.OrderId, t.Amount
FROM dbo.Customers c
CROSS APPLY dbo.itvf_CustomerOrders(c.CustomerId, 200, 2) t
ORDER BY c.Name, t.OrderDate DESC;

-- EXPECTED OUTPUT (result derived from an equivalent ROW_NUMBER() join on SQLite, since SQLite
-- has no APPLY; not executed on SQL Server):
-- Name        | OrderId | Amount
-- Asha Rao    | 3       | 700.00
-- Asha Rao    | 2       | 300.00
-- Vikram Shah | 5       | 900.00
-- Vikram Shah | 4       | 200.00

-- Keep customers with no qualifying orders:
SELECT c.Name, t.OrderId
FROM dbo.Customers c
OUTER APPLY dbo.itvf_CustomerOrders(c.CustomerId, 200, 2) t
WHERE c.CustomerId = 3;

-- EXPECTED OUTPUT (LEFT JOIN equivalent on SQLite):
-- Name       | OrderId
-- Meera Iyer | NULL
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The function body is a single SELECT, so the optimizer treats it like a parameterised view and merges it into the outer plan (no per-row function call). APPLY evaluates the right side for each left row, which allows TOP N per group and correlated parameters. OUTER APPLY keeps left rows with no match, like LEFT JOIN.
हिंदी: Body सिर्फ़ एक SELECT, इसलिए plan में merge हो जाती है। CROSS APPLY = INNER जैसा, OUTER APPLY = LEFT जैसा।

---

## ⚡ Alternative Solution

```sql
-- Without a function: ROW_NUMBER (works on every version and engine)
SELECT Name, OrderId, Amount
FROM (
  SELECT c.Name, o.OrderId, o.Amount,
         ROW_NUMBER() OVER (PARTITION BY c.CustomerId ORDER BY o.OrderDate DESC) AS rn
  FROM dbo.Customers c
  JOIN dbo.Orders o ON o.CustomerId = c.CustomerId AND o.Amount >= 200
) x
WHERE rn <= 2;
-- On large tables, APPLY + a supporting index (CustomerId, OrderDate DESC) INCLUDE (Amount)
-- often wins; compare both plans.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: writing a multi-statement TVF (BEGIN ... RETURN @t) for a one-query job
--    -> optimizer cannot inline it, uses a fixed row estimate (Q090).
-- ❌ Wrong: calling an iTVF in FROM like a scalar: SELECT dbo.itvf_CustomerOrders(1,200,2);  -- invalid
-- ❌ Wrong: CROSS APPLY when you need customers without orders -> they silently disappear. Use OUTER APPLY.
-- ✅ Single SELECT, schema-qualified name, SCHEMABINDING if views/indexes depend on it.
```

---

## 🎯 Interview Tip (1 line)
Say: "Inline TVF is my default reusable-query building block: parameterised, fully inlined, statistics flow through. I pair it with APPLY for top-N-per-row, choose OUTER APPLY when the parent must be preserved, and reach for multi-statement TVFs only when procedural logic truly cannot be expressed as one query."

---

## 🔗 Related Questions
→ Q038 (CROSS APPLY and OUTER APPLY) | Q088 (Scalar UDF cost) | Q090 (Multi-statement TVF) | Q091 (Views) | Q067 (Top-N per group)
