---

# Q080. Recompile, Plan Caching and Parameter Sniffing
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (MySQL has no cached-plan-per-procedure model like this; PostgreSQL has generic vs custom plans for prepared statements)

---

## ❓ Question
A procedure `dbo.usp_OrdersByStatus @Status` is fast for `'Cancelled'` (few rows) but very slow for `'Shipped'` (most rows) — only after the cache was cleared by a deployment. Explain parameter sniffing, how plan caching works for procedures, and list the fixes with their trade-offs.

---

## 💡 Quick Concept (2 lines only)
On first execution SQL Server compiles the procedure using the actual parameter values ("sniffing") and caches that plan for reuse. If later calls have very different data distribution the cached plan can be badly suited. Fixes: `OPTION (RECOMPILE)`, `OPTIMIZE FOR`, local variables, `OPTION (OPTIMIZE FOR UNKNOWN)`, separate procedures, or Query Store forcing.
हिंदी: पहली call के parameter पर plan बनकर cache होता है (sniffing)। बाद में data skew वाली value आए तो वही plan slow हो सकता है। Fix: RECOMPILE / OPTIMIZE FOR / Query Store।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (skewed data: most rows 'Shipped', very few 'Cancelled')
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT IDENTITY(1,1) PRIMARY KEY,
  CustomerId INT         NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
CREATE INDEX IX_Orders_Status ON dbo.Orders (Status) INCLUDE (CustomerId, Amount);
GO
-- (load e.g. 1,000,000 'Shipped' rows and 50 'Cancelled' rows)

CREATE OR ALTER PROCEDURE dbo.usp_OrdersByStatus
    @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE Status = @Status;
END;
GO

-- Scenario (described per Microsoft docs; plan shapes NOT executed here, no SQL Server available):
EXEC dbo.usp_OrdersByStatus 'Cancelled';  -- compiled first -> plan tuned for ~50 rows (index seek + lookups) is cached
EXEC dbo.usp_OrdersByStatus 'Shipped';    -- reuses that plan for ~1M rows -> can be much slower than a scan plan

-- ============================================
-- FIXES
-- ============================================

-- 1) Recompile every time (fresh plan per call; costs CPU; best for rarely-run/skew-heavy procs)
CREATE OR ALTER PROCEDURE dbo.usp_OrdersByStatus_Rc @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE Status = @Status
    OPTION (RECOMPILE);
END;
GO

-- 2) Plan for "average" distribution instead of the sniffed value
CREATE OR ALTER PROCEDURE dbo.usp_OrdersByStatus_Unk @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE Status = @Status
    OPTION (OPTIMIZE FOR UNKNOWN);
END;
GO

-- 3) Plan for a representative value
CREATE OR ALTER PROCEDURE dbo.usp_OrdersByStatus_Hint @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE Status = @Status
    OPTION (OPTIMIZE FOR (@Status = 'Shipped'));
END;
GO

-- Housekeeping commands
EXEC sys.sp_recompile N'dbo.usp_OrdersByStatus';          -- mark procedure for recompile on next run
-- ALTER DATABASE SCOPED CONFIGURATION CLEAR PROCEDURE_CACHE;   -- clears plan cache of the current database (2016+/Azure)
-- Query Store (2016+/Azure SQL): find the regressed query and "force plan" for the good plan -- see Q113/Q114.
```

---

## 🔍 Why This Works (3 lines max)
The optimizer chooses seek-plus-lookup for a selective value and scan for a non-selective one, and the choice is frozen in the cached plan. RECOMPILE re-chooses per call, OPTIMIZE FOR UNKNOWN uses density averages (a "middle" plan), and OPTIMIZE FOR (value) picks the plan you trust for the heavy case.
हिंदी: Optimizer selective value पर seek और heavy value पर scan चुनता है — पर plan cache में फंस जाता है। RECOMPILE हर बार नया plan बनाता है।

---

## ⚡ Alternative Solution

```sql
-- Branch on the known skew: separate statements => separate plans in one procedure
CREATE OR ALTER PROCEDURE dbo.usp_OrdersByStatus_Branch @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    IF @Status = 'Shipped'          -- the "big" value: scan-friendly
        SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE Status = 'Shipped';
    ELSE                            -- rare values: seek-friendly
        SELECT OrderId, CustomerId, Amount FROM dbo.Orders WHERE Status = @Status;
END;
GO
-- SQL Server 2022 (compat 160) adds Parameter Sensitive Plan (PSP) optimization that can keep multiple plans
-- automatically; Query Store hints (2022 / Azure SQL) let you add OPTION hints without changing code.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Blaming "bad statistics" and running UPDATE STATISTICS or clearing the whole cache in production.
--    Often the stats are fine; the plan is just wrong for THIS parameter. Compare actual vs estimated rows first.
-- ❌ Copying the parameter into a local variable (DECLARE @s = @Status) as a permanent fix:
--    it behaves like OPTIMIZE FOR UNKNOWN (average guess) which may be bad for both cases.
-- ❌ OPTION (RECOMPILE) on a procedure executed thousands of times per second -> CPU spike on compilation.
-- ❌ Testing only in SSMS: SET options (ARITHABORT) differ from the app connection, so SSMS gets a different cached
--    plan than Node.js -> "fast in SSMS, slow in app".
```

---

## 🎯 Interview Tip (1 line)
Say: "I confirm sniffing by comparing estimated vs actual rows and checking Query Store for plan regressions, then choose the least invasive fix — Query Store plan forcing, OPTIMIZE FOR, or RECOMPILE for infrequent skew-heavy procs — instead of clearing the cache." Mention SSMS-vs-app SET option differences.

---

## 🔗 Related Questions
→ Q071 (Catch-all queries) | Q109 (Statistics and cardinality) | Q113 (Query Store basics) | Q114 (Parameter sniffing and fixes)
