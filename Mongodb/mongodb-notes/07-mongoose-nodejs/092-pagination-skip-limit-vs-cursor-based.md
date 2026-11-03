# 92. Pagination in MongoDB — skip/limit vs Cursor-based
# हिंदी में: MongoDB में Pagination — skip/limit बनाम Cursor-based

---

## 🔵 Simple Definition (English)
**Pagination** returns a large result set in small pages. **Offset pagination** uses `skip(n).limit(k)` ("give me page 5"). **Cursor (keyset) pagination** remembers the last item seen and asks for items "after" it using a range filter on an indexed, ordered field (`{ _id: { $lt: lastId } }`) — it never skips.

## 🔵 सरल परिभाषा (Hindi)
**Pagination** बड़े result set को छोटे pages में लौटाता है। **Offset pagination** `skip(n).limit(k)` इस्तेमाल करता है ("page 5 दो")। **Cursor (keyset) pagination** आखिरी देखा हुआ item याद रखता है और indexed, ordered field पर range filter (`{ _id: { $lt: lastId } }`) से उसके "बाद" वाले items माँगता है — यह कभी skip नहीं करता।

---

## 🔴 Problem it Solves
Returning 5 million orders in one response crashes the server and the browser. `skip/limit` fixes the size but has two hidden problems: (1) **performance** — `skip(90000)` makes MongoDB walk past 90,000 index entries (or documents) just to throw them away, so deep pages get slower linearly; (2) **correctness** — if a new order is inserted while the user moves from page 1 to 2, items shift and the user sees a duplicate or misses a row. Cursor pagination solves both: constant cost per page and a stable position.

## 🔴 यह क्यों बना? (Hindi)
50 लाख orders एक response में भेजने से server और browser दोनों crash होते हैं। `skip/limit` size ठीक करता है पर इसमें दो छुपी समस्याएँ हैं: (1) **performance** — `skip(90000)` में MongoDB को 90,000 index entries (या documents) पार करके फेंकनी पड़ती हैं, इसलिए deep pages linearly धीमे होते जाते हैं; (2) **correctness** — user के page 1 से 2 पर जाते समय नया order insert हो जाए तो items खिसक जाते हैं और user को duplicate दिखता है या row छूट जाती है। Cursor pagination दोनों हल करता है: हर page की cost constant और position stable।

---

## 🟢 How it Works — Step by Step

**Offset (skip/limit):**
Step 1 → Client sends `?page=3&limit=10`.
Step 2 → Server computes `skip = (page-1)*limit` and runs `find().sort(...).skip(20).limit(10)`.
Step 3 → MongoDB scans and discards the first 20, returns 10. Cost grows with `skip`.

**Cursor (keyset):**
Step 1 → First request: `find().sort({createdAt:-1,_id:-1}).limit(10)`.
Step 2 → Response includes `nextCursor` = last item's sort key(s) (encode as base64 string).
Step 3 → Next request sends `?cursor=...`; server filters `createdAt < last.createdAt OR (createdAt = last.createdAt AND _id < last._id)`.
Step 4 → The compound index `{createdAt:-1,_id:-1}` jumps straight to that position — cost does not depend on page depth.
Step 5 → Fetch `limit + 1` rows to know if a next page exists without a second count query.

**Golden rule:** the sort must be **deterministic** — always add `_id` as a tie-breaker.

## 🟢 कैसे काम करता है? (Hindi)
**Offset (skip/limit):**
Step 1 → Client `?page=3&limit=10` भेजता है।
Step 2 → Server `skip = (page-1)*limit` निकालकर `find().sort(...).skip(20).limit(10)` चलाता है।
Step 3 → MongoDB पहले 20 scan करके फेंकता है, 10 लौटाता है। Cost `skip` के साथ बढ़ती है।

**Cursor (keyset):**
Step 1 → पहली request: `find().sort({createdAt:-1,_id:-1}).limit(10)`।
Step 2 → Response में `nextCursor` = आखिरी item की sort key(s) (base64 string में encode)।
Step 3 → अगली request `?cursor=...` भेजती है; server filter लगाता है `createdAt < last.createdAt OR (createdAt = last.createdAt AND _id < last._id)`।
Step 4 → Compound index `{createdAt:-1,_id:-1}` सीधे उस position पर पहुँचता है — cost page की depth पर निर्भर नहीं।
Step 5 → `limit + 1` rows लाओ ताकि बिना अलग count query के पता चले कि अगला page है या नहीं।

