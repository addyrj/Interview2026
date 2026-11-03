# 77. Anti-Patterns — Unbounded Arrays, Massive Documents
# हिंदी में: Anti-Patterns — Unbounded Arrays और Massive Documents

---

## 🔵 Simple Definition (English)
An **anti-pattern** is a design that looks fine in a demo and fails at scale. The two most famous MongoDB schema anti-patterns are **unbounded arrays** (an array inside a document that can grow without limit — comments on a post, followers of a user, events of a device) and **massive documents** (documents so large they approach the **16 MB BSON limit** or simply bloat RAM and I/O). Related smells: too many collections/indexes, unnecessary indexes, bloated documents holding rarely-read fields, case-insensitive queries without proper indexes, and separating data that is always read together.

## 🔵 सरल परिभाषा (Hindi)
**Anti-pattern** ऐसा design है जो demo में ठीक दिखता है पर scale पर फेल हो जाता है। MongoDB के दो सबसे मशहूर schema anti-patterns हैं **unbounded arrays** (document के अंदर ऐसा array जो बिना सीमा बढ़ सकता है — post के comments, user के followers, device के events) और **massive documents** (इतने बड़े documents जो **16 MB BSON limit** के पास पहुँचें या RAM और I/O फुला दें)। संबंधित smells: बहुत ज़्यादा collections/indexes, बेकार indexes, कम पढ़े जाने वाले fields से भरे bloated documents, और हमेशा साथ पढ़े जाने वाले data को अलग कर देना।

---

## 🔴 Problem it Solves
Understanding anti-patterns prevents outages that appear months after launch. An array that holds 10 items in testing holds 2 million in production: the document grows, MongoDB must relocate/rewrite it, the **entire document** is loaded into the cache even if you want one element, index entries multiply (a multikey index adds one entry per element), updates slow down, `$push` finally fails with `BSONObj size ... is invalid`, and reads of the parent become slow for everyone. It's far cheaper to avoid than to migrate away from under load.

## 🔴 यह क्यों बना? (Hindi)
Anti-patterns समझने से वे outages टलते हैं जो launch के महीनों बाद दिखते हैं। Testing में 10 items वाला array production में 20 लाख का हो जाता है: document बढ़ता है, MongoDB को उसे rewrite करना पड़ता है, एक element चाहिए तब भी **पूरा document** cache में लोड होता है, index entries बढ़ती हैं (multikey index हर element की एक entry जोड़ता है), updates धीमे हो जाते हैं, `$push` आख़िर `BSONObj size ... is invalid` से फेल होता है, और parent की reads सबके लिए धीमी हो जाती हैं। इन्हें शुरू में टालना, load में migrate करने से कहीं सस्ता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **Spot the risk**: any array whose size depends on user activity or time (comments, likes, logs, orders, followers, events) is unbounded.
Step 2 → **Understand the mechanics**: MongoDB stores a document contiguously; each `$push` grows it; the whole document is read into the WiredTiger cache and written to the oplog/journal in part or whole; the hard limit is **16 MB (16,777,216 bytes)** per document.
Step 3 → **Measure**: `$bsonSize` / `Object.bsonSize`, `$size`, and average document size from `db.coll.stats()` (`avgObjSize`).
Step 4 → **Fix the unbounded array**: move children to their own collection with a `parentId` + compound index; or cap with `$push` + `$slice` (Subset), or bucket them (Bucket pattern, note 72).
Step 5 → **Fix the massive doc**: split rarely-used big fields (full text, binaries, history) into a related collection (or GridFS for files > 16 MB), keep hot fields small.
Step 6 → **Guard**: alert when `avgObjSize` or max array length passes a threshold, and use `$jsonSchema` `maxItems` to hard-stop runaway arrays (note 75).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Risk पहचानो**: कोई भी array जिसका size user activity या समय पर निर्भर है (comments, likes, logs, orders, followers, events) unbounded है।
Step 2 → **Mechanics समझो**: MongoDB document को contiguous रखता है; हर `$push` उसे बड़ा करता है; पूरा document WiredTiger cache में आता है और oplog/journal में (पूरा या आंशिक) लिखा जाता है; hard limit **16 MB (16,777,216 bytes)** प्रति document है।
Step 3 → **नापो**: `$bsonSize` / `Object.bsonSize`, `$size`, और `db.coll.stats()` से औसत document size (`avgObjSize`)।
Step 4 → **Unbounded array ठीक करो**: children को अपनी collection में `parentId` + compound index के साथ ले जाओ; या `$push` + `$slice` से सीमित करो (Subset), या bucket करो (Bucket pattern, note 72)।
Step 5 → **Massive doc ठीक करो**: कम इस्तेमाल होने वाले बड़े fields (पूरा text, binaries, history) को related collection में डालो (16 MB से बड़ी files के लिए GridFS); hot fields छोटे रखो।
Step 6 → **Guard लगाओ**: `avgObjSize` या array length threshold पार करे तो alert, और `$jsonSchema` का `maxItems` बेकाबू arrays को रोक दे (note 75)।

