---

# Q220. Zero-Downtime Schema Migration — Expand/Contract Pattern
# Category: Replication & Scaling
# Difficulty: ⭐⭐⭐⭐ Expert
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
How do you add a NOT NULL column, rename a column, and change a column type on a 100M row production table without downtime? Explain the Expand/Contract pattern step by step.

---

## 💡 Quick Concept (2 lines only)
Expand/Contract (a.k.a. Parallel Change) splits any breaking schema change into phases: expand (add new, keep old), transition (backfill, dual-write), contract (remove old). Each phase deploys independently — no downtime, no rollback panic.
हिंदी: Expand/Contract = 3 phases: expand (नया add करो), transition (backfill + dual write), contract (पुराना remove करो)। हर phase separate deploy।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SCENARIO 1: ADD NOT NULL COLUMN WITH DEFAULT
-- (DANGEROUS if done naively on large table!)
-- ============================================

-- BAD (causes full table rewrite in older MySQL / full lock in PgSQL):
ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL DEFAULT '';
-- MySQL 5.x: rewrites entire 100M row table! Minutes/hours of downtime
-- MySQL 8.0+: better but still risky
-- PgSQL: if DEFAULT is not volatile (constant), PgSQL 11+ adds it without rewrite!
--        But NOT NULL with DEFAULT may still need backfill verification

-- ✅ SAFE: Expand/Contract Pattern

-- PHASE 1: EXPAND — Add nullable column (instant — no table rewrite!)
ALTER TABLE users ADD COLUMN phone_new VARCHAR(20) NULL DEFAULT NULL;
-- NULL column with no DEFAULT → instant metadata change, no row rewrite
-- Deploy → app still works (column is nullable, app ignores it)

-- PHASE 2: BACKFILL in batches (no locking!)
DO $$
DECLARE
  batch_size INT := 1000;
  min_id BIGINT;
  max_id BIGINT;
  current_id BIGINT;
BEGIN
  SELECT MIN(id), MAX(id) INTO min_id, max_id FROM users;
  current_id := min_id;
  WHILE current_id <= max_id LOOP
    UPDATE users
    SET phone_new = COALESCE(phone, '')  -- backfill from old column
    WHERE id >= current_id AND id < current_id + batch_size
      AND phone_new IS NULL;
    current_id := current_id + batch_size;
    PERFORM pg_sleep(0.01);  -- 10ms pause to reduce I/O pressure
  END LOOP;
END $$;

-- MySQL equivalent:
-- Run in a loop from application or migration script:
UPDATE users SET phone_new = COALESCE(phone, '')
WHERE id >= ? AND id < ? AND phone_new IS NULL;
-- Run 1000 rows at a time with sleep between batches

-- PHASE 3: DEPLOY APP to dual-write (write to BOTH old and new column)
-- App reads from old column, writes to both:
-- INSERT INTO users (phone, phone_new) VALUES (?, ?)
-- UPDATE users SET phone = ?, phone_new = ? WHERE id = ?

-- PHASE 4: ADD NOT NULL constraint (after backfill is complete)
-- First verify no NULLs remain:
SELECT COUNT(*) FROM users WHERE phone_new IS NULL;
-- Must be 0!

-- PgSQL: add NOT NULL using NOT VALID (fast!) then validate separately:
ALTER TABLE users ADD CONSTRAINT users_phone_not_null
  CHECK (phone_new IS NOT NULL) NOT VALID;
