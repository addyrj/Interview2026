# 65. CAP Theorem
# हिंदी में: CAP Theorem — distributed सिस्टम में नेटवर्क टूटने (Partition) पर आपको Consistency (सबको एक जैसा ताज़ा डेटा) और Availability (हर request का जवाब) में से एक चुनना पड़ता है

---

## 🔵 Simple Definition (English)
The **CAP theorem** (Eric Brewer, 2000) says a distributed data system can't **simultaneously** guarantee all three of:
- **C — Consistency:** every read gets the **most recent write** (or an error). All nodes see the same data at the same time (linearizability).
- **A — Availability:** every request to a non-failed node gets a **(non-error) response**, though it might not be the latest data.
- **P — Partition tolerance:** the system keeps working even when the **network between nodes fails** (messages lost or delayed).
Since network partitions **will** happen in real distributed systems, the real choice during a partition is **C or A**: **CP** or **AP**.

## 🔵 सरल परिभाषा (Hindi)
CAP कहता है कि distributed सिस्टम में तीनों एक साथ नहीं मिल सकते: C (सबको सबसे ताज़ा डेटा), A (हर request का जवाब), P (नेटवर्क टूटने पर भी चलना)।
नेटवर्क तो कभी न कभी टूटेगा (P ज़रूरी है), इसलिए उस समय चुनना पड़ता है: सही डेटा (CP — कुछ requests मना) या जवाब देते रहना (AP — डेटा थोड़ा पुराना हो सकता है)।

---

## 🔴 Problem it Solves
CAP is a **thinking tool**, not a technology. Once data is replicated across machines, data centers or regions, network failures between them are inevitable (cable cuts, switch failures, cloud AZ issues, GC pauses that look like partitions). Engineers must decide **in advance** what the system does when replicas **can't talk**:
- **Refuse requests** to avoid showing wrong or conflicting data? (CP)
- **Keep serving** and reconcile differences later? (AP)

The right answer depends on the business: a **bank balance** vs a **like count**. CAP forces that conversation.

## 🔴 यह क्यों बना? (Hindi)
CAP एक सोचने का तरीका है। डेटा कई मशीनों/regions में हो तो उनके बीच नेटवर्क कभी न कभी टूटेगा। पहले से तय करना होगा: उस समय requests मना करें ताकि ग़लत डेटा न दिखे (CP), या चलते रहें और बाद में डेटा मिलाएँ (AP)?
बैंक balance के लिए CP, like count के लिए AP — business तय करता है।

---

## 🟢 How it Works — Step by Step

### The partition scenario

```
        Region A (Mumbai)                    Region B (Singapore)
       ┌────────────────┐                   ┌────────────────┐
       │  Node A        │ ◄──── X ────────► │  Node B        │
       │  balance = 500 │   network broken   │  balance = 500 │
       └────────▲───────┘                   └───────▲────────┘
                │                                   │
  User 1: withdraw ₹400 at A               User 2: read balance at B

Option CP: Node B can't confirm it has the latest value → returns ERROR / waits
           (or A refuses the write because it can't replicate) → correct, but unavailable
Option AP: Node A accepts withdraw (balance 100), Node B still answers "500"
           → available, but INCONSISTENT; must reconcile when network heals
```

### CP vs AP systems

```
┌─────────────────────┬────────────────────────────────────┬───────────────────────────────────┐
│                     │ CP (Consistency over Availability) │ AP (Availability over Consistency)│
├─────────────────────┼────────────────────────────────────┼───────────────────────────────────┤
│ During partition    │ Minority side rejects/blocks       │ All sides keep serving            │
│ Data                │ Always latest (or error)           │ May be stale/conflicting          │
│ Mechanism           │ Consensus / quorum / single leader │ Replicate async, reconcile later  │
│ Examples            │ ZooKeeper, etcd, Consul, HBase,    │ Cassandra, DynamoDB (default),    │
│                     │ MongoDB (majority writes),         │ Riak, CouchDB, DNS, CDN caches,   │
│                     │ Spanner, CockroachDB, Postgres     │ shopping carts, like counters     │
│                     │ with sync replication              │                                   │
│ Use for             │ Payments, inventory decrement,     │ Feeds, likes, carts, presence,    │
│                     │ leader election, locks, config     │ product catalog, analytics        │
└─────────────────────┴────────────────────────────────────┴───────────────────────────────────┘
(Many DBs are TUNABLE: Cassandra QUORUM reads/writes behave more CP; DynamoDB strongly
 consistent reads; MongoDB readConcern/writeConcern.)
```

