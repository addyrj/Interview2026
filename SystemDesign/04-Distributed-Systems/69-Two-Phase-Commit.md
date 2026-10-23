# 69. Two Phase Commit (2PC)
# हिंदी में: Two Phase Commit — एक coordinator सभी databases से पहले पूछता है "commit के लिए तैयार हो?" (phase 1), सब हाँ कहें तो "commit करो" (phase 2), किसी ने ना कहा तो सब rollback

---

## 🔵 Simple Definition (English)
**Two-Phase Commit (2PC)** is a protocol that makes a transaction **atomic across multiple participants** (databases/resource managers). A **coordinator** runs two phases:
1. **Prepare (voting) phase:** ask every participant "can you commit?" Each does all the work, writes it durably, locks the resources, and votes **YES** or **NO**.
2. **Commit phase:** if **all** voted YES, the coordinator tells everyone **COMMIT**. If anyone voted NO or timed out, it tells everyone **ABORT**.
It guarantees **all-or-nothing**, but it's **blocking**: if the coordinator crashes at the wrong moment, participants are stuck holding locks.

## 🔵 सरल परिभाषा (Hindi)
2PC में एक coordinator सब databases से पूछता है "commit के लिए तैयार?" — हर DB काम करके, ताला लगाकर हाँ/ना बताता है (phase 1)।
सब हाँ कहें तो "commit" का आदेश, कोई भी ना कहे तो "rollback" (phase 2)। सब या कुछ नहीं मिलता है, पर coordinator बीच में गिरा तो सब ताले लगाए इंतज़ार में अटक जाते हैं।

---

## 🔴 Problem it Solves
You need **true atomicity** across two or more transactional resources, for example:
- Transfer money between accounts in **two different bank databases**.
- Write to a **database and a message queue** atomically (XA-capable broker).
- A **distributed database** committing a transaction that touches multiple shards (internally).

Without a protocol, one participant could commit while another fails, leaving the system half-done. 2PC ensures **every participant reaches the same decision**.

## 🔴 यह क्यों बना? (Hindi)
जब दो या ज़्यादा databases में एक साथ, पक्का atomic बदलाव चाहिए (जैसे दो बैंक DBs के बीच पैसा), तो बिना protocol के एक commit हो जाएगा और दूसरा फ़ेल।
2PC पक्का करता है कि सब एक ही फ़ैसले पर पहुँचें — या तो सब commit, या सब rollback।

---

## 🟢 How it Works — Step by Step

```
                     Coordinator (Transaction Manager)
                      │
   ═══════════ PHASE 1: PREPARE ═══════════
                      │── PREPARE ──►  DB-A (Orders)    → does work, writes to log, LOCKS rows, "YES"
                      │── PREPARE ──►  DB-B (Payments)  → does work, writes to log, LOCKS rows, "YES"
                      │── PREPARE ──►  DB-C (Inventory) → constraint fails → "NO"
                      │
   ═══════════ PHASE 2: DECISION ══════════
   All YES?  → write "COMMIT" to coordinator log → send COMMIT to all → each commits, releases locks
   Any NO /  → write "ABORT" to coordinator log  → send ABORT to all  → each rolls back, releases locks
   timeout
```

### Key rule: "prepared" is a promise
```
Once a participant votes YES, it has PROMISED it can commit — even after a crash.
It cannot decide on its own anymore; it must WAIT for the coordinator's decision.
(Its prepared state + locks are durable in its log.)
```

### The blocking problem

```
Participants A, B voted YES (prepared, holding locks)
Coordinator crashes BEFORE sending the decision 💥

A & B:  "Should I commit or abort?"  → they don't know → can't decide alone
        → locks HELD until coordinator recovers (minutes? hours?)
        → other transactions touching those rows BLOCK → availability drops

This is why 2PC is called a BLOCKING protocol.
Manual intervention ("heuristic commit/abort") risks inconsistency.
```

### Failure cases

```
Participant fails before voting   → coordinator times out → ABORT all ✅
Participant fails after YES       → on restart, reads its log ("prepared") → asks coordinator ✅
Coordinator fails before decision → participants BLOCK (the core weakness) ❌
Coordinator fails after logging   → on restart, re-sends decision from its log ✅
decision
Network partition during phase 2  → some commit, others wait → eventually consistent once healed
```

### Costs
```
- 2+ network round trips per transaction + forced disk writes (fsync) at each participant & coordinator
- Locks held across the whole protocol → low throughput under contention
- Coordinator = single point of failure (unless replicated via consensus)
- All participants must support XA/prepare (many NoSQL, SaaS APIs, payment gateways DON'T)
```

### Improvements & variants
```
3PC (Three-Phase Commit): adds a "pre-commit" phase to reduce blocking — but unsafe under network
     partitions; rarely used in practice.
Consensus-backed coordinator: replicate the coordinator's decision with Paxos/Raft so it can't be lost
     → Spanner, CockroachDB, YugabyteDB use 2PC across shards where each participant/coordinator is a
       Raft/Paxos group → highly available 2PC.
Parallel commits (CockroachDB) reduce commit latency to ~1 round trip.
```

