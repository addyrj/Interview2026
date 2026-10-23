---

# Q011. Pagination — Offset vs Keyset (Cursor-Based)
# Category: Fundamentals
# Difficulty: ⭐⭐ Medium
# DB: Both (MySQL + PostgreSQL)

---

## ❓ Question
What is the problem with LIMIT/OFFSET pagination on large tables? Implement keyset (cursor-based) pagination. How do you handle compound sort keys?

---

## 💡 Quick Concept (2 lines only)
OFFSET pagination scans and discards N rows — performance degrades linearly (OFFSET 100,000 = scan 100,000 rows). Keyset pagination uses `WHERE id > last_seen_id` — always O(log N) via index, no wasted scan.
हिंदी: OFFSET = N rows scan करके discard करो — slow at scale। Keyset = `WHERE id > last_id` — index hit करो, O(log N)।

---

## ✅ Answer / Solution

```sql
-- ============================================
-- SETUP
-- ============================================

CREATE TABLE orders (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,  -- MySQL
  user_id    INT NOT NULL,
  amount     DECIMAL(10,2),
  created_at DATETIME NOT NULL,
  status     VARCHAR(20)
);

-- PgSQL version:
-- id BIGSERIAL PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL

CREATE INDEX idx_orders_created ON orders(created_at, id);
-- Composite index for compound sort

-- ============================================
-- PROBLEM: OFFSET PAGINATION (BAD AT SCALE)
-- ============================================

-- Page 1 (fast):
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 0;

-- Page 5001 (SLOW — scans 100,000 rows!):
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 100000;

-- EXPLAIN shows:
-- type: ALL (full scan) or index scan starting from row 1
-- rows: ~100020 rows examined to return 20!
-- This gets progressively slower: page 10000 = scan 200,000 rows

-- ============================================
-- SOLUTION 1: KEYSET PAGINATION BY ID
-- (Simple monotonic primary key)
-- ============================================

-- First page (no cursor):
SELECT id, user_id, amount, created_at
FROM orders
ORDER BY id ASC
LIMIT 20;
-- Returns rows with id 1..20. Client stores last_id = 20.

-- Next page (cursor = last_id from previous response):
SELECT id, user_id, amount, created_at
FROM orders
WHERE id > 20          -- ← cursor condition (uses PK index directly!)
ORDER BY id ASC
LIMIT 20;
-- Returns rows id 21..40. Store last_id = 40.

-- Always O(log N) — index seek to id=20, read next 20 rows forward.
-- No wasted scan!

-- ============================================
-- SOLUTION 2: KEYSET WITH COMPOUND SORT
-- (Sorted by created_at DESC, then id DESC for tiebreaking)
-- ============================================

-- First page:
SELECT id, user_id, amount, created_at
FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20;
-- Last row: created_at='2024-01-15 12:30:00', id=1234
-- Client stores cursor = {created_at: '2024-01-15 12:30:00', id: 1234}

-- Next page using "row comparison" (PgSQL supports this natively):
-- PgSQL:
SELECT id, user_id, amount, created_at
FROM orders
WHERE (created_at, id) < ('2024-01-15 12:30:00', 1234)
ORDER BY created_at DESC, id DESC
LIMIT 20;
-- PgSQL row comparison (tuple comparison) — clean syntax

-- MySQL: doesn't support tuple comparison in all cases — use explicit condition:
SELECT id, user_id, amount, created_at
FROM orders
WHERE created_at < '2024-01-15 12:30:00'
   OR (created_at = '2024-01-15 12:30:00' AND id < 1234)
ORDER BY created_at DESC, id DESC
LIMIT 20;
-- Equivalent logic: same created_at but lower id, OR earlier created_at
-- Index on (created_at, id) makes this efficient

-- ============================================
-- SOLUTION 3: BASE64-ENCODED OPAQUE CURSOR (API-FRIENDLY)
-- ============================================

-- Don't expose raw created_at + id to clients (leaks internals).
-- Encode cursor as opaque token:

/*  Node.js:
    function encodeCursor(row) {
      const payload = { created_at: row.created_at, id: row.id };
      return Buffer.from(JSON.stringify(payload)).toString('base64');
    }

    function decodeCursor(cursor) {
      return JSON.parse(Buffer.from(cursor, 'base64').toString('utf8'));
    }

    // API response:
    {
      "data": [...],
      "next_cursor": "eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSIsImlkIjoxMjM0fQ=="
    }

    // Next page request:
    GET /api/orders?cursor=eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNSIsImlkIjoxMjM0fQ==
*/

-- ============================================
-- COMPARISON TABLE
-- ============================================

/*
Feature                  | OFFSET Pagination     | Keyset Pagination
─────────────────────────┼───────────────────────┼───────────────────────
Performance              | O(N) — degrades       | O(log N) — constant
Jump to arbitrary page   | ✅ Yes                | ❌ No (forward only)
Stable under inserts     | ❌ Items shift pages  | ✅ Cursor-stable
Total count available    | ✅ Easy COUNT(*)       | ❌ Expensive
Sort by any column       | ✅ Easy               | ⚠️ Need unique sort key
Reverse / prev page      | ✅ Easy               | ⚠️ Needs extra logic
Use case                 | Small tables, admin   | Large tables, infinite
                         | pages, reports        | scroll, APIs
*/

-- ============================================
-- WHEN OFFSET IS OK
-- ============================================

-- Small tables (< 10,000 rows): offset is fine
-- Admin panels with "jump to page N": OFFSET is necessary
-- Reports with exact row count: OFFSET + COUNT(*)
-- Pre-fetching all pages in background: OFFSET acceptable

-- ============================================
-- FULL API EXAMPLE (Node.js + MySQL2)
-- ============================================

/*
async function getOrders(cursor, limit = 20) {
  let rows;
  if (!cursor) {
    // First page
    rows = await db.query(
      'SELECT id, user_id, amount, created_at FROM orders ORDER BY created_at DESC, id DESC LIMIT ?',
      [limit + 1]  // fetch one extra to detect if there's a next page
    );
  } else {
    const { created_at, id } = decodeCursor(cursor);
    rows = await db.query(`
      SELECT id, user_id, amount, created_at FROM orders
      WHERE created_at < ?
         OR (created_at = ? AND id < ?)
      ORDER BY created_at DESC, id DESC
      LIMIT ?
    `, [created_at, created_at, id, limit + 1]);
  }

  const hasNextPage = rows.length > limit;
  if (hasNextPage) rows.pop();  // remove the extra row

  return {
    data: rows,
    next_cursor: hasNextPage ? encodeCursor(rows[rows.length - 1]) : null,
    has_next_page: hasNextPage
  };
}
*/
```