### Why not "CA"?
```
CA = consistent + available with NO partitions → only possible on a single node (or a network
that never fails). In any real distributed system, P is not optional. A single-node Postgres is
"CA" in a trivial sense — but it's not distributed.
```

### PACELC — the more useful extension (Daniel Abadi)

```
if Partition:   choose Availability or Consistency      (PA / PC)
Else (normal):  choose Latency or Consistency           (EL / EC)

Even WITHOUT failures, strong consistency costs latency (wait for replicas/consensus).

DynamoDB, Cassandra → PA/EL   (fast, eventually consistent by default)
Spanner, CockroachDB → PC/EC  (consistent, pays latency, e.g. cross-region commits)
MongoDB (default)   → PA/EC-ish depending on config
```

### Common misunderstandings (interviewers love these)
```
✗ "Pick any 2 of 3 forever" → No: you choose C vs A ONLY during a partition; otherwise you can have both.
✗ CAP's C = ACID's C → No: CAP C = linearizability; ACID C = constraints/invariants.
✗ Availability = uptime % → CAP's A is a strict definition: EVERY non-failed node must answer.
✓ The choice can be PER OPERATION: checkout is CP, browsing is AP — in the same product.
```

## 🟢 कैसे काम करता है? (Hindi)
1. डेटा दो जगह (Mumbai, Singapore) है और बीच का नेटवर्क टूट गया (partition)।
2. CP चुना: जो node पक्का नहीं कर सकता कि उसके पास ताज़ा डेटा है, वो error देगा — सही पर उपलब्ध नहीं।
3. AP चुना: दोनों nodes जवाब देते रहेंगे, पर अलग-अलग डेटा दिख सकता है — नेटवर्क ठीक होने पर मिलाना पड़ेगा।
4. "CA" असली distributed सिस्टम में नहीं होता, क्योंकि partition से बचा नहीं जा सकता।
5. PACELC: बिना partition के भी चुनना पड़ता है — तेज़ (latency) या पक्का consistent। और यह चुनाव हर feature के लिए अलग हो सकता है।

---

## 🟡 Real World Example

**Amazon shopping cart (Dynamo, AP)** — Amazon decided "add to cart" must always work, even during failures, because a rejected cart action means lost sales. Conflicting cart versions are merged later (union of items). Occasionally a deleted item reappears, which is an acceptable trade-off.

**Banks / UPI (CP)** — if the bank's core system can't confirm the balance, the transaction is declined ("bank server unavailable") instead of risking a double spend.

**Google Spanner (CP with very high availability)** — uses GPS and atomic clocks (TrueTime) plus Paxos to give globally consistent transactions. During a partition, the minority side can't commit, but Google's private network makes partitions rare, so it's "effectively CA" in practice (Brewer's own 2017 note).

**Facebook/Instagram likes (AP)** — like counts can differ slightly between regions for a few seconds. Nobody is harmed, and availability matters more.

**Zookeeper/etcd (CP)** — Kubernetes stores cluster state in etcd. If etcd loses quorum, the API server stops accepting writes, which is better than split-brain decisions about which pods run.

