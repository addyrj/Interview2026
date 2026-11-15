---

# Q036. Table Inheritance (PgSQL)
# Category: Data Types & DDL
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL has no equivalent)

---

## ❓ Question
Model `vehicles` with child tables `cars` and `trucks` using PostgreSQL `INHERITS`. How do queries on the parent behave, what is `ONLY`, and what are the gotchas (PK/FK/unique not inherited)? When should you NOT use it?

---

## 💡 Quick Concept (2 lines only)
`CREATE TABLE child (...) INHERITS (parent)` copies the parent's columns; a SELECT on the parent also returns child rows unless you write `FROM ONLY parent`. Constraints like PK, UNIQUE and FOREIGN KEY are NOT shared across the hierarchy.
हिंदी: INHERITS से child को parent के columns मिलते हैं और parent पर SELECT child rows भी देता है, पर PK/UNIQUE/FK inherit नहीं होते।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL only; verified on PGlite = PostgreSQL 18.6)
-- ============================================

CREATE TABLE vehicles (
  id    SERIAL PRIMARY KEY,
  brand TEXT NOT NULL,
  year  INT
);
CREATE TABLE cars   (door_count INT)  INHERITS (vehicles);
CREATE TABLE trucks (payload_kg INT)  INHERITS (vehicles);

INSERT INTO vehicles (brand, year) VALUES ('Generic', 2000);
INSERT INTO cars   (brand, year, door_count) VALUES ('Honda', 2022, 4), ('Toyota', 2021, 2);
INSERT INTO trucks (brand, year, payload_kg) VALUES ('Tata', 2020, 5000);

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: parent query includes ALL descendants
SELECT * FROM vehicles ORDER BY id;

-- Step 2: ONLY = just the parent's own rows
SELECT * FROM ONLY vehicles ORDER BY id;

-- Step 3: which physical table did each row come from?
SELECT tableoid::regclass AS source_table, brand FROM vehicles ORDER BY brand;

-- Step 4: updating via the parent updates child rows too
UPDATE vehicles SET year = year + 1 WHERE brand = 'Honda';
SELECT * FROM cars ORDER BY id;

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1:
-- id | brand   | year
-- 1  | Generic | 2000
-- 2  | Honda   | 2022
-- 3  | Toyota  | 2021
-- 4  | Tata    | 2020
--
-- Step 2:
-- id | brand   | year
-- 1  | Generic | 2000
--
-- Step 3:
-- source_table | brand
-- vehicles     | Generic
-- cars         | Honda
-- trucks       | Tata
-- cars         | Toyota
--
-- Step 4 (cars, Honda year bumped to 2023):
-- id | brand  | year | door_count
-- 2  | Honda  | 2023 | 4
-- 3  | Toyota | 2021 | 2
```

---

## 🔍 Why This Works (3 lines max)
Each child is a real separate table; the parent scan is an "append" over parent plus children, and `tableoid` tells which one produced the row. `ONLY` removes the children from that scan. `SERIAL` shares the parent's sequence, so ids stay unique unless you override them.
हिंदी: हर child असली अलग table है; parent query सब children को जोड़कर पढ़ती है, `ONLY` से सिर्फ parent की rows आती हैं।

---

## ⚡ Alternative Solution

```sql
-- The big gotchas (all reproduced on PG 18.6):

-- 1) PK/UNIQUE not enforced across the hierarchy -> duplicate id silently accepted
INSERT INTO cars (id, brand, year) VALUES (1, 'Dup', 2023);   -- succeeds! id=1 already exists in vehicles

-- 2) A FOREIGN KEY pointing at the parent only sees the parent's OWN rows
CREATE TABLE orders (id INT PRIMARY KEY, vehicle_id INT REFERENCES vehicles(id));
INSERT INTO orders VALUES (1, 2);   -- id 2 is a car
-- ERROR: insert or update on table "orders" violates foreign key constraint "orders_vehicle_id_fkey"

-- Modern alternatives (usually better):
--  * Declarative partitioning (PARTITION BY LIST/RANGE/HASH) — real constraint/ pruning support
--  * Single table + "type" column (+ nullable type-specific columns or a JSONB column)
--  * Class-table design: vehicles + car_details(vehicle_id PK/FK) joined 1:1
-- MySQL: no INHERITS; use the single-table or 1:1 detail-table patterns above.
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Wrong: assuming the PK on the parent also protects children
-- ❌ Wrong: DELETE/UPDATE on parent and forgetting it also hits child rows (use FROM ONLY if you mean parent-only)
SELECT count(*) FROM vehicles;        -- 4, not 1: includes cars + trucks
-- ✅ Correct: SELECT count(*) FROM ONLY vehicles;   -- 1

-- ❌ Wrong: using INHERITS for partitioning in new code
-- ✅ Correct: declarative partitioning (PG 10+), which handles routing, pruning and constraints
```

---

## 🎯 Interview Tip (1 line)
Say: "PG table inheritance exists but I avoid it for new designs because unique/PK/FK constraints don't span children; for partitioning I use declarative partitions, and for subtype modelling I use a type column or 1:1 detail tables."

---

## 🔗 Related Questions
→ Q031 (Foreign keys) | Q037 (CHECK constraints) | Q038 (DEFERRABLE) | Partitioning questions
