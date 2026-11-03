# 27. Write Concern and Read Concern
# हिंदी में: Write Concern और Read Concern

---

## 🔵 Simple Definition (English)
**Write concern** controls **how many replica-set members must acknowledge a write** (and whether it must be on disk/journaled) before MongoDB tells the client "success". **Read concern** controls **how safe/consistent the data returned by a read is** (`local`, `available`, `majority`, `linearizable`, `snapshot`). Together with **read preference** (which node to read from) they let you trade speed against durability and consistency.

## 🔵 सरल परिभाषा (Hindi)
**Write concern** तय करता है कि client को "success" बताने से पहले **replica set के कितने members को write acknowledge करना होगा** (और क्या journal/disk पर लिखा होना चाहिए)। **Read concern** तय करता है कि read से मिला **data कितना सुरक्षित/consistent** है (`local`, `available`, `majority`, `linearizable`, `snapshot`)। **Read preference** (किस node से पढ़ना है) के साथ मिलकर ये speed बनाम durability/consistency का trade-off तय करते हैं।

---

## 🔴 Problem it Solves
A replica set has one primary and several secondaries replicating asynchronously. If the primary acknowledges a write immediately and then crashes before secondaries copy it, a new primary is elected **without** that write and the write is **rolled back** — the user was told "payment saved" but it is gone. Likewise, a reader may see data from the primary that later gets rolled back (a "dirty" read). Write and read concerns let you pick the level of guarantee per operation: cheap and fast for page-view counters, strict for money.

