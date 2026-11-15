---

# Q160. UUID vs BIGINT — Trade-offs at Scale
# Category: Schema Design
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL 8.0+ | PostgreSQL)

---

## ❓ Question
Should the primary key be an auto-increment BIGINT or a UUID? How do storage size, index locality, and InnoDB's clustered index change the answer, and how do you store UUIDs efficiently in MySQL?

---

## 💡 Quick Concept (2 lines only)
BIGINT is 8 bytes and monotonically increasing (appends to the right edge of the B-tree); random UUIDv4 is 16 bytes (36 as text) and inserts at random leaf pages, causing page splits and cache misses. UUIDs win on global uniqueness and not leaking row counts.
हिंदी: BIGINT छोटा और sequential होता है; random UUID बड़ा है और B-tree में बिखरकर insert होता है, पर globally unique है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 9.1.0 verified)
-- ============================================

CREATE TABLE ev_uuid    (id CHAR(36) PRIMARY KEY, v INT);                 -- anti-pattern: 36 bytes x utf8mb4 collation
CREATE TABLE ev_uuidbin (id BINARY(16) PRIMARY KEY, v INT);               -- good: 16 bytes
CREATE TABLE ev_big     (id BIGINT PRIMARY KEY AUTO_INCREMENT, v INT);    -- 8 bytes, sequential

-- ============================================
-- SOLUTION
-- ============================================
-- Step 1: store UUID compactly. UUID_TO_BIN(uuid, 1) swaps the time fields so that
--         UUIDv1 values become roughly time-ordered => much better insert locality.
INSERT INTO ev_uuidbin VALUES (UUID_TO_BIN(UUID(), 1), 1), (UUID_TO_BIN(UUID(), 1), 2);

-- Step 2: read back as text
SELECT BIN_TO_UUID(id, 1) AS u, LENGTH(id) AS bytes FROM ev_uuidbin;

-- ============================================
-- EXPECTED OUTPUT (values differ per run; lengths are stable)
-- ============================================
-- u                                    | bytes
-- 6e458754-d9a3-11f1-a2fe-5a0f3bfb3b33 | 16
-- 6e45884e-d9a3-11f1-a2fe-5a0f3bfb3b33 | 16     <- same time-ish prefix after the swap => sequential-ish
```

---

## 🔍 Why This Works (3 lines max)
InnoDB stores rows in primary-key order and copies the PK into every secondary index, so a 36-byte random key bloats every index and splits pages on each insert. BINARY(16) with swapped time bits cuts size by more than half and restores near-append behaviour.
हिंदी: InnoDB में PK हर secondary index में copy होती है, इसलिए छोटी और sequential PK बहुत फायदेमंद है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL (verified in PGlite): native uuid type is 16 bytes
CREATE TABLE ev_uuid (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), v INT);   -- gen_random_uuid() built in since PG13
INSERT INTO ev_uuid (v) VALUES (1);
SELECT pg_column_size(id) AS bytes, length(id::text) AS txt_len FROM ev_uuid;  -- 16 | 36
SELECT pg_column_size(1::bigint);                                              -- 8
-- PostgreSQL heap is NOT clustered by PK, so random UUIDs hurt less than in InnoDB, but the index itself
-- still gets random inserts and full-page-write WAL amplification.

-- Time-ordered IDs (best of both): UUIDv7 / ULID / Snowflake (64-bit, k-sortable).
--   PostgreSQL 18 has uuidv7() (NOT run here); MySQL has no native v7 - generate in the app and store BINARY(16).
-- Hybrid: BIGINT internal PK for joins + UUID public_id UNIQUE column for URLs/APIs.
CREATE TABLE accounts (
  id        BIGINT PRIMARY KEY AUTO_INCREMENT,   -- PgSQL: BIGINT GENERATED ALWAYS AS IDENTITY
  public_id BINARY(16) NOT NULL UNIQUE           -- PgSQL: UUID
);
```

---

## ⚠️ Common Mistake

```sql
-- ❌ CHAR(36) / VARCHAR(36) primary key with random UUIDv4 in InnoDB: 36+ bytes in every secondary index, random page splits
CREATE TABLE bad (id CHAR(36) PRIMARY KEY);
-- ❌ INT AUTO_INCREMENT on a table that will exceed 2.1B rows (or 4.29B unsigned) - use BIGINT UNSIGNED
-- ❌ Exposing sequential BIGINT ids publicly (enumeration, business-volume leak)
-- ✅ BINARY(16) + UUID_TO_BIN(..,1), or time-ordered ids, or BIGINT PK + public UUID
```

---

## 🎯 Interview Tip (1 line)
Say: "In InnoDB the PK is the clustered key and is copied into every secondary index, so I prefer a sequential BIGINT or a time-ordered 16-byte ID; if UUIDs are required I store BINARY(16) with UUID_TO_BIN swap or UUIDv7, and keep random UUIDv4 off the clustered key."

---

## 🔗 Related Questions
→ Q165 (AUTO_INCREMENT gaps) | Q166 (AUTO_INCREMENT reset) | Q147 (Multi-tenancy) | Q156 (Database per service)
