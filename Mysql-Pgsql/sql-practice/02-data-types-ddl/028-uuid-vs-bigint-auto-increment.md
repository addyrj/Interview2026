---

# Q028. UUID Primary Key vs BIGINT AUTO_INCREMENT
# Category: Data Types & DDL
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL 13+; uuidv7() needs PostgreSQL 18)

---

## ❓ Question
Should a primary key be a UUID or a BIGINT auto-increment? Compare size, index locality, insert performance, security/leakage and distributed-ID needs. How do you store UUIDs efficiently in MySQL and PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
BIGINT sequences are small (8 bytes) and monotonic, so inserts append to the right edge of the B-tree; random UUIDv4 keys (16 bytes) scatter inserts across pages, causing page splits and cache churn — but they can be generated anywhere without coordination and do not leak row counts. Time-ordered UUIDs (v7, or MySQL's swapped UUID_TO_BIN) give most of both benefits.
हिंदी: BIGINT छोटा और क्रमबद्ध है; random UUID बड़ा और बिखरा हुआ है पर कहीं भी generate हो सकता है; UUIDv7 दोनों का बीच का रास्ता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+ / 9.x) — run this first
-- ============================================

-- Option A: BIGINT AUTO_INCREMENT (default choice)
CREATE TABLE orders_seq (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  customer_id INT NOT NULL,
  total       DECIMAL(10,2)
);

-- Option B: UUID stored compactly as BINARY(16)
CREATE TABLE orders_uuid (
  id          BINARY(16) PRIMARY KEY,
  customer_id INT NOT NULL,
  total       DECIMAL(10,2)
);

-- Option C: UUID as CHAR(36) — anti-pattern (36 bytes x utf8mb4 index overhead, copied into every secondary index)
CREATE TABLE orders_uuid_char (
  id          CHAR(36) PRIMARY KEY,
  customer_id INT NOT NULL,
  total       DECIMAL(10,2)
);

-- ============================================
-- SOLUTION
-- ============================================

INSERT INTO orders_seq (customer_id, total) VALUES (1, 99.50), (2, 10.00);
INSERT INTO orders_uuid VALUES (UUID_TO_BIN(UUID(), 1), 1, 99.50), (UUID_TO_BIN(UUID(), 1), 2, 10.00);
-- second arg 1 = swap_flag: moves the time-low/time-high parts to the front so keys are roughly ascending

SELECT id, customer_id FROM orders_seq;
-- id | customer_id
-- 1  | 1
-- 2  | 2

SELECT LENGTH(id) AS bin_bytes, LENGTH(BIN_TO_UUID(id, 1)) AS text_len FROM orders_uuid;
-- bin_bytes | text_len
-- 16        | 36              (two rows, same values)

-- What the swap flag does (known UUID v1 input):
SELECT HEX(UUID_TO_BIN('6ccd780c-baba-1026-9564-5b8c656024db'))    AS no_swap,
       HEX(UUID_TO_BIN('6ccd780c-baba-1026-9564-5b8c656024db', 1)) AS with_swap;
