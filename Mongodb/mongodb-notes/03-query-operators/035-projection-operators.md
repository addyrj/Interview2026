# 35. Projection Operators ($slice, $elemMatch)
# हिंदी में: Projection Operators ($slice, $elemMatch)

---

## 🔵 Simple Definition (English)
**Projection** decides which fields come back from `find()`. **Projection operators** shape **array** fields in the result: **`$slice`** returns the first N, last N, or a window (`[skip, limit]`) of an array; **`$elemMatch`** (projection form) returns only the **first array element that matches** a condition; and the positional **`"arr.$"`** returns the first element that matched the **query filter**. They change only what is *returned*, never what is *stored*.

## 🔵 सरल परिभाषा (Hindi)
**Projection** तय करता है कि `find()` से कौन-सी fields वापस आएँ। **Projection operators** result में **array** fields का आकार बदलते हैं: **`$slice`** array के पहले N, आख़िरी N या एक window (`[skip, limit]`) लौटाता है; **`$elemMatch`** (projection रूप) सिर्फ वो **पहला array element** लौटाता है जो condition से match करे; और positional **`"arr.$"`** वो पहला element लौटाता है जो **query filter** से match हुआ। ये सिर्फ *लौटाई जाने वाली* चीज़ बदलते हैं, *stored* data नहीं।

---

## 🔴 Problem it Solves
A product document may hold hundreds of comments or variants. The product page needs only the **latest 2 comments**, or only the **red variant**. Sending the whole 500-element array wastes network, memory and client parsing time (and may hit the 16 MB document ceiling in transit). Projection operators trim arrays **on the server** before they are sent.

## 🔴 यह क्यों बना? (Hindi)
Product document में सैकड़ों comments या variants हो सकते हैं। Product page को सिर्फ **आख़िरी 2 comments** या सिर्फ **red variant** चाहिए। पूरा 500-element array भेजने से network, memory और client parsing का समय बर्बाद होता है। Projection operators arrays को भेजने से पहले **server पर ही** छाँट देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **`$slice: n`** (positive) returns the **first n** elements; **`$slice: -n`** returns the **last n**.
Step 2 → **`$slice: [skip, limit]`** returns a window: skip first `skip` elements, then take `limit` (pagination inside an array).
Step 3 → `$slice` alone keeps **all other fields** (it behaves like an exclusion-style projection); combining it with inclusion (`t: 1`) returns `_id`, `t` and the sliced array.
Step 4 → **`{ arr: { $elemMatch: { cond } } }`** in the projection returns an array with **only the first element** satisfying `cond`. If none match, the field is **omitted**. It is independent of the filter.
Step 5 → **`{ "arr.$": 1 }`** returns the first element matched by the **query filter** on that same array. Only **one** positional projection per query is allowed.
Step 6 → Restrictions: you can't mix inclusion and exclusion (except `_id`), and a positional `$` projection can't be combined with another positional projection.
Step 7 → For **all** matching elements, or computed slices, use aggregation: `$filter`, `$slice`, `$arrayElemAt`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`$slice: n`** (धनात्मक) **पहले n** elements लौटाता है; **`$slice: -n`** **आख़िरी n**।
Step 2 → **`$slice: [skip, limit]`** एक window देता है: पहले `skip` elements छोड़ो, फिर `limit` लो (array के अंदर pagination)।
Step 3 → अकेला `$slice` **बाकी सभी fields** रखता है (exclusion-style projection जैसा); inclusion (`t: 1`) के साथ मिलाने पर `_id`, `t` और sliced array मिलते हैं।
Step 4 → Projection में **`{ arr: { $elemMatch: { cond } } }`** ऐसा array देता है जिसमें `cond` पूरी करने वाला **सिर्फ पहला element** हो। कोई match न हो तो field **हट जाती है**। यह filter से स्वतंत्र है।
Step 5 → **`{ "arr.$": 1 }`** उसी array पर **query filter** से match हुआ पहला element लौटाता है। एक query में सिर्फ **एक** positional projection की अनुमति है।
Step 6 → पाबंदियाँ: inclusion और exclusion मिला नहीं सकते (`_id` को छोड़कर), और positional `$` projection दूसरे positional projection के साथ नहीं चलता।
Step 7 → **सारे** matching elements या computed slices के लिए aggregation लो: `$filter`, `$slice`, `$arrayElemAt`।

---

## 🟡 Real World Example
**Flipkart product page**: `{ t: "Phone", comments: [c1..c500], variants: [ {c:"red",s:1}, {c:"blue",s:0}, {c:"red",s:5} ] }`. The listing page shows only the last 2 comments (`$slice: -2`). Comment pagination uses `$slice: [20, 10]`. The "red" swatch needs the first red variant (`$elemMatch` projection) without downloading all variants.

