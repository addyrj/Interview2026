---

# Q169. ORM Options — Prisma, TypeORM, Sequelize with SQL Server
# Category: Azure SQL + Node.js Integration
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL (Node.js ORMs; MySQL/PostgreSQL have first-class support in all three, SQL Server support is narrower)

---

## ❓ Question
Your Express API talks to Azure SQL. The team debates Prisma vs TypeORM vs Sequelize vs raw `mssql`. Show how each connects, how a paginated query looks, and how you still call a stored procedure when the ORM cannot express the query. Which would you pick and why?

---

## 💡 Quick Concept (2 lines only)
ORMs map tables to objects and generate parameterized SQL, but complex T-SQL (window functions, MERGE, OUTPUT, procs, hints) usually needs a raw-query escape hatch. Pick the ORM by team skills and schema ownership, and keep raw `mssql` for hot or complex paths.
हिंदी: ORM = objects से SQL generate। Complex T-SQL (procs, MERGE, OUTPUT) के लिए raw query escape hatch रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (the table all three ORMs map to)
-- Verified by sqlglot (tsql) parse only; not executed on SQL Server
-- ============================================

CREATE TABLE dbo.Customers (
    CustomerId INT IDENTITY(1,1) PRIMARY KEY,
    Name       NVARCHAR(100) NOT NULL,
    Email      NVARCHAR(255) NOT NULL UNIQUE,
    CreatedAt  DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE dbo.Orders (
    OrderId    INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL REFERENCES dbo.Customers(CustomerId),
    Amount     DECIMAL(10,2) NOT NULL,
    Status     VARCHAR(20)   NOT NULL DEFAULT 'Pending',
    CreatedAt  DATETIME2(0)  NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

-- Stored procedure for the escape-hatch case
CREATE PROCEDURE dbo.usp_GetCustomerOrders
    @CustomerId INT,
    @PageSize   INT = 20,
    @PageNo     INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    SELECT OrderId, Amount, Status, CreatedAt
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
    ORDER BY CreatedAt DESC, OrderId DESC
    OFFSET (@PageNo - 1) * @PageSize ROWS FETCH NEXT @PageSize ROWS ONLY;
END;
GO
```

```javascript
// ===== 1) Prisma (provider "sqlserver") =====
// schema.prisma:
//   datasource db { provider = "sqlserver"  url = env("DATABASE_URL") }
//   DATABASE_URL="sqlserver://myserver.database.windows.net:1433;database=shop;user=app;password=***;encrypt=true"
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

const orders = await prisma.orders.findMany({
  where: { CustomerId: 42 },
  orderBy: { CreatedAt: 'desc' },
  take: 20, skip: 0,
});
// Raw escape hatch (tagged template = parameterized, safe):
const rows = await prisma.$queryRaw`EXEC dbo.usp_GetCustomerOrders @CustomerId = ${42}`;

// ===== 2) TypeORM (type: 'mssql', uses tedious/mssql) =====
const ds = new DataSource({
  type: 'mssql', host: 'myserver.database.windows.net', port: 1433,
  username: 'app', password: process.env.DB_PWD, database: 'shop',
  options: { encrypt: true }, synchronize: false,       // never true in prod
  entities: [Order], migrations: ['dist/migrations/*.js'],
});
const rows2 = await ds.query('EXEC dbo.usp_GetCustomerOrders @0', [42]);

// ===== 3) Sequelize (dialect 'mssql') =====
const sequelize = new Sequelize('shop', 'app', process.env.DB_PWD, {
  dialect: 'mssql', host: 'myserver.database.windows.net',
  dialectOptions: { options: { encrypt: true } },
  pool: { max: 10, min: 0, idle: 10000 },
});
const [res] = await sequelize.query(
  'EXEC dbo.usp_GetCustomerOrders @CustomerId = :id',
  { replacements: { id: 42 } });
```

```text
-- Comparison (my summary; verify against current docs before quoting versions)
-- Prisma     : best typed client / DX; schema-first (prisma db pull for existing DB);
--              no stored-proc mapping, no TVP, limited T-SQL features -> use $queryRaw
-- TypeORM    : decorators, QueryBuilder, migrations; mssql driver is mature
-- Sequelize  : oldest; callback/promise API, weaker TypeScript story
-- Raw mssql  : full control (TVPs, bulk insert, output params), you write all SQL
```

---

## 🔍 Why This Works (3 lines max)
All three emit parameterized `sp_executesql` calls, so SQL injection is handled for normal queries. Anything beyond CRUD (TVPs, MERGE, OUTPUT, hints, bulk copy) falls out of ORM reach, which is why a raw path is mandatory. The pool settings still matter: each ORM wraps its own driver pool.
हिंदी: ORM CRUD के लिए अच्छा है; TVP/MERGE/bulk के लिए raw `mssql` चाहिए। Pool settings हर ORM में अलग देखो।

---

## ⚡ Alternative Solution

```javascript
// Raw mssql: no ORM, full T-SQL power (TVP, output params, bulk insert)
const sql = require('mssql');
const pool = await new sql.ConnectionPool({
  server: 'myserver.database.windows.net', database: 'shop',
  user: 'app', password: process.env.DB_PWD,
  options: { encrypt: true }, pool: { max: 10 },
}).connect();

const r = await pool.request()
  .input('CustomerId', sql.Int, 42)
  .input('PageNo', sql.Int, 1)
  .execute('dbo.usp_GetCustomerOrders');
console.log(r.recordset);
// Common hybrid: ORM for simple CRUD + migrations, raw mssql for reports and hot paths.
```

---

## ⚠️ Common Mistake

```text
-- Wrong: synchronize: true (TypeORM) or sequelize.sync({ alter: true }) against production
--        -> ORM diffs the model and may ALTER/DROP columns on a live Azure SQL DB.
--   Fix: migrations only (see Q170), synchronize off.

-- Wrong: string-concatenating into $queryRawUnsafe / sequelize.query(`... ${id}`)
--        -> SQL injection. Use tagged templates / replacements / bind parameters.

-- Wrong: N+1 from lazy relations (loop of findOne per order)
--   Fix: include/relations (one JOIN) or one IN (...) query. See Q152.

-- Wrong: assuming the ORM maps DATETIME2 / NVARCHAR the way you expect;
--        a JS string sent as NVARCHAR against a VARCHAR column can cause implicit
--        conversion and index scans. Check the generated parameter types (see Q143).
```

---

## 🎯 Interview Tip (1 line)
Say: "I treat the ORM as a productivity layer, not a replacement for T-SQL: CRUD and migrations through the ORM, but stored procedures, TVPs, MERGE and reporting through raw `mssql` with typed parameters. I check generated SQL and parameter types in Query Store, because ORM-generated NVARCHAR parameters against VARCHAR columns are a classic hidden scan. Schema changes go through migrations, never `synchronize`."

---

## 🔗 Related Questions
→ Q159 (mssql / tedious) | Q160 (pooling and retries) | Q161 (parameterized queries and procs) | Q170 (migrations) | Q152 (N+1) | Q143 (implicit conversions)
