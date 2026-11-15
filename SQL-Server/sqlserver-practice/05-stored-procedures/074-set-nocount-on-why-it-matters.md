---

# Q074. SET NOCOUNT ON — Why It Matters
# Category: Stored Procedures
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (not a concept in MySQL/PostgreSQL — they do not send per-statement "rows affected" messages mid-procedure)

---

## ❓ Question
Why does nearly every SQL Server stored procedure start with `SET NOCOUNT ON`? What exactly does it suppress, how can forgetting it break a Node.js (`mssql`/tedious) or ADO.NET client, and does it affect `@@ROWCOUNT`?

---

## 💡 Quick Concept (2 lines only)
By default SQL Server sends a "(N rows affected)" message (a DONE_IN_PROC token) after every statement inside a procedure. `SET NOCOUNT ON` stops those messages — less network chatter, and client libraries that read "rows affected" from the first message do not get confused by extra ones.
हिंदी: NOCOUNT ON = हर statement के बाद "N rows affected" message बंद। Network traffic कम और client confusion नहीं। `@@ROWCOUNT` फिर भी काम करता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.AuditLog (
  AuditId   INT IDENTITY(1,1) PRIMARY KEY,
  Action    VARCHAR(50)  NOT NULL,
  LoggedAt  DATETIME2(0) NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

CREATE TABLE dbo.Orders (
  OrderId INT PRIMARY KEY,
  Status  VARCHAR(20) NOT NULL
);
INSERT INTO dbo.Orders VALUES (1, 'Pending'), (2, 'Pending'), (3, 'Shipped');
GO

-- ============================================
-- SOLUTION
-- ============================================

CREATE OR ALTER PROCEDURE dbo.usp_ShipOrders_NoCount
AS
BEGIN
    SET NOCOUNT ON;                                   -- first line, always

    UPDATE dbo.Orders SET Status = 'Shipped' WHERE Status = 'Pending';
    DECLARE @n INT = @@ROWCOUNT;                      -- @@ROWCOUNT is NOT affected by NOCOUNT

    INSERT INTO dbo.AuditLog (Action) VALUES ('ShipOrders');

    SELECT @n AS RowsShipped;                         -- the only result the client should see
END;
GO

EXEC dbo.usp_ShipOrders_NoCount;
-- Expected: RowsShipped = 2   (hand-checked: two rows have Status = 'Pending'; not executed on SQL Server)
-- Messages tab: no "(2 rows affected)" / "(1 row affected)" lines for the UPDATE and INSERT.

-- Without SET NOCOUNT ON the same call emits additional DONE_IN_PROC messages for the UPDATE and the INSERT
-- before the SELECT result set (per Microsoft docs).
-- Node.js: with mssql, result.rowsAffected is an array with one entry per statement/result when counts are ON;
-- with NOCOUNT ON the array only reflects what the procedure explicitly returns.
```

---

## 🔍 Why This Works (3 lines max)
Each DML statement normally generates a small message packet; in a loop of 10,000 inserts that is 10,000 extra round-trip fragments. Turning it off cuts traffic and removes surprises for drivers that treat the first "done" token as the result. `@@ROWCOUNT` is still set — it is a session value, not a message.
हिंदी: हर statement का message network पर जाता है — बंद करने से performance बेहतर। `@@ROWCOUNT` unaffected रहता है।

---

## ⚡ Alternative Solution

```sql
-- Set it for the whole session/connection instead of every procedure (also covers ad-hoc batches):
SET NOCOUNT ON;

-- Server-wide default (affects every connection; changed via the "user options" setting, bit 512):
EXEC sys.sp_configure 'show advanced options', 1;  RECONFIGURE;
EXEC sys.sp_configure 'user options', 512;         RECONFIGURE;
-- Not recommended as a blanket change: it silently alters behaviour for legacy apps. Prefer per-procedure.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: put SET NOCOUNT ON after the first DML statement -> that statement still emits a count.
-- ❌ Wrong: believing NOCOUNT ON zeroes @@ROWCOUNT -- it does not.
-- ❌ Wrong: relying on "rows affected" from the driver to detect "nothing updated" in a procedure that has
--           NOCOUNT ON. Return the count yourself (OUTPUT param or SELECT @@ROWCOUNT) -- see Q069.
-- ❌ Wrong: forgetting it in procedures used by ORMs / ADO.NET SqlDataAdapter and seeing odd
--           "Concurrency violation: 0 records affected" or wrong affected-row counts.
```

---

## 🎯 Interview Tip (1 line)
Say: "`SET NOCOUNT ON` is the first line of every procedure and trigger — it removes the DONE_IN_PROC chatter, helps chatty loops, and avoids driver confusion — but `@@ROWCOUNT` still works, so I return counts explicitly when the app needs them." Bonus: mention that triggers with NOCOUNT off can break ORMs that read the affected-row count.

---

## 🔗 Related Questions
→ Q020 (@@ROWCOUNT, @@ERROR) | Q069 (Input and OUTPUT parameters) | Q075 (Calling from Node.js) | Q094 (AFTER triggers)
