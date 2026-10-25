# 176. Pagination — Cursor vs Offset
# हिंदी में: Pagination — Cursor vs Offset Approach

---

## 🔵 Simple Definition (English)
**Pagination** splits a large dataset into smaller "pages" returned one at a time. **Offset pagination** (`?page=3&limit=20`) skips N rows and returns the next M — simple but slow/unstable on large or changing datasets. **Cursor pagination** (`?after=<lastItemId>&limit=20`) uses a pointer to the last-seen item to fetch the next batch — faster and stable even as data changes.

## 🔵 सरल परिभाषा (Hindi)
**Pagination** बड़े dataset को छोटे "pages" में बाँटकर एक-एक return करता है। **Offset pagination** (`?page=3&limit=20`) N rows skip करके अगली M return करता है — simple पर large/changing datasets पर slow/unstable। **Cursor pagination** (`?after=<lastItemId>&limit=20`) last-seen item के pointer से अगला batch fetch करता है — faster और data बदलने पर भी stable।

---

## 🔴 Problem it Solves
Offset pagination has two production-breaking issues at scale:
1. **Performance degrades as page number grows**: `SELECT * FROM orders OFFSET 1000000 LIMIT 20` forces the DB to scan and discard 1 million rows before returning 20 — gets slower and slower on later pages.
2. **Items shift / duplicate when data changes between page loads**: if Amazon shows "page 2 of search results" and a new product gets inserted at the top while the user is scrolling, OFFSET-based pages can show the SAME item twice or skip an item entirely — because "page 2" is just "rows 21-40 right now," and that set shifts as data is added/removed.

Cursor pagination avoids both: it jumps directly to "give me items after THIS specific item" (indexed lookup, no scan-and-discard) and is stable because it's anchored to an actual item, not a shifting numeric offset.

## 🔴 यह क्यों बना? (Hindi)
Offset pagination में scale पर दो production-breaking issues हैं:
1. **Page number बढ़ने पर performance गिरती है**: `SELECT * FROM orders OFFSET 1000000 LIMIT 20` DB को 1 million rows scan करके discard करने पर मजबूर करता है, फिर 20 return करता है — later pages धीरे-धीरे slower होते जाते हैं।
2. **Data बदलने पर items shift/duplicate होते हैं**: अगर Amazon "page 2" दिखा रहा है और scroll के दौरान नया product top पर insert हो जाये, तो OFFSET-based pages SAME item दो बार दिखा सकते हैं या कोई item पूरी तरह skip हो सकता है — क्योंकि "page 2" सिर्फ "अभी के rows 21-40" है, जो data add/remove होने पर shift हो जाता है।

Cursor pagination दोनों problems avoid करता है: यह directly "इस specific item के बाद वाले items दो" पर जाता है (indexed lookup, कोई scan-and-discard नहीं) और stable है क्योंकि यह एक actual item पर anchored है, shifting numeric offset पर नहीं।

---

## 🟢 How it Works — Step by Step

**Offset pagination:**
Step 1 → Client sends `?page=3&limit=20`.
Step 2 → Server computes `offset = (page - 1) * limit = 40`.
Step 3 → Query: `SELECT * FROM table ORDER BY id LIMIT 20 OFFSET 40`.
Step 4 → Server returns items + `totalCount` so client can show "Page 3 of 50."

