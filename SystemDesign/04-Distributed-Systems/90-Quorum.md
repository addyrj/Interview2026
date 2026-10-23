# 90. Quorum
# हिंदी में: Quorum — फ़ैसला या write पक्का मानने के लिए ज़रूरी न्यूनतम nodes की संख्या (आम तौर पर बहुमत), ताकि कुछ nodes गिरने पर भी डेटा सही और सुरक्षित रहे

---

## 🔵 Simple Definition (English)
A **quorum** is the **minimum number of nodes that must participate** in an operation for it to be considered successful. With **N replicas**:
- **Write quorum (W):** a write succeeds when W replicas acknowledge it.
- **Read quorum (R):** a read queries R replicas and returns the newest value.
- If **R + W > N**, every read set **overlaps** every write set → reads see the latest acknowledged write.
In consensus protocols (Raft/Paxos), the quorum is a **majority** (⌊N/2⌋ + 1), so two conflicting decisions can **never both** get a majority.

## 🔵 सरल परिभाषा (Hindi)
Quorum यानी किसी काम को सफल मानने के लिए कम से कम कितने nodes की हामी चाहिए — आम तौर पर बहुमत।
N copies हों: write W copies पर पक्का हो, read R copies से हो, और R + W > N हो तो पढ़ने वालों में कम से कम एक के पास नया डेटा ज़रूर होगा।

---

## 🔴 Problem it Solves
With replicated data:
- Writing to **all** replicas (W = N) means **one dead node blocks all writes** → low availability.
- Writing to **one** replica (W = 1) means reads may hit a replica that **doesn't have the write** → stale data, and **data loss** if that node dies.
- In leader elections, without a majority rule, **two partitions could each pick a leader** (split brain).

Quorums give a **tunable balance**: tolerate some failures **and** keep consistency guarantees.

## 🔴 यह क्यों बना? (Hindi)
सारी copies पर लिखो तो एक node बंद होते ही writes रुक जाते हैं; एक ही पर लिखो तो दूसरी copy से पुराना डेटा मिलेगा और वो node गिरा तो डेटा गया। Election में बहुमत का नियम न हो तो दो leaders बन सकते हैं।
Quorum बीच का रास्ता देता है — कुछ nodes गिरें तब भी सिस्टम चले और डेटा सही रहे।

---

## 🟢 How it Works — Step by Step

### Read/write quorum overlap

```
N = 3 replicas: A, B, C
W = 2, R = 2 → R + W = 4 > 3 ✅

Write x=5 → A ✓, B ✓  (C slow/down) → success (2 acks)
Read      → asks B, C  → B says x=5 (v2), C says x=4 (v1) → return newest (v2) ✅
Any 2-node read set shares at least one node with any 2-node write set.

Also: read repair → C is updated to v2 in the background
```

### Common configurations (N = 3)

```
┌──────────┬──────────┬─────────────────────────────────────────────────────────────┐
│ W, R     │ R+W > N? │ Behaviour                                                   │
├──────────┼──────────┼─────────────────────────────────────────────────────────────┤
│ W=3, R=1 │ yes      │ fast reads, writes fail if any node down                    │
│ W=2, R=2 │ yes ⭐    │ balanced; tolerates 1 node down for both reads & writes     │
│ W=1, R=3 │ yes      │ fast writes, reads fail if any node down                    │
│ W=1, R=1 │ no       │ fastest, highest availability, may read stale (eventual)    │
└──────────┴──────────┴─────────────────────────────────────────────────────────────┘
Fault tolerance: writes survive N − W failures; reads survive N − R failures.
```

### Majority quorum in consensus

```
Nodes  Majority  Failures tolerated
  3       2            1
  4       3            1      ← even numbers add cost without extra tolerance
  5       3            2
  7       4            3
Why majority? Any two majorities INTERSECT → two leaders/values can't both be chosen.
Cost: every write waits for the majority → latency = the slowest node in the fastest majority.
Across 3 regions: write latency ≈ RTT to the 2nd closest region.
```

### Sloppy quorum & hinted handoff (Dynamo-style, availability first)
```
Strict quorum: must use the key's designated N replicas.
Sloppy quorum: if designated replicas are down, write to OTHER healthy nodes temporarily
               (with a "hint" to forward later) → writes stay available during failures,
               but R + W > N no longer guarantees reading the latest value.
```

### Quorums don't guarantee everything
```
- Concurrent writes still need conflict resolution (timestamps/LWW, vector clocks)
- Partial write failure (write reached 1 of the required 2) → may be visible later ("not rolled back")
- Clock skew affects LWW
- Linearizability needs extra care (read repair before returning, or consensus)
```

