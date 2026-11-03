# 37. Regular Expressions in MongoDB
# हिंदी में: MongoDB में Regular Expressions

---

## 🔵 Simple Definition (English)
MongoDB supports **PCRE-style regular expressions** for matching string fields, through the **`$regex`** operator or a JavaScript/driver regex literal (`/^SKU-\d{3}$/i`). In aggregation there are `$regexMatch`, `$regexFind` and `$regexFindAll`. A regex query can use an **index** efficiently only when it is a **case-sensitive, anchored prefix** (`^abc`); otherwise MongoDB still scans every index key (or document).

## 🔵 सरल परिभाषा (Hindi)
MongoDB string fields को match करने के लिए **PCRE-style regular expressions** को support करता है, **`$regex`** operator या JavaScript/driver के regex literal (`/^SKU-\d{3}$/i`) से। Aggregation में `$regexMatch`, `$regexFind` और `$regexFindAll` हैं। Regex query **index** का कुशलता से इस्तेमाल तभी करती है जब वो **case-sensitive, शुरुआत से anchored prefix** (`^abc`) हो; वरना MongoDB हर index key (या document) scan करता है।

---

## 🔴 Problem it Solves
Equality can't answer "phone numbers that are valid Indian mobiles", "SKUs like `SKU-###`", "emails ending in `@gmail.com`" or "names that contain *cafe* in any casing". Regexes express these patterns directly in the database, avoiding loading data into the app for filtering. The flip side is performance and safety: badly written regexes scan everything, and unescaped user input can be abused (ReDoS / unintended wildcards).

## 🔴 यह क्यों बना? (Hindi)
Equality से "वैध Indian mobile numbers", "`SKU-###` जैसे SKUs", "`@gmail.com` पर ख़त्म होने वाली emails" या "ऐसे names जिनमें किसी भी casing में *cafe* हो" नहीं पूछ सकते। Regexes ये patterns सीधे database में express करते हैं, app में data लाकर filter करने की ज़रूरत नहीं। दूसरा पहलू performance और safety है: ख़राब regexes सब कुछ scan करते हैं, और unescaped user input का दुरुपयोग हो सकता है (ReDoS / अनचाहे wildcards)।

---

## 🟢 How it Works — Step by Step

Step 1 → Two syntaxes: shell/driver literal `{ sku: /^SKU-\d{3}$/ }` or operator form `{ sku: { $regex: "^SKU-\\d{3}$", $options: "i" } }` (backslashes are doubled inside strings).
Step 2 → Flags: `i` case-insensitive, `m` `^`/`$` match at line breaks, `s` dot matches `\n` (use the **`$options`** string form for `s`), `x` extended (ignore whitespace/comments).
Step 3 → **Index use**: for `/^abc/` MongoDB converts the pattern into a range scan `["abc", "abd")` on a normal index. For `/abc/`, `/abc$/` or `/^abc/i` every key in the index is checked (index scan, not a collection scan, but still O(n)).
Step 4 → `{ field: { $not: /re/ } }` negates a pattern (missing fields also match).
Step 5 → **Escape user input** with a helper before embedding it in a pattern, otherwise `.`, `*`, `(` act as regex syntax.
Step 6 → In aggregation: `$regexMatch` (boolean), `$regexFind` (first match with captures and index), `$regexFindAll` (array of matches) — they work on expressions, so you can compute with matches inside `$project`/`$addFields`.
Step 7 → For **case-insensitive** equality/search at scale, prefer a **collation** index (`strength: 2`) or a lower-cased helper field; for real word search use `$text`/Atlas Search.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → दो syntax: shell/driver literal `{ sku: /^SKU-\d{3}$/ }` या operator रूप `{ sku: { $regex: "^SKU-\\d{3}$", $options: "i" } }` (strings के अंदर backslash दोगुना लिखते हैं)।
Step 2 → Flags: `i` case-insensitive, `m` `^`/`$` line breaks पर match, `s` dot `\n` से भी match (इसके लिए **`$options`** string रूप इस्तेमाल करो), `x` extended (whitespace/comments अनदेखे)।
Step 3 → **Index का उपयोग**: `/^abc/` के लिए MongoDB pattern को सामान्य index पर range scan `["abc", "abd")` में बदल देता है। `/abc/`, `/abc$/` या `/^abc/i` के लिए index की हर key जाँची जाती है (collection scan नहीं, पर फिर भी O(n))।
Step 4 → `{ field: { $not: /re/ } }` pattern को उलटता है (missing fields भी match करती हैं)।
Step 5 → Pattern में डालने से पहले **user input को escape** करो, वरना `.`, `*`, `(` regex syntax की तरह काम करेंगे।
Step 6 → Aggregation में: `$regexMatch` (boolean), `$regexFind` (पहला match, captures और index के साथ), `$regexFindAll` (matches का array) — ये expressions पर चलते हैं, इसलिए `$project`/`$addFields` में matches से compute कर सकते हैं।
Step 7 → बड़े पैमाने पर **case-insensitive** equality/search के लिए **collation** index (`strength: 2`) या lower-case helper field बेहतर है; असली word search के लिए `$text`/Atlas Search।

