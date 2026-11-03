# 63. $unionWith and $merge/$out
# हिंदी में: $unionWith और $merge/$out

---

## 🔵 Simple Definition (English)
**`$unionWith`** appends the documents of another collection (optionally run through its own pipeline) to the current stream, like SQL `UNION ALL`. **`$out`** and **`$merge`** are the two output stages that WRITE the pipeline result into a collection. `$out` replaces the target collection entirely; `$merge` inserts or updates documents inside it. Both must be the last stage.

## 🔵 सरल परिभाषा (Hindi)
**`$unionWith`** दूसरी collection के documents (चाहे उनकी अपनी pipeline से गुज़रे) मौजूदा stream में जोड़ देता है, SQL के `UNION ALL` जैसा। **`$out`** और **`$merge`** वो दो output stages हैं जो pipeline का नतीजा collection में लिखते हैं। `$out` target collection पूरी बदल देता है; `$merge` उसके अंदर documents insert या update करता है। दोनों आखिरी stage होने चाहिए।

---

## 🔴 Problem it Solves
Data often lives in several collections (live `orders` and `archived` orders) and reports need both. Also expensive reports should be precomputed once and saved (a summary collection) instead of recomputed on every dashboard load. `$unionWith` combines; `$out`/`$merge` materialize.

## 🔴 यह क्यों बना? (Hindi)
Data अक्सर कई collections में होता है (live `orders` और `archived` orders) और reports को दोनों चाहिए। महँगी reports को हर dashboard load पर दोबारा चलाने की जगह एक बार precompute करके save करना बेहतर है (summary collection)। `$unionWith` जोड़ता है; `$out`/`$merge` नतीजा सहेजते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ $unionWith: { coll: "archived", pipeline: [...] } }` (4.4+) reads `archived`, runs the optional pipeline, and appends results after the current documents.
Step 2 → Shorthand: `{ $unionWith: "archived" }`. Duplicates are NOT removed (it is UNION ALL). Add `$group` to dedupe.
Step 3 → `$out: "name"` writes results to a collection, atomically replacing it when the pipeline finishes (existing indexes are kept; on failure the old collection stays).
Step 4 → `$merge: { into, on, whenMatched, whenNotMatched }` (4.2+) upserts per document. `on` must be a unique index (the `_id` index works).
Step 5 → `whenMatched`: "replace", "keepExisting", "merge", "fail" or a pipeline. `whenNotMatched`: "insert", "discard", "fail".
Step 6 → `$merge` can write into the same collection you read from (4.4+). Prefer `$merge` for incremental refresh and `$out` for a full rebuild.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `{ $unionWith: { coll: "archived", pipeline: [...] } }` (4.4+) `archived` पढ़ता है, optional pipeline चलाता है और नतीजे मौजूदा documents के बाद जोड़ता है।
Step 2 → Shorthand: `{ $unionWith: "archived" }`। Duplicates हटते नहीं (UNION ALL है)। Dedupe के लिए `$group` लगाओ।
Step 3 → `$out: "name"` नतीजा collection में लिखता है, pipeline खत्म होने पर उसे atomically बदल देता है (मौजूदा indexes रहते हैं; fail हो तो पुरानी collection रहती है)।
Step 4 → `$merge: { into, on, whenMatched, whenNotMatched }` (4.2+) हर document का upsert करता है। `on` unique index होना चाहिए (`_id` index चलता है)।
Step 5 → `whenMatched`: "replace", "keepExisting", "merge", "fail" या pipeline। `whenNotMatched`: "insert", "discard", "fail"।
Step 6 → `$merge` उसी collection में भी लिख सकता है जिससे पढ़ रहा है (4.4+); incremental refresh के लिए `$merge` बेहतर है, पूरा बदलने के लिए `$out`।

---

## 🟡 Real World Example
**Razorpay's reconciliation**: the live `payments` collection holds the last 90 days and `payments_archive` holds older ones. Annual reports use `$unionWith` to read both. A nightly job computes per-merchant totals and saves them into `merchant_daily_summary` with `$merge`, so the dashboard reads a tiny precomputed collection.

## 🟡 Real Example Hindi mein
**Razorpay की reconciliation**: live `payments` collection में पिछले 90 दिन और `payments_archive` में पुराने होते हैं। Annual reports `$unionWith` से दोनों पढ़ती हैं। हर रात एक job merchant-wise totals निकालकर `$merge` से `merchant_daily_summary` में save करती है, इसलिए dashboard एक छोटी precomputed collection पढ़ता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4. archived has one doc: { _id:101, customer:"Old", city:"Delhi", amount:60 }
db.orders.aggregate([
  { $match: { _id: 1 } },                                            // one live order
  { $project: { customer: 1, city: 1, amount: 1 } },
  { $unionWith: {
      coll: "archived",                                              // collection to append
      pipeline: [ { $project: { customer: 1, city: 1, amount: 1 } } ] // shape it the same way
  } }
])
// Output (real):
// { _id: 1,   customer: 'Aarav', city: 'Delhi', amount: 450 }
// { _id: 101, customer: 'Old',   city: 'Delhi', amount: 60 }
```

## 💻 Code Example — Advanced

