# 126. Migrate Schema Without Downtime
# हिंदी में: बिना Downtime के Schema Migrate करना

> ✅ Verified on a real `mongod` v8.0.4 (standalone). ObjectIds/timestamps vary run to run; this note uses fixed `_id`s so output is reproducible.

---

## 🔵 Simple Definition (English)
A **zero-downtime schema migration** changes the shape of documents (rename a field, split a field, change a type) while the application keeps serving traffic. MongoDB has no `ALTER TABLE`; documents of different shapes live in the same collection, so you migrate with the **expand → migrate → contract** pattern and a `schemaVersion` field, never with one big blocking change.

## 🔵 सरल परिभाषा (Hindi)
**Zero-downtime schema migration** का मतलब है documents की shape बदलना (field rename, split, type change) जबकि application traffic serve करती रहे। MongoDB में `ALTER TABLE` नहीं है; अलग-अलग shape के documents एक ही collection में रह सकते हैं, इसलिए हम **expand → migrate → contract** pattern और `schemaVersion` field इस्तेमाल करते हैं, एक बड़े blocking change की जगह।

---

## 🔴 Problem it Solves
Interview scenario: `users` has `name: "Aarav Sharma"`. Product wants `firstName` and `lastName`. The collection has 50 million documents and the app runs on 20 pods that are deployed gradually. If you update all documents and deploy new code "at once", you get: (1) old pods crash reading missing `firstName`, (2) new pods crash reading old docs, (3) a giant `updateMany` that holds locks/oplog pressure and slows everything. You need a plan where **old code and new code both work at every moment**.

## 🔴 यह क्यों बना? (Hindi)
Interview scenario: `users` में `name: "Aarav Sharma"` है। Product को `firstName` और `lastName` चाहिए। Collection में 5 करोड़ documents हैं और app 20 pods पर धीरे-धीरे deploy होती है। अगर सब documents एक साथ update करो और code "एक बार में" deploy करो: (1) पुराने pods missing `firstName` पर crash, (2) नए pods पुराने docs पर crash, (3) बहुत बड़ा `updateMany` oplog और load बढ़ाता है। हमें ऐसा plan चाहिए जिसमें **हर पल पुराना और नया code दोनों चलें**।

---

## 🟢 How it Works — Step by Step

Step 1 → **Expand**: deploy code that *writes both* shapes (`name` + `firstName`/`lastName` + `schemaVersion: 2`) and *reads either* shape (fallback to splitting `name`).
Step 2 → **Backfill**: a background job upgrades old documents (no `schemaVersion`) in small batches, using a pipeline update, throttled, restartable (it only selects not-yet-migrated docs).
Step 3 → **Verify**: count docs where `schemaVersion != 2` until it hits 0; optionally enable a `$jsonSchema` validator with `validationAction: "warn"` first, then `"error"`.
Step 4 → **Switch reads**: deploy code that reads only the new fields.
Step 5 → **Contract**: stop writing the old field, then `$unset` the old `name` field. Keep a rollback window before this step.
Step 6 → Optional **lazy migration**: upgrade a document when the app reads/writes it, so hot documents move first; backfill handles the cold tail.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Expand**: ऐसा code deploy करो जो *दोनों shapes लिखे* (`name` + `firstName`/`lastName` + `schemaVersion: 2`) और *कोई भी shape पढ़ सके* (fallback में `name` split करे)।
Step 2 → **Backfill**: background job पुराने documents (जिनमें `schemaVersion` नहीं) को छोटे batches में upgrade करे, pipeline update से, throttled और restartable।
Step 3 → **Verify**: `schemaVersion != 2` वाले docs गिनो जब तक 0 न हो जाएँ; पहले `$jsonSchema` validator `validationAction: "warn"` में, फिर `"error"`।
Step 4 → **Reads switch**: ऐसा code deploy करो जो सिर्फ नए fields पढ़े।
Step 5 → **Contract**: पुराना field लिखना बंद करो, फिर `name` को `$unset` करो। इससे पहले rollback window रखो।
Step 6 → Optional **lazy migration**: document read/write होने पर upgrade करो, hot documents पहले migrate होंगे; बाकी cold tail backfill करेगा।

