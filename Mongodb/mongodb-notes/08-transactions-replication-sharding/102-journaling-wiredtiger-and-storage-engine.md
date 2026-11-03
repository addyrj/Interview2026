# 102. Journaling, WiredTiger and Storage Engine
# हिंदी में: Journaling, WiredTiger और Storage Engine

---

## 🔵 Simple Definition (English)
A **storage engine** is the part of `mongod` that decides how data is written to disk and read back into memory. MongoDB's default (and in practice the only one in Community 8.x) is **WiredTiger**. It stores documents in B-tree files, keeps a **cache** of hot pages in RAM, compresses data (snappy by default), uses document-level concurrency, and protects against crashes with **checkpoints** (a consistent snapshot every ~60 seconds) plus a **journal** (a write-ahead log flushed roughly every 100 ms, or immediately when you ask with `j: true`).

## 🔵 सरल परिभाषा (Hindi)
**Storage engine** `mongod` का वह हिस्सा है जो तय करता है कि data disk पर कैसे लिखा जाए और memory में वापस कैसे पढ़ा जाए। MongoDB का default (और Community 8.x में असल में एकमात्र) engine **WiredTiger** है। यह documents को B-tree files में रखता है, hot pages का **cache** RAM में रखता है, data compress करता है (default snappy), document-level concurrency देता है, और crash से बचाने के लिए **checkpoints** (लगभग हर 60 सेकंड में consistent snapshot) और **journal** (write-ahead log, लगभग हर 100 ms पर flush, या `j: true` देने पर तुरंत) इस्तेमाल करता है।

---

## 🔴 Problem it Solves
Writing every change straight to its final place on disk is slow (random I/O), and if the machine loses power halfway you get a half-written, corrupt file. Old engines (MMAPv1) also locked a whole collection or database for every write, so one slow writer blocked everyone.

WiredTiger fixes three things at once. Writes go first to a sequential **journal** (fast append, survives a crash). Data pages live in an in-memory **cache** and are flushed to disk lazily by **checkpoints**. And locking happens at the **document** level, so thousands of clients can write different documents in the same collection simultaneously. Compression cuts disk use, usually by 50 to 80 percent.

## 🔴 यह क्यों बना? (Hindi)
हर change को सीधे disk में उसकी final जगह पर लिखना धीमा है (random I/O), और बीच में बिजली चली जाए तो file आधी-लिखी और corrupt हो सकती है। पुराना engine (MMAPv1) हर write पर पूरा collection या database lock करता था, तो एक धीमा writer सबको रोक देता था।

WiredTiger तीन चीज़ें एक साथ ठीक करता है। Writes पहले sequential **journal** में जाते हैं (तेज़ append, crash से सुरक्षित)। Data pages memory के **cache** में रहते हैं और **checkpoints** से धीरे-धीरे disk पर जाते हैं। और locking **document** level पर होती है, इसलिए एक ही collection के अलग documents पर हज़ारों clients एक साथ लिख सकते हैं। Compression से disk use अक्सर 50 से 80 प्रतिशत कम होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Client sends `insertOne`. `mongod` applies it to the **in-memory cache** page (a "dirty" page) under a document-level lock.
Step 2 → The change is also appended to the **journal** (`journal/WiredTigerLog.*`) as a redo record. Journal records are flushed to disk about every **100 ms** (`storage.journal.commitIntervalMs`), or at once if the write used `writeConcern: { j: true }`.
Step 3 → With a replica set, `w: "majority"` also implies journaling on the majority nodes (since MongoDB 5.0 the default write concern is majority, which waits for the journal on the primary).
Step 4 → Every ~**60 seconds** a **checkpoint** writes all dirty pages to the data files (`collection-*.wt`, `index-*.wt`) as one consistent snapshot. Old journal files are then recycled.
Step 5 → On a crash, restart loads the last checkpoint and **replays the journal** after it, so you lose at most the last un-flushed journal window (up to ~100 ms) for non-`j:true` writes.
Step 6 → When the cache fills (default: the larger of 50 percent of (RAM minus 1 GB) or 256 MB), WiredTiger **evicts** pages. Data on disk is stored compressed (snappy for collections, prefix compression for indexes).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Client `insertOne` भेजता है। `mongod` उसे document-level lock के साथ **in-memory cache** page (एक "dirty" page) पर apply करता है।
Step 2 → Change को **journal** (`journal/WiredTigerLog.*`) में redo record की तरह append भी किया जाता है। Journal लगभग हर **100 ms** (`storage.journal.commitIntervalMs`) पर flush होता है, या write में `writeConcern: { j: true }` हो तो तुरंत।
Step 3 → Replica set में `w: "majority"` का मतलब majority nodes पर journaling भी है (MongoDB 5.0 से default write concern majority है)।
Step 4 → हर ~**60 सेकंड** में **checkpoint** सारे dirty pages को data files (`collection-*.wt`, `index-*.wt`) में एक consistent snapshot की तरह लिखता है। फिर पुराने journal files recycle होते हैं।
Step 5 → Crash के बाद restart पर आख़िरी checkpoint load होता है और उसके बाद का **journal replay** होता है, इसलिए `j:true` के बिना वाले writes में ज़्यादा से ज़्यादा आख़िरी un-flushed window (~100 ms) जाती है।
Step 6 → Cache भर जाए (default: (RAM - 1 GB) का 50 प्रतिशत या 256 MB, जो बड़ा हो) तो WiredTiger pages **evict** करता है। Disk पर data compressed रहता है (collections में snappy, indexes में prefix compression)।