### Where 2PC is used today
```
✅ Inside distributed databases (Spanner, CockroachDB, TiDB, Yugabyte, Vitess cross-shard, MongoDB
   multi-shard transactions) — hidden from you
✅ XA transactions in enterprise Java (JTA) across Oracle/DB2 + IBM MQ
✅ Postgres PREPARE TRANSACTION (building block for external coordinators)
✅ Kafka transactions (exactly-once) use a 2PC-like protocol with a transaction coordinator
❌ Across microservices over HTTP / with external APIs → use Sagas (next topic)
```

## 🟢 कैसे काम करता है? (Hindi)
1. Phase 1 (Prepare): coordinator सबसे पूछता है; हर DB काम करके log में लिखता है, rows पर ताला लगाता है, और "हाँ" या "ना" कहता है।
2. "हाँ" कहने के बाद DB ख़ुद फ़ैसला नहीं ले सकता — उसे coordinator के आदेश का इंतज़ार करना ही होगा।
3. Phase 2: सब हाँ → coordinator log में "COMMIT" लिखकर सबको commit भेजता है; कोई ना/timeout → सबको abort।
4. कमज़ोरी: coordinator फ़ैसला भेजने से पहले गिर गया तो सब DBs ताले लगाए अटके रहते हैं (blocking)।
5. आज 2PC ज़्यादातर distributed databases (Spanner, CockroachDB) के अंदर छिपा होता है, जहाँ coordinator ख़ुद Raft से सुरक्षित है; microservices में इसकी जगह Saga।

---

## 🟡 Real World Example

**Google Spanner / CockroachDB** — a transaction touching rows on different shards uses 2PC, but every participant and the coordinator is a Paxos/Raft-replicated group, so a single machine crash doesn't block the transaction. This makes 2PC practical at Google scale.

**Traditional banking (Java EE + XA)** — core banking and insurance systems historically used XA transactions across Oracle databases and IBM MQ queues, so a debit and the outgoing message were committed atomically.

**Kafka exactly-once** — a producer writing to multiple partitions plus committing consumer offsets uses Kafka's transaction coordinator, which follows a 2PC-like flow (prepare commit, write markers to partitions).

**Why microservices avoid it** — the Netflix and Amazon architectures explicitly avoid cross-service 2PC because one slow or failed service would hold locks across others and reduce overall availability (Topic 19: availabilities multiply).

## 🟡 Real Example Hindi में
Google Spanner और CockroachDB में कई shards वाला transaction 2PC से होता है, पर हर हिस्सा Raft/Paxos से सुरक्षित है, इसलिए एक मशीन गिरने से अटकता नहीं।
पुराने बैंकिंग सिस्टम Oracle और IBM MQ के बीच XA (2PC) इस्तेमाल करते थे। Netflix/Amazon जैसी कंपनियाँ microservices में 2PC से बचती हैं, क्योंकि एक धीमी service सबको रोक देती है।

---

## 🟠 My Stack Example

### Postgres building blocks (PREPARE TRANSACTION)
```sql
-- On DB-A (orders)
BEGIN;
INSERT INTO orders(id, user_id, total) VALUES (9001, 42, 450);
PREPARE TRANSACTION 'txn_9001';        -- phase 1: durable, locks held, YES vote

-- On DB-B (payments)
BEGIN;
UPDATE wallets SET balance = balance - 450 WHERE user_id = 42 AND balance >= 450;
PREPARE TRANSACTION 'txn_9001';

-- Coordinator decides (phase 2):
COMMIT PREPARED 'txn_9001';            -- on both
-- or ROLLBACK PREPARED 'txn_9001';

-- Find stuck prepared transactions (blocking risk!)
SELECT gid, prepared, owner FROM pg_prepared_xacts;
```
Requires `max_prepared_transactions > 0`. **Danger:** orphaned prepared transactions hold locks and block VACUUM, so monitor them.

### A tiny coordinator in Node (educational — don't hand-roll in production)
```js
async function twoPhaseCommit(gid, participants /* [{ pool, work: async (client) => {} }] */) {
  const clients = [];
  try {
    // Phase 1: prepare all
    for (const p of participants) {
      const c = await p.pool.connect(); clients.push(c);
      await c.query('BEGIN');
      await p.work(c);
      await c.query(`PREPARE TRANSACTION '${gid}'`);
    }
    await coordinatorLog.write(gid, 'COMMIT');            // durable decision BEFORE phase 2
    // Phase 2: commit all (retry until success — decision is final)
    for (const c of clients) await retryForever(() => c.query(`COMMIT PREPARED '${gid}'`));
  } catch (e) {
    await coordinatorLog.write(gid, 'ABORT');
    for (const c of clients) await c.query(`ROLLBACK PREPARED '${gid}'`).catch(() => c.query('ROLLBACK').catch(() => {}));
    throw e;
  } finally { clients.forEach((c) => c.release()); }
}
// Recovery process on restart: read coordinatorLog + pg_prepared_xacts → finish COMMIT/ROLLBACK.
```

