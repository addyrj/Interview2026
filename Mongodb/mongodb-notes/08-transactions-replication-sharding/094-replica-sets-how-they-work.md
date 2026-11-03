# 94. Replica Sets — How They Work
# हिंदी में: Replica Sets कैसे काम करते हैं

---

## 🔵 Simple Definition (English)
A **replica set** is a group of `mongod` processes that hold the same data. One member is the **primary** (accepts all writes); the others are **secondaries** that copy the primary's changes by replaying its **oplog**. If the primary dies, the remaining members automatically **elect** a new primary. It gives high availability, redundancy and optional read scaling.

## 🔵 सरल परिभाषा (Hindi)
**Replica set** `mongod` processes का एक group है जिनके पास एक जैसा data होता है। एक member **primary** होता है (सारी writes लेता है); बाकी **secondaries** primary का **oplog** replay करके उसके changes copy करते हैं। Primary मर जाए तो बचे हुए members अपने आप नया primary **elect** कर लेते हैं। इससे high availability, redundancy और optional read scaling मिलती है।

---

## 🔴 Problem it Solves
A single MongoDB server is a single point of failure: disk dies, machine reboots, data centre loses power, and the app is down (or data is lost). Backups restore only to the last snapshot. A replica set keeps 3+ live copies on different machines/zones, so one failure causes seconds of failover instead of hours of downtime, and with `w: 'majority'` no acknowledged write is lost.

## 🔴 यह क्यों बना? (Hindi)
अकेला MongoDB server single point of failure है: disk खराब, machine reboot, data centre की बिजली गई — और app बंद (या data खो गया)। Backup सिर्फ आखिरी snapshot तक restore करता है। Replica set अलग machines/zones पर 3+ live copies रखता है, इसलिए एक failure से घंटों की जगह कुछ सेकंड का failover होता है, और `w: 'majority'` के साथ कोई acknowledged write नहीं खोती।

---

## 🟢 How it Works — Step by Step

Step 1 → Typical set: **3 members** (1 primary + 2 secondaries) on different hosts/zones. Odd number of voters avoids tied elections.
Step 2 → Clients connect with a replica-set connection string (`mongodb://h1,h2,h3/?replicaSet=rs0`); the driver discovers who is primary and routes writes there.
Step 3 → A write is applied on the primary and recorded as an entry in `local.oplog.rs` (a capped collection).
Step 4 → Secondaries **tail the oplog** (pull from the primary or another secondary) and apply entries in order — replication is asynchronous and idempotent.
Step 5 → Members send **heartbeats** every 2 s (`heartbeatIntervalMillis`). If the primary is unreachable for 10 s (`electionTimeoutMillis`), a secondary calls an election.
Step 6 → Special members: **arbiter** (votes, holds no data), **hidden** (priority 0, invisible to apps, for backups/analytics), **delayed** (hidden + `secondaryDelaySecs`, protects against bad deployments), **priority 0** (can never become primary).
Step 7 → Max 50 members, max 7 voting members.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → आम set: अलग hosts/zones पर **3 members** (1 primary + 2 secondaries)। Voters की संख्या odd रखो ताकि election tie न हो।
Step 2 → Clients replica-set connection string से जुड़ते हैं (`mongodb://h1,h2,h3/?replicaSet=rs0`); driver पता लगाता है कि primary कौन है और writes वहीं भेजता है।
Step 3 → Write primary पर लगती है और `local.oplog.rs` (एक capped collection) में entry बन जाती है।
Step 4 → Secondaries oplog को **tail** करते हैं और entries क्रम से apply करते हैं — replication asynchronous और idempotent है।
Step 5 → Members हर 2 s में **heartbeat** भेजते हैं। Primary 10 s (`electionTimeoutMillis`) तक unreachable रहे तो कोई secondary election बुलाता है।
Step 6 → विशेष members: **arbiter** (vote देता है, data नहीं रखता), **hidden** (priority 0, apps को नहीं दिखता, backup/analytics के लिए), **delayed** (hidden + `secondaryDelaySecs`, गलत deployment से बचाव), **priority 0** (कभी primary नहीं बनेगा)।
Step 7 → अधिकतम 50 members, अधिकतम 7 voting members।

---

## 🟡 Real World Example
**Swiggy's orders cluster** runs a 3-node replica set across three availability zones in Mumbai. Writes (new orders) go to the primary in zone A; secondaries in B and C hold copies. When zone A has a network outage at dinner time, B and C elect a new primary within seconds, the app driver retries the failed write automatically (`retryWrites=true`), and customers barely notice. A hidden member in zone C feeds the nightly analytics export so reports never slow down live traffic.

