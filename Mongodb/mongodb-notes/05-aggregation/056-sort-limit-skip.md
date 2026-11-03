# 56. $sort, $limit, $skip in Pipelines
# हिंदी में: Pipeline में $sort, $limit, $skip

---

## 🔵 Simple Definition (English)
**`$sort`** orders documents (1 ascending, -1 descending). **`$limit`** keeps only the first N documents. **`$skip`** drops the first N. Combined, they give "top N" lists and pagination inside an aggregation pipeline.

## 🔵 सरल परिभाषा (Hindi)
**`$sort`** documents को क्रम में लगाता है (1 ascending, -1 descending)। **`$limit`** सिर्फ पहले N documents रखता है। **`$skip`** पहले N छोड़ देता है। तीनों मिलकर pipeline में "top N" lists और pagination देते हैं।

---

## 🔴 Problem it Solves
Apps show "top 10 restaurants" or page 3 of an order list. Sorting and slicing in application code means loading everything. Doing it in the pipeline lets the database return exactly one page, and `$sort` + `$limit` together use a special top-k algorithm that keeps only N documents in memory.

## 🔴 यह क्यों बना? (Hindi)
Apps "top 10 restaurants" या order list का page 3 दिखाते हैं। Application code में sort और slice करने के लिए सब कुछ load करना पड़ता। Pipeline में करने से database सिर्फ एक page लौटाता है, और `$sort` + `$limit` साथ हों तो top-k algorithm सिर्फ N documents memory में रखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `$sort: { amount: -1 }` orders the stream, highest first.
Step 2 → Sort on multiple fields: `{ city: 1, amount: -1 }`, left to right priority.
Step 3 → `$skip: n` discards n documents; `$limit: m` then keeps m. Order of stages matters: skip then limit.
Step 4 → If `$sort` is the first stage (or right after an index-friendly `$match`), an index can supply the order with no in-memory sort.
Step 5 → Sort is not stable for ties. Add a unique tiebreaker like `_id` for deterministic pages.
Step 6 → Without an index a blocking sort is limited to 100 MB unless `allowDiskUse` is used.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `$sort: { amount: -1 }` stream को सबसे बड़े से क्रम में लगाता है।
Step 2 → कई fields पर sort: `{ city: 1, amount: -1 }`, priority बाएँ से दाएँ।
Step 3 → `$skip: n` n documents हटाता है; फिर `$limit: m` m रखता है। Stages का क्रम मायने रखता है: पहले skip फिर limit।
Step 4 → अगर `$sort` पहला stage है (या index-friendly `$match` के बाद), तो index से order मिल जाता है, memory में sort नहीं होता।
Step 5 → बराबर values पर sort stable नहीं होता। Deterministic pages के लिए `_id` जैसा unique tiebreaker जोड़ो।
Step 6 → बिना index के blocking sort की limit 100 MB है, जब तक `allowDiskUse` न हो।

---

## 🟡 Real World Example
**Flipkart's "Top deals" and order list**: the home page runs `$sort` by discount descending with `$limit: 20`. The "My Orders" page uses `$sort` by date with `$skip` and `$limit` for paging. A compound index `{ userId: 1, ts: -1 }` makes the order list sort free.

## 🟡 Real Example Hindi mein
**Flipkart का "Top deals" और order list**: home page discount के हिसाब से `$sort` descending और `$limit: 20` चलाता है। "My Orders" page date से `$sort` और `$skip`/`$limit` से paging करता है। Compound index `{ userId: 1, ts: -1 }` से sort मुफ्त हो जाता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders
// Page 2 (size 2) of orders by amount descending
db.orders.aggregate([
  { $sort: { amount: -1 } },                       // 890, 450, 310, 230, 120, 75
  { $skip: 1 },                                    // drop the biggest one
  { $limit: 2 },                                   // keep the next two
  { $project: { customer: 1, amount: 1 } }
])
// Output (real):
// { _id: 1, customer: 'Aarav', amount: 450 }
// { _id: 5, customer: 'Diya',  amount: 310 }
```

## 💻 Code Example — Advanced

```javascript
// Multi-field sort: city ascending, then amount descending within each city
db.orders.aggregate([
  { $sort: { city: 1, amount: -1 } },
  { $project: { city: 1, amount: 1 } }
])
// Output (real):
// { _id: 1, city: 'Delhi',  amount: 450 }
// { _id: 3, city: 'Delhi',  amount: 120 }
// { _id: 4, city: 'Mumbai', amount: 890 }
// { _id: 5, city: 'Mumbai', amount: 310 }
// { _id: 2, city: 'Mumbai', amount: 230 }
// { _id: 6, city: 'Pune',   amount: 75 }