**सुनहरा नियम:** sort **deterministic** होना चाहिए — tie-breaker के रूप में हमेशा `_id` जोड़ो।

---

## 🟡 Real World Example
**Razorpay's transactions dashboard** has merchants with 50 million payments. The "Payments" table uses cursor pagination (imagine a design like this): the UI keeps the last payment's `(created_at, id)`, so scrolling to "payments from 2 months ago" is as fast as page 1, and new payments arriving every second never cause duplicates. Back-office tools with small result sets (a few hundred refunds) can still use simple page numbers because users want "jump to page 7".

## 🟡 Real Example Hindi mein
**Razorpay के transactions dashboard** में merchants के पास 5 करोड़ payments हैं। "Payments" table cursor pagination इस्तेमाल करती है: UI आखिरी payment का `(created_at, id)` रखती है, इसलिए "2 महीने पुराने payments" तक scroll करना page 1 जितना ही तेज़ है, और हर सेकंड आ रहे नए payments से duplicates नहीं बनते। Back-office tools में छोटे result sets (कुछ सौ refunds) पर साधारण page numbers चल सकते हैं क्योंकि users को "page 7 पर जाओ" चाहिए।

---

## 💻 Code Example — Basic

Run in mongosh against MongoDB 8.0.4 with 100,000 documents (`n` = 1..100000, `createdAt` increasing):

```javascript
// Setup: 100,000 orders with an index that matches the sort
db = db.getSiblingDB('shop');
db.orders.drop();
const docs = [];
for (let i = 1; i <= 100000; i++)
  docs.push({ n: i, amount: i % 500, createdAt: new Date(1700000000000 + i * 1000) }); // 1 sec apart
db.orders.insertMany(docs);                         // bulk insert
db.orders.createIndex({ createdAt: -1, _id: -1 });  // sort key + tie-breaker

// ---- OFFSET: page 30001 with limit 3 -> skip 90000 ----
const s = db.orders.find().sort({ createdAt: -1, _id: -1 })
  .skip(90000).limit(3)
  .explain('executionStats').executionStats;        // ask MongoDB how much work it did
print('skip: returned', s.nReturned,
      'keysExamined', s.totalKeysExamined,
      'docsExamined', s.totalDocsExamined);
// Output: skip: returned 3 keysExamined 90003 docsExamined 3
//   -> 90,003 index entries walked to return 3 rows!

// ---- CURSOR: page 1 ----
const page1 = db.orders.find().sort({ createdAt: -1, _id: -1 }).limit(3).toArray();
print(page1.map(d => d.n));                         // Output: [ 100000, 99999, 99998 ]

// ---- CURSOR: page 2, using the last row of page 1 ----
const last = page1[2];                              // remember last item (the "cursor")
const q = { $or: [                                  // "strictly after" in the sort order
  { createdAt: { $lt: last.createdAt } },           // older timestamp
  { createdAt: last.createdAt, _id: { $lt: last._id } } // same timestamp, smaller _id (tie-break)
]};
const page2 = db.orders.find(q).sort({ createdAt: -1, _id: -1 }).limit(3).toArray();
print(page2.map(d => d.n));                         // Output: [ 99997, 99996, 99995 ]

// ---- CURSOR cost deep in the data (rows older than the 50,000th) ----
const c = db.orders.find({ createdAt: { $lt: new Date(1700000000000 + 50000 * 1000) } })
  .sort({ createdAt: -1, _id: -1 }).limit(3)
  .explain('executionStats').executionStats;
print('cursor: returned', c.nReturned,
      'keysExamined', c.totalKeysExamined,
      'docsExamined', c.totalDocsExamined);
// Output: cursor: returned 3 keysExamined 3 docsExamined 3   <- constant, regardless of depth
```

Verified output summary: skip examined **90,003** index keys; the cursor query examined **3**.

