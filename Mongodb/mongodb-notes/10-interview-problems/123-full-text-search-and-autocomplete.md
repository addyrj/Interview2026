# 123. Full-text Search + Autocomplete
# हिंदी में: Full-text Search + Autocomplete

---

## 🔵 Simple Definition (English)
**Full-text search** finds documents by words and meaning rather than exact equality: it tokenizes text, removes stop words, stems words (`running` -> `run`) and ranks results by relevance. MongoDB gives you a built-in **`text` index** with `$text` queries. **Autocomplete** (search-as-you-type) suggests results while the user is still typing a prefix; in plain MongoDB this is done with an indexed **prefix range/regex** query, and in Atlas with the **Atlas Search `autocomplete`** operator.

## 🔵 सरल परिभाषा (Hindi)
**Full-text search** documents को exact equality की जगह शब्दों और मतलब से ढूँढता है: text को tokens में तोड़ता है, stop words हटाता है, शब्दों को stem करता है (`running` -> `run`) और relevance से rank करता है। MongoDB में built-in **`text` index** और `$text` queries मिलते हैं। **Autocomplete** (search-as-you-type) user के टाइप करते-करते prefix पर suggestions देता है; सादे MongoDB में यह indexed **prefix range/regex** query से होता है, और Atlas में **Atlas Search `autocomplete`** operator से।

---

## 🔴 Problem it Solves
`find({ name: "samsung" })` only matches the exact value. `find({ name: /samsung/i })` is case-insensitive but unanchored, so it scans every document (COLLSCAN) and has no ranking. Users search with typos-free but partial, multi-word, differently inflected phrases ("android phone", "run"), and expect the best match on top and suggestions after two letters. You need an index-backed, ranked, fast search without bolting on a separate search engine for simple cases.

## 🔴 यह क्यों बना? (Hindi)
`find({ name: "samsung" })` सिर्फ exact value match करता है। `find({ name: /samsung/i })` case-insensitive है पर anchored नहीं, इसलिए हर document scan करता है (COLLSCAN) और कोई ranking नहीं देता। Users अधूरे, multi-word, अलग रूप के phrases खोजते हैं ("android phone", "run"), best match ऊपर चाहते हैं और दो अक्षर के बाद suggestions। सरल मामलों के लिए अलग search engine जोड़े बिना index-backed, ranked, तेज़ search चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 -> Create ONE text index over the searchable fields, with **weights** so a title match outranks a description match: `createIndex({name:"text", desc:"text"}, {weights:{name:10, desc:1}})`. A collection can have only one text index.
Step 2 -> At write time MongoDB tokenizes each field, lower-cases, drops stop words, stems (English by default) and stores the terms in the index.
Step 3 -> Query with `{ $text: { $search: "android phone" } }`. Words are OR-ed; `"quoted phrase"` requires the phrase; `-word` excludes a term.
Step 4 -> Rank with `{ score: { $meta: "textScore" } }` in the projection and sort by it.
Step 5 -> For autocomplete store a **normalized lower-case copy** (`nameLower`) with a normal index, and query a prefix: `{ nameLower: { $regex: "^sam" } }` (or `$gte: "sam", $lt: "san"`). Case-sensitive anchored prefix regexes use index bounds; case-insensitive (`/i`) ones do not.
Step 6 -> Escape user input before putting it into a regex, limit to 5-10 results, require 2+ characters and debounce on the client.
Step 7 -> Need typo tolerance, fuzzy match, highlights or true "edge n-gram" autocomplete? Use **Atlas Search** (Lucene based, Atlas/Enterprise-search only) or an external engine; these are not available on a plain `mongod`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 -> Searchable fields पर **एक** text index बनाओ, **weights** के साथ ताकि title match description से ऊपर आए: `createIndex({name:"text", desc:"text"}, {weights:{name:10, desc:1}})`। एक collection में सिर्फ एक text index हो सकता है।
Step 2 -> Write के समय MongoDB हर field को tokenize करता है, lower-case, stop words हटाता, stem करता (default English) और terms index में रखता है।
Step 3 -> `{ $text: { $search: "android phone" } }` से query करो। शब्द OR होते हैं; `"quoted phrase"` में पूरा phrase चाहिए; `-word` उस term को बाहर करता है।
Step 4 -> Projection में `{ score: { $meta: "textScore" } }` से rank करो और उसी पर sort करो।
Step 5 -> Autocomplete के लिए **lower-case normalized copy** (`nameLower`) रखो, उस पर normal index, और prefix query: `{ nameLower: { $regex: "^sam" } }` (या `$gte: "sam", $lt: "san"`)। Case-sensitive anchored prefix regex index bounds इस्तेमाल करता है; case-insensitive (`/i`) नहीं करता।
Step 6 -> User input को regex में डालने से पहले escape करो, 5-10 results तक सीमित रखो, 2+ अक्षर माँगो और client पर debounce करो।
Step 7 -> Typo tolerance, fuzzy match, highlight या सच्चा "edge n-gram" autocomplete चाहिए? **Atlas Search** (Lucene based, सिर्फ Atlas) या external engine इस्तेमाल करो; ये सादे `mongod` पर उपलब्ध नहीं।

