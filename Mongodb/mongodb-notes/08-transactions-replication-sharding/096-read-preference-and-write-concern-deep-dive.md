# 96. Read Preference and Write Concern Deep Dive
# हिंदी में: Read Preference और Write Concern की गहराई

---

## 🔵 Simple Definition (English)
Three dials control consistency vs speed in a replica set:
- **Write concern** (`w`, `j`, `wtimeout`) — how many members must confirm a write before the driver gets "OK".
- **Read preference** — WHICH member serves a read (`primary`, `primaryPreferred`, `secondary`, `secondaryPreferred`, `nearest`).
- **Read concern** (`local`, `available`, `majority`, `linearizable`, `snapshot`) — HOW up to date / how durable the data you read must be.

## 🔵 सरल परिभाषा (Hindi)
Replica set में consistency बनाम speed को तीन dials नियंत्रित करते हैं:
- **Write concern** (`w`, `j`, `wtimeout`) — driver को "OK" मिलने से पहले कितने members को write confirm करनी होगी।
- **Read preference** — read **कौन सा** member serve करेगा (`primary`, `primaryPreferred`, `secondary`, `secondaryPreferred`, `nearest`)।
- **Read concern** (`local`, `available`, `majority`, `linearizable`, `snapshot`) — जो data पढ़ा जाए वह **कितना** ताज़ा / कितना durable हो।

---

## 🔴 Problem it Solves
Not all data deserves the same guarantee. A "like" counter can lose a few increments, but a payment must never vanish after failover. Strong guarantees cost latency (waiting for other nodes), weak ones cost safety. Likewise, sending every read to the primary wastes secondaries, while reading a secondary may return stale data. These three settings let you choose per operation instead of one global trade-off.

## 🔴 यह क्यों बना? (Hindi)
हर data को एक जैसी guarantee नहीं चाहिए। "Like" counter कुछ increments खो सकता है, पर payment failover के बाद कभी गायब नहीं होना चाहिए। Strong guarantees latency (दूसरे nodes का इंतज़ार) की कीमत पर आती हैं, कमज़ोर guarantees safety की कीमत पर। इसी तरह हर read primary पर भेजना secondaries बर्बाद करता है, जबकि secondary से पढ़ने पर stale data मिल सकता है। ये तीन settings हर operation के लिए अलग trade-off चुनने देती हैं।

---

## 🟢 How it Works — Step by Step

**Write concern**
Step 1 → `w: 1` (default for non-majority-capable sets) — primary acknowledges after applying in memory. Fast; can be rolled back after failover.
Step 2 → `w: 'majority'` (default since MongoDB 5.0) — acknowledged after a majority of voting data-bearing members have the write. Survives failover.
Step 3 → `w: <N>` — N specific members; `w: 0` — fire and forget (no ack, unsafe).
Step 4 → `j: true` — also wait for the write to be in the on-disk **journal**.
Step 5 → `wtimeout` (ms) — stop waiting and return a write-concern error; the write is NOT undone.

**Read preference**
Step 6 → `primary` (default): always the primary — freshest. `primaryPreferred`: primary, else secondary. `secondary`: only secondaries. `secondaryPreferred`: secondary, else primary. `nearest`: lowest latency member (any role).
Step 7 → Tag sets and `maxStalenessSeconds` (min 90) restrict to specific data centres or limit staleness.

**Read concern**
Step 8 → `local`: whatever this node has (may be rolled back). `majority`: only data acknowledged by a majority (will not roll back). `linearizable`: primary-only, reflects all majority-acked writes before the read started (slowest). `snapshot`: for transactions.

## 🟢 कैसे काम करता है? (Hindi)
**Write concern**
Step 1 → `w: 1` — primary memory में apply करके ack देता है। तेज़; failover के बाद rollback हो सकती है।
Step 2 → `w: 'majority'` (MongoDB 5.0 से default) — voting data-bearing members के majority के पास write पहुँचने पर ack। Failover में बचती है।
Step 3 → `w: <N>` — N विशेष members; `w: 0` — बिना ack (असुरक्षित)।
Step 4 → `j: true` — on-disk **journal** में लिखे जाने का भी इंतज़ार।
Step 5 → `wtimeout` (ms) — इंतज़ार छोड़कर write-concern error दो; write undo **नहीं** होती।

**Read preference**
Step 6 → `primary` (default): हमेशा primary — सबसे ताज़ा। `primaryPreferred`: primary, नहीं तो secondary। `secondary`: सिर्फ secondaries। `secondaryPreferred`: secondary, नहीं तो primary। `nearest`: सबसे कम latency वाला member (कोई भी role)।
Step 7 → Tag sets और `maxStalenessSeconds` (न्यूनतम 90) से specific data centres या staleness सीमित की जाती है।

**Read concern**
Step 8 → `local`: इस node के पास जो है (rollback हो सकता है)। `majority`: सिर्फ majority-acked data (rollback नहीं होगा)। `linearizable`: सिर्फ primary, read शुरू होने से पहले की सारी majority-acked writes दिखाता है (सबसे धीमा)। `snapshot`: transactions के लिए।

