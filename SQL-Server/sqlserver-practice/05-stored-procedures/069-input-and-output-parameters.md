# Q069. Input and OUTPUT Parameters
# Category: STORED PROCEDURES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL — PostgreSQL procedures use INOUT parameters; MySQL uses OUT/INOUT with session variables

---

## ❓ Question
Write `dbo.usp_GetCustomerOrderSummary` that takes a `@CustomerId` and returns, through OUTPUT parameters, the number of orders and the total amount. Show how to call it from T-SQL and from Node.js using the `mssql` package, and what happens for a customer with no orders.

---

## 💡 Quick Concept (2 lines only)
Input parameters pass values in; parameters declared with OUTPUT (or OUT) are assigned inside the procedure and handed back to the caller. The caller must also say OUTPUT when it executes the procedure.
हिंदी: OUTPUT parameter से procedure scalar values वापस देता है। Caller को भी EXEC में OUTPUT लिखना ज़रूरी है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (same tables as Q068)
-- ============================================
CREATE TABLE dbo.Customers (CustomerId INT NOT NULL PRIMARY KEY, Name VARCHAR(50) NOT NULL);
CREATE TABLE dbo.Orders (
    OrderId    INT           NOT NULL PRIMARY KEY,
    CustomerId INT           NOT NULL REFERENCES dbo.Customers (CustomerId),
    OrderDate  DATE          NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL,
    Status     VARCHAR(20)   NOT NULL
);

INSERT INTO dbo.Customers (CustomerId, Name) VALUES (101, 'Asha'), (102, 'Ravi'), (103, 'Meena');
INSERT INTO dbo.Orders (OrderId, CustomerId, OrderDate, Amount, Status) VALUES
 (1, 101, '2024-01-10', 500.00, 'Shipped'),
 (2, 101, '2024-02-10', 250.50, 'Pending'),
 (3, 102, '2024-01-15', 100.00, 'Pending');
GO

-- ============================================
-- PROCEDURE
-- ============================================
CREATE PROCEDURE dbo.usp_GetCustomerOrderSummary
    @CustomerId  INT,
    @OrderCount  INT           OUTPUT,
    @TotalAmount DECIMAL(12,2) OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT @OrderCount  = COUNT(*),
           @TotalAmount = ISNULL(SUM(Amount), 0)       -- SUM over no rows is NULL; return 0.00 instead
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId;
END;
GO

-- ============================================
-- CALL FROM T-SQL
-- ============================================
DECLARE @cnt INT, @total DECIMAL(12,2);

EXEC dbo.usp_GetCustomerOrderSummary
     @CustomerId  = 101,
     @OrderCount  = @cnt   OUTPUT,       -- OUTPUT keyword required here too
     @TotalAmount = @total OUTPUT;

SELECT @cnt AS OrderCount, @total AS TotalAmount;

-- EXPECTED OUTPUT (values derived from equivalent aggregate query on SQLite; procedure not executed on SQL Server):
-- customer 101 -> OrderCount = 2, TotalAmount = 750.50
-- customer 102 -> OrderCount = 1, TotalAmount = 100.00
-- customer 103 -> OrderCount = 0, TotalAmount = 0.00   (no orders: COUNT is 0, SUM was NULL -> ISNULL)
```

```js
// ============================================
// NODE.JS (mssql package) — not executed here
// ============================================
const sql = require('mssql');

async function getSummary(pool, customerId) {
  const result = await pool.request()
    .input('CustomerId', sql.Int, customerId)
    .output('OrderCount', sql.Int)
    .output('TotalAmount', sql.Decimal(12, 2))
    .execute('dbo.usp_GetCustomerOrderSummary');

  return result.output;   // { OrderCount: 2, TotalAmount: 750.5 }
}
```

---

## 🔍 Why This Works (3 lines max)
The procedure assigns to the parameters with SELECT @var = ..., and on return SQL Server copies their final values back into the caller's variables, but only for parameters flagged OUTPUT at both ends. ISNULL guards the empty-set case where SUM would return NULL. `mssql` declares the types with `.output()` and exposes the values as `result.output`.
हिंदी: Procedure के अंदर value assign होती है, caller के variable में वापस कॉपी होती है। Empty customer पर SUM = NULL, इसलिए ISNULL।

---

## ⚡ Alternative Solution

```sql
-- Return the summary as a one-row result set instead (easier for APIs, supports many columns):
CREATE PROCEDURE dbo.usp_GetCustomerOrderSummary_RS
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT COUNT(*) AS OrderCount, ISNULL(SUM(Amount), 0) AS TotalAmount
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId;
END;
GO
-- Node.js: const r = await pool.request().input('CustomerId', sql.Int, 101).execute('dbo.usp_GetCustomerOrderSummary_RS');
--          r.recordset[0]  -> { OrderCount: 2, TotalAmount: 750.5 }
-- Rule: OUTPUT for a few scalars / generated IDs, result sets for data.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Forgetting OUTPUT on the caller side: the variable stays NULL
DECLARE @cnt INT, @total DECIMAL(12,2);
EXEC dbo.usp_GetCustomerOrderSummary 101, @cnt, @total;      -- passes values in; nothing comes back
SELECT @cnt, @total;                                          -- NULL, NULL

-- ❌ Positional call with the wrong order of parameters -> use named parameters
-- ❌ Declaring @TotalAmount as DECIMAL (no precision) -> defaults to DECIMAL(18,0): 750.50 becomes 751
-- ❌ Using an OUTPUT param for a list of rows (it can only hold one scalar value)
-- ❌ In Node.js, forgetting `.output('Name', type)` -> the value is missing from result.output
```

---

## 🎯 Interview Tip (1 line)
Say: "OUTPUT is for a few scalars such as a row count or a newly generated id; anything tabular goes back as a result set. I always type decimals with precision and scale, use named parameters, and read result.output in mssql — and I remember that the caller has to repeat the OUTPUT keyword."

---

## 🔗 Related Questions
→ Q068 (What is a stored procedure) | Q070 (RETURN codes vs OUTPUT params vs result sets) | Q075 (Calling a procedure from Node.js) | Q013 (IDENTITY, SCOPE_IDENTITY, @@IDENTITY and SEQUENCE)