## 🟡 Real Example Hindi mein
**Flipkart product page**: `{ t: "Phone", comments: [c1..c500], variants: [ {c:"red",s:1}, {c:"blue",s:0}, {c:"red",s:5} ] }`। Listing page सिर्फ आख़िरी 2 comments दिखाता है (`$slice: -2`)। Comment pagination `$slice: [20, 10]` से होती है। "red" swatch को पहला red variant चाहिए (`$elemMatch` projection), सारे variants download किए बिना।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use flipkart_proj_demo                             // switch database
db.dropDatabase()                                  // clean start
db.p.insertOne({                                   // one product with arrays
  _id: 1, t: "Phone",
  comments: ["c1", "c2", "c3", "c4"],
  variants: [ { c: "red", s: 1 }, { c: "blue", s: 0 }, { c: "red", s: 5 } ]
})
const j = x => print(JSON.stringify(x))

// ---- $slice ----
j(db.p.find({}, { comments: { $slice: 2 } }).toArray())
// {"_id":1,"t":"Phone","comments":["c1","c2"],"variants":[...all three...]}   first 2; other fields kept

j(db.p.find({}, { comments: { $slice: -2 }, t: 1 }).toArray())
// [{"_id":1,"t":"Phone","comments":["c3","c4"]}]                              last 2, with inclusion of t

j(db.p.find({}, { comments: { $slice: [1, 2] }, _id: 0, t: 1 }).toArray())
// [{"t":"Phone","comments":["c2","c3"]}]                                      skip 1, take 2

// ---- $elemMatch (projection form): first element matching a condition ----
j(db.p.find({}, { variants: { $elemMatch: { c: "red" } }, _id: 0 }).toArray())
// [{"variants":[{"c":"red","s":1}]}]       only the FIRST red variant (the second red one is dropped)

j(db.p.find({}, { variants: { $elemMatch: { c: "green" } }, t: 1, _id: 0 }).toArray())
// [{"t":"Phone"}]                          no match -> the variants field is omitted entirely

// ---- positional "$": first element matched by the QUERY ----
j(db.p.find({ "variants.c": "red" }, { "variants.$": 1, _id: 0 }).toArray())
// [{"variants":[{"c":"red","s":1}]}]

// ---- Errors ----
db.p.find({}, { "comments.$": 1, "variants.$": 1 }).toArray()
// Error: Cannot specify more than one positional projection per query.
db.p.find({}, { t: 1, comments: 0 }).toArray()
// Error: Cannot do exclusion on field comments in inclusion projection
```

## 💻 Code Example — Advanced

```javascript
// Aggregation equivalents give MORE power than find-projection (mongosh)
db.p.aggregate([{ $project: {
  _id: 0,
  last: { $arrayElemAt: ["$comments", -1] },                                  // last comment as a scalar
  red:  { $filter: { input: "$variants", as: "v", cond: { $eq: ["$$v.c", "red"] } } } // ALL red variants
} }])
// Output: [ { last: 'c4', red: [ { c: 'red', s: 1 }, { c: 'red', s: 5 } ] } ]

db.p.aggregate([{ $project: { _id: 0, first2: { $slice: ["$comments", 2] } } }])
// Output: [ { first2: [ 'c1', 'c2' ] } ]

// Paginating an array: page 3 of size 10 => skip 20, take 10
db.p.find({ _id: 1 }, { comments: { $slice: [20, 10] } })
```

```javascript
// Node.js driver v6 — projection option on find()
const product = await db.collection('p').findOne(
  { _id: 1 },
  { projection: { t: 1, comments: { $slice: -2 } } }   // last two comments only
);
console.log(product);                                    // { _id: 1, t: 'Phone', comments: ['c3','c4'] }
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Product = mongoose.model('Product', new mongoose.Schema({ t: String, comments: [String], variants: [{ c: String, s: Number }] }));
const app = express();

// GET /products/:id?page=2&size=10  -> comment pagination with $slice
app.get('/products/:id', async (req, res) => {
  const page = Math.max(1, Number(req.query.page) || 1);          // 1-based page
  const size = Math.min(50, Number(req.query.size) || 10);        // cap page size
  const p = await Product.findById(req.params.id, {
    t: 1,
    comments: { $slice: [(page - 1) * size, size] }              // Mongoose passes $slice through
  }).lean();
  if (!p) return res.sendStatus(404);
  res.json(p);
});

