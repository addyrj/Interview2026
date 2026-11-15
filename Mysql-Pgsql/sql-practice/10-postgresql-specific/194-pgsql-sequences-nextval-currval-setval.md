---

# Q194. PgSQL Sequences — nextval, currval, setval
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL (MySQL uses AUTO_INCREMENT)

---

## ❓ Question
Explain `nextval`, `currval`, `setval`. Show how a sequence behaves across rollbacks, and fix the classic bug where `INSERT` fails with a duplicate key after rows were loaded with explicit ids.

---

## 💡 Quick Concept (2 lines only)
A sequence is a separate counter object: `nextval` advances and returns, `currval` returns the last value fetched IN THIS SESSION, `setval` repositions it. Sequences are non-transactional, so rollbacks leave gaps.
हिंदी: Sequence अलग counter object है; nextval आगे बढ़ाता है, currval इसी session की last value देता है, setval position बदलता है; rollback पर gap रह जाता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- PostgreSQL
-- ============================================

CREATE SEQUENCE invoice_no_seq START 1000 INCREMENT 1;

CREATE TABLE customers (id SERIAL PRIMARY KEY, name TEXT);
-- Bulk-loaded with EXPLICIT ids (e.g. migration): sequence is NOT advanced
INSERT INTO customers (id, name) VALUES (1,'Asha'), (2,'Ravi'), (3,'Meena');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: currval before any nextval in this session fails
SELECT currval('invoice_no_seq');
-- ERROR: currval of sequence "invoice_no_seq" is not yet defined in this session

-- Step 2: nextval / currval
SELECT nextval('invoice_no_seq');   -- 1000
SELECT nextval('invoice_no_seq');   -- 1001
SELECT currval('invoice_no_seq');   -- 1001

-- Step 3: setval(seq, value)        -> next nextval returns value+1
SELECT setval('invoice_no_seq', 5000);
SELECT nextval('invoice_no_seq');   -- 5001
-- setval(seq, value, false)         -> next nextval returns value itself
SELECT setval('invoice_no_seq', 7000, false);
SELECT nextval('invoice_no_seq');   -- 7000

-- Step 4: the duplicate key bug (sequence still at 1, ids 1..3 exist)
INSERT INTO customers (name) VALUES ('Karan');
-- ERROR: duplicate key value violates unique constraint "customers_pkey"

-- Step 5: the fix -- resync the sequence to MAX(id)
SELECT setval(pg_get_serial_sequence('customers', 'id'),
              (SELECT MAX(id) FROM customers));
INSERT INTO customers (name) VALUES ('Karan') RETURNING id;

-- Step 6: rollback does NOT give the number back
BEGIN;
SELECT nextval('invoice_no_seq');   -- 7001
ROLLBACK;
SELECT nextval('invoice_no_seq');   -- 7002  (7001 is a permanent gap)

-- ============================================
-- EXPECTED OUTPUT (real, PGlite = PostgreSQL 18)
-- ============================================

-- nextval: 1000, 1001 | currval: 1001 | setval -> 5000, next 5001
-- setval(...,false) -> 7000, next 7000
-- Step 5: setval returns 3, INSERT ... RETURNING id -> 4
-- Step 6: 7001 inside the rolled-back tx, then 7002
-- Note: in my run the failed INSERT in Step 4 also burned a sequence value; resync fixed it.
```

---

## 🔍 Why This Works (3 lines max)
Sequences are designed for concurrency, so nextval is never rolled back and never blocks other sessions; the price is gaps. Explicit-id inserts bypass the default `nextval(...)`, so the counter lags behind until you `setval` it to MAX(id).
हिंदी: Sequence concurrency के लिए बना है इसलिए rollback नहीं होता; explicit id insert करने पर counter पीछे रह जाता है, setval से ठीक करो।

---

## ⚡ Alternative Solution

```sql
-- Modern standard way (PostgreSQL 10+): identity column instead of SERIAL
CREATE TABLE tickets (
  id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title TEXT
);
INSERT INTO tickets (title) VALUES ('a'), ('b') RETURNING id;   -- 1, 2

-- Inspect all sequences:
SELECT sequencename, last_value, increment_by FROM pg_sequences WHERE schemaname = 'public';
-- customers_id_seq 4 1 | invoice_no_seq 7002 1 | tickets_id_seq 2 1

-- MySQL: AUTO_INCREMENT; last id = SELECT LAST_INSERT_ID(); reset = ALTER TABLE t AUTO_INCREMENT = 5000;
-- MySQL 5.7 InnoDB lost the counter on restart; 8.0+ persists it. Gaps also happen on rollback there.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Using currval()/MAX(id)+1 to get "the id I just inserted" under concurrency
SELECT MAX(id) + 1 FROM customers;      -- race condition: two sessions get the same id
-- ✅ INSERT ... RETURNING id   (or currval in the same session)

-- ❌ Expecting gap-free invoice numbers from a sequence
-- ✅ Legally gap-free numbering needs a counter row locked with SELECT ... FOR UPDATE (slower, serialised)
```

---

## 🎯 Interview Tip (1 line)
Say: "Sequences are non-transactional by design so gaps are normal; I use identity columns and RETURNING, resync with setval after bulk loads, and use a locked counter table only when gap-free numbering is a legal requirement."

---

## 🔗 Related Questions
→ Q195 (Advisory locks) | Q016 (RETURNING clause) | Q017 (SELECT FOR UPDATE)
