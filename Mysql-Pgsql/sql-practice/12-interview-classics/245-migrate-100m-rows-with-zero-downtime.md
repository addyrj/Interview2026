---

# Q245. How Would You Migrate 100M Rows With Zero Downtime?
# Category: Interview Classics
# Difficulty: ⭐⭐⭐ Hard
# DB: Both

---

## ❓ Question
You must add and backfill a new column (and later a unique constraint) on a 100M-row users table without downtime. Describe the expand / backfill / contract strategy and show it working on a small table.

---

## 💡 Quick Concept (2 lines only)
Never rewrite a huge table in one locking statement: Expand (add nullable column, dual-write via app or trigger), Backfill in small keyset batches, Verify, then Contract (enforce constraints, switch reads, drop old). Every step is backwards-compatible and reversible.
हिंदी: एक बड़ा ALTER नहीं; नया column जोड़ो, dual-write चालू करो, छोटे batches में backfill करो, verify करके constraints लगाओ।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8; 1,000 rows stand in for 100M)
-- ============================================

SET SESSION cte_max_recursion_depth = 5000;
CREATE TABLE users (
  id    BIGINT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(100) NOT NULL
);
INSERT INTO users (email)
WITH RECURSIVE n AS (SELECT 1 i UNION ALL SELECT i+1 FROM n WHERE i < 1000)
SELECT CONCAT('User', i, '@Example.COM') FROM n;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1 EXPAND: add a nullable column (metadata-only / instant, no table rewrite)
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(100) NULL, ALGORITHM=INSTANT;

-- Step 2 DUAL-WRITE: new/updated rows are populated automatically (or do this in app code)
DELIMITER //
CREATE TRIGGER trg_users_bi BEFORE INSERT ON users FOR EACH ROW SET NEW.email_normalized = LOWER(NEW.email)//
CREATE TRIGGER trg_users_bu BEFORE UPDATE ON users FOR EACH ROW SET NEW.email_normalized = LOWER(NEW.email)//
DELIMITER ;

INSERT INTO users (email) VALUES ('NewSignup@Example.COM');   -- id 1001, filled by the trigger

-- Step 3 BACKFILL: keyset batches by primary-key range, each its own short transaction.
-- In production: 5,000-10,000 rows per batch, sleep between batches, watch replica lag.
UPDATE users SET email_normalized = LOWER(email) WHERE id >    0 AND id <=  400 AND email_normalized IS NULL;
SELECT ROW_COUNT() AS rows_updated;   -- 400
UPDATE users SET email_normalized = LOWER(email) WHERE id >  400 AND id <=  800 AND email_normalized IS NULL;
SELECT ROW_COUNT() AS rows_updated;   -- 400
UPDATE users SET email_normalized = LOWER(email) WHERE id >  800 AND id <= 1200 AND email_normalized IS NULL;
SELECT ROW_COUNT() AS rows_updated;   -- 200 (row 1001 already filled by trigger)

-- Step 4 VERIFY before enforcing anything
SELECT COUNT(*) AS total_rows, SUM(email_normalized IS NULL) AS still_null FROM users;
-- total_rows | still_null
-- 1001       | 0
SELECT COUNT(*) AS mismatches FROM users WHERE email_normalized <> LOWER(email);
-- mismatches
-- 0

-- Step 5 CONTRACT: enforce, index, remove temporary machinery
ALTER TABLE users MODIFY email_normalized VARCHAR(100) NOT NULL;   -- online DDL, may rebuild: use gh-ost/pt-osc at 100M
ALTER TABLE users ADD UNIQUE INDEX uq_users_email_norm (email_normalized);
DROP TRIGGER trg_users_bi;
DROP TRIGGER trg_users_bu;

