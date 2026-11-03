# 60. $facet — Multiple Pipelines
# हिंदी में: $facet — कई Pipelines एक साथ

---

## 🔵 Simple Definition (English)
**`$facet`** runs several independent sub-pipelines on the SAME set of input documents in a single stage and returns one document whose fields are the results of each sub-pipeline. It is used for faceted search (counts per category + results + total) in one round trip.

## 🔵 सरल परिभाषा (Hindi)
**`$facet`** एक ही stage में एक ही input documents पर कई independent sub-pipelines चलाता है और एक document लौटाता है जिसके fields हर sub-pipeline के नतीजे होते हैं। Faceted search (category-wise counts + results + total) एक ही round trip में करने के लिए इस्तेमाल होता है।

---

## 🔴 Problem it Solves
A search results page needs: the current page of results, the total count, and counts per status/brand. Running three queries triples the work and can show inconsistent numbers if data changes between them. `$facet` scans the input once and feeds every sub-pipeline.

## 🔴 यह क्यों बना? (Hindi)
Search results page को चाहिए: मौजूदा page के results, total count, और status/brand-wise counts। तीन queries चलाने से काम तीन गुना होता है और बीच में data बदले तो numbers inconsistent हो सकते हैं। `$facet` input एक बार पढ़कर हर sub-pipeline को देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Put filters before: `$match` first so facet input is small.
Step 2 → `$facet: { name1: [stages], name2: [stages] }`.
Step 3 → Each sub-pipeline receives all input documents independently.
Step 4 → Output is ONE document: `{ name1: [...], name2: [...] }`.
Step 5 → Inside sub-pipelines nested `$facet`, `$out` and `$merge` are not allowed.
Step 6 → The whole output must fit the 16 MB document limit, and sub-pipelines cannot use indexes (input comes from the previous stage).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Filters पहले लगाओ: `$match` पहले ताकि facet का input छोटा रहे।
Step 2 → `$facet: { name1: [stages], name2: [stages] }`।
Step 3 → हर sub-pipeline को सारे input documents अलग-अलग मिलते हैं।
Step 4 → Output एक ही document: `{ name1: [...], name2: [...] }`।
Step 5 → Sub-pipelines के अंदर nested `$facet`, `$out` और `$merge` allowed नहीं हैं।
Step 6 → पूरा output 16 MB document limit में आना चाहिए, और sub-pipelines index इस्तेमाल नहीं कर सकते (input पिछले stage से आता है)।

---

## 🟡 Real World Example
**Flipkart's product listing**: for the query "phone", one `$facet` returns `results` (page 1, 20 items), `total` (count), `byBrand` (counts per brand) and `byPriceBucket` (using `$bucket`). The left filter panel and the grid are filled from one database call.