---

## 🟡 Real World Example
**Flipkart's cart and catalog**: the product catalog page uses `readPreference: secondaryPreferred` because showing a price that is 200 ms stale is fine and it takes load off the primary. Checkout reads stock with `primary` + `readConcern: majority`, and the order insert uses `w: 'majority', j: true` — a customer who paid must never lose the order after a failover. The "recently viewed" counter uses `w: 1` for speed.

## 🟡 Real Example Hindi mein
**Flipkart का cart और catalog**: product catalog page `readPreference: secondaryPreferred` इस्तेमाल करता है क्योंकि 200 ms पुराना price दिखाना चलता है और primary का load घटता है। Checkout stock को `primary` + `readConcern: majority` से पढ़ता है, और order insert `w: 'majority', j: true` से होता है — जिस customer ने payment कर दिया उसका order failover के बाद कभी नहीं खोना चाहिए। "Recently viewed" counter गति के लिए `w: 1` इस्तेमाल करता है।

---

## 💻 Code Example — Basic

Run on a real single-node replica set (MongoDB 8.0.4). Results as observed:

```javascript
db = db.getSiblingDB('shop');

// 1. Cluster default write concern (MongoDB 5.0+ implicit default is majority)
db.adminCommand({ getDefaultRWConcern: 1 }).defaultWriteConcern;
// Output: { w: 'majority', wtimeout: 0 }

// 2. Strong write: wait for majority + journal, give up after 5 s
db.orders.insertOne({ a: 1 }, { writeConcern: { w: 'majority', j: true, wtimeout: 5000 } }).acknowledged;
// Output: true

// 3. Impossible write concern: asking for 2 members on a 1-member set
try { db.orders.insertOne({ a: 2 }, { writeConcern: { w: 2, wtimeout: 1000 } }); }
catch (e) { print(e.codeName, '-', e.message); }
// Output: UnsatisfiableWriteConcern - Not enough data-bearing nodes
// (error code 100). The server rejects it up front instead of waiting for wtimeout.

// 4. Read preference + read concern on a query
db.orders.find().readPref('secondaryPreferred').toArray().length;  // served by secondary if any, else primary
db.orders.find().readConcern('majority').toArray().length;          // only majority-committed docs
```

Observation worth noting: after the failed `w:2` insert, the document `{ a: 2 }` was still applied on the primary (write-concern errors do not undo the write), but a `readConcern: 'majority'` read could briefly show fewer documents than a `local` read until the majority commit point advanced — the exact count depends on timing.

## 💻 Code Example — Advanced