## 💻 Code Example — Advanced

Reusable Mongoose helper with opaque cursor and `hasNext` (limit + 1 trick):

```javascript
const { ObjectId } = require('mongoose').Types;

// Encode / decode the cursor so clients treat it as an opaque string
const encode = (d) => Buffer.from(JSON.stringify({ t: d.createdAt.getTime(), id: d._id })).toString('base64url');
const decode = (c) => { const o = JSON.parse(Buffer.from(c, 'base64url').toString()); return { t: new Date(o.t), id: new ObjectId(o.id) }; };

async function paginate(Model, filter, { limit = 20, cursor } = {}) {
  limit = Math.min(Math.max(Number(limit) || 20, 1), 100);     // clamp 1..100
  const q = { ...filter };
  if (cursor) {
    const { t, id } = decode(cursor);                          // throws on tampered cursor -> 400
    q.$or = [{ createdAt: { $lt: t } }, { createdAt: t, _id: { $lt: id } }];
  }
  const rows = await Model.find(q)
    .sort({ createdAt: -1, _id: -1 })                          // deterministic order
    .limit(limit + 1)                                          // fetch one extra
    .lean();
  const hasNext = rows.length > limit;                         // extra row => more pages exist
  if (hasNext) rows.pop();                                     // drop the extra row
  return { items: rows, nextCursor: hasNext ? encode(rows[rows.length - 1]) : null };
}
```

Offset pagination done right when you must have page numbers:

```javascript
// total count is expensive on huge collections — cache it, or return "10,000+" instead
const [items, total] = await Promise.all([
  Order.find({ merchantId }).sort({ _id: -1 }).skip((page - 1) * limit).limit(limit).lean(),
  Order.countDocuments({ merchantId }),            // countDocuments honours the filter (accurate)
]);
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
app.get('/orders', async (req, res, next) => {
  try {
    const { limit, cursor } = req.query;                  // ?limit=20&cursor=eyJ0Ijo...
    const result = await paginate(Order, { merchantId: req.user.merchantId }, { limit, cursor });
    res.json(result);                                     // { items: [...], nextCursor: "..." | null }
  } catch (e) {
    if (e instanceof SyntaxError) return res.status(400).json({ error: 'Bad cursor' });
    next(e);
  }
});
// Index to support it (filter field first, then sort fields — ESR rule):
// Order.schema.index({ merchantId: 1, createdAt: -1, _id: -1 });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Sorting by a non-unique field only
```javascript
// Wrong — many rows share the same createdAt; pages overlap or skip rows
find().sort({ createdAt: -1 }).skip(20).limit(10)

