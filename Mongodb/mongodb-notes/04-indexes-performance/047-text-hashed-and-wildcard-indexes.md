# 47. Text, Hashed and Wildcard Indexes
# हिंदी में: Text, Hashed और Wildcard Indexes

---

## 🔵 Simple Definition (English)
Three specialised index types:
- **Text index** (`{ field: "text" }`): full-text search over string fields with stemming, stop-words and relevance score (`$text`, `$search`). Only one text index per collection.
- **Hashed index** (`{ field: "hashed" }`): stores a hash of the value. Supports **equality only** (no range / sort). Used for hash-based **sharding** and even distribution.
- **Wildcard index** (`{ "$**": 1 }` or `{ "payload.$**": 1 }`): indexes many or unknown field names - for documents with dynamic/unpredictable keys.

## 🔵 सरल परिभाषा (Hindi)
तीन special index types:
- **Text index** (`{ field: "text" }`): string fields पर full-text search, stemming, stop-words और relevance score के साथ (`$text`, `$search`)। एक collection में सिर्फ एक text index।
- **Hashed index** (`{ field: "hashed" }`): value का hash store करता है। सिर्फ **equality** support (range / sort नहीं)। Hash-based **sharding** और समान distribution के लिए।
- **Wildcard index** (`{ "$**": 1 }` या `{ "payload.$**": 1 }`): कई या अनजान field names को index करता है - dynamic keys वाले documents के लिए।

---

## 🔴 Problem it Solves
A regular index cannot do word search ("mongodb tips" finding "MongoDB text search tips"), cannot spread sequential keys evenly across shards, and cannot index fields whose names you do not know in advance (user-defined attributes). These three types fill those gaps without an external search engine or hundreds of manual indexes.

## 🔴 यह क्यों बना? (Hindi)
Regular index word search ("mongodb tips" से "MongoDB text search tips" ढूँढना) नहीं कर सकता, sequential keys को shards में समान रूप से बाँट नहीं सकता, और ऐसे fields को index नहीं कर सकता जिनके नाम पहले से पता न हों (user-defined attributes)। ये तीन types बिना external search engine या सैकड़ों manual indexes के यह कमी पूरी करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 (Text) → `createIndex({ title: "text" })` tokenizes words, lowercases, stems ("indexing" -> "index") and drops stop-words.
Step 2 (Text) → `find({ $text: { $search: "mongodb" } })` matches any word; `"exact phrase"` in quotes; `-word` excludes. Sort by relevance with `{ $meta: "textScore" }`.
Step 3 (Hashed) → `createIndex({ uid: "hashed" })` stores hash(uid). `find({ uid: 5 })` uses it (verified IXSCAN) but `{ uid: { $gt: 0 } }` falls back to COLLSCAN (verified).
Step 4 (Hashed) → A hashed shard key spreads monotonically increasing keys (like ObjectId) evenly across shards, avoiding hot shards; trade-off: range queries become scatter-gather.
Step 5 (Wildcard) → `createIndex({ "payload.$**": 1 })` indexes every field under `payload` (any depth), e.g. `payload.a`, `payload.b.c`.
Step 6 (Wildcard) → One wildcard index serves queries on any single field under the path; it does not replace compound indexes for multi-field filters.
Step 7 → Check with `explain()`; wildcard indexes are bigger and slower to write than targeted indexes.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 (Text) → `createIndex({ title: "text" })` शब्दों को tokenize, lowercase, stem ("indexing" -> "index") करता है और stop-words हटाता है।
Step 2 (Text) → `find({ $text: { $search: "mongodb" } })` किसी भी शब्द से match; quotes में exact phrase; `-word` से exclude। Relevance sort `{ $meta: "textScore" }` से।
Step 3 (Hashed) → `createIndex({ uid: "hashed" })` hash(uid) store करता है। `find({ uid: 5 })` में काम आता है (IXSCAN, verified) पर `{ uid: { $gt: 0 } }` COLLSCAN बन जाती है (verified)।
Step 4 (Hashed) → Hashed shard key बढ़ते क्रम की keys (जैसे ObjectId) को shards में समान बाँटती है और hot shard से बचाती है; कीमत: range queries scatter-gather हो जाती हैं।
Step 5 (Wildcard) → `createIndex({ "payload.$**": 1 })` `payload` के नीचे हर field (किसी भी depth) को index करता है।
Step 6 (Wildcard) → एक wildcard index उस path की किसी भी एक field की query serve करता है; multi-field filters के लिए compound index का विकल्प नहीं।
Step 7 → `explain()` से जाँचो; wildcard indexes बड़े होते हैं और writes धीमे करते हैं।

