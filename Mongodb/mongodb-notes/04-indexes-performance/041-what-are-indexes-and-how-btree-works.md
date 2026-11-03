# 41. What are Indexes + How B-Tree Works in MongoDB
# हिंदी में: Indexes क्या हैं और MongoDB में B-Tree कैसे काम करता है

---

## 🔵 Simple Definition (English)
An **index** is a separate, sorted data structure that stores the values of one or more fields together with a pointer to the document. MongoDB's default storage engine (WiredTiger) implements indexes as **B-trees** (B+-tree style), so lookups, range scans and sorts on the indexed field take O(log n) instead of scanning every document (a **COLLSCAN**). Like a book's index: jump to the page instead of reading the whole book.

## 🔵 सरल परिभाषा (Hindi)
**Index** एक अलग, sorted data structure है जो एक या ज़्यादा fields की values के साथ document का pointer रखता है। MongoDB का default storage engine (WiredTiger) indexes को **B-tree** के रूप में बनाता है, इसलिए indexed field पर lookup, range scan और sort O(log n) में होते हैं, हर document scan (**COLLSCAN**) करने की ज़रूरत नहीं। किताब के index जैसा: पूरी किताब पढ़ने की जगह सीधे page पर जाओ।

---

## 🔴 Problem it Solves
Without an index, `find({ userId: 42 })` reads all documents in the collection. With millions of documents that means seconds of latency and heavy CPU/IO. Indexes cut that to a handful of page reads, at the cost of extra disk/RAM and slower writes (each insert/update must also update every index).

## 🔴 यह क्यों बना? (Hindi)
Index के बिना `find({ userId: 42 })` collection के सारे documents पढ़ता है। लाखों documents हों तो सेकंडों की latency और भारी CPU/IO। Index इसे कुछ page reads तक घटा देता है, कीमत है extra disk/RAM और धीमे writes (हर insert/update को हर index भी update करना पड़ता है)।

---

## 🟢 How it Works — Step by Step

Step 1 → `createIndex({ userId: 1 })` builds a B-tree: keys (sorted userId values) -> record locations of documents.
Step 2 → A query on `userId` walks from the root node, down internal nodes (each holds many keys), to the leaf node containing the key: about 3-4 levels even for millions of keys.
Step 3 → Leaf entries point to the documents, so MongoDB does a FETCH to read each document (unless the query is covered).
Step 4 → Because keys are sorted, range queries (`$gte/$lt`) just walk neighbouring leaf entries, and `sort` on the same key needs no extra sorting.
Step 5 → Every write (insert/update/delete of an indexed field) also modifies the B-tree. More indexes = slower writes and more RAM.
Step 6 → Every collection has a default unique index on `_id`. Verify the effect with `explain()`: COLLSCAN before, IXSCAN after.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `createIndex({ userId: 1 })` एक B-tree बनाता है: keys (sorted userId) -> documents की location।
Step 2 → `userId` पर query root node से चलकर internal nodes (हर एक में कई keys) से होती हुई उस leaf तक पहुँचती है जहाँ key है: लाखों keys के लिए भी लगभग 3-4 levels।
Step 3 → Leaf entries documents की ओर इशारा करते हैं, इसलिए MongoDB FETCH करके document पढ़ता है (जब तक query covered न हो)।
Step 4 → Keys sorted हैं, इसलिए range queries बस पड़ोसी leaf entries चलती हैं, और उसी key पर `sort` को अलग sorting नहीं चाहिए।
Step 5 → हर write indexed field पर B-tree भी बदलता है। ज़्यादा indexes = धीमे writes और ज़्यादा RAM।
Step 6 → हर collection में `_id` पर default unique index होता है। `explain()` से असर देखो: पहले COLLSCAN, बाद में IXSCAN।

---

## 🟡 Real World Example
**Flipkart's** order-history page runs `orders.find({ userId })` for millions of users and tens of crores of orders. Without an index on `userId`, each page load would scan the entire orders collection. With `{ userId: 1 }` it touches only that user's entries, so the page opens in milliseconds.

## 🟡 Real Example Hindi mein
**Flipkart** का order-history page करोड़ों orders में हर user के लिए `orders.find({ userId })` चलाता है। `userId` पर index न हो तो हर page load पूरे orders collection को scan करेगा। `{ userId: 1 }` index से सिर्फ उसी user की entries छुई जाती हैं और page मिलीसेकंड में खुलता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4). 5000 orders, userId = i % 500, so each user has 10 orders
use idx_demo
// helper: print winning plan + work done
const ex = (cur) => {
  const e = cur.explain("executionStats");
  print(e.queryPlanner.winningPlan.stage, "keys", e.executionStats.totalKeysExamined,
        "docs", e.executionStats.totalDocsExamined, "returned", e.executionStats.nReturned);
};

ex(db.orders.find({ userId: 42 }))
// Output: COLLSCAN keys 0 docs 5000 returned 10    <- read ALL 5000 docs for 10 results

db.orders.createIndex({ userId: 1 })     // Output: 'userId_1'  (1 = ascending)

ex(db.orders.find({ userId: 42 }))
// Output: FETCH (over IXSCAN userId_1) keys 10 docs 10 returned 10   <- touched only 10

