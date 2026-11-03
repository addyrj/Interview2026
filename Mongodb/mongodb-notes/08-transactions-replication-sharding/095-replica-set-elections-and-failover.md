# 95. Replica Set Elections and Failover
# हिंदी में: Replica Set Elections और Failover

---

## 🔵 Simple Definition (English)
An **election** is the vote by which replica set members choose a new **primary**. It is triggered when the current primary is unreachable (no heartbeat for `electionTimeoutMillis`, default 10 s), when a member with a higher priority becomes available, or when an admin calls `rs.stepDown()`. **Failover** is the whole process of detecting the failure, electing, and having clients reconnect to the new primary. MongoDB uses a Raft-like protocol (protocol version 1) with **terms** and needs a **majority** of voting members.

## 🔵 सरल परिभाषा (Hindi)
**Election** वह voting है जिससे replica set members नया **primary** चुनते हैं। यह तब होता है जब मौजूदा primary unreachable हो (`electionTimeoutMillis`, default 10 s तक heartbeat नहीं), higher priority वाला member available हो जाए, या admin `rs.stepDown()` call करे। **Failover** पूरी प्रक्रिया है — failure पहचानना, election, और clients का नए primary से जुड़ना। MongoDB Raft-जैसा protocol (protocol version 1) इस्तेमाल करता है जिसमें **terms** हैं और voting members का **majority** चाहिए।

---

## 🔴 Problem it Solves
If a single primary is hard-wired, its failure means manual intervention at 3 a.m. Worse, if two nodes both think they're primary during a network partition (**split brain**), they accept conflicting writes and data diverges. Elections with majority voting guarantee at most one primary per term: a partitioned minority can never elect a leader, so it stays read-only and consistency is preserved.

## 🔴 यह क्यों बना? (Hindi)
Primary hard-wired हो तो उसके fail होने पर रात 3 बजे manual काम करना पड़ता। उससे भी बुरा — network partition में दो nodes खुद को primary मान लें (**split brain**) तो वे conflicting writes लेते हैं और data diverge हो जाता है। Majority वाली elections गारंटी देती हैं कि हर term में अधिकतम एक primary हो: partition में फँसा minority कभी leader नहीं चुन सकता, इसलिए वह read-only रहता है और consistency बनी रहती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Every member sends a **heartbeat** to the others every 2 s.
Step 2 → A secondary that doesn't hear from the primary for `electionTimeoutMillis` (10 s) decides it's dead. It increments the **term** and becomes a **candidate**.
Step 3 → (Pre-vote, 4.0+) It first asks "would you vote for me?" without changing terms, so a node isolated by a flaky network doesn't disrupt a healthy set.
Step 4 → The candidate requests votes. A member grants a vote only if: the candidate's oplog is **at least as up to date** as its own, it hasn't already voted this term, and the candidate has not lower priority-eligibility.
Step 5 → With a **majority of voting members** (2 of 3, 3 of 5), the candidate becomes primary. Higher `priority` makes a member more likely/faster to win.
Step 6 → The new primary may need to **roll back** operations that the old primary accepted but had not replicated (only writes without `w: 'majority'`). Rolled back data goes to `rollback/` files.
Step 7 → Drivers detect the topology change via `hello` monitoring, re-route to the new primary, and `retryWrites` re-sends the in-flight write once.
Step 8 → Typical failover: about 10–12 seconds (shorter with tuned `electionTimeoutMillis`).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → हर member हर 2 s में बाकी को **heartbeat** भेजता है।
Step 2 → जो secondary `electionTimeoutMillis` (10 s) तक primary से कुछ न सुने, वह मान लेता है कि primary मर गया। वह **term** बढ़ाकर **candidate** बन जाता है।
Step 3 → (Pre-vote, 4.0+) पहले वह बिना term बदले पूछता है "क्या तुम मुझे vote दोगे?", ताकि flaky network में अलग-थलग पड़ा node स्वस्थ set को disturb न करे।
Step 4 → Candidate votes माँगता है। Member vote तभी देता है जब candidate का oplog उससे **कम से कम उतना up to date** हो, उसने इस term में पहले vote न दिया हो।
Step 5 → **Voting members के majority** (3 में 2, 5 में 3) मिलने पर candidate primary बनता है। ऊँची `priority` वाले member के जीतने की संभावना ज़्यादा होती है।
Step 6 → नए primary को वे operations **rollback** करने पड़ सकते हैं जो पुराने primary ने लीं पर replicate नहीं हुईं (सिर्फ बिना `w: 'majority'` वाली writes)। Rollback data `rollback/` files में जाता है।
Step 7 → Drivers topology बदलाव पहचानते हैं, नए primary पर route करते हैं, और `retryWrites` in-flight write को एक बार दोबारा भेजता है।
Step 8 → आम failover: लगभग 10–12 सेकंड (`electionTimeoutMillis` कम करके घटाया जा सकता है)।

---