---

## 🟡 Real World Example
**Flipkart** product search box uses a text index on `title` + `description` for basic keyword search (large-scale search uses Elasticsearch/Atlas Search). **Razorpay** stores webhook `payload` documents whose fields differ by event type (`payment.captured`, `refund.created`) - a wildcard index on `payload.$**` makes any payload field searchable. A sharded `events` collection uses a hashed `userId` shard key so writes are spread evenly across shards.

## 🟡 Real Example Hindi mein
**Flipkart** search box basic keyword search के लिए `title` + `description` पर text index use करता है (बड़े स्तर पर Elasticsearch/Atlas Search)। **Razorpay** webhook `payload` documents event type के हिसाब से अलग fields रखते हैं (`payment.captured`, `refund.created`) - `payload.$**` पर wildcard index से कोई भी payload field searchable हो जाती है। Sharded `events` collection hashed `userId` shard key से writes shards में समान बाँटती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4)
use special_idx
db.posts.insertMany([
  { t: "Learn MongoDB indexing fast" },
  { t: "Cooking biryani at home" },
  { t: "MongoDB text search tips" }
])

// ---- TEXT ----
db.posts.createIndex({ t: "text" })       // only ONE text index per collection
db.posts.find(
  { $text: { $search: "mongodb" } },
  { score: { $meta: "textScore" }, t: 1, _id: 0 }
).sort({ score: { $meta: "textScore" } })
// Output: [ { t: 'MongoDB text search tips', score: 0.625 },
//           { t: 'Learn MongoDB indexing fast', score: 0.625 } ]   (scores equal here; tie order may vary)

// phrase + negation: "home" but not mongodb
db.posts.find({ $text: { $search: "\"home\" -mongodb" } }).toArray().length   // Output: 1

// ---- HASHED ----
db.users2.createIndex({ uid: "hashed" })
db.users2.insertMany([{ uid: 1 }, { uid: 2 }])
db.users2.find({ uid: 1 }).explain("executionStats")        // IXSCAN(uid_hashed)  keys 1 docs 1  <- equality works
db.users2.find({ uid: { $gt: 0 } }).explain("executionStats") // COLLSCAN  <- range can't use a hashed index
```

## 💻 Code Example — Advanced

```javascript
// ---- WILDCARD ----
db.ev.createIndex({ "payload.$**": 1 })       // name: 'payload.$**_1'
db.ev.insertMany([
  { payload: { a: 1 } },
  { payload: { b: { c: 2 } } },
  { payload: { z: "q" } }
])
db.ev.find({ "payload.b.c": 2 })   // IXSCAN(payload.$**_1)  keys 1  docs 1   <- verified
db.ev.find({ "payload.z": "q" })   // IXSCAN(payload.$**_1)  keys 1  docs 1   <- verified
// Index every field of every document (use sparingly):
// db.ev.createIndex({ "$**": 1 })
// Include/exclude specific paths:
// db.ev.createIndex({ "$**": 1 }, { wildcardProjection: { "payload.big": 0, _id: 0 } })

// Multi-field text index with weights (title matters more than body)
db.articles.createIndex({ title: "text", body: "text" }, { weights: { title: 10, body: 1 }, default_language: "english" })
// Hashed shard key (needs a sharded cluster, syntax only - not runnable on a standalone):
// sh.shardCollection("shop.events", { userId: "hashed" })
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const postSchema = new mongoose.Schema({ title: String, body: String });
postSchema.index({ title: 'text', body: 'text' }, { weights: { title: 5, body: 1 } });
const Post = mongoose.model('Post', postSchema);

