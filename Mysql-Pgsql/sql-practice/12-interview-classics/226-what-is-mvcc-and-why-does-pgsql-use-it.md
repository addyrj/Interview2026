---

# Q226. What is MVCC and Why Does PgSQL Use It?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL InnoDB + PostgreSQL)

---

## ❓ Question
What is MVCC (Multi-Version Concurrency Control)? Why do PostgreSQL and InnoDB use it, how do they store old versions differently, and what is the cost (bloat, VACUUM)? Demonstrate snapshot reads and non-blocking readers.

---

## 💡 Quick Concept (2 lines only)
MVCC keeps several versions of a row so readers see a consistent snapshot while writers create new versions: readers never block writers and writers never block readers. PostgreSQL stores old versions in the table itself (cleaned by VACUUM); InnoDB keeps them in undo logs (purged in the background).
हिंदी: MVCC में row के कई versions रहते हैं; reader अपना snapshot देखता है, इसलिए read और write एक-दूसरे को block नहीं करते।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1 and PostgreSQL)
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  owner   VARCHAR(30) NOT NULL,
  balance DECIMAL(10,2) NOT NULL         -- PostgreSQL: NUMERIC(10,2)
);                                       -- MySQL: add ENGINE=InnoDB (default; MyISAM has no MVCC)

INSERT INTO accounts VALUES (1, 'Alice', 1000.00), (2, 'Bob', 500.00);

-- ============================================
-- SOLUTION 1 — MySQL: snapshot read (two sessions, timed with SLEEP; all output real)
-- ============================================

-- Default isolation: SELECT @@transaction_isolation;  ->  REPEATABLE-READ

-- Session A:
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;     -- 1000.00   (snapshot taken at this first read)

-- Session B (meanwhile, autocommit):
UPDATE accounts SET balance = balance - 300 WHERE id = 1;
SELECT balance FROM accounts WHERE id = 1;     -- 700.00    (B sees its own committed change)

-- Session A (still in the same transaction):
SELECT balance FROM accounts WHERE id = 1;     -- 1000.00   <- STILL the old version (undo log)
COMMIT;
SELECT balance FROM accounts WHERE id = 1;     -- 700.00    <- new transaction, new snapshot

-- Same test with READ COMMITTED in session A:
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- first read 1000.00, B updates to 700.00, second read in same txn = 700.00  (snapshot per statement)

-- Readers do not wait for writers:
-- Session W: START TRANSACTION; UPDATE accounts SET balance = balance + 1 WHERE id = 2;   (row locked, uncommitted)
-- Session R: SELECT balance FROM accounts WHERE id = 2;
-- Result: 500.00 returned immediately (old committed version from undo), no lock wait.

-- Old versions live in undo; SHOW ENGINE INNODB STATUS shows "History list length" = number of
-- undo records not yet purged (a long-open transaction makes it grow).

-- ============================================
-- SOLUTION 2 — PostgreSQL: the versions are visible in the table (PGlite + pageinspect)
-- ============================================

SELECT ctid, xmin, xmax, id, balance FROM accounts ORDER BY id;
-- Result:
-- ctid  | xmin | xmax | id | balance
-- (0,1) | 754  | 0    | 1  | 1000.00      <- xmin = txid that created the version
-- (0,2) | 754  | 0    | 2  | 500.00

UPDATE accounts SET balance = balance - 300 WHERE id = 1;

SELECT ctid, xmin, xmax, id, balance FROM accounts ORDER BY id;
-- Result:
-- (0,3) | 755 | 0 | 1 | 700.00            <- NEW physical tuple at slot 3
-- (0,2) | 754 | 0 | 2 | 500.00

SELECT lp, t_xmin, t_xmax, t_ctid FROM heap_page_items(get_raw_page('accounts', 0)) ORDER BY lp;
-- Result: the OLD version is still physically in the page
-- lp | t_xmin | t_xmax | t_ctid
-- 1  | 754    | 755    | (0,3)      <- dead to new snapshots: deleted (xmax) by txn 755, points to new version
-- 2  | 754    | 0      | (0,2)
-- 3  | 755    | 0      | (0,3)      <- live version

