---

# Q014. Variables, SET vs SELECT and Batches (GO)
# Category: T-SQL Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL uses @var session variables and SET/SELECT INTO; PostgreSQL needs DO blocks or psql variables)

---

## ❓ Question
Declare and use variables, explain the difference between `SET @v = ...` and `SELECT @v = ...` (no rows, many rows), what a batch is, why `GO` is not T-SQL, and why a variable declared before `GO` disappears after it.

---

## 💡 Quick Concept (2 lines only)
Local variables (`@name`) live only inside one batch. `GO` is a client-tool command (SSMS, sqlcmd) that splits the script into batches; the server never sees it. `SET` assigns one value (errors if a scalar subquery returns 2 rows), `SELECT @v = col` keeps the LAST row and leaves @v unchanged when no rows match.
हिंदी: Variable सिर्फ अपने batch में ज़िंदा रहता है। GO server का command नहीं, tool का है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Payments (
  PaymentId  INT           NOT NULL PRIMARY KEY,
  CustomerId INT           NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Payments (PaymentId, CustomerId, Amount) VALUES
  (1, 10, 100.00), (2, 10, 250.00), (3, 20, 75.50);
GO

-- ============================================
-- 1. Declare, assign, use (one batch)
-- ============================================

DECLARE @CustomerId INT = 10,
        @Total      DECIMAL(10,2),
        @Cnt        INT;

SET @Total = (SELECT SUM(Amount) FROM dbo.Payments WHERE CustomerId = @CustomerId);
SELECT @Cnt = COUNT(*) FROM dbo.Payments WHERE CustomerId = @CustomerId;   -- assign several at once with SELECT

SELECT @CustomerId AS CustomerId, @Total AS Total, @Cnt AS Cnt;
-- CustomerId | Total  | Cnt
-- 10         | 350.00 | 2
GO

-- ============================================
-- 2. SET vs SELECT when no row matches
-- ============================================

DECLARE @a DECIMAL(10,2) = -1, @b DECIMAL(10,2) = -1;

SET    @a = (SELECT Amount FROM dbo.Payments WHERE CustomerId = 999);   -- scalar subquery -> NULL
SELECT @b = Amount FROM dbo.Payments WHERE CustomerId = 999;            -- no rows -> @b NOT touched

SELECT @a AS FromSet, @b AS FromSelect;
-- FromSet | FromSelect
-- NULL    | -1.00

-- ============================================
-- 3. SELECT with many rows keeps the last one read (non-deterministic without ORDER BY)
-- ============================================

DECLARE @amt DECIMAL(10,2);
SELECT @amt = Amount FROM dbo.Payments WHERE CustomerId = 10 ORDER BY PaymentId;
SELECT @amt AS LastRowWins;      -- 250.00 (PaymentId 2 is processed last)

-- SET with a multi-row subquery raises an error instead:
--   SET @amt = (SELECT Amount FROM dbo.Payments WHERE CustomerId = 10);
--   -> "Subquery returned more than 1 value ..."

-- ============================================
-- 4. Variable scope ends at GO
-- ============================================
GO
PRINT @CustomerId;   -- error: Must declare the scalar variable "@CustomerId" (new batch)

-- Note: the sums/counts were checked on SQLite; the SET-vs-SELECT, batch-scope and error
-- behaviour is per Microsoft docs and not executed on any engine here. Not executed on SQL Server.
```

---

## 🔍 Why This Works (3 lines max)
The server compiles and executes one batch at a time, and variables belong to that batch's scope, so `GO` (which only tells SSMS/sqlcmd where to cut) resets them. `SELECT @v = ...` is a row-by-row assignment so it silently survives no-row and many-row results, while `SET` follows strict scalar rules.
हिंदी: SET सख्त है (NULL / error), SELECT चुपचाप आख़िरी row रख लेता है या कुछ नहीं बदलता।

---

## ⚡ Alternative Solution

```sql
-- Table variable (one batch only) and sqlcmd scripting variables
DECLARE @Ids TABLE (CustomerId INT PRIMARY KEY);
INSERT INTO @Ids VALUES (10), (20);
SELECT p.* FROM dbo.Payments p JOIN @Ids i ON i.CustomerId = p.CustomerId;

-- Persist values across batches: temp table (#t), SESSION_CONTEXT, or sqlcmd :setvar
EXEC sys.sp_set_session_context @key = N'tenant', @value = 42;
SELECT SESSION_CONTEXT(N'tenant');       -- 42 (SQL Server 2016+/Azure SQL)

-- From Node.js (mssql) there is NO GO: send each batch separately or use a stored procedure:
-- const r = await pool.request().input('CustomerId', sql.Int, 10)
--                     .query('SELECT SUM(Amount) AS Total FROM dbo.Payments WHERE CustomerId = @CustomerId');
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: putting GO inside application code / a stored procedure body
--    The server returns a syntax error: "Incorrect syntax near 'GO'". Split scripts in the client.

-- ❌ Wrong: SELECT @v = col for a lookup that may return no rows, then trusting @v
--    -> stale value from a previous assignment. ✅ SET @v = (SELECT ...) or check @@ROWCOUNT.

-- ❌ Wrong: declaring a variable twice in the same batch / using it in the next batch.

-- ❌ Wrong: DECLARE @s VARCHAR; (no length) -> length 1 in a declaration, 30 in a CAST. Always give a length.

-- ❌ Wrong: variable-driven filter like WHERE Col = @p OR @p IS NULL used with plan reuse without thinking about parameter sniffing.
```

---

## 🎯 Interview Tip (1 line)
Say: "I use SET for single deliberate assignments and SELECT when I assign several variables from one row, and I know SELECT leaves the variable untouched on no rows. GO is an SSMS/sqlcmd separator, not T-SQL, so my Node code sends batches or calls stored procedures instead."

---

## 🔗 Related Questions
→ Q015 (Control flow) | Q016 (Temp tables vs table variables vs CTEs) | Q017 (Dynamic SQL with sp_executesql) | Q020 (@@ROWCOUNT, @@ERROR) | Q075 (Calling a procedure from Node.js)
