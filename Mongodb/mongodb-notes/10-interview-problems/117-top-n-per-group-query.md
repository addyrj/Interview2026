# 117. Top N per Group Query
# हिंदी में: हर Group में Top N निकालना

---

## 🔵 Simple Definition (English)
**Top N per group** means: for every category (restaurant, city, department) return only the best N documents ("top 2 dishes per cuisine", "3 highest-paid per team"). A plain `$limit` gives N rows for the *whole* collection, not per group, so you need group-aware stages: `$group` with **`$topN` / `$firstN`** (MongoDB 5.2+), or **`$setWindowFields`** with `$rank`/`$denseRank` (5.0+), or the classic *sort → group → `$push` → `$slice`* pattern.

## 🔵 सरल परिभाषा (Hindi)
**Top N per group** का मतलब: हर category (restaurant, शहर, department) के लिए सिर्फ सबसे अच्छे N documents लौटाना ("हर cuisine के top 2 dishes", "हर team के 3 सबसे ज़्यादा salary वाले")। सादा `$limit` पूरे collection के N rows देता है, हर group के नहीं, इसलिए group-aware stages चाहिए: `$group` के साथ **`$topN` / `$firstN`** (MongoDB 5.2+), या `$rank`/`$denseRank` के साथ **`$setWindowFields`** (5.0+), या पुराना *sort → group → `$push` → `$slice`* pattern।

---

## 🔴 Problem it Solves
"Show the top-rated 2 dishes in every category" is a daily need on menus, leaderboards and dashboards. Fetching all documents and trimming in application code wastes network and memory; running one query per category (N+1 queries) is slow and doesn't scale as categories grow. The aggregation pipeline lets the database do it in one round trip — but the naive `$sort` + `$limit` returns just the global top N, which is the most common wrong answer in interviews.

## 🔴 यह क्यों बना? (Hindi)
"हर category की top-rated 2 dishes दिखाओ" menus, leaderboards और dashboards में रोज़ की ज़रूरत है। सारे documents लाकर application code में काटना network और memory बर्बाद करता है; हर category के लिए अलग query (N+1) धीमी है और categories बढ़ने पर scale नहीं करती। Aggregation pipeline यह काम एक ही round trip में database में कर देती है — लेकिन naive `$sort` + `$limit` सिर्फ global top N देता है, जो interview में सबसे आम गलत जवाब है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Understand the data**: `products { name, cat, price, rating }`. Goal: best 2 by `rating` in each `cat`.
Step 2 → **Option A — `$topN`** (5.2+): `$group: { _id: "$cat", top: { $topN: { n: 2, sortBy: { rating: -1 }, output: {...} } } }`. One stage, no pre-sort, and the server keeps only N items per group in memory.
Step 3 → **Option B — `$firstN`**: first `$sort` the whole input, then `$group` with `$firstN: { n: 2, input: "$name" }` — it takes the first N in arrival order. Needs the sort before the group.
Step 4 → **Option C — window functions** (5.0+): `$setWindowFields` with `partitionBy: "$cat"`, `sortBy: { rating: -1 }`, `output: { rank: { $denseRank: {} } }`, then `$match: { rank: { $lte: 2 } }`. This keeps full documents and handles **ties** (equal ratings share a rank).
Step 5 → **Option D — legacy** (any version): `$sort` → `$group` with `$push` → `$project` with `$slice: ["$items", 2]`. Works everywhere but builds each group's full array first (16 MB risk, wasteful).
Step 6 → **Add a tie-breaker** (`name` or `_id`) to the sort for deterministic output.
Step 7 → **Performance**: a `$match` first reduces input; an index on `{ cat: 1, rating: -1 }` can support the sort for the `$firstN` approach.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Data समझो**: `products { name, cat, price, rating }`। लक्ष्य: हर `cat` में `rating` के हिसाब से सबसे अच्छे 2।
Step 2 → **Option A — `$topN`** (5.2+): `$group: { _id: "$cat", top: { $topN: { n: 2, sortBy: { rating: -1 }, output: {...} } } }`। एक ही stage, पहले sort की ज़रूरत नहीं, और server हर group के सिर्फ N items memory में रखता है।
Step 3 → **Option B — `$firstN`**: पहले पूरे input को `$sort` करो, फिर `$group` में `$firstN: { n: 2, input: "$name" }` — यह आने के क्रम में पहले N लेता है। Group से पहले sort ज़रूरी है।
Step 4 → **Option C — window functions** (5.0+): `partitionBy: "$cat"`, `sortBy: { rating: -1 }`, `output: { rank: { $denseRank: {} } }` के साथ `$setWindowFields`, फिर `$match: { rank: { $lte: 2 } }`। इसमें पूरा document रहता है और **ties** (बराबर rating = बराबर rank) संभलते हैं।
Step 5 → **Option D — legacy** (हर version): `$sort` → `$push` वाला `$group` → `$slice: ["$items", 2]` वाला `$project`। हर जगह चलता है पर हर group का पूरा array पहले बनाता है (16 MB risk, बर्बादी)।
Step 6 → Sort में **tie-breaker** (`name` या `_id`) जोड़ो ताकि output deterministic रहे।
Step 7 → **Performance**: पहले `$match` input घटाता है; `$firstN` वाले तरीके में `{ cat: 1, rating: -1 }` index sort को support कर सकता है।

