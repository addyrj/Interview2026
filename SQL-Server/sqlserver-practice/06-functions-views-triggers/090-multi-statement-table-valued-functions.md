---

# Q090. Multi-Statement Table-Valued Functions
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: not available; PostgreSQL: PL/pgSQL RETURNS TABLE functions)

---

## ❓ Question
Write a multi-statement TVF that returns a customer's order count and net total, with a "Tier" label computed by procedural logic. Then explain why it can hurt performance and when an inline TVF is better.

---

## 💡 Quick Concept (2 lines only)
A multi-statement TVF declares a return table variable, fills it with several statements and RETURNs it. It is not inlined: the optimizer used a fixed guess for its row count (1 in older versions, 100 in 2014-2016) and gets a better estimate through interleaved execution from SQL Server 2017 (compat 140).
हिंदी: Multi-statement TVF = table variable भरकर return। Optimizer को row count का अंदाज़ा नहीं होता (fixed guess), 2017 में interleaved execution से सुधार।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY, CustomerId INT NOT NULL,
  OrderDate DATE NOT NULL, Amount DECIMAL(10,2) NOT NULL, Discount DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Orders VALUES
  (1, 1, '2024-01-05', 500, 50), (2, 1, '2024-02-10', 300,  0), (3, 1, '2024-03-15', 700, 70),
  (4, 2, '2024-01-20', 200,  0), (5, 2, '2024-02-25', 900, 90);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER FUNCTION dbo.mstvf_CustomerSummary (@CustomerId INT)
RETURNS @Result TABLE
(
  CustomerId  INT,
  OrderCount  INT,
  NetTotal    DECIMAL(12,2),
  Tier        VARCHAR(10)
)
AS
BEGIN
  INSERT INTO @Result (CustomerId, OrderCount, NetTotal)
  SELECT CustomerId, COUNT(*), SUM(Amount - Discount)
  FROM dbo.Orders
  WHERE CustomerId = @CustomerId
  GROUP BY CustomerId;

  UPDATE @Result
  SET Tier = CASE WHEN NetTotal >= 1000 THEN 'GOLD' ELSE 'SILVER' END;

  RETURN;
END;
GO

SELECT CustomerId, OrderCount, NetTotal, Tier FROM dbo.mstvf_CustomerSummary(1);

-- EXPECTED OUTPUT (aggregate part derived from equivalent GROUP BY on SQLite: 3 orders, 1380;
-- Tier applies the CASE rule NetTotal >= 1000 -> GOLD; function not executed on SQL Server):
-- CustomerId | OrderCount | NetTotal | Tier
-- 1          | 3          | 1380.00  | GOLD
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
The function builds the result in a table variable using ordinary statements (INSERT, UPDATE, IF, loops), so any logic is possible. The cost is that the table variable and function boundary hide the real row count from the optimizer, which can pick poor join strategies when the result is large.
हिंदी: Table variable में कोई भी logic चल सकता है, पर optimizer को असली row count नहीं पता, इसलिए बड़े results पर plan खराब हो सकता है।

---

## ⚡ Alternative Solution

```sql
-- Same result as an inline TVF: single SELECT, fully inlined, accurate statistics.
CREATE OR ALTER FUNCTION dbo.itvf_CustomerSummary (@CustomerId INT)
RETURNS TABLE
AS
RETURN
(
  SELECT CustomerId,
         COUNT(*) AS OrderCount,
         SUM(Amount - Discount) AS NetTotal,
         CASE WHEN SUM(Amount - Discount) >= 1000 THEN 'GOLD' ELSE 'SILVER' END AS Tier
  FROM dbo.Orders
  WHERE CustomerId = @CustomerId
  GROUP BY CustomerId
);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using a multi-statement TVF inside a CROSS APPLY over millions of customers
SELECT c.CustomerId, s.Tier
FROM dbo.Customers c CROSS APPLY dbo.mstvf_CustomerSummary(c.CustomerId) s;
-- function runs per row, with a fixed row estimate for each call.

-- ❌ Wrong: expecting indexes on the returned table (only inline constraints/PK are possible).
-- ❌ Wrong: assuming it is "just a view" -> it is a black box to the optimizer.
-- ✅ Prefer an inline TVF; use CASE/CTEs to express the logic as one statement.
```

---

## 🎯 Interview Tip (1 line)
Say: "Multi-statement TVFs are a last resort. I rewrite them as inline TVFs when the logic fits one SELECT; otherwise I consider a temp table in a stored procedure, which has real statistics. Row-estimate behaviour varies by version and compatibility level (interleaved execution from 2017), so I always check the actual execution plan."

---

## 🔗 Related Questions
→ Q089 (Inline TVF) | Q088 (Scalar UDF cost) | Q179 (CTE vs temp table vs table variable) | Q079 (Procedure vs function vs view) | Q109 (Statistics and cardinality)
