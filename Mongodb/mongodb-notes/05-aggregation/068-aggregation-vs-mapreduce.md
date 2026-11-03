# 68. Aggregation vs MapReduce
# हिंदी में: Aggregation बनाम MapReduce

---

## 🔵 Simple Definition (English)
**MapReduce** is the older way to compute aggregates: you write a JavaScript `map` function that `emit`s key/value pairs and a `reduce` function that folds the values per key. The **aggregation pipeline** does the same jobs declaratively with native operators (`$group`, `$sum`, `$merge`...). Since MongoDB **5.0, `mapReduce` is deprecated**; the docs say to use aggregation (with `$group`, `$merge`, and when truly needed `$accumulator` / `$function`). Verified on 8.0.4: `mapReduce` still runs but prints a `DeprecationWarning`.

## 🔵 सरल परिभाषा (Hindi)
**MapReduce** aggregates निकालने का पुराना तरीका है: आप JavaScript `map` function लिखते हैं जो key/value pairs `emit` करता है और `reduce` function जो हर key के values को fold करता है। **Aggregation pipeline** वही काम declarative तरीके से native operators (`$group`, `$sum`, `$merge`...) से करती है। MongoDB **5.0 से `mapReduce` deprecated** है; docs कहते हैं aggregation इस्तेमाल करो (`$group`, `$merge`, और ज़रूरत हो तो `$accumulator` / `$function`)। 8.0.4 पर verify किया: `mapReduce` अब भी चलता है पर `DeprecationWarning` छापता है।

---