---

## 🟡 Real World Example
**A social app stores `comments[]` inside each `posts` document.** Works for 20 comments. A celebrity's post goes viral: 1.5 lakh comments. Every new comment rewrites a multi-MB document, loading the post page pulls all comments into memory, the post receives a hot write lock, and eventually inserts fail at 16 MB. The fix used by **Instagram-like feeds**: `comments` collection `{ postId, userId, text, createdAt }` with index `{ postId: 1, createdAt: -1 }`, plus `post.commentCount` (Computed) and `post.topComments` (Subset, 3 items).

## 🟡 Real Example Hindi mein
**एक social app हर `posts` document के अंदर `comments[]` रखता है।** 20 comments तक ठीक चलता है। किसी celebrity की post viral होती है: 1.5 लाख comments। हर नया comment कई MB का document rewrite करता है, post page खोलने पर सारे comments memory में आते हैं, post पर hot write contention होती है, और आख़िर 16 MB पर inserts फेल होते हैं। **Instagram जैसी feeds** में fix: `comments` collection `{ postId, userId, text, createdAt }` और index `{ postId: 1, createdAt: -1 }`, साथ में `post.commentCount` (Computed) और `post.topComments` (Subset, 3 items)।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4) - SEE the anti-pattern grow
use t77
db.posts.insertOne({ _id: 1, comments: [] })

// Simulate 5,000 comments pushed into ONE document (each ~130 bytes of text)
for (let i = 0; i < 5000; i++)
  db.posts.updateOne({ _id: 1 }, { $push: { comments: { u: "user" + i, text: "nice post number " + i + " ".repeat(100) } } })

// Measure the document
db.posts.aggregate([ { $project: { n: { $size: "$comments" }, bytes: { $bsonSize: "$$ROOT" } } } ])
// Output (real): [ { _id: 1, n: 5000, bytes: 791699 } ]   <- ~0.8 MB for just 5,000 comments
// Linear growth: ~106,000 comments would reach the 16 MB (16,777,216 byte) limit
bsonsize(db.posts.findOne({ _id: 1 }))
// Output: 791699   (mongosh helper function)

// What the hard limit looks like (server-side): grow a 9 MB document beyond 16 MB
db.d.insertOne({ _id: 1, a: "x".repeat(9 * 1024 * 1024) })
db.d.updateOne({ _id: 1 }, [ { $set: { b: "$a" } } ])          // doubles the document to ~18 MB
// Output (real): MongoServerError code 10334: BSONObj size: 18874398 (0x120001E) is invalid.
//                Size must be between 0 and 16793600(16MB) ...
```

## 💻 Code Example — Advanced

```javascript
// mongosh — the FIX: child collection + Computed count + Subset of top comments

db.comments.createIndex({ postId: 1, createdAt: -1 })             // "latest comments of a post" in index order

// Add a comment: three small writes instead of growing one huge document
function addComment(postId, user, text) {
  db.comments.insertOne({ postId: postId, u: user, text: text, createdAt: new Date() }) // 1) full history in its own collection
  db.posts.updateOne({ _id: postId }, {
    $inc: { commentCount: 1 },                                    // 2) Computed: O(1) count for the UI
    $push: { topComments: { $each: [ { u: user, text: text } ], $slice: -3 } } // 3) Subset: last 3 only, never more
  })
}
db.posts.updateOne({ _id: 2 }, { $setOnInsert: { title: "Viral" } }, { upsert: true })
addComment(2, "asha", "first!")
addComment(2, "ravi", "second")