// Range pagination: faster than $skip on big collections (no skipping cost)
db.orders.aggregate([
  { $match: { _id: { $gt: 3 } } },                 // continue after the last _id of previous page
  { $sort: { _id: 1 } },                           // uses the _id index
  { $limit: 2 }                                    // page size
])
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/orders?page=2&size=2 (tested with Mongoose on mongod 8.0.4)
app.get("/api/orders", async (req, res) => {
  const page = Math.max(parseInt(req.query.page) || 1, 1);   // never below 1 (skip rejects negatives)
  const size = Math.min(parseInt(req.query.size) || 10, 50); // cap size so clients cannot ask for 1M rows
  const rows = await Order.aggregate([
    { $sort: { amount: -1, _id: 1 } },             // _id as tiebreaker for stable pages
    { $skip: (page - 1) * size },
    { $limit: size },
    { $project: { customer: 1, amount: 1 } }
  ]);
  res.json({ page, size, rows });
});
// Real result for page=2,size=2:
// [{"_id":5,"customer":"Diya","amount":310},{"_id":2,"customer":"Diya","amount":230}]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `$limit` before `$sort`
```javascript
// Wrong — takes 2 arbitrary docs, THEN sorts them
db.orders.aggregate([{ $limit: 2 }, { $sort: { amount: -1 } }])
// Right — sort first, then limit
db.orders.aggregate([{ $sort: { amount: -1 } }, { $limit: 2 }])
```

❌ Mistake 2: Negative or zero values
```javascript
// $skip: -1 -> error "Expected a non-negative number in: $skip: -1"
// $limit: 0 -> error "the limit must be positive"
```

❌ Mistake 3: Deep `$skip` pagination
✅ `$skip: 100000` still walks 100000 entries. Use range pagination (`_id > lastSeen`).

---

## 🧠 Tricky Interview Question
Q: Two orders have the same amount. You paginate with only `$sort: {amount: -1}`. What can go wrong?
Answer: Ties have no guaranteed order, so the same document can appear on two pages or be missed. Fix by adding a unique second key: `{ amount: -1, _id: 1 }`.

---

## ⚫ Interview Questions + Answers

Q1: What does `$sort` + `$limit` do internally?
A1: The optimizer coalesces them into a top-k sort that holds only `limit` documents in memory.

Q2: When can `$sort` use an index?
A2: When it is at the start of the pipeline, or after a `$match`, and the index key order matches the sort. Stages like `$group` or `$project` that change fields break this.

Q3: `$skip` vs range pagination?
A3: `$skip` is simple but O(n) in the offset; range pagination filters by last seen key and stays fast.

Q4: What is the sort memory limit?
A4: 100 MB per blocking stage unless disk use is allowed.

Q5: How do you get a global top-N and per-group top-N?
A5: Global: `$sort` + `$limit`. Per group: `$group` with `$topN`/`$push` + `$slice`, or `$setWindowFields` (5.0+).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Leaderboards, top-N lists, small paged lists

❌ Avoid when:
- Very deep pages with `$skip` (use range pagination)
- Sorting huge unindexed data in memory

---

## 📊 Visual Diagram
```
 amounts: 890 450 310 230 120 75      (after $sort -1)
           └─┘ └──────┘
          skip=1  limit=2  ->  450, 310
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$sort` | Orders documents | क्रम में लगाता है |
| `$limit` | Keep first N | पहले N रखो |
| `$skip` | Drop first N | पहले N छोड़ो |
| Tiebreaker | Unique extra sort key | Ties तोड़ने वाली unique key |
| Top-k sort | Sort that stores only k docs | सिर्फ k docs रखने वाला sort |
| Range pagination | Page using last seen key | आखिरी key से paging |

---

## ⚡ 3-Line Summary
English:
1. `$sort` orders, `$skip` drops, `$limit` keeps; order of stages matters.
2. Always add a unique tiebreaker like `_id` for stable pages.
3. Prefer range pagination over deep `$skip`.

Hindi:
1. `$sort` क्रम लगाता है, `$skip` छोड़ता है, `$limit` रखता है; stages का क्रम मायने रखता है।
2. Stable pages के लिए `_id` जैसा unique tiebreaker हमेशा जोड़ो।
3. गहरे `$skip` की जगह range pagination इस्तेमाल करो।

---

## ➡️ Next Topic
**57. $unwind** — flattening arrays into one document per element.
