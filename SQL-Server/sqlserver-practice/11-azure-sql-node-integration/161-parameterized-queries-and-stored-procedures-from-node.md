---

# Q161. Parameterized Queries and Stored Procedures from Node
# Category: AZURE SQL + NODE.JS INTEGRATION
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (mssql uses @name parameters; mysql2/pg use ? or $1 placeholders)

---

## ❓ Question
From Express, fetch shipped orders for a customer safely (no SQL injection) and call a stored procedure with an input and an OUTPUT parameter. Show the SQL and the `mssql` code, and demonstrate why string concatenation is dangerous.

---

## 💡 Quick Concept (2 lines only)
`request.input(name, type, value)` sends values as typed RPC parameters (`sp_executesql`), never as part of the SQL text, so input cannot change the query structure. `request.execute('proc')` calls a stored procedure and `request.output()` captures OUTPUT parameters.
हिंदी: `input()` values को parameter बनाकर भेजता है, SQL text में नहीं जोड़ता, इसलिए injection नहीं होता। Proc के लिए `execute()`, OUTPUT के लिए `output()`।

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
  Total      DECIMAL(10,2) NOT NULL
);
INSERT INTO dbo.Orders VALUES
  (1, 42, 'Shipped', 250.00), (2, 42, 'Pending', 99.50),
  (3,  7, 'Shipped', 410.00), (4, 42, 'Shipped',  75.25);
GO

CREATE OR ALTER PROCEDURE dbo.usp_GetCustomerOrders
  @CustomerId INT,
  @Status     VARCHAR(20),
  @OrderCount INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;
  SELECT OrderId, Total FROM dbo.Orders
  WHERE CustomerId = @CustomerId AND Status = @Status
  ORDER BY OrderId;
  SET @OrderCount = @@ROWCOUNT;
END;
GO

DECLARE @n INT;
EXEC dbo.usp_GetCustomerOrders @CustomerId = 42, @Status = 'Shipped', @OrderCount = @n OUTPUT;
SELECT @n AS OrderCount;

/* EXPECTED OUTPUT (result derived from equivalent query on SQLite; proc/OUTPUT not executed on SQL Server)
OrderId  Total
1        250.00
4        75.25
-- OrderCount = 2
*/
```

```js
const { sql, getPool } = require('./db');

// 1) Parameterized ad-hoc query
app.get('/customers/:id/orders', async (req, res) => {
  const pool = await getPool();
  const r = await pool.request()
    .input('cid', sql.Int, Number(req.params.id))
    .input('status', sql.VarChar(20), req.query.status || 'Shipped')   // match column type -> no implicit conversion
    .query('SELECT OrderId, Total FROM dbo.Orders WHERE CustomerId = @cid AND Status = @status ORDER BY OrderId');
  res.json(r.recordset);
});

// 2) Stored procedure with OUTPUT
const r = await (await getPool()).request()
  .input('CustomerId', sql.Int, 42)
  .input('Status', sql.VarChar(20), 'Shipped')
  .output('OrderCount', sql.Int)
  .execute('dbo.usp_GetCustomerOrders');
// r.recordset -> rows, r.output.OrderCount -> 2, r.returnValue -> RETURN code
```

---

## 🔍 Why This Works (3 lines max)
Parameters travel separately from the statement text, so the server compiles one plan shape and treats values as data only. Declaring the exact type (`VarChar(20)`) avoids implicit conversions that can ruin index seeks (VARCHAR vs NVARCHAR).
हिंदी: Values और query अलग भेजे जाते हैं, इसलिए injection impossible। Column जैसा ही type दो वरना implicit conversion से index seek बेकार हो सकता है।

---

## ⚡ Alternative Solution

```js
// Tagged template (mssql supports it): values still become parameters
const r = await pool.query`SELECT OrderId, Total FROM dbo.Orders WHERE CustomerId = ${cid}`;
// Dynamic column/ORDER BY cannot be parameters -> whitelist them:
const SORT = { total: 'Total', id: 'OrderId' };
const col = SORT[req.query.sort] ?? 'OrderId';
```

---

## ⚠️ Common Mistake

```js
// ❌ Wrong: string concatenation
const q = `SELECT * FROM dbo.Orders WHERE CustomerId = 42 AND Status = '${req.query.status}'`;
// status = x' OR 1=1 --   -> WHERE ... Status = 'x' OR 1=1 --'   returns every row (comment kills the rest)
// Equivalent check on SQLite: the parameterised version with that value returns 0 rows ([]).
// ❌ Wrong: sql.NVarChar for a VARCHAR column (implicit conversion, possible scan)
// ❌ Wrong: ignoring r.returnValue / forgetting SET NOCOUNT ON affects row counts and chatty responses
```

---

## 🎯 Interview Tip (1 line)
Say: "Every value goes through `input()` with an explicit type matching the column; identifiers like sort columns are whitelisted; and stored procedures give me a narrow permission surface (GRANT EXECUTE only) plus a stable contract with OUTPUT parameters — that is injection defence in depth, not just escaping."

---

## 🔗 Related Questions
→ Q069 (Input and OUTPUT parameters) | Q075 (Calling a procedure from Node.js) | Q137 (SQL injection) | Q143 (Implicit conversions)