---

## 🟡 Real World Example
**Swiggy's order service** takes tens of thousands of order-status updates per minute on one replica set. Because WiredTiger locks per document, two delivery partners updating different orders never block each other. The team uses `w: "majority", j: true` for payment-confirmation writes (must survive a crash), while low-value "partner location ping" writes use `w: 1` and accept the ~100 ms journal window in exchange for speed. They watch the **WiredTiger cache dirty percentage**; if it climbs above ~20 percent, the checkpoints and disk are falling behind and they add RAM or faster disks.

## 🟡 Real Example Hindi mein
**Swiggy की order service** एक replica set पर हर मिनट हज़ारों order-status updates लेती है। WiredTiger per-document lock करता है, इसलिए अलग orders update करने वाले दो delivery partners एक-दूसरे को block नहीं करते। Payment-confirmation writes के लिए team `w: "majority", j: true` इस्तेमाल करती है (crash से बचना ज़रूरी), जबकि कम महत्व के "partner location ping" writes `w: 1` पर चलते हैं और speed के बदले ~100 ms journal window स्वीकार करते हैं। वे **WiredTiger cache dirty percentage** पर नज़र रखते हैं; ~20 प्रतिशत से ऊपर जाए तो मतलब checkpoints/disk पीछे हैं, और वे RAM या तेज़ disk जोड़ते हैं।

---

## 💻 Code Example — Basic

```javascript
// Run inside mongosh. Verified on MongoDB 8.0.4 (standalone, default settings).

// Which storage engine is running?
db.serverStatus().storageEngine.name           // Output: 'wiredTiger'
db.serverStatus().storageEngine.persistent     // Output: true  (data survives restart)

// Default WiredTiger cache size on this machine (bytes). Depends on your RAM.
db.serverStatus().wiredTiger.cache["maximum bytes configured"]
// Output (a 16 GB machine here): Long('3758096384')  -> ~3.5 GiB

// Create some data in a scratch database
const d = db.getSiblingDB("st");
d.orders.insertMany(Array.from({ length: 1000 }, (_, i) => ({ i, name: "item" + i, city: "Pune" })));

// Which compressor does this collection use? (default = snappy)
d.orders.stats().wiredTiger.creationString.match(/block_compressor=[a-z]*/)[0]
// Output: 'block_compressor=snappy'

// Insert and force the journal to disk BEFORE the server answers (j: true)
d.runCommand({
  insert: "j",                         // collection name
  documents: [{ a: 1 }],               // one document
  writeConcern: { w: 1, j: true }      // w:1 = primary acked, j:true = journal fsynced
})
// Output: { n: 1, ok: 1 }

// Where are the files? On the host (not in mongosh):
//   <dbpath>/collection-*.wt, index-*.wt   -> data and index B-tree files
//   <dbpath>/journal/WiredTigerLog.*       -> the write-ahead log (the journal)
//   <dbpath>/WiredTiger.wt, _mdb_catalog.wt-> engine + catalog metadata
```

## 💻 Code Example — Advanced