---

## 🟡 Real World Example
**Zomato's "Top dishes in each cuisine"** carousel: dishes have a `cuisine` and `rating`. Home-page code needs the 2 best dishes for *every* cuisine in a single query. Likewise **Flipkart** shows "top 3 bestsellers per category", and **Razorpay's** dashboard shows the 5 largest transactions per merchant. All are "Top N per group".

## 🟡 Real Example Hindi mein
**Zomato का "हर cuisine के Top dishes"** carousel: dishes में `cuisine` और `rating` होती है। Home-page को *हर* cuisine की 2 सबसे अच्छी dishes एक ही query में चाहिए। इसी तरह **Flipkart** "हर category के top 3 bestsellers" दिखाता है, और **Razorpay** का dashboard हर merchant के 5 सबसे बड़े transactions। सब "Top N per group" हैं।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("menu");
db.products.insertMany([
  { name: "Biryani", cat: "main",    price: 300, rating: 4.5 },
  { name: "Dal",     cat: "main",    price: 150, rating: 4.1 },
  { name: "Paneer",  cat: "main",    price: 250, rating: 4.8 },
  { name: "Kheer",   cat: "dessert", price: 90,  rating: 4.0 },
  { name: "Jalebi",  cat: "dessert", price: 80,  rating: 4.7 },
  { name: "Gulab",   cat: "dessert", price: 70,  rating: 4.7 }
]);

// WRONG answer people give: gives top 2 of the WHOLE collection, not per category
db.products.aggregate([{ $sort: { rating: -1 } }, { $limit: 2 }]);

// RIGHT: $topN per group (MongoDB 5.2+) — best 2 by rating, ties broken by name
db.products.aggregate([
  { $group: {
      _id: "$cat",                                       // one output doc per category
      top: { $topN: {
          n: 2,                                          // keep only 2 per group
          sortBy: { rating: -1, name: 1 },               // best rating first, then name A-Z
          output: { name: "$name", rating: "$rating" }   // what to return for each item
      } }
  } },
  { $sort: { _id: 1 } }                                  // sort groups for stable output
]);
// Output (JSON):
// [ { _id: "dessert", top: [ { name: "Gulab",  rating: 4.7 }, { name: "Jalebi", rating: 4.7 } ] },
//   { _id: "main",    top: [ { name: "Paneer", rating: 4.8 }, { name: "Biryani", rating: 4.5 } ] } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — three more ways, same data, tested on MongoDB 8.0.4

// B) $sort + $firstN: sort the input first, then take the first 2 names per group
db.products.aggregate([
  { $sort: { cat: 1, rating: -1, name: 1 } },            // order inside each cat
  { $group: { _id: "$cat", top: { $firstN: { n: 2, input: "$name" } } } },
  { $sort: { _id: 1 } }
]);
// Output: [ { _id: 'dessert', top: ['Gulab','Jalebi'] }, { _id: 'main', top: ['Paneer','Biryani'] } ]

