---

# Q118. OR vs UNION in WHERE Clause
# Category: Query Optimization
# Difficulty: ⭐⭐ Medium
# DB: Both

---

## ❓ Question
Find a customer by `email` OR by `phone`. Compare `WHERE a = ? OR b = ?` with `UNION`/`UNION ALL`: when does the optimizer use both indexes, when does OR fall back to a full table scan, and how do you rewrite it?

---

## 💡 Quick Concept (2 lines only)
Modern optimizers can combine two indexes for OR (PostgreSQL BitmapOr, MySQL index_merge union) as long as EVERY OR branch is indexable. If even one branch is not (no index, function on column), the whole OR degrades to a full scan; splitting into UNION lets each branch use its own index.
हिंदी: OR की हर शर्त पर index हो तो optimizer दोनों index जोड़ लेता है; एक भी शर्त बिना index की हो तो पूरा table scan होता है, तब UNION से हर हिस्से को अलग index मिलता है।

---

## ✅ Answer / Solution

```sql
-- Verified: PostgreSQL on PGlite 18.6 and MySQL 9.1.0, 50,000 rows.

-- ============================================
-- SETUP (PostgreSQL)  -- MySQL: AUTO_INCREMENT instead of SERIAL, see Alternative
-- ============================================

CREATE TABLE customers (
  id    SERIAL PRIMARY KEY,
  email VARCHAR(100),
  phone VARCHAR(20),
  city  VARCHAR(50)
);

INSERT INTO customers (email, phone, city)
SELECT 'user' || g || '@example.com', '9' || lpad(g::text, 9, '0'), 'city' || (g % 100)
FROM generate_series(1, 50000) g;

CREATE INDEX idx_customers_email ON customers (email);
CREATE INDEX idx_customers_phone ON customers (phone);
ANALYZE customers;

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: OR with two indexed columns
SELECT id, email, phone FROM customers
WHERE email = 'user42@example.com' OR phone = '9000000777'
ORDER BY id;

-- Step 2: UNION rewrite (de-duplicates, so a row matching both appears once)
SELECT id, email FROM customers WHERE email = 'user42@example.com'
UNION
SELECT id, email FROM customers WHERE phone = '9000000777'
ORDER BY id;

-- Step 3: when OR breaks - one branch is not indexed (city has no index)
EXPLAIN SELECT id FROM customers WHERE email = 'user42@example.com' OR city = 'city7';

-- Step 4: UNION ALL when branches cannot overlap (cheaper, no de-dup sort)
-- SELECT ... WHERE status = 'open' UNION ALL SELECT ... WHERE status = 'pending';

-- ============================================
-- EXPECTED OUTPUT
-- ============================================

-- Step 1 result (both strategies return the same 2 rows):
-- id  | email                | phone
-- 42  | user42@example.com   | 9000000042
-- 777 | user777@example.com  | 9000000777
--
-- PostgreSQL plan for OR (real): Bitmap Heap Scan -> BitmapOr
--   -> Bitmap Index Scan on idx_customers_email
--   -> Bitmap Index Scan on idx_customers_phone         (cost 8.72..16.36)
-- PostgreSQL plan for UNION (real): Unique -> Sort -> Append of 2 Index Scans   (cost ~16.76)
-- Both are fast here: the optimizer handled OR well, UNION was not needed.
--
-- Step 3 (real): Seq Scan on customers (cost=0.00..1218.00 rows=493 width=4)
--   Filter: (email = 'user42@example.com') OR (city = 'city7')    <- one bad branch kills the index
```

---

## 🔍 Why This Works (3 lines max)
For OR the planner builds one bitmap per branch from the matching index and ORs them together, which only works if every branch has an index. UNION runs each SELECT independently so each can pick its own best plan, at the cost of an extra sort/hash to remove duplicates.
हिंदी: OR में हर branch का index चाहिए; UNION हर SELECT को अलग plan देता है पर duplicates हटाने का थोड़ा extra काम करता है।

---

## ⚡ Alternative Solution

```sql
-- MySQL 9.1.0 (real EXPLAIN output):
CREATE TABLE customers (
  id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(100), phone VARCHAR(20), city VARCHAR(50),
  INDEX idx_email (email), INDEX idx_phone (phone)
);
EXPLAIN SELECT id, email FROM customers WHERE email = 'user42@example.com' OR phone = '9000000777';
--  type=index_merge key=idx_email,idx_phone rows=2  Extra: Using union(idx_email,idx_phone); Using where
EXPLAIN SELECT id, email FROM customers WHERE email = 'user42@example.com'
UNION SELECT id, email FROM customers WHERE phone = '9000000777';
--  two ref lookups + UNION RESULT using temporary
EXPLAIN SELECT id FROM customers WHERE email = 'user42@example.com' OR city = 'city7';
--  type=ALL rows=50097 (full scan)  -> same degradation as PostgreSQL

-- Use UNION ALL + guard against duplicates instead of UNION when the cost of de-dup matters:
SELECT id FROM customers WHERE email = 'user42@example.com'
UNION ALL
SELECT id FROM customers WHERE phone = '9000000777' AND email <> 'user42@example.com';
-- (this UNION ALL variant was not run; NULL-safe version needs: AND (email IS NULL OR email <> ...))

-- Index merge can be disabled/inspected in MySQL: SELECT @@optimizer_switch;  (index_merge_union=on)
```

---

## ⚠️ Common Mistake
```sql
-- ❌ Rewriting every OR as UNION blindly: on 9.1 and PG 18 the optimizer already used both
--    indexes for the 2-indexed-column OR, and UNION added a Sort/Unique step (more work).
-- ❌ Using UNION when you meant UNION ALL -> unnecessary sort/dedup of large result sets.
-- ❌ Wrapping one OR branch in a function: email = ? OR lower(phone) = ?
--    -> Seq Scan (verified on PostgreSQL) unless an expression index exists on lower(phone).
-- ❌ OR inside a multi-column composite index prefix: (a,b) index cannot serve a=1 OR b=2.
-- ✅ Check EXPLAIN first; rewrite to UNION/UNION ALL only when the OR plan is a Seq Scan / type=ALL.
```

---

## 🎯 Interview Tip (1 line)
Say: "OR is fine if every branch is independently indexed - PostgreSQL uses BitmapOr and MySQL index_merge - but one unindexed or function-wrapped branch forces a full scan; then I split into UNION ALL (adding exclusion predicates to avoid duplicates) or add the missing index, and I prove it with EXPLAIN."

---

## 🔗 Related Questions
→ Q119 (Function on indexed column) | Q117 (Avoid SELECT *) | Q109 (Slow query diagnosis) | Q239 (Find duplicates)
