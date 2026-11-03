# 3. MongoDB Architecture (mongod, databases, collections, documents)
# हिंदी में: MongoDB Architecture (mongod, databases, collections, documents)

---

## 🔵 Simple Definition (English)
MongoDB's architecture is a hierarchy: a **server process (`mongod`)** hosts many **databases**; each database holds many **collections**; each collection holds many **documents**; each document holds **fields** (key-value pairs). Underneath, the **WiredTiger storage engine** writes data to disk, and clients talk to `mongod` through the wire protocol using a **driver** or **mongosh**. For production, several `mongod`s form a **replica set**, and big datasets are split over **shards** behind a **`mongos`** router.

## 🔵 सरल परिभाषा (Hindi)
MongoDB की architecture एक hierarchy है: एक **server process (`mongod`)** कई **databases** चलाता है; हर database में कई **collections**; हर collection में कई **documents**; हर document में **fields** (key-value pairs)। नीचे **WiredTiger storage engine** data को disk पर लिखता है, और clients **driver** या **mongosh** से wire protocol के ज़रिए `mongod` से बात करते हैं। Production में कई `mongod` मिलकर **replica set** बनाते हैं, और बड़ा data **`mongos`** router के पीछे **shards** में बँटता है।

---

## 🔴 Problem it Solves
You need a clear mental model to answer "where does my data live, how is it organised, and how does it stay available and scale?". Without it, people mix up terms (database vs collection), create hundreds of databases when one with many collections would do, or deploy a single standalone server in production and lose data when it dies. The layered architecture separates concerns: logical organisation (db/collection/document), storage (WiredTiger), availability (replica set) and scale (sharding).

## 🔴 यह क्यों बना? (Hindi)
आपको साफ़ mental model चाहिए: "मेरा data कहाँ रहता है, कैसे organised है, और available व scalable कैसे रहता है?" इसके बिना लोग terms (database vs collection) mix कर देते हैं, जहाँ एक database में कई collections काफ़ी हैं वहाँ सैकड़ों databases बना देते हैं, या production में सिर्फ़ एक standalone server चलाकर उसके मरने पर data खो देते हैं। Layered architecture अलग-अलग concerns बाँटती है: logical organisation (db/collection/document), storage (WiredTiger), availability (replica set) और scale (sharding)।

---

## 🟢 How it Works — Step by Step

Step 1 → `mongod` starts with a `--dbpath` (data files) and `--port` (27017 by default); it loads the **WiredTiger** engine.
Step 2 → A client opens a TCP connection; `mongod` authenticates it (if auth is on) and starts a session.
Step 3 → The client chooses a database; every database has its own set of files and its own namespace for collections. System databases: `admin`, `local`, `config`.
Step 4 → A write goes to the in-memory cache, is recorded in the **journal** (write-ahead log) and checkpointed to disk periodically.
Step 5 → In a **replica set**, the primary also writes the change to the **oplog**; secondaries replay it. If the primary dies, an election picks a new one.
Step 6 → In a **sharded cluster**, `mongos` routes each query to the right shard using the **shard key** and config servers' metadata.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `mongod` एक `--dbpath` (data files) और `--port` (default 27017) के साथ शुरू होता है; यह **WiredTiger** engine load करता है।
Step 2 → Client TCP connection खोलता है; `mongod` (auth on हो तो) authenticate करता है और session शुरू होता है।
Step 3 → Client database चुनता है; हर database की अपनी files और collections का अपना namespace होता है। System databases: `admin`, `local`, `config`।
Step 4 → Write पहले in-memory cache में जाती है, **journal** (write-ahead log) में दर्ज होती है और समय-समय पर disk पर checkpoint होती है।
Step 5 → **Replica set** में primary बदलाव **oplog** में भी लिखता है; secondaries उसे replay करते हैं। Primary मर जाए तो election से नया चुना जाता है।
Step 6 → **Sharded cluster** में `mongos` हर query को **shard key** और config servers के metadata से सही shard तक भेजता है।

---

