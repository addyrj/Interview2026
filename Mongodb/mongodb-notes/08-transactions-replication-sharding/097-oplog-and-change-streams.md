# 97. Oplog and Change Streams
# हिंदी में: Oplog और Change Streams

---

## 🔵 Simple Definition (English)
The **oplog** (`local.oplog.rs`) is a special **capped collection** on every replica set member that records every data-modifying operation in order; secondaries replay it to stay in sync. **Change streams** are a safe, supported API built on top of the oplog that lets applications **subscribe** to inserts, updates, deletes and more on a collection, database or the whole deployment, and **resume** after a disconnect using a resume token.

## 🔵 सरल परिभाषा (Hindi)
**Oplog** (`local.oplog.rs`) हर replica set member पर एक विशेष **capped collection** है जो हर data-बदलने वाले operation को क्रम से record करती है; secondaries इसे replay करके sync रहते हैं। **Change streams** oplog के ऊपर बना सुरक्षित, supported API है जिससे applications किसी collection, database या पूरे deployment पर inserts, updates, deletes वगैरह को **subscribe** कर सकती हैं, और disconnect के बाद resume token से **resume** कर सकती हैं।

---

## 🔴 Problem it Solves
Apps often need to react to data changes: push an "Out for delivery" notification, update a search index, invalidate a cache, or sync to a warehouse. Polling ("anything new?") wastes queries and adds latency. Tailing the raw oplog works but is internal, version-specific, undocumented in format and unsafe (rollbacks, sharding). Change streams give real-time, ordered, resumable, rollback-aware events with authentication and filtering through an aggregation pipeline.

## 🔴 यह क्यों बना? (Hindi)
Apps को अक्सर data changes पर react करना होता है: "Out for delivery" notification भेजना, search index update करना, cache invalidate करना, warehouse में sync करना। Polling ("कुछ नया है?") queries बर्बाद करती है और latency बढ़ाती है। Raw oplog tail करना काम तो करता है पर वह internal, version-specific और असुरक्षित है (rollbacks, sharding)। Change streams real-time, ordered, resumable, rollback-aware events देते हैं, authentication और aggregation pipeline से filtering के साथ।

---

## 🟢 How it Works — Step by Step

Step 1 → Every write on the primary appends one entry to `local.oplog.rs` with fields: `ts` (timestamp), `op` (`i` insert, `u` update, `d` delete, `c` command, `n` no-op), `ns` (namespace), `o` (the change), `o2` (the target `_id` for updates).
Step 2 → The oplog is **capped**: fixed size (default 5% of free disk, min 990 MB, max 50 GB), old entries are overwritten. The time between first and last entry is the **oplog window**.
Step 3 → Secondaries pull entries and apply them. Entries are **idempotent** (updates are stored as diffs/`$set` equivalents, never `$inc`).
Step 4 → `collection.watch(pipeline, options)` opens a **tailable** cursor on the oplog through the server, filtered and converted into friendly change events.
Step 5 → Each event carries an `_id` (the **resume token**). Save it; after a crash use `resumeAfter: token` or `startAfter` to continue without gaps, as long as the token is still inside the oplog window.
Step 6 → Events are only delivered once **majority-committed**, so a rollback never shows up.
Step 7 → `fullDocument: 'updateLookup'` fetches the current full document for updates (it can be newer than the change); `fullDocumentBeforeChange` (6.0+, needs `changeStreamPreAndPostImages`) returns before/after images.
Step 8 → Requires a replica set or sharded cluster (not a standalone).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Primary पर हर write `local.oplog.rs` में एक entry जोड़ती है, fields: `ts` (timestamp), `op` (`i` insert, `u` update, `d` delete, `c` command, `n` no-op), `ns` (namespace), `o` (बदलाव), `o2` (updates में target `_id`)।
Step 2 → Oplog **capped** है: fixed size (default free disk का 5%, न्यूनतम 990 MB, अधिकतम 50 GB), पुरानी entries overwrite होती हैं। पहली और आखिरी entry का अंतर **oplog window** है।
Step 3 → Secondaries entries खींचकर apply करते हैं। Entries **idempotent** हैं (updates diffs/`$set` जैसे रूप में, `$inc` नहीं)।
Step 4 → `collection.watch(pipeline, options)` server के ज़रिए oplog पर **tailable** cursor खोलता है, filter और readable change events में बदलकर।
Step 5 → हर event में `_id` (**resume token**) होता है। उसे save करो; crash के बाद `resumeAfter: token` या `startAfter` से बिना gap के continue करो, बशर्ते token अभी oplog window के अंदर हो।
Step 6 → Events तभी मिलते हैं जब वे **majority-committed** हों, इसलिए rollback कभी नहीं दिखता।
Step 7 → `fullDocument: 'updateLookup'` updates पर वर्तमान पूरा document लाता है (यह change से नया हो सकता है); `fullDocumentBeforeChange` (6.0+, `changeStreamPreAndPostImages` चाहिए) before/after images देता है।
Step 8 → Replica set या sharded cluster चाहिए (standalone नहीं)।