---

## 🟡 Real World Example
**Flipkart seller & inventory tools**: validating Indian mobile numbers with `{ phone: /^[6-9]\d{9}$/ }`, finding SKUs of the exact format `SKU-123` with `/^SKU-\d{3}$/`, and an admin search box that finds `email: /@gmail\.com$/i`. A product search "cafe" should match both "Café Latte" and "cafe mocha" — the regex `/^cafe/i` finds only the second, because é is a different character (unless you use a collation with diacritic-insensitivity).

## 🟡 Real Example Hindi mein
**Flipkart seller और inventory tools**: Indian mobile numbers की validation `{ phone: /^[6-9]\d{9}$/ }` से, ठीक `SKU-123` format वाले SKUs `/^SKU-\d{3}$/` से, और admin search box जो `email: /@gmail\.com$/i` ढूँढता है। Product search "cafe" को "Café Latte" और "cafe mocha" दोनों से match होना चाहिए — regex `/^cafe/i` सिर्फ दूसरे को ढूँढता है, क्योंकि é अलग अक्षर है (जब तक diacritic-insensitive collation न हो)।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh.

```javascript
use flipkart_regex_demo                            // switch database
db.dropDatabase()                                  // clean start
db.l.insertMany([                                  // three listings
  { _id: 1, phone: "9876543210", email: "a.b@Gmail.com",  sku: "SKU-001",  name: "Café Latte" },
  { _id: 2, phone: "12345",      email: "x@y",            sku: "sku-002",  name: "cafe mocha" },
  { _id: 3, phone: "9123456789", email: "z@corp.co.in",   sku: "SKU-1000", name: "Tea" }
])
const ids = q => print(JSON.stringify(db.l.find(q).toArray().map(x => x._id)))

ids({ phone: /^[6-9]\d{9}$/ })                     // [1,3]   valid 10-digit mobiles starting 6-9
ids({ sku: /^SKU-\d{3}$/ })                        // [1]     exactly three digits; SKU-1000 and sku-002 rejected
ids({ sku: /^SKU-\d{3}$/i })                       // [1,2]   case-insensitive now accepts sku-002
ids({ email: /@gmail\.com$/i })                    // [1]     escaped dot, anchored end, ignore case
ids({ name: /^cafe/i })                            // [2]     "Café" does not match: é != e
ids({ name: { $regex: "caf", $options: "i" } })    // [1,2]   substring (unanchored) with options string
ids({ name: { $not: /^caf/i } })                   // [3]     $not negates the pattern

// The dot is a wildcard unless escaped
ids({ email: { $regex: "a\\.b" } })                // [1]     literal dot
ids({ email: { $regex: "a.b" } })                  // [1]     matches too, but "a.b" would also match "aXb"!

// Escaping user input
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")   // escape regex metacharacters
esc("a.b+c")                                       // 'a\\.b\\+c'
ids({ email: new RegExp(esc("a.b"), "i") })        // [1]

ids({ $or: [ { name: /tea/i }, { sku: /002$/ } ] })// [2,3]  regex inside $or

// ---- aggregation regex operators ----
db.l.aggregate([
  { $match: { _id: 1 } },
  { $project: {
      m: { $regexMatch: { input: "$email", regex: /gmail/i } },       // true / false
      f: { $regexFind:  { input: "$phone", regex: "\\d{3}" } } } }    // first match object
]).toArray()
// Output: [ { _id: 1, m: true, f: { match: '987', idx: 0, captures: [] } } ]

db.l.aggregate([
  { $match: { _id: 3 } },
  { $project: { _id: 0, parts: { $regexFindAll: { input: "$phone", regex: "\\d{3}" } } } },
  { $project: { m: "$parts.match" } }
]).toArray()
// Output: [ { m: [ '912', '345', '678' ] } ]
```

