---

# Q163. InnoDB Redo Log vs Undo Log
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (PostgreSQL equivalents: WAL and MVCC old tuple versions)

---

## ❓ Question
What is the difference between the InnoDB redo log and undo log, which guarantees which ACID property, and how do you inspect them? How do they differ from the binary log?

---

## 💡 Quick Concept (2 lines only)
Redo log = physical "re-apply this page change" journal for crash recovery (Durability). Undo log = old row versions used for ROLLBACK and for MVCC consistent reads (Atomicity + Isolation).
हिंदी: Redo = crash के बाद दोबारा चलाने के लिए (Durability); Undo = rollback और पुराने snapshot पढ़ने के लिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 verified)
-- ============================================

CREATE TABLE orders (id INT PRIMARY KEY, status VARCHAR(20));
INSERT INTO orders VALUES (1,'paid'),(2,'paid'),(3,'new');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: UNDO in action - rollback restores the old version
START TRANSACTION;
UPDATE orders SET status = 'x' WHERE id <= 3;   -- old values saved in undo, new pages in buffer pool + redo
SELECT status FROM orders WHERE id = 1;         -- 'x' (own change)
ROLLBACK;                                       -- undo applied
SELECT status FROM orders WHERE id = 1;         -- 'paid' again

-- Step 2: inspect settings
SELECT @@innodb_redo_log_capacity, @@innodb_log_buffer_size, @@innodb_flush_log_at_trx_commit;
SHOW VARIABLES LIKE 'innodb_undo%';
SHOW GLOBAL STATUS LIKE 'Innodb_redo_log%';

-- ============================================
-- EXPECTED OUTPUT (real run)
-- ============================================
-- Step 1:  x   then   paid
-- Step 2:
--   innodb_redo_log_capacity = 104857600 (100MB; 8.0.30+ replaces innodb_log_file_size/files_in_group)
--   innodb_log_buffer_size   = 67108864
--   innodb_flush_log_at_trx_commit = 1     <- fsync redo at every commit = full durability
--   innodb_undo_tablespaces = 2 (innodb_undo_001, innodb_undo_002) | innodb_undo_log_truncate = ON
--   Innodb_redo_log_current_lsn 21078178 | checkpoint_lsn 21016406 | physical_size 3276800
```

---

## 🔍 Why This Works (3 lines max)
On commit only the (sequential, cheap) redo log must be flushed; dirty pages are written lazily and replayed from redo after a crash. Undo keeps prior versions so readers get consistent snapshots without blocking writers, and purge threads remove undo once no transaction needs it.
हिंदी: Commit पर सिर्फ redo flush होता है; undo पुराने versions रखता है ताकि rollback और MVCC चले।

---

## ⚡ Alternative Solution

```sql
-- Comparison table (answer this verbally):
-- | aspect        | redo log                 | undo log                          | binary log (server layer)       |
-- | layer         | InnoDB                   | InnoDB                            | MySQL server                    |
-- | content       | physical page changes    | previous row versions             | logical row events/statements   |
-- | purpose       | crash recovery           | rollback + MVCC                   | replication, PITR               |
-- | lifetime      | circular, recycled       | purged when no snapshot needs it  | kept per binlog_expire seconds  |

-- Long-running transactions bloat undo (history list length grows, purge falls behind):
SELECT NAME, COUNT FROM information_schema.INNODB_METRICS WHERE NAME = 'trx_rseg_history_len';
-- (real run on idle server: 24)
-- Find the culprit: SELECT trx_id, trx_started FROM information_schema.INNODB_TRX ORDER BY trx_started LIMIT 5;

-- Two-phase commit ties redo and binlog together: prepare redo -> write binlog -> commit redo.
-- innodb_flush_log_at_trx_commit=2 / sync_binlog=0 trades durability (up to ~1s data loss on OS crash) for speed.
-- PostgreSQL: WAL = redo; old tuple versions live in the heap (VACUUM cleans) instead of a separate undo log.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Confusing the three logs: "binlog is used for crash recovery" - no, redo is; binlog is for replication/PITR
-- ❌ Leaving a transaction open (BEGIN; SELECT ...; then idle for hours): purge blocked, undo/ibdata grows, queries slow
-- ❌ innodb_flush_log_at_trx_commit=0/2 on a payments DB to "get speed"
-- ✅ Keep transactions short; size redo capacity so checkpoints aren't forced under write bursts
```

---

## 🎯 Interview Tip (1 line)
Say: "Redo is physical, write-ahead, circular and gives durability via crash recovery; undo holds old versions for rollback and MVCC and is purged when no read view needs it; binlog is a separate server-level logical log for replication - and I watch history list length for long transactions."

---

## 🔗 Related Questions
→ Q162 (Buffer pool) | Q164 (Binary log) | Q165 (AUTO_INCREMENT gaps - rollback does not return IDs)