---

## 🟡 Real World Example
**Flipkart-style product search box.** A user types "sam": the page immediately shows "Samsung Galaxy Buds", "Samsung Galaxy S24" (prefix autocomplete on the lower-cased name). The user presses Enter on "android phone": the results page runs `$text` search and shows Galaxy S24 first, because the word "android" and "phone" are in its description and the weighted title also matches the brand. "Sansui TV" appears lower (matches "android" only). Typing "run" also finds "Running Shoes" because of stemming.

## 🟡 Real Example Hindi mein
**Flipkart जैसा product search box।** User "sam" टाइप करता है: page तुरंत "Samsung Galaxy Buds", "Samsung Galaxy S24" दिखाता है (lower-case name पर prefix autocomplete)। User "android phone" पर Enter दबाता है: results page `$text` search चलाता है और Galaxy S24 सबसे ऊपर दिखाता है क्योंकि description में "android" और "phone" दोनों हैं। "Sansui TV" नीचे आता है (सिर्फ "android" match)। "run" टाइप करने पर भी "Running Shoes" मिलता है, stemming की वजह से।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4 with mongosh (ObjectIds omitted from output).

```javascript
// mongosh --port 27017
const d = db.getSiblingDB("fts");                      // demo database
d.dropDatabase();                                      // clean start
d.products.insertMany([                                // sample catalog
  { name: "Samsung Galaxy S24",  desc: "flagship android phone with great camera", brand: "Samsung" },
  { name: "Samsung Galaxy Buds", desc: "wireless earbuds",                         brand: "Samsung" },
  { name: "Apple iPhone 15",     desc: "phone with titanium design",               brand: "Apple" },
  { name: "Sansui TV 43",        desc: "smart android tv",                         brand: "Sansui" },
  { name: "Running Shoes",       desc: "lightweight shoes for runners",            brand: "Nike" },
]);

// ONE text index, title is 10x more important than description
d.products.createIndex({ name: "text", desc: "text" }, { weights: { name: 10, desc: 1 }, name: "txt" });

// Ranked search: project the score and sort by it
d.products.find(
  { $text: { $search: "android phone" } },             // words are OR-ed
  { name: 1, score: { $meta: "textScore" } }           // add relevance score to results
).sort({ score: { $meta: "textScore" } });             // best match first
// Output: [ 'Samsung Galaxy S24' 1.2 ], [ 'Sansui TV 43' 0.667 ], [ 'Apple iPhone 15' 0.667 ]

d.products.find({ $text: { $search: "run" } }, { name: 1 });
// Output: [ 'Running Shoes' ]          <- stemming: "run" matches "running"/"runners"

d.products.find({ $text: { $search: "\"android phone\"" } }, { name: 1 });
// Output: [ 'Samsung Galaxy S24' ]     <- exact phrase "android phone"

d.products.find({ $text: { $search: "android -tv" } }, { name: 1 });
// Output: [ 'Samsung Galaxy S24' ]     <- "-tv" excludes Sansui TV

// AUTOCOMPLETE: normalized copy + normal index + anchored prefix
d.products.createIndex({ nameLower: 1 });              // regular B-tree index
d.products.updateMany({}, [{ $set: { nameLower: { $toLower: "$name" } } }]); // fill the copy (pipeline update)
d.products.find({ nameLower: { $regex: "^sam" } }, { name: 1, _id: 0 }).limit(5);
// Output: [ { name: 'Samsung Galaxy Buds' }, { name: 'Samsung Galaxy S24' } ]

d.products.find({ nameLower: { $regex: "^sam" } }).explain("executionStats");
// Output (summary): stage IXSCAN, totalKeysExamined 3, totalDocsExamined 2, nReturned 2

d.products.find({ desc: /phone/i }).explain().queryPlanner.winningPlan.stage;
// Output: COLLSCAN   <- unanchored / case-insensitive regex cannot use an index efficiently
```

