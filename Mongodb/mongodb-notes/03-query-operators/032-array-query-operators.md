# 32. Array Query Operators ($all, $elemMatch, $size)
# हिंदी में: Array Query Operators ($all, $elemMatch, $size)

---

## 🔵 Simple Definition (English)
Array query operators filter documents based on the **contents or length of an array field**. **`$all`** matches arrays that contain **every** listed value (in any order, extra elements allowed). **`$elemMatch`** matches arrays where **at least one single element** satisfies **all** the given conditions together. **`$size`** matches arrays of an **exact length**. Plain equality on an array field (`{ tags: "veg" }`) already means "the array contains `veg`".

## 🔵 सरल परिभाषा (Hindi)
Array query operators document को array field की **contents या length** के आधार पर filter करते हैं। **`$all`** उन arrays से match करता है जिनमें दी गई **हर** value हो (किसी भी क्रम में, extra elements चलते हैं)। **`$elemMatch`** उन arrays से match करता है जहाँ **कम से कम एक ही element** दी गई **सारी** conditions एक साथ पूरी करे। **`$size`** **ठीक उतनी length** वाले arrays से match करता है। Array field पर साधारण equality (`{ tags: "veg" }`) का मतलब पहले से "array में `veg` है" होता है।

---

## 🔴 Problem it Solves
Arrays behave differently from scalars in queries. `{ ratings: { $gt: 4, $lt: 5 } }` does **not** mean "a rating between 4 and 5" — different elements can satisfy each condition. Matching "has both `biryani` AND `spicy` tags" needs more than `$in` (which means OR). And there is no way to ask "exactly 2 tags" with comparison operators. These three operators fix those gaps.

## 🔴 यह क्यों बना? (Hindi)
Queries में arrays scalars से अलग व्यवहार करते हैं। `{ ratings: { $gt: 4, $lt: 5 } }` का मतलब "4 और 5 के बीच की rating" **नहीं** है — अलग-अलग elements हर condition पूरी कर सकते हैं। "`biryani` AND `spicy` दोनों tags हैं" के लिए `$in` (जो OR है) काफ़ी नहीं। और "ठीक 2 tags" पूछने का comparison operators से कोई तरीका नहीं। ये तीन operators यही कमियाँ भरते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Equality on an array**: `{ tags: "biryani" }` is true if **any element equals** `"biryani"`. `{ tags: ["biryani","spicy"] }` (an array literal) requires an **exact** array: same elements, same order, nothing else.
Step 2 → **`$in`** = at least one of the listed values is in the array (OR). **`$all`** = every listed value is in the array (AND, order ignored).
Step 3 → **Multiple conditions on one array field** (`$gt` and `$lt`) are each checked against **any** element, possibly different ones. To force the **same element**, wrap in **`$elemMatch`**.
Step 4 → **`$elemMatch`** also works on arrays of subdocuments: `{ items: { $elemMatch: { sku: "a", qty: { $gt: 2 } } } }`.
Step 5 → **`$size: n`** needs a **number** (not `{ $gt: 1 }`). For "length greater than n", use `$expr` with the aggregation `$size`, or store a counter field, or test `"tags.2": { $exists: true }` (has at least 3 elements).
Step 6 → `$size` cannot use an index to satisfy the size itself; `$all`/`$elemMatch` can use multikey indexes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Array पर equality**: `{ tags: "biryani" }` तब true है जब **कोई भी element** `"biryani"` हो। `{ tags: ["biryani","spicy"] }` (array literal) **ठीक वही** array माँगता है: वही elements, वही क्रम, और कुछ नहीं।
Step 2 → **`$in`** = दी गई values में से कम से कम एक array में है (OR)। **`$all`** = दी गई हर value array में है (AND, क्रम मायने नहीं)।
Step 3 → **एक array field पर कई conditions** (`$gt` और `$lt`) हर एक **किसी भी** element पर जाँची जाती है, शायद अलग-अलग पर। **एक ही element** पर लागू करवाने के लिए **`$elemMatch`** में लपेटो।
Step 4 → **`$elemMatch`** subdocuments के arrays पर भी चलता है: `{ items: { $elemMatch: { sku: "a", qty: { $gt: 2 } } } }`।
Step 5 → **`$size: n`** को **number** चाहिए (`{ $gt: 1 }` नहीं)। "length n से ज़्यादा" के लिए `$expr` + aggregation `$size`, या counter field, या `"tags.2": { $exists: true }` (कम से कम 3 elements) इस्तेमाल करो।
Step 6 → `$size` की length index से satisfy नहीं होती; `$all`/`$elemMatch` multikey indexes इस्तेमाल कर सकते हैं।

