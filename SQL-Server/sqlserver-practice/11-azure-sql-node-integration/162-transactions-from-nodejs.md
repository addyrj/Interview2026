---

# Q162. Transactions from Node.js
# Category: AZURE SQL + NODE.JS INTEGRATION
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL/MySQL drivers use BEGIN/COMMIT on one client connection; same idea)

---

## ❓ Question
Implement a funds transfer from Express so that both updates commit together or neither does, with proper rollback on error. Show the T-SQL-only version (stored procedure) and the Node `mssql` version.

---

## 💡 Quick Concept (2 lines only)
A transaction must run on ONE connection; in `mssql` use `new sql.Transaction(pool)` and create every request from that transaction object. Rollback in `catch`, release always, and keep the transaction short.
हिंदी: Transaction एक ही connection पर चलता है। `mssql` में हर request `transaction` से बनाओ, error पर rollback करो और transaction छोटा रखो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================
CREATE TABLE dbo.Accounts (
  AccountId INT PRIMARY KEY,
  Balance   DECIMAL(12,2) NOT NULL CHECK (Balance >= 0)
);
INSERT INTO dbo.Accounts VALUES (1, 1000.00), (2, 500.00);
GO

CREATE OR ALTER PROCEDURE dbo.usp_Transfer @From INT, @To INT, @Amount DECIMAL(12,2)
AS
BEGIN
  SET NOCOUNT ON; SET XACT_ABORT ON;      -- any runtime error rolls the whole txn back
  BEGIN TRAN;
    UPDATE dbo.Accounts SET Balance = Balance - @Amount WHERE AccountId = @From;
    UPDATE dbo.Accounts SET Balance = Balance + @Amount WHERE AccountId = @To;
  COMMIT;
END;
GO

EXEC dbo.usp_Transfer @From = 1, @To = 2, @Amount = 200;
SELECT AccountId, Balance FROM dbo.Accounts ORDER BY AccountId;
/* EXPECTED OUTPUT (result derived from equivalent statements on SQLite; not executed on SQL Server)
AccountId  Balance
1          800.00
2          700.00
*/

EXEC dbo.usp_Transfer @From = 1, @To = 2, @Amount = 5000;   -- CHECK (Balance >= 0) is violated
-- The CHECK failure raises an error and the transaction is rolled back (XACT_ABORT ON);
-- balances stay 800 / 700 (SQLite confirmed the CHECK fails and rollback leaves 800/700).
-- Exact SQL Server error text/number: not verified here.
```

```js
async function transfer(from, to, amount) {
  const pool = await getPool();
  const tx = new sql.Transaction(pool);
  await tx.begin();                                   // optionally: tx.begin(sql.ISOLATION_LEVEL.READ_COMMITTED)
  try {
    await new sql.Request(tx).input('f', sql.Int, from).input('a', sql.Decimal(12, 2), amount)
      .query('UPDATE dbo.Accounts SET Balance = Balance - @a WHERE AccountId = @f');
    await new sql.Request(tx).input('t', sql.Int, to).input('a', sql.Decimal(12, 2), amount)
      .query('UPDATE dbo.Accounts SET Balance = Balance + @a WHERE AccountId = @t');
    await tx.commit();
  } catch (e) {
    try { await tx.rollback(); } catch (_) { /* already rolled back by the server */ }
    throw e;                                          // let withRetry (Q160) decide about retrying
  }
}
```

---

## 🔍 Why This Works (3 lines max)
Requests built from the transaction share its connection, so both UPDATEs are in one atomic unit; the CHECK constraint enforces the business rule inside the database. XACT_ABORT (or catching and rolling back) guarantees no half-applied transfer.
हिंदी: एक ही connection पर दोनों UPDATE = atomic। Error पर rollback; CHECK constraint rule database में enforce करता है।

---

## ⚡ Alternative Solution

```sql
-- Put the whole transaction in the procedure (one round trip) and just EXEC it from Node.
-- Also valid: a single atomic statement when possible (no multi-step txn needed):
UPDATE dbo.Accounts
SET Balance = Balance + CASE AccountId WHEN 1 THEN -200 WHEN 2 THEN 200 END
WHERE AccountId IN (1, 2);
```

---

## ⚠️ Common Mistake

```js
// ❌ Wrong: pool.request() inside the transaction -> uses a DIFFERENT connection, not part of the txn
await tx.begin(); await pool.request().query('UPDATE ...');   // autocommits separately!
// ❌ Wrong: no rollback/finally -> connection returns to pool with an open transaction (blocking!)
// ❌ Wrong: calling external HTTP APIs or waiting for user input while the transaction is open
// ❌ Wrong: retrying only one statement after a deadlock - retry the whole function (Q130, Q160)
```

---

## 🎯 Interview Tip (1 line)
Say: "Same connection, short transaction, rollback on every failure path, SET XACT_ABORT ON for server-side procs, constraints as the last line of defence, and an idempotency or retry strategy for deadlocks — and I often move multi-statement logic into a procedure to cut round trips and lock time."

---

## 🔗 Related Questions
→ Q072 (Procedures with transactions) | Q118 (BEGIN TRAN/COMMIT/ROLLBACK and XACT_ABORT) | Q130 (Retry for deadlock victims) | Q160 (Pooling and retries)
