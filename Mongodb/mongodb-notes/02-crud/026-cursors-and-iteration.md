# 26. Cursors and Iteration
# हिंदी में: Cursors और Iteration

---

## 🔵 Simple Definition (English)
A **cursor** is a pointer to the result set of a query. `find()` does **not** return an array; it returns a cursor that fetches documents from the server **lazily, in batches** (first batch up to 101 docs / 16 MB, later batches up to 16 MB). You iterate with `hasNext()/next()`, `forEach`, `for await ... of`, or materialise with `toArray()`. Cursors also support chained modifiers: `sort`, `skip`, `limit`, `project`, `batchSize`.

## 🔵 सरल परिभाषा (Hindi)
**Cursor** एक query के result set का pointer है। `find()` array **नहीं** लौटाता; यह एक cursor लौटाता है जो server से documents **आलसी (lazy) तरीके से, batches में** लाता है (पहला batch ~101 docs तक, बाद वाले batches 16 MB तक)। Iterate करने के लिए `hasNext()/next()`, `forEach`, `for await ... of` या सब कुछ memory में लाने के लिए `toArray()` इस्तेमाल होता है। Cursor पर `sort`, `skip`, `limit`, `project`, `batchSize` जैसे modifiers chain हो सकते हैं।

---

## 🔴 Problem it Solves
A query may match 5 million documents. Returning them all in one response would blow server and client memory and the 16 MB BSON message limit. Cursors solve this by streaming results in manageable batches: the client asks for the next batch (`getMore`) only when it needs it. This keeps memory flat, lets you start processing the first rows immediately, and lets you stop early.

## 🔴 यह क्यों बना? (Hindi)
एक query 50 लाख documents match कर सकती है। सबको एक response में भेजने से server और client की memory फट जाती और 16 MB BSON message limit टूट जाती। Cursor results को छोटे batches में stream करता है: client तभी अगला batch (`getMore`) मांगता है जब ज़रूरत हो। इससे memory स्थिर रहती है, पहली rows पर काम तुरंत शुरू हो जाता है, और बीच में रुकना भी संभव है।

---

## 🟢 How it Works — Step by Step

Step 1 → `collection.find(filter)` builds a cursor object. **Nothing is sent to the server yet** — cursors are lazy until you iterate.
Step 2 → Chained modifiers (`sort`, `skip`, `limit`, `batchSize`) are recorded in the cursor. Order of writing does not matter: the server always applies **sort → skip → limit**.
Step 3 → On first `next()`/`hasNext()` the driver sends a `find` command; server returns the first batch (default: 101 documents) plus a **cursor id**.
Step 4 → When the local batch is exhausted, the driver sends `getMore` with the cursor id to fetch the next batch (until 16 MB or `batchSize`).
Step 5 → When the server has no more data, the cursor id becomes `0` and the cursor is exhausted/closed.
Step 6 → Idle cursors are killed by the server after **10 minutes** of inactivity (`cursorTimeoutMillis`). Always `close()` early-exited cursors; `for await` closes automatically on `break`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `collection.find(filter)` एक cursor object बनाता है। **अभी server को कुछ नहीं भेजा गया** — iterate करने तक cursor lazy रहता है।
Step 2 → `sort`, `skip`, `limit`, `batchSize` जैसे modifiers cursor में record होते हैं। लिखने का क्रम मायने नहीं रखता: server हमेशा **sort → skip → limit** लगाता है।
Step 3 → पहले `next()`/`hasNext()` पर driver `find` command भेजता है; server पहला batch (default 101 documents) और एक **cursor id** लौटाता है।
Step 4 → Local batch खत्म होने पर driver cursor id के साथ `getMore` भेजकर अगला batch लाता है।
Step 5 → Data खत्म होने पर cursor id `0` हो जाता है और cursor बंद।
Step 6 → 10 मिनट idle रहने पर server cursor को kill कर देता है (`cursorTimeoutMillis`)। बीच में निकलो तो `close()` करो; `for await` में `break` पर यह अपने आप होता है।

---

## 🟡 Real World Example
**Razorpay's monthly settlement export** reads ~8 million payment documents for a merchant report. The service does `payments.find({ merchantId, month }).batchSize(1000)` and streams each document into a CSV writer using `for await`. Memory stays under 50 MB no matter how many rows exist. The earlier version used `toArray()` and crashed the Node process with an out-of-memory error during festive-season volumes.

## 🟡 Real Example Hindi mein
**Razorpay का monthly settlement export** एक merchant की report के लिए ~80 लाख payment documents पढ़ता है। Service `payments.find({ merchantId, month }).batchSize(1000)` चलाती है और `for await` से हर document CSV writer में stream करती है। कितनी भी rows हों, memory 50 MB से कम रहती है। पुराना version `toArray()` इस्तेमाल करता था और festive season के volume में Node process out-of-memory से crash हो जाता था।