---

## 🟡 Real World Example
**Razorpay-style customer profile**: `customers.name` becomes `firstName` + `lastName` because the invoice PDF needs a surname. They ship the dual-write release on Monday, run the backfill at night with 1000-doc batches and a 50 ms sleep, watch the "pending" counter on a dashboard, switch reads on Thursday, and drop `name` two weeks later after confirming no rollback. At no point did a request fail.

## 🟡 Real Example Hindi mein
**Razorpay जैसा customer profile**: `customers.name` को `firstName` + `lastName` में बदलना है क्योंकि invoice PDF में surname चाहिए। Monday को dual-write release, रात में 1000-doc batches और 50 ms sleep के साथ backfill, dashboard पर "pending" counter देखना, Thursday को reads switch, और दो हफ्ते बाद rollback न होने की पुष्टि करके `name` हटाना। इस पूरे समय किसी request ने fail नहीं किया।

---

## 💻 Code Example — Basic

```javascript
// mongosh — seed a v1 collection (old shape: single "name" field)
const d = db.getSiblingDB('mig');           // pick the database
d.dropDatabase();                           // start clean for the demo
d.users.insertMany([                        // four legacy documents, no schemaVersion
  { _id: 1, name: "Aarav Sharma", phone: "9876500001" },
  { _id: 2, name: "Priya Nair",   phone: "9876500002" },
  { _id: 3, name: "Rohan Mehta Jr", phone: "9876500003" }, // multi-word surname
  { _id: 4, name: "Madonna" }                              // single-word name, edge case
]);

// EXPAND: the new app version already writes the v2 shape (dual-write: keeps "name" too)
d.users.insertOne({
  _id: 5, schemaVersion: 2,                 // marker: this doc is already migrated
  firstName: "Neha", lastName: "Gupta",     // new fields
  name: "Neha Gupta",                       // old field kept so old pods still work
  phone: "9876500005"
});

// How much work is left? Old docs simply lack schemaVersion.
print("pending v1:", d.users.countDocuments({ schemaVersion: { $exists: false } }));
// Output: pending v1: 4

// MIGRATE: ONE pipeline update (array form) computes new fields from old ones server-side.
// A pipeline update lets us reference "$name"; a plain {$set:{..}} cannot.
const pipe = [{ $set: {
  firstName: { $arrayElemAt: [{ $split: ["$name", " "] }, 0] },   // first token
  lastName: { $trim: { input: {                                   // everything after first token
    $reduce: {
      input: { $slice: [{ $split: ["$name", " "] }, 1, 10] },     // tokens 1..10
      initialValue: "",
      in: { $concat: ["$$value", " ", "$$this"] }                 // join with spaces
    } } } },                                                      // $trim removes leading space
  schemaVersion: 2                                                // mark as migrated
}}];

// Filter selects ONLY not-yet-migrated docs => idempotent and safe to re-run/resume
const r = d.users.updateMany({ schemaVersion: { $exists: false } }, pipe);
printjson({ matched: r.matchedCount, modified: r.modifiedCount });
// Output: { matched: 4, modified: 4 }

d.users.find({}, { name: 1, firstName: 1, lastName: 1, schemaVersion: 1 }).forEach(x => printjson(x));
// Output (abridged, verified):
// { _id: 1, name: 'Aarav Sharma', firstName: 'Aarav', lastName: 'Sharma', schemaVersion: 2 }
// { _id: 3, name: 'Rohan Mehta Jr', firstName: 'Rohan', lastName: 'Mehta Jr', schemaVersion: 2 }
// { _id: 4, name: 'Madonna', firstName: 'Madonna', lastName: '', schemaVersion: 2 }  <- edge case handled
```

## 💻 Code Example — Advanced