## 🟡 Real World Example
**Razorpay** style fintech platform: one `mongod` replica set (3 nodes across availability zones) hosts a database `payments_logs` with collections `webhooks`, `events`, `audit`. If the primary node crashes at 2 AM, a secondary is elected within seconds and the app (driver with retryable writes) continues with no manual action. As event volume grows to billions of documents, the `events` collection is sharded by `merchantId`, and `mongos` routers spread load over shards.

## 🟡 Real Example Hindi mein
**Razorpay** जैसा fintech platform: एक `mongod` replica set (availability zones में 3 nodes) में database `payments_logs` है जिसमें collections `webhooks`, `events`, `audit` हैं। रात 2 बजे primary crash हो जाए तो कुछ seconds में secondary elect हो जाता है और app (retryable writes वाला driver) बिना manual action के चलती रहती है। Events अरबों documents तक बढ़ें तो `events` collection को `merchantId` से shard किया जाता है और `mongos` routers load बाँटते हैं।

---

## 💻 Code Example — Basic

Run on a real mongod 8.0.4 (port number and ids vary on your machine).

```javascript
// Inspect the hierarchy from mongosh
db.adminCommand({ listDatabases: 1 }).databases.map(x => x.name)
// Output (a fresh server): [ 'admin', 'config', 'local' ]   (+ any db you created)

use payments_demo                      // pick a database (created lazily)
db.events.insertOne({ type: "captured", amount: 500 })  // creates BOTH db and collection
db.getCollectionNames()                // list collections in the current db
// Output: [ 'events' ]

db.getName()                           // current database name
// Output: 'payments_demo'

// What process / storage engine / version are we talking to?
const s = db.serverStatus()
print(s.process, s.storageEngine.name, s.version)
// Output: mongod wiredTiger 8.0.4

db.hello().isWritablePrimary           // am I on a node that accepts writes?
// Output: true   (a standalone mongod is writable)

db.hello().maxBsonObjectSize           // max size of ONE document
// Output: 16777216   (16 MB)
```

## 💻 Code Example — Advanced

```javascript
// Start the server yourself, then inspect cluster-level info (shell commands + mongosh)
// $ mongod --port 27017 --dbpath ./data --bind_ip 127.0.0.1 --replSet rs0 --fork --logpath ./mongod.log
// $ mongosh --eval 'rs.initiate()'       // turn the single node into a 1-member replica set

// Node.js driver: who am I talking to, and what do the system databases hold?
const { MongoClient } = require('mongodb');

async function inspect() {
  const client = new MongoClient('mongodb://127.0.0.1:27017');
  await client.connect();
  try {
    // List every database via the admin database
    const { databases } = await client.db().admin().listDatabases();
    console.log(databases.map(d => d.name));      // e.g. [ 'admin', 'config', 'local', 'payments_demo' ]

    // 'ping' command proves the server is alive
    console.log(await client.db('admin').command({ ping: 1 })); // { ok: 1 }

    // Collections inside a database (type 'collection' vs 'view' vs 'timeseries')
    const cols = await client.db('payments_demo').listCollections().toArray();
    console.log(cols.map(c => [c.name, c.type])); // [ [ 'events', 'collection' ] ]

    // The 'local' database holds the oplog on replica-set members (local.oplog.rs)
  } finally {
    await client.close();
  }
}
inspect().catch(console.error);
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose maps this hierarchy to code: connection -> database, Model -> collection, instance -> document
const express = require('express');
const mongoose = require('mongoose');

// The db name 'payments_demo' in the URI selects the database
mongoose.connect('mongodb://127.0.0.1:27017/payments_demo');

// Model 'Event' -> collection 'events' (Mongoose lowercases and pluralises the name)
const Event = mongoose.model('Event', new mongoose.Schema({ type: String, amount: Number }));

const app = express();
app.get('/health', (req, res) => {
  // readyState: 0 disconnected, 1 connected, 2 connecting, 3 disconnecting
  res.json({ db: mongoose.connection.name, state: mongoose.connection.readyState });
});
app.get('/events', async (req, res) => res.json(await Event.find().limit(10))); // each result is a document
app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Creating one database per customer/tenant without thinking
```javascript
// Wrong - 10,000 databases = 10,000 sets of files, high memory/file-handle overhead
db.getSiblingDB("tenant_" + id).orders.insertOne({})