SELECT id, email, email_normalized FROM users WHERE id IN (1, 1001);
-- id  | email             | email_normalized
-- 1   | User1@Example.COM | user1@example.com
-- (id 1001 returns NewSignup@Example.COM / newsignup@example.com on PostgreSQL's run; same logic)

-- ============================================
-- PostgreSQL version (ran on PGlite) - differences only
-- ============================================
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(100);        -- nullable, no default = instant
CREATE FUNCTION fn_users_normalize() RETURNS trigger AS $$
BEGIN NEW.email_normalized := LOWER(NEW.email); RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER trg_users_normalize BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION fn_users_normalize();

-- batch with SKIP LOCKED so it never fights live traffic; reports rows updated
WITH batch AS (SELECT id FROM users WHERE id > 0 AND id <= 400 AND email_normalized IS NULL
               ORDER BY id FOR UPDATE SKIP LOCKED),
     upd AS (UPDATE users u SET email_normalized = LOWER(u.email) FROM batch WHERE u.id = batch.id RETURNING 1)
SELECT COUNT(*) AS rows_updated FROM upd;                          -- 400
SELECT COUNT(*) AS total_rows, COUNT(*) FILTER (WHERE email_normalized IS NULL) AS still_null FROM users;
-- 1001 | 600   (trigger already filled the new signup)
-- after the 2 remaining batches: 1001 | 0  and mismatches = 0

-- PostgreSQL non-blocking NOT NULL: validate a CHECK without a long lock, then promote it
ALTER TABLE users ADD CONSTRAINT chk_email_norm_nn CHECK (email_normalized IS NOT NULL) NOT VALID;
ALTER TABLE users VALIDATE CONSTRAINT chk_email_norm_nn;           -- scans without blocking writes
ALTER TABLE users ALTER COLUMN email_normalized SET NOT NULL;      -- fast: PG 12+ uses the validated CHECK
-- At 100M rows build the index with: CREATE UNIQUE INDEX CONCURRENTLY uq_users_email_norm ON users (email_normalized);
-- (CONCURRENTLY cannot run inside a transaction; the plain CREATE UNIQUE INDEX was what ran on PGlite.)

-- NOT RUN (cannot be reproduced here): gh-ost / pt-online-schema-change / pg_repack on 100M rows, replica lag
-- monitoring, CDC (Debezium) based table-to-table copy, and the final cut-over of reads/writes.
```

---

## 🔍 Why This Works (3 lines max)
Each step is small, online and backward compatible, so the old app version keeps working at every point and any step can be rolled back. Batched keyset updates hold locks for milliseconds, keep undo/WAL and replica lag bounded, and the trigger guarantees no row is missed during the backfill.
हिंदी: हर step छोटा और reversible है; batches से lock कम रहता है और trigger से कोई row नहीं छूटती।

---

## ⚡ Alternative Solution

```sql
-- Shadow-table copy (for changes ALTER can't do online, e.g. changing PK or partitioning):
-- 1. CREATE TABLE users_new (...new shape...)
-- 2. Triggers (or CDC/binlog/logical replication) copy ongoing writes users -> users_new
-- 3. Copy history in chunks:  INSERT INTO users_new SELECT ... WHERE id > :last ORDER BY id LIMIT 10000
-- 4. Verify counts + checksums, then atomically swap:  RENAME TABLE users TO users_old, users_new TO users;  (MySQL)
--    PostgreSQL: BEGIN; ALTER TABLE users RENAME TO users_old; ALTER TABLE users_new RENAME TO users; COMMIT;
-- Tools doing exactly this: gh-ost (binlog based), pt-online-schema-change (triggers), pg_repack, pglogical.
-- Rollout order: deploy dual-write app -> backfill -> switch reads (feature flag) -> stop old writes -> drop old column.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ One giant statement: locks/undo/WAL explode, replicas lag for hours, long transaction blocks DDL
UPDATE users SET email_normalized = LOWER(email);          -- 100M rows in one transaction

-- ❌ OFFSET paging for backfill (OFFSET 50000000 gets slower each batch)
-- ❌ Adding NOT NULL DEFAULT / unique index first -> long lock or table rewrite (engine/version dependent)
-- ❌ Dropping the old column in the same deploy -> no rollback path
-- ✅ Keyset batches (WHERE id > :last ORDER BY id LIMIT n), throttle, verify, then contract in a later release
```

---

## 🎯 Interview Tip (1 line)
Say: "Expand, dual-write, backfill in throttled keyset batches, verify, then contract: no step takes a long lock, each is backward compatible and reversible, I watch replica lag, and for changes that can't be done online I use a shadow table with gh-ost, pt-osc or pg_repack and an atomic rename cut-over."

---

## 🔗 Related Questions
→ Q241 (Sharding) | Q242 (SELECT FOR UPDATE) | Q221 (DELETE vs TRUNCATE vs DROP) | Q225 (ACID real examples)