// Page the comments (range-based, cheap even at 10 lakh): newest first, 20 per page
db.comments.find({ postId: 2 }).sort({ createdAt: -1 }).limit(20)

// Hard guard so a bug can never create a runaway array again (see note 75)
db.runCommand({ collMod: "posts", validator: { $jsonSchema: { bsonType: "object",
  properties: { topComments: { bsonType: "array", maxItems: 3 } } } }, validationAction: "error" })

// Audit script: find documents whose array is already too big (run periodically)
db.posts.aggregate([
  { $project: { n: { $size: { $ifNull: ["$comments", []] } }, bytes: { $bsonSize: "$$ROOT" } } },
  { $match: { $or: [ { n: { $gt: 1000 } }, { bytes: { $gt: 1000000 } } ] } },  // >1000 items or >1 MB
  { $sort: { bytes: -1 } }, { $limit: 20 }
])
// Output for our 5,000-comment doc in the earlier demo: [ { _id: 1, n: 5000, bytes: 791699 } ]
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

// GOOD design: comments live in their own collection
const Comment = mongoose.model('Comment', new Schema({
  postId: { type: Schema.Types.ObjectId, required: true },
  user: String, text: { type: String, maxlength: 2000 },       // cap text size too
  createdAt: { type: Date, default: Date.now }
}));
Comment.schema.index({ postId: 1, createdAt: -1 });             // declare the compound index

const Post = mongoose.model('Post', new Schema({
  title: String,
  commentCount: { type: Number, default: 0 },                    // Computed
  topComments: { type: [{ user: String, text: String, _id: false }], validate: v => v.length <= 3 } // Subset, bounded
}));

const app = express();
app.use(express.json());

app.post('/posts/:id/comments', async (req, res) => {
  const { user, text } = req.body;
  const c = await Comment.create({ postId: req.params.id, user, text });
  await Post.updateOne({ _id: req.params.id }, {
    $inc: { commentCount: 1 },
    $push: { topComments: { $each: [{ user, text }], $slice: -3 } }
  });
  res.status(201).json(c);
});

