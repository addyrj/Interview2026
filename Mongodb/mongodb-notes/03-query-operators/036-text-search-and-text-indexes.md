# 36. Text Search ($text) and Text Indexes
# हिंदी में: Text Search ($text) और Text Indexes

---

## 🔵 Simple Definition (English)
A **text index** (`createIndex({ field: "text" })`) tokenizes string fields into **stemmed, lower-cased words** (minus "stop words" like *the*). The **`$text`** query operator then searches that index for words, **phrases** (`"\"paneer butter\""`), and **negations** (`-chicken`), and can return a **relevance score** via `{ $meta: "textScore" }`. A collection can have **only one** text index (but it may cover several fields, each with a **weight**). This is MongoDB's built-in lightweight full-text search; on Atlas, **Atlas Search** is the more powerful alternative.

## 🔵 सरल परिभाषा (Hindi)
**Text index** (`createIndex({ field: "text" })`) string fields को **stemmed, lower-case शब्दों** में तोड़ता है ("stop words" जैसे *the* हटाकर)। **`$text`** query operator फिर उस index में शब्द, **phrases** (`"\"paneer butter\""`) और **negation** (`-chicken`) खोजता है, और `{ $meta: "textScore" }` से **relevance score** भी दे सकता है। एक collection में **सिर्फ एक** text index हो सकता है (पर उसमें कई fields हो सकती हैं, हर एक का **weight** अलग)। यह MongoDB का built-in हल्का full-text search है; Atlas पर **Atlas Search** ज़्यादा शक्तिशाली विकल्प है।

---

## 🔴 Problem it Solves
`$regex` can only match a pattern; it does not understand that *run*, *runs* and *running* are the same word, cannot rank results by relevance, and is slow when unanchored. A food-search bar needs: case-insensitive, multi-word, language-aware matching ("cube" finds "cubes"), ranking (title matches beat description matches), and an indexed lookup. A text index provides exactly that without running a separate search engine.

## 🔴 यह क्यों बना? (Hindi)
`$regex` सिर्फ pattern match करता है; उसे नहीं पता कि *run*, *runs* और *running* एक ही शब्द हैं, वो results को relevance से rank नहीं कर सकता, और unanchored होने पर धीमा है। Food-search bar को चाहिए: case-insensitive, multi-word, भाषा-जागरूक matching ("cube" से "cubes" मिले), ranking (title match, description match से ऊपर), और indexed lookup। Text index अलग search engine चलाए बिना यही देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create the index: `db.f.createIndex({ name: "text", desc: "text" }, { weights: { name: 5, desc: 1 }, name: "food_text" })`. Wildcard `{ "$**": "text" }` indexes every string field.
Step 2 → At write time, MongoDB splits text into tokens, lower-cases them, removes **stop words** (the, a, is ...) and **stems** them (language default is English: *runs* -> *run*, *cubes* -> *cube*).
Step 3 → Query: `{ $text: { $search: "paneer biryani" } }`. Space-separated words are combined with **OR**.
Step 4 → **Phrase**: escaped quotes inside the string: `"\"paneer butter\""` requires that exact phrase. **Negation**: `"biryani -chicken"` excludes documents containing *chicken*.
Step 5 → **Score**: `find({ $text: ... }, { score: { $meta: "textScore" } }).sort({ score: { $meta: "textScore" } })` ranks by relevance (weights influence it).
Step 6 → Options: `$language` (e.g. `"none"` disables stemming/stop words), `$caseSensitive`, `$diacriticSensitive`.
Step 7 → Limits: **one text index per collection**; without the index a `$text` query fails with `text index required for $text query`; inside `$or`, every clause must be indexed.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Index बनाओ: `db.f.createIndex({ name: "text", desc: "text" }, { weights: { name: 5, desc: 1 }, name: "food_text" })`। Wildcard `{ "$**": "text" }` हर string field को index करता है।
Step 2 → Write के समय MongoDB text को tokens में बाँटता है, lower-case करता है, **stop words** (the, a, is ...) हटाता है और **stem** करता है (default भाषा English: *runs* -> *run*, *cubes* -> *cube*)।
Step 3 → Query: `{ $text: { $search: "paneer biryani" } }`। Space से अलग शब्द **OR** से जुड़ते हैं।
Step 4 → **Phrase**: string के अंदर escaped quotes: `"\"paneer butter\""` ठीक वही phrase माँगता है। **Negation**: `"biryani -chicken"` उन documents को हटाता है जिनमें *chicken* है।
Step 5 → **Score**: `find({ $text: ... }, { score: { $meta: "textScore" } }).sort({ score: { $meta: "textScore" } })` relevance से rank करता है (weights असर डालते हैं)।
Step 6 → Options: `$language` (जैसे `"none"` stemming/stop words बंद करता है), `$caseSensitive`, `$diacriticSensitive`।
Step 7 → सीमाएँ: collection में **एक ही text index**; `$text` query में ऐसी जगह हो जहाँ index इस्तेमाल हो सके, index न हो तो query `text index required for $text query` से fail होती है।

