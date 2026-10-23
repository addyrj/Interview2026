# 66. Strong Consistency
# हिंदी में: Strong Consistency — कोई भी, कहीं से भी पढ़े, उसे हमेशा सबसे ताज़ा लिखा हुआ डेटा ही मिलेगा; सिस्टम ऐसे बर्ताव करता है जैसे डेटा की एक ही copy हो

---

## 🔵 Simple Definition (English)
**Strong consistency** means that once a write is **acknowledged**, **every subsequent read** (from any client, any replica, any region) returns that write or a newer one. The system behaves **as if there were a single copy** of the data and operations happened one at a time in real-time order. The formal term is **linearizability**.

## 🔵 सरल परिभाषा (Hindi)
Strong consistency का मतलब: जैसे ही write पक्का ("OK") हुआ, उसके बाद कोई भी, किसी भी सर्वर से पढ़े — उसे वही नया डेटा मिलेगा।
सिस्टम ऐसे चलता है जैसे डेटा की बस एक ही copy है — कभी पुराना डेटा नहीं दिखता।

---

## 🔴 Problem it Solves
With replicated data and **eventual consistency**, reads can return **stale** values. For some operations, stale data is **dangerous**:
- **Double spending:** two withdrawals both see "balance = ₹500".
- **Overselling:** two buyers both see "1 item left".
- **Wrong decisions:** two nodes both believe they're the leader (split brain).
- **Confusing UX:** "I changed my password but the old one still works."

Strong consistency makes the distributed system **as easy to reason about as a single machine**: no anomalies to handle in application code.

## 🔴 यह क्यों बना? (Hindi)
Replicas से पुराना डेटा पढ़ने पर ख़तरा है: दो withdrawals दोनों को ₹500 दिखे, दो ग्राहकों को "1 item बचा" दिखे, दो nodes ख़ुद को leader समझें।
Strong consistency distributed सिस्टम को एक मशीन जितना आसान बना देती है — ऐप में ऐसी गड़बड़ियाँ संभालनी ही नहीं पड़तीं।

---

## 🟢 How it Works — Step by Step

### What linearizability guarantees

```
Real time ──────────────────────────────────────────────►
Client A:  write(x=1) ──── ack ✓
Client B:                         read(x) → MUST return 1 (not 0)
Client C:                                   read(x) → MUST return 1

If any read after the ack could return 0 → NOT strongly consistent.
Also: once ANY client has read the new value, no later read may return the old one.
```

### How systems achieve it

```
1. Single leader + reads from leader
   All writes AND reads go to the primary. Simple. (Postgres primary, MongoDB primary reads)
   Leader failover must not lose acked writes → needs sync replication or consensus.

2. Synchronous replication
   Primary waits for replica(s) to confirm before ack → replicas never behind acked data.
   RDS Multi-AZ standby, Postgres synchronous_standby_names.

3. Quorum reads + writes (leaderless)
   N replicas, write to W, read from R, with R + W > N → read set overlaps write set
   (Cassandra QUORUM/QUORUM with N=3: W=2, R=2) — plus repair/timestamps
   (Strict linearizability needs extra care; quorums give "strong-ish" read-your-latest.)

4. Consensus protocols (Raft / Paxos)
   A majority of nodes agree on the order of every write (replicated log).
   Leader election + log replication; reads via leader with lease or ReadIndex.
   etcd, Consul, ZooKeeper (ZAB), CockroachDB, TiDB, Spanner (Paxos), Kafka KRaft.

5. Global clocks (Spanner TrueTime)
   Commit-wait on bounded clock uncertainty → externally consistent transactions worldwide.
```

### Raft in one picture

```
           client write x=5
                 │
            ┌────▼────┐   append entry #42 "x=5"
            │ LEADER  │─────────────┬──────────────┐
            └────┬────┘             ▼              ▼
                 │            ┌──────────┐   ┌──────────┐
                 │            │Follower 1│   │Follower 2│
                 │            └────┬─────┘   └────┬─────┘
                 │◄──── ack #42 ───┘              │ (slow)
     majority (2 of 3) has it → COMMIT → apply → reply "OK" to client
Leader dies → followers elect a new leader that HAS all committed entries → no acked write lost
Minority partition can't commit → unavailable (CP)
```

### The costs

