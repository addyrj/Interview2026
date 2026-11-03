# 16. Sorting, limit, skip
# हिंदी में: Sorting, limit और skip

---

## 🔵 Simple Definition (English)
`sort()` orders results (`1` ascending, `-1` descending), `limit(n)` caps how many documents are returned, and `skip(n)` jumps over the first n documents. MongoDB applies them in a fixed logical order regardless of how you chain them: **sort, then skip, then limit**.

## 🔵 सरल परिभाषा (Hindi)
`sort()` results को order करता है (`1` ascending, `-1` descending), `limit(n)` तय करता है कि कितने documents लौटें, और `skip(n)` शुरू के n documents छोड़ देता है। आप जैसे भी chain करें, MongoDB logical order में लागू करता है: **पहले sort, फिर skip, फिर limit**।

---

## 🔴 Problem it Solves
Without ordering, `find()` returns documents in unspecified order, so UIs show random lists. Without limit, a query can pull millions of documents into memory. Sort + skip + limit give paginated, deterministic result pages (leaderboards, "latest 10 orders", product listings).

## 🔴 यह क्यों बना? (Hindi)
Ordering के बिना `find()` unspecified order में documents देता है, इसलिए UI में list random दिखती है। Limit के बिना query लाखों documents memory में खींच सकती है। Sort + skip + limit deterministic, paginated pages देते हैं (leaderboards, "latest 10 orders", product listings)।

---

## 🟢 How it Works — Step by Step

Step 1 → Server finds documents matching the filter.
Step 2 → `sort({field: 1|-1})` orders them. Multiple keys sort left to right; ties are broken by the next key.
Step 3 → `skip(n)` discards the first n sorted docs.
Step 4 → `limit(n)` keeps the next n. (Chain order in code does not change this.)
Step 5 → If an index matches the sort keys, no in-memory sort is needed; otherwise a blocking SORT stage is used (limited to 100 MB unless `allowDiskUse`).
Step 6 → Add a unique tiebreaker (usually `_id`) to make pagination stable.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server filter से match होने वाले documents ढूँढता है।
Step 2 → `sort({field: 1|-1})` उन्हें order करता है। कई keys हों तो बाएँ से दाएँ sort होती है; tie पर अगली key।
Step 3 → `skip(n)` sorted के पहले n docs छोड़ देता है।
Step 4 → `limit(n)` अगले n रखता है। (Code में chain order से फ़र्क नहीं पड़ता।)
Step 5 → Sort keys पर index हो तो in-memory sort नहीं लगता; वरना blocking SORT stage चलता है (100 MB limit, जब तक `allowDiskUse` न हो)।
Step 6 → Pagination stable रखने के लिए unique tiebreaker (आमतौर पर `_id`) जोड़ो।

---

## 🟡 Real World Example
Flipkart's "price: low to high" listing page 3 (20 items per page) is `find({category:"phones"}).sort({price:1,_id:1}).skip(40).limit(20)`. The `_id` tiebreaker prevents the same phone appearing on two pages when many have the same price. For deep pages, they switch to range-based paging (`price > lastSeen`) because large `skip` still scans and discards documents.

## 🟡 Real Example Hindi mein
Flipkart के "price: low to high" listing का page 3 (20 items प्रति page) है `find({category:"phones"}).sort({price:1,_id:1}).skip(40).limit(20)`। `_id` tiebreaker यह रोकता है कि कई phones की कीमत समान होने पर एक ही phone दो pages पर दिखे। गहरे pages के लिए वे range-based paging (`price > lastSeen`) पर जाते हैं क्योंकि बड़ा `skip` भी documents scan करके फेंकता है।

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh"
db.m.insertMany([
  { n: "c", p: 30 }, { n: "a", p: 10 }, { n: "b", p: 20 },
  { n: "d", p: 10 }, { n: "e", p: 50 }
])

// price ascending, then name DESCENDING for ties; skip first 1; return 3
db.m.find({}, { _id: 0 }).sort({ p: 1, n: -1 }).skip(1).limit(3)
// Sorted full list: d(10), a(10), b(20), c(30), e(50)
// After skip(1) -> drops d. limit(3) keeps:
// Output: [ { n: 'a', p: 10 }, { n: 'b', p: 20 }, { n: 'c', p: 30 } ]
```

## 💻 Code Example — Advanced

```javascript
// Top-3 most expensive (descending + limit)
db.m.find({}, { _id: 0 }).sort({ p: -1 }).limit(3)
// Output: [ { n: 'e', p: 50 }, { n: 'c', p: 30 }, { n: 'b', p: 20 } ]

