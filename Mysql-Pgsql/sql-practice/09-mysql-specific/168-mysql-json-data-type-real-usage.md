---

# Q168. MySQL JSON Data Type — Real Usage
# Category: MySQL Specific
# Difficulty: ⭐⭐⭐ Hard
# DB: MySQL (verified on MySQL 9.1); PgSQL JSONB equivalents noted

---

## ❓ Question
Store semi-structured event payloads in a MySQL JSON column. Show: extracting values (`->` vs `->>`), filtering, searching arrays, updating a path, exploding an array with JSON_TABLE, and indexing a JSON field. What type pitfalls bite in production?

---

## 💡 Quick Concept (2 lines only)
MySQL JSON is a validated binary format with path functions; you cannot index the column directly, so index a path through a generated column or a functional index. `->` returns JSON (quoted), `->>` returns plain text.
हिंदी: JSON column validated binary होता है; सीधे index नहीं होता — generated column या functional index से path index करो। `->>` plain text देता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE user_events (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id    INT NOT NULL,
  event_type VARCHAR(30) NOT NULL,
  payload    JSON NOT NULL
);

INSERT INTO user_events (user_id, event_type, payload) VALUES
 (1,'checkout','{"cart_total": 1499.50, "coupon": "NEW10", "items": [{"sku":"A1","qty":2},{"sku":"B7","qty":1}], "device": {"os":"android","app_ver":"5.2"}}'),
 (2,'checkout','{"cart_total": 320.00, "coupon": null, "items": [{"sku":"C3","qty":1}], "device": {"os":"ios","app_ver":"5.1"}}'),
 (3,'login',   '{"device": {"os":"android","app_ver":"5.2"}, "ip":"10.0.0.7"}'),
 (1,'checkout','{"cart_total": 80.00, "items": [{"sku":"A1","qty":1}], "device": {"os":"web"}}');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: -> returns JSON, ->> returns text; JSON null vs missing key vs SQL NULL
SELECT id, payload->'$.coupon' AS coupon_json, payload->>'$.coupon' AS coupon_text FROM user_events ORDER BY id;
-- id | coupon_json | coupon_text
-- 1  | "NEW10"     | NEW10
-- 2  | null        | null        <- JSON null (a 4-char string with ->>)
-- 3  | NULL        | NULL        <- key missing = SQL NULL
-- 4  | NULL        | NULL

-- Step 2: comparison type pitfall
SELECT id FROM user_events WHERE payload->>'$.cart_total' > 1000;     -- numeric compare   -> 1
SELECT id FROM user_events WHERE payload->>'$.cart_total' > '1000';   -- STRING compare    -> 1, 2, 4  (WRONG!)
SELECT id FROM user_events WHERE CAST(payload->>'$.cart_total' AS DECIMAL(10,2)) > 1000;   -- explicit -> 1

-- Step 3: search inside arrays
SELECT id FROM user_events WHERE JSON_CONTAINS(payload->'$.items', '{"sku":"A1"}') ORDER BY id;   -- 1, 4
SELECT id FROM user_events WHERE 'B7' MEMBER OF (payload->'$.items[*].sku');                       -- 1
SELECT id, JSON_LENGTH(payload,'$.items') AS item_kinds FROM user_events WHERE event_type='checkout';
-- 1 -> 2 | 2 -> 1 | 4 -> 1

-- Step 4: partial updates (do not rewrite the whole document in the app)
UPDATE user_events SET payload = JSON_SET(payload, '$.coupon', 'VIP20', '$.device.app_ver', '5.3') WHERE id = 2;
UPDATE user_events SET payload = JSON_REMOVE(payload, '$.ip') WHERE id = 3;
SELECT payload FROM user_events WHERE id = 3;
-- {"device": {"os": "android", "app_ver": "5.2"}}
-- Note: MySQL normalizes key order (shorter keys first), so the stored text differs from what you inserted.

