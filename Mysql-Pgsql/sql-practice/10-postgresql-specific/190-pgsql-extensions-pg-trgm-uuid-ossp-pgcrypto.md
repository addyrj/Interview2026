---

# Q190. PgSQL Extensions — pg_trgm, uuid-ossp, pgcrypto
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL only (verified on PostgreSQL 18.6 via PGlite with contrib extensions)

---

## ❓ Question
What are PostgreSQL extensions and how do you install them? Show fuzzy/substring search with `pg_trgm` (and its GIN index), UUID generation with `uuid-ossp` (vs built-in `gen_random_uuid`), and password hashing / digests / encryption with `pgcrypto`.

---

## 💡 Quick Concept (2 lines only)
`CREATE EXTENSION name` loads packaged SQL objects (types, functions, operators, index classes) into the current database. `pg_trgm` adds trigram similarity and makes `LIKE '%x%'` indexable, `uuid-ossp` generates UUIDs, and `pgcrypto` provides hashing, `crypt()` password storage and encryption.
हिंदी: `CREATE EXTENSION` से extra features जुड़ते हैं; pg_trgm fuzzy search देता है, uuid-ossp UUID बनाता है, pgcrypto hashing/encryption देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first; needs superuser or a trusted extension; per database)
-- ============================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- hyphen in name => must be quoted
CREATE EXTENSION IF NOT EXISTS pgcrypto;

SELECT extname, extversion FROM pg_extension ORDER BY 1;
-- pg_trgm   | 1.6
-- pgcrypto  | 1.4
-- plpgsql   | 1.0
-- uuid-ossp | 1.1
-- (versions from PostgreSQL 18.6 in PGlite)

-- ============================================
-- SOLUTION 1: pg_trgm
-- ============================================

SELECT show_trgm('postgres');
-- {"  p"," po",es ,gre,ost,pos,res,stg,tgr}      (3-character windows, padded)

SELECT round(similarity('postgres','postgress')::numeric,3) AS s1,
       round(similarity('postgres','mysql')::numeric,3)     AS s2,
       'postgres' % 'postgress'                              AS is_similar;
-- s1 = 0.727 | s2 = 0.000 | is_similar = true       (% uses pg_trgm.similarity_threshold, default 0.3)

