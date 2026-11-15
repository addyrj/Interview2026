---

# Q114. Parameter Sniffing and Fixes
# Category: Indexes + Execution Plans
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL has no plan-per-parameter caching problem in the same way; PostgreSQL has a similar generic-vs-custom plan switch for prepared statements)

---

## ❓ Question
`EXEC GetOrdersByCustomer @CustomerId = 2` is fast, but after a plan recompile caused by a call with `@CustomerId = 1` (a customer with a huge number of orders) the same procedure is slow for everyone. Explain why and show 4 fixes.

---

## 💡 Quick Concept (2 lines only)
On first compile SQL Server "sniffs" the parameter value, builds a plan optimized for that value and caches it for all later calls. With skewed data, a plan good for a "big" value (scan) is bad for a "small" value (seek + lookup) and vice versa.
हिंदी: पहली बार जो parameter value आती है, उसी के हिसाब से plan बनता है और cache हो जाता है। Data skewed हो तो वही plan दूसरी values के लिए खराब निकलता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (skewed data: customer 1 has most orders)
-- ============================================

CREATE TABLE dbo.Orders (
    OrderId     INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId  INT           NOT NULL,
    Status      VARCHAR(20)   NOT NULL,
    Amount      DECIMAL(10,2) NOT NULL
);
CREATE INDEX IX_Orders_CustomerId ON dbo.Orders (CustomerId);
GO

-- Small demo data (11 rows). In real life think 5 million rows for customer 1.
INSERT INTO dbo.Orders (CustomerId, Status, Amount) VALUES
  (1,'Shipped',10),(1,'Shipped',10),(1,'Shipped',10),(1,'Shipped',10),(1,'Shipped',10),
  (1,'Shipped',10),(1,'Shipped',10),(1,'Shipped',10),(1,'Shipped',10),
  (2,'Shipped',10),(3,'Pending',10);

-- Show the skew
SELECT CustomerId, COUNT(*) AS cnt FROM dbo.Orders GROUP BY CustomerId ORDER BY CustomerId;
-- Result derived from equivalent query on SQLite; not executed on SQL Server:
-- CustomerId | cnt
-- 1          | 9
-- 2          | 1
-- 3          | 1
GO

CREATE PROCEDURE dbo.GetOrdersByCustomer
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId;
END;
GO

-- ============================================
-- THE PROBLEM (behaviour per Microsoft docs; plans not shown)
-- ============================================
-- 1) Plan cache empty, EXEC ... @CustomerId = 1   -> optimizer sees "many rows" -> scan plan cached
-- 2) EXEC ... @CustomerId = 2                     -> reuses the scan plan (wasteful for 1 row)
-- The reverse also happens: seek + key lookup plan cached for a rare value, then used for the big customer
-- (millions of lookups).

-- ============================================
-- FIX 1: OPTION (RECOMPILE) — new plan per call (best for rare, heavy, skewed queries)
-- ============================================

ALTER PROCEDURE dbo.GetOrdersByCustomer
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
    OPTION (RECOMPILE);          -- costs CPU on every call; avoid on very hot procs
END;
GO

-- ============================================
-- FIX 2: OPTIMIZE FOR UNKNOWN — plan from average density, not the sniffed value
-- ============================================

ALTER PROCEDURE dbo.GetOrdersByCustomer
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
    OPTION (OPTIMIZE FOR (@CustomerId UNKNOWN));   -- stable but "average" plan
END;
GO

-- ============================================
-- FIX 3: OPTIMIZE FOR a typical value
-- ============================================

ALTER PROCEDURE dbo.GetOrdersByCustomer
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
    OPTION (OPTIMIZE FOR (@CustomerId = 2));       -- plan tuned for the common small case
END;
GO

-- ============================================
-- FIX 4: branch to separate procedures/statements for big vs small
-- ============================================

ALTER PROCEDURE dbo.GetOrdersByCustomer
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    IF @CustomerId IN (SELECT CustomerId FROM dbo.BigCustomers)   -- tiny lookup table
        EXEC dbo.GetOrdersByCustomer_Big @CustomerId = @CustomerId;
    ELSE
        EXEC dbo.GetOrdersByCustomer_Small @CustomerId = @CustomerId;
END;
GO
-- Each child proc gets its own cached plan.
-- Other options: Query Store forced plan (Q113), plan guides, or the PSP optimization in SQL Server 2022
-- (compat level 160) which can keep multiple plans for one parameterized statement.
```

---

## 🔍 Why This Works (3 lines max)
RECOMPILE makes every execution compile with the real value, so no stale plan is reused. OPTIMIZE FOR UNKNOWN uses average statistics so the plan is "medium" for everyone. Splitting into branches gives each shape its own cached plan.
हिंदी: RECOMPILE = हर call पर नया plan। OPTIMIZE FOR UNKNOWN = average वाला plan। Branching = हर shape का अपना plan।

---

## ⚡ Alternative Solution

```sql
-- Local variable trick (old-school): hides the value from the optimizer, same effect as UNKNOWN
ALTER PROCEDURE dbo.GetOrdersByCustomer
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @LocalId INT = @CustomerId;
    SELECT OrderId, Status, Amount FROM dbo.Orders WHERE CustomerId = @LocalId;
END;
GO

-- Node.js: parameters via mssql are sent through sp_executesql/RPC, so sniffing applies there as well
-- const result = await pool.request().input('CustomerId', sql.Int, 2).execute('dbo.GetOrdersByCustomer');
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "fixing" it by clearing the whole plan cache in production
DBCC FREEPROCCACHE;   -- every query recompiles at once -> CPU spike

-- ✅ Evict just one plan, or use Query Store to force the good plan:
-- EXEC sys.sp_recompile N'dbo.GetOrdersByCustomer';   -- marks only that proc for recompile

-- ❌ Wrong: adding OPTION (RECOMPILE) to a proc called thousands of times per second
-- ✅ Reserve it for heavy, rare, skewed queries; for hot paths prefer branching or forcing a plan.

-- ❌ Wrong: blaming sniffing without proof
-- ✅ Compare "compiled value" vs "runtime value" in the actual execution plan (ParameterCompiledValue vs
--    ParameterRuntimeValue) and look for multiple plans in Query Store.
```

---

## 🎯 Interview Tip (1 line)
Say: "Sniffing is not a bug, it is usually good because plans are reused; it hurts with skewed data. I confirm by comparing compiled vs runtime parameter values, then pick the cheapest fix: RECOMPILE for rare heavy queries, branching or OPTIMIZE FOR for hot ones, or a Query Store forced plan as a stop-gap. On SQL Server 2022 I also check whether PSP optimization applies."

---

## 🔗 Related Questions
→ Q080 (recompile, plan caching and sniffing) | Q113 (Query Store) | Q151 (parameter sniffing deep-dive) | Q181 (what is parameter sniffing)
