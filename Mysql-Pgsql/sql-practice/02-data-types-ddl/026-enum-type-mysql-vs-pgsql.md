---

# Q026. ENUM Type — MySQL vs PgSQL Approach
# Category: Data Types & DDL
# Difficulty: ⭐⭐ Medium
# DB: Both (different implementations)

---

## ❓ Question
How do ENUMs work in MySQL vs PostgreSQL? Show ordering, invalid-value handling, and adding values later. What are the alternatives (lookup table, CHECK constraint) and when would you avoid ENUM?

---

## 💡 Quick Concept (2 lines only)
MySQL ENUM is a column-level list of strings stored as a 1-2 byte index; PostgreSQL ENUM is a standalone reusable type (4 bytes) created with `CREATE TYPE`. In both, values sort by definition order, not alphabetically — and changing the value list later has costs.
हिंदी: ENUM में values define किए गए क्रम में sort होती हैं, alphabetical नहीं; list बदलना महंगा या सीमित हो सकता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (MySQL) — run this first
-- ============================================

CREATE TABLE support_tickets (
  id       INT PRIMARY KEY AUTO_INCREMENT,
  subject  VARCHAR(100),
  priority ENUM('low','medium','high','urgent') NOT NULL DEFAULT 'medium'
);

INSERT INTO support_tickets (subject, priority) VALUES
  ('Login broken',   'urgent'),
  ('Typo on page',   'low'),
  ('Slow dashboard', 'high'),
  ('Feature ask',    'medium');

-- ============================================
-- SOLUTION (MySQL 9.1.0, all verified)
-- ============================================

-- 1) ORDER BY uses the internal index (definition order), not the text
SELECT subject, priority, priority + 0 AS enum_index
FROM support_tickets ORDER BY priority DESC;
-- subject        | priority | enum_index
-- Login broken   | urgent   | 4
-- Slow dashboard | high     | 3
-- Feature ask    | medium   | 2
-- Typo on page   | low      | 1

-- 2) Alphabetical order needs a cast
SELECT subject, priority FROM support_tickets ORDER BY CAST(priority AS CHAR);
-- Slow dashboard high | Typo on page low | Feature ask medium | Login broken urgent

-- 3) Filter by label or by index (index form is a trap: 2 = 'medium')
SELECT subject FROM support_tickets WHERE priority = 'high';   -- Slow dashboard
SELECT subject FROM support_tickets WHERE priority = 2;        -- Feature ask

-- 4) Invalid value: strict mode => error
INSERT INTO support_tickets (subject, priority) VALUES ('Bad value', 'critical');
-- ERROR 1265 (01000): Data truncated for column 'priority' at row 1
-- With sql_mode='' it silently stores the special empty-string error value '' (index 0).

-- 5) Add a value at the END (documented as a metadata-only change); middle/reorder rebuilds the table
--    (ALTER ran fine on MySQL 9.1.0; INSTANT-vs-rebuild timing itself was not measured)
ALTER TABLE support_tickets
  MODIFY priority ENUM('low','medium','high','urgent','blocker') NOT NULL DEFAULT 'medium';

-- ============================================
-- PostgreSQL version (verified on PostgreSQL 18 via PGlite)
-- ============================================
CREATE TYPE ticket_priority AS ENUM ('low','medium','high','urgent');

CREATE TABLE support_tickets (
  id       SERIAL PRIMARY KEY,
  subject  VARCHAR(100),
  priority ticket_priority NOT NULL DEFAULT 'medium'
);
INSERT INTO support_tickets (subject, priority) VALUES
  ('Login broken','urgent'),('Typo on page','low'),('Slow dashboard','high'),('Feature ask','medium');

SELECT subject, priority FROM support_tickets ORDER BY priority DESC;
-- Login broken | urgent / Slow dashboard | high / Feature ask | medium / Typo on page | low

SELECT subject FROM support_tickets WHERE priority >= 'high' ORDER BY subject;   -- comparison by enum order
-- Login broken, Slow dashboard

