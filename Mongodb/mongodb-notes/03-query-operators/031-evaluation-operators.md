# 31. Evaluation Operators ($regex, $expr, $mod)
# हिंदी में: Evaluation Operators ($regex, $expr, $mod)

---

## 🔵 Simple Definition (English)
**Evaluation operators** compute something about a field's value instead of just comparing it. **`$regex`** matches strings against a pattern. **`$expr`** lets you use **aggregation expressions** inside a query — most famously to **compare two fields of the same document** (`$gt: ["$spent", "$budget"]`). **`$mod: [divisor, remainder]`** matches numbers whose remainder after division equals a given value. (Other members: `$text`, `$where`, `$jsonSchema`.)

## 🔵 सरल परिभाषा (Hindi)
**Evaluation operators** field की value की सिर्फ तुलना नहीं करते, बल्कि कुछ **compute** करते हैं। **`$regex`** strings को pattern से match करता है। **`$expr`** query के अंदर **aggregation expressions** चलाने देता है — सबसे मशहूर उपयोग **एक ही document की दो fields की तुलना** (`$gt: ["$spent", "$budget"]`)। **`$mod: [divisor, remainder]`** उन numbers से match करता है जिनका divisor से भाग देने पर बचा हुआ remainder दिया गया हो। (बाकी: `$text`, `$where`, `$jsonSchema`।)

---

## 🔴 Problem it Solves
Basic comparison operators (`$gt`, `$eq`) only compare a field to a **constant** you supply. Real questions need more: "users whose email ends with `@gmail.com`" (pattern), "customers who spent more than their own budget" (field vs field), "every 5th invoice" (arithmetic). Without evaluation operators you would pull all documents to the application and filter in JavaScript, wasting network and memory.

## 🔴 यह क्यों बना? (Hindi)
बुनियादी comparison operators (`$gt`, `$eq`) field की तुलना सिर्फ आपकी दी हुई **constant** से करते हैं। असली सवाल ज़्यादा होते हैं: "वो users जिनकी email `@gmail.com` पर ख़त्म होती है" (pattern), "वो customers जिन्होंने अपने ही budget से ज़्यादा ख़र्च किया" (field vs field), "हर 5वाँ invoice" (arithmetic)। Evaluation operators के बिना सारे documents application में खींचकर JavaScript में filter करने पड़ते, जिससे network और memory बर्बाद होती।

---

## 🟢 How it Works — Step by Step

Step 1 → **`$regex`**: `{ name: { $regex: "^rahul", $options: "i" } }` or the shorthand `{ name: /^rahul/i }`. Options: `i` ignore case, `m` multi-line anchors, `s` dot matches newline, `x` extended.
Step 2 → A regex anchored at the start and case-sensitive (`/^Rahul/`) can use an **index** (tight bounds); unanchored or case-insensitive patterns scan the whole index/collection. (Detailed in topic 37.)
Step 3 → **`$expr`**: `{ $expr: { $gt: ["$spent", "$budget"] } }`. Field paths are written with `$` and the expression language is the same as aggregation (`$multiply`, `$cond`, `$size`, ...).
Step 4 → `$expr` can use indexes only in limited cases (it uses an index for equality-style comparisons against constants/variables in some versions); field-to-field comparisons generally scan. Prefer storing a precomputed boolean if the query is hot.
Step 5 → **`$mod`**: `{ n: { $mod: [5, 0] } }` matches `n` divisible by 5. The divisor can't be 0 (`divisor cannot be 0`). It truncates non-integers to integers first.
Step 6 → Evaluation operators combine with all others using implicit AND or `$and/$or`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **`$regex`**: `{ name: { $regex: "^rahul", $options: "i" } }` या shorthand `{ name: /^rahul/i }`। Options: `i` case ignore, `m` multi-line anchors, `s` dot newline से भी match करे, `x` extended।
Step 2 → शुरुआत से anchored और case-sensitive regex (`/^Rahul/`) **index** इस्तेमाल कर सकता है (tight bounds); unanchored या case-insensitive patterns पूरा index/collection scan करते हैं। (विस्तार topic 37 में।)
Step 3 → **`$expr`**: `{ $expr: { $gt: ["$spent", "$budget"] } }`। Field paths `$` से लिखे जाते हैं और expression language aggregation वाली ही है (`$multiply`, `$cond`, `$size`, ...)।
Step 4 → `$expr` index सीमित मामलों में ही इस्तेमाल करता है; field-to-field तुलना आमतौर पर scan करती है। Query बहुत चलती हो तो precomputed boolean field रखना बेहतर है।
Step 5 → **`$mod`**: `{ n: { $mod: [5, 0] } }` उन `n` से match करता है जो 5 से विभाज्य हैं। Divisor 0 नहीं हो सकता (`divisor cannot be 0`)। Non-integers को पहले integer में truncate करता है।
Step 6 → Evaluation operators बाकी सबके साथ implicit AND या `$and/$or` से मिलाए जा सकते हैं।

---