VACUUM accounts;
SELECT lp, lp_flags, t_xmin FROM heap_page_items(get_raw_page('accounts', 0)) ORDER BY lp;
-- Result: slot 1 is reclaimed (lp_flags=2: redirect to slot 3, tuple body gone); slots 2,3 normal.
-- (txids 754/755 and exact slots vary per run; the pattern is what matters)

-- The cost of "update = insert new version": table growth until VACUUM can reuse space
CREATE TABLE bloat (id INT PRIMARY KEY, v INT);
INSERT INTO bloat SELECT g, 0 FROM generate_series(1, 10000) g;
SELECT pg_relation_size('bloat');      -- 368640 bytes
UPDATE bloat SET v = v + 1;
SELECT pg_relation_size('bloat');      -- 729088  (doubled: 10,000 dead + 10,000 live versions)
VACUUM bloat;
SELECT pg_relation_size('bloat');      -- 729088  (VACUUM does NOT shrink the file; it marks space reusable)
UPDATE bloat SET v = v + 1;
SELECT pg_relation_size('bloat');      -- 729088  (second update reused the freed space, no further growth)
-- Shrink the file only with VACUUM FULL / pg_repack (takes heavy locks).
```

---

## 🔍 Why This Works (3 lines max)
Each row version carries visibility info (PostgreSQL xmin/xmax; InnoDB hidden trx id + roll pointer to undo), and a snapshot decides which version a transaction may see. That removes read locks entirely, trading them for extra storage and background cleanup.
हिंदी: हर version पर transaction id लगी होती है; snapshot तय करता है कौन-सा version दिखे, और cleanup VACUUM या purge करता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL isolation: default READ COMMITTED (snapshot per statement)
--   REPEATABLE READ = one snapshot per transaction (prevents phantoms too, unlike the SQL standard)
--   SERIALIZABLE    = SSI, may raise "could not serialize access" -> app must retry
-- MySQL InnoDB default: REPEATABLE READ (consistent reads from snapshot; locking reads/DML see latest data + gap locks)

-- Monitoring bloat / vacuum (PostgreSQL):
SELECT relname, n_live_tup, n_dead_tup FROM pg_stat_user_tables WHERE relname = 'accounts';
-- (after VACUUM: 2 live, 0 dead on the test above)

-- Tuning: autovacuum_vacuum_scale_factor lower for hot tables; fillfactor < 100 enables HOT updates;
-- avoid long-running / idle-in-transaction sessions (they pin old versions in BOTH engines).

-- Key design difference:
--   PostgreSQL: new version in heap, indexes may need new entries (HOT updates avoid it) -> VACUUM
--   InnoDB:     update in place, old image in undo log, rollback = apply undo -> purge thread
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "MVCC means no locks at all" -> writers still lock rows against other writers
--    (two concurrent UPDATEs of the same row serialize; use SELECT ... FOR UPDATE for read-modify-write)
-- ❌ Wrong: leaving a transaction open for hours: PostgreSQL cannot vacuum dead rows,
--    InnoDB history list length / undo tablespace keeps growing.
-- ❌ Wrong: expecting VACUUM to shrink the table file (it only recycles space; VACUUM FULL rewrites it)
-- ❌ Wrong: using MyISAM and expecting transactions/snapshots (no MVCC there)
-- ✅ Correct: short transactions, healthy autovacuum, monitor n_dead_tup / history list length
```

---

## 🎯 Interview Tip (1 line)
Say: "MVCC gives each transaction a consistent snapshot so readers never block writers; PostgreSQL pays for it with in-heap dead tuples that VACUUM must reclaim (bloat, txid wraparound), InnoDB with undo logs and purge — and in both engines long-running transactions are the real enemy."

---

## 🔗 Related Questions
→ Q227 (deadlocks) | Q017 (SELECT FOR UPDATE) | Q225 (ACID real examples) | Q230 (InnoDB vs MyISAM)
