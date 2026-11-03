# 74. Schema Versioning + Migrations
# हिंदी में: Schema Versioning और Migrations

---

## 🔵 Simple Definition (English)
**Schema versioning** means tagging each document with a `schemaVersion` number so documents of different shapes can safely coexist while your code evolves. A **migration** converts old-shape documents to the new shape — either **lazily** (upgrade a document when the app reads/writes it) or **in bulk** (a background job using `updateMany` with an update pipeline). MongoDB has no `ALTER TABLE`; you never "lock the table", you roll the change over gradually.

## 🔵 सरल परिभाषा (Hindi)
**Schema versioning** का मतलब हर document पर `schemaVersion` number लगाना है ताकि code के विकसित होते समय अलग-अलग shape के documents सुरक्षित तरीके से साथ रह सकें। **Migration** पुरानी shape के documents को नई shape में बदलती है — या तो **lazily** (app जब document पढ़े/लिखे तब upgrade करे) या **bulk** में (`updateMany` + update pipeline वाली background job)। MongoDB में `ALTER TABLE` नहीं होता; "table lock" नहीं करते, बदलाव धीरे-धीरे roll out करते हैं।

---

## 🔴 Problem it Solves
Requirements change: `name` becomes `firstName` + `lastName`, a single `phone` becomes `contact.phones[]`. In SQL you run a migration with downtime or heavy locks. In MongoDB, with millions of documents live and many app instances at different deploy versions, you can't change everything at once; code that assumes the new shape crashes on old documents (and vice versa). Without a version marker you don't even know which documents are old. Versioning gives zero-downtime, reversible, observable change.

## 🔴 यह क्यों बना? (Hindi)
Requirements बदलती हैं: `name` से `firstName` + `lastName`, एक `phone` से `contact.phones[]`। SQL में migration downtime या भारी locks के साथ चलती है। MongoDB में लाखों live documents और अलग-अलग deploy versions पर चलते कई app instances के साथ सब कुछ एक बार में नहीं बदल सकते; नई shape मानने वाला code पुराने documents पर crash होता है (और उल्टा भी)। Version marker के बिना पता ही नहीं चलता कौन से documents पुराने हैं। Versioning से zero-downtime, reversible, observable बदलाव मिलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → From day one add `schemaVersion: 1` to every new document (a missing field means "version 1" implicitly).
Step 2 → **Expand**: deploy app code that can **read both** v1 and v2 (upgrade function `v1 → v2` in memory).
Step 3 → Start **writing v2** for all new/updated documents (`schemaVersion: 2`).
Step 4 → **Migrate** old data: lazily (upgrade on access and save back) and/or a background batch job (`updateMany` with an aggregation-pipeline update, in small batches, off-peak).
Step 5 → **Verify**: `countDocuments({ schemaVersion: { $lt: 2 } })` reaches 0 (and `$exists: false` for implicit v1).
Step 6 → **Contract**: remove v1 handling from code, drop old fields; optionally enforce v2 with `$jsonSchema` (note 75), and add a rollback plan (keep old fields until confident).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पहले दिन से हर नए document में `schemaVersion: 1` लगाओ (field न होना यानी implicit version 1)।
Step 2 → **Expand**: ऐसा app code deploy करो जो v1 और v2 **दोनों पढ़ सके** (memory में `v1 → v2` upgrade function)।
Step 3 → सारे नए/updated documents **v2 में लिखना** शुरू करो (`schemaVersion: 2`)।
Step 4 → पुराना data **migrate** करो: lazily (access पर upgrade करके save) और/या background batch job (`updateMany` + aggregation-pipeline update, छोटे batches में, off-peak)।
Step 5 → **Verify**: `countDocuments({ schemaVersion: { $lt: 2 } })` 0 हो जाए (implicit v1 के लिए `$exists: false`)।
Step 6 → **Contract**: code से v1 handling हटाओ, पुराने fields drop करो; चाहें तो `$jsonSchema` (note 75) से v2 enforce करो, और rollback plan रखो (भरोसा होने तक पुराने fields रखो)।

---

## 🟡 Real World Example
**Paytm-style wallet users**: the original `users` had one `phone`. Product adds multiple numbers + verified flag. The team deploys code reading both shapes, writes `schemaVersion: 2` with `contact.phones[]` for new signups, then an off-peak job migrates 8 crore old users in batches of 10,000 over a week. A dashboard tracks the remaining v1 count until it hits zero; then the v1 code path is deleted.

