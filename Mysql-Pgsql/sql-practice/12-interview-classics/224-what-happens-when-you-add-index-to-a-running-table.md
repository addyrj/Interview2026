---

# Q224. What Happens When You Add an Index to a Running Table?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
You must add an index to a 300,000-row (think: 300 million) production table that is serving traffic. What happens during the build in MySQL and PostgreSQL, which locks are taken, and how do you do it safely?

---

## 💡 Quick Concept (2 lines only)
MySQL InnoDB builds secondary indexes online (ALGORITHM=INPLACE, LOCK=NONE: reads and writes continue) but needs a brief exclusive metadata lock at start and end. PostgreSQL plain CREATE INDEX blocks writes for the whole build; CREATE INDEX CONCURRENTLY avoids that by scanning twice, at the cost of time and a possible INVALID index on failure.
हिंदी: MySQL में online build चलता है पर शुरू/अंत में छोटा metadata lock लगता है; PostgreSQL में सामान्य CREATE INDEX writes रोकता है, इसलिए CONCURRENTLY use करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP — MySQL 9.1 (300,000 rows)
-- ============================================

CREATE TABLE payments (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  account_id INT NOT NULL,
  amount     DECIMAL(10,2) NOT NULL,
  created_at DATETIME NOT NULL,
  memo       VARCHAR(100)
) ENGINE=InnoDB;

SET SESSION cte_max_recursion_depth = 300000;

INSERT INTO payments (account_id, amount, created_at, memo)
WITH RECURSIVE seq AS (SELECT 1 AS n UNION ALL SELECT n+1 FROM seq WHERE n < 300000)
SELECT n % 1000, n % 500, NOW(), CONCAT('m', n) FROM seq;

-- ============================================
-- SOLUTION — MySQL: ask explicitly for online DDL
-- ============================================

-- Step 1: state the algorithm and lock you require; MySQL errors out instead of silently locking
ALTER TABLE payments
  ADD INDEX idx_acct_created (account_id, created_at),
  ALGORITHM=INPLACE, LOCK=NONE;
-- Result: succeeded (about 0.2 s for 300k rows on this machine; scales with table size)

-- Step 2: what is NOT online (MySQL 9.1, verified error messages)
ALTER TABLE payments ADD FULLTEXT INDEX ft_memo (memo), ALGORITHM=INPLACE, LOCK=NONE;
-- ERROR 1846 (0A000): LOCK=NONE is not supported. Reason: Fulltext index creation requires a lock. Try LOCK=SHARED.

ALTER TABLE payments ADD INDEX idx_x (amount), ALGORITHM=COPY, LOCK=NONE;
-- ERROR 1846 (0A000): LOCK=NONE is not supported. Reason: COPY algorithm requires a lock. Try LOCK=SHARED.

ALTER TABLE payments ADD INDEX idx_c (created_at), ALGORITHM=INSTANT;
-- ERROR 1845 (0A000): ALGORITHM=INSTANT is not supported for this operation. Try ALGORITHM=COPY/INPLACE.
-- (INSTANT works for e.g. ADD COLUMN, not for building an index.)

-- Step 3: the metadata-lock trap (reproduced with two sessions)
-- Session A:  BEGIN; SELECT COUNT(*) FROM payments; SELECT SLEEP(6);   -- long open transaction
-- Session B:  ALTER TABLE payments ADD INDEX idx_memo (memo(20)), ALGORITHM=INPLACE, LOCK=NONE;
-- Session C:  SELECT id, state FROM information_schema.processlist WHERE info LIKE 'ALTER%';
-- Result:
-- id | state
-- ---+--------------------------------
-- 77 | Waiting for table metadata lock       <- ALTER is queued behind session A
-- While B waits, NEW queries on payments queue behind B too -> an apparent outage.
-- Once A commits, B runs and the index appears.

-- ============================================
-- POSTGRESQL (verified on PGlite)
-- ============================================

