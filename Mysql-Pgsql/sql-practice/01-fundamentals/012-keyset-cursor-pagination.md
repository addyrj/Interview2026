---

# Q012. Keyset / Cursor-Based Pagination
# Category: Fundamentals
# Difficulty: ⭐⭐⭐ Hard
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
A `feed_posts` feed is sorted by `created_at DESC`, and many posts share the same timestamp. Implement "next page" and "previous page" with keyset (cursor) pagination so no row is skipped or repeated, show the supporting index, and explain why OFFSET pages drift when new rows arrive. (Q011 covers the OFFSET-vs-keyset basics; this one is the compound-cursor, tie-safe version.)

---

## 💡 Quick Concept (2 lines only)
Keep the last row's sort key as the cursor and ask for rows strictly "after" it: `WHERE (created_at, id) < (:last_created_at, :last_id) ORDER BY created_at DESC, id DESC LIMIT n`. The unique `id` is part of the key, so ties on `created_at` cannot cause skips or duplicates.
हिंदी: आखिरी row की (created_at, id) को cursor बनाओ और उससे "आगे" की rows माँगो; unique `id` tie-breaker होने से कोई row छूटती या दोहराती नहीं।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP (run this first)
-- ============================================

CREATE TABLE feed_posts (
  id         INT PRIMARY KEY,
  author     VARCHAR(20),
  created_at DATETIME,          -- PostgreSQL: use TIMESTAMP (DATETIME does not exist there)
  title      VARCHAR(40)
);

INSERT INTO feed_posts VALUES
  (1, 'asha',   '2024-05-01 10:00:00', 'p1'),
  (2, 'ben',    '2024-05-01 10:00:00', 'p2'),   -- same timestamp as id 1
  (3, 'asha',   '2024-05-02 09:00:00', 'p3'),
  (4, 'chitra', '2024-05-02 09:00:00', 'p4'),   -- three rows share 05-02 09:00
  (5, 'ben',    '2024-05-02 09:00:00', 'p5'),
  (6, 'dev',    '2024-05-03 08:00:00', 'p6'),
  (7, 'asha',   '2024-05-04 07:00:00', 'p7'),
  (8, 'ben',    '2024-05-05 06:00:00', 'p8');

-- Index that matches the ORDER BY exactly (both engines accept this syntax)
CREATE INDEX idx_feed_created_id ON feed_posts (created_at DESC, id DESC);

-- ============================================
-- SOLUTION
-- ============================================

-- Page 1 (no cursor yet)
SELECT id, created_at FROM feed_posts
ORDER BY created_at DESC, id DESC
LIMIT 3;

-- Page 2: cursor = last row of page 1 = ('2024-05-03 08:00:00', 6)
SELECT id, created_at FROM feed_posts
WHERE (created_at, id) < ('2024-05-03 08:00:00', 6)    -- row-value comparison
ORDER BY created_at DESC, id DESC
LIMIT 3;

-- Page 3: cursor = ('2024-05-02 09:00:00', 4)  <- cursor lands INSIDE a group of ties
SELECT id, created_at FROM feed_posts
WHERE (created_at, id) < ('2024-05-02 09:00:00', 4)
ORDER BY created_at DESC, id DESC
LIMIT 3;

-- ============================================
-- EXPECTED OUTPUT (identical on MySQL 9.1.0 and PGlite)
-- ============================================

-- Page 1: ids 8, 7, 6
-- Page 2: ids 5, 4, 3          (all three at 2024-05-02 09:00:00)
-- Page 3: ids 3, 2, 1          <- cursor was id 4 (a tie row); id 3 shares its timestamp and
--         is correctly included, then 2 and 1 from 05-01 10:00
-- MySQL 9.1.0 EXPLAIN for page 2: key=idx_feed_created_id, rows=3, Extra "Using where; Using index"
--   i.e. an index range scan that reads only a few rows - no sort, no skipped-row scan.
```

---

## 🔍 Why This Works (3 lines max)
The row-value comparison `(created_at, id) < (a, b)` means "created_at < a, or created_at = a and id < b", which matches the sort order exactly. The composite index lets the engine seek straight to the cursor and read `n` rows - cost is O(log N + n) at any depth. Because `id` is unique, the sort key is unique and the cursor is unambiguous.
हिंदी: `(created_at, id) < (a, b)` का मतलब sort order के हिसाब से "आगे की rows" है; composite index से सीधे cursor पर पहुँचते हैं, इसलिए page कितना भी गहरा हो, तेज़ रहता है।

---

## ⚡ Alternative Solution

```sql
-- Expanded OR form - for engines/ORMs without row-value comparison (same rows, verified):
SELECT id, created_at FROM feed_posts
WHERE created_at < '2024-05-03 08:00:00'
   OR (created_at = '2024-05-03 08:00:00' AND id < 6)
ORDER BY created_at DESC, id DESC
LIMIT 3;                                            -- ids 5, 4, 3

-- Previous page: flip comparison AND order, then re-reverse in the app (or an outer query)
SELECT id, created_at FROM feed_posts
WHERE (created_at, id) > ('2024-05-04 07:00:00', 7)
ORDER BY created_at ASC, id ASC LIMIT 3;            -- id 8 (the only newer row)

-- Cursor token: base64(created_at|id) sent to the client, never raw SQL
-- Fetch n+1 rows to know if "has_next" without a COUNT(*)

-- Syntax differences:
--   MySQL: DATETIME;   PostgreSQL: TIMESTAMP (or TIMESTAMPTZ).  Row-value comparison works in both.
--   Mixed ASC/DESC keys cannot use row-value comparison correctly -> use the expanded OR form.
--   PostgreSQL supports NULLS FIRST/LAST in the index; MySQL has no such option, keep sort keys NOT NULL.
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: cursor on a non-unique column only
SELECT id FROM feed_posts WHERE created_at < '2024-05-02 09:00:00'
ORDER BY created_at DESC, id DESC LIMIT 3;
-- Returned ids 2, 1 on both engines: id 3 (same timestamp as the cursor row) was SKIPPED forever
-- ✅ Include the unique tiebreaker in both the WHERE and the ORDER BY

-- ❌ Wrong: LIMIT/OFFSET while data changes. I fetched page 1 (OFFSET 0 = ids 8,7,6), then inserted
--    a newer post (id 9, 05-06). OFFSET 3 then returned ids 6, 5, 4 -> id 6 was shown TWICE.
--    The keyset query with cursor (05-03 08:00, 6) still returned 5, 4, 3 - stable.
-- ❌ Wrong: keyset with no index on the sort key - you pay for a full sort on every page
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET pagination re-reads and discards the skipped rows and drifts when data changes; I use keyset pagination on a unique composite key like (created_at, id) with a matching index, fetch n+1 rows for has_next, and accept that you lose random 'jump to page 50' access."

---

## 🔗 Related Questions
→ Q011 (Offset vs Keyset) | Q001 (SELECT/ORDER BY/LIMIT) | Q075 (Top N per group) | Q010 (Date/time functions)