## 🔴 यह क्यों बना? (Hindi)
Replica set में एक primary और कई secondaries होते हैं जो asynchronous replicate करते हैं। अगर primary तुरंत write acknowledge कर दे और secondaries के copy करने से पहले crash हो जाए, तो नया primary उस write के **बिना** चुना जाता है और write **rollback** हो जाता है — user को "payment saved" बताया गया था पर वह गायब है। इसी तरह reader primary का ऐसा data देख सकता है जो बाद में rollback हो जाए। Write और read concern हर operation पर guarantee का स्तर चुनने देते हैं: page-view counter के लिए सस्ता/तेज़, पैसे के लिए सख्त।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends a write with a **write concern** `{ w, j, wtimeout }`.
Step 2 → `w` = number of members (or `"majority"`) that must have applied the write. `w:0` = fire-and-forget (no ack), `w:1` = primary only (**default `w:1` before 5.0; since MongoDB 5.0 the implicit default is `"majority"`** when the deployment can support it), `w:"majority"` = more than half of voting data-bearing members.
Step 3 → `j:true` = wait until the write is in the on-disk **journal** (survives a crash). With `w:"majority"` journaling is implied by default on modern versions.
Step 4 → `wtimeout` (ms) = how long to wait for acknowledgement. If it expires you get a **write concern error**, but the write may still have been applied (it is NOT undone).
Step 5 → For reads, `readConcern.level` decides the snapshot: `local` (node's latest, may roll back), `available` (like local, may return orphan docs in sharded clusters), `majority` (only data acknowledged by a majority = will not roll back), `linearizable` (reflects all majority-acked writes before the read started; primary only, slow), `snapshot` (point-in-time view, used in multi-document transactions).
Step 6 → **Causal consistency** sessions + `majority` read/write give "read your own writes" even across secondaries.
Step 7 → Defaults can be set cluster-wide (`setDefaultRWConcern`), per connection string (`w=majority`), per collection handle, or per operation (most specific wins).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client write के साथ **write concern** `{ w, j, wtimeout }` भेजता है।
Step 2 → `w` = कितने members (या `"majority"`) ने write apply कर लिया हो। `w:0` = भेजो और भूल जाओ (ack नहीं), `w:1` = सिर्फ primary (**5.0 से पहले default `w:1`; MongoDB 5.0 से implicit default `"majority"`** है जब deployment support करे), `w:"majority"` = voting data-bearing members के आधे से ज़्यादा।
Step 3 → `j:true` = write on-disk **journal** में पहुँचने तक रुको (crash में भी बचेगा)।
Step 4 → `wtimeout` (ms) = acknowledgement के लिए कितना इंतज़ार। समय खत्म तो **write concern error** आती है, पर write फिर भी apply हो चुका हो सकता है (undo नहीं होता)।
Step 5 → Reads के लिए `readConcern.level` snapshot तय करता है: `local` (node का latest, rollback हो सकता है), `available` (local जैसा, sharded में orphan docs दे सकता है), `majority` (सिर्फ majority-acked data = rollback नहीं होगा), `linearizable` (read शुरू होने से पहले के सभी majority-acked writes दिखते हैं; सिर्फ primary, slow), `snapshot` (point-in-time view, multi-document transactions में)।
Step 6 → **Causal consistency** sessions + `majority` से secondaries पर भी "अपना लिखा खुद पढ़ो" मिलता है।
Step 7 → Defaults cluster-wide (`setDefaultRWConcern`), connection string (`w=majority`), collection handle या हर operation पर सेट हो सकते हैं (सबसे specific जीतता है)।

---

## 🟡 Real World Example
**Razorpay payment ledger**: when a payment is captured, the service writes `{ paymentId, status: "captured" }` with `{ w: "majority", j: true, wtimeout: 5000 }`; it only returns HTTP 200 after a majority of nodes have it, so a primary failover cannot lose the record. The reconciliation job reads with `readConcern: "majority"` so it never reports a payment that later vanishes. Meanwhile, the **analytics click-tracker** writes page-view events with `w: 1` (or even `w: 0`) because losing an occasional event is acceptable and latency matters more.

## 🟡 Real Example Hindi mein
**Razorpay payment ledger**: payment capture होने पर service `{ paymentId, status: "captured" }` को `{ w: "majority", j: true, wtimeout: 5000 }` के साथ लिखती है; HTTP 200 तभी लौटता है जब majority nodes के पास record हो, इसलिए primary failover से record नहीं खोएगा। Reconciliation job `readConcern: "majority"` से पढ़ती है ताकि कभी ऐसा payment न दिखे जो बाद में गायब हो जाए। वहीं **analytics click-tracker** page-view events `w: 1` (या `w: 0`) से लिखता है क्योंकि कभी-कभार event खोना चलेगा और latency ज़्यादा ज़रूरी है।

---

## 💻 Code Example — Basic (mongosh; single-node replica set `rs0`, MongoDB 8.0.4)

```javascript
const d = db.getSiblingDB("wc");

// 1) Strongest common write: majority + journal + timeout
printjson(d.pay.insertOne({ _id: 1, amt: 100 },
          { writeConcern: { w: "majority", j: true, wtimeout: 5000 } }));
// { acknowledged: true, insertedId: 1 }

// 2) Asking for more members than exist -> error immediately
try {
  d.pay.insertOne({ _id: 2 }, { writeConcern: { w: 2, wtimeout: 500 } }); // only 1 node!
} catch (e) {
  print(e.codeName, e.code);   // UnsatisfiableWriteConcern 100
}
// IMPORTANT: the document _id:2 WAS still written (count later shows it). The error only says
// "could not satisfy the acknowledgement you asked for" — it is not a rollback.

// 3) Fire-and-forget: w:0 -> no acknowledgement, server replies only { ok: 1 }
printjson(d.runCommand({ insert: "pay", documents: [{ _id: 3 }], writeConcern: { w: 0 } }));
// { ok: 1 }   (you do NOT know whether it succeeded)

// 4) Read concerns
print(JSON.stringify(d.pay.find({ _id: 1 }).readConcern("majority").toArray()));
// [{"_id":1,"amt":100}]   only majority-committed data
print(JSON.stringify(d.pay.find({ _id: 1 }).readConcern("linearizable").toArray()));
// [{"_id":1,"amt":100}]   latest majority-acked; reads from primary only

// 5) Cluster default (replica sets only)
printjson(db.adminCommand({ getDefaultRWConcern: 1 }).defaultWriteConcern);
// { w: 'majority', wtimeout: 0 }   <- default in 5.0+ (output seen on this 8.0.4 server)
```

## 💻 Code Example — Advanced

```javascript
// Snapshot read + majority write inside a multi-document transaction
const s = db.getMongo().startSession();
s.startTransaction({ readConcern: { level: "snapshot" }, writeConcern: { w: "majority" } });
const c = s.getDatabase("wc").pay;
print(c.countDocuments());       // 4 (docs 1,2,3,4 at snapshot time)
s.commitTransaction();           // write concern applies at COMMIT, not per statement
print("txn ok");

// Standalone mongod (no replica set) restrictions I saw while testing:
//   w:2                    -> "cannot use 'w' > 1 when a host is not replicated"
//   readConcern 'snapshot' -> "node needs to be a replica set member to use readConcern: snapshot"
//   getDefaultRWConcern    -> "'getDefaultRWConcern' is not supported on standalone nodes."

// Set defaults for the whole cluster (admin privilege)
db.adminCommand({ setDefaultRWConcern: 1, defaultWriteConcern: { w: "majority" } });

// Atlas / production connection string: concerns live in the URI
// mongodb+srv://user:pw@cluster/db?w=majority&retryWrites=true&readConcernLevel=majority
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Node driver: concerns at client, db, collection or operation level
const { MongoClient, WriteConcern } = require('mongodb');
const client = new MongoClient(process.env.MONGO_URI, {
  writeConcern: { w: 'majority', journal: true, wtimeoutMS: 5000 }, // note: driver option names differ (journal, wtimeoutMS)
  readConcernLevel: 'majority',
});
const payments = client.db('pay').collection('payments');

// Critical route: money -> strict
app.post('/api/payments/capture', async (req, res) => {
  try {
    await payments.insertOne({ orderId: req.body.orderId, status: 'captured' },
      { writeConcern: { w: 'majority', journal: true, wtimeoutMS: 5000 } });
    res.status(201).json({ ok: true });
  } catch (e) {
    // WriteConcernError: the write MAY have been applied -> do not blindly retry; make writes idempotent (unique key)
    res.status(503).json({ error: 'not confirmed', code: e.code });
  }
});

// Non-critical route: analytics -> relaxed, per-collection handle
const events = client.db('pay').collection('events', { writeConcern: { w: 1 } });

// Mongoose: schema-level option
const paymentSchema = new mongoose.Schema({ orderId: String }, { writeConcern: { w: 'majority', j: true, wtimeout: 5000 } });
// Per-query: Payment.find().read('secondary').
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating a write concern error as "the write failed"
```javascript
// Wrong — retry blindly after wtimeout; may insert twice
try { await col.insertOne(doc, { writeConcern: { w: 'majority', wtimeout: 100 } }); }
catch { await col.insertOne(doc); }

// Right — have a unique key / idempotency key so a retry is safe, or check existence first
await col.updateOne({ idemKey }, { $setOnInsert: doc }, { upsert: true, writeConcern: { w: 'majority' } });
```

❌ Mistake 2: Using `w:0` for important data
✅ Correct: `w:0` gives no acknowledgement and no errors — even duplicate-key or network failures are invisible. Use only for disposable telemetry.

❌ Mistake 3: Reading from secondaries with `local` and expecting your own write
✅ Correct: secondary reads are stale (replication lag). Use primary reads, or causally consistent sessions with `majority`.

❌ Mistake 4: Confusing `readConcern` with `readPreference`
✅ Correct: **read preference** = WHICH node (primary, secondary, nearest). **Read concern** = WHAT consistency level of data.

---

## 🧠 Tricky Interview Question

```javascript
// 3-node replica set. Primary applies the write, then crashes before replicating.
db.orders.insertOne({ _id: 1 }, { writeConcern: { w: 1 } });  // returned success
// After failover, does the order exist?
```
Answer: Probably **no**. `w:1` is acknowledged by the primary alone; if it dies before a secondary copies the write, the new primary lacks it and when the old primary rejoins the write is **rolled back** (saved to a rollback file). The client saw success, so data was silently lost. With `w:"majority"` the write survives any failover because a majority (which must overlap the next election's majority) holds it. This is exactly why the default became `majority` in MongoDB 5.0.

---

## ⚫ Interview Questions + Answers

Q1: What are the components of a write concern?
A1: `w` (acks required: number, `"majority"`, or a tag set), `j` (wait for journal), `wtimeout` (ms before a write concern error is returned). Example: `{ w: "majority", j: true, wtimeout: 5000 }`.

Q2: What does `wtimeout` expiry mean — is the write undone?
A2: No. The write may well be applied on the primary and may replicate later; you only learn that the requested acknowledgement was not reached in time. Design retries to be idempotent.

Q3: Explain the read concern levels.
A3: `local` = newest data on that node (may roll back). `available` = like local with no orphan filtering in sharded clusters (lowest latency). `majority` = data acknowledged by a majority (rollback-safe). `linearizable` = guarantees you see every majority-acked write that completed before the read (primary only, needs `maxTimeMS`). `snapshot` = consistent point-in-time snapshot, used inside transactions.

Q4: What is the default write concern in MongoDB 5.0+?
A4: Implicit default is `w: "majority"` (unless an arbiter or other constraint makes the "majority of data-bearing voting members" unsafe, in which case it falls back to `w:1`). Before 5.0 it was `w:1`. Check with `getDefaultRWConcern`.

Q5: How do you get "read your own writes" with secondary reads?
A5: Use a causally consistent session (`startSession({ causalConsistency: true })`) together with `majority` read and write concerns; the driver passes `afterClusterTime` so a secondary waits until it has caught up to your write.

---

## 🔷 When to Use + When Not to Use
✅ Use `w:"majority"` (+ read `majority`) when:
- Money, orders, inventory, user accounts: data that must survive failover

✅ Use `w:1`/`w:0` when:
- Logs, metrics, click events, caches where occasional loss is OK and latency matters

❌ Avoid:
- `linearizable` on hot paths (slow, primary-only)
- `w:"majority"` with a tiny `wtimeout` and no retry/idempotency strategy
- `w` greater than the number of data-bearing nodes (UnsatisfiableWriteConcern / hang)

---

## 📊 Visual Diagram
```
  CLIENT ── insert {w:"majority", j:true} ──►  PRIMARY ──replicate──► SECONDARY 1
     ▲                                          │    └─replicate──► SECONDARY 2
     │                                          │
     │   ack only AFTER majority (2 of 3)       │  w:1  → ack right here  (fast, can roll back)
     └──────────────────────────────────────────┘  w:0  → no ack at all

  READ CONCERN (what you may see):
  local/available ─► latest on this node  (may be rolled back)
  majority        ─► only majority-committed data  (safe)
  linearizable    ─► majority + real-time order (primary, slow)
  snapshot        ─► point-in-time inside a transaction
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Write concern | Acknowledgement level for writes | Writes के acknowledgement का स्तर |
| `w` | Number/“majority” of nodes to ack | कितने nodes ack करें |
| `j` | Wait for journal flush | Journal में लिखे जाने तक रुको |
| `wtimeout` | Max wait for ack (ms) | Ack के लिए अधिकतम इंतज़ार |
| Read concern | Consistency level of reads | Reads की consistency का स्तर |
| Rollback | Undoing writes not on new primary | नए primary पर न मौजूद writes का undo |
| Read preference | Which node to read from | किस node से पढ़ना है |

---

## ⚡ 3-Line Summary
English:
1. Write concern = how many nodes must acknowledge (`w`, `j`, `wtimeout`); read concern = how safe the returned data is.
2. `w:1` can lose data on failover; `w:"majority"` (default since 5.0) and `majority` reads prevent rollback surprises.
3. A write-concern timeout is not a rollback; make retries idempotent. Read preference chooses the node, read concern chooses the guarantee.

Hindi:
1. Write concern = कितने nodes acknowledge करें (`w`, `j`, `wtimeout`); read concern = लौटा data कितना सुरक्षित है।
2. `w:1` failover में data खो सकता है; `w:"majority"` (5.0 से default) और `majority` reads rollback की मुसीबत रोकते हैं।
3. Write-concern timeout का मतलब rollback नहीं; retries को idempotent बनाओ। Read preference node चुनता है, read concern guarantee।

---

## ➡️ Next Topic
**28. Comparison Operators ($eq, $gt, $in, $nin)** — the building blocks of every MongoDB filter.
