# Q070. RETURN Codes vs OUTPUT Params vs Result Sets
# Category: STORED PROCEDURES
# Difficulty: ⭐⭐ Medium
# DB: SQL Server / Azure SQL — RETURN <int> is T-SQL specific; PostgreSQL procedures cannot return a value this way, MySQL procedures use OUT params

---

## ❓ Question
A procedure `dbo.usp_CancelOrder` must tell the caller whether the cancel worked (success, not found, already shipped), give back the new status, and optionally return the updated order row. Which of RETURN code, OUTPUT parameter and result set do you use for what, and how does the Node.js `mssql` driver expose each one?

---

## 💡 Quick Concept (2 lines only)
Three channels: RETURN gives one INT status code (default 0), OUTPUT parameters give scalar values, and SELECT gives result sets. Use RETURN for status, OUTPUT for small scalars, result sets for data.
हिंदी: RETURN = सिर्फ़ INT status code, OUTPUT = छोटी scalar values, SELECT = असली data rows। तीनों का काम अलग है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Orders (
    OrderId    INT           NOT NULL PRIMARY KEY,
    CustomerId INT           NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL,
    Status     VARCHAR(20)   NOT NULL
);

INSERT INTO dbo.Orders (OrderId, CustomerId, Amount, Status) VALUES
 (1, 101, 500.00, 'Shipped'),
 (2, 101, 250.50, 'Pending'),
 (3, 102, 100.00, 'Pending');
GO

-- ============================================
-- PROCEDURE: all three channels
-- ============================================
CREATE PROCEDURE dbo.usp_CancelOrder
    @OrderId   INT,
    @NewStatus VARCHAR(20) OUTPUT          -- channel 2: scalar out
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CurrentStatus VARCHAR(20);
    SELECT @CurrentStatus = Status FROM dbo.Orders WHERE OrderId = @OrderId;

    IF @CurrentStatus IS NULL
    BEGIN
        SET @NewStatus = NULL;
        RETURN 1;                          -- channel 1: 1 = order not found
    END;

    IF @CurrentStatus = 'Shipped'
    BEGIN
        SET @NewStatus = @CurrentStatus;
        RETURN 2;                          -- 2 = already shipped, cannot cancel
    END;

    UPDATE dbo.Orders SET Status = 'Cancelled' WHERE OrderId = @OrderId;
    SET @NewStatus = 'Cancelled';

    SELECT OrderId, CustomerId, Amount, Status     -- channel 3: result set
    FROM dbo.Orders WHERE OrderId = @OrderId;

    RETURN 0;                              -- 0 = success (also the default if RETURN is omitted)
END;
GO

-- ============================================
-- CALLING IT
-- ============================================
DECLARE @rc INT, @st VARCHAR(20);

EXEC @rc = dbo.usp_CancelOrder @OrderId = 2,  @NewStatus = @st OUTPUT;
SELECT @rc AS ReturnCode, @st AS NewStatus;     -- 0, Cancelled   (+ one result-set row for order 2)

EXEC @rc = dbo.usp_CancelOrder @OrderId = 1,  @NewStatus = @st OUTPUT;
SELECT @rc AS ReturnCode, @st AS NewStatus;     -- 2, Shipped

EXEC @rc = dbo.usp_CancelOrder @OrderId = 99, @NewStatus = @st OUTPUT;
SELECT @rc AS ReturnCode, @st AS NewStatus;     -- 1, NULL

-- EXPECTED OUTPUT: derived by hand from the procedure logic against the 3 sample rows
-- (order 2 is Pending -> cancelled; order 1 is Shipped -> code 2; order 99 does not exist -> code 1).
-- Not executed on SQL Server; no equivalent engine for T-SQL procedures.
```

```js
// ============================================
// NODE.JS (mssql) — how each channel appears (not executed here)
// ============================================
const result = await pool.request()
  .input('OrderId', sql.Int, 2)
  .output('NewStatus', sql.VarChar(20))
  .execute('dbo.usp_CancelOrder');

result.returnValue;     // 0   <- RETURN code
result.output;          // { NewStatus: 'Cancelled' }   <- OUTPUT params
result.recordset;       // [{ OrderId: 2, CustomerId: 101, Amount: 250.5, Status: 'Cancelled' }]  <- result set

if (result.returnValue === 1) throw new NotFoundError();
if (result.returnValue === 2) throw new ConflictError('already shipped');
```

---

## 🔍 Why This Works (3 lines max)
RETURN ends the procedure immediately and delivers a single INT that the caller captures with `EXEC @rc = ...`; it is meant for status, not data. OUTPUT parameters copy scalar values back, and every SELECT that is not an assignment streams a result set to the client. `mssql` maps these to `returnValue`, `output` and `recordset(s)`, so the API layer can translate codes into HTTP 404/409.
हिंदी: RETURN से procedure तुरंत ख़त्म होता है और INT code मिलता है। Data हमेशा result set से, छोटी values OUTPUT से।

---

## ⚡ Alternative Solution

```sql
-- Modern approach for business errors: THROW a custom error, let the driver raise it as an exception
-- (SQL Server 2012+; error numbers for THROW must be 50000 or higher)
IF @CurrentStatus = 'Shipped'
    THROW 50002, 'Order already shipped and cannot be cancelled.', 1;
-- Node.js: catch (err) { err.number === 50002 ... }
-- Trade-off: RETURN codes need the caller to check them every time; THROW cannot be silently ignored.
-- Not executed on SQL Server; behaviour per Microsoft docs.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ RETURN with a non-integer or a data value
RETURN 'Cancelled';       -- conversion error: RETURN only carries an INT   (use an OUTPUT parameter)
RETURN @TotalAmount;      -- 250.50 would be converted/truncated to an integer - never return data this way

-- ❌ Assuming RETURN 0 means "no error" for SQL errors: a failed statement does not automatically change the code.
--    Without TRY...CATCH or XACT_ABORT the procedure may keep running and still return 0.
-- ❌ Reserving system-like values: negative codes -1 to -99 are used by SQL Server itself (e.g. for failed procedures); use small positive codes
-- ❌ Ignoring the code in the caller: EXEC dbo.usp_CancelOrder ... with no @rc check
```

---

## 🎯 Interview Tip (1 line)
Say: "RETURN for a status code, OUTPUT for a few scalars like a new id, result sets for data — and for real failures I prefer TRY...CATCH with THROW so the Node.js layer gets an exception with a number instead of relying on every caller to check @rc."

---

## 🔗 Related Questions
→ Q068 (What is a stored procedure) | Q069 (Input and OUTPUT parameters) | Q073 (TRY...CATCH inside procedures) | Q075 (Calling a procedure from Node.js) | Q072 (Procedures with transactions)