-- NOT VALID: constraint added instantly (doesn't scan existing rows!)

-- Validate in background (scans table but doesn't hold full lock):
ALTER TABLE users VALIDATE CONSTRAINT users_phone_not_null;
-- Holds ShareUpdateExclusiveLock — reads/writes continue!

-- MySQL 8.0: ALTER TABLE is online by default (ALGORITHM=INPLACE, LOCK=NONE)
ALTER TABLE users MODIFY COLUMN phone_new VARCHAR(20) NOT NULL DEFAULT '';

-- PHASE 5: DEPLOY APP to read from new column
-- Switch reads: app reads phone_new instead of phone

-- PHASE 6: CONTRACT — Remove old column
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users RENAME COLUMN phone_new TO phone;  -- PgSQL
-- MySQL: ALTER TABLE users CHANGE phone_new phone VARCHAR(20) NOT NULL;

-- ============================================
-- SCENARIO 2: RENAME A COLUMN (Safest way)
-- ============================================

-- NEVER: ALTER TABLE users RENAME COLUMN email TO email_address;
-- → All existing queries break instantly!

-- Safe rename using virtual column / trigger:

-- PHASE 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255) NULL;

-- PHASE 2: Sync with trigger (PgSQL)
CREATE OR REPLACE FUNCTION sync_email_columns()
RETURNS TRIGGER AS $$
BEGIN
  -- Write to email_address syncs to email and vice versa
  IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
    IF NEW.email IS DISTINCT FROM OLD.email THEN
      NEW.email_address := NEW.email;
    END IF;
    IF NEW.email_address IS DISTINCT FROM OLD.email_address THEN
      NEW.email := NEW.email_address;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_email_cols
  BEFORE INSERT OR UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION sync_email_columns();

-- PHASE 3: Backfill
UPDATE users SET email_address = email WHERE email_address IS NULL;

-- PHASE 4: Deploy app to use new column name (email_address)
-- PHASE 5: Remove trigger
DROP TRIGGER sync_email_cols ON users;
DROP FUNCTION sync_email_columns();
-- PHASE 6: Drop old column
ALTER TABLE users DROP COLUMN email;

-- ============================================
-- SCENARIO 3: CHANGE COLUMN TYPE (e.g., INT → BIGINT)
-- ============================================

-- Same pattern: add new column, backfill, dual-write, switch, drop old

-- PHASE 1: Add bigint column alongside int
ALTER TABLE orders ADD COLUMN id_new BIGINT NULL;

-- PHASE 2: Backfill
UPDATE orders SET id_new = id WHERE id_new IS NULL;

-- PHASE 3: New column becomes the primary key (careful — FK constraints!)
-- Update all foreign key references too (orders.user_id etc.)

-- For INT→BIGINT PK specifically:
-- MySQL 8.0 InnoDB: ALTER TABLE orders MODIFY id BIGINT NOT NULL AUTO_INCREMENT;
-- Uses online DDL — reads/writes continue, rebuild happens in background
-- Verify with: SHOW PROCESSLIST; or monitor innodb_online_ddl_background_merge_events

-- ============================================
-- ADDING AN INDEX WITHOUT DOWNTIME
-- ============================================

-- MySQL 8.0: online DDL (default)
ALTER TABLE orders ADD INDEX idx_status (status),
  ALGORITHM=INPLACE, LOCK=NONE;
-- Reads/writes continue during index build!
-- If LOCK=NONE fails (some DDL types need LOCK=SHARED), MySQL tells you

-- PgSQL: CREATE INDEX CONCURRENTLY (always use this!)
CREATE INDEX CONCURRENTLY idx_orders_status ON orders(status);
-- ← No exclusive lock! Reads/writes continue.
-- Takes 2-3x longer than regular CREATE INDEX (two table scans)
-- Can fail: if it fails, leaves an INVALID index → DROP INDEX and retry

-- Drop invalid index (PgSQL):
SELECT indexname FROM pg_indexes
JOIN pg_index ON pg_indexes.indexname::regclass = pg_index.indexrelid
WHERE NOT pg_index.indisvalid AND tablename = 'orders';
-- If any result: DROP INDEX CONCURRENTLY the invalid index, then recreate

-- ============================================
-- TOOLS FOR SCHEMA MIGRATIONS
-- ============================================

/*
MySQL:
  gh-ost (GitHub's Online Schema Change):
    - Creates shadow table, replicates changes, atomic cutover
    - Works on tables of any size, supports MySQL replication
    - gh-ost --host=master --database=mydb --table=orders
              --alter="ADD COLUMN notes TEXT" --execute

  pt-online-schema-change (Percona Toolkit):
    - Trigger-based approach
    - Older but widely used

PostgreSQL:
  pg_repack:
    - Rebuilds table/indexes without holding locks
    - For reducing bloat or changing storage params

  Flyway / Liquibase:
    - Migration management tools
    - Support PgSQL and MySQL
    - Version-controlled migrations with rollback scripts

  squawker / migra:
    - PgSQL schema diff tools
    - Auto-generate migration SQL from schema differences
*/

-- ============================================
-- CHECKLIST FOR ZERO-DOWNTIME MIGRATION
-- ============================================

/*
Before migration:
  ✅ Test migration on staging with production-size data
  ✅ Measure migration duration on staging (estimate prod time)
  ✅ Have rollback plan for each phase
  ✅ Check for long-running transactions (they block DDL!)
  ✅ Notify team of deployment window

During backfill:
  ✅ Batch size: 1000-5000 rows per batch
  ✅ Sleep 10-50ms between batches (reduce I/O pressure)
  ✅ Monitor slow query log (backfill should not appear there)
  ✅ Monitor replication lag (backfill can cause lag on replicas)

For each ALTER TABLE:
  ✅ PgSQL: use CONCURRENTLY for indexes, NOT VALID for constraints
  ✅ MySQL: specify ALGORITHM=INPLACE, LOCK=NONE and let it fail gracefully
  ✅ Monitor active locks: pg_stat_activity / SHOW PROCESSLIST
  ✅ Set lock_timeout (PgSQL) to prevent indefinite waits:
     SET lock_timeout = '5s';  -- fail if can't acquire lock in 5 seconds
     ALTER TABLE ...;
*/
```

---

## 🔍 Why This Works (3 lines max)
The key insight is that adding a nullable column is instant (metadata change only, no row rewriting), while adding a NOT NULL column triggers row rewrites on large tables. Expand/Contract separates the risky schema changes into safe incremental steps, each independently deployable and rollbackable. PgSQL's `NOT VALID` + `VALIDATE CONSTRAINT` and `CREATE INDEX CONCURRENTLY` are the specific tools that make constraint and index changes lock-free.
हिंदी: Nullable column add = instant (metadata only)। NOT NULL/DEFAULT column = full table rewrite। Expand/Contract = छोटे safe steps में break करो। PgSQL NOT VALID + CONCURRENTLY = lock-free।

---

## ⚡ Alternative Solution

```sql
-- For MySQL at scale: use gh-ost (no need for manual Expand/Contract for many cases):
-- gh-ost --host=master --database=myapp --table=users
--        --alter="ADD COLUMN phone_new VARCHAR(20) NOT NULL DEFAULT ''"
--        --execute --chunk-size=1000 --max-lag-millis=500
-- gh-ost handles the shadow table, triggers, backfill, and atomic cutover automatically
-- Use gh-ost for MySQL tables > 10M rows — much safer than manual ALTER TABLE
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Running ALTER on huge table without CONCURRENTLY / online DDL
CREATE INDEX idx_status ON orders(status);  -- PgSQL
-- Exclusive lock! All reads + writes on orders blocked for minutes/hours!
-- ✅ Fix:
CREATE INDEX CONCURRENTLY idx_status ON orders(status);

-- ❌ Wrong: Forgetting to handle long-running transactions before DDL
-- PgSQL DDL (even CREATE INDEX CONCURRENTLY) waits for all open transactions to complete
-- A 10-minute reporting query blocks your DDL for 10 minutes!
-- ✅ Fix: SET lock_timeout = '5s' — fail fast if blocked, retry later

-- ❌ Wrong: Batch updates without sleep — saturates I/O, causes replication lag
-- ✅ Fix: sleep 10-50ms between batches; monitor replica lag during backfill

-- ❌ Wrong: Dual-write only going one direction
-- If old code writes phone but new code reads phone_new → missing data!
-- ✅ Dual-write must: write BOTH columns when either changes
-- AND: new code must handle NULL phone_new until backfill is complete
```

---

## 🎯 Interview Tip (1 line)
Say: "I use the Expand/Contract pattern: Phase 1 — add new nullable column (instant, no lock); Phase 2 — backfill in small batches with sleep to avoid I/O spikes; Phase 3 — deploy dual-write (write both old and new columns); Phase 4 — verify backfill complete, add NOT NULL constraint with NOT VALID then VALIDATE; Phase 5 — switch reads to new column; Phase 6 — drop old column. Each phase is a separate deploy, fully reversible."

---

## 🔗 Related Questions
→ Q147 (multi-tenancy) | Q181 (JSONB) | Q196 (row-level security) | Q086 (EXPLAIN output) | Q031 (index build concurrently)