db.orders.getIndexes().map(i => i.name)  // Output: [ '_id_', 'userId_1' ]
```

## 💻 Code Example — Advanced

```javascript
// Which indexes are actually used? $indexStats shows usage counters since server start
db.orders.aggregate([{ $indexStats: {} }, { $project: { name: 1, "accesses.ops": 1, _id: 0 } }])
// Output: one row per index, e.g. { name: '_id_', accesses: { ops: Long('0') } }, ...
// Drop indexes with ops = 0 for a long time: they only slow down writes.

// Range scan + sorted output using the same index: no in-memory SORT stage
ex(db.orders.find({ userId: { $gte: 10, $lt: 20 } }).sort({ userId: -1 }))
// Output: FETCH keys 100 docs 100 returned 100 (the index is read backwards for -1)

// Build index in a production-friendly way: MongoDB 4.2+ builds hold locks only briefly
db.orders.createIndex({ createdAt: -1 }, { name: "createdAt_desc" })
db.orders.dropIndex("createdAt_desc")        // remove by name
db.orders.hideIndex("userId_1")              // hide: planner ignores it (safe "test before drop")
db.orders.unhideIndex("userId_1")
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose: declare indexes in the schema (built on startup when autoIndex is true)
const orderSchema = new mongoose.Schema({
  userId: { type: Number, index: true },   // single field index shortcut
  status: String,
  createdAt: Date,
});
orderSchema.index({ userId: 1, createdAt: -1 });  // compound index (see topic 43)
const Order = mongoose.model('Order', orderSchema);

// In production disable auto index creation and build indexes via migrations:
// mongoose.connect(uri, { autoIndex: false });
app.get('/api/orders', async (req, res) => {
  res.json(await Order.find({ userId: +req.query.userId }).sort({ createdAt: -1 }).limit(20));
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Indexing every field "just in case"
```javascript
// Wrong - each extra index slows every insert/update and eats RAM
db.orders.createIndex({ a: 1 }); db.orders.createIndex({ b: 1 }); db.orders.createIndex({ c: 1 })
// Right - index fields used in real queries (filter + sort), verify with explain(), drop unused ones
```

❌ Mistake 2: Never checking if the index is used
✅ Correct: always run `explain("executionStats")` and compare `totalDocsExamined` to `nReturned`.

❌ Mistake 3: Low-selectivity index (e.g., a boolean `isActive` alone) gives little benefit because it still returns a large share of documents.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.createIndex({ userId: 1 })
db.orders.find({ userId: 42 }).explain("executionStats").executionStats.totalDocsExamined
```
Answer: `10` here, not 5000 - but if the query were `{ userId: { $ne: 42 } }` the planner would still examine nearly all documents; negation operators and low-selectivity filters cannot narrow the B-tree range much. An index helps only when it can bound the search.

---

## ⚫ Interview Questions + Answers

Q1: What data structure does MongoDB use for indexes?
A1: B-trees (WiredTiger), keeping keys sorted with pointers to documents; lookups are O(log n).

Q2: What are the costs of indexes?
A2: Extra storage, RAM (working set), and slower writes since each write updates every relevant index.

Q3: What is a COLLSCAN vs IXSCAN?
A3: COLLSCAN reads every document; IXSCAN walks index keys then fetches matching documents.

Q4: Does `_id` have an index?
A4: Yes, a unique index on `_id` is created automatically and cannot be dropped.

Q5: How can you safely test dropping an index?
A5: `hideIndex()` (MongoDB 4.4+) makes the planner ignore it while it is still maintained; unhide if performance degrades.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Fields appear in frequent filters, sorts or joins ($lookup)
- Collection is large and queries are selective

❌ Avoid when:
- Collection is tiny (scan is cheap)
- Write-heavy collections where reads are rare
- Low-selectivity single-field indexes

---

## 📊 Visual Diagram
```
B-TREE on userId (simplified)

                [ 250 ]                      <- root
              /          \
        [ 100 | 180 ]   [ 330 | 410 ]        <- internal nodes
        /    |     \      /     |     \
   [1..99][100..179][180..249] [250..]...    <- leaves: sorted keys -> doc pointers
                       |
                       v  pointer
                 { userId: 200, ... }        <- the document

 find({userId:200}): root -> internal -> leaf -> doc   (3-4 hops, not 5000 docs)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Index | Sorted structure for fast lookup | Fast lookup के लिए sorted structure |
| B-tree | Balanced tree used by index | Balanced tree |
| COLLSCAN | Full collection scan | पूरे collection का scan |
| IXSCAN | Index scan | Index scan |
| Selectivity | How well a filter narrows results | Filter कितना narrow करता है |
| hideIndex | Make planner ignore index | Planner से index छुपाना |

---

## ⚡ 3-Line Summary
English:
1. Indexes are B-trees that turn full scans into O(log n) lookups.
2. They cost RAM, disk and write speed, so index only what queries need.
3. Verify with `explain("executionStats")`; remove unused ones (use `hideIndex` to test).

Hindi:
1. Index B-tree हैं जो full scan को O(log n) lookup बना देते हैं।
2. इनकी कीमत RAM, disk और write speed है, इसलिए सिर्फ ज़रूरी fields पर index बनाओ।
3. `explain("executionStats")` से जाँचो; unused हटाओ (`hideIndex` से test करो)।

---

## ➡️ Next Topic
**42. Single Field Index**
