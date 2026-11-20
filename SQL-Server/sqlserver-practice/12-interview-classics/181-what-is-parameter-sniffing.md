---

# Q181. What Is Parameter Sniffing
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL has a similar generic-vs-custom plan choice for prepared statements; MySQL has no plan cache, so it does not suffer this)

---

## ❓ Question
`usp_GetOrdersByStatus @Status` runs in 5 ms for 'Pending' but crawls for 'Shipped', and sometimes the reverse after a restart. What is parameter sniffing, why does it happen, and what are your fixes?

---

## 💡 Quick Concept (2 lines only)
When a procedure or parameterized query compiles, SQL Server "sniffs" the parameter value passed on that first call, builds a plan optimized for it, and caches it for every later call. Good when values are similar; bad when data is skewed, because a plan for a rare value is terrible for a common one (and vice versa).
हिंदी: पहली call की value देखकर plan बनता है और cache हो जाता है। Data skewed हो तो वही plan दूसरी value पर बहुत धीमा हो सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (skewed data: 99.9 percent Shipped, 0.1 percent Pending)
-- ============================================
CREATE TABLE dbo.Orders (
  OrderId INT IDENTITY(1,1) PRIMARY KEY,
  Status  VARCHAR(20)  NOT NULL,
  Notes   VARCHAR(200) NULL
);
CREATE INDEX IX_Orders_Status ON dbo.Orders (Status);

-- Simplified load: 9990 Shipped + 10 Pending
INSERT INTO dbo.Orders (Status)
SELECT TOP (9990) 'Shipped' FROM sys.all_objects a CROSS JOIN sys.all_objects b;
INSERT INTO dbo.Orders (Status)
SELECT TOP (10) 'Pending' FROM sys.all_objects;

SELECT Status, COUNT(*) AS Cnt FROM dbo.Orders GROUP BY Status ORDER BY Cnt DESC;
-- Result derived from equivalent counts on SQLite 3; not executed on SQL Server
-- Status  | Cnt
-- Shipped | 9990
-- Pending | 10
GO

CREATE PROCEDURE dbo.usp_GetOrdersByStatus @Status VARCHAR(20)
AS
BEGIN
  SET NOCOUNT ON;
  SELECT OrderId, Status, Notes FROM dbo.Orders WHERE Status = @Status;
END;
GO

-- ============================================
-- THE PROBLEM (behaviour per Microsoft docs; plans are not reproduced here)
-- ============================================
EXEC dbo.usp_GetOrdersByStatus @Status = 'Pending';   -- compiled first: index seek + key lookups looks best for 10 rows
EXEC dbo.usp_GetOrdersByStatus @Status = 'Shipped';   -- reuses that plan: ~9990 key lookups instead of one scan

-- ============================================
-- DIAGNOSE: compare the plan's "Parameter Compiled Value" with "Runtime Value"
-- in the actual execution plan properties; check Query Store for multiple plans / regressions (Q113).
-- ============================================

-- ============================================
-- FIXES (pick by situation)
-- ============================================
-- 1) Recompile every time: always right, costs CPU per call. Good for rare / report procedures.
ALTER PROCEDURE dbo.usp_GetOrdersByStatus @Status VARCHAR(20)
AS
BEGIN
  SET NOCOUNT ON;
  SELECT OrderId, Status, Notes FROM dbo.Orders WHERE Status = @Status OPTION (RECOMPILE);
END;
GO

-- 2) Average plan instead of a sniffed one:
--    ... OPTION (OPTIMIZE FOR UNKNOWN)     -- uses density statistics, no specific value
-- 3) Plan for a typical value:
--    ... OPTION (OPTIMIZE FOR (@Status = 'Shipped'))
-- 4) Split logic: a "rare value" branch and a "common value" branch calling different sub-procedures.
-- 5) Query Store hints (Azure SQL / SQL Server 2022) to add hints without changing code.
-- 6) SQL Server 2022 (compat level 160): Parameter Sensitive Plan optimization can keep multiple
--    plans for one query automatically for some patterns. Do not assume it fixes every case.
```

```javascript
// Node.js: parameterized calls are required anyway (also stops SQL injection) and they use plan caching
const res = await pool.request()
  .input('Status', sql.VarChar(20), 'Pending')    // match the column type: avoids implicit conversion
  .execute('dbo.usp_GetOrdersByStatus');
```

---

## 🔍 Why This Works (3 lines max)
Plan caching saves compile time, but the cached plan carries assumptions from the first value's row estimate. With skewed data those assumptions fail for other values: a seek plus lookups is great for 10 rows and awful for 9,990. OPTION (RECOMPILE) or OPTIMIZE FOR change which values the optimizer is allowed to rely on.
हिंदी: Plan cache compile time बचाता है, पर पहली value की assumptions साथ ले आता है। Skew में वही problem है।

---

## ⚡ Alternative Solution

```sql
-- Local-variable trick (old-school, behaves like OPTIMIZE FOR UNKNOWN):
ALTER PROCEDURE dbo.usp_GetOrdersByStatus @Status VARCHAR(20)
AS
BEGIN
  DECLARE @S VARCHAR(20) = @Status;      -- optimizer cannot sniff a local variable
  SELECT OrderId, Status, Notes FROM dbo.Orders WHERE Status = @S;
END;
GO
-- Cleanup / emergency: clear one bad plan, not the whole cache
-- EXEC sp_recompile 'dbo.usp_GetOrdersByStatus';
-- Azure SQL / 2016+: ALTER DATABASE SCOPED CONFIGURATION CLEAR PROCEDURE_CACHE;
-- Do NOT run DBCC FREEPROCCACHE on a busy production server.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: calling parameter sniffing "a bug". It is a trade-off that helps most workloads.
-- ❌ Wrong: WITH RECOMPILE on every hot OLTP procedure: compile CPU adds up at high call rates.
-- ❌ Wrong: clearing the whole plan cache to "fix" it. The problem returns and you cause a compile storm.
-- ❌ Wrong: testing in SSMS with local variables (DECLARE @s ...) and expecting the procedure's plan:
--    local variables are not sniffed, so SSMS results differ from the app's.
-- ❌ Wrong: ignoring SET options differences: different SET ARITHABORT in SSMS vs the app can give
--    different cached plans, which is why "it is fast in SSMS but slow from the app".
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I confirm it with the actual plan's compiled vs runtime parameter values and with Query Store showing different plans for the same query. Then I choose the least invasive fix: a covering index so both plans are cheap, OPTION (RECOMPILE) for rare queries, OPTIMIZE FOR for known skew, branching procedures for extreme skew, or Query Store hints when I cannot change code. PSP on 2022 helps but I verify." Also say that deliberate skew awareness belongs in design reviews.

---

## 🔗 Related Questions
→ Q080 (recompile, plan caching and parameter sniffing) | Q114 (parameter sniffing and fixes) | Q151 (parameter sniffing deep-dive) | Q113 (Query Store basics) | Q109 (statistics and cardinality estimation)
