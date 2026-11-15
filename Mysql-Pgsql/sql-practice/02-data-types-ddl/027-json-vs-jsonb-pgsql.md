---

# Q027. JSON vs JSONB — PgSQL Difference
# Category: Data Types & DDL
# Difficulty: ⭐⭐⭐ Hard
# DB: PostgreSQL (MySQL JSON comparison included)

---

## ❓ Question
What is the difference between `JSON` and `JSONB` in PostgreSQL? Cover storage, duplicate keys, key order, operators, indexing and equality. How does MySQL's JSON type compare?

---

## 💡 Quick Concept (2 lines only)
JSON stores the exact input text (whitespace, key order and duplicate keys kept; re-parsed on every access); JSONB stores a decomposed binary form (keys sorted/deduplicated, last duplicate wins) that is slightly slower to write but supports indexing (GIN), containment operators and equality. Default to JSONB.
हिंदी: JSON text जैसा-का-तैसा रखता है; JSONB binary में parse करके रखता है, इसलिए index और fast query मिलती है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (PostgreSQL) — run this first
-- ============================================

CREATE TABLE api_logs (
  id            SERIAL PRIMARY KEY,
  payload_json  JSON,
  payload_jsonb JSONB
);

-- Same document into both; note extra spaces and a DUPLICATE key "plan"
INSERT INTO api_logs (payload_json, payload_jsonb) VALUES (
  '{"user": "asha",   "plan": "pro", "plan": "free", "tags": ["a","b"]}',
  '{"user": "asha",   "plan": "pro", "plan": "free", "tags": ["a","b"]}'
);

-- ============================================
-- SOLUTION
-- ============================================

-- 1) What got stored?
SELECT payload_json::text AS json_text, payload_jsonb::text AS jsonb_text FROM api_logs;
-- json_text  | {"user": "asha",   "plan": "pro", "plan": "free", "tags": ["a","b"]}   <- verbatim
-- jsonb_text | {"plan": "free", "tags": ["a", "b"], "user": "asha"}   <- sorted, deduped, normalized

-- 2) Extraction operators work on both (->  returns json(b), ->> returns text)
SELECT payload_jsonb->>'plan' AS plan, payload_jsonb->'tags'->>0 AS first_tag, payload_json->>'plan' AS plan_json
FROM api_logs;
-- plan | first_tag | plan_json
-- free | a         | free        <- even JSON returns the LAST duplicate when read

-- 3) Containment / existence operators: JSONB only
SELECT id FROM api_logs WHERE payload_jsonb @> '{"plan":"free"}';       -- 1
SELECT id FROM api_logs WHERE payload_json  @> '{"plan":"free"}';
-- ERROR: operator does not exist: json @> unknown
SELECT payload_jsonb ? 'user' AS has_user, payload_jsonb ?| array['nope','plan'] AS has_any FROM api_logs;
-- true | true

-- 4) Indexing: GIN works on JSONB only
CREATE INDEX idx_payload_gin ON api_logs USING GIN (payload_jsonb);     -- OK
CREATE INDEX idx_payload_json_gin ON api_logs USING GIN (payload_json);
-- ERROR: data type json has no default operator class for access method "gin"

-- 5) Equality: JSONB yes, JSON no
SELECT '{"a":1,"b":2}'::jsonb = '{"b":2,"a":1}'::jsonb AS jsonb_equal;   -- true
SELECT '{"a":1,"b":2}'::json  = '{"b":2,"a":1}'::json;
-- ERROR: operator does not exist: json = json

-- 6) Modify in place (JSONB has rich functions)
SELECT jsonb_set(payload_jsonb, '{plan}', '"enterprise"') ->> 'plan' AS updated FROM api_logs;
-- enterprise

-- 7) Quirks
SELECT ('{"a": 1, "a": 2}'::jsonb)::text AS dup_key, ('[1,   2]'::json)::text AS json_ws;
-- {"a": 2} | [1,   2]
SELECT '{"a":"x\u0000y"}'::jsonb;
-- ERROR: unsupported Unicode escape sequence   (\u0000 is allowed in JSON, rejected by JSONB)