INSERT INTO support_tickets (subject, priority) VALUES ('Bad value','critical');
-- ERROR: invalid input value for enum ticket_priority: "critical"

SELECT enum_range(NULL::ticket_priority);          -- {low,medium,high,urgent}
ALTER TYPE ticket_priority ADD VALUE 'blocker' AFTER 'urgent';   -- no rewrite; can place anywhere
SELECT enum_range(NULL::ticket_priority);          -- {low,medium,high,urgent,blocker}
SELECT pg_column_size('high'::ticket_priority);    -- 4

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Shown inline above. Row order is only deterministic where ORDER BY is given.
```

---

## 🔍 Why This Works (3 lines max)
Both engines store a compact numeric position and map it to the label, so comparisons and sorts follow the declared order and storage is small. PostgreSQL's separate type is reusable across tables and supports `ADD VALUE`; but neither engine lets you easily drop or rename-and-reorder labels in use (PgSQL can `RENAME VALUE`, not drop).
हिंदी: दोनों में label के पीछे number रहता है, इसलिए sort/compare declared order में होता है।

---

## ⚡ Alternative Solution

```sql
-- Option 1: lookup table + FOREIGN KEY (most flexible; works identically on both DBs)
CREATE TABLE ticket_priorities_lookup (
  code       VARCHAR(10) PRIMARY KEY,
  sort_order SMALLINT NOT NULL
);
INSERT INTO ticket_priorities_lookup VALUES ('low',1),('medium',2),('high',3),('urgent',4);

CREATE TABLE support_tickets_v2 (
  id       INT PRIMARY KEY,                       -- PgSQL: SERIAL
  subject  VARCHAR(100),
  priority VARCHAR(10) NOT NULL REFERENCES ticket_priorities_lookup(code)
);
INSERT INTO support_tickets_v2 (id, subject, priority) VALUES (1, 'x', 'critical');
-- PgSQL: ERROR: insert or update on table "support_tickets_v2" violates foreign key constraint
-- MySQL: ERROR 1452 (23000): Cannot add or update a child row ... (same idea)
-- Adding a new priority = one INSERT (no DDL), can carry extra columns (label, colour, SLA hours).

-- Option 2: CHECK constraint (MySQL 8.0.16+, PgSQL always)
CREATE TABLE support_tickets_v3 (
  id       INT PRIMARY KEY,
  priority VARCHAR(10) NOT NULL CHECK (priority IN ('low','medium','high','urgent'))
);
-- PgSQL: ERROR: new row for relation "support_tickets_v3" violates check constraint
-- Changing the list = DROP/ADD CONSTRAINT (cheap on small tables; validates all rows).

-- Rule: stable, tiny, ordered sets (priority, size) => ENUM is fine.
--       Business-owned or growing lists (country, category, status with workflow) => lookup table.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong (MySQL): ENUM('0','1','2') — numeric-looking labels; WHERE col = 1 matches the INDEX, not the label '1'
-- ❌ Wrong (MySQL): inserting a typo with sql_mode='' => silently stored as '' (index 0)
-- ❌ Wrong: inserting a new value in the MIDDLE of a MySQL ENUM on a big table => full table rebuild
--          (appending at the end is the cheap case; ordering changes are not)
-- ❌ Wrong: using ENUM for values the business edits often (needs a deploy/DDL each time)

-- ✅ Correct: lookup table for evolving domains; ENUM only for small, stable, ordered lists
```

---

## 🎯 Interview Tip (1 line)
Say: "ENUM gives compact storage and ordering but couples the schema to the value list — I use it for tiny stable sets, a lookup table with a foreign key when the business owns the values, and I always keep sql_mode strict so MySQL doesn't swallow bad values."

---

## 🔗 Related Questions
→ Q022 (VARCHAR vs CHAR) | Q030 (CHECK / FOREIGN KEY constraints) | Q021 (TINYINT as status code)