```
Latency:      every write waits for replicas/majority; cross-region quorum = 100+ ms per write
Availability: during partitions, minority side can't serve (CP)
Throughput:   leader bottleneck; coordination overhead
Complexity:   consensus, leader leases, fencing, clock bounds
→ Use strong consistency where correctness requires it, not everywhere.
```

### Consistency models ladder (strongest → weakest)

```
Strict/Linearizable   → real-time single-copy behaviour                  (etcd, Spanner)
Sequential            → all see same order, not necessarily real-time
Causal                → cause-before-effect order preserved                (Topic 91)
Read-your-writes      → you always see your own writes
Monotonic reads       → never see time go backwards
Eventual              → replicas converge "eventually"                    (Topic 67)
```

## 🟢 कैसे काम करता है? (Hindi)
1. सबसे आसान तरीका: सारे reads और writes एक ही leader (primary) से।
2. Synchronous replication: primary तब तक "OK" नहीं देता जब तक replica ने डेटा पक्का न कर लिया हो।
3. Quorum: N copies में से W पर लिखो और R से पढ़ो, जहाँ R + W > N — पढ़ने वालों में कम से कम एक के पास नया डेटा होगा।
4. Consensus (Raft/Paxos): बहुमत (majority) nodes हर write के क्रम पर सहमत होते हैं; leader गिरे तो नया leader सब पक्के writes के साथ चुना जाता है।
5. क़ीमत: हर write में इंतज़ार (latency), partition में कुछ हिस्सा बंद, और ज़्यादा जटिलता — इसलिए सिर्फ़ ज़रूरी जगह इस्तेमाल करो।

---

## 🟡 Real World Example

**Google Spanner** — globally distributed SQL with external consistency, used for Google Ads billing and Gmail metadata. It uses Paxos replication per shard plus TrueTime (GPS and atomic clocks) to order transactions worldwide.

**Kubernetes / etcd** — all cluster state (which pods run where) is stored in etcd using Raft. Strong consistency prevents two schedulers from making conflicting decisions.

**CockroachDB at fintechs, YugabyteDB, TiDB at Indian companies** — Raft-based distributed SQL used where horizontal scale and strong consistency are both required (payments, ledgers).

**Bank core systems** — account balances are always read from the authoritative ledger (primary), never from a lagging replica, before authorizing a debit.

## 🟡 Real Example Hindi में
Google Spanner दुनिया भर में strongly consistent SQL देता है — Google Ads billing इस पर चलती है, atomic clocks और Paxos की मदद से।
Kubernetes का पूरा cluster state etcd (Raft) में रहता है, ताकि दो schedulers आपस में टकराने वाले फ़ैसले न लें। बैंक debit से पहले balance हमेशा primary ledger से पढ़ते हैं।

---

## 🟠 My Stack Example

### Postgres: strong reads = read from primary
```js
// critical read-before-write → primary + transaction (+ lock if needed)
await withTx(async (tx) => {
  const { rows: [w] } = await tx.query('SELECT balance FROM wallets WHERE user_id=$1 FOR UPDATE', [uid]);
  if (w.balance < amt) throw new AppError(422, 'INSUFFICIENT_BALANCE');
  await tx.query('UPDATE wallets SET balance = balance - $1 WHERE user_id = $2', [amt, uid]);
});
// never use the replica pool for this path
```

### Postgres synchronous replication (no acked write lost on failover)
```conf
# primary postgresql.conf
synchronous_commit = on
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'   # wait for 1 standby to confirm
# AWS: RDS Multi-AZ / Aurora (quorum of 4/6 storage copies) gives this without manual config
```

### MongoDB linearizable read
```js
await Wallet.updateOne({ userId, balance: { $gte: amt } }, { $inc: { balance: -amt } },
                       { writeConcern: { w: 'majority' } });
const w = await Wallet.findOne({ userId }).read('primary').setOptions({ readConcern: { level: 'linearizable' }, maxTimeMS: 2000 });
```

### Cassandra: quorum for "strong-ish" reads
```js
const q = 'SELECT seats_left FROM shows WHERE show_id = ?';
await client.execute(q, [showId], { consistency: cassandra.types.consistencies.quorum });
// RF=3, write QUORUM (2) + read QUORUM (2) → overlap → latest value
```