---

## 🟡 Real World Example
**Zomato order tracking**: when a restaurant taps "Order ready", the `orders` document status changes to `READY`. A **notification service** holds a change stream filtered to `status` updates and pushes "Your food is ready" to the customer, while a **search-sync service** updates Elasticsearch from the same stream — no polling, no dual-write bugs. If the notification service restarts, it resumes from its stored token and misses nothing (within the oplog window).

## 🟡 Real Example Hindi mein
**Zomato order tracking**: Restaurant "Order ready" दबाता है तो `orders` document का status `READY` हो जाता है। **Notification service** `status` updates पर filter किए change stream से customer को "आपका खाना तैयार है" push करती है, और **search-sync service** उसी stream से Elasticsearch update करती है — न polling, न dual-write bugs। Notification service restart हो तो अपने stored token से resume करती है और (oplog window के अंदर) कुछ नहीं छूटता।

---

## 💻 Code Example — Basic

Oplog inspection, run on MongoDB 8.0.4 replica set. (Update shown as a diff, ObjectIds vary.)

```javascript
const ol = db.getSiblingDB('local').oplog.rs;          // the oplog collection
db = db.getSiblingDB('shop');
db.o.insertOne({ a: 1 });                               // generates an 'i' entry
db.o.updateOne({ a: 1 }, { $set: { b: 2 } });           // generates a 'u' entry

ol.find({ ns: 'shop.o' }).sort({ $natural: -1 }).limit(2).forEach(e => printjson({ op: e.op, ns: e.ns, o: e.o, o2: e.o2 }));
// Output (newest first):
// { op: 'u', ns: 'shop.o', o: { '$v': 2, diff: { i: { b: 2 } } }, o2: { _id: ObjectId('...') } }
// { op: 'i', ns: 'shop.o', o: { _id: ObjectId('...'), a: 1 } }

db.getSiblingDB('local').getCollection('oplog.rs').stats().capped;   // Output: true
rs.printReplicationInfo();   // shows configured oplog size and the time window between first/last event
```

Change stream in mongosh:
```javascript
const cs = db.orders.watch([{ $match: { operationType: 'update' } }]); // only updates
while (!cs.isClosed()) {                                // blocks and waits for events
  const ev = cs.tryNext();                              // returns null when nothing new yet
  if (ev) printjson(ev);                                // print each change event
}
```

## 💻 Code Example — Advanced

Real Node driver test (MongoDB 8.0.4, replica set). A watcher filters inserts/updates, we then insert, update and delete one document, and finally resume from the first token.