---

## 🟡 Real World Example
**Zomato restaurant filters**: each restaurant has `tags: ["biryani","spicy","nonveg"]` and `ratings: [4,5,3]`. "Show restaurants that are both **biryani and spicy**" -> `$all`. "Restaurants that have **a single rating of exactly 4 or more but below 5**" -> `$elemMatch`. "Restaurants with **no ratings yet**" -> `$size: 0`. "Exactly 2 cuisine tags" -> `$size: 2`.

## 🟡 Real Example Hindi mein
**Zomato restaurant filters**: हर restaurant में `tags: ["biryani","spicy","nonveg"]` और `ratings: [4,5,3]` होते हैं। "**biryani और spicy दोनों** वाले restaurants" -> `$all`। "ऐसे restaurants जिनकी **कोई एक rating 4 या उससे ज़्यादा पर 5 से कम** हो" -> `$elemMatch`। "जिनकी **अभी कोई rating नहीं**" -> `$size: 0`। "ठीक 2 cuisine tags" -> `$size: 2`।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use zomato_arr_demo                                // switch database
db.dropDatabase()                                  // clean start
db.r.insertMany([                                  // four restaurants
  { _id: 1, n: "Meghana",  tags: ["biryani","spicy","nonveg"], ratings: [4,5,3] },
  { _id: 2, n: "Paradise", tags: ["biryani","hyderabadi"],      ratings: [5,5]   },
  { _id: 3, n: "Veg",      tags: ["veg","spicy"],               ratings: []      },
  { _id: 4, n: "Odd",      tags: "biryani",                     ratings: [2]     } // tags is a plain string here!
])
const ids = q => print(JSON.stringify(db.r.find(q).toArray().map(x => x._id)))

ids({ tags: "biryani" })                           // [1,2,4]  contains biryani (also matches the scalar string)
ids({ tags: { $all: ["biryani","spicy"] } })       // [1]      has BOTH
ids({ tags: ["biryani","spicy"] })                 // []       EXACT array literal: nobody has exactly these two
ids({ tags: { $in: ["veg","spicy"] } })            // [1,3]    has AT LEAST ONE (OR)

ids({ tags: { $size: 2 } })                        // [2,3]    exactly 2 elements (scalar doc 4 never matches $size)
ids({ tags: { $size: 0 } })                        // []
ids({ ratings: { $size: 0 } })                     // [3]      empty array

// The classic trap: conditions on DIFFERENT elements
ids({ ratings: { $gt: 4, $lt: 5 } })               // [1]      [4,5,3]: 5 > 4 AND 4 < 5 — two different elements!
ids({ ratings: { $elemMatch: { $gt: 4, $lt: 5 } } })// []      no single rating is strictly between 4 and 5
ids({ ratings: { $elemMatch: { $gte: 5 } } })      // [1,2]    some rating >= 5
ids({ "ratings.0": 5 })                            // [2]      first rating is 5 (positional dot notation)
ids({ ratings: { $all: [5, 4] } })                 // [1]      contains both 5 and 4

// $size does NOT take operators
db.r.find({ ratings: { $size: { $gt: 1 } } }).toArray()
// Error: Failed to parse $size. Expected a number in: $size: { $gt: 1 }