-- no_swap   | 6CCD780CBABA102695645B8C656024DB
-- with_swap | 1026BABA6CCD780C95645B8C656024DB      <- timestamp bytes now lead => sequential-ish
-- NOTE: the swap flag only helps with UUID v1 (MySQL's UUID()); random v4 stays random.

-- ============================================
-- PostgreSQL version (verified on PostgreSQL 18 via PGlite)
-- ============================================
CREATE TABLE orders_seq  (id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, customer_id INT NOT NULL, total NUMERIC(10,2));
CREATE TABLE orders_uuid (id UUID PRIMARY KEY DEFAULT gen_random_uuid(),       customer_id INT NOT NULL, total NUMERIC(10,2));

SELECT pg_column_size(id) AS uuid_bytes, length(id::text) AS text_len, pg_typeof(id) AS typ FROM orders_uuid LIMIT 1;
-- uuid_bytes | text_len | typ
-- 16         | 36       | uuid          <- native 16-byte type, no BINARY(16) gymnastics needed
SELECT pg_column_size(1::bigint) AS bigint_bytes;                     -- 8
SELECT gen_random_uuid() <> gen_random_uuid() AS unique_each_call;    -- true  (v4, built in since PG 13)
SELECT uuidv7();                                                      -- e.g. 01a1af4d-de1c-7fff-8e50-7b68aeaf41f8 (time-ordered, PG 18+)
SELECT '123'::uuid;                                                   -- ERROR: invalid input syntax for type uuid: "123"
SELECT 'AAAAAAAA-bbbb-4ccc-8ddd-eeeeeeeeeeee'::uuid::text;            -- aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee (normalized lowercase)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Copied from MySQL 9.1.0 and PostgreSQL 18 (PGlite). UUID values change on every run.
-- Insert-throughput / index-bloat claims below are standard B-tree behaviour; they were
-- NOT benchmarked in this run.
```

---

## 🔍 Why This Works (3 lines max)
In InnoDB the primary key is the clustered index and is copied into every secondary index, so a 16-byte (or 36-byte text) key bloats everything and random keys split pages all over the tree. PostgreSQL heap tables are not clustered, so the penalty is mostly index-side (WAL volume, cache misses), but the same locality argument applies to the PK index.
हिंदी: InnoDB में PK हर secondary index में कॉपी होती है, इसलिए बड़ी और random PK सब कुछ भारी कर देती है।

---

## ⚡ Alternative Solution

```sql
-- Decision guide
--   Single DB, internal ids, high insert rate ........ BIGINT AUTO_INCREMENT / IDENTITY
--   Public-facing ids (URLs/APIs) ................... keep BIGINT PK + add a separate UUID/NanoID column (UNIQUE) for exposure
--   Multi-writer / offline clients / sharded .......... UUIDv7 (PG18 uuidv7(), app-side libraries), ULID, or Snowflake-style BIGINT
--   Merging data from many systems ................... UUID (no collisions)

-- Hybrid: BIGINT clustered PK + external UUID (MySQL)
CREATE TABLE orders_hybrid (
  id         BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,   -- joins, FKs, clustering
  public_id  BINARY(16) NOT NULL UNIQUE,                   -- what the API exposes
  total      DECIMAL(10,2)
);
INSERT INTO orders_hybrid (public_id, total) VALUES (UUID_TO_BIN(UUID(), 1), 10.00);

-- PostgreSQL 18: time-ordered default
CREATE TABLE orders_v7 (id UUID PRIMARY KEY DEFAULT uuidv7(), total NUMERIC(10,2));
-- Before PG 18: generate UUIDv7 in the app, or use an extension (e.g. pg_uuidv7).

-- Sizes: BIGINT 8 B | UUID 16 B | CHAR(36) 36 B (utf8mb4 can reserve up to 144 B in some buffers)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: PRIMARY KEY CHAR(36) / VARCHAR(36) in MySQL InnoDB — fat clustered key repeated in all secondary indexes
-- ❌ Wrong: random UUIDv4 clustered PK on a write-heavy InnoDB table (page splits, ~50% fill, poor buffer-pool hit rate)
-- ❌ Wrong: using UUID_TO_BIN(uuid, 1) but reading with BIN_TO_UUID(id) (flag mismatch => different string)
-- ❌ Wrong: exposing sequential BIGINT ids in URLs  => enumeration attacks (/orders/1001, /orders/1002) and row-count leakage
--          (an unguessable id does NOT replace authorization checks, though)

-- ✅ Correct: BINARY(16)/native UUID, time-ordered (v7 or swapped v1), same swap flag on write and read
```

---

## 🎯 Interview Tip (1 line)
Say: "Default to BIGINT identity for locality and size; use time-ordered UUIDs (v7) only when ids must be generated client-side or across shards, stored as BINARY(16) in MySQL or native uuid in PostgreSQL — never random UUIDv4 or CHAR(36) as a clustered key."

---

## 🔗 Related Questions
→ Q029 (SERIAL vs IDENTITY vs AUTO_INCREMENT) | Q021 (INT vs BIGINT) | Q030 (PRIMARY KEY / UNIQUE) | Q022 (CHAR/VARCHAR)