// C) Window function: keeps WHOLE documents and gives you the rank
db.products.aggregate([
  { $setWindowFields: {
      partitionBy: "$cat",                               // restart ranking for each category
      sortBy: { rating: -1 },                            // rank by rating, best first
      output: { rank: { $denseRank: {} } }               // 1,1,2 for ties (no gaps)
  } },
  { $match: { rank: { $lte: 2 } } },                     // keep ranks 1 and 2 (ties may give > 2 rows!)
  { $project: { _id: 0, name: 1, cat: 1, rating: 1, rank: 1 } },
  { $sort: { cat: 1, rank: 1, name: 1 } }
]);
// Output: dessert/Gulab 4.7 rank1, dessert/Jalebi 4.7 rank1, dessert/Kheer 4.0 rank2,
//         main/Paneer 4.8 rank1, main/Biryani 4.5 rank2
// NOTE: dessert returned 3 rows because two items tie at rank 1 and Kheer is rank 2.
// Use $rowNumber (or $documentNumber) instead of $denseRank for EXACTLY N rows per group.

// D) Legacy pattern for old servers: push all, then $slice
db.products.aggregate([
  { $sort: { cat: 1, rating: -1, name: 1 } },
  { $group: { _id: "$cat", items: { $push: "$name" } } },
  { $project: { top: { $slice: ["$items", 2] } } },
  { $sort: { _id: 1 } }
]);
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();

const Product = mongoose.model('Product', new mongoose.Schema({
  name: String, cat: String, price: Number, rating: Number,
}));

// GET /api/top-dishes?n=2 — top N dishes per category
app.get('/api/top-dishes', async (req, res) => {
  // validate n: it is user input going into the pipeline
  const n = Math.min(Math.max(parseInt(req.query.n) || 2, 1), 10);
  const result = await Product.aggregate([
    { $match: { rating: { $gte: 1 } } },                       // filter first = less work
    { $group: { _id: '$cat', top: { $topN: {
        n, sortBy: { rating: -1, name: 1 }, output: { name: '$name', rating: '$rating' } } } } },
    { $sort: { _id: 1 } },
  ]);
  res.json(result);
});
// Mongoose does NOT cast inside aggregate(); numbers like n must be parsed by you.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: `$sort` + `$limit` for per-group results
```javascript
// Wrong — returns the 2 best items overall
db.products.aggregate([{ $sort: { rating: -1 } }, { $limit: 2 }]);

// Right — $group with $topN, which limits PER group
db.products.aggregate([{ $group: { _id: "$cat", top: { $topN: { n: 2, sortBy: { rating: -1 }, output: "$name" } } } }]);
```

❌ Mistake 2: Using `$firstN` without sorting first
✅ Correct: `$firstN` takes the first N *in pipeline order*, which is not guaranteed without a preceding `$sort`. `$topN` carries its own `sortBy`, so it is safer.

❌ Mistake 3: Using `$rank`/`$denseRank` and expecting exactly N rows
✅ Correct: ties produce more than N rows; use `$rowNumber` or `$documentNumber` for an exact N, and add a tie-breaker sort key.

❌ Mistake 4: Running on MongoDB < 5.2 and getting "Unrecognized expression $topN"
✅ Correct: use the `$push` + `$slice` legacy pattern (or window functions on 5.0+).

---

## 🧠 Tricky Interview Question

```javascript
// Gulab 4.7, Jalebi 4.7, Kheer 4.0 are desserts. "Top 2 per category" using
// $denseRank <= 2 returns how many dessert rows? And with $topN n:2?
```
Answer: `$denseRank` gives Gulab=1, Jalebi=1, Kheer=2, so `rank <= 2` returns **3** rows. `$topN` with `n: 2` returns exactly **2** (Gulab and Jalebi, deterministic because of the `name` tie-breaker). Which one is right depends on the business rule: "ties share a place" (rank) vs "exactly N items" (topN/rowNumber). Mention the choice explicitly.

---

## ⚫ Interview Questions + Answers