// "more than 2 ratings" workaround with $expr
db.r.find({ $expr: { $gt: [ { $size: { $ifNull: ["$ratings", []] } }, 2 ] } }).toArray().map(x => x._id)
// Output: [ 1 ]
```

## 💻 Code Example — Advanced

```javascript
// $elemMatch on arrays of subdocuments (mongosh)
db.s.insertMany([
  { _id: 1, items: [ { sku: "a", qty: 5 }, { sku: "b", qty: 1 } ] },
  { _id: 2, items: [ { sku: "a", qty: 1 }, { sku: "b", qty: 5 } ] }
])
ids2 = q => print(JSON.stringify(db.s.find(q).toArray().map(x => x._id)))

ids2({ items: { $elemMatch: { sku: "a", qty: { $gt: 2 } } } })   // [1]    ONE element is sku a AND qty > 2
ids2({ "items.sku": "a", "items.qty": { $gt: 2 } })              // [1,2]  separate elements may satisfy each! (trap)

// $all combined with $elemMatch: need an item a (any qty) AND an item b with qty 5
ids2({ items: { $all: [ { $elemMatch: { sku: "a" } }, { $elemMatch: { sku: "b", qty: 5 } } ] } }) // [2]

// Indexing: multikey index supports $all / $elemMatch on the first listed value
db.r.createIndex({ tags: 1 })                                      // becomes a multikey index automatically
```

```javascript
// Node.js driver v6 — filter restaurants by many tags
const wanted = ['biryani', 'spicy'];                 // from query string
const rows = await db.collection('r').find({
  tags: { $all: wanted },                            // must have all tags
  ratings: { $elemMatch: { $gte: 4 } }               // and at least one rating >= 4
}, { projection: { n: 1, _id: 0 } }).toArray();
console.log(rows);                                   // [{ n: 'Meghana' }]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Restaurant = mongoose.model('Restaurant', new mongoose.Schema({ n: String, tags: [String], ratings: [Number] }));
const app = express();

