---

# Q022. VARCHAR vs TEXT vs CHAR — Storage Difference
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (behaviour differs a lot between MySQL and PostgreSQL)

---

## ❓ Question
Explain CHAR(n), VARCHAR(n) and TEXT: storage, padding, indexing and comparison behaviour. When should you use each in MySQL vs PostgreSQL?

---

## 💡 Quick Concept (2 lines only)
CHAR(n) is fixed-length (padded), VARCHAR(n) is variable-length with a length limit, TEXT is variable-length for large strings. In PostgreSQL all three share one storage mechanism (TEXT/VARCHAR are equally fast, CHAR just pads); in MySQL TEXT is stored off-page, cannot have a default value and needs a prefix length for indexes.
हिंदी: CHAR fixed, VARCHAR limit वाला variable, TEXT बड़ा variable; PgSQL में तीनों की speed लगभग समान है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL 8.0+ / 9.x) — run this first
-- ============================================

CREATE TABLE products (
  id           INT PRIMARY KEY,
  country_code CHAR(2)      NOT NULL,   -- always exactly 2 letters => CHAR
  sku          CHAR(8)      NOT NULL,   -- fixed-width code
  title        VARCHAR(100) NOT NULL,   -- bounded text, indexed/searched
  description  TEXT                     -- long free text, rarely filtered
);

INSERT INTO products VALUES
  (1, 'IN', 'AB12', 'Cotton Kurta', 'Soft cotton kurta, regular fit'),
  (2, 'US', 'XY99', 'Denim Jacket', NULL);

-- ============================================
-- SOLUTION
-- ============================================

-- 1) CHAR is padded on storage; MySQL strips trailing spaces on READ
SELECT id, CONCAT('[', sku, ']') AS sku_bracketed, LENGTH(sku) AS sku_len, CHAR_LENGTH(title) AS title_chars
FROM products;
-- id | sku_bracketed | sku_len | title_chars
-- 1  | [AB12]        | 4       | 12
-- 2  | [XY99]        | 4       | 12

-- 2) Multibyte: LENGTH() = bytes, CHAR_LENGTH() = characters
SELECT LENGTH('हिंदी') AS bytes, CHAR_LENGTH('हिंदी') AS chars;
-- bytes | chars
-- 15    | 5
-- With utf8mb4 MySQL reserves up to 4 bytes per CHAR/VARCHAR character (see below).

-- 3) Too-long value: strict mode rejects it
INSERT INTO products VALUES (3, 'IND', 'AB12', 'x', 'y');
-- ERROR 1406 (22001): Data too long for column 'country_code' at row 1
-- (with sql_mode='' it is silently truncated: 'TOOLONG123456' -> 'TOOLONG1')

-- 4) Reserved bytes per column (utf8mb4 = up to 4 bytes/char), from information_schema:
SELECT column_name, data_type, character_maximum_length AS max_chars, character_octet_length AS max_bytes
FROM information_schema.columns
WHERE table_schema = DATABASE() AND table_name = 'products' ORDER BY column_name;
-- country_code | char    | 2     | 8
-- description  | text    | 65535 | 65535
-- id           | int     | NULL  | NULL
-- sku          | char    | 8     | 32
-- title        | varchar | 100   | 400

-- 5) Indexing: VARCHAR is fine, TEXT needs a prefix length
CREATE INDEX idx_title ON products(title);                 -- OK
CREATE INDEX idx_desc  ON products(description);
-- ERROR 1170 (42000): BLOB/TEXT column 'description' used in key specification without a key length
CREATE INDEX idx_desc  ON products(description(50));       -- OK: prefix index (first 50 chars)

-- 6) Trailing-space comparison depends on the COLLATION (MySQL 8 default utf8mb4_0900_ai_ci is NO PAD)
SELECT 'ab' COLLATE utf8mb4_general_ci = 'ab   ' COLLATE utf8mb4_general_ci AS pad_space_collation,
       'ab' COLLATE utf8mb4_0900_ai_ci = 'ab   ' COLLATE utf8mb4_0900_ai_ci AS no_pad_default;
