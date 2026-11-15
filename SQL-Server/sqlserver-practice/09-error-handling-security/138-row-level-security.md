
---

# Q138. Row-Level Security
# Category: ERROR HANDLING + SECURITY
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server 2016+ and Azure SQL (PostgreSQL has CREATE POLICY ... USING; MySQL has no native RLS)

---

## ❓ Question
Sales reps should see only their own rows in `Sales`, managers see all. The app uses one shared database login (a connection pool), so the filter must use `SESSION_CONTEXT`. Implement a security policy with filter and block predicates.

---

## 💡 Quick Concept (2 lines only)
RLS = an inline table-valued function (predicate) + a SECURITY POLICY that applies it as FILTER (hides rows on read/update/delete) and BLOCK (rejects writes) predicates. The filtering is enforced by the engine on every query, whatever the application forgets.
हिंदी: RLS में एक inline function (predicate) और SECURITY POLICY होती है। FILTER पढ़ते वक़्त rows छुपाता है, BLOCK ग़लत write रोकता है; app भूल भी जाए तो engine लागू रखता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Sales (
  SaleId   INT IDENTITY(1,1) PRIMARY KEY,
  SalesRep NVARCHAR(50) NOT NULL,
  Amount   INT NOT NULL
);
INSERT INTO dbo.Sales (SalesRep, Amount)
VALUES (N'Amy', 100), (N'Amy', 250), (N'Raj', 400), (N'Raj', 50);
GO
CREATE SCHEMA Security;
GO

-- ============================================
-- SOLUTION
-- ============================================
-- 1) Predicate function: must be inline TVF with SCHEMABINDING
CREATE FUNCTION Security.fn_SalesFilter (@SalesRep AS NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
  SELECT 1 AS allowed
  WHERE  @SalesRep = CAST(SESSION_CONTEXT(N'RepName') AS NVARCHAR(50))   -- set by the app per request
     OR  CAST(SESSION_CONTEXT(N'IsManager') AS INT) = 1
     OR  USER_NAME() = N'dbo';                                           -- admins/migrations
GO

-- 2) Security policy
CREATE SECURITY POLICY Security.SalesPolicy
  ADD FILTER PREDICATE Security.fn_SalesFilter(SalesRep) ON dbo.Sales,   -- SELECT/UPDATE/DELETE visibility
  ADD BLOCK  PREDICATE Security.fn_SalesFilter(SalesRep) ON dbo.Sales AFTER INSERT   -- cannot insert for others
WITH (STATE = ON);
GO

-- 3) Per-request usage (the pooled login is not dbo)
EXEC sp_set_session_context @key = N'RepName', @value = N'Amy', @read_only = 1;
SELECT * FROM dbo.Sales;      -- only Amy's rows
```

```js
// Node.js (mssql): set the context on the SAME connection that runs the query
const tx = new sql.Transaction(pool); await tx.begin();
await new sql.Request(tx)
  .input('rep', sql.NVarChar(50), user.repName)
  .query("EXEC sp_set_session_context @key = N'RepName', @value = @rep, @read_only = 1");
const rows = await new sql.Request(tx).query('SELECT * FROM dbo.Sales');
await tx.commit();   // pooled connections are reused; @read_only = 1 prevents later overwriting on that session
```

```sql
-- EXPECTED OUTPUT
-- Policy objects and SESSION_CONTEXT are not executed on SQL Server. The filter result was derived from
-- an equivalent WHERE SalesRep = 'Amy' on SQLite:
-- SaleId | SalesRep | Amount
-- 1      | Amy      | 100
-- 2      | Amy      | 250
-- Raj's rows (400, 50) are hidden. Inserting (N'Raj', 10) as Amy is rejected by the BLOCK predicate.
```

---

## 🔍 Why This Works (3 lines max)
The engine rewrites every query on `dbo.Sales` to include the predicate, so access paths like direct SELECT, views and procedures are all covered. Block predicates stop a user writing rows they could not see.
हिंदी: Engine हर query में predicate अपने-आप जोड़ देता है, इसलिए कोई भी रास्ता हो filter बच नहीं सकता। BLOCK predicate ग़लत writes रोकता है।

---

## ⚡ Alternative Solution

```sql
-- Application-layer filtering: add WHERE SalesRep = @rep in every query/proc (simple, but one forgotten WHERE = leak).
-- Or per-tenant views: CREATE VIEW dbo.vMySales AS SELECT ... WHERE SalesRep = CAST(SESSION_CONTEXT(N'RepName') AS NVARCHAR(50));
-- Multi-tenant SaaS: TenantId column + RLS predicate on TenantId is the standard pattern.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: forgetting to set SESSION_CONTEXT on pooled connections -> NULL context = no rows (or, worse, a fallback leaks rows)
-- ❌ Wrong: not setting @read_only = 1, so SQL injection can overwrite the context and impersonate another rep
-- ❌ Wrong: non-SCHEMABINDING or multi-statement predicate function (not allowed / slow)
-- ❌ Wrong: relying on RLS as the only control: side-channel leaks through error messages or crafted predicates are documented;
--           combine with least privilege. Also, indexes on the filter column matter for performance.
```

---

## 🎯 Interview Tip (1 line)
Say: "For multi-tenant apps I put TenantId on every table and enforce it with RLS using SESSION_CONTEXT set per request with read_only, plus BLOCK predicates for writes. It is defence in depth beneath application checks, and I index the predicate column and test performance because the function runs per row."

---

## 🔗 Related Questions
→ Q136 (Least-privilege permissions) | Q139 (Dynamic data masking) | Q089 (Inline table-valued functions) | Q153 (Connection pooling with Node.js)
