---

# Q188. Inheritance in PostgreSQL
# Category: PostgreSQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL only (verified on PostgreSQL 18.6 via PGlite)

---

## ❓ Question
What is table inheritance (`INHERITS`) in PostgreSQL? Show how parent queries include child rows, how to query `ONLY` the parent, and the limitations (unique keys, foreign keys). When would you use it today versus declarative partitioning?

---

## 💡 Quick Concept (2 lines only)
`CREATE TABLE child (...) INHERITS (parent)` copies the parent's columns into the child; selecting from the parent also returns child rows (use `ONLY` to exclude them). Constraints like PRIMARY KEY, UNIQUE and FOREIGN KEY are NOT shared across the hierarchy, which is why declarative partitioning replaced it for most uses.
हिंदी: INHERITS से child table parent के columns लेती है और parent से SELECT करने पर child rows भी आती हैं (ONLY से नहीं); PK/UNIQUE/FK पूरे hierarchy में लागू नहीं होते।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE vehicles (
  id         SERIAL PRIMARY KEY,
  plate      TEXT NOT NULL,
  created_at DATE DEFAULT '2024-01-01'
);
CREATE TABLE cars   (doors      INT) INHERITS (vehicles);
CREATE TABLE trucks (payload_kg INT) INHERITS (vehicles);

INSERT INTO vehicles (plate)          VALUES ('GEN-001');
INSERT INTO cars     (plate, doors)   VALUES ('CAR-100', 4), ('CAR-200', 2);
INSERT INTO trucks   (plate, payload_kg) VALUES ('TRK-900', 8000);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: parent query includes all children; tableoid tells which table a row lives in
SELECT tableoid::regclass AS source, id, plate FROM vehicles ORDER BY id;
-- source   | id | plate
-- vehicles | 1  | GEN-001
-- cars     | 2  | CAR-100
-- cars     | 3  | CAR-200
-- trucks   | 4  | TRK-900
-- (ids 1-4 come from the parent's one shared sequence; children inherit the DEFAULT, not a separate sequence)

-- Step 2: ONLY = just the parent's own rows
SELECT tableoid::regclass AS source, id, plate FROM ONLY vehicles;
-- vehicles | 1 | GEN-001

-- Step 3: child has its own extra columns
SELECT * FROM cars ORDER BY id;
-- id | plate   | created_at | doors
-- 2  | CAR-100 | 2024-01-01 | 4
-- 3  | CAR-200 | 2024-01-01 | 2

-- Step 4: UPDATE/DELETE on the parent also reach children
UPDATE vehicles SET plate = plate || '-X' WHERE plate LIKE 'CAR-1%';
SELECT plate FROM cars ORDER BY id;
-- CAR-100-X
-- CAR-200
UPDATE ONLY vehicles SET plate = 'NOPE' WHERE plate LIKE 'CAR%';   -- 0 rows: no parent-only row matches

-- Step 5: the catalog view
SELECT inhrelid::regclass AS child, inhparent::regclass AS parent FROM pg_inherits ORDER BY 1;
-- cars   | vehicles
-- trucks | vehicles

-- Step 6: schema changes on the parent cascade down
ALTER TABLE vehicles ADD COLUMN color TEXT DEFAULT 'white';
SELECT * FROM trucks;
-- id | plate   | created_at | payload_kg | color
-- 4  | TRK-900 | 2024-01-01 | 8000       | white

-- ============================================
-- LIMITATIONS (real output)
-- ============================================

-- (a) Primary key is NOT inherited -> duplicate id across the hierarchy
INSERT INTO cars (id, plate, doors) VALUES (1, 'DUP', 4);          -- succeeds!
SELECT id, plate FROM vehicles WHERE id = 1 ORDER BY plate;
-- 1 | DUP
-- 1 | GEN-001

-- (b) Foreign keys only see the parent's own rows
CREATE TABLE service_log (vehicle_id INT REFERENCES vehicles(id), note TEXT);
INSERT INTO service_log VALUES (2, 'oil change');       -- id 2 lives in cars
-- ERROR: insert or update on table "service_log" violates foreign key constraint "service_log_vehicle_id_fkey"

-- (c) Detach a child
ALTER TABLE cars NO INHERIT vehicles;
SELECT count(*) FROM vehicles;                           -- 2 (GEN-001 + trucks' TRK-900; the 3 cars rows no longer included)

-- (d) Cannot drop parent while children depend on it
DROP TABLE vehicles;
-- ERROR: cannot drop table vehicles because other objects depend on it    (use DROP ... CASCADE)
```

---

## 🔍 Why This Works (3 lines max)
Inheritance is just a catalog link (`pg_inherits`): a scan of the parent becomes an Append over parent plus each child. Each table is physically independent, so indexes and constraints are per table; that independence is both the flexibility and the limitation (no global uniqueness, FKs ignore children).
हिंदी: Inheritance सिर्फ़ catalog link है; parent scan = parent + सभी children का Append, इसलिए constraints हर table के अपने होते हैं।

---

## ⚡ Alternative Solution

```sql
-- Modern single-table alternatives:
-- 1) Declarative partitioning for size/lifecycle (Q189) - routes inserts and prunes automatically.
-- 2) Single table + type discriminator + nullable columns (or JSONB for type-specific fields):
CREATE TABLE vehicles_one (id SERIAL PRIMARY KEY, kind TEXT CHECK (kind IN ('car','truck')),
                           plate TEXT, doors INT, payload_kg INT);
-- 3) Supertype/subtype tables with shared PK + FKs (strong integrity):
--    CREATE TABLE car (vehicle_id INT PRIMARY KEY REFERENCES vehicles(id), doors INT);

-- MySQL has no table inheritance. Use approach 2 or 3.
-- Where INHERITS is still seen: legacy partitioning (pre-10), audit/log tables, and extensions like TimescaleDB history.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Assuming the parent's PRIMARY KEY / UNIQUE protects children
-- Verified: INSERT INTO cars (id=1, ...) succeeded while vehicles already had id 1.
-- ✅ Add a unique index on each child, or avoid inheritance when global uniqueness is needed.

-- ❌ Expecting FK targets to include child rows (service_log -> vehicles only sees ONLY vehicles rows).

-- ❌ Forgetting ONLY in maintenance:
UPDATE vehicles SET ...            -- touches every child
-- ✅ UPDATE ONLY vehicles SET ... when you mean the parent alone.

-- ❌ Using inheritance for new partitioned designs -> no automatic row routing, manual triggers, no global index.
```

---

## 🎯 Interview Tip (1 line)
Say: "INHERITS exists but constraints are not inherited and FKs ignore children, so for new designs I use declarative partitioning for scale and either a type column or supertype/subtype tables for OO-style modelling."

---

## 🔗 Related Questions
→ Q189 (Declarative partitioning) | Q177 (MySQL partitioning) | Q182 (JSONB for type-specific fields) | Q244 (JSON vs relational)
