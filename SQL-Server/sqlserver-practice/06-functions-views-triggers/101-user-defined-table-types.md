---

# Q101. User-Defined Table Types
# Category: Functions, Views + Triggers
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL passes arrays/composite types or JSON; MySQL has no table-typed parameters)

---

## ❓ Question
Create an order with many line items in ONE round trip. Define a user-defined table type `dbo.OrderLineType (ProductId, Qty)`, a stored procedure that accepts it as a parameter, and show how Node.js (`mssql`) passes an array of lines.

---

## 💡 Quick Concept (2 lines only)
A user-defined table type (UDTT) is a reusable table schema you can declare as a variable or pass to a procedure as a table-valued parameter (TVP). TVPs are always `READONLY` inside the procedure.
हिंदी: UDTT = table जैसा parameter type। एक call में पूरी list भेजो, बार-बार proc call करने की ज़रूरत नहीं। Proc के अंदर यह READONLY होता है।

---

## ✅ Answer / Solution

```sql
-- Not executed on SQL Server (no instance available). Expected output derived from an
-- equivalent join/sum on SQLite; TVP behaviour per Microsoft docs.
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE Products (ProductId INT PRIMARY KEY, Name VARCHAR(50) NOT NULL, Price DECIMAL(10,2) NOT NULL);
INSERT INTO Products VALUES (10,'Keyboard',50.00),(20,'Mouse',20.00),(30,'Monitor',200.00);

CREATE TABLE Orders (OrderId INT IDENTITY(1,1) PRIMARY KEY, CustomerId INT NOT NULL, CreatedAt DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME());
CREATE TABLE OrderLines (
  OrderId INT NOT NULL REFERENCES Orders(OrderId),
  ProductId INT NOT NULL REFERENCES Products(ProductId),
  Qty INT NOT NULL CHECK (Qty > 0),
  UnitPrice DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (OrderId, ProductId)
);
GO

-- ============================================
-- 1) The table type
-- ============================================
CREATE TYPE dbo.OrderLineType AS TABLE (
  ProductId INT NOT NULL PRIMARY KEY,   -- PK rejects duplicate products in the payload
  Qty       INT NOT NULL CHECK (Qty > 0)
);
GO

-- ============================================
-- 2) Procedure taking the TVP
-- ============================================
CREATE PROCEDURE dbo.usp_CreateOrder
  @CustomerId INT,
  @Lines      dbo.OrderLineType READONLY,     -- READONLY is mandatory
  @OrderId    INT OUTPUT
AS
BEGIN
  SET NOCOUNT ON;
  SET XACT_ABORT ON;
  BEGIN TRAN;
    INSERT INTO Orders (CustomerId) VALUES (@CustomerId);
    SET @OrderId = SCOPE_IDENTITY();

    INSERT INTO OrderLines (OrderId, ProductId, Qty, UnitPrice)
    SELECT @OrderId, l.ProductId, l.Qty, p.Price
    FROM @Lines l
    JOIN Products p ON p.ProductId = l.ProductId;
  COMMIT;
END
GO

-- ============================================
-- 3) Call it from T-SQL
-- ============================================
DECLARE @Lines dbo.OrderLineType, @NewId INT;
INSERT INTO @Lines (ProductId, Qty) VALUES (10,2),(30,1),(20,3);
EXEC dbo.usp_CreateOrder @CustomerId = 1, @Lines = @Lines, @OrderId = @NewId OUTPUT;

SELECT l.ProductId, p.Name, l.Qty, l.UnitPrice * l.Qty AS LineTotal
FROM OrderLines l JOIN Products p ON p.ProductId = l.ProductId
WHERE l.OrderId = @NewId ORDER BY l.ProductId;

-- Output:
-- ProductId | Name     | Qty | LineTotal
-- 10        | Keyboard | 2   | 100.00
-- 20        | Mouse    | 3   | 60.00
-- 30        | Monitor  | 1   | 200.00
-- (order total = 360.00)
```

```js
// Node.js (mssql package) - rows go as ONE parameter
const sql = require('mssql');
const tvp = new sql.Table('dbo.OrderLineType');   // must match the type name
tvp.columns.add('ProductId', sql.Int);
tvp.columns.add('Qty', sql.Int);
[[10, 2], [30, 1], [20, 3]].forEach(r => tvp.rows.add(...r));

const result = await pool.request()
  .input('CustomerId', sql.Int, 1)
  .input('Lines', tvp)                              // TVP
  .output('OrderId', sql.Int)
  .execute('dbo.usp_CreateOrder');
console.log(result.output.OrderId);
```

---

## 🔍 Why This Works (3 lines max)
The whole list arrives as a typed, indexed rowset, so the INSERT...SELECT joins it to Products in one set-based statement instead of N procedure calls. The PRIMARY KEY on the type rejects duplicate products early, and the transaction makes header + lines atomic.
हिंदी: पूरा array एक typed table के रूप में जाता है, इसलिए एक ही set-based INSERT चलता है। Type की PK duplicate lines रोकती है।

---

## ⚡ Alternative Solution

```sql
-- JSON payload (OPENJSON, compat level 130+, SQL Server 2016+): no type to deploy
CREATE PROCEDURE dbo.usp_CreateOrderJson @CustomerId INT, @LinesJson NVARCHAR(MAX)
AS
BEGIN
  SET NOCOUNT ON;
  INSERT INTO Orders (CustomerId) VALUES (@CustomerId);
  DECLARE @OrderId INT = SCOPE_IDENTITY();
  INSERT INTO OrderLines (OrderId, ProductId, Qty, UnitPrice)
  SELECT @OrderId, j.ProductId, j.Qty, p.Price
  FROM OPENJSON(@LinesJson) WITH (ProductId INT '$.productId', Qty INT '$.qty') j
  JOIN Products p ON p.ProductId = j.ProductId;
END
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: no READONLY -> compile error; and trying to UPDATE/DELETE the TVP inside the proc
CREATE PROCEDURE dbo.usp_Bad @Lines dbo.OrderLineType AS SELECT 1;   -- error: must be READONLY
-- ✅ Copy to a #temp table first if you need to modify rows

-- ❌ Wrong: ALTER TYPE (not supported) - changing a type means dropping dependent procs, dropping and re-creating the type
-- ❌ Wrong: sending thousands of rows via TVP and expecting accurate row estimates - TVPs have no statistics,
--           so the optimizer guesses a low cardinality; copy to #temp for large payloads (see Q016, Q146)
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "TVPs are my choice for batch inputs from Node because `mssql` supports `sql.Table` natively and the type enforces shape. Trade-offs: types are schema objects so changing them is a deployment problem, there are no statistics so big payloads go to a #temp table first, and OPENJSON is the lower-ceremony alternative for small, nested payloads."

---

## 🔗 Related Questions
→ Q016 (Temp tables vs table variables) | Q075 (Calling a proc from Node.js) | Q076 (Table-valued parameters) | Q086 (Bulk insert and batching)