-- ============================================
-- EXPECTED OUTPUT
-- ============================================
-- Everything above was run on PostgreSQL 18 via PGlite (GIN index creation succeeded on
-- the tiny table; the index's real performance benefit was not benchmarked).
```

---

## 🔍 Why This Works (3 lines max)
JSON is validated text, so every operator re-parses it; JSONB is parsed once on insert into a binary tree with unique, sorted keys, enabling fast key lookup, `@>` containment and GIN indexing. The price is a little extra insert time and loss of original formatting/duplicate keys.
हिंदी: JSON हर बार parse होता है; JSONB एक बार parse होकर index-योग्य बन जाता है, formatting चली जाती है।

---

## ⚡ Alternative Solution

```sql
-- ============================================
-- MySQL JSON (MySQL 9.1.0, verified) — behaves like JSONB, not like PgSQL JSON
-- ============================================
CREATE TABLE api_logs (
  id      INT PRIMARY KEY AUTO_INCREMENT,
  payload JSON,
  plan    VARCHAR(20) GENERATED ALWAYS AS (payload->>'$.plan') VIRTUAL,   -- index via generated column
  INDEX idx_plan (plan)
);
INSERT INTO api_logs (payload) VALUES ('{"user": "asha",   "plan": "pro", "plan": "free", "tags": ["a","b"]}');

SELECT payload FROM api_logs;
-- {"plan": "free", "tags": ["a", "b"], "user": "asha"}      <- normalized, last duplicate wins

SELECT payload->>'$.plan' AS plan, payload->'$.tags[0]' AS first_tag FROM api_logs;
-- free | "a"            <- -> keeps JSON quoting, ->> unquotes
SELECT id FROM api_logs WHERE plan = 'free';                  -- 1  (EXPLAIN: type=ref, key=idx_plan)
SELECT JSON_CONTAINS(payload, '"free"', '$.plan') FROM api_logs;          -- 1
SELECT JSON_UNQUOTE(JSON_EXTRACT(JSON_SET(payload, '$.plan', 'enterprise'), '$.plan')) FROM api_logs;  -- enterprise
SELECT CAST('{"b":2,"a":1}' AS JSON) = CAST('{"a":1,"b":2}' AS JSON);    -- 1
SELECT CAST('{"zeta":1,"alpha":2}' AS JSON);                              -- {"zeta": 1, "alpha": 2}
-- (MySQL orders keys by length, then alphabetically: zeta before alpha)

-- MySQL has no GIN-style index on whole documents; use generated columns or multi-valued indexes
-- (INDEX ((CAST(payload->'$.tags' AS CHAR(10) ARRAY)))) for arrays — not run here.
-- Note: ->> is only valid on a column/path expression, not on a function result like JSON_SET(...)->>'$.x' (syntax error).

-- PgSQL equivalent of the generated-column index: an expression index
CREATE INDEX idx_plan ON api_logs ((payload_jsonb->>'plan'));
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: choosing JSON "because it's faster to insert" then filtering on keys
SELECT * FROM api_logs WHERE payload_json->>'plan' = 'free';   -- full scan + re-parse every row
-- ❌ Wrong: expecting JSONB to preserve key order / formatting / duplicate keys (audit/signature use cases!)
-- ❌ Wrong: GIN index on JSONB, then querying with ->> equality — GIN serves @>, ?, ?|, not ->>
WHERE payload_jsonb->>'plan' = 'free'      -- needs a btree EXPRESSION index instead
-- ✅ Correct: WHERE payload_jsonb @> '{"plan":"free"}'   (uses GIN)
--            or CREATE INDEX ON api_logs ((payload_jsonb->>'plan'))  for the ->> form
-- ❌ Wrong: stuffing core relational fields (ids, amounts used in joins) into JSON(B) instead of columns
```

---

## 🎯 Interview Tip (1 line)
Say: "JSONB by default — it's binary, deduplicated, comparable and GIN-indexable (@>, ?); I only use JSON when I must preserve the exact text. For hot attributes I still promote them to real columns or expression indexes, and in MySQL I index JSON via generated columns."

---

## 🔗 Related Questions
→ Q022 (TEXT / VARCHAR) | Q026 (ENUM vs alternatives) | Q030 (CHECK constraints on JSON shape) | Q018 (CTE)