---

## 🟡 Real World Example
**Zomato dish search**: the search bar queries `{ $text: { $search: "paneer biryani" } }` over dish `name` (weight 5) and `desc` (weight 1). "Chicken Biryani" ranks first because the title contains *biryani* (score 4.35), followed by "Paneer Butter Masala" (3.93). Typing "cube" also finds "Grilled cottage cheese cubes" because of stemming, and "biryani -chicken" gives the vegetarian options.

## 🟡 Real Example Hindi mein
**Zomato dish search**: search bar dish के `name` (weight 5) और `desc` (weight 1) पर `{ $text: { $search: "paneer biryani" } }` चलाता है। "Chicken Biryani" सबसे ऊपर आता है क्योंकि title में *biryani* है (score 4.35), फिर "Paneer Butter Masala" (3.93)। "cube" टाइप करने पर "Grilled cottage cheese cubes" भी मिलता है (stemming की वजह से), और "biryani -chicken" से vegetarian विकल्प मिलते हैं।

---

## 💻 Code Example — Basic

Tested on MongoDB 8.0.4, mongosh (scores are computed by the server; yours should match on the same data).

```javascript
use zomato_text_demo                               // switch database
db.dropDatabase()                                  // clean start
db.f.insertMany([                                  // five dishes
  { _id: 1, name: "Paneer Butter Masala", desc: "Creamy tomato gravy with paneer cubes" },
  { _id: 2, name: "Chicken Biryani",      desc: "Hyderabadi style dum biryani with chicken" },
  { _id: 3, name: "Veg Biryani",          desc: "Fragrant rice cooked with vegetables" },
  { _id: 4, name: "Paneer Tikka",         desc: "Grilled cottage cheese cubes" },
  { _id: 5, name: "Running shoes",        desc: "He runs daily" }
])

// ONE text index over two fields; name matters 5x more than desc
db.f.createIndex({ name: "text", desc: "text" }, { weights: { name: 5, desc: 1 }, name: "food_text" })

const ids = s => JSON.stringify(db.f.find({ $text: { $search: s } }).toArray().map(x => x._id))
ids("biryani")                                     // [2,3]       single word
ids("paneer biryani")                              // [2,3,1,4]   OR of the words
ids("\"paneer butter\"")                           // [1]         exact phrase
ids("biryani -chicken")                            // [3]         negation removes the chicken one
ids("run")                                         // [5]         stemming: "runs" matches "run"
ids("cube")                                        // [4,1]       stemming: "cubes" matches "cube"
ids("the")                                         // []          stop word, ignored

// ---- relevance score ----
db.f.find({ $text: { $search: "paneer biryani" } }, { name: 1, score: { $meta: "textScore" } })
  .sort({ score: { $meta: "textScore" } })         // best match first
// Output (id, name, score):
//   2 Chicken Biryani        4.35   <- 'biryani' in name (weight 5) AND in desc
//   1 Paneer Butter Masala   3.93
//   3 Veg Biryani            3.75
//   4 Paneer Tikka           3.75

db.f.getIndexes().map(i => i.name)                 // [ '_id_', 'food_text' ]

db.f.createIndex({ other: "text" })                // a SECOND text index
// Error code: IndexOptionsConflict   (only one text index per collection)

// ---- no text index -> error ----
db.g.insertOne({ a: "hello" })
db.g.find({ $text: { $search: "hello" } }).toArray()
// IndexNotFound: text index required for $text query
```