**Cursor pagination:**
Step 1 → Client sends `?limit=20` initially → server returns 20 items + a `nextCursor` (the last item's unique, sortable ID/timestamp).
Step 2 → Client sends next request with `?after=<nextCursor>&limit=20`.
Step 3 → Query: `SELECT * FROM table WHERE id > <cursor> ORDER BY id LIMIT 20` — uses an index, no scanning skipped rows.
Step 4 → Server returns the next batch + a new `nextCursor` (or `null` if no more data).

## 🟢 कैसे काम करता है? (Hindi)
**Offset pagination:**
Step 1 → Client `?page=3&limit=20` भेजता है।
Step 2 → Server `offset = (page - 1) * limit = 40` compute करता है।
Step 3 → Query: `SELECT * FROM table ORDER BY id LIMIT 20 OFFSET 40`।
Step 4 → Server items + `totalCount` return करता है ताकि client "Page 3 of 50" दिखा सके।

**Cursor pagination:**
Step 1 → Client शुरू में `?limit=20` भेजता है → server 20 items + `nextCursor` (last item का unique, sortable ID/timestamp) return करता है।
Step 2 → Client अगली request `?after=<nextCursor>&limit=20` के साथ भेजता है।
Step 3 → Query: `SELECT * FROM table WHERE id > <cursor> ORDER BY id LIMIT 20` — index use होता है, कोई skip rows scan नहीं।
Step 4 → Server अगला batch + नया `nextCursor` return करता है (या `null` अगर और data नहीं)।

---

## 🟡 Real World Example
**Instagram/Twitter-style infinite scroll feeds (used similarly by Zomato's review feed)** always use cursor pagination — as new posts/reviews are constantly being added, offset pagination would cause duplicate or skipped posts as users scroll (since "page 2" keeps shifting). Cursor-based "give me posts older than this timestamp/ID" stays stable regardless of new inserts. Meanwhile, Amazon's traditional numbered search result pages ("Page 1, 2, 3... 50") use OFFSET pagination because showing explicit page numbers and jumping to "page 37 directly" is a feature users expect — something cursor pagination can't easily do (you can't jump to an arbitrary page without walking through cursors sequentially).

## 🟡 Real Example Hindi mein
**Instagram/Twitter-style infinite scroll feeds (Zomato का review feed भी similar)** हमेशा cursor pagination use करते हैं — क्योंकि नए posts/reviews लगातार add होते रहते हैं, offset pagination duplicate या skipped posts cause करेगा scroll करते वक़्त (क्योंकि "page 2" shift होता रहता है)। Cursor-based "इस timestamp/ID से पुराने posts दो" data add होने पर भी stable रहता है। वहीं Amazon के traditional numbered search result pages ("Page 1, 2, 3... 50") OFFSET pagination use करते हैं क्योंकि explicit page numbers दिखाना और "page 37 पर directly जाना" एक feature है जो users expect करते हैं — जो cursor pagination से आसान नहीं है।

---

## 💻 Code Example — Basic

```javascript
// basic-pagination.js
// Install: npm install express mongoose

const express = require('express');
const app = express();
const Product = require('./models/Product'); // assume a Mongoose model

// --- OFFSET PAGINATION ---
app.get('/products/offset', async (req, res) => {
  const page = Number(req.query.page) || 1;    // which page, default 1
  const limit = Number(req.query.limit) || 20; // items per page, default 20
  const skip = (page - 1) * limit;             // how many items to skip

  const [items, total] = await Promise.all([
    Product.find().sort({ _id: 1 }).skip(skip).limit(limit), // skip + limit = offset pagination
    Product.countDocuments(),                                 // total count for "Page X of Y" UI
  ]);

  res.json({
    data: items,
    meta: { page, limit, total, totalPages: Math.ceil(total / limit) },
  });
});

// --- CURSOR PAGINATION ---
app.get('/products/cursor', async (req, res) => {
  const limit = Number(req.query.limit) || 20;
  const after = req.query.after; // the last seen item's _id from the previous response

  const filter = after ? { _id: { $gt: after } } : {}; // only fetch items AFTER the cursor
  const items = await Product.find(filter).sort({ _id: 1 }).limit(limit); // indexed lookup, no skip

  const nextCursor = items.length === limit ? items[items.length - 1]._id : null; // null = no more pages

  res.json({ data: items, meta: { nextCursor } });
});

app.listen(3000);
```

## 💻 Code Example — Advanced

```javascript
// advanced-pagination.js — base64-encoded opaque cursors, stable multi-field sort

const express = require('express');
const app = express();
const Order = require('./models/Order');

// Encode a cursor object into an opaque base64 string -- hides internal field names from clients
function encodeCursor(obj) {
  return Buffer.from(JSON.stringify(obj)).toString('base64url');
}
function decodeCursor(str) {
  return JSON.parse(Buffer.from(str, 'base64url').toString('utf8'));
}

// Cursor pagination with a compound sort key (createdAt + _id as tiebreaker)
// Tiebreaker is essential: createdAt alone can have duplicate timestamps across rows
app.get('/orders', async (req, res, next) => {
  try {
    const limit = Math.min(Number(req.query.limit) || 20, 100); // cap limit to prevent abuse
    const cursorParam = req.query.cursor;

    let filter = {};
    if (cursorParam) {
      const { createdAt, id } = decodeCursor(cursorParam);
      // Compound condition: items strictly after the cursor's (createdAt, id) pair
      filter = {
        $or: [
          { createdAt: { $gt: createdAt } },
          { createdAt: createdAt, _id: { $gt: id } },
        ],
      };
    }

    const items = await Order.find(filter)
      .sort({ createdAt: 1, _id: 1 }) // MUST match the compound cursor logic exactly
      .limit(limit + 1); // fetch one extra to detect if there's a next page

    const hasMore = items.length > limit;
    const page = hasMore ? items.slice(0, limit) : items;

    const nextCursor = hasMore
      ? encodeCursor({ createdAt: page[page.length - 1].createdAt, id: page[page.length - 1]._id })
      : null;

    res.json({ data: page, meta: { nextCursor, hasMore } });
  } catch (err) {
    next(err);
  }
});

module.exports = app;
```

---

## 🟠 Express.js Integration

```javascript
// Hybrid: expose offset pagination for admin dashboards (need page numbers),
// cursor pagination for the public/mobile feed API (infinite scroll)
const express = require('express');
const router = express.Router();

router.get('/admin/orders', async (req, res) => {
  // admin UI wants "Page 5 of 42" style navigation -> offset works well here
  const { page = 1, limit = 50 } = req.query;
  const orders = await Order.find().skip((page - 1) * limit).limit(Number(limit));
  res.json({ data: orders });
});

router.get('/feed/orders', async (req, res) => {
  // mobile infinite-scroll feed -> cursor avoids duplicate/skipped items as new orders arrive
  const { cursor, limit = 20 } = req.query;
  const filter = cursor ? { _id: { $gt: cursor } } : {};
  const orders = await Order.find(filter).sort({ _id: 1 }).limit(Number(limit));
  res.json({ data: orders, nextCursor: orders.at(-1)?._id || null });
});

module.exports = router;
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using offset pagination for a frequently-changing, infinitely-scrolled feed
✅ Correct: Use cursor pagination for feeds where items are constantly inserted — offset will cause duplicates/skips.

```javascript
// Wrong -- offset on a live feed causes skipped/duplicate posts as new ones are inserted
app.get('/feed', (req, res) => { /* skip/limit based */ });

// Right -- cursor anchored to a stable, unique, sortable field
app.get('/feed', (req, res) => { /* WHERE id > cursor */ });
```

❌ Mistake 2: Using a non-unique field alone as the cursor (e.g., just `createdAt`)
✅ Correct: Always add a unique tiebreaker field (like `_id`) to the sort/cursor, since multiple rows can share the same timestamp, causing items to be skipped or duplicated.

```javascript
// Wrong
.sort({ createdAt: 1 }) // ties on same timestamp are unordered/unstable

// Right
.sort({ createdAt: 1, _id: 1 }) // _id breaks ties deterministically
```

---

## 🧠 Tricky Interview Question

```javascript
// A user is on "page 2" (offset pagination, 20 items/page) of a product list sorted by newest first.
// While they're viewing page 2, 5 NEW products get inserted at the top of the list.
// What happens when they click "page 3"?
```
Answer: They will see **5 duplicate items** that they already saw on page 2 (or, depending on direction, skip 5 items they haven't seen yet) — because "page 3" is defined as "rows 41-60 right now," but 5 new rows shifted everything down by 5 positions since page 2 was loaded. This is the classic offset pagination instability problem. Cursor pagination avoids this entirely because "give me items after ID X" remains correct regardless of how many new items get inserted elsewhere in the list.

---

## ⚫ Interview Questions + Answers

Q1: Why is `OFFSET` slow for large page numbers in SQL databases?
A1: `OFFSET N` doesn't jump directly to row N — the database must still scan through and discard the first N rows before it can start returning results. As N grows (deep pages), this scan cost grows linearly, making later pages progressively slower, even though the final result set size (LIMIT) stays constant.

Q2: Can you jump to an arbitrary page (e.g., "go to page 50") with cursor pagination?
A2: Not directly — cursor pagination only supports "next" (and optionally "previous" with a reversed cursor), not arbitrary random access, because it's based on sequentially walking from a known anchor point. If arbitrary page-jumping is a hard UX requirement, offset pagination (or a hybrid/precomputed index) is necessary.

Q3: What makes a good cursor field?
A3: It must be **unique** (no duplicates, so no items get skipped/repeated) and **sortable in a stable, monotonic order** matching the query's `ORDER BY` (e.g., auto-increment ID, MongoDB ObjectId [which is time-ordered], or a composite of timestamp + unique ID as tiebreaker). It should also ideally be indexed for fast range queries (`WHERE id > cursor`).

Q4: How do "opaque" cursors (base64-encoded) improve API design over exposing raw IDs?
A4: Opaque cursors hide implementation details (which fields are used for sorting/pagination) from the client, so the backend can change its internal pagination logic (e.g., switch sort fields, add a tiebreaker) without breaking the API contract — clients just pass back whatever cursor string they were given, without parsing or depending on its internal structure.

Q5: How would you implement "previous page" with cursor pagination?
A5: Maintain both a `before` and `after` cursor parameter. For "previous," reverse the sort order, query items before the cursor, limit, then reverse the result back to the original display order. Alternatively, store cursors for each page visited client-side (in app state) so "previous" just re-uses a cached cursor rather than needing true backward cursor queries.

---

## 🔷 When to Use + When Not to Use
✅ Use Offset when:
- Admin dashboards / UIs that need "Page X of Y" navigation and jump-to-page functionality.
- Dataset is relatively small/static (pagination depth rarely goes very deep).

✅ Use Cursor when:
- Infinite scroll feeds, real-time/frequently-changing datasets (social feeds, chat, live orders).
- Performance matters on very large datasets (millions of rows, deep pagination).

❌ Avoid Offset when:
- Data changes frequently between page loads, or dataset/page depth is huge (performance cliff).

❌ Avoid Cursor when:
- Users need to jump to an arbitrary page number directly.

---

## 📊 Visual Diagram
```
OFFSET PAGINATION:                      CURSOR PAGINATION:
──────────────────────                  ──────────────────────
page=1 → OFFSET 0  LIMIT 20             limit=20 (no cursor) → items 1-20, nextCursor=id20
page=2 → OFFSET 20 LIMIT 20             after=id20 → WHERE id > id20 LIMIT 20 → items 21-40
page=3 → OFFSET 40 LIMIT 20             after=id40 → WHERE id > id40 LIMIT 20 → items 41-60
  ↑ DB scans+discards 40 rows first       ↑ DB jumps straight to id > X using an index
  ↑ unstable if rows inserted/removed     ↑ stable regardless of inserts elsewhere
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Offset pagination | Skip N, take M | N skip करके M लेना |
| Cursor pagination | Pointer to last item | Last item का pointer |
| Opaque cursor | Encoded cursor hiding internals | Internal details hide करने वाला cursor |
| Tiebreaker field | Unique field to break sort ties | Sort ties तोड़ने वाला unique field |
| Infinite scroll | Continuously loading feed | लगातार load होने वाला feed |

---

## ⚡ 3-Line Summary
English:
1. Offset pagination (`skip`/`limit`) is simple and supports page-number navigation but degrades on deep pages and shifts when data changes.
2. Cursor pagination (`WHERE id > lastSeenId`) stays fast and stable for large/frequently-changing datasets but can't jump to arbitrary pages.
3. Always include a unique tiebreaker field in cursor sorts, and consider opaque (encoded) cursors to hide internal sort logic from clients.

Hindi:
1. Offset pagination (`skip`/`limit`) simple है और page-number navigation support करता है पर deep pages पर slow होता है और data बदलने पर shift होता है।
2. Cursor pagination (`WHERE id > lastSeenId`) large/frequently-changing datasets पर fast और stable रहता है पर arbitrary page पर jump नहीं कर सकता।
3. Cursor sorts में हमेशा unique tiebreaker field रखो, और internal sort logic hide करने के लिए opaque (encoded) cursors consider करो।

---

## ➡️ Next Topic
**177. Filtering + Sorting + Searching** — Query params से API results को filter, sort, और search करना।