// GET /restaurants?tags=biryani,spicy&minRating=4
app.get('/restaurants', async (req, res) => {
  const filter = {};
  if (req.query.tags) filter.tags = { $all: String(req.query.tags).split(',') }; // AND of tags
  if (req.query.minRating) filter.ratings = { $elemMatch: { $gte: Number(req.query.minRating) } };
  res.json(await Restaurant.find(filter).select('n -_id').lean());
});
```
Mongoose declares `tags: [String]` as an array path, so `$all`, `$elemMatch` and `$size` values are cast per element type. Remember a schema-less value like our `_id: 4` (a string where an array is expected) will fail Mongoose casting on save.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `$gt` + `$lt` on an array and expecting one element to satisfy both
```javascript
db.r.find({ ratings: { $gt: 4, $lt: 5 } })              // Wrong: [1] matches (5>4 and 4<5 on different elements)
db.r.find({ ratings: { $elemMatch: { $gt: 4, $lt: 5 } } }) // Right: []
```

❌ Mistake 2: `$in` when you mean "all"
```javascript
db.r.find({ tags: { $in: ["biryani","spicy"] } })       // Wrong: biryani OR spicy -> [1,2,3,4]
db.r.find({ tags: { $all: ["biryani","spicy"] } })      // Right: both -> [1]
```

❌ Mistake 3: Putting an operator inside `$size`
```javascript
db.r.find({ ratings: { $size: { $gt: 1 } } })           // Wrong: error "Expected a number"
db.r.find({ "ratings.1": { $exists: true } })           // Right: at least 2 elements
```

---

## 🧠 Tricky Interview Question

```javascript
db.s.find({ "items.sku": "a", "items.qty": { $gt: 2 } })
db.s.find({ items: { $elemMatch: { sku: "a", qty: { $gt: 2 } } } })
```
Document 2 is `items: [ {sku:"a", qty:1}, {sku:"b", qty:5} ]`. Is it returned by each?

Answer: **First: yes. Second: no.** In the first query each condition may be satisfied by a **different** element (`sku:"a"` by element 0, `qty > 2` by element 1). In the second, `$elemMatch` forces both conditions onto the **same** element. Real output: first `[1,2]`, second `[1]`.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `$in` and `$all`?
A1: `$in` matches if the field equals/contains **any** listed value (OR). `$all` requires the array to contain **every** listed value (AND), regardless of order and extra elements.

Q2: When is `$elemMatch` necessary?
A2: When two or more conditions must hold for the **same array element**, especially on arrays of subdocuments.

Q3: Can `$size` compare lengths (`> 3`)?
A3: No, it accepts only an exact number. Use `$expr` with `{ $gt: [{ $size: "$arr" }, 3] }`, an `"arr.3": {$exists:true}` check, or maintain a counter field.

Q4: What does `{ tags: ["a","b"] }` (array literal) do?
A4: It matches documents whose `tags` is exactly `["a","b"]` (same order, same length), or arrays that contain that array as an element. It is not "contains a and b" — that is `$all`.

Q5: Do array operators use indexes?
A5: A multikey index (one entry per element) supports equality, `$all` and `$elemMatch` (on the first/most selective value). `$size` can't use an index for the length.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Tag/category filtering with AND semantics (`$all`).
- Multi-condition checks on one subdocument element (`$elemMatch`).
- Validating or finding exact-length arrays (`$size`), such as empty carts.

❌ Avoid when:
- Arrays grow unbounded (comments, logs) — model as separate documents.
- You need "length greater than N" frequently — store `count` and index it.
- Using `$size` on large collections without another selective filter.

---

## 📊 Visual Diagram
```
 tags: ["biryani","spicy","nonveg"]
   {tags:"spicy"}                      -> contains         ✔
   {tags:{$all:["spicy","biryani"]}}   -> both (any order) ✔
   {tags:{$in:["veg","spicy"]}}        -> at least one     ✔
   {tags:{$size:3}}                    -> exact length 3   ✔
   {tags:["spicy","biryani"]}          -> exact array      ✖ (order/length differ)

 items: [ {sku:a,qty:1}, {sku:b,qty:5} ]
   "items.sku":a , "items.qty":>2     -> different elements OK   ✔ (trap)
   $elemMatch{ sku:a , qty:>2 }       -> SAME element required   ✖
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$all` | Array contains all values | Array में सभी values हैं |
| `$elemMatch` | One element meets all conditions | एक element सारी conditions पूरी करे |
| `$size` | Exact array length | Array की ठीक length |
| `$in` | Matches any of the values | किसी एक value से match |
| Multikey index | Index with an entry per array element | हर element के लिए entry वाला index |
| Dot-position (`arr.0`) | Access a specific array index | Array के specific index तक पहुँच |

---

## ⚡ 3-Line Summary
English:
1. `$all` = contains every value, `$in` = contains any value, `$size` = exact length, `$elemMatch` = one element meets all conditions.
2. Separate conditions on an array can be met by different elements — use `$elemMatch` to bind them to one.
3. `$size` accepts only a number; use `$expr` or a counter field for "greater than" length checks.

Hindi:
1. `$all` = हर value मौजूद, `$in` = कोई एक value मौजूद, `$size` = ठीक लंबाई, `$elemMatch` = एक element सारी conditions पूरी करे।
2. Array पर अलग conditions अलग elements से पूरी हो सकती हैं — उन्हें एक element से बाँधने के लिए `$elemMatch` लो।
3. `$size` सिर्फ number लेता है; "से बड़ी" length के लिए `$expr` या counter field इस्तेमाल करो।

---

## ➡️ Next Topic
**33. Querying Nested Documents + Dot Notation** — reaching into embedded objects with `"address.city"` and the exact-match trap.