```javascript
const { MongoClient } = require('mongodb');
const c = new MongoClient('mongodb://127.0.0.1:27017/?replicaSet=rs0'); await c.connect();
const col = c.db('shop').collection('orders');

const cs = col.watch(
  [{ $match: { operationType: { $in: ['insert', 'update'] } } }],   // server-side filter (delete ignored)
  { fullDocument: 'updateLookup' }                                  // include full doc on updates
);
cs.on('change', (ch) => console.log(
  ch.operationType, JSON.stringify(ch.documentKey),
  ch.fullDocument && ch.fullDocument.status,
  ch.updateDescription && JSON.stringify(ch.updateDescription.updatedFields),
  'token?', !!ch._id._data));                                       // _id._data is the resume token

await col.insertOne({ _id: 1, status: 'PLACED' });
await col.updateOne({ _id: 1 }, { $set: { status: 'OUT_FOR_DELIVERY' } });
await col.deleteOne({ _id: 1 });                                    // filtered out, not printed
```
Observed output:
```text
insert {"_id":1} PLACED undefined token? true
update {"_id":1} OUT_FOR_DELIVERY {"status":"OUT_FOR_DELIVERY"} token? true
```
The delete produced no output because the pipeline excluded it.

Resuming after a crash:
```javascript
const token = firstEvent._id;                       // persist this durably (DB/Redis) after processing
await cs.close();                                   // simulate crash/disconnect
const cs2 = col.watch([], { resumeAfter: token });  // continue AFTER that event
const next = await cs2.next();
console.log('resumed first event:', next.operationType);
// Observed output: resumed first event: update   (the insert was before the token, so skipped)
```

Pre/post images (6.0+, syntax reference):
```javascript
db.runCommand({ collMod: 'orders', changeStreamPreAndPostImages: { enabled: true } });
col.watch([], { fullDocument: 'whenAvailable', fullDocumentBeforeChange: 'whenAvailable' });
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Server-Sent Events: push order status changes to a customer's browser
app.get('/orders/:id/stream', async (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  res.flushHeaders();

  // Mongoose model.watch() returns a change stream filtered to this one order
  const stream = Order.watch(
    [{ $match: { 'documentKey._id': new mongoose.Types.ObjectId(req.params.id) } }],
    { fullDocument: 'updateLookup' }
  );
  stream.on('change', (ch) => res.write(`data: ${JSON.stringify({ status: ch.fullDocument?.status })}\n\n`));
  stream.on('error', () => res.end());

  req.on('close', () => stream.close());     // IMPORTANT: free the cursor when the browser leaves
});
```
Note: one change stream per connected user does not scale; use one shared stream plus an in-process pub/sub (or Redis) and fan out.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reading the oplog directly in application code
```javascript
// Wrong — internal format changes between versions, includes noise, can be rolled back
db.getSiblingDB('local').oplog.rs.find({ ns: 'shop.orders' })
// Right — use the supported API
db.orders.watch([...])
```

❌ Mistake 2: Not saving resume tokens
✅ Correct: After a restart you'd either miss events or reprocess everything. Persist the last processed token and use `resumeAfter`.

❌ Mistake 3: Oplog window shorter than your downtime
✅ Correct: If the token falls off the end of the oplog, resume fails with `ChangeStreamHistoryLost`. Size the oplog (`replSetResizeOplog`) to cover outages, or re-sync the data fully.

❌ Mistake 4: Opening a change stream on a standalone server
✅ Correct: Error "The $changeStream stage is only supported on replica sets". Use a replica set even in dev.

❌ Mistake 5: Not closing streams on client disconnect
✅ Correct: Each open stream holds a server cursor; leaks pile up. Close in `req.on('close')`.

---

## 🧠 Tricky Interview Question

Q: With `fullDocument: 'updateLookup'`, does `ch.fullDocument` always equal the document right after that update?

