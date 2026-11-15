---

# Q075. Calling a Procedure from Node.js (mssql)
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL (Node driver: `mssql` package on top of `tedious`)

---

## ❓ Question
From an Express route, call `dbo.usp_GetCustomerOrders @CustomerId, @MinAmount, @TotalRows OUTPUT`, read both the result set and the OUTPUT parameter and the RETURN value, use a shared connection pool, and handle SQL errors safely.

---

## 💡 Quick Concept (2 lines only)
Create ONE `ConnectionPool` at startup, then per request use `pool.request().input(...).output(...).execute('dbo.proc')` — `execute` sends an RPC call (parameterized, no SQL injection). Result: `recordset`, `recordsets`, `output`, `returnValue`, `rowsAffected`.
हिंदी: Pool एक बार बनाओ। `request().input().output().execute()` — parameters typed और safe। Result में `recordset`, `output`, `returnValue` मिलते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (T-SQL side)
-- ============================================

CREATE TABLE dbo.Orders (
  OrderId    INT           NOT NULL PRIMARY KEY,
  CustomerId INT           NOT NULL,
  Amount     DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders VALUES (1, 101, 250.00), (2, 101, 80.00), (3, 102, 1200.00), (7, 101, 560.00);
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetCustomerOrders
    @CustomerId INT,
    @MinAmount  DECIMAL(10,2) = 0,
    @TotalRows  INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT @TotalRows = COUNT(*) FROM dbo.Orders WHERE CustomerId = @CustomerId AND Amount >= @MinAmount;

    SELECT OrderId, Amount FROM dbo.Orders
    WHERE CustomerId = @CustomerId AND Amount >= @MinAmount
    ORDER BY OrderId;

    RETURN 0;   -- status code (0 = success by convention)
END;
GO

-- T-SQL equivalent of what Node does:
DECLARE @total INT, @rc INT;
EXEC @rc = dbo.usp_GetCustomerOrders @CustomerId = 101, @MinAmount = 100, @TotalRows = @total OUTPUT;
SELECT @rc AS ReturnCode, @total AS TotalRows;
-- Expected (hand-checked on the 4 sample rows; not executed on SQL Server):
-- result set: (1, 250.00), (7, 560.00)
-- ReturnCode = 0, TotalRows = 2
```

```javascript
// ============================================
// db.js  -- ONE pool for the whole process
// ============================================
const sql = require('mssql');

const config = {
  server: process.env.DB_SERVER,            // e.g. myserver.database.windows.net (Azure SQL)
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  options: { encrypt: true, trustServerCertificate: false },  // encrypt required for Azure SQL
  pool: { max: 10, min: 0, idleTimeoutMillis: 30000 },
};

const poolPromise = new sql.ConnectionPool(config).connect();   // reuse everywhere
module.exports = { sql, poolPromise };

// ============================================
// route.js
// ============================================
const { sql, poolPromise } = require('./db');

app.get('/customers/:id/orders', async (req, res, next) => {
  try {
    const pool = await poolPromise;
    const result = await pool.request()
      .input('CustomerId', sql.Int, Number(req.params.id))
      .input('MinAmount', sql.Decimal(10, 2), Number(req.query.min ?? 0))
      .output('TotalRows', sql.Int)
      .execute('dbo.usp_GetCustomerOrders');

    res.json({
      rows: result.recordset,                // first result set
      total: result.output.TotalRows,        // OUTPUT parameter
      status: result.returnValue,            // RETURN code
    });
  } catch (err) {
    // err.number = SQL Server error number, err.message, err.procName, err.lineNumber (tedious RequestError)
    next(err);
  }
});
// Node code is illustrative, not executed here (no SQL Server available).
```

---

## 🔍 Why This Works (3 lines max)
`execute()` uses the RPC protocol with typed parameters, so values never get concatenated into SQL text. A single pool avoids the cost of opening a connection per request (and exhausting Azure SQL connection limits), and OUTPUT/RETURN values come back on the same result object.
हिंदी: `execute()` = typed RPC call, injection नहीं। एक pool reuse करो; OUTPUT और RETURN उसी result में आते हैं।

---

## ⚡ Alternative Solution

```javascript
// Ad-hoc parameterized query (fine for simple reads, but plan-cache and permission model differ from procs):
const r = await pool.request()
  .input('cid', sql.Int, 101)
  .query('SELECT OrderId, Amount FROM dbo.Orders WHERE CustomerId = @cid');

// Transaction across several procedure calls from Node:
const tx = new sql.Transaction(pool);
await tx.begin();
try {
  await new sql.Request(tx).input('OrderId', sql.Int, 1).execute('dbo.usp_ShipOrder');
  await tx.commit();
} catch (e) { await tx.rollback(); throw e; }
```

---

## ⚠️ Common Mistake

```javascript
// ❌ Opening a new connection per request:  await sql.connect(config)  inside the handler -> pool churn.
// ❌ Building the call as a string: `EXEC dbo.usp_GetCustomerOrders ${req.params.id}`  -> SQL injection.
// ❌ Not declaring types (.input('x', value)) -> driver guesses type (e.g. NVARCHAR vs VARCHAR) and can
//    cause implicit conversion on an indexed VARCHAR column -> index scan instead of seek.
// ❌ Forgetting SET NOCOUNT ON in the procedure and reading result.rowsAffected expecting one number.
// ❌ Holding a Transaction open while awaiting an external HTTP call.
```

---

## 🎯 Interview Tip (1 line)
Say: "One pool per process, typed `.input()` parameters, `.execute()` for procs, errors surfaced with `err.number` and mapped to HTTP codes (for example 2627/2601 duplicate key to 409) — and I set `encrypt: true` plus a connection retry for Azure SQL transient faults." The two error numbers are well-known duplicate-key codes, but confirm in your own environment.

---

## 🔗 Related Questions
→ Q069 (Input and OUTPUT parameters) | Q070 (RETURN codes vs OUTPUT vs result sets) | Q074 (SET NOCOUNT ON) | Q076 (Table-valued parameters)
