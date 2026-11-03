# 119. Paginated Search API with Filters
# हिंदी में: Filters के साथ Paginated Search API

---

## 🔵 Simple Definition (English)
A **paginated search API** returns a filtered, sorted slice of a large collection (`GET /products?brand=Apple&minPrice=3000&sort=price&page=2`). The interview problem is to build it safely and fast: whitelist filters, choose **offset (skip/limit)** vs **keyset (cursor)** pagination, design a compound index following **ESR (Equality, Sort, Range)**, and return the **total count** without a second slow scan.

## 🔵 सरल परिभाषा (Hindi)
**Paginated search API** बड़े collection का filter और sort किया हुआ एक टुकड़ा लौटाती है (`GET /products?brand=Apple&minPrice=3000&sort=price&page=2`)। Interview में इसे सुरक्षित और तेज़ बनाना होता है: filters की whitelist, **offset (skip/limit)** बनाम **keyset (cursor)** pagination का चुनाव, **ESR (Equality, Sort, Range)** नियम से compound index, और दूसरे धीमे scan के बिना **total count** लौटाना।

---

## 🔴 Problem it Solves
Listing pages (products, orders, restaurants) must handle millions of documents. Problems: (1) returning everything crashes the client; (2) `skip(100000)` makes deep pages slower because the server still walks 100000 entries; (3) filters taken blindly from `req.query` allow NoSQL injection (`?price[$gt]=0`) or accidental regex DoS; (4) sorting on a field without an index forces an in-memory sort that fails beyond 100 MB; (5) `skip` pagination returns duplicates or misses rows when documents are inserted between page loads.

## 🔴 यह क्यों बना? (Hindi)
Listing pages (products, orders, restaurants) में लाखों documents संभालने पड़ते हैं। समस्याएँ: (1) सब कुछ लौटाने पर client crash हो जाता है; (2) `skip(100000)` से गहरे pages धीमे हो जाते हैं क्योंकि server फिर भी 100000 entries पार करता है; (3) `req.query` से आँख मूँदकर लिए filters NoSQL injection (`?price[$gt]=0`) या regex DoS की जगह बनाते हैं; (4) बिना index वाले field पर sort memory में होता है जो 100 MB के बाद fail हो जाता है; (5) page loads के बीच नए documents आने पर `skip` pagination में duplicates या छूटे rows आते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Whitelist & validate filters**: accept only known keys (`brand`, `minPrice`, `maxPrice`), cast to numbers/strings, reject objects (so `{ $gt: ... }` cannot be injected). Cap `limit` (e.g. max 50).
Step 2 → **Build the query object**: `{ brand, price: { $gte, $lte } }`.
Step 3 → **Pick the index by ESR**: Equality fields first (`brand`), then Sort field (`price`), then Range fields. Add `_id` as the final tie-breaker: `{ brand: 1, price: 1, _id: 1 }`.
Step 4 → **Offset pagination**: `.sort({ price: 1, _id: 1 }).skip((page - 1) * limit).limit(limit)`. Simple, supports "jump to page 7", but cost grows with page depth.
Step 5 → **Keyset pagination**: send the last row's `(price, _id)` as a cursor and query `price > last.price OR (price = last.price AND _id > last._id)`. Constant cost per page, stable under inserts, but only "next/prev", no jump-to-page.
Step 6 → **Total count**: `countDocuments(filter)` (accurate, uses the index), or a single aggregation with `$facet: { data: [...], total: [{ $count: "n" }] }`. For huge collections show "10,000+" using `limit(10001)` before counting, or cache.
Step 7 → **Verify with explain**: `executionStats` should show `IXSCAN`, `totalKeysExamined ≈ nReturned`, and no `SORT` stage.
Step 8 → **Always return a stable sort** (add `_id`), otherwise rows with equal `price` may shuffle between pages.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Filters whitelist और validate करो**: सिर्फ जाने-पहचाने keys (`brand`, `minPrice`, `maxPrice`) लो, numbers/strings में cast करो, objects reject करो (ताकि `{ $gt: ... }` inject न हो)। `limit` की upper limit रखो (जैसे 50)।
Step 2 → **Query object बनाओ**: `{ brand, price: { $gte, $lte } }`।
Step 3 → **ESR से index चुनो**: पहले Equality fields (`brand`), फिर Sort field (`price`), फिर Range fields। अंत में tie-breaker के रूप में `_id`: `{ brand: 1, price: 1, _id: 1 }`।
Step 4 → **Offset pagination**: `.sort({ price: 1, _id: 1 }).skip((page - 1) * limit).limit(limit)`। सरल, "page 7 पर जाओ" support करता है, पर page जितना गहरा उतना महँगा।
Step 5 → **Keyset pagination**: आख़िरी row का `(price, _id)` cursor भेजो और query करो `price > last.price OR (price = last.price AND _id > last._id)`। हर page का खर्च constant, inserts के बीच स्थिर, पर सिर्फ "next/prev", page पर कूदना नहीं।
Step 6 → **Total count**: `countDocuments(filter)` (सटीक, index इस्तेमाल करता है), या एक aggregation में `$facet: { data: [...], total: [{ $count: "n" }] }`। बहुत बड़े collections में `limit(10001)` से "10,000+" दिखाओ, या cache करो।
Step 7 → **explain से जाँचो**: `executionStats` में `IXSCAN`, `totalKeysExamined ≈ nReturned`, और कोई `SORT` stage नहीं दिखना चाहिए।
Step 8 → **Stable sort हमेशा**: `_id` जोड़ो, वरना बराबर `price` वाले rows pages के बीच इधर-उधर हो सकते हैं।