## 🟡 Real Example Hindi mein
**Paytm जैसे wallet users**: शुरुआत में `users` में एक `phone` था। Product ने कई numbers + verified flag जोड़ा। Team ने ऐसा code deploy किया जो दोनों shapes पढ़ता है, नए signups के लिए `contact.phones[]` के साथ `schemaVersion: 2` लिखा, फिर off-peak job ने एक हफ़्ते में 10,000 के batches में 8 करोड़ पुराने users migrate किए। Dashboard बचे हुए v1 की count दिखाता रहा जब तक 0 नहीं हुई; फिर v1 code path हटा दिया गया।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t74
db.users.insertMany([
  { _id: 1, name: "Asha Kumar", phone: "9999911111" },                       // v1 (no schemaVersion field)
  { _id: 2, name: "Ravi", phone: "8888822222", schemaVersion: 2,
    contact: { phones: ["8888822222"] } }                                    // already v2
])

// How many documents still need migration? (missing field = implicit v1)
db.users.countDocuments({ schemaVersion: { $exists: false } })
// Output: 1

// Bulk migration with an UPDATE PIPELINE (array as 2nd arg): reads old fields while writing new ones
const r = db.users.updateMany(
  { schemaVersion: { $exists: false } },                                     // only old docs -> idempotent & restartable
  [
    { $set: {
        schemaVersion: 2,                                                    // new marker
        firstName: { $arrayElemAt: [ { $split: ["$name", " "] }, 0 ] },      // "Asha Kumar" -> "Asha"
        contact: { phones: ["$phone"] }                                      // phone -> contact.phones[]
    } },
    { $unset: ["phone"] }                                                    // drop the old field
  ]
)
// Output: { matchedCount: 1, modifiedCount: 1 }
db.users.find({ _id: 1 }, { _id: 0 })
// Output: [ { name: 'Asha Kumar', schemaVersion: 2, firstName: 'Asha', contact: { phones: [ '9999911111' ] } } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — batched migration job (safe for huge collections), with progress and idempotence
// Node driver version below; the same loop works in mongosh.
const { MongoClient } = require('mongodb');

async function migrateUsers(uri) {
  const client = new MongoClient(uri);                       // one client for the job
  await client.connect();
  const users = client.db('t74').collection('users');
  const BATCH = 10000;                                       // small batches = short locks, bounded oplog bursts
  let total = 0;

  for (;;) {
    // 1) pick a batch of ids still on the old version (uses an index on schemaVersion if you add one)
    const ids = await users
      .find({ schemaVersion: { $exists: false } }, { projection: { _id: 1 } })
      .limit(BATCH).map(d => d._id).toArray();
    if (ids.length === 0) break;                             // nothing left -> done

    // 2) upgrade exactly that batch; the filter repeats the version check so a retry never double-migrates
    const r = await users.updateMany(
      { _id: { $in: ids }, schemaVersion: { $exists: false } },
      [ { $set: { schemaVersion: 2,
                  firstName: { $arrayElemAt: [ { $split: ['$name', ' '] }, 0 ] },
                  contact: { phones: ['$phone'] } } },
        { $unset: ['phone'] } ]
    );
    total += r.modifiedCount;
    console.log(`migrated ${total} so far`);                  // progress for the ops dashboard
    await new Promise(res => setTimeout(res, 200));          // throttle: give production traffic room
  }
  await client.close();                                      // always release connections
  return total;
}

// LAZY migration (upgrade on read) - app-level function:
function upgrade(doc) {
  if (!doc.schemaVersion) {                                  // v1 -> v2 in memory
    doc.firstName = doc.name.split(' ')[0];
    doc.contact = { phones: [doc.phone] };
    delete doc.phone;
    doc.schemaVersion = 2;
  }
  return doc;                                                // callers always see v2 shape
}
// After upgrading, write back with: users.replaceOne({_id: doc._id, schemaVersion: {$exists:false}}, doc)
// (the filter guards against a concurrent migration)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require('mongoose');
const express = require('express');
const { Schema } = mongoose;

const userSchema = new Schema({
  schemaVersion: { type: Number, default: 2 },            // new docs are v2
  firstName: String,
  contact: { phones: [String] },
  name: String, phone: String                              // legacy v1 fields (kept until migration finishes)
});

// Lazy upgrade on load: Mongoose "init" hook runs when a document is hydrated from the DB
userSchema.post('init', function (doc) {
  if (!doc.schemaVersion || doc.schemaVersion < 2) {
    doc.firstName = (doc.name || '').split(' ')[0];
    doc.contact = { phones: doc.phone ? [doc.phone] : [] };
    doc.schemaVersion = 2;                                 // changes are in memory; call save() to persist
  }
});
const User = mongoose.model('User', userSchema);

