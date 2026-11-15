---

# Q131. Next-Key Lock in MySQL — Example
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (InnoDB only)

---

## ❓ Question
What is a next-key lock? For a `tickets` table with a NON-unique index on `priority`, show exactly which records and gaps are locked by `SELECT ... WHERE priority = 20 FOR UPDATE`, and which inserts/updates from another session are blocked.

---

## 💡 Quick Concept (2 lines only)
Next-key lock = record lock on an index entry + gap lock on the gap BEFORE it. InnoDB uses it by default at REPEATABLE READ for range/non-unique index scans; it also adds a gap lock on the next entry after the last match.
हिंदी: Next-key lock = index record का lock + उससे पहले की gap का lock; REPEATABLE READ में non-unique index scan पर default।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — MySQL, REPEATABLE READ
-- ============================================

CREATE TABLE tickets (
  id       INT PRIMARY KEY,
  priority INT,
  title    VARCHAR(30),
  INDEX idx_priority (priority)          -- NON-unique secondary index
);

INSERT INTO tickets VALUES
  (1, 10, 't1'),
  (2, 20, 't2'),
  (3, 20, 't3'),     -- two rows share priority 20
  (4, 30, 't4');

-- ============================================
-- SOLUTION
-- ============================================

-- Session A:
START TRANSACTION;
SELECT * FROM tickets WHERE priority = 20 FOR UPDATE;

SELECT index_name, lock_type, lock_mode, lock_data
FROM performance_schema.data_locks
WHERE object_name = 'tickets'
ORDER BY index_name, lock_data;

-- Session B (innodb_lock_wait_timeout=1 so it fails fast):
INSERT INTO tickets VALUES (9, 15, 'n');   -- priority 15: inside gap (10..20)  -> BLOCKED
INSERT INTO tickets VALUES (9, 20, 'n');   -- priority 20: between (20,3) and (30,4) -> BLOCKED
INSERT INTO tickets VALUES (9, 25, 'n');   -- priority 25: same gap -> BLOCKED
INSERT INTO tickets VALUES (9, 35, 'n');   -- after the last locked gap -> OK
INSERT INTO tickets VALUES (9, 30, 'n');   -- sorts AFTER (30,4) -> OK
UPDATE tickets SET title = 'z' WHERE id = 4;   -- row (30,4) is only GAP-locked, not record-locked -> OK
UPDATE tickets SET title = 'z' WHERE id = 2;   -- record lock on id 2 -> BLOCKED

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1)
-- ============================================
-- index_name   | lock_type | lock_mode     | lock_data
-- NULL         | TABLE     | IX            | NULL
-- idx_priority | RECORD    | X             | 20, 2     <- next-key: record (20,2) + gap before it (10..20)
-- idx_priority | RECORD    | X             | 20, 3     <- next-key: record (20,3) + gap between the two 20s
-- idx_priority | RECORD    | X,GAP         | 30, 4     <- gap only: (20,3)..(30,4)
-- PRIMARY      | RECORD    | X,REC_NOT_GAP | 2         <- matching clustered rows are record-locked
-- PRIMARY      | RECORD    | X,REC_NOT_GAP | 3
--
-- B results: ERROR 1205 (timeout) for priority 15, 20, 25 and for UPDATE id=2;
--            OK for priority 35, priority 30 and UPDATE id=4.
```

---

## 🔍 Why This Works (3 lines max)
In a non-unique index, entries are ordered by (priority, primary key), so InnoDB locks every matching entry as a next-key lock and then a gap lock on the following entry (30,4) to stop new priority-20 or in-between rows (phantoms). The `X` without suffix IS the next-key lock.
हिंदी: `X` (बिना GAP/REC_NOT_GAP) = next-key lock; matching entries के बाद अगली entry पर सिर्फ gap lock लगता है।

---

## ⚡ Alternative Solution

```sql
-- Unique-index equality that finds the row degrades next-key lock to a plain record lock:
SELECT * FROM tickets WHERE id = 2 FOR UPDATE;      -- X,REC_NOT_GAP on PRIMARY 2 only (verified on seats table)

-- Range scan on the PK locks up to the supremum (the "infinity" record):
SELECT * FROM seats WHERE id >= 20 FOR UPDATE;      -- seats(10,20,30) from Q130
-- data_locks: X on 'supremum pseudo-record', X on 30, X,REC_NOT_GAP on 20  (verified)
-- => nobody can insert any id > 30 either!

-- Reduce locking: READ COMMITTED (no gap/next-key locks for searches) — or add a UNIQUE key and query it by equality.
-- PostgreSQL: no next-key locks; row locks only, phantoms handled by snapshots/SSI.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: believing "I only lock rows that match"
SELECT * FROM tickets WHERE priority = 20 FOR UPDATE;
-- Real effect: priority 15..30-ish inserts are blocked too (see above), which shows up as random
-- "Lock wait timeout" errors on an unrelated INSERT in production.
-- ❌ Also wrong: FOR UPDATE on an unindexed column -> full scan -> next-key locks on EVERY record + supremum (like a table lock)
-- ✅ Index the filter column, keep transactions short, check performance_schema.data_locks
```

---

## 🎯 Interview Tip (1 line)
Say: "Next-key = record + preceding gap; it is how InnoDB's REPEATABLE READ prevents phantoms for locking reads, and I debug surprise waits by reading data_locks for X vs X,GAP vs X,REC_NOT_GAP."

---

## 🔗 Related Questions
→ Q130 (Gap lock) | Q129 (Deadlock example) | Q132 (Row vs table locking) | Q121 (Isolation levels)
