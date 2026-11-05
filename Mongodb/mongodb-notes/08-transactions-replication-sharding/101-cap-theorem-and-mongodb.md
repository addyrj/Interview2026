# 101. CAP Theorem and MongoDB
# हिंदी में: CAP Theorem और MongoDB

---

## 🔵 Simple Definition (English)
The **CAP theorem** says a distributed data store can guarantee only two of three properties at the same time **when a network partition happens**: **C**onsistency (every read sees the latest write), **A**vailability (every request gets a non-error response) and **P**artition tolerance (the system keeps working when nodes cannot talk to each other). Since partitions are unavoidable on real networks, the real choice is **CP vs AP**. MongoDB is by default a **CP** system: during a partition, the side that cannot reach a majority stops accepting writes (no primary), so data stays consistent at the cost of availability. With tunable read/write concerns you can lean toward availability.

## 🔵 सरल परिभाषा (Hindi)
**CAP theorem** कहता है कि एक distributed database **network partition** के समय तीन में से सिर्फ दो चीज़ें guarantee कर सकता है: **C**onsistency (हर read को latest write दिखे), **A**vailability (हर request को error-free response मिले) और **P**artition tolerance (nodes आपस में बात न कर पाएँ तब भी system चले)। Real network में partition होना तय है, इसलिए असली choice **CP बनाम AP** है। MongoDB default रूप से **CP** है: partition में जो side majority तक नहीं पहुँच पाती वहाँ primary नहीं बचता और writes बंद हो जाते हैं — data consistent रहता है, availability कम होती है। Read/Write concern बदलकर आप availability की तरफ झुक सकते हैं।

---

## 🔴 Problem it Solves
When data is copied across many servers (replica set) for safety, copies can disagree if the network breaks. Without a clear model, teams assume "we have replicas so we are always up AND always correct" — which is impossible. CAP gives a vocabulary to decide what to sacrifice: should the app return stale data (AP) or return an error/wait (CP)? For a payment ledger you want correctness; for a "likes counter" you want always-on. MongoDB exposes this decision through **replica set elections, writeConcern, readConcern and readPreference**.

## 🔴 यह क्यों बना? (Hindi)
जब data safety के लिए कई servers (replica set) पर copy होता है, network टूटने पर copies आपस में disagree कर सकती हैं। साफ model के बिना teams मान लेती हैं "replicas हैं तो हम हमेशा up भी रहेंगे और हमेशा सही भी" — जो असंभव है। CAP यह तय करने की भाषा देता है कि क्या छोड़ना है: stale data लौटाएँ (AP) या error/wait करें (CP)? Payment ledger में correctness चाहिए, "likes counter" में हमेशा चालू रहना। MongoDB यह फ़ैसला **replica set election, writeConcern, readConcern और readPreference** से कराता है।

---

## 🟢 How it Works — Step by Step

Step 1 → A replica set has 1 **primary** (takes writes) and N **secondaries** (copy the oplog). Clients write only to the primary.
Step 2 → A partition splits the 3 nodes into {Primary} | {Sec1, Sec2}.
Step 3 → The majority side (2 of 3) **elects a new primary** after `electionTimeoutMillis` (default 10 s). The old primary cannot see a majority, so it **steps down** to secondary and rejects writes -> that side loses *availability for writes* (this is the "C over A" choice).
Step 4 → Writes with `w: "majority"` are acknowledged only when a majority has them; such writes survive failover. Writes done with `w: 1` on the old primary that were not replicated are **rolled back** when it rejoins.
Step 5 → Reads: `readConcern: "majority"` returns only majority-committed data (consistent). `readPreference: "secondary"` reads from replicas that may lag (available but possibly **stale** -> AP-like).
Step 6 → Pick per operation: money = `w: majority` + `readConcern: majority` (+ `linearizable` if needed); analytics/likes = `w: 1` + secondary reads.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Replica set में 1 **primary** (writes लेता है) और N **secondaries** (oplog copy करते) होते हैं। Client सिर्फ primary पर write करता है।
Step 2 → Partition से 3 nodes बँट जाते हैं: {Primary} | {Sec1, Sec2}।
Step 3 → Majority side (3 में से 2) `electionTimeoutMillis` (default 10 s) बाद **नया primary चुनती** है। पुराना primary majority नहीं देख पाता इसलिए **step down** होकर secondary बन जाता है और writes reject करता है -> उस side की write availability जाती है (यही "C over A" choice है)।
Step 4 → `w: "majority"` वाले writes तभी acknowledge होते हैं जब majority के पास पहुँच जाएँ; ये failover में बचते हैं। पुराने primary पर `w: 1` से हुए जो writes replicate नहीं हुए, वो वापस join होने पर **rollback** हो जाते हैं।
Step 5 → Reads: `readConcern: "majority"` सिर्फ majority-committed data देता है (consistent)। `readPreference: "secondary"` lag वाले replicas से पढ़ता है (available पर **stale** हो सकता है -> AP जैसा)।
Step 6 → हर operation के हिसाब से चुनो: पैसा = `w: majority` + `readConcern: majority`; analytics/likes = `w: 1` + secondary reads।