### etcd / Consul for coordination (CP store)
```js
// leader election / config that MUST be consistent
import { Etcd3 } from 'etcd3';
const etcd = new Etcd3({ hosts: 'http://etcd:2379' });
await etcd.put('config/payment-gateway').value('razorpay');           // replicated via Raft
const gw = await etcd.get('config/payment-gateway').string();         // linearizable by default
```

### UX tip for mobile: show strong-consistency waits honestly
```
Payment screen: "Processing…" until the server confirms the COMMITTED result;
don't optimistically show "Paid ✓" (optimistic UI is for likes, not money).
```

---

## ⚫ Interview Questions + Answers

**Q1: What is strong consistency (linearizability)?**
A1: A guarantee that operations appear to take effect atomically at some point between their start and completion, in real-time order. After a write is acknowledged, every subsequent read from any client or replica returns that value or a newer one, and once a client observes a new value, nobody can observe an older one later. The system behaves like a single, up-to-date copy.

**Q2: How do distributed databases achieve strong consistency?**
A2: By routing reads and writes through a single leader with synchronous replication, by quorum reads and writes where R + W > N so reads overlap the latest write, or by consensus protocols (Raft/Paxos) where a majority agrees on a replicated log of operations, with leader election and safe reads (leader leases or ReadIndex). Spanner adds tightly bounded global clocks (TrueTime) for externally consistent multi-region transactions.

**Q3: What does strong consistency cost?**
A3: Latency, because writes and sometimes reads wait for replicas or a majority, which is very expensive across regions. Availability, because during partitions the minority side can't serve consistent requests (CP). Throughput, because a single leader per shard becomes a bottleneck. And operational complexity. That's why systems use it selectively, for money, inventory, locks and metadata.

**Q4: What's the difference between strong consistency and read-your-writes?**
A4: Read-your-writes is weaker: it only guarantees that a client sees its own writes, for example by routing that user to the primary after a write. Other clients may still see stale data. Strong consistency guarantees all clients see the latest acknowledged write. Many products only need read-your-writes for good UX, which is much cheaper to provide.

**Q5: When would you require strong consistency in a system design interview?**
A5: For operations where stale reads cause incorrect irreversible outcomes: financial balances and ledgers, payment state, inventory reservations for scarce stock, seat or slot booking, unique username or handle claims, leader election, distributed locks, configuration and service metadata, and permission revocations. I'd keep these on a single-leader ACID database or a consensus-based store, and let the rest (feeds, counts, catalog) be eventually consistent.

---

## 🔷 Trade-offs
✅ Advantages:
- Simple programming model; no stale reads or conflicts; correct for critical data.

❌ Disadvantages:
- Higher latency (especially geo-distributed), lower availability during partitions.
- Leader bottlenecks; complex consensus and failover machinery.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Strong consistency | Always read latest acked write | हमेशा सबसे ताज़ा डेटा |
| Linearizability | Single-copy, real-time order behaviour | एक copy जैसा व्यवहार |
| Synchronous replication | Wait for replica before ack | replica का इंतज़ार करके OK |
| Quorum | Majority / overlapping set of nodes | बहुमत nodes |
| Consensus | Nodes agreeing on a value/order | nodes की सहमति |
| Raft / Paxos | Consensus algorithms | सहमति के algorithms |
| Leader | Node coordinating writes | writes संभालने वाला node |
| Split brain | Two leaders at once | एक साथ दो leaders |
| TrueTime | Spanner's bounded-uncertainty clock | Spanner की घड़ी |

---

## ⚡ 3-Line Summary
**English:**
1. Strong consistency (linearizability): after a write is acked, every read everywhere sees it — like one copy.
2. Achieved via single leader + sync replication, quorums (R+W>N), or consensus (Raft/Paxos); Spanner adds TrueTime.
3. Costs latency and availability during partitions — use it for money, inventory, locks, metadata.

**Hindi:**
1. Strong consistency: write पक्का होते ही हर जगह से वही नया डेटा दिखे — जैसे एक ही copy।
2. तरीके: एक leader + sync replication, quorum (R+W>N), या Raft/Paxos।
3. क़ीमत: latency और partition में कम उपलब्धता — पैसे, stock, locks के लिए इस्तेमाल करो।

---

## ➡️ Next Topic Suggestion
**67. Eventual Consistency** — The other side: let replicas be briefly different and converge later. Next: how eventual consistency works, conflict resolution (LWW, CRDTs), and designing UX around it.
