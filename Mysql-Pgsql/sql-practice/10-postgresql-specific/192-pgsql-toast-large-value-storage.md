---

# Q192. PgSQL TOAST — Large Value Storage
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐ Medium
# DB: PostgreSQL

---

## ❓ Question
A `documents` table stores big text bodies, yet the table's heap is only 8 kB. Where does the data live? Explain TOAST, show how to see it, and how to control the storage strategy per column.

---

## 💡 Quick Concept (2 lines only)
Rows must fit in an 8 kB page, so values over ~2 kB are compressed and/or moved out-of-line into a hidden `pg_toast.pg_toast_<oid>` table. It is automatic, per column, and invisible to queries.
हिंदी: बड़ी values (~2KB+) automatically compress होकर या अलग hidden TOAST table में चली जाती हैं, query में कुछ बदलना नहीं पड़ता।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)  -- PostgreSQL
-- ============================================

CREATE TABLE documents (
  id    SERIAL PRIMARY KEY,
  title TEXT,
  body  TEXT
);

-- 3 small docs (240 chars)
INSERT INTO documents (title, body)
SELECT 'doc ' || g, repeat('lorem ipsum ', 20) FROM generate_series(1, 3) g;

-- 1 big doc, 160,000 chars of hex (hard to compress)
INSERT INTO documents (title, body)
VALUES ('big random',
        (SELECT string_agg(md5(i::text), '') FROM generate_series(1, 5000) i));

-- 1 big doc, 300,000 chars but highly compressible
INSERT INTO documents (title, body) VALUES ('big compressible', repeat('abc', 100000));

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: logical length vs bytes actually stored
SELECT id, title, length(body) AS chars, pg_column_size(body) AS stored_bytes
FROM documents ORDER BY id;

-- Step 2: find the hidden TOAST table of this table
SELECT c.relname, t.relname AS toast_table
FROM pg_class c LEFT JOIN pg_class t ON t.oid = c.reltoastrelid
WHERE c.relname = 'documents';

-- Step 3: heap alone vs heap + TOAST + (no indexes)
SELECT pg_size_pretty(pg_relation_size('documents')) AS main_heap,
       pg_size_pretty(pg_table_size('documents'))    AS heap_plus_toast;

-- Step 4: per-column strategy: p=plain, e=external, m=main, x=extended
SELECT attname, attstorage FROM pg_attribute
WHERE attrelid = 'documents'::regclass AND attnum > 0;

-- Step 5: change strategy (store out-of-line but do NOT compress -> faster substring())
ALTER TABLE documents ALTER COLUMN body SET STORAGE EXTERNAL;

-- ============================================
-- EXPECTED OUTPUT (real, PGlite = PostgreSQL 18)
-- ============================================

-- Step 1:
-- id | title            | chars  | stored_bytes
-- 1  | doc 1            | 240    | 244      <- small: stored inline (+4 byte header)
-- 2  | doc 2            | 240    | 244
-- 3  | doc 3            | 240    | 244
-- 4  | big random       | 160000 | 160000   <- stored out-of-line (not compressed in this build)
-- 5  | big compressible | 300000 | 3442     <- compressed ~87x
--
-- Step 2:  documents | pg_toast_16385   (the number is the table OID, differs on your DB)
-- Step 3:  main_heap = 8192 bytes | heap_plus_toast = 216 kB
-- Step 4:  id p | title x | body x       (x = extended: compress + out-of-line)
```

---

## 🔍 Why This Works (3 lines max)
When a row exceeds TOAST_TUPLE_THRESHOLD (~2 kB), PgSQL first compresses the largest "extended" columns, then slices them into ~2 kB chunks in the TOAST table, leaving a small pointer in the heap. So the heap stays at 8 kB while `pg_table_size` shows the true cost.
हिंदी: Row बड़ी हो तो पहले compress, फिर 2KB chunks में TOAST table में; heap में सिर्फ pointer रहता है।

---

## ⚡ Alternative Solution

```sql
-- Check compression algorithm per column (PostgreSQL 14+):
ALTER TABLE documents ALTER COLUMN body SET COMPRESSION lz4;   -- needs lz4 build; default pglz

-- Biggest tables INCLUDING toast + indexes:
SELECT relname, pg_size_pretty(pg_total_relation_size(oid)) AS total
FROM pg_class WHERE relkind = 'r' AND relnamespace = 'public'::regnamespace
ORDER BY pg_total_relation_size(oid) DESC LIMIT 5;

-- MySQL equivalent: InnoDB stores long TEXT/BLOB/VARCHAR off-page in "overflow pages"
-- (DYNAMIC row format keeps only a 20-byte pointer in the clustered index record).
-- No per-column strategy knob like PgSQL STORAGE.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ SELECT * on a table with huge TOASTed columns when you only need metadata
SELECT * FROM documents;                 -- detoasts every body: big IO + network
-- ✅ Select only needed columns; TOAST data is fetched lazily, only when the column is read
SELECT id, title FROM documents;

-- ❌ Measuring table size with pg_relation_size only
SELECT pg_relation_size('documents');    -- 8192 bytes: misleading, ignores TOAST
-- ✅ pg_table_size (heap+toast) or pg_total_relation_size (+indexes)
```

---

## 🎯 Interview Tip (1 line)
Say: "TOAST is transparent compression plus out-of-line storage for values over ~2 kB; I avoid SELECT * on wide tables, size tables with pg_total_relation_size, and use STORAGE EXTERNAL or lz4 compression when a column is read by substring or is already compressed."

---

## 🔗 Related Questions
→ Q191 (VACUUM — TOAST tables are vacuumed too) | Q181 (JSONB — large JSONB is TOASTed) | Q244 (JSON vs relational)