### What you'd actually do in your stack
```
Need atomic multi-table writes?        → keep them in ONE Postgres (same service) → normal transaction
Need horizontal scale + atomic txns?   → CockroachDB / YugabyteDB / Spanner (2PC done safely for you)
Order + payment + inventory services?  → Saga + outbox + idempotency (Topic 70)
DB write + publish event atomically?   → Transactional outbox (not XA)
```

---

## ⚫ Interview Questions + Answers

**Q1: Explain the two-phase commit protocol.**
A1: A coordinator manages a transaction across participants. In phase 1 (prepare), it asks each participant to prepare. Each executes the transaction, durably logs it, holds locks, and votes yes (a promise it can commit) or no. In phase 2, if all voted yes, the coordinator durably logs COMMIT and instructs all to commit. Otherwise it logs ABORT and instructs rollback. Participants then commit or roll back and release locks, so everyone reaches the same outcome.

**Q2: Why is 2PC called a blocking protocol?**
A2: After voting yes, a participant can no longer decide unilaterally. If the coordinator fails before telling it the outcome, the participant must wait, keeping its locks, until the coordinator recovers, because committing or aborting on its own might contradict what others did. This blocks other transactions and reduces availability. Replicating the coordinator with consensus (as in Spanner and CockroachDB) mitigates it.

**Q3: What are the drawbacks of 2PC in microservices?**
A3: Synchronous coupling across all services (availability multiplies down), locks held across network round trips (poor throughput), a coordinator SPOF, and higher latency. Most services and external APIs (HTTP services, payment gateways, many NoSQL stores) don't support prepare/commit semantics. Long-running business processes (minutes or hours) can't hold locks. Hence sagas with compensations are preferred.

**Q4: Where is 2PC still a good choice?**
A4: Inside distributed SQL databases for cross-shard transactions (with consensus-replicated participants and coordinator), in tightly controlled enterprise environments with XA-capable resources and short transactions, and in streaming systems' internal transaction protocols (Kafka exactly-once). Essentially, where all participants are under one system's control and failures are handled by replication.

**Q5: What's 3PC and why isn't it widely used?**
A5: Three-phase commit adds a "pre-commit" phase between voting and commit, so participants can reach a decision even if the coordinator fails, reducing blocking under the assumption of bounded delays and no partitions. In real networks with partitions and unbounded delays, 3PC can lead to inconsistency, and it adds another round trip. Practical systems prefer 2PC over a consensus-replicated coordinator (Paxos/Raft commit) instead.

---

## 🔷 Trade-offs
✅ Advantages:
- Strong atomicity across participants; well understood; supported by XA databases.

❌ Disadvantages:
- Blocking on coordinator failure; locks held long → low throughput & availability.
- Extra round trips + fsyncs → latency; limited participant support; complex recovery.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| 2PC | Two-phase atomic commit protocol | दो चरणों वाला commit |
| Coordinator | Drives the protocol | प्रक्रिया चलाने वाला |
| Participant | Resource voting & committing | भाग लेने वाला DB |
| Prepare phase | Vote yes/no after doing work | तैयार हो? हाँ/ना |
| Commit phase | Final commit/abort | अंतिम commit/rollback |
| Blocking | Waiting indefinitely for decision | फ़ैसले का अनिश्चित इंतज़ार |
| XA | Standard interface for 2PC | 2PC का मानक इंटरफ़ेस |
| Prepared transaction | Durable, locked, awaiting decision | तैयार पर अधूरा transaction |
| 3PC | Three-phase variant | तीन चरणों वाला रूप |

---

## ⚡ 3-Line Summary
**English:**
1. 2PC: coordinator asks all participants to PREPARE (vote), then sends COMMIT if all yes, else ABORT — atomic across resources.
2. It's blocking (coordinator crash leaves prepared participants holding locks), slow, and needs XA-capable resources.
3. Used safely inside distributed DBs with consensus-replicated coordinators; for microservices use Sagas + outbox.

**Hindi:**
1. 2PC: पहले सबसे "तैयार?" पूछो, सब हाँ तो commit, वरना rollback — कई DBs में atomic।
2. कमज़ोरी: coordinator गिरा तो सब ताले लगाए अटके; धीमा; हर सिस्टम इसे support नहीं करता।
3. Distributed DBs के अंदर सुरक्षित रूप से चलता है; microservices के लिए Saga + Outbox।

---

## ➡️ Next Topic Suggestion
**70. Saga Pattern** — The practical alternative for microservices: a chain of local transactions with compensating actions, orchestrated or choreographed. Next: the full saga design for an order flow.
