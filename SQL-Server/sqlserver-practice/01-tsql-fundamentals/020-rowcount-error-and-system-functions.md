---

# Q020. @@ROWCOUNT, @@ERROR and System Functions
# Category: T-SQL FUNDAMENTALS
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (MySQL: ROW_COUNT(); PostgreSQL: GET DIAGNOSTICS / FOUND / ROW_COUNT in PL/pgSQL)

---

## ❓ Question
After an UPDATE, how do you know how many rows changed? Show why `@@ROWCOUNT` and `@@ERROR` must be captured immediately, when to use `ROWCOUNT_BIG()`, and name the system functions an interviewer expects you to know (`@@TRANCOUNT`, `SCOPE_IDENTITY()`, `@@VERSION`, `DB_NAME()`, `SYSDATETIME()`).

---

## 💡 Quick Concept (2 lines only)
`@@ROWCOUNT` holds the row count of the LAST statement and is overwritten by nearly every following statement (even IF and SET). `@@ERROR` holds the error number of the last statement only, 0 means success; modern code prefers TRY...CATCH.
हिंदी: @@ROWCOUNT और @@ERROR सिर्फ पिछले statement की value रखते हैं; अगला statement इन्हें बदल देता है। तुरंत किसी variable में save करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE Orders (
  OrderId INT PRIMARY KEY,
  Status  VARCHAR(20) NOT NULL,
  Amount  DECIMAL(10,2) NOT NULL
);

INSERT INTO Orders (OrderId, Status, Amount) VALUES
  (1, 'Pending', 500.00),
  (2, 'Pending', 300.00),
  (3, 'Shipped', 750.00);
GO

-- ============================================
-- SOLUTION: capture both in ONE statement
-- ============================================

DECLARE @Rows INT, @Err INT;

UPDATE Orders SET Status = 'Cancelled' WHERE Status = 'Pending';

SELECT @Rows = @@ROWCOUNT, @Err = @@ERROR;     -- one SELECT reads both before either is reset

IF @Rows = 0
    PRINT 'No rows matched';
ELSE
    PRINT CONCAT(@Rows, ' rows cancelled, error = ', @Err);

-- Output (Messages tab):
-- 2 rows cancelled, error = 0

-- Zero-row UPDATE
UPDATE Orders SET Status = 'X' WHERE OrderId = 999;
SELECT @@ROWCOUNT AS RowsAffected;
-- Output:
-- RowsAffected
-- 0

-- Counts (2 and 0) derived from the equivalent UPDATEs on SQLite 3.49 (cursor.rowcount);
-- @@ERROR / @@ROWCOUNT semantics are per Microsoft docs; not executed on SQL Server.

-- ============================================
-- Other system functions worth knowing
-- ============================================

SELECT
    @@TRANCOUNT      AS OpenTransactions,   -- 0 outside a transaction
    DB_NAME()        AS CurrentDb,
    SUSER_SNAME()    AS LoginName,
    SYSDATETIME()    AS ServerTimeHighPrecision,
    ROWCOUNT_BIG()   AS BigRowCount;        -- bigint version, for statements touching > 2 billion rows
-- (Values depend on the server and session; not shown.)
```

---

## 🔍 Why This Works (3 lines max)
`SELECT @Rows = @@ROWCOUNT, @Err = @@ERROR` runs as one statement, so both globals still describe the UPDATE when they are read. Later statements overwrite them (SET options, BEGIN TRAN, COMMIT and an IF test all reset @@ROWCOUNT to 0 per docs), so the safe habit is capture-first. `@@ROWCOUNT` is an INT and overflows past 2,147,483,647 rows, hence `ROWCOUNT_BIG()`.
हिंदी: दोनों को एक ही SELECT में पढ़ो ताकि UPDATE की value बची रहे। IF के बाद @@ROWCOUNT 0 हो जाता है। बहुत बड़ी tables के लिए ROWCOUNT_BIG()।

---

## ⚡ Alternative Solution

```sql
-- Modern approach: TRY...CATCH for errors, OUTPUT for the exact rows changed
BEGIN TRY
    UPDATE Orders
    SET Status = 'Cancelled'
    OUTPUT inserted.OrderId, deleted.Status AS OldStatus, inserted.Status AS NewStatus
    WHERE Status = 'Shipped';
END TRY
BEGIN CATCH
    SELECT ERROR_NUMBER() AS ErrNo, ERROR_MESSAGE() AS ErrMsg, ERROR_LINE() AS ErrLine;
END CATCH;
-- OUTPUT / TRY...CATCH have no SQLite equivalent; behaviour per Microsoft docs.

-- Identity of the last insert in the SAME scope (not @@IDENTITY - triggers can change that):
-- INSERT INTO Orders ... ; SELECT SCOPE_IDENTITY();
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: another statement between the DML and the read
UPDATE Orders SET Status = 'Cancelled' WHERE Status = 'Pending';
IF 1 = 1 SELECT 'doing something else';
SELECT @@ROWCOUNT;     -- no longer the UPDATE's count (it now reflects the intervening statements)
-- Rule: read @@ROWCOUNT on the very next statement.

-- ❌ Wrong: IF @@ERROR <> 0 after several statements - only the LAST statement's status is held
INSERT INTO Orders VALUES (1, 'Dup', 1);   -- primary key violation
INSERT INTO Orders VALUES (9, 'OK', 1);
IF @@ERROR <> 0 PRINT 'failed';            -- reports on the 2nd INSERT, error of the 1st is lost

-- ❌ Wrong: relying on SET NOCOUNT ON to remove @@ROWCOUNT - it only suppresses the "n rows affected"
--           message to the client; @@ROWCOUNT still works
```

---

## 🎯 Interview Tip (1 line)
Say: "I capture @@ROWCOUNT in the next statement, use ROWCOUNT_BIG when batching huge deletes, and for errors I use TRY...CATCH with THROW instead of @@ERROR checks. I also know SET NOCOUNT ON stops the rows-affected messages but does not change @@ROWCOUNT." Good detail for Node.js: `result.rowsAffected` in `mssql` mirrors these counts.

---

## 🔗 Related Questions
→ Q010 (INSERT, UPDATE, DELETE and OUTPUT) | Q013 (IDENTITY, SCOPE_IDENTITY) | Q074 (SET NOCOUNT ON) | Q132 (TRY...CATCH complete guide)