-- Plain CREATE INDEX takes SHARE lock: SELECT works, INSERT/UPDATE/DELETE wait until the build ends.
-- Safe way for live tables:
CREATE INDEX CONCURRENTLY idx_acct_created ON payments (account_id, created_at);

SELECT indexrelid::regclass AS idx, indisvalid
FROM pg_index WHERE indrelid = 'payments'::regclass ORDER BY 1;
-- Result:
-- idx              | indisvalid
-- -----------------+-----------
-- payments_pkey    | true
-- idx_acct_created | true

-- Failure mode: a build that fails leaves an INVALID index behind
CREATE UNIQUE INDEX CONCURRENTLY uq_acct ON payments (account_id);   -- account_id has duplicates
-- ERROR: could not create unique index "uq_acct"
SELECT indexrelid::regclass AS idx, indisvalid
FROM pg_index WHERE indrelid = 'payments'::regclass ORDER BY 1;
-- Result: payments_pkey true | idx_acct_created true | uq_acct FALSE   <- invalid, still maintained, costs writes
DROP INDEX CONCURRENTLY uq_acct;                                       -- clean up, then retry

-- Restriction: not allowed inside a transaction block (so most migration tools need a "no transaction" flag)
BEGIN;
CREATE INDEX CONCURRENTLY idx_in_tx ON payments (memo);
-- ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block
ROLLBACK;
```

---

## 🔍 Why This Works (3 lines max)
Online builds read the table while recording concurrent changes (InnoDB row log / PostgreSQL second snapshot pass) and merge them at the end, so writers are not blocked for the long scan — only for short lock hand-offs. Any long-running transaction can still stall the brief lock phase, which then queues every later query.
हिंदी: Build के दौरान बदलाव log होते रहते हैं और अंत में merge होते हैं; लंबी transaction metadata lock अटका सकती है।

---

## ⚡ Alternative Solution

```sql
-- Very large MySQL tables: external online-schema-change tools (not run here)
--   gh-ost / pt-online-schema-change  (shadow table + triggers/binlog + atomic rename)
--   throttle on replica lag; also helps when replicas replay a long ALTER serially.

-- MySQL: protect yourself from lock pile-ups
SET SESSION lock_wait_timeout = 5;     -- ALTER gives up quickly instead of blocking the queue
-- PostgreSQL equivalent
SET lock_timeout = '5s';

-- Check progress
--   PostgreSQL: SELECT * FROM pg_stat_progress_create_index;     (not run: PGlite is single-session)
--   MySQL: performance_schema.events_stages_current (stage/innodb/alter table (read PK and internal sorting))

-- PostgreSQL: CONCURRENTLY needs 2 table scans and waits for old transactions -> 2-3x slower than plain build
-- Disk: need temp space roughly equal to the new index size
-- Also: every extra index slows writes forever, so confirm benefit with EXPLAIN first (Q229).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: running plain CREATE INDEX on a busy PostgreSQL table in peak hours
--    -> all writers block for the full build time.
-- ❌ Wrong: not specifying ALGORITHM/LOCK in MySQL -> a surprising COPY/SHARED rebuild may be chosen silently.
-- ❌ Wrong: forgetting to check for INVALID indexes after a failed CONCURRENTLY run.
-- ❌ Wrong: running the ALTER while a forgotten long transaction (or idle-in-transaction session) is open.
-- ✅ Correct: off-peak, with lock timeouts, explicit ALGORITHM=INPLACE, LOCK=NONE (MySQL) or CONCURRENTLY (PG),
--    watch replica lag, and verify the index is valid and used.
```

---

## 🎯 Interview Tip (1 line)
Say: "I state ALGORITHM=INPLACE, LOCK=NONE in MySQL so it fails fast if it cannot be online, use CREATE INDEX CONCURRENTLY in Postgres and check for INVALID leftovers, set lock timeouts because a waiting DDL queues all later queries behind it, and for huge tables or replicas I use gh-ost/pt-osc."

---

## 🔗 Related Questions
→ Q220 (zero-downtime migration) | Q219 (blue-green DB deployment) | Q223 (B-Tree index) | Q229 (optimize slow query)