## 🟡 Real World Example
**Zomato Gold fraud/budget checks**: `find({ $expr: { $gt: ["$spent", "$budget"] } })` finds corporate employees who exceeded their own meal budget — two fields in one document. Marketing finds Gmail customers with `email: /@gmail\.com$/i`. A lucky-draw gives a coupon to every 5th order number: `{ orderNo: { $mod: [5, 0] } }`.

## 🟡 Real Example Hindi mein
**Zomato Gold budget checks**: `find({ $expr: { $gt: ["$spent", "$budget"] } })` ऐसे corporate employees ढूँढता है जिन्होंने अपने meal budget से ज़्यादा ख़र्च किया — एक ही document की दो fields। Marketing Gmail customers `email: /@gmail\.com$/i` से ढूँढती है। Lucky draw में हर 5वें order number को coupon: `{ orderNo: { $mod: [5, 0] } }`।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use zomato_eval_demo                               // switch database
db.dropDatabase()                                  // clean start
db.u.insertMany([                                  // four customers
  { _id: 1, name: "Rahul Sharma", email: "rahul@gmail.com", spent: 500, budget: 400, n: 10 },
  { _id: 2, name: "rahul verma",  email: "RV@yahoo.com",     spent: 100, budget: 400, n: 7  },
  { _id: 3, name: "Priya",        email: "priya@gmail.com",  spent: 900, budget: 900, n: 4  },
  { _id: 4, name: "Amit Rahul",   email: "a@x.in",           spent: 5,   budget: 10,  n: 5  }
])
const ids = q => print(JSON.stringify(db.u.find(q).toArray().map(x => x._id))) // prints matching ids

// ---- $regex ----
ids({ name: /^Rahul/ })                                      // [1]      anchored, case-sensitive
ids({ name: { $regex: "^rahul", $options: "i" } })           // [1,2]    ignore case
ids({ email: { $regex: /@gmail\.com$/ } })                   // [1,3]    ends with @gmail.com

// ---- $expr: compare two fields of the SAME document ----
ids({ $expr: { $gt:  ["$spent", "$budget"] } })              // [1]      spent > budget
ids({ $expr: { $gte: ["$spent", "$budget"] } })              // [1,3]    spent >= budget
ids({ $expr: { $gt: [ { $multiply: ["$spent", 0.5] }, 200 ] } }) // [1,3]  computed value: half the spend > 200

// ---- $mod ----
ids({ n: { $mod: [5, 0] } })                                 // [1,4]    n divisible by 5
ids({ n: { $mod: [2, 1] } })                                 // [2,4]    odd numbers
db.u.find({ n: { $mod: [0, 1] } }).toArray()
// Error: divisor cannot be 0

// ---- $jsonSchema is also an evaluation operator ----
ids({ $jsonSchema: { required: ["name"], properties: { n: { bsonType: "int" } } } }) // [1,2,3,4]
```

## 💻 Code Example — Advanced

```javascript
// Index behaviour of $regex (mongosh) — actual explain output on our 4-doc collection
db.u.createIndex({ name: 1 })                                // index on name
db.u.find({ name: /^Rahul/ }).explain("executionStats")
  .queryPlanner.winningPlan.inputStage.indexBounds
// Output: { name: [ '["Rahul", "Rahum")', '[/^Rahul/, /^Rahul/]' ] }
//   -> tight range ["Rahul","Rahum") : only a small slice of the index is read

// Unanchored regex: every key must be examined
const ex = q => { const e = db.u.find(q).explain("executionStats").executionStats; print(e.totalKeysExamined, e.totalDocsExamined) }
ex({ name: /^Rahul/ })    // 2 1   keys, docs  (prefix range)
ex({ name: /Rahul/ })     // 4 2   all 4 index keys scanned, 2 docs fetched
ex({ name: /^rahul/i })   // 4 2   case-insensitive -> full index scan

// Multi-line / dot-all flags
db.u.updateOne({ _id: 1 }, { $set: { name: "Rahul\nSharma" } }) // value now contains a newline
ids({ name: /^Sharma/m })                                    // [1]  m flag: ^ matches after a newline
ids({ name: /^Sharma/ })                                     // []   without m: no match
ids({ name: { $regex: "Rahul.Sharma", $options: "s" } })     // [1]  s flag: . matches the newline
```
(Key/doc counts above are from this tiny collection; the point is the pattern, not the absolute numbers.)

```javascript
// Node.js driver v6 — regex built from user input MUST be escaped
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');   // escape regex metacharacters
const results = await db.collection('u').find({
  name: { $regex: '^' + esc(userInput), $options: 'i' }      // prefix search, safe from regex injection
}).limit(20).toArray();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Customer = mongoose.model('Customer', new mongoose.Schema({ name: String, email: String, spent: Number, budget: Number, n: Number }));
const app = express();

// GET /customers/over-budget  -> $expr
app.get('/customers/over-budget', async (req, res) => {
  const rows = await Customer.find({ $expr: { $gt: ['$spent', '$budget'] } }).select('name spent budget').lean();
  res.json(rows);
});

// GET /customers/search?prefix=rah  -> $regex with escaped input
app.get('/customers/search', async (req, res) => {
  const p = String(req.query.prefix || '').replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // never trust raw input
  res.json(await Customer.find({ name: { $regex: '^' + p, $options: 'i' } }).limit(20).lean());
});