### Cassandra consistency levels (practical)
```
ONE, TWO, THREE, QUORUM (majority of replicas across DCs), LOCAL_QUORUM (majority in local DC) ⭐,
EACH_QUORUM, ALL, ANY (write only, hinted handoff)
Common: RF=3 per DC, LOCAL_QUORUM reads & writes → strong-ish within DC, tolerant of 1 node failure,
no cross-region latency on each request.
```

## 🟢 कैसे काम करता है? (Hindi)
1. N copies; write तब सफल जब W copies "OK" कहें; read R copies से, जिसमें सबसे नया version लौटाओ।
2. R + W > N हो तो read और write के nodes में कम से कम एक साझा होगा — इसलिए नया डेटा ज़रूर मिलेगा।
3. N=3, W=2, R=2 सबसे आम: एक node गिरने पर भी reads और writes दोनों चलते हैं।
4. Consensus (Raft) में quorum = बहुमत; दो बहुमत हमेशा आपस में मिलते हैं, इसलिए दो leaders/values नहीं बन सकते। 3 nodes = 1 failure, 5 nodes = 2 failures सह सकते हैं।
5. Quorum concurrent writes के conflicts नहीं सुलझाता — उसके लिए timestamps/vector clocks; Cassandra में LOCAL_QUORUM सबसे आम।

---

## 🟡 Real World Example

**Amazon Dynamo & DynamoDB** — the Dynamo paper popularized (N, R, W) tuning, with Amazon's cart typically at N=3, R=2, W=2, plus sloppy quorums and hinted handoff for availability. DynamoDB replicates each item across 3 AZs and acknowledges writes after a quorum.

**Amazon Aurora** — stores 6 copies of data across 3 AZs, with a write quorum of 4/6 and a read quorum of 3/6. It can lose an entire AZ plus one more node and still read, and lose an AZ and still write.

**etcd / ZooKeeper / Consul** — usually run as 3 or 5 nodes. Kubernetes docs recommend an odd-sized etcd cluster: 3 tolerates 1 failure, 5 tolerates 2.

**Cassandra at Netflix/Discord/Apple** — RF=3 with LOCAL_QUORUM is the standard balance of consistency and availability per data center.

## 🟡 Real Example Hindi में
Amazon का cart N=3, R=2, W=2 पर चलता था। Aurora हर डेटा की 6 copies 3 AZ में रखता है — write के लिए 4/6, read के लिए 3/6 — पूरा AZ गिरने पर भी चलता है।
etcd/ZooKeeper 3 या 5 nodes पर चलाए जाते हैं — 3 nodes में 1 और 5 में 2 failures सह सकते हैं। Cassandra में RF=3 और LOCAL_QUORUM आम है।

---

## 🟠 My Stack Example

### Cassandra (Node.js driver) — choose consistency per query
```js
import cassandra from 'cassandra-driver';
const client = new cassandra.Client({ contactPoints: ['cass1', 'cass2', 'cass3'], localDataCenter: 'ap-south-1', keyspace: 'chat' });
const { localQuorum, one } = cassandra.types.consistencies;

// critical: message write must be durable on 2 of 3 replicas in this DC
await client.execute('INSERT INTO messages (channel_id, bucket, msg_id, author, body) VALUES (?, ?, ?, ?, ?)',
  [ch, bucket, msgId, uid, body], { prepare: true, consistency: localQuorum });

// non-critical: typing indicators / read receipts fine with ONE
await client.execute('UPDATE receipts SET last_read = ? WHERE channel_id = ? AND user_id = ?',
  [msgId, ch, uid], { prepare: true, consistency: one });
```

### MongoDB — majority write/read concerns (quorum)
```js
await Order.create([doc], { writeConcern: { w: 'majority', wtimeout: 5000 } });   // ack from majority of replica set
const o = await Order.findById(id).setOptions({ readConcern: { level: 'majority' } });
```

### Postgres synchronous replication quorum
```conf
synchronous_standby_names = 'ANY 1 (standby_a, standby_b)'   # commit waits for any 1 of 2 standbys
```

### Sizing your etcd/Consul/ZooKeeper cluster
```
3 nodes in 3 AZs → survives 1 AZ loss
5 nodes across 3 AZs (2/2/1) → survives 2 node failures (or 1 AZ)
Never 2 nodes (majority = 2 → ANY failure stops writes) — worse than 1 for availability!
```