---

## 🟡 Real World Example
**Flipkart's mobile listing**: filters brand = Apple, price between 3,000 and 15,000, sorted by price. The first page uses `limit(20)`; "Load more" sends the last `(price, _id)` as a cursor. A `$facet` pipeline returns the first page and the count ("7 results") in one call. The same endpoint on **Swiggy** filters restaurants by cuisine and rating, sorted by distance; they cap `limit` at 50 so scrapers cannot pull whole catalogs.

## 🟡 Real Example Hindi mein
**Flipkart की mobile listing**: filters brand = Apple, price 3,000 से 15,000, price से sorted। पहला page `limit(20)` लेता है; "Load more" आख़िरी `(price, _id)` को cursor बनाकर भेजता है। `$facet` pipeline एक call में पहला page और count ("7 results") देती है। **Swiggy** पर यही endpoint cuisine और rating से restaurants filter करता है और distance से sort करता है; वे `limit` को 50 पर cap करते हैं ताकि scrapers पूरा catalog न खींच सकें।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("search");
// 20 phones: odd _id = Apple, even = Samsung, price = _id * 1000
for (let i = 1; i <= 20; i++)
  db.items.insertOne({ _id: i, title: "Phone " + i, brand: i % 2 ? "Apple" : "Samsung", price: i * 1000, rating: 3 + (i % 3) });

// ESR index: Equality (brand), Sort (price), tie-breaker (_id)
db.items.createIndex({ brand: 1, price: 1, _id: 1 });

const filter = { brand: "Apple", price: { $gte: 3000, $lte: 15000 } };

// OFFSET pagination: page 2 with limit 3 => skip 2 (shown here as skip(2) to keep the demo short)
db.items.find(filter, { title: 1, price: 1 }).sort({ price: 1, _id: 1 }).skip(2).limit(3).toArray();
// Output: [ {_id:7,title:'Phone 7',price:7000}, {_id:9,...9000}, {_id:11,...11000} ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — keyset (cursor) pagination, $facet totals and explain. Tested on 8.0.4
use("search");
const filter = { brand: "Apple", price: { $gte: 3000, $lte: 15000 } };

// A) KEYSET page 1: no cursor yet
const page = db.items.find(filter, { title: 1, price: 1 })
  .sort({ price: 1, _id: 1 }).limit(3).toArray();
page.map(x => x._id);                              // Output: [ 3, 5, 7 ]
const last = page[page.length - 1];                // cursor = last row's (price, _id)

// B) KEYSET page 2: rows strictly AFTER the cursor in (price, _id) order
const next = db.items.find({
  $and: [
    filter,
    { $or: [ { price: { $gt: last.price } },                       // later price
             { price: last.price, _id: { $gt: last._id } } ] }     // same price, later _id
  ]
}, { title: 1, price: 1 }).sort({ price: 1, _id: 1 }).limit(3).toArray();
next.map(x => x._id);                              // Output: [ 9, 11, 13 ]

