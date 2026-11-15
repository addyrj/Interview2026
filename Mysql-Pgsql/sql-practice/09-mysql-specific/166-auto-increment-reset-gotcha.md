---

# Q166. AUTO_INCREMENT Reset — Gotcha
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (verified on MySQL 9.1 InnoDB; PgSQL equivalent noted, not run)

---

## ❓ Question
You delete rows from a table and want ids to start again from 1. What do `DELETE`, `TRUNCATE` and `ALTER TABLE ... AUTO_INCREMENT = n` actually do to the counter, and why does the ALTER sometimes seem to be ignored?

---

## 💡 Quick Concept (2 lines only)
DELETE never resets the counter; TRUNCATE does (it recreates the table). `ALTER TABLE ... AUTO_INCREMENT = n` can only move the counter UP to at least MAX(id)+1; a smaller value is silently ignored.
हिंदी: DELETE counter reset नहीं करता, TRUNCATE करता है। ALTER AUTO_INCREMENT सिर्फ MAX(id)+1 या उससे ऊपर जा सकता है, छोटा value ignore होता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE a (id INT AUTO_INCREMENT PRIMARY KEY, v INT);
INSERT INTO a (v) VALUES (1),(2),(3);          -- ids 1,2,3

SELECT AUTO_INCREMENT FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'a';
-- AUTO_INCREMENT = 4   (the NEXT value to be handed out; information_schema may cache this, see note below)

-- ============================================
-- SOLUTION
-- ============================================

-- Case 1: DELETE of the latest row does not reuse its id (MySQL 8.0+ persists the counter)
DELETE FROM a WHERE id = 3;
INSERT INTO a (v) VALUES (4);
SELECT * FROM a;
-- id | v
-- 1  | 1
-- 2  | 2
-- 4  | 4        <- 3 is not reused
-- (MySQL 5.7 and earlier: after a server RESTART the counter was recomputed as MAX(id)+1 and id 3 WAS reused;
--  8.0 stores the counter in the redo log. Not restart-tested here.)

-- Case 2: empty the table with DELETE, then set the counter back
DELETE FROM a;
ALTER TABLE a AUTO_INCREMENT = 1;               -- allowed because the table is empty (MAX(id)+1 = 1)
INSERT INTO a (v) VALUES (5);
SELECT * FROM a;
-- id | v
-- 1  | 5

-- Case 3: the gotcha — ALTER to a value lower than MAX(id)+1 is ignored
INSERT INTO a (id, v) VALUES (100, 6);          -- manual id
INSERT INTO a (v) VALUES (7);                   -- 101
ALTER TABLE a AUTO_INCREMENT = 50;              -- no error, no warning... but no effect (max is 101)
INSERT INTO a (v) VALUES (8);                   -- 102, not 50
SELECT * FROM a ORDER BY id;
-- id  | v
-- 1   | 5
-- 100 | 6
-- 101 | 7
-- 102 | 8

-- Case 4: TRUNCATE resets to 1 (drops and recreates the table; DDL, cannot roll back, fails if FKs reference it)
TRUNCATE TABLE a;
INSERT INTO a (v) VALUES (9);
SELECT * FROM a;
-- id | v
-- 1  | 9
```

---

## 🔍 Why This Works (3 lines max)
The counter is a table-level property, separate from the rows. DELETE removes rows only; TRUNCATE rebuilds the table, so the counter restarts; ALTER sets it but InnoDB enforces counter > current max to avoid duplicate keys, so a too-small value is raised silently.
हिंदी: Counter rows से अलग property है; TRUNCATE table दोबारा बनाता है इसलिए reset; ALTER छोटा value दे तो InnoDB उसे MAX+1 कर देता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL: the sequence is a separate object; reset it explicitly
TRUNCATE TABLE a RESTART IDENTITY;                       -- table + identity counter
ALTER TABLE a ALTER COLUMN id RESTART WITH 1;            -- identity column
SELECT setval(pg_get_serial_sequence('a','id'), COALESCE(MAX(id),0)+1, false) FROM a;   -- after bulk-loading explicit ids
-- PgSQL does NOT protect you: if you set it too low you get duplicate-key errors on the next insert.
-- (PgSQL variants not run here.)

-- MySQL: after loading rows with explicit ids, no manual fix is needed:
-- the counter automatically moves to MAX(id)+1 (see Case 3: 100 -> next is 101).

-- Set the starting value for a new table
CREATE TABLE orders_seed (id BIGINT AUTO_INCREMENT PRIMARY KEY) AUTO_INCREMENT = 1000;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: "my ids are huge, I'll just reset the counter on prod"
ALTER TABLE orders AUTO_INCREMENT = 1;   -- ignored if rows exist; if you delete rows first, old ids in
                                         -- logs, caches, URLs, other services now point to the WRONG new rows
-- ❌ Wrong: TRUNCATE in prod expecting it to be a fast DELETE: implicit commit, no rollback, no triggers,
--    blocked by FK references, resets the counter
-- ❌ Wrong: relying on information_schema.TABLES.AUTO_INCREMENT being current (cached;
--    set information_schema_stats_expiry=0 or ANALYZE TABLE to refresh)
-- ✅ Never reuse ids of deleted business rows; reset counters only in dev/test databases
```

---

## 🎯 Interview Tip (1 line)
Say: "DELETE leaves the counter alone, TRUNCATE resets it, and ALTER TABLE AUTO_INCREMENT can only raise it above MAX(id)+1 — and in production I wouldn't reset it at all, since reused ids confuse caches, audit logs and downstream systems."

---

## 🔗 Related Questions
→ Q165 (AUTO_INCREMENT gaps) | Q015 (DELETE vs TRUNCATE vs DROP) | Q160 (UUID vs BIGINT) | Q154 (Sharding ids)