## 💻 Code Example — Advanced

```javascript
// Index behaviour (mongosh) — look at the index bounds, not just counts
db.l.createIndex({ sku: 1 })
db.l.find({ sku: /^SKU-/ }).explain("executionStats").queryPlanner.winningPlan.inputStage.indexBounds
// Output: { sku: [ '["SKU-", "SKU.")', '[/^SKU-/, /^SKU-/]' ] }
//   -> only the narrow range ["SKU-","SKU.") is scanned (prefix optimization)

const ex = q => { const e = db.l.find(q).explain("executionStats").executionStats; print("keys", e.totalKeysExamined, "docs", e.totalDocsExamined) }
ex({ sku: /^SKU-/ })      // keys 3 docs 2   prefix range scan; fetches only the 2 case-sensitive matches
ex({ sku: /^sku-/i })     // keys 3 docs 3   case-insensitive -> full index scan, all 3 fetched
ex({ sku: /001$/ })       // keys 3 docs 1   suffix pattern -> every key examined
// On 3 documents all look similar; on millions only the prefix form stays fast.

// Case-insensitive search the SCALABLE way: collation index
db.l.createIndex({ name: 1 }, { collation: { locale: "en", strength: 1 } })   // strength 1 ignores case AND diacritics
db.l.find({ name: "cafe latte" }).collation({ locale: "en", strength: 1 })     // finds "Café Latte" via the index
```

```javascript
// Node.js driver v6 — safe user-driven prefix search with limits (prevents ReDoS and wildcard abuse)
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
async function searchSku(db, userInput) {
  const q = String(userInput).slice(0, 30);                 // cap length
  return db.collection('l').find({ sku: new RegExp('^' + esc(q)) }) // anchored => index friendly
           .limit(20).toArray();                             // never return unbounded results
}
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Express 5, Mongoose 8.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const Order = mongoose.model('Order', new mongoose.Schema({ customer: String, phone: String }));
const app = express();

// GET /orders?validPhone=1  -> only orders with a valid Indian mobile number
app.get('/orders', async (req, res) => {
  const f = {};
  if (req.query.validPhone) f.phone = { $regex: /^[6-9]\d{9}$/ };  // RegExp literal in a Mongoose filter
  res.json(await Order.find(f).select('customer -_id').lean());
});
// Real run (phone "9876543210") -> [{"customer":"Aman K"}]

// Schema-level validation with a regex (app-side, runs on save)
// phone: { type: String, match: [/^[6-9]\d{9}$/, 'Invalid mobile number'] }
```
Do not confuse `match:` (Mongoose validator, runs in Node) with `$regex` (runs in MongoDB). For database-level enforcement use `$jsonSchema` validation with a `pattern`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unanchored, case-insensitive regex on a huge collection
```javascript
db.users.find({ name: /rahul/i })            // Wrong: examines every index key / document
db.users.find({ name: /^rahul/ })            // Right (prefix): or use a collation index / $text
```

❌ Mistake 2: Unescaped user input
```javascript
db.l.find({ email: { $regex: req.query.q } })   // Wrong: "a.b" wildcard, "(" crashes, "(a+)+$" can freeze (ReDoS)
db.l.find({ email: { $regex: esc(req.query.q) } })  // Right: escape + cap length
```

❌ Mistake 3: Forgetting to double the backslash in string form
```javascript
db.l.find({ phone: { $regex: "^\d{10}$" } })     // Wrong: JS turns "\d" into "d" -> regex ^d{10}$ matches nothing
db.l.find({ phone: { $regex: "^\\d{10}$" } })    // Right (or use the /^\d{10}$/ literal)
```