## 🟡 Real World Example
**Razorpay's payments database** is a 5-member replica set over three zones (2+2+1). During a zone outage, the surviving 3 members can still form a majority (3 of 5) and elect a primary. Writes made with `w: 'majority'` (payment captured) are never lost, because at least one surviving member has them. A write from the old primary that only had `w: 1` and hadn't replicated might be rolled back — which is exactly why payment-critical writes always use majority.

## 🟡 Real Example Hindi mein
**Razorpay का payments database** तीन zones (2+2+1) में 5-member replica set है। एक zone का outage हो तो बचे 3 members भी majority (5 में 3) बना सकते हैं और primary चुन लेते हैं। `w: 'majority'` वाली writes (payment captured) कभी नहीं खोतीं क्योंकि कम से कम एक surviving member के पास वे होती हैं। पुराने primary की सिर्फ `w: 1` वाली और replicate न हुई write rollback हो सकती है — इसीलिए payment-critical writes हमेशा majority से होती हैं।

---

## 💻 Code Example — Basic

Verified on a single-node replica set (MongoDB 8.0.4). A one-member set elects itself on startup:

```javascript
// Who is primary and when was it elected?
rs.status().members.map(m => ({ name: m.name, state: m.stateStr, electionTime: !!m.electionTime }));
// Output: [ { name: '127.0.0.1:27117', state: 'PRIMARY', electionTime: true } ]

// Election timing settings
rs.conf().settings;
// Output (trimmed): { electionTimeoutMillis: 10000, heartbeatIntervalMillis: 2000, heartbeatTimeoutSecs: 10 }

// Try a graceful step-down with 60 s freeze and 10 s catch-up
rs.stepDown(60, 10);
// Output on a ONE-member set (no electable secondary exists):
// MongoServerError: ExceededTimeLimit - No electable secondaries caught up as of <time>.
//   Please use the replSetStepDown command with the argument {force: true} to force node to step down.
```
That error is the safety mechanism: `rs.stepDown()` refuses to leave the set without a primary unless an up-to-date electable secondary exists. (Real multi-node election could not be demonstrated in a single-node test environment.)

## 💻 Code Example — Advanced

Multi-node operations (syntax reference, not run here):

```javascript
// Planned maintenance on the primary: step down, don't become primary again for 120 s
rs.stepDown(120, 30);          // stepDownSecs=120, secondaryCatchUpPeriodSecs=30

// Prefer mongo1 as primary: raise priority via reconfig
const cfg = rs.conf();
cfg.members[0].priority = 5;   // higher priority wins elections when caught up
rs.reconfig(cfg);              // triggers a priority-takeover election if needed

// Prevent a member from ever being elected (e.g. cross-region DR node)
cfg.members[2].priority = 0;
rs.reconfig(cfg);

// Make elections quicker in a stable LAN (default 10000)
cfg.settings.electionTimeoutMillis = 5000;
rs.reconfig(cfg);

// Force a specific node to call an election right now (rarely needed)
rs.stepDown();                 // on the current primary
```

