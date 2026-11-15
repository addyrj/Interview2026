---

# Q082. Procedure Versioning and Deployment
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL (same ideas for MySQL/PostgreSQL migrations: Flyway, Liquibase, Sqitch)

---

## ❓ Question
How do you version and deploy stored procedures safely across dev/stage/prod without losing permissions or breaking the running Node.js app? Compare `CREATE OR ALTER`, `DROP/CREATE`, `ALTER`, a migration tool and a versioned-name approach (`usp_X_v2`).

---

## 💡 Quick Concept (2 lines only)
Keep procedure definitions in source control and deploy them as idempotent scripts (`CREATE OR ALTER`, SQL Server 2016 SP1+ / Azure SQL) or a database project/migration tool (DACPAC, Flyway, Liquibase). `ALTER`/`CREATE OR ALTER` keeps permissions; `DROP` + `CREATE` loses them.
हिंदी: Procedure code git में रखो और idempotent script (`CREATE OR ALTER`) से deploy करो। `DROP+CREATE` permissions खो देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT PRIMARY KEY,
  CustomerId INT NOT NULL,
  Status     VARCHAR(20) NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
GO

CREATE TABLE dbo.SchemaVersion (
  VersionId   INT IDENTITY(1,1) PRIMARY KEY,
  ScriptName  VARCHAR(200) NOT NULL UNIQUE,
  AppliedAt   DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- ============================================
-- SOLUTION: idempotent, re-runnable deployment script (V003__usp_GetOrders.sql)
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_GetOrders
    @CustomerId INT,
    @Status     VARCHAR(20) = NULL        -- v2: new OPTIONAL parameter = backward compatible with old callers
AS
BEGIN
    SET NOCOUNT ON;
    -- Version: 2 | Changed: optional @Status filter | Ticket: ORD-1234
    SELECT OrderId, CustomerId, Status, Amount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
      AND (@Status IS NULL OR Status = @Status);
END;
GO

GRANT EXECUTE ON dbo.usp_GetOrders TO public;   -- explicit grants are part of the script (still harmless to repeat)
GO

-- Track what ran (migration-style)
IF NOT EXISTS (SELECT 1 FROM dbo.SchemaVersion WHERE ScriptName = 'V003__usp_GetOrders.sql')
    INSERT INTO dbo.SchemaVersion (ScriptName) VALUES ('V003__usp_GetOrders.sql');
GO

SELECT ScriptName FROM dbo.SchemaVersion;
-- Expected: one row 'V003__usp_GetOrders.sql' (AppliedAt = deploy time). Not executed on SQL Server; trivial by inspection.
```

---

## 🔍 Why This Works (3 lines max)
`CREATE OR ALTER` makes the script safe to run on any environment regardless of whether the procedure exists, and it preserves existing GRANTs. Adding only optional parameters (with defaults) and keeping result-set columns stable means old Node.js code keeps working during a rolling deploy.
हिंदी: `CREATE OR ALTER` हर environment पर safe है और permissions बचाता है। नया parameter optional रखो ताकि पुराना app न टूटे।

---

## ⚡ Alternative Solution

```sql
-- Breaking change? Version the name and migrate callers, then drop the old one in a later release:
CREATE OR ALTER PROCEDURE dbo.usp_GetOrders_v2
    @CustomerId INT, @Status VARCHAR(20), @PageSize INT = 50      -- result set changed
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@PageSize) OrderId, CustomerId, Status, Amount
    FROM dbo.Orders WHERE CustomerId = @CustomerId AND Status = @Status ORDER BY OrderId;
END;
GO
-- Pre-2016 SP1 compatibility pattern:
-- IF OBJECT_ID(N'dbo.usp_GetOrders', N'P') IS NOT NULL DROP PROCEDURE dbo.usp_GetOrders;  -- loses GRANTs!
-- Tooling: SSDT/SqlPackage DACPAC (state-based), Flyway/Liquibase/DbUp (migration-based), GitHub Actions / Azure DevOps pipeline.
-- Inspect what is deployed: SELECT OBJECT_DEFINITION(OBJECT_ID(N'dbo.usp_GetOrders'));
```

---

## ⚠️ Common Mistake

```sql
-- ❌ DROP PROCEDURE + CREATE PROCEDURE in production: permissions vanish; callers get "permission denied"
--    in the gap, and a failed CREATE leaves NO procedure at all.
-- ❌ Editing procedures directly in prod via SSMS -> drift between environments, no history.
-- ❌ Changing result-set column order/names or removing a parameter in place -> breaks INSERT...EXEC consumers
--    and the Node.js code that reads columns by name.
-- ❌ Deploying schema changes and procedure changes in the wrong order (proc references a column not there yet).
--    Deferred name resolution lets the CREATE succeed and then fail at runtime.
-- ❌ WITH ENCRYPTION to "protect" code: easily reversed and blocks your own tooling.
```

---

## 🎯 Interview Tip (1 line)
Say: "Procedures live in git, deploy through a pipeline with idempotent `CREATE OR ALTER` scripts or a DACPAC, grants are in source control, changes are backward compatible (optional params, stable columns), and breaking changes get a versioned name with a deprecation window — plus a smoke test after deploy." Mention rollback = redeploy previous version script.

---

## 🔗 Related Questions
→ Q068 (What is a stored procedure) | Q081 (WITH EXECUTE AS and security) | Q028 (ALTER TABLE safely) | Q077 (INSERT...EXEC)