---

## 💻 Code Example — Basic (mongosh, tested on MongoDB 8.0.4)

```javascript
const d = db.getSiblingDB("shop");
d.nums.insertMany(Array.from({ length: 10 }, (_, i) => ({ n: i + 1 })));  // n = 1..10

// 1) Modifiers: sort -> skip(2) -> limit(3) => 3rd,4th,5th smallest
const c = d.nums.find({}, { _id: 0 }).sort({ n: 1 }).skip(2).limit(3);
print(JSON.stringify(c.toArray()));
// [{"n":3},{"n":4},{"n":5}]

// 2) Manual iteration with hasNext()/next()
const c2 = d.nums.find({}, { _id: 0 }).batchSize(2);  // fetch 2 docs per batch
print(c2.hasNext());                 // true  -> first batch fetched from server
print(JSON.stringify(c2.next()));    // {"n":1}
print(c2.objsLeftInBatch());         // 1  -> one more doc already in local batch

// 3) while loop over a cursor
const it = d.nums.find({ n: { $gt: 8 } }, { _id: 0 });
while (it.hasNext()) print(JSON.stringify(it.next()));
// {"n":9}
// {"n":10}

// 4) map / forEach are cursor methods; in mongosh map() returns a cursor -> add toArray()
print(JSON.stringify(d.nums.find({ n: { $lte: 3 } }, { _id: 0 }).map(x => x.n * 2).toArray()));
// [2,4,6]
d.nums.find({ n: { $lte: 2 } }, { _id: 0 }).forEach(x => print(JSON.stringify(x)));
// {"n":1}
// {"n":2}

// 5) Counting: do NOT iterate to count
print(d.nums.countDocuments({ n: { $gt: 5 } }), d.nums.estimatedDocumentCount());
// 5 10   (countDocuments = accurate with filter; estimated = fast, from metadata)
```

## 💻 Code Example — Advanced (Node.js driver, tested)

```javascript
const { MongoClient } = require('mongodb');
const client = new MongoClient('mongodb://127.0.0.1:27017');
await client.connect();
const col = client.db('nodedemo').collection('orders');

// A) for await...of : streams one doc at a time, closes cursor on break/throw
for await (const doc of col.find({}).sort({ _id: 1 })) {
  console.log('doc', doc._id);          // processes docs as they arrive
}

// B) Manual control + explicit close
const cur = col.find({}).batchSize(1);  // tiny batches, just to demonstrate
console.log(await cur.hasNext(), (await cur.next())._id);  // true 1
await cur.close();                       // free the server-side cursor NOW

// C) Stream large export without loading into memory
const stream = col.find({ status: 'paid' }).stream();   // Node Readable stream
stream.on('data', (doc) => csv.write(doc));             // backpressure aware
stream.on('end', () => console.log('export done'));

// D) Tailable cursor concept: only for CAPPED collections (like `tail -f`)
// col.find({}, { tailable: true, awaitData: true })

// E) Pagination: skip is O(n); prefer range-based ("keyset") pagination
const page = await col.find({ _id: { $gt: lastSeenId } }).sort({ _id: 1 }).limit(20).toArray();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose cursor: stream big results without loading all as Mongoose docs
for await (const o of Order.find({ status: 'paid' }).sort({ amt: 1 }).cursor()) {
  console.log('mongoose', o.amt);        // tested output: 11 then 21
}

// Express: paginated list using limit + lean (plain objects, less memory)
app.get('/orders', async (req, res) => {
  const limit = Math.min(+req.query.limit || 20, 100);      // cap page size! never trust client
  const filter = { amt: { $gt: +req.query.min || 0 } };
  const rows = await Order.find(filter).sort({ _id: 1 }).limit(limit).select('status amt -_id').lean();
  res.json(rows);   // tested: GET /orders?min=6&limit=5 -> [{"status":"paid","amt":11},{"status":"paid","amt":21}]
});

// Express: stream NDJSON for huge exports
app.get('/export', async (req, res) => {
  res.setHeader('Content-Type', 'application/x-ndjson');
  for await (const o of Order.find().lean().cursor()) res.write(JSON.stringify(o) + '\n');
  res.end();
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `toArray()` on huge result sets
```javascript
// Wrong — loads millions of docs into RAM
const all = await col.find({}).toArray();