---

## 🟡 Real World Example
**Razorpay** keeps payment records in a replica set. During a data-centre network glitch, the primary in zone A is cut off from zones B and C. Zones B+C elect a new primary within ~10 seconds; for those seconds payment-writes fail with "not primary" and the app retries (`retryWrites=true`). No two primaries accept conflicting payments — consistency preserved. Meanwhile **Swiggy's** "restaurant rating widget" reads from secondaries (`readPreference=secondaryPreferred`): it may show a rating that is a few seconds old, but the page always loads — an acceptable AP-style trade-off.

## 🟡 Real Example Hindi mein
**Razorpay** payment records replica set में रखता है। Data-centre में network glitch से zone A का primary, zone B और C से कट जाता है। B+C ~10 सेकंड में नया primary चुन लेते हैं; इन सेकंड्स में payment writes "not primary" से fail होते हैं और app retry करता है (`retryWrites=true`)। दो primaries कभी conflicting payments नहीं लेते — consistency बची रहती है। वहीं **Swiggy** का "restaurant rating widget" secondaries से पढ़ता है (`secondaryPreferred`): rating कुछ सेकंड पुरानी हो सकती है, पर page हमेशा load होता है — यह AP-style trade-off स्वीकार्य है।

---

## 💻 Code Example — Basic

```javascript
// cap-basic.js — run in mongosh. Verified on mongod 8.0.4 (standalone, port 27131)
const d = db.getSiblingDB("cap");          // pick database "cap"

// writeConcern w:"majority" -> ack only after majority of voting nodes have it (CP-leaning)
const r = d.t.insertOne(
  { a: 1 },                                 // the document
  { writeConcern: { w: "majority", wtimeout: 1000 } } // wait max 1s for majority ack
);
printjson(r.acknowledged);                  // Output: true (standalone = majority of 1)

// asking for 2 copies on a standalone server is impossible
try {
  d.t.insertOne({ a: 2 }, { writeConcern: { w: 2, wtimeout: 1000 } });
} catch (e) {
  print(e.message);                         // Output: cannot use 'w' > 1 when a host is not replicated
}

// readConcern majority -> only data that is durable on a majority
printjson(d.t.find().readConcern("majority").toArray().length); // Output: 1
```
(`w:2` error is the same mechanism that, on a real replica set, makes writes time out while a partition leaves you without a majority.)

## 💻 Code Example — Advanced