// Mongoose select with $elemMatch
// Product.find().select({ variants: { $elemMatch: { c: 'red' } } })
```
In Mongoose, `.select('-comments')` removes a path, while `$slice` must be given as an object (`{ comments: { $slice: 5 } }`) or via `.slice('comments', 5)` on the query.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Expecting `$elemMatch` projection to return all matches
```javascript
db.p.find({}, { variants: { $elemMatch: { c: "red" } } })   // Wrong: only ONE red variant returned
db.p.aggregate([{ $project: { variants: { $filter: { input: "$variants", as: "v", cond: { $eq: ["$$v.c","red"] } } } } }]) // Right: both
```

❌ Mistake 2: Mixing inclusion and exclusion
```javascript
db.p.find({}, { t: 1, comments: 0 })                 // Wrong: error — cannot exclude in inclusion projection
db.p.find({}, { t: 1 })                              // Right (or only exclusions: { comments: 0 })
```

❌ Mistake 3: Using `$slice` and expecting a stored/filtered change
```javascript
// $slice in find() only trims the OUTPUT. To trim what is STORED use $push with $slice:
db.p.updateOne({ _id: 1 }, { $push: { comments: { $each: ["c5"], $slice: -100 } } }) // keep last 100
```

---

## 🧠 Tricky Interview Question

```javascript
db.p.find({}, { comments: { $slice: 1 }, t: 1, _id: 0 })
db.p.find({}, { comments: { $slice: 1 } })
```
Why do the two results differ in shape?

Answer: In MongoDB 4.4+, `$slice` with an **inclusion** projection (`t: 1`) returns only `t` and the sliced `comments` (real output `{"t":"Phone","comments":["c1"]}`); alone it behaves like exclusion — **all other fields are returned** along with the sliced array (`variants` and `t` appear). Also `$slice` and `$elemMatch` projections apply to what is returned, not to matching: the filter still examines the full array.

---

## ⚫ Interview Questions + Answers

Q1: What are the forms of `$slice` in projection?
A1: `$slice: n` (first n), `$slice: -n` (last n), `$slice: [skip, limit]` (window).

Q2: Difference between `$elemMatch` in the query and in the projection?
A2: In the query it filters which **documents** are returned (some element satisfies all conditions). In the projection it limits which **elements** of the array are returned (first matching one).

Q3: What does the positional `$` projection return?
A3: The first array element matched by the query condition on that array. It requires the array field in the filter, and only one positional projection per query.

Q4: How can you get all matching elements?
A4: Aggregation: `$filter` in `$project`/`$addFields`, or `$unwind` then `$match`.

Q5: How can you keep an array at a fixed maximum size in storage?
A5: Use `$push` with `$each` and `$slice` (e.g. `$slice: -100` keeps the latest 100), optionally with `$sort`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Previewing large arrays (latest comments, first photos).
- Paging inside an array.
- Returning one selected element of an array of subdocuments.

❌ Avoid when:
- You need all matches or computed fields — use aggregation `$filter`/`$slice`.
- Arrays are big enough to need real pagination and independent querying — use a separate collection.
- You expect it to reduce **work** on the server — it only reduces the data **sent**.

---

## 📊 Visual Diagram
```
 comments: [ c1 , c2 , c3 , c4 ]
   $slice: 2        -> [ c1 c2 ]
   $slice: -2       -> [ c3 c4 ]
   $slice: [1,2]    -> [ c2 c3 ]       (skip 1, take 2)

 variants: [ red(1) , blue(0) , red(5) ]
   $elemMatch {c:"red"}  -> [ red(1) ]         first match only
   "variants.$" (filter c=red) -> [ red(1) ]
   aggregation $filter   -> [ red(1) , red(5) ] all matches
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Projection | Choose returned fields | लौटने वाली fields चुनना |
| `$slice` | First/last/window of an array | Array के पहले/आख़िरी/window elements |
| `$elemMatch` (projection) | First element matching a condition | Condition से match होने वाला पहला element |
| `arr.$` | First element matched by query | Query से match हुआ पहला element |
| `$filter` | All matching elements (aggregation) | सारे matching elements (aggregation) |
| Inclusion/Exclusion | Whitelist vs blacklist of fields | Fields की whitelist बनाम blacklist |

---

## ⚡ 3-Line Summary
English:
1. `$slice` trims arrays to first/last N or a window; `$elemMatch` and `arr.$` return only the first matching element.
2. These shape the returned data only and cannot be mixed with exclusions in an inclusion projection.
3. For all matches or computed trimming, use aggregation `$filter`/`$slice`; to cap stored size use `$push` with `$slice`.

Hindi:
1. `$slice` arrays को पहले/आख़िरी N या window तक छाँटता है; `$elemMatch` और `arr.$` सिर्फ पहला matching element लौटाते हैं।
2. ये सिर्फ लौटाया गया data बदलते हैं और inclusion projection में exclusion के साथ नहीं मिलते।
3. सारे matches या computed trimming के लिए aggregation `$filter`/`$slice` लो; stored size सीमित करने के लिए `$push` के साथ `$slice` इस्तेमाल करो।

---

## ➡️ Next Topic
**36. Text Search ($text) and Text Indexes** — stemming, stop words, relevance scoring and phrase search.
