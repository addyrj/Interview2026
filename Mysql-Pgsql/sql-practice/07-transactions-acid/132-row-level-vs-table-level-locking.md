---

# Q132. Row-Level vs Table-Level Locking
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
What is the difference between row-level and table-level locking? Show that two sessions can update different rows at the same time, but an explicit table lock blocks everyone. Show the syntax in both MySQL and PostgreSQL.

---

## 💡 Quick Concept (2 lines only)
Row locks (InnoDB, all PG DML) lock only the touched rows, so concurrency is high. Table locks (LOCK TABLES, LOCK TABLE, DDL) lock the whole table, which is simple but blocks everything else.
हिंदी: Row lock सिर्फ छुए गए rows को रोकता है; table lock पूरे table को — इसलिए concurrency गिरती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first) — MySQL and PostgreSQL
-- ============================================

CREATE TABLE accounts (
  id      INT PRIMARY KEY,
  owner   VARCHAR(50),
  balance DECIMAL(10,2)
);

INSERT INTO accounts VALUES (1, 'Alice', 1000), (2, 'Bob', 500);

-- ============================================
-- SOLUTION (MySQL, two sessions; lock_wait_timeout=1 so blocked ones fail fast)
-- ============================================

-- Session A: row lock on id=1 only
START TRANSACTION;
UPDATE accounts SET balance = balance - 10 WHERE id = 1;

-- Session B:
UPDATE accounts SET balance = balance + 1 WHERE id = 2;   -- OK, different row
UPDATE accounts SET balance = balance + 1 WHERE id = 1;   -- BLOCKED, same row
LOCK TABLES accounts WRITE;                               -- BLOCKED too (needs to wait for A's open txn)

-- Session A: ROLLBACK;  then explicit table lock:
LOCK TABLES accounts WRITE;
-- Session B:
SELECT * FROM accounts WHERE id = 2;                      -- BLOCKED, even a plain read
-- Session A: UNLOCK TABLES;

-- PostgreSQL equivalent of the explicit table lock (must be inside a transaction):
BEGIN;
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;     -- blocks everything, even SELECT
-- COMMIT releases it (there is no UNLOCK in PG)

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1)
-- ============================================
-- B update id=2 -> succeeds
-- B update id=1 -> ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction
-- B LOCK TABLES -> ERROR 1205 (metadata lock wait timeout)
-- B select id=2 while A holds LOCK TABLES WRITE -> ERROR 1205
--
-- PGlite (single session): LOCK TABLE ... ACCESS EXCLUSIVE shows in pg_locks:
-- mode                | granted
-- AccessExclusiveLock | true
```

---

## 🔍 Why This Works (3 lines max)
InnoDB and PostgreSQL store lock info per row (or per tuple), so unrelated rows do not interfere. Explicit table locks and most DDL take a table-level lock that conflicts with the table-level intention locks (IX / RowExclusive) held by every writer.
हिंदी: DML row-level lock लेता है; LOCK TABLE और DDL table-level, जो सब readers/writers से टकराता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL: lighter table-level options
LOCK TABLES accounts READ;                 -- others can read, nobody can write
FLUSH TABLES WITH READ LOCK;               -- global read lock (backups) - dangerous on busy servers
-- MySQL MyISAM has ONLY table locks; InnoDB (default) has row locks + table intention locks (IS/IX).

-- PostgreSQL: choose the weakest table lock that works (8 modes, from ACCESS SHARE to ACCESS EXCLUSIVE)
LOCK TABLE accounts IN SHARE ROW EXCLUSIVE MODE;   -- blocks writers, allows plain reads
-- Plain SELECT = ACCESS SHARE; INSERT/UPDATE/DELETE = ROW EXCLUSIVE; ALTER TABLE/DROP = ACCESS EXCLUSIVE
-- Row-level lock in PG also leaves a table-level RowShareLock (seen in pg_locks for FOR NO KEY UPDATE).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: running ALTER TABLE / CREATE INDEX on a hot table during peak traffic
ALTER TABLE accounts ADD COLUMN status VARCHAR(10);
-- PG takes ACCESS EXCLUSIVE; if it queues behind one long transaction, ALL new queries queue behind IT.
-- MySQL waits on the metadata lock the same way.
-- ✅ PG: SET lock_timeout = '3s'; CREATE INDEX CONCURRENTLY ...; MySQL 8: ALGORITHM=INPLACE/INSTANT, or gh-ost / pt-osc

-- ❌ Wrong: mixing LOCK TABLES with InnoDB transactions and expecting normal COMMIT behaviour
-- LOCK TABLES implicitly commits the open transaction in MySQL.
```

---

## 🎯 Interview Tip (1 line)
Say: "OLTP relies on row-level locks plus MVCC; table locks only come from explicit LOCK TABLE and DDL, and the real production danger is a lock queue — one long transaction plus an ALTER blocks every other query — so I always set lock_timeout and use online schema-change tools."

---

## 🔗 Related Questions
→ Q128 (FOR UPDATE vs FOR SHARE) | Q135 (Long-running transactions) | Q130 (Gap lock) | Q129 (Deadlock)