## 🔴 Problem it Solves
Early MongoDB had no powerful query-side analytics, so MapReduce (inspired by Google's paper) was the only way to do grouping and custom calculations. But it runs **JavaScript in the server's JS engine**: slow (BSON to JS and back), hard to index, hard to read/debug, no pipeline optimization and a security surface. The aggregation framework runs compiled C++ operators, gets optimized, uses indexes in its first stages and composes (`$match` → `$group` → `$sort`). Understanding the comparison is a classic interview question and helps you migrate legacy jobs.

## 🔴 यह क्यों बना? (Hindi)
शुरुआती MongoDB में query-side analytics नहीं थी, तो MapReduce (Google के paper से प्रेरित) grouping और custom calculation का एकमात्र तरीका था। पर यह **server के JS engine में JavaScript** चलाता है: slow (BSON से JS और वापस), index मुश्किल, पढ़ना/debug करना कठिन, pipeline optimization नहीं, और security risk। Aggregation framework compiled C++ operators चलाता है, optimize होता है, पहले stages में index इस्तेमाल करता है और compose होता है। यह तुलना interview का classic सवाल है और legacy jobs migrate करने में काम आती है।

---

## 🟢 How it Works — Step by Step

Step 1 → MapReduce: server iterates the input docs and calls your `map()` for each; inside, `emit(key, value)` outputs a pair.
Step 2 → Server groups emitted values by key and calls `reduce(key, values[])` (it may call it multiple times on partial sets, so reduce must be **associative, commutative and idempotent**, and return the same shape it receives).
Step 3 → Output goes `inline` (16 MB limit) or `out` to a collection (modern servers: only `replace`/`merge`/`reduce` modes).
Step 4 → Aggregation equivalent: `$match` (input filter) → `$group` with accumulators (`$sum`, `$avg`, `$push`...) → `$sort` → optionally `$merge` into a collection (the replacement for `out`).
Step 5 → For logic that no operator expresses, aggregation has `$accumulator` (custom accumulate/merge/finalize JS) and `$function` (custom JS expression) — still JS, so a last resort, and disabled when `security.javascriptEnabled: false`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → MapReduce: server input docs पर iterate करके हर doc के लिए आपका `map()` बुलाता है; उसके अंदर `emit(key, value)` एक pair देता है।
Step 2 → Server emitted values को key से group करके `reduce(key, values[])` बुलाता है (यह partial sets पर कई बार चल सकता है, इसलिए reduce **associative, commutative और idempotent** होना चाहिए और वही shape लौटाए जो लेता है)।
Step 3 → Output `inline` (16 MB limit) या `out` से collection में (modern servers में सिर्फ़ `replace`/`merge`/`reduce` modes)।
Step 4 → Aggregation equivalent: `$match` (input filter) → accumulators के साथ `$group` (`$sum`, `$avg`, `$push`...) → `$sort` → ज़रूरत हो तो `$merge` (यह `out` का replacement है)।
Step 5 → जिस logic को कोई operator express न कर पाए उसके लिए `$accumulator` (custom accumulate/merge/finalize JS) और `$function` हैं — ये भी JS हैं, इसलिए आख़िरी विकल्प, और `security.javascriptEnabled: false` होने पर बंद रहते हैं।

---

## 🟡 Real World Example
**Razorpay's old nightly settlement job** used `mapReduce` to total payments per merchant: `map` emitted `(merchantId, amount)` and `reduce` summed. It took minutes and could not use a compound index well. The rewrite is a three-stage pipeline: `$match` the day's range (index), `$group` by merchant with `$sum`, `$merge` into `merchant_daily_totals`. Same result, much faster, and the `$merge` target can be updated incrementally.

## 🟡 Real Example Hindi mein
**Razorpay की पुरानी nightly settlement job** merchant-wise payments का total निकालने के लिए `mapReduce` इस्तेमाल करती थी: `map` ने `(merchantId, amount)` emit किया और `reduce` ने जोड़ा। मिनट लगते थे और compound index ठीक से नहीं लगता था। Rewrite तीन-stage pipeline है: दिन की range पर `$match` (index), merchant से `$group` + `$sum`, और `$merge` से `merchant_daily_totals` में। नतीजा वही, पर बहुत तेज़, और `$merge` target incrementally update हो सकता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh on MongoDB 8.0.4
use t68
db.orders.insertMany([                              // 3 sample orders
  { city: "Pune",  amount: 100 },
  { city: "Pune",  amount: 250 },
  { city: "Delhi", amount: 300 }
])

// OLD WAY: mapReduce - total amount per city (deprecated since 5.0)
db.orders.mapReduce(
  function () { emit(this.city, this.amount); },            // map: one (key,value) per doc
  function (key, values) { return Array.sum(values); },     // reduce: fold the values of one key
  { out: { inline: 1 } }                                    // return the result instead of writing a collection
)
// Prints: DeprecationWarning: Collection.mapReduce() is deprecated. Use an aggregation instead.
// Output: { results: [ { _id: 'Delhi', value: 300 }, { _id: 'Pune', value: 350 } ], ok: 1 }

// NEW WAY: the same thing with $group (native, optimizable, can use an index in $match)
db.orders.aggregate([
  { $group: { _id: "$city", total: { $sum: "$amount" } } }, // group key = city, accumulate with $sum
  { $sort: { _id: 1 } }                                     // sort by city name for stable output
])
// Output: [ { _id: 'Delhi', total: 300 }, { _id: 'Pune', total: 350 } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — replacing mapReduce "out: collection" with $merge, and custom logic with $accumulator

// 1) $merge = materialized result collection (replacement for mapReduce's out)
db.orders.aggregate([
  { $group: { _id: "$city", total: { $sum: "$amount" } } },   // compute
  { $merge: { into: "city_totals", whenMatched: "replace" } } // upsert by _id into city_totals
])
db.city_totals.find().sort({ _id: 1 })
// Output: [ { _id: 'Delhi', total: 300 }, { _id: 'Pune', total: 350 } ]
// whenMatched options: replace | merge | keepExisting | fail | [pipeline]; whenNotMatched: insert | discard | fail

// 2) Custom average with $accumulator (JavaScript, like old map/reduce but inside $group)
db.orders.aggregate([
  { $group: { _id: "$city",
      avg: { $accumulator: {
        init: function () { return { s: 0, n: 0 }; },                       // initial state per group
        accumulate: function (st, a) { return { s: st.s + a, n: st.n + 1 }; },// fold one doc's value in
        accumulateArgs: ["$amount"],                                        // fields passed as "a"
        merge: function (a, b) { return { s: a.s + b.s, n: a.n + b.n }; },  // combine partial states (shards)
        finalize: function (s) { return s.s / s.n; },                       // final value
        lang: "js"
      } } } },
  { $sort: { _id: 1 } }
])
// Output: [ { _id: 'Delhi', avg: 300 }, { _id: 'Pune', avg: 175 } ]
// But the native { $avg: "$amount" } gives the same answer faster - $accumulator is the last resort.
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

const Order = mongoose.model('Order', new mongoose.Schema({ city: String, amount: Number }));
const app = express();

// Modern reporting endpoint - aggregation, not mapReduce
app.get('/totals', async (req, res) => {
  const rows = await Order.aggregate([
    { $group: { _id: '$city', total: { $sum: '$amount' }, orders: { $sum: 1 } } },
    { $sort: { total: -1 } }
  ]);
  res.json(rows);
});

// Nightly refresh job (cron / BullMQ) writing a read-optimised summary collection
async function refreshCityTotals() {
  await Order.aggregate([
    { $group: { _id: '$city', total: { $sum: '$amount' } } },
    { $merge: { into: 'city_totals', whenMatched: 'replace', whenNotMatched: 'insert' } }
  ]);                                    // $merge as the last stage returns no documents
}
// Mongoose 8 has no Model.mapReduce() at all - another sign to avoid it.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Writing new code with `mapReduce`
```javascript
// Wrong — deprecated, slower, JS execution, blocked if javascriptEnabled=false
db.orders.mapReduce(function(){ emit(this.city, 1) }, function(k,v){ return Array.sum(v) }, { out: "counts" })
// Right
db.orders.aggregate([ { $group: { _id: "$city", n: { $sum: 1 } } }, { $merge: "counts" } ])
```

❌ Mistake 2: A non-idempotent `reduce` (or returning a different shape than `emit`)
```javascript
// Wrong — reduce may run on partial results again; returning {count: n} while emit used a number breaks the 2nd pass
function (k, vals) { return { count: vals.length }; }
// Right — emit and reduce must return the same shape: emit(k, 1) and reduce returns Array.sum(vals)
```
✅ Also: reaching for `$function`/`$accumulator` first. Check if `$reduce`, `$map`, `$filter`, `$avg` or `$setUnion` already do it.

---

## 🧠 Tricky Interview Question

If a key has only **one** emitted value, does MongoDB call `reduce` for it?

Answer: No. For a key with a single value the server skips `reduce` and uses that value directly as the result. That is exactly why `reduce` must return the **same shape** as the value passed to `emit` — otherwise keys with one value and keys with many values would have different output shapes. In the aggregation pipeline this problem doesn't exist: `$group` always runs its accumulators.

---

## ⚫ Interview Questions + Answers

Q1: Why was mapReduce deprecated?
A1: Aggregation covers its use cases with faster native operators, index use and optimizer rewrites. MapReduce's JS execution is slower, harder to maintain, and was the only feature needing server-side JS for ordinary analytics. Deprecated in 5.0; use `$group`/`$merge`.

Q2: How do you replace `out: "collection"`?
A2: End the pipeline with `$merge` (insert/update/replace into an existing or new collection, even on sharded ones) or `$out` (replaces the entire target collection atomically).

Q3: Difference between `$out` and `$merge`?
A3: `$out` overwrites the whole target collection. `$merge` upserts per document with `whenMatched`/`whenNotMatched` policies and can write into the same database/collection incrementally (e.g. daily rollups).

Q4: Can aggregation do everything mapReduce did?
A4: Yes: `$group` for per-key fold, `$bucket`/`$bucketAuto`, `$unwind`+`$group` for "emit many per doc" patterns, `$accumulator` for custom folds, `$function` for custom expressions.

Q5: Does an aggregation also have the 16 MB result limit?
A5: A single output *document* is limited to 16 MB (e.g., `$push` into one huge array fails), but the cursor returns any number of documents. `$merge`/`$out` write results without client transfer.

---

## 🔷 When to Use + When Not to Use
✅ Use aggregation when:
- Any new reporting/analytics/rollup logic (always)
- You need optimizer, indexes and readable stages

❌ Avoid mapReduce when:
- Writing anything new — it is deprecated
- Security policy disables server-side JavaScript

⚠️ Only touch mapReduce to read/maintain legacy code until migrated. For truly huge cross-system batch analytics consider Spark / the Atlas Data Federation rather than long pipelines.

---

## 📊 Visual Diagram
```
MAPREDUCE (legacy)                 AGGREGATION (modern)
──────────────────                 ────────────────────
 docs ─► map() emit(k,v)           docs ─► $match (index)
          │                                  │
          ▼                                  ▼
     group by key                      $group { $sum, $avg, ... }
          │                                  │
          ▼                                  ▼
   reduce(k, values[])                 $sort / $limit
          │                                  │
          ▼                                  ▼
  out: inline / collection            $merge / $out / cursor
  (JS engine, slow)                   (native C++, optimized)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| map | Emits key/value per document | हर doc पर key/value emit |
| reduce | Folds values of one key | एक key के values fold |
| `$group` | Native grouping stage | Native grouping stage |
| `$merge` | Write results into a collection (upsert) | Result को collection में लिखना |
| `$out` | Replace a whole collection with results | पूरी collection replace |
| `$accumulator` | Custom JS accumulator in `$group` | Custom JS accumulator |
| Deprecated | Still works, scheduled for removal | अभी चलता है, हटने वाला है |

---

## ⚡ 3-Line Summary
English:
1. MapReduce (JS map/reduce functions) is deprecated since MongoDB 5.0; the aggregation pipeline does everything faster with native operators.
2. Replace `out` with `$merge`/`$out`, per-key folds with `$group`, and custom logic with `$accumulator`/`$function` only if needed.
3. Never write new mapReduce; migrate legacy jobs, keeping reduce's "same shape" rule in mind while doing so.

Hindi:
1. MapReduce (JS map/reduce functions) MongoDB 5.0 से deprecated है; aggregation pipeline native operators से सब कुछ तेज़ करती है।
2. `out` की जगह `$merge`/`$out`, per-key fold की जगह `$group`, और custom logic के लिए सिर्फ़ ज़रूरत पर `$accumulator`/`$function`।
3. नया mapReduce कभी मत लिखो; legacy jobs migrate करो, और reduce का "same shape" नियम याद रखो।

---

## ➡️ Next Topic
**69. Schema Design Philosophy — Model for Access Patterns** — design the document shape from how your app reads and writes, not from entities.