// Right — add a unique tie-breaker
find().sort({ createdAt: -1, _id: -1 }).skip(20).limit(10)
```

❌ Mistake 2: `skip/limit` without an index for the sort
✅ Correct: Without a matching index MongoDB performs an in-memory sort of all matching documents (limit of 100 MB for blocking sorts, error beyond it unless `allowDiskUse`). Always index the sort fields.

❌ Mistake 3: Cursor on a non-indexed or mutable field
✅ Correct: If the sort key changes (e.g. `updatedAt`), an item can jump between pages. Use immutable fields such as `createdAt`/`_id`.

❌ Mistake 4: Running `count()` on every page request
✅ Correct: `countDocuments` scans matching docs; on millions of rows it's slow. Cache it, or skip totals and show "Next".

❌ Mistake 5: Cursor with only `_id` when the sort is by another field
✅ Correct: The cursor must contain every field in the sort, in the same direction.

---

## 🧠 Tricky Interview Question

Q: Why can the cursor filter `{ createdAt: { $lte: last.createdAt }, _id: { $lt: last._id } }` return wrong pages?

Answer: It requires BOTH conditions. A row with an *older* `createdAt` but a *larger* `_id` fails the `_id` test and is silently dropped. The `_id` comparison must apply only when `createdAt` is equal, hence the `$or`: `createdAt < t` OR (`createdAt == t` AND `_id < id`). Since a single sort key (`_id`) is monotonic in ObjectId generation time, many apps simply sort on `_id` alone and use `{_id: {$lt: last}}`, which is simpler but ties the order to insertion time, not to a business timestamp.

---

## ⚫ Interview Questions + Answers

Q1: Why does `skip(100000)` get slow?
A1: MongoDB cannot jump to an offset; it must traverse and discard 100,000 index entries (we measured 90,003 keys examined to return 3 rows). Cost is O(skip + limit).

Q2: What are the downsides of cursor pagination?
A2: No "jump to page N", no total page count, and the cursor must be tied to a fixed sort. Going backwards needs a reversed query. Good for infinite scroll and APIs/exports, not for numbered pagination UIs.

Q3: How do you paginate backwards?
A3: Reverse the comparison and sort (`$gt` + ascending), fetch `limit` rows, then reverse the array in application code.

Q4: What index supports `find({merchantId}).sort({createdAt:-1,_id:-1})`?
A4: `{ merchantId: 1, createdAt: -1, _id: -1 }` — equality field first, then sort fields (ESR rule). This allows a bounded index scan with no in-memory sort.

Q5: Is data consistent across pages?
A5: Cursor pagination is stable for inserts at the "top" (new items do not shift later pages). Neither technique gives a snapshot across requests — for that you need a snapshot read concern in a transaction or a fixed upper bound (`createdAt <= firstRequestTime`) carried in the cursor.

---

## 🔷 When to Use + When Not to Use
✅ Use cursor pagination when:
- Infinite scroll feeds, large exports, log/transaction streams, public APIs
- Collections with millions of documents or frequent inserts

✅ Use skip/limit when:
- Small collections (admin tables, a few thousand rows) and users need "go to page 7"

❌ Avoid skip/limit when:
- `skip` can exceed ~10,000, or data changes rapidly during browsing

---

## 📊 Visual Diagram
```
 OFFSET: skip(6).limit(3)                 CURSOR: after last=(t5,id5)
 ──────────────────────────               ───────────────────────────
 idx: 1 2 3 4 5 6 | 7 8 9 | 10            idx: 1 2 3 4 5 | 6 7 8 | 9 10
      └─ walk & discard ─┘└return┘                     seek here ─┘└return┘
 cost = skip + limit (grows)              cost = limit (constant)

 Insert at top while paging (offset):     Insert at top while paging (cursor):
 page1 [A B C] → new X inserted           page1 [A B C] → new X inserted
 page2 [C D E]  ← C repeated!             page2 [D E F]  ← correct
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Offset pagination | `skip`/`limit` by page number | Page number से skip/limit |
| Keyset / cursor pagination | Seek after last seen key | आखिरी key के बाद से seek |
| Tie-breaker | Unique field making sort deterministic | Sort को पक्का करने वाला unique field |
| `explain()` | Shows query execution stats | Query execution stats दिखाता है |
| `keysExamined` | Index entries scanned | Scan हुई index entries |
| Opaque cursor | Encoded token clients don't parse | Encoded token जिसे client नहीं समझता |
| ESR rule | Equality, Sort, Range index order | Index field order का नियम |

---

## ⚡ 3-Line Summary
English:
1. `skip/limit` is simple but scans all skipped entries (90,003 keys for 3 rows in our test) and shifts when data changes.
2. Cursor pagination filters "after the last seen (sortKey, _id)" using a matching compound index, so each page costs only `limit`.
3. Always sort deterministically with `_id` as a tie-breaker, fetch `limit+1` for `hasNext`, and index the sort fields.

Hindi:
1. `skip/limit` आसान है पर skip हुई सारी entries scan करता है (हमारे test में 3 rows के लिए 90,003 keys) और data बदलने पर खिसक जाता है।
2. Cursor pagination matching compound index से "आखिरी देखे (sortKey, _id) के बाद" filter करता है, इसलिए हर page की cost सिर्फ `limit` है।
3. हमेशा `_id` को tie-breaker बनाकर deterministic sort करो, `hasNext` के लिए `limit+1` लाओ, और sort fields पर index बनाओ।

---

## ➡️ Next Topic
**93. ACID in MongoDB + Multi-Document Transactions** — When single-document atomicity is not enough and how to run all-or-nothing updates across documents.