-- Step 5: turn an array into rows
SELECT jt.sku, SUM(jt.qty) AS total_qty
FROM user_events e,
     JSON_TABLE(e.payload, '$.items[*]' COLUMNS (sku VARCHAR(10) PATH '$.sku', qty INT PATH '$.qty')) jt
GROUP BY jt.sku ORDER BY jt.sku;
-- sku | total_qty
-- A1  | 3
-- B7  | 1
-- C3  | 1

-- Step 6: indexing — generated column (works in 5.7+) and functional index (8.0.13+)
ALTER TABLE user_events
  ADD COLUMN os VARCHAR(20) GENERATED ALWAYS AS (payload->>'$.device.os') VIRTUAL,
  ADD INDEX idx_os (os);
EXPLAIN SELECT id FROM user_events WHERE os = 'android';
-- type=ref | key=idx_os | key_len=83 | Extra=Using index

ALTER TABLE user_events ADD INDEX idx_total ((CAST(payload->>'$.cart_total' AS DECIMAL(10,2))));   -- functional index
ALTER TABLE user_events ADD INDEX idx_skus  ((CAST(payload->'$.items[*].sku' AS CHAR(10) ARRAY))); -- multi-valued index for MEMBER OF / JSON_CONTAINS

-- Step 7: invalid JSON is rejected on write
INSERT INTO user_events (user_id,event_type,payload) VALUES (9,'x','{bad json}');
-- ERROR 3140 (22032): Invalid JSON text: "Missing a name for object member." ...
```

---

## 🔍 Why This Works (3 lines max)
JSON is parsed once on write into a binary form, so path lookups are fast and invalid documents never get stored. Indexes work only on values extracted via a generated column / functional index (or a multi-valued index for arrays), because the document itself has no natural ordering.
हिंदी: JSON write पर parse होकर binary में जाता है; index सिर्फ extracted value (generated column / functional / multi-valued) पर बनता है।

---

## ⚡ Alternative Solution

```sql
-- PostgreSQL JSONB (operators differ):
--   payload->'coupon'           JSON        payload->>'coupon'        text
--   payload @> '{"device":{"os":"android"}}'     containment (GIN-indexable)
--   jsonb_set(payload, '{coupon}', '"VIP20"')    update a path
--   jsonb_array_elements(payload->'items')       explode array (like JSON_TABLE)
--   CREATE INDEX ON user_events USING GIN (payload);       -- one index for most queries
--   WHERE (payload->>'cart_total')::numeric > 1000

-- Rule of thumb: columns you filter/join/sort on constantly -> real columns.
-- Rarely-queried, variable attributes -> JSON.
-- Large JSON docs updated often are costly: InnoDB rewrites most of the value unless partial update applies.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: compare ->> output to a string literal for numbers
WHERE payload->>'$.cart_total' > '1000'     -- '320.0' > '1000' is TRUE as text. Returned rows 1, 2, 4.
-- ✅ CAST to a number, or use numeric literal as in Step 2

-- ❌ Wrong: querying a path with no supporting index on a big table -> full scan parsing every JSON doc
WHERE payload->>'$.device.os' = 'android'   -- fine at 4 rows, painful at 40M
-- ❌ Wrong: storing core relational data (user_id, status, amount) only inside JSON: no FK, no CHECK,
--    no column stats, hard joins
-- ❌ Wrong: expecting ->> on JSON null to give SQL NULL (it gives the text 'null')
```

---

## 🎯 Interview Tip (1 line)
Say: "I use JSON for sparse, variable attributes and keep anything I join, sort or constrain as real columns; I index hot paths with generated columns or functional/multi-valued indexes, and I'm careful about ->> returning text, which silently breaks numeric comparisons."

---

## 🔗 Related Questions
→ Q152 (EAV) | Q244 (JSON vs relational) | Q158 (Generated columns) | Q150 (Event sourcing payloads)