```javascript
// Per-collection compression, journal tuning and cache health. Verified on 8.0.4.

const d = db.getSiblingDB("st");

// 1) Choose a heavier compressor for an archive collection (zlib/zstd save more disk, cost more CPU)
d.createCollection("zc", {
  storageEngine: { wiredTiger: { configString: "block_compressor=zlib" } } // set at creation time only
});
d.zc.stats().wiredTiger.creationString.match(/block_compressor=[a-z]*/)[0]
// Output: 'block_compressor=zlib'

// 2) Server-wide choices live in mongod.conf (YAML), not in mongosh:
//   storage:
//     dbPath: /var/lib/mongo
//     wiredTiger:
//       engineConfig:
//         cacheSizeGB: 4                       # cap the cache explicitly (esp. in containers)
//       collectionConfig:
//         blockCompressor: zstd                # default for NEW collections: none | snappy | zlib | zstd
//     journal:
//       commitIntervalMs: 100                  # how often the journal is flushed (default 100)

// 3) Is the cache healthy? Compare used vs configured vs dirty bytes.
const c = db.serverStatus().wiredTiger.cache;
const used  = c["bytes currently in the cache"];       // bytes held now
const max   = c["maximum bytes configured"];           // the cache limit
const dirty = c["tracked dirty bytes in the cache"];   // changed but not yet checkpointed
print("cache used %:", (100 * used / max).toFixed(2));  // Output example: cache used %: 0.51
print("dirty %:", (100 * dirty / max).toFixed(2));      // alert if this stays high (> 20)

// 4) Checkpoint-related and log stats (names are stable across 6.x-8.x)
Object.keys(db.serverStatus().wiredTiger.log).slice(0, 4)
// Output: ['busy returns attempting to switch slots', 'force log remove time sleeping (usecs)', ...]

// 5) Force a flush before a file-copy backup (blocks writes; see note 108)
// db.fsyncLock();   // flush dirty pages + stop writes
// db.fsyncUnlock(); // resume writes
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Choosing durability per request with the Node driver / Mongoose.
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const Payment = mongoose.model('Payment', new mongoose.Schema({ orderId: String, amount: Number }));
const Ping    = mongoose.model('Ping',    new mongoose.Schema({ partnerId: String, lat: Number, lng: Number }));

// CRITICAL write: wait until a majority of nodes have it AND it is in the journal
app.post('/payments', async (req, res) => {
  const [doc] = await Payment.create([req.body], {
    writeConcern: { w: 'majority', j: true },   // survives a crash of the primary
  });
  res.status(201).json(doc);
});

// CHEAP write: ack as soon as the primary has applied it in memory/journal buffer
app.post('/pings', async (req, res) => {
  await Ping.collection.insertOne(req.body, { writeConcern: { w: 1, j: false } }); // fastest
  res.sendStatus(202);
});

// Schema-level default write concern (applies to every save of this model)
const Order = mongoose.model('Order', new mongoose.Schema({ total: Number }, {
  writeConcern: { w: 'majority', j: true, wtimeout: 5000 },
}));
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Thinking the journal means "every write is on disk when the call returns"
```javascript
// Wrong assumption — w:1 with j:false returns before the journal is fsynced.
await coll.insertOne(doc, { writeConcern: { w: 1, j: false } }); // may lose ~100 ms on a power cut

