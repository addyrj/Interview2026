---

# Q171. CI/CD for Database Changes
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (pipeline ideas apply equally to MySQL/PostgreSQL)

---

## ❓ Question
Design a CI/CD pipeline that ships schema changes for an Azure SQL database together with a Node.js/Express app, without downtime and without a human running scripts in production. Show the pipeline, a safe migration, and a smoke test.

---

## 💡 Quick Concept (2 lines only)
Treat the schema as code: migrations in git, validated on a throwaway database in CI, deployed by a pipeline using a least-privilege identity, with expand/contract so old and new app versions both work during rollout.
हिंदी: Schema भी code है: git में migrations, CI में throwaway DB पर test, pipeline से deploy, expand/contract से zero downtime।

---

## ✅ Answer / Solution

```yaml
# .github/workflows/db-deploy.yml  (GitHub Actions; Azure DevOps has the same stages)
name: db-deploy
on:
  pull_request:
    paths: ['sql/**']
  push:
    branches: [main]
    paths: ['sql/**']

jobs:
  validate:                       # runs on every PR
    runs-on: ubuntu-latest
    services:
      mssql:
        image: mcr.microsoft.com/mssql/server:2022-latest
        env: { ACCEPT_EULA: 'Y', MSSQL_SA_PASSWORD: '${{ secrets.CI_SA_PWD }}' }
        ports: ['1433:1433']
    steps:
      - uses: actions/checkout@v4
      - name: Apply all migrations to empty DB
        run: flyway -url="jdbc:sqlserver://localhost:1433;trustServerCertificate=true" -user=sa -password="${{ secrets.CI_SA_PWD }}" -locations=filesystem:sql migrate
      - name: Validate checksums
        run: flyway -url=... -locations=filesystem:sql validate
      - name: Run integration tests
        run: npm ci && npm test

  deploy-staging:
    needs: validate
    if: github.ref == 'refs/heads/main'
    environment: staging
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: flyway -url="${{ secrets.STAGING_JDBC }}" -locations=filesystem:sql migrate

  deploy-prod:
    needs: deploy-staging
    environment: production        # required reviewers = manual approval gate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: flyway -url="${{ secrets.PROD_JDBC }}" -locations=filesystem:sql migrate
      # then deploy the Node app (App Service / container) AFTER the schema step
```

```sql
-- ============================================
-- Expand step (deploys BEFORE the new app version) - backward compatible
-- Verified by sqlglot (tsql) parse only; not executed on SQL Server
-- ============================================

ALTER TABLE dbo.Customers ADD FullName NVARCHAR(200) NULL;   -- new column, nullable
GO

-- Backfill in small batches (see Q145) so the log and locks stay small
DECLARE @Rows INT = 1;
WHILE @Rows > 0
BEGIN
    UPDATE TOP (5000) dbo.Customers
    SET FullName = CONCAT(FirstName, N' ', LastName)
    WHERE FullName IS NULL;
    SET @Rows = @@ROWCOUNT;
END;
GO

-- ============================================
-- Contract step (a LATER release, after no app version reads the old columns)
-- ============================================

ALTER TABLE dbo.Customers DROP COLUMN FirstName;
GO

-- ============================================
-- Post-deploy smoke test the pipeline can run (fails the job on error)
-- ============================================

IF OBJECT_ID('dbo.Customers') IS NULL
    THROW 50001, 'Smoke test failed: dbo.Customers missing', 1;
GO
-- Result: not executed on SQL Server; behaviour per Microsoft docs.
```

---

## 🔍 Why This Works (3 lines max)
CI applies every migration to an empty database, so broken or out-of-order scripts fail on the PR, not in production. Expand/contract means at every moment both the old and new app versions run correctly against the current schema. A protected environment adds approval and keeps the prod credentials out of developer hands.
हिंदी: CI में empty DB पर सब migrations चलते हैं। Expand/contract से old+new app दोनों चलते हैं। Prod approval gate के पीछे।

---

## ⚡ Alternative Solution

```text
-- State-based: build a DACPAC (SSDT / sqlproj), then
--   sqlpackage /Action:DeployReport  -> review the generated diff as a PR artifact
--   sqlpackage /Action:Publish       -> apply; set BlockOnPossibleDataLoss=true
-- Auth in pipeline: federated identity / managed identity to Azure SQL (Entra), no passwords
-- Extra safety: take a point-in-time marker (note the UTC time) before prod deploys so a
--   PITR restore target is known (Q166); for big changes test on a restored copy of prod.
```

---

## ⚠️ Common Mistake

```text
-- Wrong: deploying app and schema simultaneously, with the app needing the new column
--        -> old instances still running during rollout crash. Use expand/contract.
-- Wrong: running migrations from app startup on N instances (races, long locks).
-- Wrong: CI tests against SQLite/in-memory instead of SQL Server; T-SQL differences
--        (IDENTITY, DATETIME2, collations, MERGE, isolation) hide bugs. Use the real engine image.
-- Wrong: the pipeline login is db_owner/sysadmin-like and its secret lives in the repo.
-- Wrong: dropping columns in the same release that stops using them (no rollback path).
```

---

## 🎯 Interview Tip (1 line)
Say: "Schema changes are versioned, validated against a real SQL Server container on every PR, and deployed by a gated pipeline using managed identity. Every change is expand then contract across at least two releases, large backfills are batched, and I rehearse risky changes on a restored copy of production. My rollback story is roll forward, or PITR for catastrophic cases."

---

## 🔗 Related Questions
→ Q170 (migrations) | Q166 (backup and PITR) | Q163 (Entra / managed identity) | Q145 (batching) | Q191 (zero-downtime migration) | Q136 (least privilege)
