---

# Q126. Queue Processing with READPAST
# Category: Transactions + Locking
# Difficulty: ⭐⭐⭐ Hard
# DB: SQL Server (PostgreSQL / MySQL 8: SELECT ... FOR UPDATE SKIP LOCKED)

---

## ❓ Question
Several worker processes pull jobs from a `JobQueue` table. How do you let each worker claim different jobs without blocking each other or processing a job twice, using `READPAST`, `UPDLOCK` and `OUTPUT`?

---

## 💡 Quick Concept (2 lines only)
Claim jobs with one atomic statement: `UPDATE TOP (n) ... WITH (ROWLOCK, READPAST, UPDLOCK) SET Status = 'Processing' OUTPUT inserted.*`. READPAST skips rows another worker has locked, so workers never wait for each other.
हिंदी: एक ही atomic UPDATE से job claim करो। READPAST दूसरे worker द्वारा locked rows छोड़ देता है, इसलिए workers एक-दूसरे का इंतज़ार नहीं करते और कोई job दो बार नहीं जाती।

---

## ✅ Answer / Solution

NOTE: not executed on SQL Server (concurrency + OUTPUT). The claim logic (oldest 2 pending rows, then status change) was checked with SQLite using LIMIT; READPAST skip behaviour is per Microsoft docs.

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE dbo.JobQueue (
    JobId     INT IDENTITY(1,1) PRIMARY KEY,
    Payload   VARCHAR(100) NOT NULL,
    Status    VARCHAR(20)  NOT NULL DEFAULT 'Pending',
    CreatedAt DATETIME2    NOT NULL DEFAULT SYSUTCDATETIME()
);
CREATE INDEX IX_JobQueue_Status_JobId ON dbo.JobQueue (Status, JobId);   -- worker seeks, not scans
GO

INSERT INTO dbo.JobQueue (Payload, Status) VALUES
  ('email-1', 'Pending'),
  ('email-2', 'Pending'),
  ('email-3', 'Pending'),
  ('email-4', 'Done'),
  ('email-5', 'Pending');
GO

-- ============================================
-- SOLUTION: claim up to 2 jobs atomically
-- ============================================

CREATE PROCEDURE dbo.ClaimJobs
    @BatchSize INT = 2
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH NextJobs AS (
        SELECT TOP (@BatchSize) JobId, Payload, Status
        FROM dbo.JobQueue WITH (ROWLOCK, READPAST, UPDLOCK)
        WHERE Status = 'Pending'
        ORDER BY JobId
    )
    UPDATE NextJobs
    SET Status = 'Processing'
    OUTPUT inserted.JobId, inserted.Payload;
END;
GO

EXEC dbo.ClaimJobs @BatchSize = 2;
-- Expected (worker 1, equivalent query on SQLite; not executed on SQL Server):
-- JobId | Payload
-- 1     | email-1
-- 2     | email-2

EXEC dbo.ClaimJobs @BatchSize = 2;   -- a second worker, even while the first transaction is still open
-- Expected: next unlocked pending rows
-- JobId | Payload
-- 3     | email-3
-- 5     | email-5

SELECT JobId, Status FROM dbo.JobQueue ORDER BY JobId;
-- JobId | Status
-- 1     | Processing
-- 2     | Processing
-- 3     | Processing   (after the second claim)
-- 4     | Done
-- 5     | Processing   (after the second claim)

-- When a worker finishes:
UPDATE dbo.JobQueue SET Status = 'Done' WHERE JobId = 1;
```

---

## 🔍 Why This Works (3 lines max)
Selecting and updating in one statement means a row is claimed under a single lock, so two workers cannot both read it as Pending. READPAST makes a worker skip rows locked by others instead of waiting, and the (Status, JobId) index lets each claim seek instead of scan. OUTPUT returns exactly the claimed rows without a second query.
हिंदी: Select और update एक ही statement में, इसलिए दो workers एक job नहीं ले सकते। READPAST locked rows skip करता है। OUTPUT से claimed rows सीधे मिल जाते हैं।

---

## ⚡ Alternative Solution

```sql
-- Node.js worker (mssql) calling the procedure in a loop:
-- const r = await pool.request().input('BatchSize', sql.Int, 10).execute('dbo.ClaimJobs');
-- for (const job of r.recordset) { await handle(job); await pool.request().input('id', sql.Int, job.JobId)
--   .query("UPDATE dbo.JobQueue SET Status='Done' WHERE JobId=@id"); }

-- For very high volume or ordering/retry semantics consider Azure Service Bus / Storage Queues instead of a table.
-- Add a "LockedAt" column and a sweeper that resets stale 'Processing' rows if a worker crashes.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: SELECT the next job, then UPDATE it in a second statement without locks
SELECT TOP (1) JobId FROM dbo.JobQueue WHERE Status = 'Pending' ORDER BY JobId;
UPDATE dbo.JobQueue SET Status = 'Processing' WHERE JobId = @id;
-- two workers read the same JobId -> duplicate processing.

-- ❌ Wrong: no index on (Status, JobId): READPAST + scan still locks/skips lots of rows and is slow.

-- ❌ Wrong: READPAST without an explicit transaction expectation - under autocommit the lock ends
--    when the claim statement ends; that is fine here only because Status = 'Processing' marks ownership.

-- ❌ Wrong: no recovery for crashed workers: jobs stay 'Processing' forever.
```

---

## 🎯 Interview Tip (1 line)
Say: "For table-based queues I use a single UPDATE TOP (n) with ROWLOCK, READPAST, UPDLOCK on a CTE ordered by id and OUTPUT the claimed rows; the status column is the ownership marker, and I add a stale-processing sweeper. For higher scale I move to a real message broker, since a table queue adds write load to the OLTP database."

---

## 🔗 Related Questions
→ Q010 (INSERT, UPDATE, DELETE and OUTPUT) | Q122 (locks) | Q125 (lock hints) | Q075 (calling a procedure from Node.js)
