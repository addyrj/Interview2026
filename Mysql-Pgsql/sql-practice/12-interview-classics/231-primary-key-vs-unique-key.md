---

# Q231. PRIMARY KEY vs UNIQUE KEY
# Category: Interview Classics
# Difficulty: ⭐ Easy
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the difference between a PRIMARY KEY and a UNIQUE KEY? Can a table have several of each, can they hold NULL, and how does each engine treat NULLs and case in unique columns?

---

## 💡 Quick Concept (2 lines only)
PRIMARY KEY = row identity: exactly one per table, implies NOT NULL + UNIQUE (and in InnoDB it IS the clustered index). UNIQUE KEY = any number per table, only enforces no duplicates, and allows NULL (multiple NULLs allowed).
हिंदी: PRIMARY KEY = row की पहचान, table में एक ही, NULL नहीं; UNIQUE = कई हो सकते हैं, NULL चलता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL version; PostgreSQL version is in Alternative section)
-- ============================================

CREATE TABLE app_users (
  id    INT AUTO_INCREMENT PRIMARY KEY,   -- one PK per table, NOT NULL implied
  email VARCHAR(255) NULL,
  phone VARCHAR(20)  NULL,
  UNIQUE KEY uq_email (email),            -- UNIQUE can be added many times
  UNIQUE KEY uq_phone (phone)
);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: normal rows
INSERT INTO app_users (email, phone) VALUES ('a@x.com', '111');
-- Step 2: NULLs in UNIQUE columns are allowed, and repeated NULLs do not conflict
INSERT INTO app_users (email, phone) VALUES (NULL, '222');
INSERT INTO app_users (email, phone) VALUES (NULL, NULL);
INSERT INTO app_users (email, phone) VALUES (NULL, NULL);

SELECT * FROM app_users;

-- Result:
-- id | email   | phone
-- ---+---------+------
-- 1  | a@x.com | 111
-- 2  | NULL    | 222
-- 3  | NULL    | NULL
-- 4  | NULL    | NULL      <- two rows with NULL email: fine (NULL != NULL)

-- Step 3: duplicates are rejected
INSERT INTO app_users (email, phone) VALUES ('a@x.com', '333');
-- MySQL 9.1: ERROR 1062 (23000): Duplicate entry 'a@x.com' for key 'app_users.uq_email'

INSERT INTO app_users (id, email) VALUES (1, 'z@x.com');
-- MySQL 9.1: ERROR 1062 (23000): Duplicate entry '1' for key 'app_users.PRIMARY'

-- Step 4: PK cannot be NULL, and only one PK exists
CREATE TABLE bad_pk (id INT NULL PRIMARY KEY);
-- MySQL: ERROR 1171: All parts of a PRIMARY KEY must be NOT NULL; if you need NULL in a key, use UNIQUE instead
CREATE TABLE two_pk (a INT PRIMARY KEY, b INT PRIMARY KEY);
-- MySQL: ERROR 1068: Multiple primary key defined
-- (a composite PK is fine: PRIMARY KEY (a, b))

-- Step 5: see the indexes
SELECT INDEX_NAME, NON_UNIQUE, COLUMN_NAME
FROM information_schema.statistics
WHERE table_schema = DATABASE() AND table_name = 'app_users';

-- Result:
-- INDEX_NAME | NON_UNIQUE | COLUMN_NAME
-- -----------+------------+------------
-- PRIMARY    | 0          | id
-- uq_email   | 0          | email
-- uq_phone   | 0          | phone

-- ============================================
-- CASE SENSITIVITY (MySQL vs PostgreSQL)
-- ============================================
CREATE TABLE ci (id INT PRIMARY KEY, email VARCHAR(50) UNIQUE);
INSERT INTO ci VALUES (1, 'Bob@x.com');
INSERT INTO ci VALUES (2, 'bob@x.com');
-- MySQL (default utf8mb4 case-insensitive collation): ERROR 1062 Duplicate entry 'bob@x.com'
-- PostgreSQL: both rows are inserted (default comparison is case-sensitive)
-- PG fix for case-insensitive uniqueness: CREATE UNIQUE INDEX ON ci (lower(email));
```

---

## 🔍 Why This Works (3 lines max)
A PRIMARY KEY is a UNIQUE constraint plus NOT NULL plus the designated row identifier (referenced by foreign keys, the InnoDB clustered index). UNIQUE only builds a unique secondary index, and SQL treats NULL as "unknown", so two NULLs are not considered equal.
हिंदी: NULL = unknown, इसलिए दो NULL आपस में equal नहीं माने जाते और UNIQUE में कई NULL चल जाते हैं।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL version (verified on PGlite)
CREATE TABLE app_users (
  id    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email VARCHAR(255),
  phone VARCHAR(20),
  CONSTRAINT uq_email UNIQUE (email),
  CONSTRAINT uq_phone UNIQUE (phone)
);
-- Same inserts give the same 4 rows (multiple NULLs OK).
-- Duplicate: ERROR: duplicate key value violates unique constraint "uq_email"

-- PostgreSQL 15+ ONLY: make NULLs collide too
CREATE TABLE nn (email VARCHAR(255), CONSTRAINT uq UNIQUE NULLS NOT DISTINCT (email));
INSERT INTO nn VALUES (NULL);
INSERT INTO nn VALUES (NULL);   -- ERROR: duplicate key value violates unique constraint "uq"
-- MySQL has no NULLS NOT DISTINCT; emulate with a generated column: COALESCE(email, '')

-- Table with no PK: InnoDB uses the first NOT NULL UNIQUE index as clustered index,
-- else a hidden 6-byte row id. PostgreSQL has no clustered index concept (heap table).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong belief: "UNIQUE allows only one NULL" (that is SQL Server behaviour)
-- MySQL and PostgreSQL both allow many NULLs in a UNIQUE column (shown above).

-- ❌ Wrong: using a wide/random UUID string as InnoDB PRIMARY KEY
--   every secondary index stores the PK, so a CHAR(36) PK bloats all indexes
--   and random inserts split pages. Prefer BIGINT AUTO_INCREMENT or UUIDv7/BINARY(16).

-- ✅ Correct: surrogate BIGINT PK + UNIQUE constraint on the natural key (email)
```

---

## 🎯 Interview Tip (1 line)
Say: "PK is the single NOT NULL row identifier — in InnoDB it is the clustered index, so I keep it short and monotonic; UNIQUE enforces business uniqueness on natural keys, permits multiple NULLs in both MySQL and Postgres, and I watch collation differences (MySQL is case-insensitive by default, Postgres is not)."

---

## 🔗 Related Questions
→ Q239 (find duplicates) | Q223 (B-Tree index) | Q013 (UPSERT) | Q232 (VARCHAR vs TEXT)