CREATE TABLE customers (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO customers (name) VALUES
 ('Aditya Ranjan'),('Adithya Ranjan'),('Aditi Rao'),('Rohan Mehta'),
 ('Priya Sharma'),('Priyanka Sharma'),('Ravi Kumar');

-- Typo-tolerant lookup
SELECT name, round(similarity(name,'Adityaa Ranjn')::numeric,3) AS sim
FROM customers WHERE name % 'Adityaa Ranjn' ORDER BY sim DESC, name;
-- Aditya Ranjan  | 0.556
-- Adithya Ranjan | 0.381
-- Aditi Rao      | 0.333

-- Index for LIKE '%...%' / ILIKE / similarity on 30,000 rows
CREATE TABLE names_big AS SELECT i AS id, md5(i::text) AS name FROM generate_series(1,30000) i;
CREATE INDEX idx_names_trgm ON names_big USING GIN (name gin_trgm_ops);
ANALYZE names_big;
SET enable_seqscan = off;      -- to show applicability on this small table
EXPLAIN SELECT id FROM names_big WHERE name ILIKE '%abcd%';
-- Bitmap Index Scan on idx_names_trgm      <- a plain B-tree can NOT serve a leading wildcard
EXPLAIN SELECT id FROM names_big WHERE name % 'abcdef12';
-- Bitmap Index Scan on idx_names_trgm
RESET enable_seqscan;

-- ============================================
-- SOLUTION 2: uuid-ossp (and the built-in alternative)
-- ============================================

SELECT length(uuid_generate_v4()::text) AS len;                 -- 36 (random UUID)
SELECT uuid_generate_v5(uuid_ns_url(), 'https://example.com');  -- deterministic (name-based)
-- 4fd35a71-71ef-5a55-a9d9-aa75c889a6d0        (same input -> same UUID, always)
SELECT length(gen_random_uuid()::text) AS len;                  -- 36; built into core since PG13, no extension needed

-- ============================================
-- SOLUTION 3: pgcrypto
-- ============================================

CREATE TABLE app_users (id SERIAL PRIMARY KEY, email TEXT, pwd_hash TEXT);
INSERT INTO app_users (email, pwd_hash) VALUES ('a@x.com', crypt('s3cret', gen_salt('bf', 8)));   -- bcrypt, cost 8

SELECT email,
       pwd_hash = crypt('s3cret', pwd_hash) AS right_pw,
       pwd_hash = crypt('wrong',  pwd_hash) AS wrong_pw,
       left(pwd_hash, 7)                    AS prefix
FROM app_users;
-- email   | right_pw | wrong_pw | prefix
-- a@x.com | true     | false    | $2a$08$           <- bcrypt, salt+cost embedded in the hash

SELECT encode(digest('hello','sha256'),'hex');
-- 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
SELECT encode(hmac('payload','key','sha256'),'hex');
-- 5d98b45c90a207fa998ce639fea6f02ecc8cc3f36fef81d694fb856b4d0a28ca
SELECT pgp_sym_decrypt(pgp_sym_encrypt('card-4111','passphrase'),'passphrase');   -- card-4111
SELECT length(gen_random_bytes(16));                                              -- 16

-- ============================================
-- What PGlite could not do
-- ============================================
CREATE EXTENSION pg_stat_statements;
-- ERROR: extension "pg_stat_statements" is not available   (not bundled in this WASM build; works on a real server
-- with shared_preload_libraries = 'pg_stat_statements' + restart. Not verified here.)
```

---

## 🔍 Why This Works (3 lines max)
An extension is a versioned bundle (`.control` + SQL script + shared library) registered in `pg_extension`, so objects are created, upgraded (`ALTER EXTENSION ... UPDATE`) and dropped as a unit. Trigram GIN indexes break each string into 3-character chunks, so a substring search becomes a posting-list intersection. bcrypt in `crypt()` embeds salt and cost in the hash string, so verification just re-hashes with the stored value.
हिंदी: Extension एक versioned bundle है; trigram index तीन-अक्षर टुकड़ों से `%x%` search तेज़ करता है, और crypt() hash में salt व cost खुद रहते हैं।

---

## ⚡ Alternative Solution

```sql
-- UUIDs without extensions:
SELECT gen_random_uuid();             -- PG13+ core, v4
SELECT uuidv7();                      -- PG18+ core, time-ordered (index-friendly); verified, returns a 36-char UUID

-- Sort-friendly key alternatives: bigint IDENTITY, ULID/UUIDv7 (avoid random-UUID B-tree page splits).

-- Hash passwords in the application (bcrypt/argon2) rather than SQL, so plaintext never reaches DB logs.
-- pgcrypto's crypt()/pgp_sym_* put the secret in the statement text (visible in logs / pg_stat_statements).

-- MySQL contrast:
--   UUID() / UUID_TO_BIN(uuid, 1) (swap flag for time-ordering), SHA2('x',256), no extension system,
--   fuzzy search: SOUNDEX() / FULLTEXT / external engine; no trigram index.

-- Check what is available on a real server:
SELECT name, default_version, installed_version FROM pg_available_extensions ORDER BY name;
```

---

## ⚠️ Common Mistake

```sql
-- ❌ CREATE EXTENSION uuid-ossp;           -- syntax error (unquoted hyphen)
-- ✅ CREATE EXTENSION "uuid-ossp";

-- ❌ Using LIKE '%term%' with only a B-tree index  -> seq scan
-- ✅ GIN (col gin_trgm_ops)  (or GiST for ORDER BY col <-> 'term' nearest-neighbour)

-- ❌ Installing in one database and expecting it in another: extensions are per database
--    (and in a specific schema; pick it deliberately, e.g. CREATE EXTENSION pgcrypto SCHEMA extensions).

-- ❌ Storing MD5/SHA of a password: digest('pw','sha256') is fast to brute-force
-- ✅ crypt(pw, gen_salt('bf', 12)) or argon2 in the app.

-- ❌ pg_stat_statements without shared_preload_libraries -> "must be loaded via shared_preload_libraries".
```

---

## 🎯 Interview Tip (1 line)
Say: "Extensions are installed per database and reviewed for managed-service support; I use pg_trgm with GIN for substring and typo-tolerant search, built-in gen_random_uuid or UUIDv7 instead of uuid-ossp, and hash passwords in the app rather than leaking secrets into SQL logs via pgcrypto."

---

## 🔗 Related Questions
→ Q184 (Full-text search) | Q182 (GIN indexes) | Q178 (Slow query log / pg_stat_statements) | Q004 (LIKE vs ILIKE)