Q1: How do you get the top N documents per group in MongoDB?
A1: `$group` by the group key with the `$topN` accumulator (5.2+), or `$setWindowFields` with partitionBy + rank and then `$match`, or on old versions `$sort` → `$group` + `$push` → `$slice`.

Q2: Difference between `$topN` and `$firstN`?
A2: `$firstN` returns the first N values in the current document order (so you must `$sort` earlier); `$topN` specifies its own `sortBy` and returns the top N by that order, with an `output` expression. Both keep only N per group in memory.

Q3: `$rank` vs `$denseRank` vs `$rowNumber`?
A3: With scores 10, 10, 8: `$rank` -> 1,1,3 (gaps), `$denseRank` -> 1,1,2 (no gaps), `$rowNumber` -> 1,2,3 (unique). For "exactly N", use `$rowNumber`.

Q4: How do you make it fast on large data?
A4: `$match` early, project only needed fields, an index supporting the sort (`{ cat: 1, rating: -1 }`) for `$sort` + `$firstN`, and use `allowDiskUse` only as a last resort. `$topN` avoids building whole arrays.

Q5: What is the drawback of the `$push` + `$slice` approach?
A5: It collects every document of a group into an array first (memory heavy; a group can hit the 16 MB document cap) just to throw most of them away.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Dashboards/carousels need "best N" for many groups in a single round trip
- You can express ordering with a deterministic sort key (rating + tie-breaker)

❌ Avoid when:
- You only need a single group's top N: a simple indexed `find().sort().limit(n)` is faster
- Results are needed in real time on huge data: precompute and store per-group top lists (materialized view / `$merge`)

---

## 📊 Visual Diagram
```
TOP 2 PER CATEGORY
──────────────────────────────────────────────────────
 products                      $group by cat + $topN(n:2, sortBy rating desc)
 ┌────────┬─────────┬──────┐
 │ Biryani│ main    │ 4.5  │──┐
 │ Dal    │ main    │ 4.1  │  ├─► main    : [ Paneer 4.8, Biryani 4.5 ]
 │ Paneer │ main    │ 4.8  │──┘   (Dal dropped)
 │ Kheer  │ dessert │ 4.0  │──┐
 │ Jalebi │ dessert │ 4.7  │  ├─► dessert : [ Gulab 4.7, Jalebi 4.7 ]
 │ Gulab  │ dessert │ 4.7  │──┘   (Kheer dropped)
 └────────┴─────────┴──────┘
 WRONG: $sort + $limit 2  → [Paneer, Jalebi/Gulab]  (global top 2)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| $topN | Top N per group with own sort | अपने sort के साथ हर group के top N |
| $firstN | First N in current order | मौजूदा क्रम में पहले N |
| $setWindowFields | Window functions over partitions | Partitions पर window functions |
| $denseRank | Rank without gaps, ties share | बिना gap का rank, ties बराबर |
| $rowNumber | Unique sequential number | अलग-अलग क्रम संख्या |
| partitionBy | Group key for a window | Window का group key |
| Tie-breaker | Extra sort key for determinism | Deterministic क्रम के लिए अतिरिक्त sort key |

---

## ⚡ 3-Line Summary
English:
1. `$sort` + `$limit` gives global top N; for per-group use `$group` with `$topN` (5.2+) or window functions (5.0+).
2. `$firstN` needs a prior `$sort`; `$denseRank` can return more than N rows on ties, `$rowNumber` gives exactly N.
3. Always add a tie-breaker and `$match` early; on very old servers use `$push` + `$slice`.

Hindi:
1. `$sort` + `$limit` global top N देता है; per-group के लिए `$group` में `$topN` (5.2+) या window functions (5.0+) लो।
2. `$firstN` से पहले `$sort` चाहिए; ties पर `$denseRank` N से ज़्यादा rows दे सकता है, `$rowNumber` ठीक N देता है।
3. हमेशा tie-breaker जोड़ो और `$match` पहले लगाओ; बहुत पुराने servers पर `$push` + `$slice` इस्तेमाल करो।

---

## ➡️ Next Topic
**118. Find Duplicate Documents** — detect, remove and prevent duplicates with `$group`, `$push` and unique indexes.
