---

# Q130. Gap Lock in MySQL InnoDB — What Is It
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (InnoDB only — PostgreSQL has no gap locks)

---

## ❓ Question
What is a gap lock in InnoDB? Given seats with ids 10, 20, 30, show that `SELECT ... WHERE id BETWEEN 11 AND 19 FOR UPDATE` blocks an insert of id 15 even though no row exists there. How do you see the lock, and how do you avoid it?

---

## 💡 Quick Concept (2 lines only)
A gap lock locks the empty space between two index records (not the records), so nobody can insert into that range. InnoDB uses it at REPEATABLE READ to stop phantom rows during locking reads.
हिंदी: Gap lock दो index records के बीच की खाली जगह को lock करता है ताकि वहाँ नया row insert न हो सके।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — MySQL, default REPEATABLE READ
-- ============================================

CREATE TABLE seats (
  id    INT PRIMARY KEY,
  label VARCHAR(10)
);

INSERT INTO seats VALUES (10, 'A'), (20, 'B'), (30, 'C');

-- ============================================
-- SOLUTION
-- ============================================

-- Session A: lock a range that contains NO rows
START TRANSACTION;
SELECT * FROM seats WHERE id BETWEEN 11 AND 19 FOR UPDATE;   -- 0 rows returned, but gap (10,20) is locked

-- Inspect the locks (MySQL 8.0+):
SELECT index_name, lock_type, lock_mode, lock_data
FROM performance_schema.data_locks
WHERE object_name = 'seats';

-- Session B (while A is open; I set innodb_lock_wait_timeout=2 to fail quickly):
INSERT INTO seats VALUES (15, 'X');          -- BLOCKS -> ERROR 1205 after timeout
INSERT INTO seats VALUES (25, 'Y');          -- OK (gap 20-30 is not locked)
UPDATE seats SET label = 'Z' WHERE id = 20;  -- OK (the record 20 itself is not locked, only the gap before it)
INSERT INTO seats VALUES (35, 'Y2');         -- OK

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1)
-- ============================================
-- data_locks:
-- index_name | lock_type | lock_mode | lock_data
-- NULL       | TABLE     | IX        | NULL
-- PRIMARY    | RECORD    | X,GAP     | 20          <- gap just BEFORE record 20, i.e. (10,20)
--
-- B insert 15 : ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction
-- B insert 25 : OK
-- B update 20 : OK
-- B insert 35 : OK
```

---

## 🔍 Why This Works (3 lines max)
For a range scan with no matching rows, InnoDB locks the gap before the next existing record (20), so inserts into (10,20) wait. Gap locks do not conflict with each other; they only block inserts into the gap.
हिंदी: Range में row नहीं मिला तो InnoDB अगले record (20) से पहले की gap lock कर देता है — उस range में insert रुक जाता है।

---

## ⚡ Alternative Solution

```sql
-- Avoid gap locks: use READ COMMITTED (gap locking is disabled for searches/index scans, only FK/duplicate checks use them)
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
START TRANSACTION;
SELECT * FROM seats WHERE id BETWEEN 11 AND 19 FOR UPDATE;
-- Session B: INSERT INTO seats VALUES (15,'X');  -> succeeds immediately (verified: row 15 inserted)
-- Trade-off: phantoms are possible again, and statement-based binlog is unsafe (use binlog_format=ROW)

-- Equality on a UNIQUE index with an existing row locks only that record (no gap):
SELECT * FROM seats WHERE id = 20 FOR UPDATE;      -- X,REC_NOT_GAP
-- Equality on a MISSING key still takes a gap lock:
SELECT * FROM seats WHERE id = 15 FOR UPDATE;      -- gap (10,20)

-- PostgreSQL: no gap locks. Phantoms are prevented by snapshot isolation (REPEATABLE READ) or SSI predicate locks (SERIALIZABLE).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "FOR UPDATE on a non-existent row locks nothing, so it's safe"
SELECT * FROM seats WHERE id = 15 FOR UPDATE;   -- in MySQL RR this locks the gap (10,20)!
-- Two sessions doing this "check then insert" can DEADLOCK: both hold gap locks (they do not conflict),
-- then both try to INSERT into the gap and wait on each other.
-- ✅ Use INSERT ... ON DUPLICATE KEY UPDATE / INSERT IGNORE, a UNIQUE constraint, or READ COMMITTED.
```

---

## 🎯 Interview Tip (1 line)
Say: "Gap locks are an InnoDB REPEATABLE READ feature that block inserts into a range; if I see unexplained lock waits or deadlocks on insert-heavy tables I check performance_schema.data_locks for X,GAP, and consider READ COMMITTED with row-based binlog."

---

## 🔗 Related Questions
→ Q131 (Next-key lock example) | Q129 (Deadlock example) | Q121 (Isolation levels) | Q126 (Default isolation)
