# 286. Build Pagination API
# हिंदी में: Pagination API बनाना

---

## 🔵 Simple Definition (English)
Pagination splits a large result set into smaller pages so clients don't fetch (and the server doesn't compute/transmit) thousands of rows in one response. The two main approaches are **offset-based** (`page`/`limit`, simple but has consistency issues) and **cursor-based** (`cursor`/`limit`, more stable under concurrent writes, used by Twitter/Stripe-style APIs).

## 🔵 सरल परिभाषा (Hindi)
Pagination बड़े result set को छोटे pages में बाँटती है ताकि client एक response में हज़ारों rows न ले (और server compute/transmit न करे)। दो main approaches: **offset-based** (`page`/`limit`, simple पर consistency issues) और **cursor-based** (`cursor`/`limit`, concurrent writes में ज़्यादा stable)।

---

## 🔴 Problem it Solves
Returning an entire table's worth of data in one API response is slow (large payload, slow serialization/transfer), memory-intensive on both server and client, and usually unnecessary (users only look at the first page or two anyway). Pagination limits each response to a manageable chunk, improving latency and resource usage. Beyond basic chunking, it also needs to handle a tricky correctness issue: what happens when rows are added/removed WHILE a user is paging through results?

## 🔴 यह क्यों बना? (Hindi)
पूरी table का data एक API response में देना slow है (बड़ा payload, slow transfer), memory-intensive, और आम तौर पर ज़रूरत नहीं (users सिर्फ पहले कुछ pages देखते हैं)। Pagination हर response को manageable chunk तक limit करती है। इसके अलावा एक tricky correctness issue भी handle करना होता है: rows add/remove होने पर क्या होता है जब user pages through कर रहा हो?

---

## 🟢 How it Works — Step by Step

