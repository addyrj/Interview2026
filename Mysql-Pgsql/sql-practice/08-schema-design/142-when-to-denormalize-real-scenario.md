---

# Q142. When to Denormalize — Real Scenario
# Category: Schema Design
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL 8.0+ | PostgreSQL) — run on MySQL 9.1.0 and PGlite

---

## ❓ Question
A blog listing page shows every post with its comment count, and it is hit thousands of times a second. `COUNT(*)` over comments per request is too slow. When is it right to denormalize, how do you store the redundant value, and how do you keep it from drifting?

---

## 💡 Quick Concept (2 lines only)
Denormalize deliberately: store a redundant, precomputed value (counter, snapshot, copied column) when reads vastly outnumber writes and the join/aggregate is a proven bottleneck. You trade write complexity and consistency risk for read speed.
हिंदी: Denormalize तभी करो जब reads ज़्यादा हों और join/count सच में bottleneck हो; बदले में writes जटिल होते हैं और data drift का जोखिम आता है।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE posts (
  post_id       INT PRIMARY KEY,
  title         VARCHAR(100),
  comment_count INT NOT NULL DEFAULT 0      -- <- the denormalized (redundant) column
);

CREATE TABLE comments (
  comment_id INT PRIMARY KEY,
  post_id    INT NOT NULL,
  body       VARCHAR(200),
  FOREIGN KEY (post_id) REFERENCES posts(post_id)
);

INSERT INTO posts (post_id, title) VALUES (1, 'Intro to MVCC'), (2, 'Indexing 101');
INSERT INTO comments VALUES (1, 1, 'Nice'), (2, 1, 'Thanks'), (3, 2, 'Great');

-- ============================================
-- SOLUTION
-- ============================================

-- Step 1: backfill the counter from the source of truth
UPDATE posts p
SET comment_count = (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.post_id);

-- Step 2: read path is now a plain column read (no join, no GROUP BY)
--   SELECT post_id, title, comment_count FROM posts ORDER BY post_id;

-- Step 3: write path keeps it in sync INSIDE the same transaction
--   BEGIN;
--   INSERT INTO comments VALUES (4, 2, 'Question');
--   UPDATE posts SET comment_count = comment_count + 1 WHERE post_id = 2;
--   COMMIT;

-- Step 4: audit query - compare cache vs truth
SELECT p.post_id, p.title,
       COUNT(c.comment_id) AS live_count,
       p.comment_count     AS cached_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.post_id
GROUP BY p.post_id, p.title, p.comment_count
ORDER BY p.post_id;

-- ============================================
-- EXPECTED OUTPUT (real; same on MySQL 9.1.0 and PGlite)
-- ============================================

-- post_id | title         | live_count | cached_count
-- 1       | Intro to MVCC | 2          | 2
-- 2       | Indexing 101  | 1          | 1

-- Now simulate DRIFT: a code path inserts a comment but forgets the counter
INSERT INTO comments VALUES (4, 2, 'Question');
UPDATE posts SET comment_count = comment_count + 1 WHERE post_id = 2;     -- correct path
INSERT INTO comments VALUES (5, 2, 'Sneaky insert, forgot counter');      -- buggy path

SELECT p.post_id, COUNT(c.comment_id) AS live_count, p.comment_count AS cached_count
FROM posts p LEFT JOIN comments c ON c.post_id = p.post_id
GROUP BY p.post_id, p.comment_count
HAVING COUNT(c.comment_id) <> p.comment_count;       -- find drifted rows
-- post_id | live_count | cached_count
-- 2       | 3          | 2                <- drift detected

-- Repair (run as a periodic reconciliation job):
UPDATE posts p
SET comment_count = (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.post_id);
-- post 1 -> 2, post 2 -> 3
```

---

## 🔍 Why This Works (3 lines max)
The counter turns an O(comments) aggregate into an O(1) column read, and the audit/repair query keeps the redundant copy honest against the source of truth. Updating it in the same transaction as the insert prevents partial updates.
हिंदी: Counter से O(1) read मिलता है; audit/repair query source of truth से मिलान करके drift ठीक करती है, और same transaction में update होने से अधूरा update नहीं होता।

---

## ⚡ Alternative Solution

```sql
-- Other legitimate denormalizations
-- 1) Snapshot of business history: order_items.unit_price_at_purchase (price changes later must not rewrite old orders)
-- 2) Copied column to avoid a join: orders.customer_city copied at order time
-- 3) Precomputed aggregate / summary table refreshed by a job
-- 4) Materialized view (PgSQL; no native one in MySQL):
CREATE MATERIALIZED VIEW post_stats AS
  SELECT post_id, COUNT(*) AS comment_count FROM comments GROUP BY post_id;
REFRESH MATERIALIZED VIEW post_stats;       -- manual/cron; CONCURRENTLY needs a unique index
-- (materialized view syntax is standard PgSQL; not part of the run above)

-- Keep the counter correct automatically with a trigger instead of app code:
-- MySQL : CREATE TRIGGER ... AFTER INSERT ON comments FOR EACH ROW
--           UPDATE posts SET comment_count = comment_count + 1 WHERE post_id = NEW.post_id;
-- PgSQL : same idea with a trigger function (hot-row contention on very popular posts!)

-- Generated columns only help for same-row expressions (Q158), not cross-table counts.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: denormalizing first, measuring never.
--    A proper index on comments(post_id) + a cached/paginated query is often enough:
CREATE INDEX idx_comments_post ON comments (post_id);

-- ❌ Wrong: updating the counter in a separate transaction (or from many code paths) -> drift (shown above).
-- ✅ One write path (service method / trigger) + a nightly reconciliation job.

-- ❌ Wrong: a single global counter row (e.g. site_total_comments) updated on every insert
--    -> row-lock hot spot serializes all writers. Shard the counter or batch it.

-- ❌ Wrong: incrementing with read-modify-write in the app (SELECT then UPDATE SET =N+1)
-- ✅ UPDATE posts SET comment_count = comment_count + 1 ...   (atomic)
```

---

## 🎯 Interview Tip (1 line)
Say: "I stay normalized until a measured read bottleneck justifies a redundant column; then I pick the least risky form (snapshot, counter, materialized view), keep one write path in the same transaction, and add a reconciliation job to detect drift."

---

## 🔗 Related Questions
→ Q141 (Normal forms) | Q158 (Generated columns) | Q145 (Soft delete) | Q146 (Audit log table)