## 💻 Code Example — Advanced

```javascript
// Options (mongosh)
db.f.find({ $text: { $search: "Biryani", $caseSensitive: true } }).toArray().length   // 2
db.f.find({ $text: { $search: "biryani", $language: "none" } }).toArray().length      // 2 (no stemming/stop words)

// Aggregation: $text must be in the FIRST $match stage. The score is read with $meta.
db.f.aggregate([
  { $match: { $text: { $search: "paneer" } } },                     // first stage only
  { $addFields: { score: { $meta: "textScore" } } },                // expose the relevance score
  { $sort: { score: -1 } },                                         // best first
  { $project: { name: 1, _id: 0, score: 1 } }
])
// Output: [ { name: 'Paneer Butter Masala', score: 3.933333333333333 }, { name: 'Paneer Tikka', score: 3.75 } ]

// Wildcard text index covering all string fields (alternative design)
// db.f.createIndex({ "$**": "text" })

// Combine text + normal filters
db.f.find({ $text: { $search: "biryani" }, _id: { $gt: 2 } })       // text first, then filter
```

```javascript
// Node.js driver v6 — search endpoint helper
async function search(db, q, limit = 10) {
  return db.collection('f').find(
    { $text: { $search: q } },                          // q comes from the user: it is a plain search string, safe from injection
    { projection: { name: 1, score: { $meta: 'textScore' } } }
  ).sort({ score: { $meta: 'textScore' } }).limit(limit).toArray();
}
```

---

## 🟠 Express.js / Mongoose Integration

Tested against MongoDB 8.0.4, Express 5, Mongoose 8.

```javascript
const express = require('express');
const mongoose = require('mongoose');
const schema = new mongoose.Schema({ name: String, desc: String });
schema.index({ name: 'text', desc: 'text' }, { weights: { name: 5 } }); // declare text index on the schema
const Food = mongoose.model('Food', schema);   // Mongoose builds the index on startup (autoIndex)
const app = express();

// GET /search?q=biryani
app.get('/search', async (req, res) => {
  const rows = await Food.find(
    { $text: { $search: String(req.query.q || '') } },
    { name: 1, score: { $meta: 'textScore' } }
  ).sort({ score: { $meta: 'textScore' } }).lean();
  res.json(rows.map(r => ({ name: r.name, score: +r.score.toFixed(2) })));
});
// Real run (docs: "Chicken Biryani" / "Veg Pulao") -> [{"name":"Chicken Biryani","score":4.5}]
```
Call `await Food.init()` (or `Food.syncIndexes()`) in tests so the index exists before the first search; in production disable `autoIndex` and create indexes in a migration.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Querying `$text` with no text index
```javascript
db.g.find({ $text: { $search: "hello" } })   // Wrong: IndexNotFound: text index required for $text query
db.g.createIndex({ a: "text" })              // Right: create it first
```

❌ Mistake 2: Expecting multi-word search to mean AND
```javascript
db.f.find({ $text: { $search: "paneer biryani" } })        // OR: returns 4 dishes
db.f.find({ $text: { $search: "\"paneer\" \"biryani\"" } })// AND of phrases: real output [] because no dish has both words
```