```javascript
// $merge: refresh a summary collection (insert new customers, replace existing ones)
db.orders.aggregate([
  { $group: { _id: "$customer", total: { $sum: "$amount" } } },      // per-customer revenue
  { $merge: {
      into: "cust_totals",                                           // target collection (created if missing)
      on: "_id",                                                     // match key, must be unique
      whenMatched: "replace",                                        // update existing summary doc
      whenNotMatched: "insert"                                       // create if absent
  } }
])
db.cust_totals.find().sort({ _id: 1 })
// Output (real):
// { _id: 'Aarav', total: 570 }
// { _id: 'Diya',  total: 540 }
// { _id: 'Kabir', total: 890 }
// { _id: 'Meera', total: 75 }

// $out: replace the whole target collection
db.orders.aggregate([ { $match: { status: "delivered" } }, { $out: "delivered_orders" } ])
db.delivered_orders.countDocuments()   // Output (real): 4
```
Both stages return no documents (the cursor is empty); you read the target collection afterwards.

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Nightly refresh endpoint/cron (Mongoose, same pipeline tested in mongosh on mongod 8.0.4)
async function refreshTotals() {
  await Order.aggregate([
    { $group: { _id: "$customer", total: { $sum: "$amount" } } },
    { $merge: { into: "cust_totals", on: "_id", whenMatched: "replace", whenNotMatched: "insert" } }
  ]);                                               // awaiting runs it to completion; result is []
}

// Read side: tiny precomputed collection
const CustTotal = mongoose.model("CustTotal", new mongoose.Schema({ total: Number }), "cust_totals");
app.get("/api/totals", async (req, res) => res.json(await CustTotal.find().sort({ _id: 1 }).lean()));

// union with Mongoose
const all = await Order.aggregate([{ $match: { _id: 2 } }, { $project: { customer: 1 } },
                                    { $unionWith: "archived" }, { $project: { customer: 1 } }]);
// Real result: [{"_id":2,"customer":"Diya"},{"_id":101,"customer":"Old"}]
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `$out` on a collection you need to keep
```javascript
db.orders.aggregate([{ $match: { status: "delivered" } }, { $out: "orders" }]) // Wrong — replaces orders with only delivered ones!
db.orders.aggregate([{ $match: { status: "delivered" } }, { $out: "delivered_orders" }]) // Right — separate target
```

❌ Mistake 2: `$merge` on a non-unique key
✅ `on` fields must have a unique index (or be `_id`), otherwise the stage errors.

❌ Mistake 3: Thinking `$unionWith` dedupes
✅ It keeps duplicates (UNION ALL). Add `$group: { _id: "$_id" }` or similar to remove them.

---

## 🧠 Tricky Interview Question
Q: After `$unionWith`, in what order do documents appear?
Answer: The documents from the input pipeline first, then the documents from the unioned collection. No sort is applied, and the second part has no guaranteed internal order, so add `$sort` if you need one. Also `$unionWith` is not a join: it stacks rows, it does not match them.

---

## ⚫ Interview Questions + Answers

Q1: `$out` vs `$merge`?
A1: `$out` replaces the whole target collection; `$merge` upserts into it and can keep existing documents, merge fields or run a custom pipeline.

Q2: Why must they be the last stage?
A2: They write results out and emit nothing for later stages.

Q3: How do you build a materialized view?
A3: Run a pipeline ending in `$merge` on a schedule, reading from the small summary collection.

Q4: Is `$unionWith` the same as `$lookup`?
A4: No. `$lookup` joins matching documents into an array; `$unionWith` appends all documents of another collection.

Q5: Are `$merge`/`$out` allowed in `$facet` or transactions?
A5: Neither is allowed inside `$facet` (the server rejects `$out` there with an error, verified). In multi-document transactions they are restricted too, so check the docs for your version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Combining live and archive collections (`$unionWith`)
- Precomputing summaries (`$merge` incremental, `$out` full rebuild)

❌ Avoid when:
- A join is needed (use `$lookup`)
- Data must be real-time (summaries lag)

---

## 📊 Visual Diagram
```
 orders ──$match──$project─┐
                           ├─ $unionWith ─► [order 1, archived 101]
 archived ──$project───────┘

 orders ─► $group ─► $merge into cust_totals   (upsert per _id)
 orders ─► $match ─► $out   delivered_orders   (replace collection)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$unionWith` | Append another collection | दूसरी collection जोड़ना |
| UNION ALL | Union keeping duplicates | Duplicates के साथ union |
| `$out` | Replace target collection | Target collection बदलना |
| `$merge` | Upsert into target | Target में upsert |
| `whenMatched` | Action if key exists | Key मिलने पर action |
| Materialized view | Saved pipeline result | सहेजा हुआ pipeline नतीजा |

---

## ⚡ 3-Line Summary
English:
1. `$unionWith` stacks another collection's documents (no dedupe, no join).
2. `$out` replaces a collection; `$merge` upserts into it; both go last.
3. Use `$merge` on a schedule to keep summary collections fresh.

Hindi:
1. `$unionWith` दूसरी collection के documents जोड़ता है (dedupe नहीं, join नहीं)।
2. `$out` collection बदलता है; `$merge` उसमें upsert करता है; दोनों आखिर में।
3. Summary collections को ताज़ा रखने के लिए schedule पर `$merge` चलाओ।

---

## ➡️ Next Topic
**64. $graphLookup** — recursive lookups for hierarchies.