```javascript
// mongosh — safety net + CONTRACT + throttled batch backfill (all verified on 8.0.4)

// 1) Validator in WARN mode: logs violations but never rejects writes, so it is safe mid-migration
d.runCommand({
  collMod: "users",                                   // modify collection options
  validator: { $jsonSchema: { required: ["firstName", "schemaVersion"] } }, // v2 contract
  validationLevel: "moderate",                        // only validate inserts + already-valid docs
  validationAction: "warn"                            // log, don't reject (switch to "error" later)
});
// Output: { ok: 1 }

print("pending after:", d.users.countDocuments({ schemaVersion: { $ne: 2 } }));
// Output: pending after: 0     <- gate: only proceed to contract when this is 0

// 2) CONTRACT: remove the legacy field once nothing reads it
d.users.updateMany({}, { $unset: { name: "" } });
printjson(d.users.findOne({ _id: 1 }));
// Output: { _id: 1, phone: '9876500001', firstName: 'Aarav', lastName: 'Sharma', schemaVersion: 2 }

// 3) Batched backfill for BIG collections: small batches keep oplog/cache pressure low
d.big.insertMany(Array.from({ length: 2500 }, (_, i) => ({ _id: i, fullName: "A" + i + " B" })));
let total = 0;
while (true) {
  // fetch next 1000 _ids of unmigrated docs (restartable: migrated docs no longer match)
  const ids = d.big.find({ v: { $exists: false } }, { _id: 1 }).limit(1000).toArray().map(x => x._id);
  if (!ids.length) break;                              // nothing left => done
  const res = d.big.updateMany({ _id: { $in: ids } }, { $set: { v: 2 } }); // upgrade this batch
  total += res.modifiedCount;
  print("batch", res.modifiedCount);
  // sleep(50);  // throttle in real life so you don't starve production traffic
}
print("total", total);
// Output:
// batch 1000
// batch 1000
// batch 500
// total 2500

// 4) GOTCHA (verified error): you cannot build a partial index on { v: {$exists:false} }
// d.big.createIndex({v:1},{partialFilterExpression:{v:{$exists:false}}})
// => MongoServerError: Expression not supported in partial index: $not
// Fix: write the marker as v:1 for old docs, or index {v:1} normally and query {v:{$lt:2}}.
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Lazy migration inside the data-access layer: the app tolerates BOTH shapes at read time.
const express = require('express');
const { MongoClient } = require('mongodb');
const app = express();
let users;                                              // collection handle set at startup
MongoClient.connect(process.env.MONGO_URI).then(c => { users = c.db('mig').collection('users'); });

// Normalise any document (v1 or v2) to the v2 shape in memory
function toV2(doc) {
  if (doc.schemaVersion === 2) return doc;              // already new
  const [first, ...rest] = (doc.name || '').split(' '); // v1: derive from "name"
  return { ...doc, firstName: first, lastName: rest.join(' '), schemaVersion: 2 };
}

app.get('/users/:id', async (req, res) => {
  const doc = await users.findOne({ _id: Number(req.params.id) });
  if (!doc) return res.sendStatus(404);
  const v2 = toV2(doc);                                 // reads work during migration
  if (doc.schemaVersion !== 2) {
    // LAZY MIGRATION: write back, but only if nobody changed it meanwhile (optimistic filter)
    await users.updateOne(
      { _id: doc._id, schemaVersion: { $exists: false } },
      { $set: { firstName: v2.firstName, lastName: v2.lastName, schemaVersion: 2 } }
    );
  }
  res.json({ firstName: v2.firstName, lastName: v2.lastName });
});
// Mongoose: keep BOTH `name` and `firstName/lastName` in the schema during expand, add
// `schemaVersion: { type: Number, default: 2 }`, and use a pre('save') hook to fill both fields.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: One giant blocking migration + simultaneous deploy
```javascript
// Wrong — renames a field everywhere while old pods still read "name"
db.users.updateMany({}, { $rename: { name: "fullName" } }); // old code now sees undefined

// Right — expand (write both) -> backfill in batches -> switch reads -> contract
```

❌ Mistake 2: Backfill that is not idempotent / resumable
```javascript
// Wrong — selects every doc each run, re-processes done docs, can't resume after a crash
db.users.updateMany({}, pipeline);