// C) One round trip: first page + total count using $facet
db.items.aggregate([
  { $match: filter },
  { $facet: {
      data:  [ { $sort: { price: 1, _id: 1 } }, { $limit: 2 }, { $project: { title: 1 } } ],
      total: [ { $count: "n" } ]
  } }
]);
// Output: [ { data: [ {_id:3,title:'Phone 3'}, {_id:5,title:'Phone 5'} ], total: [ { n: 7 } ] } ]

// D) Prove the index does the work: examined == returned (no sort stage, no scan)
const s = db.items.find(filter).sort({ price: 1, _id: 1 }).limit(3)
  .explain("executionStats").executionStats;
[s.nReturned, s.totalKeysExamined, s.totalDocsExamined];   // Output: [ 3, 3, 3 ]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();

const itemSchema = new mongoose.Schema({
  title: String, brand: String, price: Number, rating: Number,
});
itemSchema.index({ brand: 1, price: 1, _id: 1 }); // declare indexes BEFORE compiling the model
const Item = mongoose.model('Item', itemSchema);

// GET /items?brand=Apple&minPrice=3000&maxPrice=15000&limit=20&cursor=<base64>
app.get('/items', async (req, res) => {
  // 1) whitelist + cast; typeof check blocks ?brand[$ne]=x object injection
  const { brand, minPrice, maxPrice, cursor } = req.query;
  const limit = Math.min(Math.max(parseInt(req.query.limit) || 20, 1), 50);
  const filter = {};
  if (typeof brand === 'string') filter.brand = brand;
  const price = {};
  if (minPrice !== undefined && !isNaN(+minPrice)) price.$gte = +minPrice;
  if (maxPrice !== undefined && !isNaN(+maxPrice)) price.$lte = +maxPrice;
  if (Object.keys(price).length) filter.price = price;

  // 2) decode the opaque cursor (price + id) if given
  let query = filter;
  if (typeof cursor === 'string') {
    const c = JSON.parse(Buffer.from(cursor, 'base64').toString());
    query = { $and: [filter, { $or: [
      { price: { $gt: c.price } },
      { price: c.price, _id: { $gt: new mongoose.Types.ObjectId(c.id) } },
    ] }] };
  }

  // 3) fetch limit+1 to know whether another page exists, without a count query
  const rows = await Item.find(query).sort({ price: 1, _id: 1 }).limit(limit + 1).lean();
  const hasMore = rows.length > limit;
  if (hasMore) rows.pop();
  const lastRow = rows[rows.length - 1];
  const nextCursor = hasMore
    ? Buffer.from(JSON.stringify({ price: lastRow.price, id: lastRow._id })).toString('base64')
    : null;
  res.json({ items: rows, nextCursor });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing `req.query` straight into `find`
```javascript
// Wrong — ?price[$gt]=0 or ?brand[$ne]=x injects operators
Item.find(req.query);

// Right — whitelist keys, check typeof, cast numbers
if (typeof req.query.brand === 'string') filter.brand = req.query.brand;
```

❌ Mistake 2: Sorting on a non-unique field only
✅ Correct: Use `sort({ price: 1, _id: 1 })`. Equal prices otherwise appear in any order, so rows repeat or vanish between pages.

❌ Mistake 3: Deep `skip()` for infinite scroll
✅ Correct: Switch to keyset pagination. `skip(100000)` examines 100000 index entries every time.

❌ Mistake 4: Index fields in the wrong order (`{ price: 1, brand: 1 }` for equality-on-brand + sort-by-price)
✅ Correct: ESR — equality first, then sort, then range. Verify with `explain()` that there is no `SORT` stage.

---

## 🧠 Tricky Interview Question

```javascript
// Index: { brand: 1, price: 1 }. Query:
db.items.find({ brand: "Apple", price: { $gte: 3000 } }).sort({ rating: -1 }).limit(10)
// Is the index good for this query?
```
Answer: Only partly. The filter on `brand` + `price` can use the index, but the **sort field `rating` is not in the index**, so MongoDB must fetch every matching document and sort in memory (a blocking `SORT` stage, 100 MB limit). Better index by ESR: `{ brand: 1, rating: -1, price: 1 }` — equality (`brand`), sort (`rating`), range (`price`). With it MongoDB walks the index in rating order and applies the price range on index keys, stopping after 10 matches.

---

## ⚫ Interview Questions + Answers

Q1: Offset vs keyset pagination?
A1: Offset (`skip/limit`) is simple and supports random page jumps, but cost is O(skip) and results shift when data changes. Keyset (cursor with `$gt` on the sort key) is O(limit), stable and index-friendly, but only supports next/previous and needs a unique tie-breaker.

Q2: How do you return the total count efficiently?
A2: `countDocuments(filter)` uses the index but still counts every match; for huge sets use `$facet` for one trip, an approximate number (`estimatedDocumentCount` for the whole collection), a capped count (`limit(10001)` then count), or cache it. Often UIs only need "hasMore", obtained by fetching `limit + 1`.

Q3: What is the ESR rule?
A3: When designing a compound index: **E**quality fields first, then **S**ort fields, then **R**ange fields. It lets the index satisfy filter and sort without an in-memory sort and with tight scan bounds.

Q4: How do you prevent NoSQL injection in search APIs?
A4: Whitelist allowed fields, check `typeof` (reject objects/arrays), cast to expected types (Mongoose schema casting, Zod/Joi), strip `$`-prefixed keys (e.g. `express-mongo-sanitize`), cap `limit`, and avoid user-supplied `$where`/regex without escaping.

Q5: How do you check that a paginated query is efficient?
A5: `explain("executionStats")`: stage `IXSCAN` (not `COLLSCAN`), no `SORT`, `totalKeysExamined` and `totalDocsExamined` close to `nReturned`.

---

## 🔷 When to Use + When Not to Use
✅ Use keyset when:
- Infinite scroll / feeds / large datasets with a fixed sort order
- Results must be stable while data changes

✅ Use offset when:
- Small datasets or admin tables needing "go to page N" and total pages

❌ Avoid when:
- Free-text relevance ranking is the main need: use `$text` or Atlas Search instead
- Many arbitrary filter combinations on huge data: dedicated search engine (Elasticsearch/Atlas Search) fits better

---

## 📊 Visual Diagram
```
PAGINATED SEARCH
──────────────────────────────────────────────────────
 GET /items?brand=Apple&minPrice=3000&cursor=…
        │ validate + whitelist + cap limit
        ▼
  filter {brand, price range} + cursor condition
        │
        ▼   index { brand:1, price:1, _id:1 }  (E, S, tie-breaker)
  ┌──────────────────────────────────────────────┐
  │ IXSCAN → ids 3,5,7 | 9,11,13 | 15 ...        │
  └──────────────────────────────────────────────┘
        │ limit+1 rows (one extra tells hasMore)
        ▼
  { items:[…], nextCursor: base64({price,id}) }

 skip(N):  walks N entries every time   → slow deep pages
 keyset :  jumps straight past cursor   → constant time
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Offset pagination | skip + limit | skip और limit वाली pagination |
| Keyset pagination | Cursor from last row's sort key | आख़िरी row की sort key से cursor |
| ESR rule | Equality, Sort, Range index order | Index field का क्रम: Equality, Sort, Range |
| $facet | Several sub-pipelines in one stage | एक stage में कई sub-pipelines |
| Tie-breaker | Unique field added to sort | Sort में जोड़ा गया unique field |
| NoSQL injection | Operators smuggled via input | Input से घुसाए गए operators |
| explain | Shows query plan and stats | Query plan और stats दिखाता है |

---

## ⚡ 3-Line Summary
English:
1. Whitelist and cast filters, cap `limit`, and always sort by a field plus `_id`.
2. Build the compound index with ESR and prefer keyset (cursor) over deep `skip`.
3. Use `$facet` or `limit + 1` for totals/hasMore and confirm with `explain` (IXSCAN, no SORT).

Hindi:
1. Filters whitelist और cast करो, `limit` cap करो, और sort हमेशा किसी field + `_id` से करो।
2. ESR से compound index बनाओ और गहरे `skip` की जगह keyset (cursor) चुनो।
3. Totals/hasMore के लिए `$facet` या `limit + 1` इस्तेमाल करो और `explain` (IXSCAN, कोई SORT नहीं) से पुष्टि करो।

---

## ➡️ Next Topic
**120. Leaderboard with Aggregation** — rankings with ties, user rank lookup and fast top-N reads.
