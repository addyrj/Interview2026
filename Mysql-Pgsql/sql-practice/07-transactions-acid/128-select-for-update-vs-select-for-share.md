---

# Q128. SELECT FOR UPDATE vs SELECT FOR SHARE
# Category: Transactions & ACID
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
What is the difference between `SELECT ... FOR UPDATE` and `SELECT ... FOR SHARE`? Show which combinations block each other, and what `NOWAIT` and `SKIP LOCKED` do.

---

## 💡 Quick Concept (2 lines only)
FOR SHARE takes a shared (read) row lock: many sessions can hold it, but nobody can modify the row. FOR UPDATE takes an exclusive lock: it blocks other FOR UPDATE, FOR SHARE and writes (plain non-locking SELECTs still read the old version).
हिंदी: FOR SHARE = सब पढ़ सकते हैं, कोई लिख नहीं सकता; FOR UPDATE = सिर्फ मैं, बाकी सब wait।

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
-- SOLUTION
-- ============================================

-- Session A (holds a SHARED lock on Bob's row):
START TRANSACTION;                                        -- PG: BEGIN;
SELECT id FROM accounts WHERE id = 2 FOR SHARE;

-- Session B while A is still open:
SELECT id FROM accounts WHERE id = 2 FOR SHARE NOWAIT;    -- OK: shared + shared is compatible
SELECT id FROM accounts WHERE id = 2 FOR UPDATE NOWAIT;   -- FAILS: exclusive vs shared conflict
SELECT id FROM accounts FOR UPDATE SKIP LOCKED;           -- skips row 2, returns only row 1
SELECT id, balance FROM accounts WHERE id = 2;            -- plain SELECT never blocks (MVCC)

-- Then swap: A takes FOR UPDATE, B tries FOR SHARE NOWAIT -> also fails.

-- ============================================
-- EXPECTED OUTPUT (real MySQL 9.1, two sessions)
-- ============================================
-- B: FOR SHARE NOWAIT      -> id=2 returned
-- B: FOR UPDATE NOWAIT     -> ERROR 3572 (HY000): Statement aborted because lock(s) could not be
--                              acquired immediately and NOWAIT is set.
-- B: FOR UPDATE SKIP LOCKED-> id=1 only
-- B: plain SELECT          -> id=2, balance=500.00
-- A=FOR UPDATE, B=FOR SHARE NOWAIT -> ERROR 3572 as well
--
-- PostgreSQL: same behaviour documented; error is SQLSTATE 55P03 "could not obtain lock on row".
-- PGlite is single-connection, so only the SYNTAX was run there (all four variants parse and return rows).

-- ============================================
-- COMPATIBILITY MATRIX (row locks)
-- ============================================
--                 held: SHARE   held: UPDATE
-- request SHARE      OK            WAIT
-- request UPDATE    WAIT           WAIT
```

---

## 🔍 Why This Works (3 lines max)
Row locks follow the classic shared/exclusive compatibility matrix. FOR SHARE protects "I read it, nobody may change it until I finish" (e.g. checking a parent row exists); FOR UPDATE protects "I will change it". NOWAIT fails fast, SKIP LOCKED ignores locked rows.
हिंदी: Shared+Shared चलता है, Exclusive किसी के साथ नहीं; NOWAIT तुरंत error देता है, SKIP LOCKED locked rows छोड़ देता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL differences:
--   Old syntax:  SELECT ... LOCK IN SHARE MODE   (still works; FOR SHARE is the 8.0 name)
--   FOR SHARE / FOR UPDATE also accept:  OF table_name  (lock only some joined tables)
-- PostgreSQL has FOUR strengths (weakest -> strongest):
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;       -- only blocks DELETE / key changes (FK checks use this)
SELECT * FROM accounts WHERE id = 1 FOR SHARE;
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;   -- updating non-key columns; does NOT block FOR KEY SHARE
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Verified in PGlite: all four run; FOR NO KEY UPDATE shows a RowShareLock on the table in pg_locks.
-- Prefer FOR NO KEY UPDATE in PG when you do not touch the PK: it avoids blocking child-table inserts.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: using FOR UPDATE outside a transaction (autocommit)
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;   -- lock is released the instant the statement ends!
-- ✅ Wrap in START TRANSACTION / BEGIN ... COMMIT so the lock lives until you finish

-- ❌ Wrong: locking with a non-indexed filter in MySQL
SELECT * FROM accounts WHERE owner = 'Bob' FOR UPDATE;  -- no index on owner -> locks every scanned row
-- ✅ Filter on an indexed / PK column so only the intended row(s) are locked
```

---

## 🎯 Interview Tip (1 line)
Say: "FOR SHARE is for 'this must not change while I rely on it', FOR UPDATE is for read-then-write; I add NOWAIT or SKIP LOCKED for user-facing or queue code so requests never hang, and in Postgres I use FOR NO KEY UPDATE when I am not changing keys."

---

## 🔗 Related Questions
→ Q017 (SELECT FOR UPDATE) | Q242 (How FOR UPDATE works) | Q136 (SKIP LOCKED queue) | Q127 (Optimistic vs pessimistic)