// Right — ask for journal durability on writes you cannot lose
await coll.insertOne(doc, { writeConcern: { w: 'majority', j: true } });
```

❌ Mistake 2: Deleting the `journal/` folder (or copying files while mongod runs)
```text
# Wrong: rm -rf /var/lib/mongo/journal    -> unrecoverable data after a crash
# Wrong: cp -r /var/lib/mongo /backup     -> inconsistent copy while writes happen
# Right: use mongodump, a filesystem snapshot, or db.fsyncLock() + copy + db.fsyncUnlock()
```

❌ Mistake 3: Setting the cache to almost all RAM
✅ Correct: WiredTiger uses the OS file-system cache too and each connection needs memory. Leave headroom (the default of 50 percent of RAM minus 1 GB is deliberate). In Docker or Kubernetes set `cacheSizeGB` explicitly, because older images size the cache from host RAM, not the container limit.

---

## 🧠 Tricky Interview Question

**Q:** You run `db.orders.insertOne({...})` with default settings on a standalone `mongod`, and the machine loses power 50 ms later. Is the order lost?

**Answer:** It may be. On a standalone server the default write concern `{ w: 1 }` does not wait for the journal (`j` defaults to false, except `w: "majority"` implies it in a replica set). The write is in the cache and in the journal buffer, but the journal is flushed every ~100 ms. So up to ~100 ms of acknowledged writes can be lost. The checkpoint (60 s) is irrelevant for durability here, because recovery = last checkpoint + journal replay. To be safe, pass `j: true`, or use a replica set with `w: "majority"`. Data does NOT revert to the last checkpoint, which is a common wrong answer.

---

## ⚫ Interview Questions + Answers

Q1: What is WiredTiger and why did MongoDB switch to it?
A1: It is the default storage engine since 3.2 (MMAPv1 was removed in 4.2). It gives document-level concurrency control, compression, a configurable cache, checkpoints plus a journal for durability, and MVCC snapshots (which make multi-document transactions and change streams possible).

Q2: What is the difference between a checkpoint and the journal?
A2: A checkpoint is a full consistent snapshot of the data files written about every 60 seconds. The journal is a write-ahead log of individual operations flushed about every 100 ms. Recovery loads the last checkpoint and then replays the journal to reach the latest state.

Q3: Can you disable the journal?
A3: Since MongoDB 6.1 you cannot (`--nojournal` was removed) for replica set members; journaling is always on. It was possible earlier only on standalone with a checkpoint-only recovery model, which risked losing up to 60 seconds of data. Do not rely on it.

Q4: How big is the WiredTiger cache and what happens when it is full?
A4: By default the larger of 50 percent of (RAM - 1 GB) or 256 MB. Clean pages are evicted; dirty pages must be written by checkpoint/eviction threads first. If application threads are forced to evict pages, you see latency spikes, a sign of too little RAM or slow disks.

Q5: How do you choose a compressor?
A5: snappy (default) is fast with a decent ratio; zlib and zstd compress more but use more CPU, good for archives and cold data; none is for already-compressed data. Set it per collection at creation with `storageEngine.wiredTiger.configString`, or globally via `wiredTiger.collectionConfig.blockCompressor` for new collections.

---

## 🔷 When to Use + When Not to Use
✅ Tune WiredTiger when:
- Write latency spikes or high dirty-cache percentage appear in monitoring
- Running in containers where the auto-sized cache may exceed the memory limit
- Disk is expensive and archive collections can use zstd/zlib
- Some writes are critical and others are disposable, so you pick write concerns per operation

❌ Avoid:
- Changing cache or journal settings without measuring first; defaults suit most workloads
- Using `j: false` or `w: 0` for money, orders or anything you cannot regenerate
- Copying live data files for backups without `fsyncLock` or a snapshot

---

## 📊 Visual Diagram
```
WIREDTIGER WRITE PATH
──────────────────────────────────────────────────────
 Client insert
     │
     ▼
 ┌──────────────────────┐     append (~100 ms flush, or now if j:true)
 │  WiredTiger CACHE    │ ───────────────────────────────►  JOURNAL (WAL)
 │  (RAM, dirty pages)  │                                   journal/WiredTigerLog.*
 └─────────┬────────────┘
           │ checkpoint every ~60 s (consistent snapshot)
           ▼
 ┌──────────────────────┐
 │  DATA FILES (.wt)    │   collection-*.wt  index-*.wt   (compressed)
 └──────────────────────┘

 CRASH RECOVERY = last checkpoint  +  replay journal after it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Storage engine | Component that writes/reads data on disk | Disk पर data लिखने-पढ़ने वाला component |
| WiredTiger | Default engine: cache, compression, doc-level locks | Default engine |
| Journal | Write-ahead log for crash recovery | Crash recovery के लिए write-ahead log |
| Checkpoint | Consistent on-disk snapshot every ~60 s | हर ~60 s में consistent snapshot |
| Cache | RAM area holding hot pages | Hot pages का RAM area |
| Dirty page | Changed in cache, not yet checkpointed | Cache में बदला, checkpoint नहीं हुआ |
| `j: true` | Wait for journal fsync before ack | Ack से पहले journal fsync का इंतज़ार |
| Compression | snappy/zlib/zstd block compression | Data का compression |

---

## ⚡ 3-Line Summary
English:
1. WiredTiger is MongoDB's storage engine: RAM cache, document-level locking, compression, checkpoints (~60 s) plus a journal (~100 ms).
2. Crash recovery = last checkpoint + journal replay; use `j: true` or `w: "majority"` for writes you cannot lose.
3. Tune cache size and compressor only after measuring; never delete the journal or copy live files without a snapshot or `fsyncLock`.

Hindi:
1. WiredTiger MongoDB का storage engine है: RAM cache, document-level locking, compression, checkpoints (~60 s) और journal (~100 ms)।
2. Crash recovery = आख़िरी checkpoint + journal replay; ज़रूरी writes के लिए `j: true` या `w: "majority"` इस्तेमाल करो।
3. Cache और compressor पहले measure करके tune करो; journal कभी delete मत करो और live files बिना snapshot या `fsyncLock` के copy मत करो।

---

## ➡️ Next Topic
**103. MongoDB Atlas — Clusters, Search, Vector Search** — the managed cloud service that runs all of this for you.

---
> Verified on MongoDB 8.0.4 (standalone, macOS). Cache size, ObjectIds and byte counts vary by machine.