```javascript
// Node driver: set concerns at three levels (client < database/collection < operation)
const { MongoClient, ReadPreference } = require('mongodb');
const client = new MongoClient(uri, {
  w: 'majority',                         // client-level default write concern
  readPreference: 'primaryPreferred',    // client-level default
  readConcernLevel: 'majority',          // client-level default read concern
});

// Collection-level: analytics reads can hit a secondary with bounded staleness
const analytics = client.db('shop').collection('orders', {
  readPreference: new ReadPreference('secondary', null, { maxStalenessSeconds: 120 }), // <=120 s behind
});

// Tag-based routing: prefer a node tagged for the Mumbai data centre
const mumbai = new ReadPreference('nearest', [{ dc: 'mumbai' }, {}]);  // try tag, fall back to any

// Operation-level override for a critical write
await client.db('shop').collection('payments').insertOne(
  { orderId: 9, amount: 499 },
  { writeConcern: { w: 'majority', j: true, wtimeout: 3000 } }   // journaled + majority
);

// Causal consistency: read-your-own-writes even from a secondary
const session = client.startSession({ causalConsistency: true });
await orders.insertOne({ n: 1 }, { session });
const mine = await orders.findOne({ n: 1 }, { session, readPreference: 'secondary', readConcern: { level: 'majority' } });
await session.endSession();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose: per-schema write concern, per-query read preference
const orderSchema = new mongoose.Schema({ total: Number }, {
  writeConcern: { w: 'majority', j: true, wtimeout: 5000 },  // applies to saves/updates of this model
  read: 'primary',                                            // default reads for this model
});
const Order = mongoose.model('Order', orderSchema);

// Heavy dashboard endpoint -> push to secondaries
app.get('/reports/daily', async (req, res) => {
  const data = await Order.aggregate([{ $group: { _id: '$day', t: { $sum: '$total' } } }])
    .read('secondaryPreferred')            // aggregate honours read preference
    .exec();
  res.json(data);
});

// Money endpoint -> strongest write
app.post('/payments', async (req, res) => {
  const doc = await Payment.create([req.body], { writeConcern: { w: 'majority', j: true } });
  res.status(201).json(doc[0]);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Reading your own write from a secondary
```javascript
await Order.create({ ... });                         // goes to primary
const o = await Order.findById(id).read('secondary'); // may return null: not replicated yet!
// Right: read from primary, or use a causally consistent session
```

❌ Mistake 2: `w: 0` for important data
✅ Correct: `w: 0` gives no acknowledgement; network or duplicate-key errors are silently lost. Use at least `w: 1` and prefer `majority`.

❌ Mistake 3: Hard-coding `w: 3` on a 3-node set
✅ Correct: If any node is down, every write times out. `w: 'majority'` adapts to topology.

❌ Mistake 4: Assuming `wtimeout` rolls back
✅ Correct: A write-concern timeout only stops waiting. The write remains on the primary and may replicate later. Treat it as "unknown" and make writes idempotent.

❌ Mistake 5: Using `readPreference: secondary` for scale without understanding replication lag
✅ Correct: Secondaries replay all writes too, so heavy write loads limit read scaling. Measure lag with `rs.printSecondaryReplicationInfo()`; for scale, shard.

---

## 🧠 Tricky Interview Question

Q: You use `w: 'majority'` and `readConcern: 'majority'`. Is a subsequent read guaranteed to see your write?

Answer: Only if the read goes to a member that has advanced its majority commit point past your write. If the read goes to the primary right after the write acknowledged with majority, yes. If it goes to a lagging secondary, no — unless you use a **causally consistent session** (which makes the read wait until the node reaches your `afterClusterTime`) or `linearizable` on the primary. Majority/majority gives durability and no-rollback reads but not automatically read-your-writes across nodes.

---

## ⚫ Interview Questions + Answers

Q1: What is the default write concern?
A1: `w: 'majority'` since MongoDB 5.0 (for most deployments; `w: 1` when arbiters make a majority impossible). Before 5.0 it was `w: 1`.

Q2: What does `j: true` add?
A2: The member waits until the write is flushed to its on-disk journal, so it survives a process or host crash. With `w: 'majority'` on journaling members, the default behaviour already waits for journal on majority in modern versions, but explicit `j: true` states the intent.

Q3: Difference between read preference and read concern?
A3: Read preference selects the node (where). Read concern selects the data visibility level on that node (what version: local vs majority-committed vs linearizable vs snapshot).

Q4: When would you use `nearest`?
A4: Geo-distributed apps where latency matters more than freshness, e.g. serving a catalog from the closest region. Not for read-your-writes.

Q5: What are the options to avoid stale secondary reads?
A5: Read from primary, use `maxStalenessSeconds`, use causally consistent sessions, or use `linearizable` read concern for the rare strongest-consistency read.

---

## 🔷 When to Use + When Not to Use
✅ Use strong settings (`w:'majority'`, `j:true`, `primary`, `majority`) for:
- Payments, orders, inventory decrement, auth/session data

✅ Use relaxed settings (`w:1`, `secondaryPreferred`, `local`/`available`) for:
- Analytics, catalogs, logs, counters, caches where small staleness or loss is acceptable

❌ Avoid:
- `w:0` on anything you need to trust; `linearizable` on hot paths (slow)

---

## 📊 Visual Diagram
```
 WRITE  w:1            w:'majority'           w:'majority', j:true
 client ─► P (ack)     client ─► P ─► S1 ack  client ─► P ─► S1 (+journal) ack
            ▲ fast                 ▲ safe                 ▲ safest, slowest

 READ   primary │ primaryPreferred │ secondary │ secondaryPreferred │ nearest
        ┌─────┐   ┌─────┐            ┌─────┐
        │  P  │   │ S1  │  ◄── may be a few ms/secs behind P (replication lag)
        └─────┘   └─────┘

 Read concern:  local < majority < linearizable   (freshness / durability ↑, speed ↓)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Write concern | Acks required before success | Success से पहले ज़रूरी acks |
| `w: 'majority'` | Ack from majority of members | Members के majority का ack |
| `j: true` | Wait for journal flush | Journal flush का इंतज़ार |
| `wtimeout` | Max wait for write concern | Write concern का अधिकतम इंतज़ार |
| Read preference | Which node serves a read | Read कौन सा node serve करे |
| Read concern | Consistency level of data read | पढ़े गए data की consistency level |
| Causal consistency | Reads reflect prior writes in a session | Session में पिछली writes दिखना |
| `maxStalenessSeconds` | Cap on secondary lag for reads | Secondary lag की सीमा |

---

## ⚡ 3-Line Summary
English:
1. Write concern decides how many nodes confirm a write; `w:'majority'` (+`j:true`) survives failover, `w:1` can be rolled back.
2. Read preference picks the node, read concern picks the data freshness/durability; secondary reads may be stale.
3. Choose per operation: strict for money, relaxed for analytics, and use causal sessions for read-your-writes from secondaries.

Hindi:
1. Write concern तय करता है कि कितने nodes write confirm करें; `w:'majority'` (+`j:true`) failover में बचती है, `w:1` rollback हो सकती है।
2. Read preference node चुनता है, read concern data की freshness/durability; secondary reads stale हो सकती हैं।
3. हर operation के लिए चुनो: पैसों के लिए strict, analytics के लिए relaxed, और secondaries से read-your-writes के लिए causal sessions।

---

## ➡️ Next Topic
**97. Oplog and Change Streams** — The replication log that powers secondaries, and how apps can subscribe to data changes in real time.