## 🟡 Real Example Hindi में
Amazon ने तय किया कि "Add to cart" हमेशा चलना चाहिए (AP) — बाद में carts मिला लेते हैं, कभी-कभी हटाया item वापस दिखता है, पर बिक्री नहीं रुकती।
बैंक/UPI CP हैं — balance पक्का न हो तो transaction मना ("bank server unavailable"), ताकि पैसा दो बार न निकले। Kubernetes का etcd quorum खोए तो writes रोक देता है।

---

## 🟠 My Stack Example

### Your typical stack's CAP behaviour
```
PostgreSQL primary + async replicas  → writes CP-ish (single primary); replica reads can be stale (AP-ish reads)
PostgreSQL + synchronous standby     → stronger C; if standby unreachable, commits wait (less A)
Redis primary + replica (async)      → failover may lose recent writes (AP-ish)
MongoDB replica set                  → w:"majority" + readConcern "majority/linearizable" → CP
                                       w:1 + secondary reads → AP-ish
DynamoDB                             → eventually consistent reads (default, AP/EL) or ConsistentRead: true
Cassandra                            → consistency level per query: ONE (AP) ... QUORUM ... ALL (CP)
etcd / Consul (service config)       → CP (Raft)
```

### Choosing per operation (same app!)
```js
// AP-style read: product listing from replica/cache — stale is fine
const products = await readerPool.query('SELECT ... FROM products WHERE city=$1', [city]);

// CP-style: wallet debit → primary, transaction, fail if primary unreachable (don't guess!)
await withTx(async (tx) => {
  const { rowCount } = await tx.query(
    'UPDATE wallets SET balance = balance - $1 WHERE user_id = $2 AND balance >= $1', [amt, uid]);
  if (!rowCount) throw new AppError(422, 'INSUFFICIENT_BALANCE');
});
// If DB is unreachable → return 503 "Please try again" — never "assume success"
```

### MongoDB: tune C vs A per query
```js
// CP-ish for orders
await Order.create([doc], { writeConcern: { w: 'majority', j: true } });
const o = await Order.findById(id).read('primary').setOptions({ readConcern: { level: 'majority' } });

// AP-ish for feed
const feed = await Post.find({ city }).read('secondaryPreferred').limit(20);
```

### DynamoDB
```js
await ddb.send(new GetCommand({ TableName: 'Wallets', Key: { userId }, ConsistentRead: true })); // strong
await ddb.send(new GetCommand({ TableName: 'Profiles', Key: { userId } }));                     // eventual (cheaper)
```