Answer: No. `updateLookup` performs a separate lookup when the event is delivered, so it returns the document's CURRENT state. If two updates happen quickly, the event for update #1 may carry the result of update #2, and for a deleted document `fullDocument` is `null`. For exact post-update state use `fullDocument: 'required'/'whenAvailable'` with `changeStreamPreAndPostImages` enabled (6.0+), which records the true post-image at the time of change. Also, `updateDescription.updatedFields` is exact, so prefer it when only the diff is needed.

---

## ⚫ Interview Questions + Answers

Q1: What is the oplog and is it a normal collection?
A1: It is a capped collection `local.oplog.rs`, only on replica set members, recording all writes in order. Fixed size; old entries are overwritten. Secondaries tail it. (Since 4.0 it can be resized online with `replSetResizeOplog`.)

Q2: Change streams vs polling vs tailing oplog?
A2: Polling = wasteful and laggy. Raw oplog tailing = unsupported and fragile. Change streams = supported, filtered with aggregation, resumable, majority-committed, works across shards.

Q3: How does a change stream resume?
A3: Each event's `_id` is a resume token. Use `resumeAfter` (or `startAfter` after an invalidate event, or `startAtOperationTime`) to continue; works only while that point is in the oplog.

Q4: Delivery guarantees?
A4: Ordered, at-least-once from the app's viewpoint if you persist tokens after processing — so handlers must be idempotent. Events are delivered only after majority commit.

Q5: Can change streams watch a whole database or cluster?
A5: Yes: `collection.watch()`, `db.watch()` (4.0+), and `client.watch()` (4.0+) for the whole deployment.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Real-time notifications, cache invalidation, search-index sync, audit trails, event-driven microservices (CDC)

❌ Avoid when:
- Standalone MongoDB (not supported)
- You need exactly-once processing without idempotency
- Massive fan-out to thousands of clients from per-client streams (use a single stream + broker like Kafka/Redis)
- Very long downtimes beyond the oplog window without a re-sync strategy

---

## 📊 Visual Diagram
```
 app write ─► PRIMARY ─► oplog (capped ring) ─► [ts=1][ts=2][ts=3] ... overwritten oldest-first
                              │
          ┌───────────────────┼─────────────────────────┐
          ▼                   ▼                         ▼
     SECONDARY 1         SECONDARY 2              $changeStream (majority-committed only)
     applies entries     applies entries                   │
                                                           ▼
                                        { operationType, documentKey, fullDocument,
                                          _id: <resume token> }
                                                           │ save token
                                                           ▼
                                             notify / cache / search index
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Oplog | Capped log of all writes | सभी writes का capped log |
| Capped collection | Fixed-size, overwrites oldest | Fixed size, पुराना overwrite होता है |
| Oplog window | Time span the oplog covers | Oplog जितना समय कवर करता है |
| Change stream | Real-time change subscription | Real-time change subscription |
| Resume token | Event `_id` used to continue | Continue करने के लिए event `_id` |
| `updateLookup` | Fetch current full doc on update | Update पर वर्तमान पूरा doc लाना |
| CDC | Change data capture | Data changes पकड़ना |
| Idempotent | Applying twice = applying once | दो बार apply = एक बार apply |

---

## ⚡ 3-Line Summary
English:
1. The oplog is a capped collection of ordered, idempotent write entries that secondaries replay.
2. Change streams expose the oplog safely as filtered, majority-committed, resumable real-time events through `watch()`.
3. Persist resume tokens, size the oplog to your worst downtime, and make handlers idempotent.

Hindi:
1. Oplog क्रमबद्ध, idempotent write entries का capped collection है जिसे secondaries replay करते हैं।
2. Change streams oplog को `watch()` से filtered, majority-committed, resumable real-time events के रूप में सुरक्षित रूप से देते हैं।
3. Resume tokens save करो, oplog को सबसे लंबे downtime के हिसाब से रखो, और handlers idempotent बनाओ।

---

## ➡️ Next Topic
**98. Sharding — Concepts and Architecture** — When one replica set is not enough: splitting data horizontally across many shards.