## 💻 Code Example — Advanced

```javascript
// Aggregation version: text search + score + filter + pagination
// ($text must be in the FIRST $match stage of the pipeline)
db.products.aggregate([
  { $match: { $text: { $search: "android phone" } } },    // index-backed full-text match
  { $addFields: { score: { $meta: "textScore" } } },     // expose relevance as a normal field
  { $sort: { score: -1 } },                              // rank
  { $project: { name: 1, score: 1, _id: 0 } },
  { $limit: 10 },
]);
// Output: [ { name: 'Samsung Galaxy S24', score: 1.2 }, { name: 'Sansui TV 43', score: 0.667 },
//           { name: 'Apple iPhone 15', score: 0.667 } ]

// Range form of prefix (same index bounds as ^sam, no regex engine; immune to regex-special chars)
db.products.find({ nameLower: { $gte: "sam", $lt: "san" } }, { name: 1, _id: 0 });
// Output: [ { name: 'Samsung Galaxy Buds' }, { name: 'Samsung Galaxy S24' } ]
// "san" is the prefix with its last character incremented (m -> n)

// Filter + text in one query: add a compound text index with a prefix field to narrow by brand
db.products2.createIndex({ brand: 1, name: "text", desc: "text" }); // brand is an EQUALITY prefix
db.products2.find({ brand: "Samsung", $text: { $search: "galaxy" } }); // query MUST give brand equality

// Atlas Search autocomplete (Atlas only, syntax shown, NOT run here: needs an Atlas cluster)
// Index definition (JSON in Atlas UI):
//   { "mappings": { "fields": { "name": [ { "type": "autocomplete", "tokenization": "edgeGram",
//                                           "minGrams": 2, "maxGrams": 15 } ] } } }
db.products.aggregate([
  { $search: { index: "default", autocomplete: { query: "sams", path: "name", fuzzy: { maxEdits: 1 } } } },
  { $limit: 5 },
  { $project: { name: 1, _id: 0 } },
]);
```

---

## 🟠 Express.js / Mongoose Integration

Tested with Express + Mongoose 9 + supertest against MongoDB 8.0.4.

```javascript
const express = require('express');
const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: String,
  desc: String,
  nameLower: String,                                    // lower-cased copy for prefix autocomplete
});
// Weighted text index and prefix index declared on the schema (built at startup by autoIndex)
productSchema.index({ name: 'text', desc: 'text' }, { weights: { name: 10, desc: 1 } });
productSchema.index({ nameLower: 1 });
// Keep the copy in sync on every save
productSchema.pre('save', function () { this.nameLower = this.name.toLowerCase(); });
const Product = mongoose.model('Product', productSchema);

// Escape regex metacharacters so user input is treated as plain text (prevents ReDoS / injection)
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const app = express();

// GET /search?q=android   -> ranked full-text results
app.get('/search', async (req, res) => {
  const q = String(req.query.q || '').slice(0, 100);    // force string (blocks {"$ne":..} objects), cap length
  if (!q) return res.json([]);
  const rows = await Product.find(
    { $text: { $search: q } },
    { name: 1, score: { $meta: 'textScore' } }
  ).sort({ score: { $meta: 'textScore' } }).limit(10).lean();
  res.json(rows);
});

// GET /suggest?q=sam      -> up to 5 names that start with the typed prefix
app.get('/suggest', async (req, res) => {
  const p = String(req.query.q || '').toLowerCase().trim().slice(0, 30);
  if (p.length < 2) return res.json([]);                // do not search on 1 letter
  const rows = await Product.find({ nameLower: { $regex: '^' + esc(p) } }, { name: 1, _id: 0 })
    .limit(5).lean();
  res.json(rows.map((r) => r.name));
});
```
Tested responses: `/search?q=android` -> `[["Samsung Galaxy S24", 0.75], ["Sansui TV 43", 0.667]]`; `/suggest?q=Sam` -> `["Samsung Galaxy Buds", "Samsung Galaxy S24"]`; `/suggest?q=a.*` -> `[]` (the dot and star are escaped, so they are literal characters). Scores differ a little from the shell example because the sample data differs.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using an unanchored or case-insensitive regex for search/autocomplete
```javascript
// Wrong — COLLSCAN on every keystroke, no ranking
db.products.find({ name: /sam/i });

// Right — text index for words, normalized lower-case field + anchored regex for prefixes
db.products.find({ $text: { $search: "sam" } });
db.products.find({ nameLower: { $regex: "^sam" } });
```

