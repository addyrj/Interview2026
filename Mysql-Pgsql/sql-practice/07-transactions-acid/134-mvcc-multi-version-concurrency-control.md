---

# Q134. MVCC — Multi-Version Concurrency Control
# Category: Transactions & ACID
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ InnoDB | PostgreSQL) — MySQL part run on 9.1.0 with two real sessions; PgSQL part run on PGlite (single connection)

---

## ❓ Question
How can readers not block writers (and vice versa) in MySQL InnoDB and PostgreSQL? Explain MVCC, show a snapshot read that does not see a concurrent committed update, and explain how each engine stores old row versions and cleans them up.

---

## 💡 Quick Concept (2 lines only)
Instead of locking a row for readers, the DB keeps multiple versions of it; each transaction reads the version visible to its snapshot. Writers create a new version, so readers never wait.
हिंदी: Reader के लिए row lock करने की जगह DB row के कई versions रखता है; हर transaction अपने snapshot का version देखता है, इसलिए read-write आपस में block नहीं होते।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE products (
  id    INT PRIMARY KEY,
  name  VARCHAR(50),             -- PgSQL: TEXT also fine
  price DECIMAL(10,2)            -- PgSQL: NUMERIC(10,2)
);

INSERT INTO products VALUES (1, 'Keyboard', 1000.00);

-- ============================================
-- SOLUTION (MySQL, default REPEATABLE READ) - needs TWO sessions
-- ============================================

-- Session A:                                   -- Session B:
BEGIN;
SELECT price FROM products WHERE id = 1;        -- 1000.00  (snapshot taken here)
                                                BEGIN;
                                                UPDATE products SET price = 1200 WHERE id = 1;
                                                COMMIT;
SELECT price FROM products WHERE id = 1;        -- STILL 1000.00 (old version, no blocking)
SELECT price FROM products WHERE id = 1 FOR UPDATE;   -- 1200.00 (locking read = "current read")
COMMIT;
SELECT price FROM products WHERE id = 1;        -- 1200.00 (new transaction, new snapshot)

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1.0, A and B ran concurrently)
-- ============================================

-- A first read                 | 1000.00
-- B committed                  | 1200.00
-- A second read                | 1000.00   <- consistent snapshot
-- A FOR UPDATE (current read)  | 1200.00   <- sees latest committed
-- A after commit               | 1200.00

-- ============================================
-- HOW OLD VERSIONS ARE STORED
-- ============================================
-- MySQL InnoDB : row updated IN PLACE; old version lives in the UNDO log
--                (rollback segment). Readers rebuild the old row by walking
--                the undo chain. Cleanup = purge thread (blocked if an old
--                transaction/snapshot is still open -> "History list length" grows).
-- PostgreSQL   : UPDATE = insert a NEW tuple, old tuple is marked dead (xmax set).
--                Both live in the heap. Cleanup = VACUUM / autovacuum.

-- ============================================
-- PostgreSQL: SEE the versions (hidden system columns)
-- ============================================

SELECT ctid, xmin, xmax, id, price FROM products;     -- ctid = physical location
UPDATE products SET price = 1200 WHERE id = 1;
SELECT ctid, xmin, xmax, id, price FROM products;

-- ============================================
-- EXPECTED OUTPUT (real PGlite; xmin numbers differ per run)
-- ============================================

-- before:  ctid=(0,1) | xmin=753 | xmax=0 | id=1 | price=1000.00
-- after :  ctid=(0,2) | xmin=754 | xmax=0 | id=1 | price=1200.00
-- ctid moved (0,1) -> (0,2): UPDATE wrote a NEW physical tuple. The old tuple
-- (0,1) is still on the page as a dead tuple until VACUUM reclaims it.
```

---

## 🔍 Why This Works (3 lines max)
Every row version is tagged with the transaction id that created (and deleted) it; a snapshot defines which transaction ids are "visible", so a reader just picks the right version without taking row locks. Only writer-vs-writer on the same row conflict.
हिंदी: हर row version पर transaction id लगी होती है; snapshot तय करता है कौन सा version दिखेगा, इसलिए reader lock नहीं लेता; सिर्फ writer-writer टकराते हैं।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (READ COMMITTED default): snapshot is per STATEMENT, not per transaction,
-- so the second plain SELECT in session A WOULD show 1200.00.
-- Use REPEATABLE READ to freeze the snapshot like MySQL does:
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT price FROM products WHERE id = 1;
-- ... other session commits an update ...
SELECT price FROM products WHERE id = 1;   -- unchanged
COMMIT;
-- (Two-session behaviour not runnable on PGlite - single connection - explained from docs.)

-- Inspect dead tuples / bloat (PgSQL):
SELECT relname, n_live_tup, n_dead_tup FROM pg_stat_user_tables;
VACUUM (VERBOSE) products;

-- MySQL: watch undo growth caused by a forgotten transaction:
SHOW ENGINE INNODB STATUS\G         -- look for "History list length"
SELECT trx_id, trx_started FROM information_schema.innodb_trx;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong belief: "MVCC means no locks at all"
-- Writers still lock the rows they change; two UPDATEs of the same row serialize.
-- Only plain (non-locking) SELECTs are lock-free.

-- ❌ Wrong: assuming SELECT ... FOR UPDATE reads the snapshot in MySQL
-- It reads the LATEST committed version (current read) - we saw 1200.00 above
-- while the plain SELECT in the same transaction returned 1000.00.

-- ❌ Wrong: PgSQL UPDATE of one column is "in place and free"
-- Every UPDATE writes a new tuple -> heavy-update tables bloat without
-- autovacuum tuning (HOT updates and fillfactor help).

-- ✅ Keep transactions short; one idle-in-transaction session blocks VACUUM (PgSQL)
--    and undo purge (MySQL) for the whole database.
```

---

## 🎯 Interview Tip (1 line)
Say: "InnoDB keeps the newest row in place and rebuilds old versions from undo logs, Postgres appends new tuples and relies on VACUUM; in both, a long-lived transaction pins old versions and causes bloat or history-list growth, so I monitor oldest-transaction age."

---

## 🔗 Related Questions
→ Q121 (Isolation levels) | Q123 (Non-repeatable read) | Q135 (Long-running transactions) | Q128 (FOR UPDATE vs FOR SHARE)