// Page helper: page numbers start at 1
function page(coll, pageNo, size) {
  return coll.find({}, { _id: 0 })
             .sort({ p: 1, _id: 1 })        // _id tiebreaker -> stable pages
             .skip((pageNo - 1) * size)     // jump past previous pages
             .limit(size)                   // page size
             .toArray()
}
page(db.m, 2, 2)                            // 2nd page of size 2 (tie order by _id = insertion order)

// Range-based ("keyset") pagination - no big skip
const last = { p: 20, _id: db.m.findOne({ n: "b" })._id }  // last item of the previous page
db.m.find({ $or: [{ p: { $gt: last.p } }, { p: last.p, _id: { $gt: last._id } }] })
    .sort({ p: 1, _id: 1 }).limit(2)       // next 2 docs after "b"

// Index to support the sort (avoids in-memory sort)
db.m.createIndex({ p: 1, _id: 1 })
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /products?page=2&size=20&sort=price
app.get('/products', async (req, res) => {
  const page = Math.max(parseInt(req.query.page) || 1, 1);          // default page 1
  const size = Math.min(parseInt(req.query.size) || 20, 100);       // cap size to protect DB
  const items = await Product.find({})                              // Mongoose model
    .sort({ price: 1, _id: 1 })                                     // stable order
    .skip((page - 1) * size)
    .limit(size)
    .lean();                                                        // plain objects, faster
  res.json({ page, size, items });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Paginating without a unique sort key
```javascript
db.m.find().sort({ p: 1 }).skip(2).limit(2)         // Wrong: equal p values can shuffle between pages
db.m.find().sort({ p: 1, _id: 1 }).skip(2).limit(2) // Right
```

❌ Mistake 2: Huge `skip` values
✅ Correct: `skip(100000)` still walks 100000 entries; use keyset pagination.

❌ Mistake 3: Using `skip`/`limit` with no sort
✅ Correct: Without sort the order is not guaranteed; always sort when paging.

---

## 🧠 Tricky Interview Question
```javascript
db.m.find().limit(2).skip(1).sort({ p: -1 })
```
Answer: Chain order is irrelevant: it runs sort (p desc: e,c,b,a/d...), then skip(1), then limit(2) -> the 2nd and 3rd highest, `c(30)` and `b(20)`. Programming-order intuition ("limit first") is wrong.

---

## ⚫ Interview Questions + Answers

Q1: What does `sort({a:1})` do with missing fields?
A1: Documents without the field sort as `null` — before real values in ascending order.

Q2: Is sort stable?
A2: Not guaranteed for ties; add `_id` as a last key.

Q3: Memory limit for sort?
A3: 100 MB for in-memory blocking sort; beyond that error, unless `allowDiskUse: true` (or use an index).

Q4: Why is skip slow for deep pages?
A4: The server still scans and discards all skipped docs; cost is O(skip).

Q5: How does an index help sort?
A5: If index key order matches sort order (or its exact reverse), documents come pre-ordered, no SORT stage.

---

## 🔷 When to Use + When Not to Use
✅ Use sort/limit/skip when:
- Small to moderate pagination, top-N queries

❌ Avoid large skip when:
- Infinite scroll or deep pages: use keyset pagination

---

## 📊 Visual Diagram
```
 matched docs ──► SORT ──► SKIP n ──► LIMIT m ──► result
 (filter)        (index?)  (discard)   (keep)

 sorted: d a | b c e      skip(2)? -> drops d,a
                 └─ limit(2) -> b, c
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| sort | Order results | Results का क्रम |
| limit | Cap result count | Result संख्या सीमित |
| skip | Skip first n | पहले n छोड़ना |
| Keyset pagination | Range-based paging | Range आधारित paging |
| Tiebreaker | Unique extra sort key | Tie तोड़ने वाली extra key |

---

## ⚡ 3-Line Summary
English:
1. Execution order is always sort, skip, limit.
2. Add `_id` as tiebreaker for stable pages; index the sort keys.
3. Prefer keyset pagination over large skips.

Hindi:
1. Execution order हमेशा sort, skip, limit है।
2. Stable pages के लिए `_id` tiebreaker जोड़ो; sort keys पर index बनाओ।
3. बड़े skip की जगह keyset pagination चुनो।

---

## ➡️ Next Topic
**17. countDocuments vs estimatedDocumentCount**