❌ Mistake 2: Expecting `$text` to do partial words
```javascript
// Wrong — $text matches whole STEMMED words: "sam" will NOT find "Samsung"
db.products.find({ $text: { $search: "sam" } });   // Output: []

// Right — use the prefix query for partial words, $text for whole-word relevance search
```

❌ Mistake 3: Passing raw user input into a regex
```javascript
// Wrong — "a.*" or catastrophic patterns hit the server (regex injection / ReDoS)
find({ nameLower: { $regex: "^" + req.query.q } });
// Right — escape metacharacters, cap length, and force a string
find({ nameLower: { $regex: "^" + esc(String(req.query.q).slice(0, 30)) } });
```

❌ Mistake 4: Trying to create a second text index
✅ Correct: only ONE text index per collection. Put all searchable fields in it (or use a wildcard `{ "$**": "text" }`, which is costlier) and drop/recreate it to change fields.

❌ Mistake 5: Sorting `$text` results without the score
✅ Correct: without `{ $meta: "textScore" }` sort the order is arbitrary; always project and sort by the score. In aggregation, copy the score with `$addFields` first, then `$sort` on the new field.

---

## 🧠 Tricky Interview Question

"A user types `sam` in the search box. `db.products.find({ $text: { $search: 'sam' } })` returns nothing although 'Samsung Galaxy S24' exists, and `find({name: /sam/i})` works but is slow. Why, and what is the fix?"

Answer: A text index stores whole, stemmed **words** ("samsung", "galaxy", "s24"). `sam` is not a word in the index, so `$text` finds nothing; text search has no prefix matching. The `/sam/i` regex works but is unanchored and case-insensitive, so it cannot use index bounds and does a COLLSCAN (we confirmed `COLLSCAN` in `explain`). Fix: store `nameLower`, index it, and query the anchored, case-sensitive `^sam` (or `$gte "sam", $lt "san"`), which produced `IXSCAN` with 3 keys examined and 2 documents returned. Use `$text` for the full search results page, and the prefix query for the suggest dropdown. For typo tolerance and real edge n-gram autocomplete on large catalogs, move to Atlas Search.

---

## ⚫ Interview Questions + Answers

Q1: How does a MongoDB text index work and what are its limits?
A1: It tokenizes and stems text per language, drops stop words, and stores term-to-document entries. Limits: one text index per collection, whole-word matching only (no partial or fuzzy), no typo tolerance, limited language support, text score is simple TF-IDF-like, and `$text` must be in the first `$match` stage of an aggregation. It is perfect for small to medium search needs.

Q2: How do `weights` and `textScore` work?
A2: Each field gets a weight (default 1); a term found in a heavier field raises the score. The score is exposed via `{ $meta: "textScore" }` for projection and sorting. In our test a title weight of 10 and description weight of 1 put "Samsung Galaxy S24" first for "android phone" (1.2 vs 0.667).