// Right - one database, a tenantId field + index (or a handful of dbs for big tenants)
db.orders.insertOne({ tenantId: id })
db.orders.createIndex({ tenantId: 1 })
```

❌ Mistake 2: Running a standalone `mongod` in production
✅ Correct: Use a replica set (minimum 3 data-bearing nodes, or 2 + arbiter) for failover, backups and rolling upgrades. Standalone is only for local dev.

---

## 🧠 Tricky Interview Question

**Q: You run `use shop` and then `show dbs`. `shop` is not listed. Why? And how do you make it appear?**

Answer: `use shop` only switches the shell's context. MongoDB creates a database **lazily**: it appears only once it has at least one collection containing data (the first write). So `db.items.insertOne({a:1})` creates both the database and the collection, and then `show dbs` lists `shop`. (Collections are also created lazily on first insert, or explicitly with `createCollection`.)

---

## ⚫ Interview Questions + Answers

Q1: What is `mongod` vs `mongosh` vs `mongos`?
A1: `mongod` is the database server process. `mongosh` is the interactive shell client. `mongos` is the query router used only in sharded clusters.

Q2: What are the default databases?
A2: `admin` (users/roles, privileged commands), `local` (node-local data such as the oplog, never replicated) and `config` (sharding/session metadata). `test` is only the shell's default context, not a created database.

Q3: What is WiredTiger?
A3: The default storage engine since MongoDB 3.2: document-level concurrency, compression (snappy by default), journaling and checkpoints. It uses an internal cache (about 50% of RAM minus 1 GB by default).

Q4: What is the maximum document size, and why?
A4: 16 MB (`maxBsonObjectSize`) to prevent one document from hogging RAM/bandwidth. For bigger files use GridFS.

Q5: Replica set vs sharding?
A5: A replica set copies the **same** data to several nodes for high availability and read scaling. Sharding **splits** data across replica sets for write/storage scale. Real clusters use both.

---

## 🔷 When to Use + When Not to Use
✅ Use a replica set when:
- Any production workload that cannot afford downtime or data loss

✅ Use sharding when:
- One replica set cannot hold the data or handle the write throughput

❌ Avoid when:
- Sharding too early: it adds complexity and a wrong shard key is painful to fix. Scale up and index properly first.

---

## 📊 Visual Diagram
```
 Client / App / mongosh
        │  (driver, wire protocol)
        ▼
 ┌──────────────── mongod ─────────────────┐
 │  database: shop                          │
 │   ├─ collection: orders                  │
 │   │    ├─ document { _id, city, ... }    │
 │   │    └─ document { _id, items:[...] }  │
 │   └─ collection: users                   │
 │  databases: admin | config | local       │
 │  ┌────────── WiredTiger ──────────┐      │
 │  │ cache ─► journal ─► data files │      │
 │  └────────────────────────────────┘      │
 └──────────────────────────────────────────┘
   Replica set:  Primary ──oplog──► Secondary, Secondary
   Sharded:      mongos ─► Shard A (RS) | Shard B (RS) | config servers
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| mongod | Database server process | Database server process |
| Database | Container of collections | Collections का container |
| Collection | Group of documents | Documents का group |
| Document | One BSON record | एक BSON record |
| WiredTiger | Default storage engine | Default storage engine |
| Oplog | Log replicated to secondaries | Secondaries को replicate होने वाला log |
| mongos | Router in a sharded cluster | Sharded cluster का router |

---

## ⚡ 3-Line Summary
English:
1. `mongod` hosts databases -> collections -> documents, stored by the WiredTiger engine with a journal.
2. Replica sets give high availability via the oplog; sharding (with `mongos`) gives horizontal scale.
3. Databases and collections are created lazily on the first write; a document is capped at 16 MB.

Hindi:
1. `mongod` databases -> collections -> documents को host करता है, जो WiredTiger engine journal के साथ store करता है।
2. Replica sets oplog से high availability देते हैं; sharding (`mongos` के साथ) horizontal scale देती है।
3. Databases और collections पहली write पर lazily बनते हैं; एक document अधिकतम 16 MB का हो सकता है।

---

## ➡️ Next Topic
**4. BSON vs JSON + Data Types** — How documents are actually encoded and which types MongoDB supports.
