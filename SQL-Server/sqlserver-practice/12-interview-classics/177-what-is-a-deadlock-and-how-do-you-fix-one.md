---

# Q177. What Is a Deadlock and How Do You Fix One
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (MySQL InnoDB and PostgreSQL also detect deadlocks and kill one transaction, but with different error codes and no deadlock-graph XML)

---

## ❓ Question
Two API requests each update the same two accounts in opposite order, and one of them fails with "Transaction was deadlocked ... chosen as the deadlock victim". Explain what a deadlock is, how SQL Server resolves it, how you find the cause, and how you fix and handle it in code.

---

## 💡 Quick Concept (2 lines only)
A deadlock is a cycle of waits: session A holds a lock B needs while B holds a lock A needs, so neither can ever proceed. SQL Server's lock monitor detects the cycle, rolls back the cheapest session (the victim) with error 1205, and the others continue.
हिंदी: Deadlock = गोल घेरे में इंतज़ार (A को B का lock चाहिए, B को A का)। SQL Server एक को victim बनाकर rollback करता है (error 1205)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- NOT EXECUTED ON SQL SERVER: deadlocks need two concurrent sessions, and no SQL Server
-- instance exists in the authoring environment. Behaviour per Microsoft docs; syntax parsed with sqlglot.
-- ============================================
CREATE TABLE dbo.Accounts (
  AccountId INT PRIMARY KEY,
  Balance   DECIMAL(12,2) NOT NULL
);
INSERT INTO dbo.Accounts VALUES (1, 1000.00), (2, 1000.00);

-- ---------- SESSION A ----------          -- ---------- SESSION B ----------
-- BEGIN TRAN;                              -- BEGIN TRAN;
-- UPDATE dbo.Accounts                      -- UPDATE dbo.Accounts
--    SET Balance = Balance - 10            --    SET Balance = Balance - 20
--  WHERE AccountId = 1;   -- X lock on 1   --  WHERE AccountId = 2;   -- X lock on 2
-- UPDATE dbo.Accounts                      -- UPDATE dbo.Accounts
--    SET Balance = Balance + 10            --    SET Balance = Balance + 20
--  WHERE AccountId = 2;   -- waits for B   --  WHERE AccountId = 1;   -- waits for A  => cycle
-- One session gets error 1205 and is rolled back; the other completes.

-- ============================================
-- FIX 1: same lock order everywhere (always lowest AccountId first)
-- ============================================
CREATE PROCEDURE dbo.usp_Transfer
  @FromId INT, @ToId INT, @Amount DECIMAL(12,2)
AS
BEGIN
  SET NOCOUNT ON;
  SET XACT_ABORT ON;
  BEGIN TRAN;
    -- touch rows in a deterministic order (lowest id first), independent of transfer direction
    DECLARE @Lo INT = CASE WHEN @FromId < @ToId THEN @FromId ELSE @ToId END;
    DECLARE @Hi INT = CASE WHEN @FromId < @ToId THEN @ToId ELSE @FromId END;

    UPDATE dbo.Accounts SET Balance = Balance WHERE AccountId = @Lo;   -- lock lower id first
    UPDATE dbo.Accounts SET Balance = Balance WHERE AccountId = @Hi;   -- then the higher id

    UPDATE dbo.Accounts SET Balance = Balance - @Amount WHERE AccountId = @FromId;
    UPDATE dbo.Accounts SET Balance = Balance + @Amount WHERE AccountId = @ToId;
  COMMIT;
END;
GO

-- ============================================
-- FIND THE CAUSE
-- ============================================
-- The built-in system_health Extended Events session records deadlock graphs (xml_deadlock_report).
-- The graph XML lists the victim, each process' statement, and the locked resources
-- (key / page / object). Open the XML as a graph in SSMS. Trace flag 1222 writes the same to the error log.
-- Read the graph, find the two statements, check their lock order and the indexes they use.
```

```javascript
// Node.js: treat 1205 as retryable (the whole transaction must be re-run from BEGIN)
async function runTransferWithRetry(pool, from, to, amt, tries = 3) {
  for (let i = 1; ; i++) {
    try {
      return await pool.request()
        .input('FromId', sql.Int, from).input('ToId', sql.Int, to)
        .input('Amount', sql.Decimal(12, 2), amt)
        .execute('dbo.usp_Transfer');
    } catch (e) {
      if (e.number !== 1205 || i >= tries) throw e;
      await new Promise(r => setTimeout(r, 50 * i + Math.random() * 50)); // jittered backoff
    }
  }
}
```

---

## 🔍 Why This Works (3 lines max)
A cycle needs opposite lock order. Acquiring locks in one consistent order removes the cycle, and short transactions plus supporting indexes shrink how long and how many locks are held. Retrying the victim is safe because SQL Server rolled the whole transaction back.
हिंदी: Lock order एक जैसा = cycle नहीं बनता। Transaction छोटी + सही index = कम locks। Victim को retry करो।

---

## ⚡ Alternative Solution

```sql
-- Reduce reader/writer deadlocks: READ_COMMITTED_SNAPSHOT (on by default in Azure SQL Database)
ALTER DATABASE ShopDb SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE;

-- Take the write lock first when you read-then-update (avoids the shared-to-exclusive conversion deadlock)
SELECT Balance FROM dbo.Accounts WITH (UPDLOCK, ROWLOCK) WHERE AccountId = 1;

-- Cheap to say, not a fix: SET DEADLOCK_PRIORITY LOW on batch jobs so they are the victims, not APIs.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: confusing blocking with deadlock. Blocking = A waits for B and B is running (resolves
--    itself). Deadlock = circular wait, never resolves without a victim. (Q123)
-- ❌ Wrong: fixing with NOLOCK. It hides read blocking but does nothing for write-write cycles (Q183).
-- ❌ Wrong: retrying only the failed statement. After 1205 the whole transaction is gone.
-- ❌ Wrong: holding a transaction open across an API call or user think time.
-- ❌ Wrong: missing index -> scan locks many rows -> more collisions. Add the index first.
```

---

## 🎯 Interview Tip (5+ YOE level)
Say: "I pull the deadlock graph from system_health, identify the two statements and the resources, then fix in this order: a covering index so each statement locks fewer rows, a consistent access order, shorter transactions, RCSI or snapshot for reader conflicts, and retry with jitter on error 1205 as the safety net. I also log every 1205 so frequency is visible." Mention that retries must be idempotent end to end.

---

## 🔗 Related Questions
→ Q116 (deadlock graphs and index fixes) | Q123 (blocking vs deadlock) | Q124 (deadlock prevention patterns) | Q130 (retry logic for deadlock victims) | Q122 (locks: shared, exclusive, update, intent)