## 🟡 Real Example Hindi mein
**Swiggy का orders cluster** मुंबई के तीन availability zones में 3-node replica set चलाता है। Writes (नए orders) zone A के primary पर जाती हैं; B और C के secondaries में copies हैं। रात के खाने के समय zone A का network चला जाए तो B और C कुछ सेकंड में नया primary चुन लेते हैं, driver failed write को automatically retry करता है (`retryWrites=true`), और customers को लगभग पता नहीं चलता। Zone C का hidden member nightly analytics export चलाता है ताकि reports live traffic को धीमा न करें।

---

## 💻 Code Example — Basic

Created a real single-node replica set on MongoDB 8.0.4 (`--replSet rs0`, then `rs.initiate`). Verified output:

```javascript
// Start (shell): mongod --replSet rs0 --port 27017 --dbpath /data/db --bind_ip 127.0.0.1
// Then in mongosh:
rs.initiate({                                    // run ONCE on one member
  _id: 'rs0',                                    // must match --replSet name
  members: [{ _id: 0, host: '127.0.0.1:27017' }] // add more members for real HA
});

rs.status();                                     // health, state and lag of every member
// Output (trimmed):
// { set: 'rs0', myState: 1,
//   members: [ { name: '127.0.0.1:27017', stateStr: 'PRIMARY', health: 1, electionTime: true } ] }

rs.conf();                                       // the configuration document
// Output (trimmed):
// { _id: 'rs0', version: 1, protocolVersion: Long('1'),
//   members: [ { priority: 1, votes: 1, arbiterOnly: false, hidden: false } ],
//   settings: { electionTimeoutMillis: 10000, heartbeatIntervalMillis: 2000, heartbeatTimeoutSecs: 10 } }

db.hello();                                      // what a driver sees when it connects
// Output (trimmed):
// { isWritablePrimary: true, setName: 'rs0', hosts: [ '127.0.0.1:27017' ], primary: '127.0.0.1:27017' }
```

## 💻 Code Example — Advanced

Building a production-like 3-data-node set plus special members (syntax reference; the multi-node parts could not be run on this single-node test setup):

```javascript
rs.initiate({
  _id: 'rs0',
  members: [
    { _id: 0, host: 'mongo1:27017', priority: 2 },          // preferred primary
    { _id: 1, host: 'mongo2:27017', priority: 1 },          // normal secondary
    { _id: 2, host: 'mongo3:27017', priority: 1 },          // normal secondary
  ]
});

// Add a hidden analytics node: never primary, apps cannot see it
rs.add({ host: 'mongo4:27017', priority: 0, hidden: true, votes: 0 });

// Delayed member (1 hour behind) — undo for "oops, dropped the collection"
rs.add({ host: 'mongo5:27017', priority: 0, hidden: true, votes: 0, secondaryDelaySecs: 3600 });

// Measure replication lag
rs.printSecondaryReplicationInfo();                         // "x secs behind primary" per secondary

// Look at the oplog window (how long a secondary can be offline and still catch up)
rs.printReplicationInfo();                                  // oplog size, first/last event time

// Resize oplog (MongoDB 4.4+; value in MB)
db.adminCommand({ replSetResizeOplog: 1, size: 16384 });
```

Oplog entries are real documents (output of `db.getSiblingDB('local').oplog.rs.find(...)` after inserting `{a:3}` and updating `{a:1}`):
```javascript
{ op: 'i', ns: 'mh07_wc.o', o: { _id: ObjectId('...'), a: 3 } }                   // insert
{ op: 'u', ns: 'mh07_wc.o', o: { '$v': 2, diff: { i: { b: 2 } } }, o2: { _id: ObjectId('...') } } // update as a diff
```
(ObjectIds vary on every run.) Updates are stored as idempotent diffs, so replaying them twice gives the same result.

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose connecting to a 3-node set — driver handles discovery and failover
await mongoose.connect(
  'mongodb://mongo1:27017,mongo2:27017,mongo3:27017/shop?replicaSet=rs0',
  {
    readPreference: 'primary',          // default; reads go to primary (strongly consistent)
    w: 'majority',                       // acknowledged only after majority has it
    retryWrites: true,                   // auto-retry once on transient failover errors
    serverSelectionTimeoutMS: 15000,     // how long to wait for a primary during failover
  }
);

// Per-query read from secondary for reporting (accepts slightly stale data)
const report = await Order.find({ day: '2026-11-03' }).read('secondaryPreferred').lean();
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Two-member replica set
```text
// Wrong — majority of 2 is 2. If one dies, no majority => NO primary, set becomes read-only
// Right — 3 members (or 2 data nodes + 1 arbiter at minimum), ideally across 3 zones
```

❌ Mistake 2: Reading from secondaries and expecting latest data
✅ Correct: Replication is asynchronous; a secondary read can be stale. Use `primary` for read-your-writes, or `readConcern: 'majority'` with causal consistency sessions.