const app = express();
app.get('/users/:id', async (req, res) => {
  const u = await User.findById(req.params.id);
  if (!u) return res.status(404).json({ error: 'Not found' });
  if (u.isModified()) await u.save();                      // persist the lazy upgrade (best effort)
  res.json({ firstName: u.firstName, phones: u.contact.phones });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Migrating everything in one giant `updateMany` at peak hours
```javascript
// Wrong — 8 crore docs in one op: long run, replication lag, cache pressure
db.users.updateMany({}, { $set: { schemaVersion: 2 } })
// Right — batch by _id ranges / limit, throttle, run off-peak, make it idempotent (filter on the OLD version)
```

❌ Mistake 2: Deploying code that only understands the new shape
```javascript
// Wrong — user.contact.phones[0] throws on v1 docs where contact is undefined
const first = user.contact.phones[0];
// Right — upgrade(doc) first, or read defensively: user.contact?.phones?.[0] ?? user.phone
```
✅ Also: a non-idempotent migration (running twice duplicates data), no verification count, and dropping old fields before confirming the rollout.

---

## 🧠 Tricky Interview Question

During your migration an old app instance (still on v1 code) saves a document that your job already upgraded to v2. What can go wrong and how do you prevent it?

Answer: The old instance does `replaceOne`/`save()` with its stale v1 copy, **overwriting the v2 document** (new fields lost, `schemaVersion` gone) — a lost update. Prevent it by (1) rolling out the "reads both, writes v2" code to **all instances before** starting the data migration, (2) using targeted `$set` updates instead of whole-document replaces, and (3) optimistic concurrency (filter on `schemaVersion`/a `__v` field), so the stale write matches 0 documents and the app retries. This is why the sequence is expand → write-new → migrate → contract.

---

## ⚫ Interview Questions + Answers

Q1: Why add a `schemaVersion` field?
A1: It tells code which shape a document has, lets migrations target only old documents (idempotent), and lets you monitor progress. Without it you must infer shape from field existence.

Q2: Lazy vs bulk migration?
A2: Lazy upgrades documents on access: no big job, but cold documents stay old forever. Bulk (batch job) guarantees completion and consistent shape but costs load. Most teams combine both: lazy plus a background sweep.

Q3: What is an update with an aggregation pipeline?
A3: `updateMany(filter, [ {$set:...}, {$unset:...} ])` (4.2+). Stages can reference existing field values (`"$phone"`, `$split`), which the classic `$set` operator cannot — ideal for field restructuring.

Q4: How do you migrate without downtime?
A4: Expand/contract: deploy dual-read code, start writing the new shape, migrate in small throttled batches, verify counts, then remove the old path. Optionally run the migration in a replica set secondary-friendly time window.

Q5: Can schema validation help during migration?
A5: Yes: begin with `validationAction: "warn"` and `validationLevel: "moderate"` to log/allow existing invalid docs, then switch to `strict`/`error` once all documents are v2 (see note 75).

---

## 🔷 When to Use + When Not to Use
✅ Use:
- Any long-lived collection whose shape may change
- Multiple app versions running at once (rolling deploys, mobile clients)
- Large data where "stop the world" migration is impossible

❌ Avoid / skip:
- Throwaway/prototype collections
- Tiny collections where a single `updateMany` at low traffic is simplest (still wise to add the field)

---

## 📊 Visual Diagram
```
EXPAND ─► WRITE NEW ─► MIGRATE ─► VERIFY ─► CONTRACT
  │          │            │          │          │
 code       new docs     batch     count      remove
 reads      = v2         updateMany v1 == 0   v1 code,
 v1 + v2                 (throttled)          old fields

 users collection over time
 {v1}{v1}{v1}{v1}   ->  {v1}{v1}{v2}{v2}  ->  {v2}{v2}{v2}{v2}
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| schemaVersion | Field marking the document's shape version | Document की shape का version |
| Lazy migration | Upgrade on read/write | Access पर upgrade |
| Bulk migration | Background batch upgrade | Background batch upgrade |
| Idempotent | Safe to run repeatedly | बार-बार चलाना सुरक्षित |
| Expand/Contract | Add new path, then remove old | नया path जोड़ो, फिर पुराना हटाओ |
| Update pipeline | Update with aggregation stages | Aggregation stages वाला update |
| Lost update | Stale write overwrites newer data | पुराना write नया data मिटा दे |

---

## ⚡ 3-Line Summary
English:
1. Tag documents with `schemaVersion` and keep code able to read old and new shapes while you evolve the schema.
2. Migrate lazily and/or with throttled, idempotent batches using update pipelines; verify by counting remaining old versions.
3. Follow expand → write new → migrate → contract, and never deploy code that only understands the new shape.

Hindi:
1. Documents पर `schemaVersion` लगाओ और schema बदलते समय code को पुरानी और नई दोनों shapes पढ़ने लायक रखो।
2. Lazily और/या throttled, idempotent batches (update pipelines) से migrate करो; बचे पुराने versions गिनकर verify करो।
3. Expand → नया लिखो → migrate → contract क्रम अपनाओ, और ऐसा code कभी deploy न करो जो सिर्फ़ नई shape समझता हो।

---

## ➡️ Next Topic
**75. Schema Validation ($jsonSchema)** — enforce document shape at the database level with `validator`, `validationLevel` and `validationAction`.