### Quorum math helper (for interviews / capacity planning)
```js
const isConsistent = ({ N, R, W }) => R + W > N;
const writeTolerance = ({ N, W }) => N - W;      // node failures writes survive
const readTolerance  = ({ N, R }) => N - R;
console.log(isConsistent({ N: 3, R: 2, W: 2 }), writeTolerance({ N: 3, W: 2 }));   // true 1
```

---

## ⚫ Interview Questions + Answers

**Q1: What is a quorum in distributed systems?**
A1: The minimum number of nodes that must participate for an operation to succeed. With N replicas, writes need W acknowledgements and reads query R replicas. If R + W > N, read and write sets overlap, so a read sees the latest acknowledged write (with version comparison). In consensus, a majority quorum ensures any two decisions share at least one node, which prevents conflicting decisions such as two leaders.

**Q2: Why R + W > N?**
A2: If the number of replicas read plus the number written exceeds the total, then by the pigeonhole principle, at least one replica in any read set also received the latest successful write. The reader compares versions or timestamps and returns the newest. If R + W ≤ N, a read could contact only replicas that missed the write, so you get stale data.

**Q3: Why do consensus clusters use an odd number of nodes?**
A3: Majority quorum size is ⌊N/2⌋+1. A 4-node cluster needs 3 for a majority and tolerates only 1 failure, the same as 3 nodes, but costs more and adds a node to coordinate. Odd sizes maximize fault tolerance per node: 3 tolerates 1, 5 tolerates 2, 7 tolerates 3. Two nodes is the worst case, since any single failure loses the majority.

**Q4: What is a sloppy quorum and hinted handoff?**
A4: In Dynamo-style systems, when some of a key's designated replicas are unreachable, a sloppy quorum lets the write be accepted by other healthy nodes, which store it with a "hint" and hand it off to the proper replica when it recovers. This keeps writes available during failures and partitions, but weakens the R + W > N guarantee, since reads from designated replicas may miss hinted writes until handoff completes.

**Q5: How would you configure consistency for a chat app on Cassandra across two regions?**
A5: RF=3 in each region. LOCAL_QUORUM for message writes and reads, which gives strong-enough consistency within the user's region, tolerance of one node failure, and no cross-region latency per request. Cross-region replication is asynchronous, so a user switching regions might briefly not see the latest messages, which is acceptable. Use lower levels (ONE) for ephemeral data like typing indicators, and keep account and billing data in a strongly consistent store.

---

## 🔷 Trade-offs
✅ Advantages:
- Tunable consistency vs availability vs latency; tolerates node failures; prevents split decisions.

❌ Disadvantages:
- Higher latency (wait for multiple nodes; slowest in quorum); more replicas = more cost.
- Doesn't resolve concurrent-write conflicts by itself; sloppy quorums weaken guarantees.
- Cross-region quorums are slow.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Quorum | Minimum nodes for success | सफलता के लिए ज़रूरी nodes |
| N / R / W | Replicas / read count / write count | copies / पढ़ने / लिखने की संख्या |
| Majority | More than half | आधे से ज़्यादा |
| Overlap | Read and write sets share a node | दोनों सेट में साझा node |
| Replication factor | Number of copies (N) | copies की संख्या |
| Sloppy quorum | Use any healthy nodes temporarily | अस्थायी रूप से कोई भी node |
| Hinted handoff | Forward stored write later | बाद में write आगे भेजना |
| LOCAL_QUORUM | Majority within local DC | स्थानीय DC में बहुमत |
| Read repair | Fix stale replicas during reads | पढ़ते समय सुधार |

---

## ⚡ 3-Line Summary
**English:**
1. Quorum = minimum participating nodes; with N replicas, R + W > N makes reads overlap the latest write.
2. Consensus uses majority quorums (odd cluster sizes: 3 → 1 failure, 5 → 2); any two majorities intersect, preventing split decisions.
3. Tune N/R/W (or Cassandra LOCAL_QUORUM, Mongo w:majority) per data criticality; quorums add latency and don't resolve concurrent conflicts.

**Hindi:**
1. Quorum = ज़रूरी nodes; R + W > N से read को नया write ज़रूर मिलता है।
2. Consensus में बहुमत (3 → 1 failure, 5 → 2); दो बहुमत हमेशा मिलते हैं, इसलिए दो फ़ैसले नहीं बनते।
3. डेटा की ज़रूरत के हिसाब से N/R/W चुनो; latency बढ़ती है और concurrent conflicts अलग से सुलझाने पड़ते हैं।

---

## ➡️ Next Topic Suggestion
**91. Vector Clocks / Lamport Clocks** — Quorums tell you which replicas to ask; but how do you know which version is newer, or whether two writes were concurrent, when machine clocks disagree? Next: logical clocks.
