---

# Q165. AUTO_INCREMENT Gaps — Why They Happen
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (verified on MySQL 9.1, InnoDB, innodb_autoinc_lock_mode=2; PgSQL equivalent noted)

---

## ❓ Question
After a few inserts, the `id` column shows 1, 2, 4, 6, 8, 9... Why does MySQL leave gaps in AUTO_INCREMENT values, and can you rely on ids being gap-free?

---

## 💡 Quick Concept (2 lines only)
InnoDB hands out the next counter value before the row is known to be successful, and never gives it back. Failed inserts, rollbacks, INSERT IGNORE duplicates and bulk-insert pre-allocation all burn values.
हिंदी: InnoDB id पहले दे देता है और वापस नहीं लेता — failed insert, rollback, duplicate या bulk insert से gap बन जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE tickets (
  id    INT AUTO_INCREMENT PRIMARY KEY,
  code  VARCHAR(20) UNIQUE,
  title VARCHAR(50)
) ENGINE=InnoDB;

-- ============================================
-- SOLUTION
-- ============================================

INSERT INTO tickets (code, title) VALUES ('T-1','a'),('T-2','b');      -- ids 1,2
INSERT INTO tickets (code, title) VALUES ('T-1','dup');                -- fails: duplicate key, but id 3 was already taken
-- ERROR 1062 (23000): Duplicate entry 'T-1' for key 'tickets.code'
INSERT INTO tickets (code, title) VALUES ('T-3','c');                  -- gets id 4

START TRANSACTION;
INSERT INTO tickets (code, title) VALUES ('T-4','d');                  -- takes id 5
ROLLBACK;                                                              -- row gone, id 5 is NOT reused
INSERT INTO tickets (code, title) VALUES ('T-5','e');                  -- id 6

INSERT IGNORE INTO tickets (code, title) VALUES ('T-5','dup2');        -- ignored duplicate, burns id 7
INSERT INTO tickets (code, title) VALUES ('T-6','f');                  -- id 8
INSERT INTO tickets (code, title) VALUES ('T-7','g'),('T-8','h'),('T-9','i');   -- ids 9,10,11

SELECT id, code FROM tickets ORDER BY id;
-- Result (real output):
-- id | code
-- 1  | T-1
-- 2  | T-2
-- 4  | T-3      <- 3 lost to the duplicate-key error
-- 6  | T-5      <- 5 lost to the rollback
-- 8  | T-6      <- 7 lost to INSERT IGNORE
-- 9  | T-7
-- 10 | T-8
-- 11 | T-9

-- Bulk INSERT ... SELECT pre-allocates in batches of 1, 2, 4, ... (lock mode 2 = "interleaved")
CREATE TABLE b (id INT AUTO_INCREMENT PRIMARY KEY, n INT);
INSERT INTO b (n) VALUES (1),(2),(3),(4),(5);        -- ids 1..5
INSERT INTO b (n) SELECT n FROM b;                   -- 5 rows, but 1+2+4 = 7 ids reserved
INSERT INTO b (n) VALUES (99);
SELECT id, n FROM b ORDER BY id;
-- ids: 1,2,3,4,5,6,7,8,9,10 and then 13 for n=99   <- ids 11 and 12 were reserved but unused

-- Running out of ids is also a failure mode: TINYINT UNSIGNED max = 255
CREATE TABLE tiny (id TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY);
INSERT INTO tiny VALUES (254),(NULL);    -- 254, 255
INSERT INTO tiny VALUES (NULL);
-- ERROR 1062 (23000): Duplicate entry '255' for key 'tiny.PRIMARY'
```

---

## 🔍 Why This Works (3 lines max)
The auto-inc counter is incremented under a short lock and kept outside the transaction so concurrent inserts never wait for each other's commit; this means a value cannot be returned after a rollback or error. In lock mode 2 (default in 8.0+) bulk inserts may also reserve extra values.
हिंदी: Counter transaction के बाहर बढ़ता है ताकि concurrency बनी रहे — इसलिए rollback/error पर value वापस नहीं होती।

---

## ⚡ Alternative Solution

```sql
-- Check the lock mode (8.0+ default 2; 5.7 default 1 = "consecutive")
SELECT @@innodb_autoinc_lock_mode;      -- 2 on this server
-- Mode 1 gives gap-free ids for simple inserts but not for failed ones; mode 0 = table-level lock.
-- Mode 2 is only safe with ROW binlog format (the 8.0 default); statement-based replication needs mode 0 or 1.

-- PostgreSQL: SERIAL / IDENTITY use sequences, which have exactly the same gap behaviour
-- (nextval() is non-transactional; rollbacks and ON CONFLICT DO NOTHING burn values).

-- If a business needs gap-free numbers (invoice numbers, legal), do NOT use AUTO_INCREMENT:
CREATE TABLE invoice_counter (year SMALLINT PRIMARY KEY, last_no INT NOT NULL);
-- inside the same transaction as the invoice insert:
-- UPDATE invoice_counter SET last_no = last_no + 1 WHERE year = 2024;  SELECT last_no ...;  (row lock serializes)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: assuming ids are gap-free / using MAX(id) or COUNT(*) as "number of records"
SELECT MAX(id) FROM tickets;          -- 11, but only 8 rows exist
-- ❌ Wrong: "fixing" gaps by renumbering primary keys (breaks foreign keys, caches, URLs)
-- ❌ Wrong: using an INT id on a very busy table -> 2^31 ids burn faster than row count suggests
--    (ON DUPLICATE KEY UPDATE / INSERT IGNORE retries consume ids on every attempt)
-- ✅ Use BIGINT UNSIGNED, treat ids as opaque, and generate legal sequence numbers separately
```

---

## 🎯 Interview Tip (1 line)
Say: "Gaps are by design: the counter is non-transactional for concurrency, so rollbacks, duplicate-key errors, INSERT IGNORE and bulk-insert pre-allocation burn values — ids guarantee uniqueness and rough ordering, never contiguity, and I'd use BIGINT to avoid exhaustion."

---

## 🔗 Related Questions
→ Q166 (AUTO_INCREMENT reset gotcha) | Q160 (UUID vs BIGINT) | Q013 (UPSERT) | Q163 (Redo vs undo log)