## 🟡 Real Example Hindi mein
**Flipkart की product listing**: "phone" query के लिए एक `$facet` `results` (page 1, 20 items), `total` (count), `byBrand` (brand-wise counts) और `byPriceBucket` (`$bucket` से) लौटाता है। बायाँ filter panel और grid दोनों एक database call से भरते हैं।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders (6 docs)
db.orders.aggregate([
  { $facet: {
      byStatus: [ { $sortByCount: "$status" } ],                         // counts per status
      top: [ { $sort: { amount: -1 } }, { $limit: 2 },                   // top 2 orders
             { $project: { customer: 1, amount: 1 } } ],
      total: [ { $count: "n" } ]                                         // total documents
  } }
])
// Output (real) — ONE document:
// {
//   byStatus: [ { _id: 'delivered', count: 4 }, { _id: 'cancelled', count: 1 }, { _id: 'pending', count: 1 } ],
//   top: [ { _id: 4, customer: 'Kabir', amount: 890 }, { _id: 1, customer: 'Aarav', amount: 450 } ],
//   total: [ { n: 6 } ]
// }
```

## 💻 Code Example — Advanced

```javascript
// Paginated search + metadata in one call (Node driver)
const [out] = await db.collection("orders").aggregate([
  { $match: { city: "Mumbai" } },                                        // filter once, before facet
  { $facet: {
      rows: [ { $sort: { amount: -1, _id: 1 } },                         // page of results
              { $skip: 0 }, { $limit: 10 } ],
      meta: [ { $group: { _id: null, total: { $sum: 1 }, revenue: { $sum: "$amount" } } } ],
      byStatus: [ { $sortByCount: "$status" } ]
  } }
]).toArray();                                                            // returns an array with 1 doc
const total = out.meta[0]?.total ?? 0;                                   // meta is [] if nothing matched
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/search (Mongoose; the facet pattern was tested on mongod 8.0.4)
app.get("/api/search", async (req, res) => {
  const [r] = await Order.aggregate([
    { $facet: {
        rows: [ { $sort: { _id: 1 } }, { $limit: 2 }, { $project: { customer: 1 } } ],
        total: [ { $count: "n" } ]
    } }
  ]);
  // Real result: {"rows":[{"_id":1,"customer":"Aarav"},{"_id":2,"customer":"Diya"}],"total":[{"n":6}]}
  res.json({ rows: r.rows, total: r.total[0]?.n || 0 });                 // total array is empty when no docs
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Assuming `total` is a number
```javascript
r.total            // Wrong — it is an array [{ n: 6 }]
r.total[0]?.n      // Right — and may be undefined for zero matches
```

❌ Mistake 2: Faceting over the whole collection
✅ Put `$match` BEFORE `$facet`. Sub-pipelines cannot use indexes, and every sub-pipeline reads all input.

❌ Mistake 3: Output bigger than 16 MB
✅ One output document means all facets together are capped at 16 MB. Always `$limit` the results facet.

---

## 🧠 Tricky Interview Question
Q: A `$facet` with a `$match` that finds nothing: what does `total: [{ $count: "n" }]` return?
Answer: An empty array `[]`, not `[{ n: 0 }]`, because `$count` emits no document for empty input. So `total[0].n` throws; use `total[0]?.n ?? 0`. Also, `$facet` always outputs exactly one document even for empty input.

---

## ⚫ Interview Questions + Answers

Q1: What problem does `$facet` solve?
A1: Several aggregations on the same input in one pass and one round trip, e.g. results + counts.

Q2: Can sub-pipelines use indexes?
A2: No. Only the stages before `$facet` can; facet input is the already-selected stream.

Q3: What stages are disallowed inside?
A3: `$facet` (nested), `$out`, `$merge`, and a few others like `$collStats`, `$indexStats`, `$geoNear`.

Q4: How is output shaped?
A4: One document, field per facet, each an array.

Q5: Alternative if the output is too large?
A5: Run separate queries/aggregations, or use `$setWindowFields`/`$group` to compute metadata together with rows.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Search pages with filters and counts
- Dashboards needing several summaries of the same filtered data

❌ Avoid when:
- Result could exceed 16 MB
- Sub-pipelines would each need their own index

---

## 📊 Visual Diagram
```
                 filtered input (after $match)
                        │
                     $facet
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   byStatus[ ]       top[ ]           total[ ]
        └───────────────┼────────────────┘
                        ▼
     ONE document { byStatus:[..], top:[..], total:[..] }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$facet` | Parallel sub-pipelines | समानांतर sub-pipelines |
| Facet | One named sub-result | एक नामित sub-result |
| Faceted search | Results plus category counts | Results के साथ category counts |
| Sub-pipeline | Pipeline inside a facet | Facet के अंदर pipeline |
| 16 MB limit | Max BSON document size | Document का अधिकतम आकार |
| `$count` | Emits `{name: n}` | गिनती वाला stage |

---

## ⚡ 3-Line Summary
English:
1. `$facet` runs many sub-pipelines on the same input and returns one document.
2. `$match` before it; no indexes inside; output capped at 16 MB.
3. Each facet is an array, so `$count` results need `[0]?.n`.

Hindi:
1. `$facet` एक ही input पर कई sub-pipelines चलाकर एक document लौटाता है।
2. उससे पहले `$match`; अंदर index नहीं चलता; output 16 MB तक सीमित।
3. हर facet array है, इसलिए `$count` का नतीजा `[0]?.n` से पढ़ो।

---

## ➡️ Next Topic
**61. $bucket and $bucketAuto** — grouping values into ranges.