---

## 🔍 Why This Works (3 lines max)
Keyset pagination uses an index seek (O(log N)) to jump directly to the last-seen row, then reads the next N rows forward — no wasted scanning. The compound sort key `(created_at, id)` provides a unique, stable cursor even when multiple rows share the same timestamp. Encoding the cursor as base64 hides implementation details from the client and makes the API resilient to future cursor format changes.
हिंदी: Keyset = index seek करके last row के बाद से read करो। (created_at, id) unique cursor बनाता है। Base64 encode = internals hide होते हैं।

---

## ⚡ Alternative Solution

```sql
-- Seek method for offset pagination (MySQL optimization):
-- If you MUST use page numbers, use a covering index + subquery:
SELECT o.*
FROM orders o
JOIN (
  SELECT id FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 100000
) fast_page USING(id);
-- First subquery: index-only scan (fast) to find the 20 IDs
-- Then join for full row data (20 lookups vs 100,000 row reads)
-- "Deferred join" / "late row lookup" pattern
-- Still O(N) but much faster in practice for InnoDB (index only, no row fetch)
```

---

## ⚠️ Common Mistake

```sql
-- ❌ Wrong: Keyset without a unique tiebreaker
SELECT * FROM orders WHERE created_at > '2024-01-15' ORDER BY created_at LIMIT 20;
-- Multiple rows can have same created_at → cursor is ambiguous!
-- Some rows will be skipped or repeated when created_at is the boundary value

-- ✅ Fix: Always include a unique column (id) as tiebreaker:
WHERE (created_at, id) < ('2024-01-15', 1234)  -- PgSQL tuple comparison
-- OR:
WHERE created_at < '2024-01-15' OR (created_at = '2024-01-15' AND id < 1234)

-- ❌ Wrong: Using ORDER BY RAND() with keyset — random order has no stable cursor!
-- ✅ Use offset + cache results for random-ordered pages (or just use OFFSET for small tables)

-- ❌ Wrong: Fetching extra row with LIMIT N+1 but forgetting to strip it:
-- Client sees N+1 rows on the "last" page — always pop() before returning!
```

---

## 🎯 Interview Tip (1 line)
Say: "OFFSET pagination scans and discards rows — it's O(N) and degrades at scale. I use keyset pagination: store the last row's sort key as a cursor, then `WHERE (sort_col, id) < (cursor_val, cursor_id)` — this is always O(log N) via index. Trade-off: you can't jump to arbitrary page numbers."

---

## 🔗 Related Questions
→ Q012 (COUNT optimization) | Q086 (EXPLAIN) | Q083 (composite index) | Q108 (N+1 problem)