❌ Mistake 3: Expecting partial-word or typo matching
```javascript
db.f.find({ $text: { $search: "pane" } })     // Wrong: [] — $text matches whole (stemmed) words only
db.f.find({ name: /^pane/i })                 // Right for prefix search (or use Atlas Search autocomplete)
```

---

## 🧠 Tricky Interview Question

```javascript
db.f.find({ $text: { $search: "the" } })
```
Documents contain "the" in several descriptions. How many are returned?

Answer: **Zero** (real output `[]`). "the" is a stop word for the default English language, so it is not indexed and the search is empty. Switching the index language to `"none"` (`default_language: "none"`) disables stop words and stemming.

---

## ⚫ Interview Questions + Answers

Q1: How many text indexes can a collection have?
A1: Exactly one (it can cover multiple fields). A second `createIndex` with `"text"` fails with `IndexOptionsConflict`.

Q2: How are search terms combined?
A2: Plain words are OR-ed; quoted phrases must match as phrases; a leading `-` negates a term.

Q3: How does MongoDB rank results?
A3: `{ $meta: "textScore" }` — based on term frequency and the field weights set in the index; used in projection and sort.

Q4: `$text` vs `$regex` vs Atlas Search?
A4: `$text` — indexed, stemming, stop words, scoring, whole words only. `$regex` — arbitrary patterns, only prefix-anchored regexes are fast. Atlas Search (Lucene) — fuzzy, autocomplete, facets, synonyms, better relevance; Atlas-only so not testable on a local `mongod`.

Q5: Can `$text` be used in aggregation?
A5: Yes, but only in the first `$match` stage; the score is exposed with `{ $meta: "textScore" }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Simple site search over titles/descriptions with ranking.
- You want stemming and stop-word handling without a separate search system.
- Self-hosted MongoDB without Atlas.

❌ Avoid when:
- You need autocomplete, fuzzy/typo tolerance, synonyms, facets, highlighting — use Atlas Search or Elasticsearch.
- Several languages in one field (you can only set one default language per index, or a per-document language field).
- You only need a prefix match — a normal index + `^regex` is cheaper.

---

## 📊 Visual Diagram
```
 write:  "Creamy tomato gravy with paneer cubes"
          │ lower-case → remove stop words (with) → stem
          ▼
   tokens: creami · tomato · gravi · paneer · cube
          │
   TEXT INDEX  (token → doc ids, with weight)
          │
 query:  $search: "paneer biryani -chicken"
          │ tokenise · stem · OR · exclude "chicken"
          ▼
   matching docs ──► score ($meta textScore) ──► sort ──► results
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Text index | Index for full-text search | Full-text search के लिए index |
| `$text` / `$search` | Operator and search string | Search operator और string |
| Stemming | Reducing words to roots (runs→run) | शब्द को मूल रूप में लाना |
| Stop words | Ignored common words (the, a) | नज़रअंदाज़ होने वाले आम शब्द |
| `textScore` | Relevance score | Relevance score |
| Weights | Field importance in score | Score में field का महत्व |

---

## ⚡ 3-Line Summary
English:
1. A text index (one per collection) stems and tokenizes strings so `$text` can search words, phrases and negations with relevance scoring.
2. Multiple words are OR-ed; use quoted phrases, `-term`, `textScore` sorting and field weights to tune results.
3. It matches whole words only (no partial/fuzzy); for richer search use Atlas Search.

Hindi:
1. Text index (collection में एक) strings को stem और tokenize करता है ताकि `$text` शब्द, phrases और negation को relevance score के साथ खोज सके।
2. कई शब्द OR होते हैं; नतीजे सुधारने के लिए quoted phrases, `-term`, `textScore` sorting और field weights इस्तेमाल करो।
3. यह सिर्फ पूरे शब्द match करता है (partial/fuzzy नहीं); बेहतर search के लिए Atlas Search लो।

---

## ➡️ Next Topic
**37. Regular Expressions in MongoDB** — patterns, flags, index-friendly prefixes and regex safety.
