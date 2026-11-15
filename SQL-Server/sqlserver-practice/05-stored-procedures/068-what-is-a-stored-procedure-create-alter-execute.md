# Q068. What Is a Stored Procedure — CREATE, ALTER, EXECUTE
# Category: STORED PROCEDURES
# Difficulty: ⭐ Easy
# DB: SQL Server / Azure SQL — MySQL has CREATE PROCEDURE + CALL; PostgreSQL has CREATE PROCEDURE + CALL (11+); neither has T-SQL's EXEC syntax

---

## ❓ Question
Create a stored procedure `dbo.usp_GetCustomerOrders` that returns the orders of one customer, newest first. Show how to execute it (positional, named, EXEC vs sp_executesql), how to change it without losing permissions (ALTER vs DROP/CREATE), and why a procedure is better than ad-hoc SQL from the application.

---

## 💡 Quick Concept (2 lines only)
A stored procedure is a named, saved batch of T-SQL stored in the database that you call with EXEC. Its plan is compiled and cached, it takes parameters, and permissions can be granted on the procedure instead of the tables.
हिंदी: Stored procedure = database में saved T-SQL batch जिसे EXEC से चलाते हैं। Parameters लेता है, plan cache होता है, और permission procedure पर दे सकते हैं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Customers (
    CustomerId INT         NOT NULL PRIMARY KEY,
    Name       VARCHAR(50) NOT NULL,
    City       VARCHAR(50) NOT NULL
);

CREATE TABLE dbo.Orders (
    OrderId    INT           NOT NULL PRIMARY KEY,
    CustomerId INT           NOT NULL REFERENCES dbo.Customers (CustomerId),
    OrderDate  DATE          NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL,
    Status     VARCHAR(20)   NOT NULL
);

INSERT INTO dbo.Customers (CustomerId, Name, City) VALUES
 (101, 'Asha', 'Mumbai'), (102, 'Ravi', 'Delhi'), (103, 'Meena', 'Pune');

INSERT INTO dbo.Orders (OrderId, CustomerId, OrderDate, Amount, Status) VALUES
 (1, 101, '2024-01-10', 500.00, 'Shipped'),
 (2, 101, '2024-02-10', 250.50, 'Pending'),
 (3, 102, '2024-01-15', 100.00, 'Pending');
GO

-- ============================================
-- CREATE
-- ============================================
CREATE PROCEDURE dbo.usp_GetCustomerOrders
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT OrderId, OrderDate, Amount, Status
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
    ORDER BY OrderDate DESC;
END;
GO

-- ============================================
-- EXECUTE
-- ============================================
EXEC dbo.usp_GetCustomerOrders 101;                    -- positional
EXEC dbo.usp_GetCustomerOrders @CustomerId = 101;      -- named (preferred: survives parameter reordering)

-- EXPECTED OUTPUT (result derived from equivalent SELECT on SQLite; procedure itself not executed on SQL Server):
-- OrderId | OrderDate  | Amount | Status
-- 2       | 2024-02-10 | 250.50 | Pending
-- 1       | 2024-01-10 | 500.00 | Shipped
GO

-- ============================================
-- ALTER (keeps permissions, dependencies, object id) — add an optional status filter
-- ============================================
ALTER PROCEDURE dbo.usp_GetCustomerOrders
    @CustomerId INT,
    @Status     VARCHAR(20) = NULL          -- default makes it optional: old callers keep working
AS
BEGIN
    SET NOCOUNT ON;

    SELECT OrderId, OrderDate, Amount, Status
    FROM dbo.Orders
    WHERE CustomerId = @CustomerId
      AND (@Status IS NULL OR Status = @Status)
    ORDER BY OrderDate DESC;
END;
GO

EXEC dbo.usp_GetCustomerOrders @CustomerId = 101, @Status = 'Pending';
-- 2 | 2024-02-10 | 250.50 | Pending            (equivalent query on SQLite)

-- CREATE OR ALTER (SQL Server 2016 SP1+ / Azure SQL) = idempotent deployment script
-- CREATE OR ALTER PROCEDURE dbo.usp_GetCustomerOrders ... AS ...

-- Inspect the definition
EXEC sp_helptext 'dbo.usp_GetCustomerOrders';
SELECT OBJECT_DEFINITION(OBJECT_ID('dbo.usp_GetCustomerOrders'));
```

---

## 🔍 Why This Works (3 lines max)
CREATE stores the batch as a database object; the first EXEC compiles an execution plan that is cached and reused for later calls with other parameter values. ALTER replaces the body in place, so GRANT EXECUTE permissions and dependencies survive, whereas DROP + CREATE loses them. SET NOCOUNT ON suppresses the "N rows affected" messages that otherwise add round-trip noise.
हिंदी: ALTER करने से permissions बनी रहती हैं, DROP+CREATE में चली जाती हैं। Default parameter से पुराने callers नहीं टूटते।

---

## ⚡ Alternative Solution

```sql
-- Ad-hoc parameterized SQL from the app (no procedure): also plan-cached, but logic lives in the app code
EXEC sp_executesql
     N'SELECT OrderId, OrderDate, Amount, Status FROM dbo.Orders WHERE CustomerId = @CustomerId ORDER BY OrderDate DESC',
     N'@CustomerId INT',
     @CustomerId = 101;

-- Inline table-valued function: composable (can JOIN/APPLY to it), unlike a procedure
CREATE FUNCTION dbo.fn_CustomerOrders (@CustomerId INT)
RETURNS TABLE
AS RETURN (SELECT OrderId, OrderDate, Amount, Status FROM dbo.Orders WHERE CustomerId = @CustomerId);
-- SELECT * FROM dbo.fn_CustomerOrders(101);
-- Not executed on SQL Server: no equivalent engine for T-SQL procedures/functions.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Naming procedures with the sp_ prefix: SQL Server searches the master database first for sp_* names
CREATE PROCEDURE dbo.sp_GetCustomerOrders ...      -- ✅ use usp_ / proc_ or a schema-based convention

-- ❌ Omitting the schema in EXEC GetCustomerOrders -> extra name resolution, possible ambiguity between schemas
-- ❌ DROP PROCEDURE then CREATE PROCEDURE in deployments -> GRANTs are lost
-- ❌ Building WHERE clauses with string concatenation of parameters inside a procedure -> SQL injection (see Q078)
-- ❌ SELECT * in a procedure: adding a column silently changes the result contract for the Node.js API
```

---

## 🎯 Interview Tip (1 line)
Say: "I deploy with CREATE OR ALTER, schema-qualify everything, SET NOCOUNT ON, give new parameters defaults so existing callers keep working, grant EXECUTE on the procedure (or schema) rather than table access, and keep procedures thin — business rules that need unit tests usually stay in the service layer."

---

## 🔗 Related Questions
→ Q069 (Input and OUTPUT parameters) | Q074 (SET NOCOUNT ON — why it matters) | Q079 (Procedure vs function vs view) | Q082 (Procedure versioning and deployment) | Q075 (Calling a procedure from Node.js)