❌ Mistake 3: Using replica set as a backup
✅ Correct: A `drop()` or bad `update` replicates to all secondaries in milliseconds. Keep real backups (snapshots/`mongodump`) and optionally a delayed member.

❌ Mistake 4: Connection string with a single host
✅ Correct: List several members and `replicaSet=rs0` so the driver can find a new primary after failover.

❌ Mistake 5: Tiny oplog on a busy system
✅ Correct: If a secondary is down longer than the oplog window, it cannot catch up and needs a full **initial sync**. Size the oplog for hours or days of writes.

---

## 🧠 Tricky Interview Question

Q: A 3-member set has the primary plus one secondary alive, and the third member is down. Can the set accept writes with `w: 3`?

Answer: Elections and `w: 'majority'` still work (2 of 3 is a majority), so the set has a primary and accepts majority writes. But `w: 3` can never be satisfied while a member is down — the write waits until `wtimeout` and fails with a write concern error, even though the data may already be applied on the primary and one secondary (write concern errors do not roll back the write). In our single-node test, `w: 2` returned `UnsatisfiableWriteConcern - Not enough data-bearing nodes` for the same reason. Prefer `w: 'majority'`, which adapts to the set size.

---

## ⚫ Interview Questions + Answers

Q1: How does a secondary stay in sync?
A1: It reads the primary's (or a sync source's) `local.oplog.rs` capped collection and applies each entry in order using multiple parallel writer threads batched by collection/document. Oplog entries are idempotent.

Q2: What is an arbiter and should you use one?
A2: A voting member with no data. It helps reach a majority cheaply, but it cannot hold data or acknowledge `w: 'majority'` writes, so with a PSA (Primary-Secondary-Arbiter) setup losing a data node can stall majority writes. Prefer three data-bearing members.

Q3: What does `priority: 0` do?
A3: The member can vote and replicate but can never become primary — useful for remote/DR sites or hidden analytics nodes.

Q4: How many members can a replica set have?
A4: Up to 50 members, but only 7 can vote. Most production sets use 3 or 5.

Q5: Difference between replication and sharding?
A5: Replication copies the SAME data to many nodes (availability, read scaling). Sharding splits DIFFERENT data across shards (storage and write scaling). Production sharded clusters have each shard as a replica set.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- ANY production deployment (always run a replica set, even for a small app)
- You need transactions or change streams (both require one)
- You need failover, zero-downtime upgrades (rolling), and backups from secondaries

❌ Avoid when:
- Throw-away local experiments where data loss is fine (single node is simpler, though you lose transactions/change streams)
- Needing to scale WRITES beyond one machine — replication alone doesn't help; shard too

---

## 📊 Visual Diagram
```
                 ┌────────────────────┐
   writes ─────► │  PRIMARY (mongo1)  │──► oplog (local.oplog.rs)
   reads* ─────► └─────────┬──────────┘
                           │  secondaries pull + apply entries
          ┌────────────────┴────────────────┐
   ┌──────▼───────┐                  ┌──────▼───────┐
   │ SECONDARY    │◄──heartbeats────►│ SECONDARY    │
   │ (mongo2)     │      2 s         │ (mongo3)     │
   └──────────────┘                  └──────────────┘
   * reads can go to secondaries (stale-risk) via readPreference

   primary down ─► 10 s silence ─► election ─► secondary promoted
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Primary | The only member accepting writes | एकमात्र writes लेने वाला member |
| Secondary | Copy that replays the oplog | Oplog replay करने वाली copy |
| Oplog | Capped log of all data changes | सारे changes का capped log |
| Heartbeat | Periodic "I'm alive" ping | समय-समय पर "मैं ज़िंदा हूँ" ping |
| Arbiter | Voter without data | Data के बिना voter |
| Hidden member | Invisible to apps, for backup/analytics | Apps से छुपा member |
| Initial sync | Full copy for a new/lagging member | नए/पिछड़े member की पूरी copy |
| Replication lag | Delay between primary and secondary | Primary और secondary के बीच देरी |

---

## ⚡ 3-Line Summary
English:
1. A replica set is a primary plus secondaries that replay the primary's oplog, giving redundancy and automatic failover.
2. Use at least 3 voting members across zones, a multi-host connection string with `replicaSet`, and `w: 'majority'` for durability.
3. It is not a backup and does not scale writes; transactions and change streams require it.

Hindi:
1. Replica set एक primary और उसके oplog को replay करने वाले secondaries का group है, जो redundancy और automatic failover देता है।
2. कम से कम 3 voting members अलग zones में, `replicaSet` वाली multi-host connection string, और durability के लिए `w: 'majority'` रखो।
3. यह backup नहीं है और writes scale नहीं करता; transactions और change streams के लिए यह ज़रूरी है।

---

## ➡️ Next Topic
**95. Replica Set Elections and Failover** — Exactly how a new primary is chosen and what the app sees during the switch.