-- pad_space_collation | no_pad_default
-- 1                   | 0

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Results above were copied from MySQL 9.1.0 (all blocks run, incl. ERROR 1170 and the
-- working prefix index shown as Sub_part = 50 in SHOW INDEX). Sizes: TEXT max 65,535 bytes (MEDIUMTEXT 16 MB, LONGTEXT 4 GB).
```

---

## 🔍 Why This Works (3 lines max)
MySQL stores VARCHAR as 1-2 length bytes + data inline, CHAR padded to the full width, and TEXT as a pointer to off-page storage once rows get large (InnoDB DYNAMIC). PostgreSQL stores every variable-length string as a varlena (1-4 byte header + data), compresses/TOASTs values over ~2 KB automatically, and CHAR(n) only adds blank padding.
हिंदी: MySQL में TEXT off-page जा सकता है; PgSQL में सब varlena + TOAST से चलते हैं।

---

## ⚡ Alternative Solution

```sql
-- ============================================
-- PostgreSQL (verified on PostgreSQL 18 via PGlite)
-- ============================================
CREATE TABLE products (
  id INT PRIMARY KEY, country_code CHAR(2) NOT NULL, sku CHAR(8) NOT NULL,
  title VARCHAR(100) NOT NULL, description TEXT
);
INSERT INTO products VALUES (1,'IN','AB12','Cotton Kurta','Soft cotton kurta, regular fit'),(2,'US','XY99','Denim Jacket',NULL);

-- CHAR pads in storage (8 octets) but length() ignores the pad:
SELECT id, '[' || sku || ']' AS sku_bracketed, length(sku) AS sku_len, octet_length(sku) AS sku_octets FROM products;
-- 1 | [AB12] | 4 | 8

-- Comparison: char(n) ignores trailing blanks, varchar/text do not
SELECT 'ab'::char(5) = 'ab   '::char(5) AS char_pad_equal, 'ab'::varchar = 'ab   '::varchar AS varchar_equal;
-- true | false

INSERT INTO products VALUES (3,'IND','AB12','x','y');   -- ERROR: value too long for type character(2)

-- Same cost for varchar and text: 'abc' => 7 bytes in all of varchar(100) / text
SELECT pg_column_size('abc'::varchar(100)) v, pg_column_size('abc'::text) t, pg_column_size('abc'::char(8)) c;
-- 7 | 7 | 12

-- Big values are compressed automatically (TOAST): 1,000,000 chars stored in ~11 KB here
INSERT INTO products VALUES (4,'IN','AB12','x',repeat('long text ',100000));
SELECT pg_column_size(description) AS stored_bytes, length(description) AS logical_len FROM products WHERE id=4;
-- 11463 | 1000000

-- Indexes work on TEXT directly (no prefix length needed in PgSQL):
CREATE INDEX idx_desc ON products (description);   -- fine for short values
-- but with a huge value present: ERROR: index row requires 37832 bytes, maximum size is 8191 (btree row limit;
-- use a hash/GIN/full-text index or index md5(description) instead)
-- Idiomatic PgSQL: use TEXT (+ CHECK (char_length(x) <= n) if a limit is needed); avoid CHAR(n).
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: CHAR(255) for names/emails — wastes space (padding) in MySQL, and PgSQL pads too
-- ❌ Wrong: VARCHAR(255) everywhere "just in case" — MySQL temp tables / sorts allocate the max
--          size per row (utf8mb4 => 4 x 255 bytes), slowing GROUP BY / ORDER BY on those columns
-- ❌ Wrong (PgSQL): thinking VARCHAR(50) is faster/smaller than TEXT — it is not
-- ❌ Wrong (MySQL): TEXT column with DEFAULT value or full-column index
--          (MySQL: DEFAULT 'x' on TEXT => ERROR 1101; only an expression default DEFAULT ('x') works, 8.0.13+)
-- ❌ Wrong: comparing with trailing spaces and expecting same behaviour across MySQL collations

-- ✅ Correct: CHAR only for truly fixed codes (country, currency); VARCHAR(n) with a realistic n
--            for bounded text; TEXT (MySQL: only when large/unbounded) for the rest.
```

---

## 🎯 Interview Tip (1 line)
Say: "In MySQL I choose VARCHAR with a realistic limit and keep TEXT off hot paths because it's stored off-page and needs prefix indexes; in PostgreSQL VARCHAR(n), TEXT and CHAR share the same varlena/TOAST storage, so I default to TEXT with a CHECK constraint and avoid CHAR(n)."

---

## 🔗 Related Questions
→ Q021 (INT/BIGINT/TINYINT) | Q026 (ENUM) | Q027 (JSON vs JSONB) | Q030 (Constraints)
