---

# Q136. FOR UPDATE SKIP LOCKED — Queue Pattern
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL 9.5+) — MySQL run on 9.1.0 with two concurrent workers; PgSQL run on PGlite (syntax/result of one worker only)

---

## ❓ Question
Multiple workers poll a `jobs` table. How do you let each worker claim different jobs without blocking each other and without two workers taking the same job?

---

## 💡 Quick Concept (2 lines only)
`SELECT ... FOR UPDATE SKIP LOCKED` locks the rows it returns and silently skips rows already locked by other transactions. That turns a table into a safe concurrent work queue.
हिंदी: SKIP LOCKED दूसरे workers द्वारा lock की गई rows को छोड़कर आगे बढ़ जाता है, इसलिए हर worker को अलग job मिलती है और कोई इंतज़ार नहीं करता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL)
-- ============================================

CREATE TABLE jobs (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  payload    VARCHAR(100),
  status     VARCHAR(20) NOT NULL DEFAULT 'queued',
  locked_by  VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status_id (status, id)          -- so the claim query is an index range scan
);

INSERT INTO jobs (payload) VALUES
  ('email:1'), ('email:2'), ('email:3'), ('email:4');

-- ============================================
-- SOLUTION (MySQL 8.0+) - two sessions
-- ============================================

-- Worker 1:
BEGIN;
SELECT id, payload FROM jobs
WHERE status = 'queued'
ORDER BY id
LIMIT 2
FOR UPDATE SKIP LOCKED;                     -- locks jobs 1,2
-- ... do the work (keep it short) ...
UPDATE jobs SET status = 'done', locked_by = 'worker1' WHERE id IN (1, 2);
COMMIT;

-- Worker 2 (runs WHILE worker 1 still holds its locks):
BEGIN;
SELECT id, payload FROM jobs
WHERE status = 'queued'
ORDER BY id
LIMIT 2
FOR UPDATE SKIP LOCKED;                     -- skips 1,2 -> gets 3,4 immediately
ROLLBACK;

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0)
-- ============================================

-- worker1 gets: (1, email:1), (2, email:2)
-- worker2 gets: (3, email:3), (4, email:4)      <- no waiting, no overlap
-- Final table after worker1 commit: 1 done, 2 done, 3 queued, 4 queued

-- ============================================
-- PostgreSQL version: claim + mark in ONE atomic statement
-- ============================================

CREATE TABLE jobs (
  id        SERIAL PRIMARY KEY,
  payload   TEXT,
  status    TEXT NOT NULL DEFAULT 'queued',
  locked_by TEXT
);
INSERT INTO jobs (payload) VALUES ('email:1'),('email:2'),('email:3'),('email:4');
CREATE INDEX idx_jobs_queued ON jobs (id) WHERE status = 'queued';   -- partial index: stays tiny

WITH next_jobs AS (
  SELECT id FROM jobs
  WHERE status = 'queued'
  ORDER BY id
  LIMIT 2
  FOR UPDATE SKIP LOCKED
)
UPDATE jobs j
SET status = 'running', locked_by = 'worker1'
FROM next_jobs n
WHERE j.id = n.id
RETURNING j.id, j.payload, j.status;

-- Result (real PGlite):
-- id | payload | status
-- 1  | email:1 | running
-- 2  | email:2 | running
-- Remaining rows: 3 and 4 still 'queued'.
```

---

## 🔍 Why This Works (3 lines max)
Row locks are taken as rows are scanned; SKIP LOCKED makes the scan ignore rows that another transaction has locked instead of waiting. The claim + status update in one statement means a crashed worker's locks vanish on rollback and the job returns to the queue.
हिंदी: Scan के दौरान locked rows skip हो जाती हैं; और worker crash होने पर lock अपने आप छूट जाता है, तो job वापस queue में आ जाती है।

---

## ⚡ Alternative Solution

```sql
-- NOWAIT: fail immediately instead of waiting (real MySQL output):
BEGIN;
SELECT * FROM jobs WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR 3572 (HY000): Statement aborted because lock(s) could not be acquired
--                     immediately and NOWAIT is set.
-- PgSQL: ERROR: could not obtain lock on row in relation "jobs"

-- Plain FOR UPDATE (no SKIP LOCKED): worker 2 would BLOCK behind worker 1 and then
-- process the same now-'done' rows or time out - the throughput killer.

-- Lease-based variant (survives worker crash AFTER commit, not just before):
UPDATE jobs SET status = 'running', locked_by = 'w1', lease_until = NOW() + INTERVAL '5 minutes'
WHERE ... ;     -- a reaper resets expired leases back to 'queued'
-- (the lease_until column is not in the table above; add it if you use this pattern - not run)

-- Syntax support: MySQL 8.0+, PostgreSQL 9.5+; NOT in MySQL 5.7.
-- Dedicated brokers (SQS, RabbitMQ, Kafka) beat this at very high volume,
-- but SKIP LOCKED is great up to thousands of jobs/sec with one less moving part.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: SELECT then UPDATE without locking -> two workers read the same job
SELECT id FROM jobs WHERE status = 'queued' ORDER BY id LIMIT 1;   -- both get id=1
UPDATE jobs SET status = 'running' WHERE id = 1;                   -- duplicate processing

-- ❌ Wrong: holding the transaction open during the whole job (minutes)
-- Locks + pinned snapshot -> see Q135. Claim quickly (status='running'), commit,
-- do the work, then update status in a second short transaction.

-- ❌ Wrong: no index on (status, id) / partial index -> every poll scans the whole table.

-- ✅ Correct: claim with SKIP LOCKED, ORDER BY a stable key, LIMIT a small batch.
-- Note: SKIP LOCKED gives an inconsistent view by design - never use it for
-- reports or business queries, only for queues.
```

---

## 🎯 Interview Tip (1 line)
Say: "I'd implement a DB-backed queue with FOR UPDATE SKIP LOCKED plus a partial index on queued rows, claim in one short transaction, and add a lease/retry-count for crash recovery; I'd move to a real broker when throughput or fan-out demands it."

---

## 🔗 Related Questions
→ Q128 (FOR UPDATE vs FOR SHARE) | Q127 (Optimistic vs pessimistic locking) | Q135 (Long-running transactions) | Q137 (Advisory locks)