// GET /customers/lucky  -> $mod
app.get('/customers/lucky', async (req, res) => {
  res.json(await Customer.find({ n: { $mod: [5, 0] } }).lean());
});
```
Mongoose casts query values per the schema, but it does **not** cast the field paths inside `$expr` (they are aggregation syntax), so numeric strings there will not be converted.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Comparing two fields without `$expr`
```javascript
db.u.find({ spent: { $gt: "$budget" } })        // Wrong: compares to the literal string "$budget" -> []
db.u.find({ $expr: { $gt: ["$spent", "$budget"] } }) // Right
```

❌ Mistake 2: Unescaped user input in `$regex`
```javascript
db.u.find({ name: { $regex: req.query.q } })    // Wrong: "a.b*(" can crash or cause ReDoS
db.u.find({ name: { $regex: esc(req.query.q) } }) // Right: escape metacharacters, cap input length
```

❌ Mistake 3: Expecting `/Rahul/` to use the index efficiently
```javascript
db.u.find({ name: /Rahul/ })   // Wrong for speed: scans all index keys (4 of 4 in our test)
db.u.find({ name: /^Rahul/ })  // Right: anchored prefix -> tight bounds
```

---

## 🧠 Tricky Interview Question

```javascript
db.u.find({ $expr: { $gt: ["$spent", "$budget"] } })
// vs
db.u.find({ spent: { $gt: "$budget" } })
```
Do they return the same documents?

Answer: No. The first returns documents whose `spent` is greater than their own `budget` (here `_id` 1). The second compares `spent` with the **literal string** `"$budget"`; because numbers sort before strings in BSON comparison order and `$gt` is type-bracketed, no numeric `spent` matches, so it returns nothing. Field-to-field comparison requires `$expr`.

---

## ⚫ Interview Questions + Answers

Q1: What is `$expr` and why do we need it?
A1: It lets the query language use aggregation expressions, enabling field-vs-field comparisons and computed conditions inside `find`.

Q2: Does `$regex` use indexes?
A2: Yes, when the pattern is a case-sensitive prefix match (`^abc`), MongoDB scans a bounded range. Case-insensitive or unanchored patterns still use the index but scan all of its keys.

Q3: What do the regex options `i`, `m`, `s`, `x` do?
A3: `i` ignores case, `m` makes `^`/`$` match at line breaks, `s` lets `.` match newline, `x` ignores whitespace and comments in the pattern.

Q4: Explain `$mod`.
A4: `{ field: { $mod: [divisor, remainder] } }` matches when `field % divisor == remainder`. Divisor cannot be zero.

Q5: Why is `$where` discouraged compared to `$expr`?
A5: `$where` runs JavaScript on the server for every document, cannot use indexes, is slower and a security risk; `$expr` uses native aggregation expressions (and `$where` is disabled on Atlas free tiers / with `--noscripting`).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Prefix search with an index (`^abc`), simple pattern validation.
- Comparing/combining fields of the same document (`$expr`).
- Sampling or bucketing by number (`$mod`).

❌ Avoid when:
- You need real full-text search with ranking — use `$text` or Atlas Search.
- The `$expr` comparison runs on a huge hot collection — store a computed field and index it.
- Unanchored, case-insensitive regex on millions of documents.

---

## 📊 Visual Diagram
```
 find({ ... })
   $regex  ->  name: /^Rahul/        "does the text match the pattern?"
   $expr   ->  spent  >  budget      "compare two fields in ONE document"
   $mod    ->  n % 5 == 0            "remainder check"

 index use:
   /^Rahul/  : [ "Rahul" ................ "Rahum" )   tight range, fast
   /Rahul/   : [ a b c d e f ... all keys scanned ]   slow
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$regex` | Pattern match on strings | Strings पर pattern match |
| `$options` | Regex flags (i, m, s, x) | Regex flags |
| `$expr` | Aggregation expressions in find | find में aggregation expressions |
| `$mod` | Remainder check | शेषफल की जाँच |
| Anchored regex | Starts with `^` | `^` से शुरू होने वाला regex |
| ReDoS | Regex denial of service | Regex से service ठप करना |

---

## ⚡ 3-Line Summary
English:
1. `$regex` matches text patterns, `$expr` runs aggregation expressions (field vs field), `$mod` checks remainders.
2. Only anchored, case-sensitive regexes get tight index bounds; always escape user input.
3. Use `$expr` rather than `spent: { $gt: "$budget" }`, which compares against a literal string.

Hindi:
1. `$regex` text patterns, `$expr` aggregation expressions (field vs field), और `$mod` remainder जाँचता है।
2. सिर्फ anchored, case-sensitive regex को tight index bounds मिलते हैं; user input हमेशा escape करो।
3. `spent: { $gt: "$budget" }` की जगह `$expr` इस्तेमाल करो, वो literal string से तुलना करता है।

---

## ➡️ Next Topic
**32. Array Query Operators ($all, $elemMatch, $size)** — matching array contents, conditions on a single element, and array length.
