---

# Q157. Migrations — Zero-Downtime Strategies
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
You must replace `customers.full_name` with `first_name` on a live 500M-row table with no downtime. What are the safe steps, and which ALTERs are instant/online in MySQL vs PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
Use expand -> backfill -> migrate reads -> contract: every step is backward compatible, so old and new app versions both work. Prefer online DDL (INSTANT/INPLACE in MySQL, CONCURRENTLY / NOT VALID in PgSQL) and backfill in small batches.
हिंदी: Expand, backfill, switch, contract - हर step backward compatible; backfill छोटे batches में करो।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 verified)
-- ============================================

CREATE TABLE customers (id INT PRIMARY KEY AUTO_INCREMENT, full_name VARCHAR(100));
INSERT INTO customers (full_name) VALUES ('Asha Rao'),('Bala Iyer'),('Chitra');

-- ============================================
-- SOLUTION (MySQL)
-- ============================================

-- Step 1 EXPAND: add nullable column - metadata only, no table rebuild
ALTER TABLE customers ADD COLUMN first_name VARCHAR(50) NULL, ALGORITHM=INSTANT;

-- Step 2 BACKFILL in small id-range batches (loop from app/script; repeat until 0 rows)
UPDATE customers
SET first_name = SUBSTRING_INDEX(full_name, ' ', 1)
WHERE id BETWEEN 1 AND 2 AND first_name IS NULL;      -- batch 1
UPDATE customers
SET first_name = SUBSTRING_INDEX(full_name, ' ', 1)
WHERE first_name IS NULL;                              -- batch 2 (rest)

-- Step 3: online index build (reads+writes allowed during build)
ALTER TABLE customers ADD INDEX idx_fn (first_name), ALGORITHM=INPLACE, LOCK=NONE;

-- Step 4: tighten to NOT NULL. INSTANT is NOT supported for this; INPLACE rebuilds online.
ALTER TABLE customers MODIFY first_name VARCHAR(50) NOT NULL, ALGORITHM=INSTANT;
--   ERROR 1845 (0A000): ALGORITHM=INSTANT is not supported for this operation. Try ALGORITHM=COPY/INPLACE.
ALTER TABLE customers MODIFY first_name VARCHAR(50) NOT NULL, ALGORITHM=INPLACE, LOCK=NONE;   -- OK

-- Step 5: deploy app reading first_name only, THEN contract
ALTER TABLE customers DROP COLUMN full_name, ALGORITHM=INSTANT;                               -- OK

-- ============================================
-- EXPECTED OUTPUT (after step 2)
-- ============================================
-- id | full_name | first_name
-- 1  | Asha Rao  | Asha
-- 2  | Bala Iyer | Bala
-- 3  | Chitra    | Chitra
-- Step 4 INSTANT attempt fails (error above) - this is why you always spell out ALGORITHM=: MySQL errors
-- instead of silently doing a blocking COPY.
```

---

## 🔍 Why This Works (3 lines max)
Each step is individually safe and reversible, and old code keeps working because nothing is removed until readers have moved. Explicit `ALGORITHM=`/`LOCK=` makes MySQL fail fast instead of taking a long metadata/table lock.
हिंदी: ALGORITHM साफ लिखो ताकि blocking COPY की जगह error आए; पुराना column सबसे आखिर में हटाओ।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (verified in PGlite / PostgreSQL WASM)
ALTER TABLE customers ADD COLUMN first_name VARCHAR(50);          -- instant (no default rewrite since PG11)
-- backfill in batches:
UPDATE customers SET first_name = split_part(full_name,' ',1)
WHERE id IN (SELECT id FROM customers WHERE first_name IS NULL LIMIT 10000);
CREATE INDEX CONCURRENTLY idx_cust_fn ON customers (first_name);  -- no write lock (cannot run inside a txn block)

-- Add NOT NULL without a long ACCESS EXCLUSIVE scan:
ALTER TABLE customers ADD CONSTRAINT chk_fn_nn CHECK (first_name IS NOT NULL) NOT VALID; -- brief lock only
-- (new writes are checked immediately: my test INSERT without first_name already FAILED here, so the app
--  must write first_name BEFORE this step)
UPDATE customers SET first_name = split_part(full_name,' ',1) WHERE first_name IS NULL;
ALTER TABLE customers VALIDATE CONSTRAINT chk_fn_nn;              -- scans, but only SHARE UPDATE EXCLUSIVE lock
ALTER TABLE customers ALTER COLUMN first_name SET NOT NULL;       -- PG12+ reuses the validated CHECK, skips the scan
ALTER TABLE customers DROP CONSTRAINT chk_fn_nn;
-- Result verified: pg_constraint shows customers_first_name_not_null, convalidated = true

-- Big tables on MySQL: gh-ost / pt-online-schema-change (shadow table + triggers/binlog) - NOT run here.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Single-shot rename/drop on a live table: old app instances crash mid-deploy
ALTER TABLE customers RENAME COLUMN full_name TO name;   -- breaks every running old version
-- ❌ One giant UPDATE of 500M rows: huge undo log, long locks, replica lag
UPDATE customers SET first_name = ...;                    -- no WHERE/batching
-- ✅ Batches of 5-10k rows with sleeps, watch replica lag; ADD -> backfill -> switch -> DROP in separate releases
```

---

## 🎯 Interview Tip (1 line)
Say: "I follow expand/contract, use ALGORITHM=INSTANT/INPLACE or CREATE INDEX CONCURRENTLY plus NOT VALID constraints, backfill in throttled batches, and use gh-ost for rebuilds that can't be online - and never drop a column in the same release that stops reading it."

---

## 🔗 Related Questions
→ Q156 (Database per service) | Q158 (Generated columns) | Q159 (Check constraints) | Q164 (Binary log)