---

## 🧠 Tricky Interview Question

```javascript
db.l.createIndex({ sku: 1 })
db.l.find({ sku: /^sku-/i })
```
Is the index used for a tight range scan?

Answer: **No tight range.** The index exists and may be chosen, but because of the `i` flag MongoDB cannot build a prefix range, so it examines **all** keys (real run: keys 3, docs 3, versus a bounded `["SKU-","SKU.")` range for `/^SKU-/`). To get fast case-insensitive matching use a collation index with `strength: 1/2` (and query with the same collation) or store a normalised lowercase field. Also note the pattern `/^SKU-/` is only prefix-optimised when it is simple — `/^SKU-|^X/` isn't.

---

## ⚫ Interview Questions + Answers

Q1: How do you write a regex query?
A1: `{ f: /pattern/flags }` or `{ f: { $regex: "pattern", $options: "flags" } }`; in aggregation use `$regexMatch/$regexFind/$regexFindAll`.

Q2: When does a regex use an index efficiently?
A2: For case-sensitive patterns anchored at the start with a literal prefix (`^abc`). Other patterns still scan all keys of the index.

Q3: How do you do fast case-insensitive search?
A3: Create an index with a collation (`locale`, `strength: 1 or 2`) and run the query with the same collation, or maintain a normalised lowercase field; for words use `$text`/Atlas Search.

Q4: How to avoid regex injection/ReDoS?
A4: Escape metacharacters, limit input length, avoid nested quantifiers, set `maxTimeMS`, and prefer anchored prefix searches.

Q5: What is the difference between `$regex` and `$text`?
A5: `$regex` matches arbitrary character patterns (no stemming, no ranking); `$text` matches stemmed whole words from a text index with relevance scoring.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Format validation (phone, SKU, codes) and prefix lookups on indexed fields.
- Occasional admin searches on small/medium collections.
- Extracting parts of strings in aggregation.

❌ Avoid when:
- High-traffic unanchored or case-insensitive search on large collections.
- Real full-text search (use `$text` / Atlas Search).
- Untrusted input without escaping and limits.

---

## 📊 Visual Diagram
```
 index on sku:  [ SKU-001 | SKU-1000 | sku-002 ]  (sorted)

 /^SKU-/     -> range ["SKU-","SKU.") .... ■■            fast  (prefix)
 /^sku-/i    -> every key examined ......... ■■■          slower (case-insens.)
 /001$/      -> every key examined ......... ■■■          slower (suffix)

 Flags:  i = ignore case   m = ^ $ per line   s = dot matches \n   x = extended
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$regex` | Pattern-matching operator | Pattern match करने वाला operator |
| `$options` | Regex flags like `i`, `m`, `s`, `x` | Regex flags |
| Anchor (`^`, `$`) | Start / end of string | String की शुरुआत / अंत |
| Prefix regex | `^abc` — index friendly | `^abc` — index के अनुकूल |
| Collation | Language-aware comparison rules | भाषा-आधारित तुलना के नियम |
| ReDoS | Regex that causes catastrophic backtracking | Regex backtracking से service ठप |

---

## ⚡ 3-Line Summary
English:
1. Use `/pattern/flags` or `$regex` + `$options`; aggregation offers `$regexMatch`, `$regexFind`, `$regexFindAll`.
2. Only case-sensitive anchored prefix regexes get tight index ranges; use collation indexes for case-insensitive search.
3. Always escape and length-limit user input, and double backslashes in string patterns.

Hindi:
1. `/pattern/flags` या `$regex` + `$options` इस्तेमाल करो; aggregation में `$regexMatch`, `$regexFind`, `$regexFindAll` मिलते हैं।
2. सिर्फ case-sensitive anchored prefix regexes को tight index range मिलती है; case-insensitive search के लिए collation index लो।
3. User input को हमेशा escape करो और length सीमित रखो, और string patterns में backslash दोगुना लिखो।

---

## ➡️ Next Topic
**38. Next topic in 03-query-operators** — continue with the following note in the Query Operators folder.
