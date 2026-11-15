---

# Q170. Migrations with Flyway / EF / dbmate
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL (all three tools support MySQL and PostgreSQL too; the SQL inside differs)

---

## ❓ Question
How do you version-control schema changes for an Azure SQL database used by a Node.js service? Show a Flyway-style versioned migration, the EF Core and dbmate equivalents, and how to make a migration safe to re-run and safe on a live table.

---

## 💡 Quick Concept (2 lines only)
A migration tool keeps ordered, immutable scripts and records which ones ran (Flyway: `flyway_schema_history`; EF: `__EFMigrationsHistory`; dbmate: `schema_migrations`). Never edit an applied script, add a new one.
हिंदी: Migration = ordered immutable scripts + history table। Applied script कभी edit मत करो, नया script लिखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- File: sql/V1__create_orders.sql   (Flyway naming: V<version>__<desc>.sql)
-- Verified by sqlglot (tsql) parse only; not executed on SQL Server
-- ============================================

CREATE TABLE dbo.Orders (
    OrderId    INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL,
    Status     VARCHAR(20) NOT NULL DEFAULT 'Pending'
);
GO

-- ============================================
-- File: sql/V2__add_orders_shipped_at.sql
-- Additive + nullable = metadata-only, safe on a live table
-- ============================================

ALTER TABLE dbo.Orders ADD ShippedAt DATETIME2(0) NULL;
GO

-- ============================================
-- File: sql/V3__index_orders_customer.sql
-- ONLINE = ON is supported on Azure SQL / Enterprise-class editions;
-- on editions without it the statement errors, so check your tier.
-- ============================================

CREATE NONCLUSTERED INDEX IX_Orders_CustomerId
    ON dbo.Orders (CustomerId) INCLUDE (Amount, Status)
    WITH (ONLINE = ON);
GO

-- ============================================
-- Idempotent guard (useful for dbmate / repeatable scripts)
-- ============================================

IF COL_LENGTH('dbo.Orders', 'ShippedAt') IS NULL
    ALTER TABLE dbo.Orders ADD ShippedAt DATETIME2(0) NULL;
GO

-- Repeatable-style object (Flyway R__ prefix: re-applied when checksum changes)
CREATE OR ALTER PROCEDURE dbo.usp_GetOrder @OrderId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, CustomerId, Amount, Status, ShippedAt
    FROM dbo.Orders WHERE OrderId = @OrderId;
END;
GO
-- CREATE OR ALTER requires SQL Server 2016 SP1+ (and Azure SQL).
-- Result: not executed on SQL Server; behaviour per Microsoft docs and Flyway docs.
```

```bash
# ----- Flyway (CLI / Docker) -----
flyway -url="jdbc:sqlserver://myserver.database.windows.net:1433;database=shop;encrypt=true" \
       -user=deployer -password="$DB_PWD" -locations=filesystem:sql migrate
flyway info       # shows pending/applied; flyway validate catches edited scripts (checksum)

# ----- EF Core migrations (.NET) -----
dotnet ef migrations add AddShippedAt
dotnet ef migrations script --idempotent -o deploy.sql   # reviewable script for the pipeline
dotnet ef database update

# ----- dbmate (single binary, plain SQL, good fit for Node teams) -----
export DATABASE_URL="sqlserver://deployer:***@myserver.database.windows.net:1433?database=shop"
dbmate new add_shipped_at       # creates db/migrations/<timestamp>_add_shipped_at.sql
dbmate up                       # file has "-- migrate:up" and "-- migrate:down" sections
```

---

## 🔍 Why This Works (3 lines max)
Each tool compares the scripts on disk with its history table and runs only the missing ones, in order, usually in a transaction per script (DDL transactionality in SQL Server is good, but some statements such as `CREATE INDEX ... ONLINE` or `ALTER DATABASE` have their own rules). Checksums detect someone editing history. Idempotent guards make a half-failed deploy re-runnable.
हिंदी: Tool history table से pending scripts चलाता है। Checksum edited script पकड़ता है। Idempotent guards से re-run safe।

---

## ⚡ Alternative Solution

```text
-- Declarative approach: SSDT / SqlPackage (DACPAC) diffs desired schema vs target
--   sqlpackage /Action:Publish /SourceFile:shop.dacpac /TargetConnectionString:...
-- Pros: state-based, drift detection. Cons: generated diff must be reviewed;
--   data migrations and renames still need hand-written pre/post-deploy scripts.
-- Node-native option: knex migrations (mssql client) / Prisma Migrate (shadow DB needed).
```

---

## ⚠️ Common Mistake

```sql
-- Wrong: editing V2 after it ran in prod -> checksum mismatch, deploy blocked (or worse, drift).
--   Fix: add V4 with the correction.

-- Wrong: NOT NULL column with default on a huge table in one step
ALTER TABLE dbo.Orders ADD Priority INT NOT NULL DEFAULT 0;
-- Behaviour differs by version/edition; on large tables prefer: add NULL column, backfill in
-- batches (Q145), then add the constraint. Test row counts and lock time in staging first.

-- Wrong: migrations run automatically by every app instance at startup (races, partial locks).
--   Fix: one dedicated pipeline step with a least-privilege deployer login (Q136).
```

---

## 🎯 Interview Tip (1 line)
Say: "Forward-only, immutable, versioned scripts run once by the pipeline under a deployer identity, never by app instances. I split risky changes expand/backfill/contract so deploys stay backward compatible with the previous app version, and I generate an idempotent script for review. Rollback is usually a new forward migration or a PITR restore, not a magic down script."

---

## 🔗 Related Questions
→ Q028 (ALTER TABLE safely) | Q145 (batching large updates) | Q171 (CI/CD for database changes) | Q191 (migrate 100M rows) | Q136 (least privilege)