// Right — stream
for await (const doc of col.find({})) { /* process one at a time */ }
```

❌ Mistake 2: Expecting `find()` to return an array
✅ Correct: `find()` returns a cursor. `console.log(find())` prints the cursor object, not data. In mongosh it auto-prints up to 20 docs (type `it` for more) but in code you must iterate.

❌ Mistake 3: Using `skip(100000)` for deep pagination
✅ Correct: `skip(n)` still walks n index entries — O(n). Use range queries (`_id > lastId` + `limit`).

❌ Mistake 4: Forgetting the cursor is **single-use**
✅ Correct: after exhaustion you cannot re-read it; call `cursor.rewind()` or create a new `find()`.

---

## 🧠 Tricky Interview Question

```javascript
db.nums.find().limit(3).skip(2).sort({ n: -1 })
// Which docs come back for n = 1..10?
```
Answer: `n = 8, 7, 6`. The order you **chain** modifiers is irrelevant — the server always applies **sort first, then skip, then limit**. Sorted descending: 10,9,8,7,6,...; skip 2 drops 10 and 9; limit 3 keeps 8,7,6. (Contrast with an aggregation pipeline, where stage order is exactly what you write.)

---

## ⚫ Interview Questions + Answers

Q1: What does `find()` return?
A1: A cursor (a lazy iterator over the result set), not an array. The query is sent when you first iterate; documents arrive in batches via `getMore` using a server-side cursor id.

Q2: What is the default batch size and the limit on a batch?
A2: The first batch returns up to 101 documents; subsequent batches are limited by 16 MiB of data. `batchSize(n)` overrides the document count per batch (it does not limit total results - `limit()` does).

Q3: What happens to an idle cursor?
A3: The server closes it after 10 minutes of inactivity (`cursorTimeoutMillis`), and the next `getMore` fails with `CursorNotFound`. Process fast, or use `noCursorTimeout` carefully (and then you MUST close it, otherwise it leaks).

Q4: `countDocuments` vs `estimatedDocumentCount` vs `cursor.count()`?
A4: `countDocuments(filter)` runs an aggregation and is accurate (supports filter). `estimatedDocumentCount()` reads collection metadata - very fast but no filter and can be off after unclean shutdown/in sharded clusters with orphans. `cursor.count()` is deprecated/removed in modern drivers.

Q5: Why is `skip()` bad for pagination?
A5: The server still scans and discards `skip` documents, so page 10,000 is far slower than page 1. Prefer keyset pagination: filter by the last seen indexed value (`_id` or a sorted key) and `limit`.

---

## 🔷 When to Use + When Not to Use
✅ Use cursors (stream/iterate) when:
- The result set is large or unknown in size (exports, ETL, migrations)
- You want to start processing before the full result arrives
- You may stop early (`break`)

❌ Avoid `toArray()` / deep `skip()` when:
- Results can be millions of docs (memory)
- Pagination depth is large (use range queries)
- Long processing per doc may exceed the 10-minute idle timeout (process in chunks, or re-query by `_id` ranges)

---

## 📊 Visual Diagram
```
 CLIENT (driver)                              SERVER
 ───────────────                              ──────
 cursor = find({..}).sort().limit()   (lazy: nothing sent yet)
 cursor.next()  ───── find cmd ─────────►  run query, build cursor #7731
                ◄──── batch 1 (101 docs) + cursorId=7731
 ...consume 101 docs locally...
 cursor.next()  ───── getMore(7731) ────►
                ◄──── batch 2 (<=16MB)  + cursorId=7731
 ...
                ◄──── last batch, cursorId=0   => cursor exhausted
 idle > 10 min  ───────────────────────►  cursor killed (CursorNotFound)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Cursor | Lazy pointer to query results | Query results का lazy pointer |
| Batch | Group of docs fetched per round trip | एक बार में आने वाले docs का group |
| getMore | Command to fetch the next batch | अगला batch लाने का command |
| batchSize | Docs per batch (not total) | प्रति batch docs |
| limit / skip | Cap results / skip first N | सीमा / पहले N छोड़ो |
| Keyset pagination | Paging by last seen key | आखिरी देखी key से paging |
| Tailable cursor | Cursor that follows a capped collection | Capped collection को follow करने वाला cursor |

---

## ⚡ 3-Line Summary
English:
1. `find()` returns a lazy cursor that streams results in batches via `getMore`.
2. Iterate with `for await`/`hasNext()`; avoid `toArray()` on big data; server applies sort, then skip, then limit.
3. Idle cursors die after 10 minutes; prefer keyset pagination over big `skip`.

Hindi:
1. `find()` एक lazy cursor लौटाता है जो `getMore` से batches में results stream करता है।
2. `for await`/`hasNext()` से iterate करो; बड़े data पर `toArray()` से बचो; server पहले sort, फिर skip, फिर limit लगाता है।
3. Idle cursor 10 मिनट में मर जाता है; बड़े `skip` की जगह keyset pagination लो।

---

## ➡️ Next Topic
**27. Write Concern and Read Concern** — how many nodes must acknowledge a write, and what data a read is allowed to see.
