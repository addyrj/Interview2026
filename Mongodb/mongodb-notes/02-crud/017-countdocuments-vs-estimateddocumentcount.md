# 17. countDocuments vs estimatedDocumentCount
# हिंदी में: countDocuments बनाम estimatedDocumentCount

---

## 🔵 Simple Definition (English)
`countDocuments(filter)` returns an **accurate** count of documents matching a filter (it runs an aggregation `$match` + `$group`). `estimatedDocumentCount()` returns the whole-collection count from **metadata** – very fast, but takes no filter and can be slightly off after unclean shutdowns or on sharded clusters with orphans. The old `count()` is deprecated.

## 🔵 सरल परिभाषा (Hindi)
`countDocuments(filter)` filter से match होने वाले documents की **सटीक** गिनती देता है (यह aggregation `$match` + `$group` चलाता है)। `estimatedDocumentCount()` पूरे collection की गिनती **metadata** से देता है – बहुत तेज़, पर filter नहीं लेता और unclean shutdown के बाद या orphans वाले sharded clusters में थोड़ा गलत हो सकता है। पुराना `count()` deprecated है।

---

## 🔴 Problem it Solves
Showing "12,430 results" or "total orders" needs counting. Scanning a big collection for every page view is expensive. The two methods let you choose: accuracy with a filter (`countDocuments`) or speed for a rough total (`estimatedDocumentCount`).

## 🔴 यह क्यों बना? (Hindi)
"12,430 results" या "total orders" दिखाने के लिए गिनती चाहिए। हर page view पर बड़ा collection scan करना महँगा है। ये दो methods चुनाव देते हैं: filter के साथ accuracy (`countDocuments`) या मोटे total के लिए speed (`estimatedDocumentCount`)।

---

## 🟢 How it Works — Step by Step

Step 1 → `countDocuments({})` or with a filter: server runs `[{$match: filter}, {$group: {_id: 1, n: {$sum: 1}}}]`.
Step 2 → If an index covers the filter, it counts index entries (fast); otherwise scans documents.
Step 3 → `estimatedDocumentCount()` reads the stored collection count from metadata, no scanning, O(1).
Step 4 → It ignores filters entirely; options are only `maxTimeMS`.
Step 5 → Inside multi-document transactions use `countDocuments` (estimated is not allowed in transactions).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `countDocuments({})` या filter के साथ: server `[{$match: filter}, {$group: {_id: 1, n: {$sum: 1}}}]` चलाता है।
Step 2 → Filter को index cover करे तो index entries गिनता है (तेज़); नहीं तो documents scan करता है।
Step 3 → `estimatedDocumentCount()` stored collection count metadata से पढ़ता है, scan नहीं, O(1)।
Step 4 → यह filter को पूरी तरह ignore करता है; सिर्फ़ `maxTimeMS` option है।
Step 5 → Multi-document transactions में `countDocuments` इस्तेमाल करो (estimated की अनुमति नहीं)।

---

## 🟡 Real World Example
Swiggy's admin dashboard header shows "Total orders ever" using `estimatedDocumentCount()` on a 500M-doc collection (instant), while the "Cancelled orders today" tile uses `countDocuments({status:"CANCELLED", createdAt:{$gte: startOfDay}})` backed by an index, because that number must be exact.

## 🟡 Real Example Hindi mein
Swiggy के admin dashboard का header 500M-doc collection पर "Total orders ever" `estimatedDocumentCount()` से दिखाता है (तुरंत), जबकि "आज के Cancelled orders" tile `countDocuments({status:"CANCELLED", createdAt:{$gte: startOfDay}})` से index के सहारे आता है क्योंकि यह संख्या exact होनी चाहिए।

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh", collection m has 5 docs, two have p: 10
db.m.countDocuments({ p: 10 })        // Output: 2  (accurate, filtered)
db.m.countDocuments({})               // Output: 5  (all docs, still accurate)
db.m.estimatedDocumentCount()         // Output: 5  (metadata, no filter possible)
```

## 💻 Code Example — Advanced

```javascript
// Equivalent aggregation that countDocuments runs internally
db.m.aggregate([
  { $match: { p: 10 } },                         // filter
  { $group: { _id: 1, n: { $sum: 1 } } }          // count
])
// Output: [ { _id: 1, n: 2 } ]   (verified)