// Cursor pagination: pass ?before=<ISO date> instead of skip(n) which gets slower with depth
app.get('/posts/:id/comments', async (req, res) => {
  const filter = { postId: req.params.id };
  if (req.query.before) filter.createdAt = { $lt: new Date(req.query.before) };
  res.json(await Comment.find(filter).sort({ createdAt: -1 }).limit(20).lean());
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: "It's only 100 items today" arrays
```javascript
// Wrong — followers inside the user; one celebrity = millions
db.users.updateOne({ _id: celeb }, { $push: { followers: fan } })
// Right — relationship collection, unique to prevent duplicates
db.follows.createIndex({ followeeId: 1, followerId: 1 }, { unique: true })
db.follows.insertOne({ followeeId: celeb, followerId: fan })
```

❌ Mistake 2: Putting the big rarely-read blob in the hot document
```javascript
// Wrong — 3 MB "fullText" and "revisionHistory" inside the article; the list page loads them all just to show a title
{ _id, title, fullText: "...3MB...", revisionHistory: [ ... ] }
// Right — hot doc stays small; heavy parts in article_bodies { articleId, fullText } / GridFS for big files
// and use a projection { fullText: 0 } at minimum
```
✅ Also: too many indexes (each write updates every index), indexes on low-selectivity fields, and `skip(100000)` pagination.

---

## 🧠 Tricky Interview Question

"A document has an array of 10,000 small sub-documents. We only ever read the first 3. Is that a problem? Doesn't projection `{ items: { $slice: 3 } }` fix it?"

Answer: Projection (`$slice` in find) trims what's **sent to the client**, but MongoDB still loads the **whole document** into the WiredTiger cache and parses it on the server, so cache pressure and disk I/O remain; and every `$push` still rewrites/oplogs a growing document and updates a multikey index entry per element. It reduces network, not server work. Real fixes: Subset pattern (store only the 3 hot items in the parent, full set in another collection), or the Bucket pattern. Also the 16 MB limit still bites eventually.

---

## ⚫ Interview Questions + Answers

Q1: What is the maximum BSON document size and what happens at the limit?
A1: 16 MB (16,777,216 bytes). An insert or update that makes a document larger fails (our real error: code 10334 `BSONObj size ... is invalid`). For larger files use GridFS, which splits files into 255 KB (default) chunks in `fs.chunks`.

Q2: Why are unbounded arrays harmful besides the size limit?
A2: Larger documents mean more cache usage, more disk I/O and larger oplog entries per update; multikey indexes get one entry per element; concurrent writers contend on the same document; reading a single element needs the whole document.

Q3: How do you detect problem documents?
A3: `$bsonSize` and `$size` in an aggregation sorted descending; collection stats `avgObjSize`; Atlas Performance Advisor/Schema suggestions; slow-query logs showing large `docsExamined`/`responseLength`.

Q4: What are other common MongoDB schema anti-patterns?
A4: Massive number of collections (thousands, each with indexes), unnecessary/duplicate indexes, unindexed reference fields used in `$lookup`, bloated documents, separating data that is always read together, case-insensitive regex queries without a collation index, and storing everything as strings.

Q5: How would you convert an existing unbounded array to a separate collection online?
A5: Dual-write new items to the new collection, backfill old items in batches (`$unwind` + `$merge` into the new collection), switch reads, then `$unset` the array (schemaVersion helps: note 74).

---

## 🔷 When to Use + When Not to Use
✅ Embed arrays only when:
- Bounded (hard cap enforced with `$slice`/`maxItems`) and read with the parent

❌ Avoid:
- Arrays that grow with time or user activity
- Hot documents carrying large cold fields
- Relying on projection to hide size problems

For the fix, prefer: child collection + index (unbounded), Subset (hot slice), Bucket (time series), GridFS (files).

---

## 📊 Visual Diagram
```
ANTI-PATTERN                         FIX
────────────                         ───
posts                                posts                    comments
 { _id, title,                        { _id, title,            { postId, u, text,
   comments:[ c1,c2,c3 ... c150000 ]    commentCount: 150000,    createdAt }  x 150000
 }                                      topComments:[c1..c3] }  index(postId, createdAt desc)
 grows -> 16 MB limit,                small, stable, fast;
 whole doc loaded each read           history paged from child collection
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Anti-pattern | Design that fails at scale | Scale पर फेल होने वाला design |
| Unbounded array | Array with no size cap | बिना सीमा का array |
| 16 MB limit | Max BSON document size | Document का अधिकतम size |
| `$bsonSize` | Size of a document in bytes | Document का byte size |
| GridFS | Store files > 16 MB in chunks | बड़ी files chunks में |
| Working set | Hot data/indexes in RAM | RAM में hot data |
| `avgObjSize` | Average document size in stats | औसत document size |

---

## ⚡ 3-Line Summary
English:
1. Arrays that grow with usage and oversized documents cause slow reads and writes, cache pressure, and finally failures at the 16 MB limit.
2. Move unbounded children to their own indexed collection, keep only a bounded subset and a computed count in the parent.
3. Measure with `$bsonSize`/`$size`, cap with `$slice` and `maxItems`, and note that projection does not fix server-side cost.

Hindi:
1. Usage के साथ बढ़ने वाले arrays और बड़े documents से reads/writes धीमे होते हैं, cache पर दबाव पड़ता है और आख़िर 16 MB limit पर failure होता है।
2. Unbounded children को index वाली अलग collection में ले जाओ; parent में सिर्फ़ bounded subset और computed count रखो।
3. `$bsonSize`/`$size` से नापो, `$slice` और `maxItems` से सीमित करो, और याद रखो projection server-side cost ठीक नहीं करता।

---

## ➡️ Next Topic
**Section 07 — the next section of the MongoDB notes** — builds on these schema decisions (indexing, transactions and performance).
