---

# Q118. BEGIN TRAN, COMMIT, ROLLBACK and XACT_ABORT
# Category: Transactions + Locking
# Difficulty: ⭐⭐ Medium
# DB: SQL Server (PostgreSQL aborts the whole transaction on any error by default; MySQL needs START TRANSACTION)

---

## ❓ Question
How do explicit transactions work in T-SQL? What does `@@TRANCOUNT` show for nested BEGIN TRAN, what does ROLLBACK do, and why do you need `SET XACT_ABORT ON`?

---

## 💡 Quick Concept (2 lines only)
BEGIN TRAN increments `@@TRANCOUNT`; COMMIT decrements it (real commit only at 0); ROLLBACK undoes everything and sets it to 0. By default some errors only fail the statement and leave the transaction open; XACT_ABORT ON makes a run-time error roll back the whole transaction.
हिंदी: BEGIN TRAN से @@TRANCOUNT बढ़ता है, COMMIT से घटता है, ROLLBACK सब कुछ undo करके 0 कर देता है। XACT_ABORT ON = error आने पर पूरा transaction rollback।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server; behaviour per Microsoft docs. Outputs below are stated from documented semantics only.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.Payments (
    PaymentId  INT IDENTITY(1,1) PRIMARY KEY,
    OrderId    INT           NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL CHECK (Amount > 0)
);
GO

-- ============================================
-- SOLUTION: the safe template
-- ============================================

SET XACT_ABORT ON;               -- any run-time error aborts and rolls back the transaction

BEGIN TRY
    BEGIN TRANSACTION;
        INSERT INTO dbo.Payments (OrderId, Amount) VALUES (1, 250.00);
        INSERT INTO dbo.Payments (OrderId, Amount) VALUES (1, -5.00);   -- fails the CHECK constraint
    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    THROW;                       -- re-raise to the caller
END CATCH;

SELECT COUNT(*) AS PaymentRows FROM dbo.Payments;
-- Expected per documented behaviour: 0 (the first INSERT was rolled back too)

-- ============================================
-- @@TRANCOUNT with nested BEGIN TRAN
-- ============================================

BEGIN TRAN;                      -- @@TRANCOUNT = 1
    BEGIN TRAN;                  -- @@TRANCOUNT = 2 (still one physical transaction)
        SELECT @@TRANCOUNT AS DepthInside;     -- 2
    COMMIT;                      -- @@TRANCOUNT = 1 (nothing is committed yet!)
ROLLBACK;                        -- undoes ALL work, @@TRANCOUNT = 0
SELECT @@TRANCOUNT AS DepthAfter;              -- 0

-- ============================================
-- Check for an open transaction (e.g. in a CATCH block or a connection-pool cleanup)
-- ============================================

SELECT XACT_STATE() AS TxnState;
--  1 = active and committable, 0 = no transaction, -1 = doomed (only ROLLBACK is allowed)
```

---

## 🔍 Why This Works (3 lines max)
Nested BEGIN TRAN only counts depth; a single ROLLBACK anywhere undoes the outermost transaction, while COMMIT only commits at depth 0. XACT_ABORT ON converts statement-level errors into transaction-level rollbacks, so no half-applied work remains. TRY...CATCH plus a guarded ROLLBACK handles the doomed-transaction case.
हिंदी: Nested BEGIN TRAN सिर्फ गिनती है। Rollback हमेशा पूरा undo करता है। XACT_ABORT ON से error पर आधा काम नहीं बचता।

---

## ⚡ Alternative Solution

```sql
-- Node.js (mssql) - let the driver manage BEGIN/COMMIT/ROLLBACK
-- const tx = new sql.Transaction(pool);
-- await tx.begin();
-- try {
--   await new sql.Request(tx).input('o', sql.Int, 1).input('a', sql.Decimal(10,2), 250).query(
--     'INSERT INTO dbo.Payments (OrderId, Amount) VALUES (@o, @a)');
--   await tx.commit();
-- } catch (e) { await tx.rollback(); throw e; }
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: ROLLBACK without checking @@TRANCOUNT
BEGIN CATCH
    ROLLBACK TRANSACTION;        -- error "no corresponding BEGIN TRANSACTION" if none is open
END CATCH;
-- ✅ IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;

-- ❌ Wrong: thinking an inner COMMIT makes the inner work permanent
-- It does not: an outer ROLLBACK still undoes it.

-- ❌ Wrong: leaving a transaction open while calling an external API or waiting for user input
-- Locks are held for the whole time -> blocking for everyone else.
```

---

## 🎯 Interview Tip (1 line)
Say: "My template is SET XACT_ABORT ON, BEGIN TRY, BEGIN TRANSACTION, work, COMMIT, then in CATCH check XACT_STATE or @@TRANCOUNT before ROLLBACK and THROW. I keep transactions short and never nest them expecting partial rollback — for that I use savepoints."

---

## 🔗 Related Questions
→ Q072 (procedures with transactions) | Q073 (TRY...CATCH in procedures) | Q128 (savepoints and nested transactions) | Q132 (TRY...CATCH complete guide)