```javascript
// cap-advanced.js — Node driver: choose CP or AP behaviour PER OPERATION
const { MongoClient, ReadPreference } = require('mongodb');

// Connection string options set defaults for the whole client
const client = new MongoClient(
  'mongodb://n1:27017,n2:27017,n3:27017/?replicaSet=rs0' +
  '&w=majority' +              // default writes: majority (CP)
  '&retryWrites=true' +        // auto-retry once after a failover (handles election gap)
  '&serverSelectionTimeoutMS=15000' // how long to wait for a primary before erroring
);

async function main() {
  await client.connect();
  const db = client.db('pay');

  // CP path: money. Majority write + majority read = survives failover, no stale reads
  await db.collection('payments').insertOne(
    { orderId: 'o1', amt: 499, status: 'CAPTURED' },
    { writeConcern: { w: 'majority', j: true, wtimeout: 5000 } } // j:true = journaled
  );
  const p = await db.collection('payments').findOne(
    { orderId: 'o1' },
    { readConcern: { level: 'majority' }, readPreference: ReadPreference.PRIMARY }
  );

  // AP path: ratings widget. Read from any secondary, accept staleness, stay available
  const rating = await db.collection('ratings').findOne(
    { restaurantId: 'r9' },
    { readPreference: ReadPreference.SECONDARY_PREFERRED, maxStalenessSeconds: 90 } // reject too-lagging nodes
  );

  // Cheap counter: w:1 is fast but can be rolled back after failover
  await db.collection('likes').updateOne(
    { _id: 'post1' }, { $inc: { n: 1 } },
    { writeConcern: { w: 1 } }
  );
  console.log(p, rating);
}
main().catch(console.error).finally(() => client.close());
// Note: needs a real replica set; only the standalone mongosh part above was executed here.
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Per-route consistency choice with Mongoose
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const Payment = mongoose.model('Payment', new mongoose.Schema({ orderId: String, amt: Number }));
const Rating  = mongoose.model('Rating',  new mongoose.Schema({ restaurantId: String, avg: Number }));

// CP route: strong guarantees, may return 503 during election
app.post('/payments', async (req, res) => {
  try {
    const [doc] = await Payment.create([req.body], { writeConcern: { w: 'majority', wtimeout: 5000 } });
    res.status(201).json(doc);
  } catch (e) {
    res.status(503).json({ error: 'Temporarily unavailable, retry' }); // consistency over availability
  }
});

// AP route: serve possibly-stale data from secondaries, always respond
app.get('/ratings/:id', async (req, res) => {
  const r = await Rating.findOne({ restaurantId: req.params.id })
    .read('secondaryPreferred')   // Mongoose query option for readPreference
    .lean();
  res.json(r);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Saying "MongoDB is CA" (consistent and available, no partition)
```text
Wrong: "We run a replica set so we have C and A; partitions don't matter."
Right: Partitions DO happen. A replica set is CP by default: minority side
       cannot accept writes. Only the choice of C vs A during a partition exists.
