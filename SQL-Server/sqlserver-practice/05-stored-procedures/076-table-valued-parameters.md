---

# Q076. Table-Valued Parameters
# Category: Stored Procedures
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server / Azure SQL (MySQL: no TVP — pass JSON or temp table; PostgreSQL: pass an array/jsonb and unnest)

---

## ❓ Question
A Node.js service needs to fetch 500 orders by id (or bulk-update their status) in ONE procedure call. How do you pass a list of ids/rows into a stored procedure? Show a user-defined table type, a procedure with a `READONLY` table-valued parameter, and the `mssql` call.

---

## 💡 Quick Concept (2 lines only)
Create a table type (`CREATE TYPE ... AS TABLE`), declare the parameter as that type with `READONLY`, then JOIN to it like a normal table. It is strongly typed, avoids string-splitting and handles thousands of rows in one round trip.
हिंदी: `CREATE TYPE ... AS TABLE` बनाओ, procedure में `READONLY` parameter लो और उसे table की तरह JOIN करो। CSV string से बेहतर।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY,
  Status  VARCHAR(20) NOT NULL
);
INSERT INTO dbo.Orders VALUES (1,'Shipped'),(2,'Pending'),(3,'Shipped'),(4,'Cancelled'),(5,'Pending'),(6,'Shipped'),(7,'Shipped');
GO

CREATE TYPE dbo.OrderIdList AS TABLE (
  OrderId INT NOT NULL PRIMARY KEY      -- PK gives uniqueness + an index for the join
);
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_GetOrdersByIds
    @Ids dbo.OrderIdList READONLY       -- READONLY is mandatory; you cannot INSERT/UPDATE into @Ids
AS
BEGIN
    SET NOCOUNT ON;

    SELECT o.OrderId, o.Status
    FROM dbo.Orders AS o
    INNER JOIN @Ids AS i ON i.OrderId = o.OrderId
    ORDER BY o.OrderId;
END;
GO

DECLARE @list dbo.OrderIdList;
INSERT INTO @list (OrderId) VALUES (1), (4), (6);
EXEC dbo.usp_GetOrdersByIds @Ids = @list;
-- Expected (result derived from equivalent JOIN on SQLite; not executed on SQL Server):
-- OrderId | Status
-- 1       | Shipped
-- 4       | Cancelled
-- 6       | Shipped
```

```javascript
// Node.js (mssql): build the TVP and pass it
const { sql, poolPromise } = require('./db');

const tvp = new sql.Table('dbo.OrderIdList');          // must match the type name
tvp.columns.add('OrderId', sql.Int, { nullable: false });
[1, 4, 6].forEach(id => tvp.rows.add(id));

const pool = await poolPromise;
const result = await pool.request()
  .input('Ids', tvp)                                    // type inferred as TVP from the Table object
  .execute('dbo.usp_GetOrdersByIds');
console.log(result.recordset);
// Illustrative; not executed here.
```

---

## 🔍 Why This Works (3 lines max)
The table type defines a schema, so the client sends rows in a binary, typed stream and SQL Server materializes them as a table variable. Joining to it gives the optimizer a real row source instead of a parsed string, and one call replaces N round trips.
हिंदी: Rows typed होकर एक call में जाते हैं, और procedure उन्हें normal table की तरह JOIN करता है।

---

## ⚡ Alternative Solution

```sql
-- JSON array + OPENJSON (SQL Server 2016+, database compatibility level 130+): no type object needed
CREATE OR ALTER PROCEDURE dbo.usp_GetOrdersByIdsJson
    @IdsJson NVARCHAR(MAX)               -- e.g. N'[1,4,6]'
AS
BEGIN
    SET NOCOUNT ON;
    SELECT o.OrderId, o.Status
    FROM dbo.Orders AS o
    INNER JOIN OPENJSON(@IdsJson) WITH (OrderId INT '$') AS j ON j.OrderId = o.OrderId
    ORDER BY o.OrderId;
END;
GO
-- STRING_SPLIT(@csv, ',') (2016+, ordinal column needs 2022) also works but gives strings -> cast needed.
-- Rule of thumb: TVP for large/typed batches; JSON for flexible nested payloads.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting READONLY:   CREATE PROCEDURE p @Ids dbo.OrderIdList AS ...   -> compile error (must be READONLY).
-- ❌ Trying to modify the TVP inside the procedure (INSERT INTO @Ids ...) -> not allowed.
-- ❌ Using a TVP with huge row counts and expecting statistics: table-type variables have no column statistics, so
--    row-estimate can be poor (SQL Server 2019 adds deferred compilation for table variables to help). Copy into
--    a #temp table if the join is complex.
-- ❌ Passing ids as a comma-separated string and splitting with a WHILE loop.
-- ❌ Changing the table type later: you must drop dependent procedures first (types cannot be ALTERed).
```

---

## 🎯 Interview Tip (1 line)
Say: "For batch input from Node I use a table-valued parameter — typed, one round trip, joinable — and I copy it to a #temp table when the optimizer needs statistics; for loosely structured payloads I use OPENJSON." Mention that changing a type requires dropping dependent procs, so versioned type names help in deployments.

---

## 🔗 Related Questions
→ Q101 (User-defined table types) | Q086 (Bulk insert and batching procedure) | Q016 (Temp tables vs table variables) | Q075 (Calling from Node.js)
