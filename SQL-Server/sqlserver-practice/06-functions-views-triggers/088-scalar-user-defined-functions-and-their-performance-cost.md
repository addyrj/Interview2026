---

# Q088. Scalar User-Defined Functions and Their Performance Cost
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL: stored functions behave similarly; PostgreSQL: SQL-language functions can be inlined by the planner)

---

## ❓ Question
Your team wrapped the net-amount formula (Amount - Discount) in a scalar UDF and a report over 20 million orders became slow. Why, and how do you fix it?

Table: Orders(OrderId, CustomerId, OrderDate, Amount, Discount).

---

## 💡 Quick Concept (2 lines only)
Before SQL Server 2019 a scalar UDF is invoked once per row, is opaque to the optimizer (bad estimates) and forces the whole query to run serially. SQL Server 2019 (compat level 150) can inline simple scalar UDFs; the safest fix is still an inline TVF, a computed column or writing the expression inline.
हिंदी: Scalar UDF = हर row पर function call, optimizer को दिखता नहीं, query serial हो जाती है। 2019 में inlining मिली, पर inline TVF / computed column ज़्यादा safe।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  OrderDate  DATE NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL,
  Discount   DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Orders VALUES
  (1, 1, '2024-01-05', 500, 50),
  (2, 1, '2024-02-10', 300,  0),
  (3, 1, '2024-03-15', 700, 70),
  (4, 2, '2024-01-20', 200,  0),
  (5, 2, '2024-02-25', 900, 90);
GO

-- ============================================
-- SOLUTION
-- ============================================

-- The slow pattern
CREATE FUNCTION dbo.fn_NetAmount (@Amount DECIMAL(10,2), @Discount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
AS
BEGIN
  RETURN @Amount - @Discount;
END;
GO

SELECT OrderId, dbo.fn_NetAmount(Amount, Discount) AS NetAmount
FROM dbo.Orders
ORDER BY OrderId;

-- Fix 1: same logic inline (or a persisted computed column)
SELECT OrderId, Amount - Discount AS NetAmount FROM dbo.Orders ORDER BY OrderId;

ALTER TABLE dbo.Orders ADD NetAmount AS (Amount - Discount) PERSISTED;

-- EXPECTED OUTPUT (identical rows for UDF and inline; derived from the inline expression
-- on SQLite; the timing difference is NOT shown because it was not measured on SQL Server):
-- OrderId | NetAmount
-- 1       | 450.00
-- 2       | 300.00
-- 3       | 630.00
-- 4       | 200.00
-- 5       | 810.00

-- Check whether SQL Server 2019+ can inline your UDF:
SELECT OBJECT_NAME(object_id) AS FunctionName, is_inlineable
FROM sys.sql_modules
WHERE object_id = OBJECT_ID('dbo.fn_NetAmount');
-- Not executed on SQL Server; is_inlineable is available from SQL Server 2019 per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines + Hindi 1 line)
Without inlining, the UDF body is a separate invocation per row and the optimizer treats it as a black box, so it cannot parallelise or estimate cardinality well. An inline expression or computed column is part of the plan itself. Inlining (2019+) rewrites eligible UDFs into the query but has restrictions (for example, time-sensitive functions and some constructs block it).
हिंदी: Inline expression plan का हिस्सा बनता है, इसलिए parallelism और अच्छे estimates मिलते हैं। UDF per-row black box है।

---

## ⚡ Alternative Solution

```sql
-- Inline table-valued function (single SELECT) used with CROSS APPLY: always inlined, any version.
CREATE FUNCTION dbo.itvf_NetAmount (@Amount DECIMAL(10,2), @Discount DECIMAL(10,2))
RETURNS TABLE
AS RETURN (SELECT @Amount - @Discount AS NetAmount);
GO

SELECT o.OrderId, n.NetAmount
FROM dbo.Orders o
CROSS APPLY dbo.itvf_NetAmount(o.Amount, o.Discount) n;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: scalar UDF that reads a table, used in WHERE or SELECT over big tables
CREATE FUNCTION dbo.fn_CustomerTotal(@Id INT) RETURNS DECIMAL(12,2) AS
BEGIN RETURN (SELECT SUM(Amount) FROM dbo.Orders WHERE CustomerId = @Id); END;
-- SELECT ... WHERE dbo.fn_CustomerTotal(CustomerId) > 1000  -> hidden per-row query (N+1 inside the engine),
-- also non-SARGable. Also: SET STATISTICS shows UDF time hidden in the totals.
-- ✅ Rewrite as JOIN + GROUP BY or an inline TVF.
```

---

## 🎯 Interview Tip (1 line)
Say: "I avoid scalar UDFs that touch tables on large sets. On 2019+ I check sys.sql_modules.is_inlineable and compat level, but I still prefer inline TVFs or computed columns because they behave the same on every version; I prove it with SET STATISTICS TIME and the actual plan rather than assuming."

---

## 🔗 Related Questions
→ Q089 (Inline TVF) | Q090 (Multi-statement TVF) | Q029 (Computed columns) | Q108 (STATISTICS IO and TIME) | Q110 (SARGable predicates)