```
❌ Mistake 2: Using default `w: 1` for critical data and assuming it is durable
```javascript
// Wrong: acknowledged by primary only; may be rolled back after failover
await payments.insertOne(doc, { writeConcern: { w: 1 } });
// Right: majority-acknowledged writes survive elections
await payments.insertOne(doc, { writeConcern: { w: 'majority' } });
```
❌ Mistake 3: Reading from secondaries and expecting read-your-own-write.
✅ Correct: secondary reads are eventually consistent; use primary reads (or causal consistency sessions) after a write.

---

## 🧠 Tricky Interview Question
**Q:** A 3-node replica set is split 1 | 2. A client connected to the isolated single node sends `insertOne` with `w: 1`. What happens, and is the write safe?

**Answer:** The isolated old primary cannot see a majority, so it steps down and (after the heartbeat timeout) refuses writes. But there is a short window *before* it steps down where it may still accept and ack a `w: 1` write. That write is not on the majority, so the 2-node side elects a new primary without it; when the old node rejoins it **rolls back** the write (saved in a `rollback` folder). Therefore `w: 1` is NOT safe under partition; `w: "majority"` would simply time out (error) instead of silently losing data. That is exactly CP behaviour: error rather than inconsistency.

---

## ⚫ Interview Questions + Answers

Q1: Is MongoDB CP or AP?
A1: By default CP: a single primary takes writes, and the minority side of a partition becomes read-only/unavailable for writes. It is tunable — secondary reads and `w:1` push it toward AP behaviour.

Q2: What is PACELC and how does it extend CAP?
A2: If **P**artition -> choose **A** or **C**; **E**lse (normal operation) -> choose **L**atency or **C**onsistency. MongoDB is PC/EC by default (majority + primary reads), but lower writeConcern/secondary reads trade consistency for latency in normal operation.

Q3: How long is MongoDB unavailable for writes during a failover?
A3: Typically ~10-12 seconds (election timeout 10 s + election). With `retryWrites` and `serverSelectionTimeoutMS` the driver hides it from the user in most cases.

Q4: What do `readConcern: "majority"` and `"linearizable"` guarantee?
A4: `majority` returns data acknowledged by a majority (won't be rolled back). `linearizable` additionally guarantees the read reflects all majority-acknowledged writes that completed before it (only on primary, slower, needs `maxTimeMS`).

Q5: Why use an odd number of voting members or an arbiter?
A5: Elections need a strict majority. 3 nodes tolerate 1 failure; 2 nodes tolerate 0 (a split leaves no majority). An arbiter votes but holds no data; it is discouraged because it weakens `w: majority` durability.

---

## 🔷 When to Use + When Not to Use
✅ Use the CP settings (majority/primary) when:
- Money, inventory, bookings, anything where a lost/stale write is a bug
- You can tolerate a few seconds of write errors during failover

✅ Use AP-leaning settings (secondary reads, `w:1`) when:
- Dashboards, counters, feeds, caches where slightly stale data is fine

❌ Avoid assuming:
- "Replica set = no downtime" or "secondary read = latest data"

---

## 📊 Visual Diagram
```
CAP in a MongoDB 3-node replica set — network partition
──────────────────────────────────────────────────────────
   BEFORE                         AFTER PARTITION
 ┌────────┐                    ┌────────┐   ╳ cut   ┌────────┐ ┌────────┐
 │PRIMARY │◄──oplog──┐         │ old    │           │PRIMARY'│◄│SECOND. │
 └────────┘          │         │PRIMARY │           │ (new)  │ │        │
 ┌────────┐ ┌────────┐         │steps   │           └────────┘ └────────┘
 │SECOND. │ │SECOND. │         │down    │            majority side (2/3)
 └────────┘ └────────┘         └────────┘            keeps taking writes
                               minority: no writes   = Consistency kept,
                               (Availability lost)     Availability partial
 w:majority  -> CP (safe, may error)    w:1 + secondary reads -> AP (fast, may be stale)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CAP | Pick 2 of C, A, P (P is forced) | तीन में से दो, P मजबूरी |
| Partition | Nodes cannot communicate | Nodes का आपस में संपर्क टूटना |
| Election | Replica set picks a new primary | नया primary चुनना |
| writeConcern | How many nodes must ack a write | Write कितने nodes पर confirm हो |
| readConcern | Consistency level of reads | Read की consistency level |
| Rollback | Undo of unreplicated writes after failover | Failover के बाद unreplicated writes हटना |
| PACELC | CAP extended with latency trade-off | CAP + latency trade-off |

---

## ⚡ 3-Line Summary
English:
1. CAP: under a partition you choose Consistency or Availability; MongoDB defaults to CP (single primary, majority elections).
2. Tune per operation with `writeConcern`, `readConcern` and `readPreference` — majority for money, secondary reads for dashboards.
3. `w:1` writes can be rolled back after failover; `w:majority` cannot.

Hindi:
1. CAP: partition में Consistency या Availability में से एक चुनना होता है; MongoDB default रूप से CP है (एक primary, majority election)।
2. `writeConcern`, `readConcern`, `readPreference` से हर operation के लिए tune करो — पैसे के लिए majority, dashboards के लिए secondary reads।
3. `w:1` writes failover के बाद rollback हो सकते हैं; `w:majority` नहीं।

---

## ➡️ Next Topic
**106. MongoDB Security Checklist (TLS, encryption, network)** — Hardening a deployment: auth, TLS, encryption at rest and network rules.