Q3: How do you build autocomplete without Atlas?
A3: Keep a lower-cased (and possibly accent-stripped) copy of the searchable string, index it, and run an anchored prefix query with a small `limit`. For middle-of-word matches store n-grams or keywords in an array field with a multikey index. Debounce requests on the client and require at least 2 characters.

Q4: Text index vs Atlas Search vs Elasticsearch?
A4: Text index: built in, free, basic, same transaction/consistency as the data. Atlas Search: Lucene engine inside Atlas, with fuzzy, autocomplete, facets, highlights, synonyms and vector search, synced automatically. Elasticsearch: most powerful and flexible, but a separate cluster you must keep in sync (change streams or CDC) and operate. Choose by feature need and operational budget.

Q5: How do you search with a filter (brand = Samsung, price < 500) and text together?
A5: `$text` can be combined with other conditions in the same `find`. For speed, build a compound text index with equality prefix fields (`{brand:1, name:"text"}`); queries must then include equality on `brand`. Range conditions like price are applied after the text match as filters on the matched documents. In Atlas Search use the `compound` operator with `filter` clauses.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need simple ranked keyword search on a few text fields without extra infrastructure
- Prefix suggestions (names, cities, tags) can be answered with an indexed lower-case field
- Your data is modest and search quality needs are basic

❌ Avoid when:
- You need typo tolerance, synonyms, facets, highlighting or semantic/vector search: use Atlas Search or Elasticsearch/OpenSearch
- You need partial-word or substring search over millions of documents (regex scans become unusably slow)
- You need many language analyzers or custom tokenization beyond the built-in text index

---

## 📊 Visual Diagram
```
FULL-TEXT SEARCH + AUTOCOMPLETE
───────────────────────────────────────────────────────────
 products: { name, desc, nameLower }

 Indexes:  TEXT(name w10, desc w1)      B-TREE(nameLower)
              │                               │
 User types "sam" ───────────────────────────►│  prefix ^sam
              │                               ▼
              │                    ["samsung galaxy buds",
              │                     "samsung galaxy s24"]  (IXSCAN)
              │
 User submits "android phone"
              │
              ▼
   $text tokenize+stem ► match terms ► score (weights)
              │
              ▼
   sort by {$meta:"textScore"} ► limit 10 ► results page

 WRONG: /sam/i  ──► COLLSCAN (reads every document)
 BIGGER NEEDS (typos, facets): Atlas Search / Elasticsearch
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Text index | Index of stemmed words for `$text` | `$text` के लिए stemmed शब्दों का index |
| $text / $search | Full-text query operator | Full-text query operator |
| textScore | Relevance score via `$meta` | `$meta` से मिलने वाला relevance score |
| Weights | Field importance in scoring | Scoring में field का महत्व |
| Stemming | Reducing words to roots (running -> run) | शब्दों को मूल रूप में लाना |
| Prefix query | Anchored `^abc` search on an index | Index पर anchored `^abc` search |
| Edge n-gram | Prefixes of words stored for autocomplete | Autocomplete के लिए शब्दों के prefixes |
| Atlas Search | Lucene-based search in Atlas | Atlas में Lucene-आधारित search |

---

## ⚡ 3-Line Summary
English:
1. Use one weighted `text` index and `$text` with `{$meta:"textScore"}` for ranked whole-word search; it handles stemming, phrases and `-exclusions`.
2. For autocomplete, index a lower-case copy and run an anchored `^prefix` query (never `/x/i`), with escaped input and a small limit.
3. Typos, facets and real edge n-gram autocomplete need Atlas Search or an external engine.

Hindi:
1. Ranked whole-word search के लिए एक weighted `text` index और `{$meta:"textScore"}` के साथ `$text` इस्तेमाल करो; यह stemming, phrases और `-exclusions` संभालता है।
2. Autocomplete के लिए lower-case copy पर index बनाओ और anchored `^prefix` query चलाओ (कभी `/x/i` नहीं), input escape करो और limit छोटी रखो।
3. Typos, facets और असली edge n-gram autocomplete के लिए Atlas Search या external engine चाहिए।

---

## ➡️ Next Topic
**124. Analytics Dashboard Pipeline (Daily Revenue)** — build a multi-stage aggregation for daily revenue reports.