### Mobile/offline apps are AP by nature
```
React Native offline-first app (WatermelonDB/MMKV): user edits while offline (partitioned!)
→ app stays available (AP) → syncs later → conflicts resolved (last-write-wins, merge, or ask user)
But: payment/checkout screens require online confirmation (CP) → "You're offline. Connect to pay."
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the CAP theorem.**
A1: In a distributed system with replicated data, when a network partition occurs you can't provide both consistency (every read sees the latest write, i.e. linearizability) and availability (every non-failed node returns a non-error response). Partitions are unavoidable in real networks, so during a partition you choose CP (reject or block some requests to stay consistent) or AP (keep responding, possibly with stale or conflicting data, and reconcile later). Without partitions, both are possible.

**Q2: Is MongoDB/Cassandra CP or AP?**
A2: It depends on configuration, and many systems are tunable. Cassandra is designed AP (leaderless, any replica accepts writes), but with QUORUM reads and writes (R + W > N) it provides stronger consistency at the cost of availability when replicas are down. MongoDB, with a single primary and majority write and read concerns, behaves CP (a minority partition can't elect a primary or accept writes). With `w:1` and secondary reads it's more AP. Always answer with the specific settings.

**Q3: Why isn't "CA" a real option?**
A3: CA would mean consistent and available with no tolerance for partitions. In a distributed system, partitions (dropped or delayed messages) happen regardless of design, so a system must define its behaviour when they occur. Giving up P just means you haven't decided, and the system will violate C or A unpredictably. Only a single-node system is trivially CA.

**Q4: What is PACELC and why is it useful?**
A4: It extends CAP: if there's a Partition, choose Availability or Consistency. Else, in normal operation, choose Latency or Consistency. It captures that strong consistency costs latency even without failures (waiting for quorum or cross-region consensus). DynamoDB and Cassandra are PA/EL (fast, eventually consistent by default), while Spanner and CockroachDB are PC/EC. It's a better lens for real system choices.

**Q5: Design choice: for an e-commerce system, which parts would be CP and which AP?**
A5: CP: payments, wallet balances, order placement and inventory decrement for limited stock, coupon redemption limits, and seat or slot booking, where it's better to fail or retry than to double-sell. AP: product catalog browsing, search results, recommendations, reviews and ratings, cart (merge conflicts), view and like counts, delivery tracking display, and notifications, where stale-by-seconds is fine and availability drives revenue. Use different stores or settings per path.

---

## 🔷 Trade-offs
✅ CP: correct data, simpler reasoning for critical operations — ❌ errors/timeouts during partitions, higher latency.
✅ AP: always responsive, low latency, global scale — ❌ stale reads, conflicts, complex reconciliation.
✅ Tunable/per-operation: best of both — ❌ developers must understand and choose correctly.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CAP | Consistency, Availability, Partition tolerance | तीन गुण जो साथ नहीं मिलते |
| Consistency (CAP) | Every read sees latest write | हर read में सबसे ताज़ा डेटा |
| Availability (CAP) | Every request gets a response | हर request का जवाब |
| Partition | Network split between nodes | nodes के बीच नेटवर्क टूटना |
| CP system | Prefers consistency during partition | सही डेटा को प्राथमिकता |
| AP system | Prefers availability during partition | जवाब देने को प्राथमिकता |
| Linearizability | Behaves like a single up-to-date copy | एक ही ताज़ा copy जैसा व्यवहार |
| PACELC | CAP + latency vs consistency normally | CAP + सामान्य समय का चुनाव |
| Tunable consistency | Choose per query | हर query में चुनाव |

---

## ⚡ 3-Line Summary
**English:**
1. CAP: during a network partition, a distributed system must choose Consistency (CP) or Availability (AP); P is mandatory.
2. CP for money/inventory/locks (etcd, Spanner, majority-write Mongo); AP for feeds/carts/counters (Cassandra, DynamoDB default).
3. PACELC adds latency vs consistency in normal operation; choose per operation, not per company.

**Hindi:**
1. CAP: नेटवर्क टूटने पर सही डेटा (CP) या जवाब (AP) में से एक चुनना पड़ता है; P ज़रूरी है।
2. पैसे/stock/locks के लिए CP; feed/cart/counters के लिए AP।
3. PACELC: सामान्य समय में भी तेज़ी बनाम consistency; हर feature के लिए अलग चुनाव।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Martin Kleppmann — CAP theorem critique](https://www.youtube.com/results?search_query=CAP+theorem+martin+kleppmann) | Why CAP is often misunderstood, PACELC model |
| 📺 YouTube | [ByteByteGo — CAP Theorem](https://www.youtube.com/results?search_query=CAP+theorem+system+design+bytebytego) | Which databases are CP vs AP, practical examples |
| 📝 Article | [Martin Kleppmann — Please stop calling databases CP or AP](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html) | Best article explaining CAP's real-world limitations |
| 📝 Article | [DDIA Chapter 9 — Consistency and Consensus](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/) | Linearizability, Raft, 2PC — deepest treatment available |
| 🐙 GitHub | [system-design-primer — CAP Theorem](https://github.com/donnemartin/system-design-primer#cap-theorem) | CP vs AP examples, network partition scenarios |

---

## ➡️ Next Topic Suggestion
**66. Strong Consistency** — CP systems promise "always the latest data". Next: what strong consistency (linearizability) means exactly, how databases achieve it (single leader, synchronous replication, consensus), and what it costs.