Step 1 → **Offset-based pagination**: client requests `?page=2&limit=20`; server computes `OFFSET (page-1)*limit LIMIT limit` in the SQL query. Simple to implement, supports jumping to arbitrary pages ("go to page 50"), but has two problems: (a) `OFFSET` performance degrades for large offsets (DB still scans/skips all preceding rows), (b) if rows are inserted/deleted between page loads, results can shift (duplicate or skip items) — a classic "page 2 shows an item I already saw on page 1" bug.
Step 2 → **Cursor-based pagination**: client requests `?cursor=<encoded-last-seen-id>&limit=20`; server queries `WHERE id > cursor ORDER BY id LIMIT limit`. The cursor is typically an opaque, encoded pointer to the last item seen — stable under concurrent inserts/deletes since it's anchored to actual row identity, not positional offset. Downside: can't jump to an arbitrary page number, only "next"/"previous" from a known position.
Step 3 → Return pagination metadata: for offset-based, `{ page, limit, total, totalPages }`; for cursor-based, `{ data, nextCursor, hasMore }` (no total count typically, since counting is often skipped for performance).
Step 4 → Always specify a **stable sort order** (`ORDER BY created_at, id` with a tiebreaker) — without it, pagination can silently return inconsistent/duplicate results across pages since database row order isn't guaranteed without an explicit `ORDER BY`.
Step 5 → Encode cursors opaquely (base64 of a JSON object like `{ id, createdAt }`) rather than exposing raw IDs, both for a cleaner API contract and to avoid clients depending on internal ID structure.
Step 6 → Cap the maximum `limit` a client can request (e.g. max 100) to prevent abuse (someone requesting `?limit=1000000`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Offset-based**: `?page=2&limit=20` से `OFFSET`/`LIMIT` query — simple पर बड़े offsets पर slow, concurrent changes से items shift हो सकते हैं।
Step 2 → **Cursor-based**: `?cursor=X&limit=20` से `WHERE id > cursor` query — concurrent writes में stable, पर arbitrary page jump नहीं कर सकते।
Step 3 → सही pagination metadata return करो।
Step 4 → **Stable sort order** हमेशा specify करो tiebreaker के साथ।
Step 5 → Cursors opaquely encode करो (base64 JSON)।
Step 6 → Max `limit` cap करो abuse रोकने के लिए।

---

## 🟡 Real World Example
**Flipkart's** order history API uses offset pagination for the first few pages (`page=1,2,3` — users rarely go deeper, and it supports "jump to page 5" UX), but their internal analytics export API (pulling millions of order records for a data pipeline) uses cursor-based pagination keyed on `(created_at, id)`, since it must reliably page through the ENTIRE dataset without missing or duplicating rows even as new orders are continuously being inserted during the export — an offset-based approach would shift under that continuous write load.

## 🟡 Real Example Hindi mein
**Flipkart** का order history API पहले कुछ pages के लिए offset pagination use करता है (users ज़्यादा page नहीं जाते), पर internal analytics export API cursor-based pagination use करता है `(created_at, id)` से keyed, क्योंकि पूरे dataset को reliably page through करना है बिना rows miss/duplicate हुए, continuous writes के बावजूद।

---

## 💻 Code Example — Basic

```javascript
// basic-offset-pagination.js — simple offset-based pagination
// npm install express
// Run: node basic-offset-pagination.js

const express = require('express');
const app = express();

// Mock dataset — 1000 items
const allItems = Array.from({ length: 1000 }, (_, i) => ({ id: i + 1, name: `Item ${i + 1}` }));

app.get('/api/items', (req, res) => {
  const page = Math.max(1, Number(req.query.page) || 1);
  const limit = Math.min(100, Math.max(1, Number(req.query.limit) || 20)); // cap at 100

  const offset = (page - 1) * limit;
  const pageItems = allItems.slice(offset, offset + limit);

  res.json({
    data: pageItems,
    meta: {
      page,
      limit,
      total: allItems.length,
      totalPages: Math.ceil(allItems.length / limit),
      hasNextPage: offset + limit < allItems.length,
    },
  });
});

app.listen(3000, () => console.log('Offset pagination API on port 3000'));

// Try: curl "http://localhost:3000/api/items?page=2&limit=10"
```

## 💻 Code Example — Advanced

```javascript
// advanced-cursor-pagination.js — cursor-based pagination with opaque cursors
// npm install pg

const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Encode a cursor from the last row seen — opaque to the client
function encodeCursor(row) {
  const payload = JSON.stringify({ createdAt: row.created_at, id: row.id });
  return Buffer.from(payload).toString('base64url');
}

function decodeCursor(cursorString) {
  try {
    const json = Buffer.from(cursorString, 'base64url').toString('utf8');
    return JSON.parse(json);
  } catch {
    return null; // invalid/tampered cursor
  }
}

async function getProductsPage({ cursor, limit = 20 }) {
  const safeLimit = Math.min(100, Math.max(1, limit));
  let query, params;

  if (cursor) {
    const decoded = decodeCursor(cursor);
    if (!decoded) throw new Error('Invalid cursor');

    // Fetch rows AFTER the cursor position, using (created_at, id) as a stable composite key
    // This handles ties in created_at correctly via the id tiebreaker
    query = `
      SELECT id, name, price, created_at
      FROM products
      WHERE (created_at, id) > ($1, $2)
      ORDER BY created_at ASC, id ASC
      LIMIT $3
    `;
    params = [decoded.createdAt, decoded.id, safeLimit + 1]; // fetch one extra to detect hasMore
  } else {
    // First page — no cursor yet
    query = `SELECT id, name, price, created_at FROM products ORDER BY created_at ASC, id ASC LIMIT $1`;
    params = [safeLimit + 1];
  }

  const result = await pool.query(query, params);
  const rows = result.rows;

  const hasMore = rows.length > safeLimit;
  const pageRows = hasMore ? rows.slice(0, safeLimit) : rows; // drop the extra lookahead row

  return {
    data: pageRows,
    nextCursor: hasMore ? encodeCursor(pageRows[pageRows.length - 1]) : null,
    hasMore,
  };
}

module.exports = { getProductsPage };
```

---

## 🟠 Express.js Integration

```javascript
const express = require('express');
const { getProductsPage } = require('./advanced-cursor-pagination');

const app = express();

app.get('/api/products', async (req, res) => {
  try {
    const result = await getProductsPage({
      cursor: req.query.cursor,
      limit: req.query.limit ? Number(req.query.limit) : 20,
    });
    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.listen(3000, () => console.log('Cursor pagination API on port 3000'));

// Client usage pattern:
// 1. GET /api/products?limit=20                    → { data: [...], nextCursor: "eyJj...", hasMore: true }
// 2. GET /api/products?cursor=eyJj...&limit=20      → next page, using the cursor from step 1
// 3. Repeat until hasMore: false
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: No stable `ORDER BY`, causing inconsistent pagination across requests
✅ Correct: Always sort by a column (or combination) that uniquely and deterministically orders rows — without this, the database is free to return rows in any order across separate queries, causing items to appear on multiple pages or be skipped entirely.

```javascript
// Wrong: no explicit order — database's internal row order isn't guaranteed stable
`SELECT * FROM products LIMIT 20 OFFSET 20`

// Right: deterministic order with a unique tiebreaker
`SELECT * FROM products ORDER BY created_at ASC, id ASC LIMIT 20 OFFSET 20`
```

❌ Mistake 2: Allowing unbounded `limit` values
✅ Correct: Always clamp/cap the requested page size — an unbounded `limit` lets a client request the entire table in one response, defeating the purpose of pagination and risking server memory/time exhaustion.

```javascript
// Wrong: client can request ?limit=999999999
const limit = Number(req.query.limit) || 20;

// Right: clamp to a sane maximum
const limit = Math.min(100, Math.max(1, Number(req.query.limit) || 20));
```

---

## 🧠 Tricky Interview Question

```javascript
// User is viewing page 1 (items 1-20, sorted by creation time, newest first).
// Someone creates 5 NEW items while the user is about to load page 2.
// What happens with offset-based pagination here?
app.get('/items', (req, res) => {
  const offset = (page - 1) * limit; // page=2, limit=20 → offset=20
  const items = db.query(`SELECT * FROM items ORDER BY created_at DESC LIMIT 20 OFFSET 20`);
});
```
Answer: Because sorting is `DESC` (newest first) and 5 new items were inserted at the TOP, everything the user already saw on page 1 (positions 1-20) SHIFTS DOWN by 5 positions. What was at position 20 (the last item of page 1) is now at position 25 — still within the "already seen" range. But page 2's query (`OFFSET 20 LIMIT 20`) now fetches positions 21-40 of the NEW ordering, which includes items 16-20 from the user's ORIGINAL page 1 view (now shifted to positions 21-25) — causing those 5 items to appear AGAIN on page 2, duplicated from what the user already saw. This is the canonical offset-pagination consistency bug under concurrent inserts, and it's exactly why cursor-based pagination (anchored to a specific row's identity, not a numeric position) avoids it — new inserts anywhere in the table don't shift the meaning of "give me everything after THIS specific row."

---

## ⚫ Interview Questions + Answers

Q1: Why does `OFFSET` performance degrade for large page numbers?
A1: `OFFSET N` doesn't jump directly to row N — the database must still scan/count through all N preceding rows (even though it discards them) before returning the requested page. For `OFFSET 1000000`, the database does a huge amount of wasted work skipping a million rows just to return the next 20. This is why deep pagination (users jumping to page 5000) is noticeably slower than page 1, and why cursor-based pagination (which uses an indexed `WHERE id > X` condition, directly seekable via the index) doesn't have this degradation — it's always roughly the same speed regardless of how "deep" into the dataset you are.

Q2: Why can't cursor-based pagination support "jump to page N" the way offset pagination can?
A2: A cursor only encodes "the position right after THIS specific row" — it has no concept of a numeric page number, since it's not counting rows, just seeking relative to a known anchor point. To jump to "page 50" you'd need to know the cursor value at that exact position, which requires having already paged through (or precomputed) the preceding 49 pages. This is an inherent tradeoff: cursor pagination trades "arbitrary page jumping" for "stable, performant sequential/infinite-scroll pagination" — which is why infinite-scroll feeds (Twitter, Instagram) use cursors, while admin dashboards with numbered page controls often use offset pagination.

Q3: How would you implement "total count" alongside cursor-based pagination, given that cursors don't naturally provide one?
A3: Run a SEPARATE `COUNT(*)` query (with the same filters, no cursor/limit) if an accurate total is genuinely needed — accepting the extra query cost. For very large tables, consider an approximate count (cached periodically, or using database-specific fast estimation like Postgres's `pg_class.reltuples`) rather than an exact real-time count, since exact counting over huge filtered datasets can itself be a performance bottleneck. Many cursor-based APIs (Stripe, GitHub) simply DON'T expose a total count at all, relying on `hasMore`/`has_next_page` booleans instead — a deliberate design choice to avoid this cost.

Q4: What happens if a client sends a tampered or malformed cursor value?
A4: Since cursors are typically opaque encoded strings (base64 of a JSON payload, as in the advanced example), a malformed cursor fails to decode cleanly — the server should catch this (as `decodeCursor` does, returning `null` on parse failure) and respond with a clear `400 Bad Request` rather than crashing or silently returning wrong results. For added security/integrity, some APIs sign the cursor (HMAC) so tampering with the encoded values (e.g. manually crafting a cursor to skip ahead to another user's private data in a poorly-scoped query) can be detected and rejected.

Q5: How do you combine cursor-based pagination with additional sorting criteria, e.g. "sort by price, not creation date"?
A5: The cursor must encode ALL fields used in the `ORDER BY`, in the same order, plus a unique tiebreaker (usually the primary key) to handle ties. For "sort by price ascending," the cursor becomes `{ price, id }`, and the query becomes `WHERE (price, id) > ($1, $2) ORDER BY price ASC, id ASC`. If price has duplicates (many products at the same price), the `id` tiebreaker ensures deterministic, non-overlapping pages even among tied values — omitting it would reintroduce the same instability problem offset pagination has.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Offset-based: admin dashboards/UIs needing numbered page controls and "jump to page N," on datasets without heavy concurrent writes or where deep-pagination performance isn't critical
- Cursor-based: infinite-scroll feeds, APIs consumed programmatically (data exports, mobile app feeds), high-write-volume tables, or very large/deep datasets

❌ Avoid when:
- The entire dataset is small enough to return in one response reasonably (a dropdown with 50 options doesn't need pagination)
- Cursor-based pagination when the UI genuinely requires numbered page jumping as a core feature — offset is the better fit there despite its tradeoffs

---

## 📊 Visual Diagram
```
OFFSET-BASED PAGINATION
─────────────────────────
Page 1: SELECT * ORDER BY id LIMIT 20 OFFSET 0   → rows 1-20
Page 2: SELECT * ORDER BY id LIMIT 20 OFFSET 20  → rows 21-40
Page 3: SELECT * ORDER BY id LIMIT 20 OFFSET 40  → rows 41-60
         ↑ DB must scan/skip all preceding rows each time — slow for deep pages
         ↑ Concurrent inserts/deletes can shift which rows land on which page

CURSOR-BASED PAGINATION
─────────────────────────
Page 1: SELECT * WHERE id > 0   ORDER BY id LIMIT 20  → rows with id 1-20, nextCursor = encode(id:20)
Page 2: SELECT * WHERE id > 20  ORDER BY id LIMIT 20  → rows with id 21-40, nextCursor = encode(id:40)
         ↑ Always an indexed seek — same speed regardless of depth
         ↑ Stable even if rows are inserted elsewhere in the table during pagination
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Offset Pagination | Page by numeric position (page/limit) | Numeric position से page करना |
| Cursor Pagination | Page by anchor to a specific row | किसी specific row के anchor से page करना |
| Stable Sort Order | Deterministic ordering with a tiebreaker | Tiebreaker के साथ deterministic ordering |
| Opaque Cursor | Encoded pointer, not meant to be parsed by clients | Encoded pointer, client को parse नहीं करना चाहिए |
| hasMore | Boolean indicating if more pages exist | ज़्यादा pages हैं या नहीं बताने वाला boolean |
| Deep Pagination | Accessing far-into-the-dataset pages | Dataset में बहुत आगे वाले pages access करना |

---

## ⚡ 3-Line Summary
English: 1. Offset-based pagination (`page`/`limit`) is simple and supports page-jumping but degrades in performance for deep pages and shifts under concurrent writes. 2. Cursor-based pagination (`cursor`/`limit`, anchored to row identity) stays fast and stable regardless of depth or concurrent changes, at the cost of not supporting arbitrary page jumps. 3. Always use a deterministic `ORDER BY` with a unique tiebreaker, and cap the maximum page size clients can request.
Hindi: 1. Offset-based pagination simple है और page-jumping support करती है पर deep pages पर slow होती है और concurrent writes में shift होती है। 2. Cursor-based pagination (row identity से anchored) depth/concurrent changes के बावजूद fast/stable रहती है, पर arbitrary page jumps support नहीं करती। 3. हमेशा deterministic `ORDER BY` + unique tiebreaker use करो, और max page size cap करो।

---

## ➡️ Next Topic
**287. Build Multi-tenant API** — multiple tenants/organizations को data isolation के साथ serve करना।