// GET /api/search?q=mongodb tips
app.get('/api/search', async (req, res) => {
  const q = String(req.query.q || '').slice(0, 100);        // limit input length
  const posts = await Post.find(
    { $text: { $search: q } },
    { score: { $meta: 'textScore' } }                         // include relevance score
  ).sort({ score: { $meta: 'textScore' } }).limit(10);
  res.json(posts);
});

// Wildcard in Mongoose: schemaless Mixed type + index
// eventSchema.index({ 'payload.$**': 1 });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using a hashed index for range queries or sorting
```javascript
// Wrong - COLLSCAN: hashes destroy ordering
db.users2.createIndex({ uid: "hashed" }); db.users2.find({ uid: { $gt: 100 } })
// Right - a normal index for ranges
db.users2.createIndex({ uid: 1 })
```

❌ Mistake 2: Expecting `$text` to do substring / partial-word search
✅ Correct: text search matches whole stemmed words ("mong" will not match "mongodb"). Use Atlas Search or regex (slow) for partial matching.

❌ Mistake 3: Wildcard index "just in case" on whole documents - big index, slow writes. Index only dynamic subtrees.

---

## 🧠 Tricky Interview Question

```javascript
db.posts.createIndex({ t: "text" })
db.posts.createIndex({ body: "text" })   // second text index
```
Answer: The second call **fails** - a collection can have only one text index. To cover several fields put them all in one text index: `{ t: "text", body: "text" }`. Also `$text` cannot be combined with `$near`, and sorting by `textScore` needs the `$meta` projection.

---

## ⚫ Interview Questions + Answers

Q1: How many text indexes per collection?
A1: One (it can cover multiple fields, optionally with weights, or use `"$**": "text"` for all string fields).

Q2: Why use a hashed index?
A2: For equality lookups and for hashed sharding that distributes monotonically increasing keys evenly. It cannot support range queries or sort.

Q3: When is a wildcard index appropriate?
A3: Dynamic or user-defined attribute names where you cannot create targeted indexes upfront; it indexes every field under a path.

Q4: Does a wildcard index support compound queries efficiently?
A4: It supports a query on one field at a time; for multi-field filters build a regular compound index.

Q5: Text index vs regex?
A5: Text index is word-based, stemmed and ranked and can use the index; unanchored regex scans everything and has no relevance score.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Text: simple keyword search in small/medium apps
- Hashed: even shard distribution, equality lookups
- Wildcard: schema-less attribute bags

❌ Avoid when:
- Need advanced search (fuzzy, autocomplete, facets) - use Atlas Search / Elasticsearch
- Need range/sort on hashed field
- Fields are known - prefer targeted indexes

---

## 📊 Visual Diagram
```
TEXT      "Learn MongoDB indexing fast"  ->  tokens: learn, mongodb, index, fast  -> word -> docs
HASHED    uid 1,2,3,4 ...                ->  hash(uid): scattered values           (equality only)
WILDCARD  payload:{a:1}, {b:{c:2}}       ->  keys: payload.a, payload.b.c, payload.z ...
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Text index | Word search index | शब्द search index |
| Stemming | Reduce word to root | शब्द को मूल रूप में लाना |
| textScore | Relevance score | Relevance score |
| Hashed index | Index of hash values | Hash values का index |
| Wildcard index | Index over unknown field names | अनजान field names का index |

---

## ⚡ 3-Line Summary
English:
1. Text indexes give ranked word search (one per collection); hashed indexes give equality and even sharding; wildcard indexes cover dynamic field names.
2. Hashed cannot do ranges; text is not substring search.
3. For advanced search use Atlas Search; for known fields use targeted indexes.

Hindi:
1. Text index ranked word search देता है (collection में एक); hashed equality और समान sharding; wildcard dynamic field names cover करता है।
2. Hashed range नहीं कर सकता; text substring search नहीं है।
3. Advanced search के लिए Atlas Search; known fields के लिए targeted indexes।

---

## ➡️ Next Topic
**48. explain() - Reading Query Plans**