// Make filtered counts fast with an index
db.m.createIndex({ p: 1 })
db.m.explain("executionStats").aggregate([{ $match: { p: 10 } }, { $group: { _id: 1, n: { $sum: 1 } } }])
// shows IXSCAN on p_1 instead of COLLSCAN

// countDocuments options: limit caps work for "10+" style badges
db.m.countDocuments({ p: { $gte: 10 } }, { limit: 3 })   // Output: 3 (stops counting at 3)

// estimatedDocumentCount with a timeout
db.m.estimatedDocumentCount({ maxTimeMS: 500 })          // Output: 5
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
app.get('/stats', async (req, res) => {
  const [total, pending] = await Promise.all([
    Order.estimatedDocumentCount(),                       // fast approximate total
    Order.countDocuments({ status: 'PENDING' })           // exact filtered count
  ]);
  res.json({ total, pending });
});
// Mongoose: Model.count() is removed/deprecated - use the two methods above.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing a filter to `estimatedDocumentCount`
```javascript
db.m.estimatedDocumentCount({ p: 10 })   // Wrong: verified on 8.0.4 - the filter is silently ignored and it returns 5, not 2
db.m.countDocuments({ p: 10 })           // Right
```

❌ Mistake 2: Using `countDocuments({})` for the total of a huge collection on every request
✅ Correct: Use `estimatedDocumentCount()` when approximate is fine.

❌ Mistake 3: Using deprecated `count()`
✅ Correct: Replace it with one of the two methods.

---

## 🧠 Tricky Interview Question
Q: On a sharded cluster the estimated count is higher than reality. Why?
Answer: Orphaned documents (left on a shard after a chunk migration or failed cleanup) are included in metadata counts. `countDocuments` goes through the aggregation path that filters orphans, so it is accurate.

---

## ⚫ Interview Questions + Answers

Q1: Which is faster?
A1: `estimatedDocumentCount` (metadata, O(1)).

Q2: Why was `count()` deprecated?
A2: It could return inaccurate results (orphans, unclean shutdown) when used with a filter; the new methods have clear semantics.

Q3: Can `countDocuments` use an index?
A3: Yes; with a matching index it counts index keys without fetching documents.

Q4: Can you count in a transaction?
A4: Use `countDocuments`.

Q5: How to count distinct values?
A5: Aggregation `$group` by the field then `$count`, or `distinct()` for small cardinality.

---

## 🔷 When to Use + When Not to Use
✅ Use `countDocuments` when:
- You need exactness or a filter

✅ Use `estimatedDocumentCount` when:
- Dashboards, rough totals on huge collections

❌ Avoid `countDocuments({})` when:
- Running it per request on huge data

---

## 📊 Visual Diagram
```
countDocuments(filter)            estimatedDocumentCount()
  $match + $group                   read collection metadata
  (index or scan)                   (O(1), no filter)
  exact ✔  slower                   approx ~  instant
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| countDocuments | Exact filtered count | सटीक filtered गिनती |
| estimatedDocumentCount | Metadata count | Metadata से अनुमानित गिनती |
| Metadata | Stored collection info | Collection की stored जानकारी |
| Orphan document | Stray doc on a shard | Shard पर बचा हुआ extra doc |

---

## ⚡ 3-Line Summary
English:
1. `countDocuments` is exact and takes a filter; `estimatedDocumentCount` is instant and filterless.
2. Index your filter fields for fast exact counts.
3. Do not use deprecated `count()`.

Hindi:
1. `countDocuments` सटीक है और filter लेता है; `estimatedDocumentCount` तुरंत है और filter नहीं लेता।
2. तेज़ exact counts के लिए filter fields पर index बनाओ।
3. Deprecated `count()` इस्तेमाल मत करो।

---

## ➡️ Next Topic
**18. updateOne and updateMany**