// Right — filter on "not yet migrated" so reruns only touch the remainder
db.users.updateMany({ schemaVersion: { $exists: false } }, pipeline);
```

❌ Mistake 3: Using `{ $set: { firstName: "$name" } }` expecting a field copy
✅ Correct: a plain document update stores the literal string `"$name"`. Use the **array (pipeline) form** `[ { $set: { firstName: "$name" } } ]` to reference other fields.

---

## 🧠 Tricky Interview Question
**Q:** You run the backfill while users are updating profiles. A user changes their name via old code between your read and your write. How do you avoid overwriting their change?

**Answer:** Do the transformation **inside a single atomic update** (pipeline update computes from the *current* `$name` on the server), and filter on the "unmigrated" condition. Never read in the app, compute, and write back with only `{_id}` as the filter. During expand, old pods write only `name` (no `schemaVersion` bump), so a doc they touch after migration would have stale `firstName`. Hence in the expand release **all writers** must write both shapes, and the backfill re-checks (`schemaVersion` missing or `name` != joined fields) or you finish by deploying the dual-writer everywhere *before* starting the backfill.

---

## ⚫ Interview Questions + Answers

Q1: Why does MongoDB make zero-downtime migrations easier than SQL?
A1: There is no table-level schema lock or `ALTER`. Documents with different shapes coexist, so you can add fields instantly and migrate documents gradually. Schema validation is optional and can be tightened later.

Q2: What is a `schemaVersion` field for?
A2: It labels each document's shape, so code can branch (`if v==1 upgrade`), backfills can find remaining work (`schemaVersion != 2`), and progress is measurable. It is the "Schema Versioning" pattern.

Q3: Lazy vs eager migration?
A3: Lazy upgrades a document when it is read/written (no big job, hot data first, but cold data stays old forever). Eager backfill touches everything in the background. Best practice: lazy + eager backfill, then contract.

Q4: How do you throttle a backfill?
A4: Small batches (500-1000), a sleep between batches, run off-peak, use a bounded `_id` range or "unmigrated" filter, watch replication lag and WiredTiger cache, and make it resumable.

Q5: How do you change a field's *type* (string to number)?
A5: Add the new field (`priceNum`), dual-write, backfill with `$toInt/$convert` in a pipeline update, switch reads, then drop the old field. Never change in place while old code reads it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The collection is large and traffic cannot stop
- Deployments are rolling (mixed old/new code)
- You need measurable, reversible progress

❌ Avoid when:
- The collection is tiny and a maintenance window is acceptable (a single `updateMany` is fine)
- It's a brand-new field with a default (just handle missing in code, no migration needed)

---

## 📊 Visual Diagram
```
EXPAND  ->  BACKFILL  ->  SWITCH READS  ->  CONTRACT
──────────────────────────────────────────────────────
t0  docs: {name}                       old code OK
t1  app writes {name,first,last,v:2}   old+new code OK     (EXPAND)
t2  job: v-missing -> v:2 in batches   old+new code OK     (MIGRATE)
t3  pending == 0 ?  validator warn->error                   (VERIFY)
t4  app reads first/last only                               (SWITCH)
t5  $unset name                         new code only       (CONTRACT)

  rollback possible until t5 ◄──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Expand/Contract | Add new shape, later remove old | नई shape जोड़ो, बाद में पुरानी हटाओ |
| schemaVersion | Per-document shape label | हर document की shape का label |
| Pipeline update | Update using aggregation stages | Aggregation stages से update |
| Backfill | Background upgrade of old docs | पुराने docs का background upgrade |
| Dual-write | Writing old and new fields | पुराना और नया दोनों field लिखना |
| Idempotent | Safe to re-run | दोबारा चलाना सुरक्षित |

---

## ⚡ 3-Line Summary
English:
1. Never change shape in one step; use expand -> backfill -> switch reads -> contract.
2. Use `schemaVersion`, pipeline updates and small idempotent batches.
3. Validate with `warn` then `error`, and `$unset` the old field only after a rollback window.

Hindi:
1. Shape एक step में मत बदलो; expand -> backfill -> reads switch -> contract अपनाओ।
2. `schemaVersion`, pipeline updates और छोटे idempotent batches इस्तेमाल करो।
3. पहले `warn` फिर `error` validation लगाओ, और rollback window के बाद ही पुराना field हटाओ।

---

## ➡️ Next Topic
**127. MongoDB Interview Classics — 20 Most Asked Questions** — rapid-fire revision of the questions that appear in almost every MongoDB interview.
