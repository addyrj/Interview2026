---

# Q167. MySQL ENUM — Internal Storage + Pitfalls
# Category: MySQL Specific
# Difficulty: ⭐⭐ Medium
# DB: MySQL (verified on MySQL 9.1); PostgreSQL ENUM compared (verified on PGlite)

---

## ❓ Question
How does MySQL store an ENUM column internally, how does sorting work, what happens on invalid values, and why do many teams avoid ENUM in favour of a lookup table?

---

## 💡 Quick Concept (2 lines only)
ENUM stores a 1- or 2-byte integer index into the list of allowed strings (1 byte up to 255 values), so it is compact. ORDER BY sorts by that index, not alphabetically, and changing the list needs an ALTER TABLE.
हिंदी: ENUM अंदर से 1-2 byte का index रखता है; sorting index से होती है (alphabet से नहीं), और नया value जोड़ने के लिए ALTER TABLE चाहिए।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE support_tickets (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  status ENUM('open','in_progress','resolved','closed') NOT NULL DEFAULT 'open'
);

INSERT INTO support_tickets (status) VALUES
  ('open'),('closed'),('resolved'),('in_progress'),('open');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: see the hidden integer index (+0 casts to the number)
SELECT id, status, status + 0 AS enum_index FROM support_tickets ORDER BY id;
-- id | status      | enum_index
-- 1  | open        | 1
-- 2  | closed      | 4
-- 3  | resolved    | 3
-- 4  | in_progress | 2
-- 5  | open        | 1

-- Step 2: ORDER BY uses the index = definition order (a feature when order is meaningful!)
SELECT id, status FROM support_tickets ORDER BY status, id;
-- 1 open | 5 open | 4 in_progress | 3 resolved | 2 closed

-- Alphabetical needs a cast:
SELECT id, status FROM support_tickets ORDER BY CAST(status AS CHAR), id;
-- 2 closed | 4 in_progress | 1 open | 5 open | 3 resolved

-- Step 3: invalid value
INSERT INTO support_tickets (status) VALUES ('reopened');
-- strict mode (default): ERROR 1265 (01000): Data truncated for column 'status' at row 1

-- Step 4: the numeric trap — a number is treated as an INDEX, not a string
INSERT INTO support_tickets (status) VALUES (2);      -- stores 'in_progress' (index 2)!
SELECT id, status FROM support_tickets WHERE status = 2;      -- matches by index
SELECT id FROM support_tickets WHERE status = '2';            -- compares with the string '2' -> no rows
INSERT INTO support_tickets (status) VALUES (0);
-- ERROR 1265: Data truncated  (index 0 is the special "error" value '' — only reachable with non-strict sql_mode)

-- Step 5: non-strict sql_mode silently stores the empty-string error value
SET SESSION sql_mode = '';
INSERT INTO support_tickets (status) VALUES ('reopened');     -- stored as '' with index 0, just a warning
SELECT id, status, status + 0 AS idx FROM support_tickets ORDER BY id DESC LIMIT 1;
-- status = '' | idx = 0
SET SESSION sql_mode = DEFAULT;

-- Step 6: how the definition is recorded
SELECT COLUMN_TYPE FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'support_tickets' AND COLUMN_NAME = 'status';
-- enum('open','in_progress','resolved','closed')
```

---

## 🔍 Why This Works (3 lines max)
The table definition holds the string list and each row stores only the position (1..N, 0 = invalid), which is why the column is tiny and sorts by definition order. Anything that touches the list (add, reorder, rename) rewrites metadata or data, and numeric literals are interpreted as positions.
हिंदी: Rows में सिर्फ position रहती है, strings table definition में; इसलिए छोटा storage, लेकिन list बदलना और number literals risky हैं।

---

## ⚡ Alternative Solution

```sql
-- Lookup table + FK: adding a status is an INSERT, not an ALTER; can hold labels, sort_order, is_active
CREATE TABLE ticket_status (
  id   TINYINT UNSIGNED PRIMARY KEY,
  name VARCHAR(20) NOT NULL UNIQUE
);
-- support_tickets.status_id TINYINT UNSIGNED NOT NULL, FOREIGN KEY (status_id) REFERENCES ticket_status(id)

-- Or VARCHAR + CHECK (MySQL 8.0.16+ enforces CHECK):
-- status VARCHAR(20) NOT NULL CHECK (status IN ('open','in_progress','resolved','closed'))

-- PostgreSQL: CREATE TYPE ... AS ENUM, also ordered by definition (verified on PGlite)
CREATE TYPE ticket_status AS ENUM ('open','in_progress','resolved','closed');
-- ORDER BY status  -> open, in_progress, resolved, closed (same as MySQL)
-- INSERT 'reopened' -> ERROR: invalid input value for enum ticket_status: "reopened"
-- ALTER TYPE ticket_status ADD VALUE 'reopened' BEFORE 'closed';   -- cheap, no table rewrite, works
-- Then ORDER BY puts 'reopened' just before 'closed'. (PgSQL cannot DROP a value easily.)
-- MySQL: ALTER TABLE ... MODIFY status ENUM(...) — appending at the END of the list is an
--        instant metadata change; inserting in the middle or reordering rewrites the table.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: inserting numbers into an ENUM column
INSERT INTO support_tickets (status) VALUES (2);       -- becomes 'in_progress', not '2'
-- ❌ Wrong: relying on alphabetical ORDER BY (it follows definition order)
-- ❌ Wrong: inserting a new value in the middle of the list -> indexes shift, table rebuild,
--    and any code storing the numeric index is now wrong
-- ❌ Wrong: ENUM for values that change often or need attributes (labels, colours, translations)
-- ✅ Use ENUM only for tiny, stable sets (e.g. 'M','F','O'); otherwise a lookup table + FK
```

---

## 🎯 Interview Tip (1 line)
Say: "ENUM is a 1-2 byte index into a list stored in the table definition, which is compact but sorts by definition order, treats numbers as positions, and needs DDL to change; for evolving business states I prefer a lookup table with a foreign key (or CHECK constraint)."

---

## 🔗 Related Questions
→ Q159 (CHECK vs app validation) | Q152 (EAV) | Q168 (MySQL JSON) | Q013 (ALTER impact on large tables: Q157)