Driver-side resilience (Node):
```javascript
const client = new MongoClient(uri, {
  retryWrites: true,               // retry a failed write ONCE after a failover
  retryReads: true,                // same for reads
  serverSelectionTimeoutMS: 20000, // wait up to 20 s for a new primary
  w: 'majority',                   // no rollback of acknowledged writes
});
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Surface failover to users gracefully
app.post('/orders', async (req, res) => {
  try {
    res.status(201).json(await Order.create(req.body));
  } catch (e) {
    // MongoServerSelectionError => no primary within serverSelectionTimeoutMS
    if (e.name === 'MongoServerSelectionError' || e.hasErrorLabel?.('RetryableWriteError')) {
      return res.status(503).set('Retry-After', '5').json({ error: 'Database failing over, retry' });
    }
    res.status(500).json({ error: 'Server error' });
  }
});

// Watch topology events for logs and alerts
mongoose.connection.on('disconnected', () => console.warn('Mongo disconnected'));
mongoose.connection.on('reconnected', () => console.info('Mongo reconnected'));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Even number of voters across two data centres
```text
// Wrong — 2 + 2 members in DC1 and DC2: losing the inter-DC link leaves 2 vs 2, no majority, NO primary
// Right — 2 + 2 + 1 across three sites (or 1 + 1 + 1), so any single site loss keeps a majority
```

❌ Mistake 2: Using `w: 1` for important writes
✅ Correct: A `w: 1` write acknowledged by the old primary but not yet replicated is rolled back after failover. Use `w: 'majority'`.

❌ Mistake 3: No retry logic and a short `serverSelectionTimeoutMS`
✅ Correct: Failover takes ~10+ s. A 5 s timeout makes every request fail during the election. Enable `retryWrites` and give the driver time.

❌ Mistake 4: Setting very low `electionTimeoutMillis` on WAN
✅ Correct: Latency spikes will trigger needless elections ("flapping"). Tune only in stable networks.

❌ Mistake 5: Using an arbiter with `w: 'majority'` in a PSA set
✅ Correct: If the secondary is down, majority (2 of 3) needs the arbiter's ack, which it cannot give (no data) — majority writes stall. Avoid PSA or monitor it.

---

## 🧠 Tricky Interview Question

Q: A 5-member set splits by a network partition into groups of 3 and 2. Which side gets a primary, and what happens to a client connected to the 2-member side that was previously the primary side?

Answer: Only the 3-member side holds a majority (3 of 5), so it elects (or keeps) the primary. If the old primary was in the 2-member side, it cannot see a majority, so it **steps down** to secondary on its own and refuses writes (reads from it may still work with `secondary` read preference). Writes with `w: 1` it accepted just before stepping down but not replicated will be rolled back when the partition heals. Clients with `retryWrites` re-route to the 3-side primary. This is the CP behaviour of MongoDB in CAP terms.

---

## ⚫ Interview Questions + Answers

Q1: What triggers an election?
A1: Primary unreachable for `electionTimeoutMillis`, a `rs.stepDown()`, a reconfig that changes members, a higher-priority node becoming caught-up (priority takeover), or startup of a new set.

Q2: Who can win an election?
A2: A voting, electable member (`priority > 0`) whose oplog is at least as fresh as a majority of voters it contacts. The term number prevents old primaries from acting after being replaced.

Q3: What is a rollback and how do you avoid it?
A3: When a former primary rejoins having writes the new primary never saw, it reverts them and saves to `rollback/` BSON files. Avoid with `w: 'majority'` (those writes are guaranteed to survive failover).

Q4: What is pre-vote (4.0+)?
A4: Before incrementing its term, a candidate polls peers whether they would vote for it; this prevents a disconnected node from forcing everyone's term up and causing needless elections when it reconnects.

Q5: How long does failover take and how to reduce it?
A5: About 10–12 s by default. Lower `electionTimeoutMillis` (stable networks only), use `rs.stepDown()` for planned work (near-instant handover), and make clients resilient with retryable writes.

---

## 🔷 When to Use + When Not to Use
✅ Use / tune elections when:
- Planning rolling upgrades (step down primary last)
- Setting priorities so the primary stays in the region closest to your app
- Designing multi-zone topologies (odd voters, 3 sites)

❌ Avoid when:
- Using `w: 1` writes for money or inventory (election rollbacks)
- Placing a majority of voters in a single zone (zone loss = no primary)

---

## 📊 Visual Diagram
```
 t=0   P ──heartbeat──► S1, S2        (healthy, term 1)
 t=10  P ✗ (crash)                     S1,S2 hear nothing for 10 s
 t=10  S1: term 2, candidate  ──"vote for me?"──► S2
 t=11  S2 grants vote (S1's oplog is current)  => 2 of 3 = majority
 t=11  S1 = PRIMARY (term 2) ; driver re-routes, retryWrites resends
 later P restarts ──► sees term 2 ──► rolls back un-replicated writes ──► SECONDARY

 PARTITION  [P,S1,S2 | S3,S4]  ->  3-side elects; 2-side has no majority => read-only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Election | Vote to choose a primary | Primary चुनने की voting |
| Term | Election epoch number | Election का epoch number |
| Majority | More than half of voting members | Voting members में आधे से ज़्यादा |
| Step down | Primary voluntarily becomes secondary | Primary का स्वेच्छा से secondary बनना |
| Rollback | Reverting un-replicated writes | Replicate न हुई writes को वापस करना |
| Split brain | Two primaries at once (prevented) | एक साथ दो primary (रोका जाता है) |
| Priority | Weight favouring election of a member | Election में member को तरजीह देने का weight |
| Pre-vote | Poll before starting a real election | असली election से पहले की polling |

---

## ⚡ 3-Line Summary
English:
1. When the primary is silent for `electionTimeoutMillis` (10 s), an up-to-date secondary calls an election and needs a majority of voters to win.
2. Majority voting prevents split brain; un-replicated `w: 1` writes can be rolled back, so use `w: 'majority'` plus `retryWrites`.
3. Use odd voters across 3 zones, `rs.stepDown()` for planned maintenance, and priorities to choose the preferred primary.

Hindi:
1. Primary `electionTimeoutMillis` (10 s) तक चुप रहे तो up-to-date secondary election बुलाता है और जीतने के लिए voters का majority चाहिए।
2. Majority voting split brain रोकती है; replicate न हुई `w: 1` writes rollback हो सकती हैं, इसलिए `w: 'majority'` और `retryWrites` रखो।
3. 3 zones में odd voters रखो, planned maintenance के लिए `rs.stepDown()` और पसंदीदा primary के लिए priorities इस्तेमाल करो।

---

## ➡️ Next Topic
**96. Read Preference and Write Concern Deep Dive** — Controlling where reads go and how many nodes must confirm a write.
