# 118. Find Duplicate Documents
# हिंदी में: Duplicate Documents ढूँढना

---

## 🔵 Simple Definition (English)
**Finding duplicates** means locating documents that share the same value(s) for a field or a set of fields (for example the same `email`). The standard solution is `$group` by that key, count with `$sum`, collect `_id`s with `$push`, and `$match` groups whose count is greater than 1. After cleaning, a **unique index** prevents duplicates from ever coming back.

## 🔵 सरल परिभाषा (Hindi)
**Duplicates ढूँढना** यानी ऐसे documents खोजना जिनके किसी field (या fields के set) की value एक जैसी हो (जैसे वही `email`)। मानक तरीका: उस key पर `$group`, `$sum` से गिनती, `$push` से `_id`s इकट्ठा, और `$match` से वे groups छाँटना जिनकी count 1 से ज़्यादा हो। सफ़ाई के बाद **unique index** duplicates को हमेशा के लिए रोक देता है।

---

## 🔴 Problem it Solves
Duplicates appear from double-clicked "Submit" buttons, retried API calls, bulk imports run twice or a missing unique constraint. They cause double emails, double billing and wrong reports. When you finally try `createIndex({ email: 1 }, { unique: true })` on dirty data it **fails** with `E11000 DuplicateKey`, so you must find and remove the extras first — safely, keeping exactly one survivor per group.

## 🔴 यह क्यों बना? (Hindi)
Duplicates double-click हुए "Submit" button, retry हुई API calls, दो बार चले bulk import या unique constraint की कमी से आते हैं। इनसे दोहरे emails, दोहरी billing और गलत reports बनते हैं। जब आप गंदे data पर `createIndex({ email: 1 }, { unique: true })` चलाते हैं तो वह `E11000 DuplicateKey` से **fail** होता है, इसलिए पहले extras को ढूँढकर हटाना पड़ता है — सुरक्षित तरीके से, हर group में ठीक एक survivor रखकर।

---

## 🟢 How it Works — Step by Step

Step 1 → **Define "duplicate"**: same `email`? same `(userId, productId)`? case-insensitive? Normalize first (lowercase/trim) or you will miss `A@x.in` vs `a@x.in`.
Step 2 → **Group**: `$group: { _id: "$email", ids: { $push: "$_id" }, n: { $sum: 1 } }` — one bucket per distinct email, with the list of `_id`s and a count.
Step 3 → **Filter**: `$match: { n: { $gt: 1 } }` keeps only the buckets that have duplicates.
Step 4 → **Choose the survivor**: sort before grouping (e.g. `$sort: { _id: 1 }`) so `ids[0]` is the oldest; keep it, delete the rest (`ids.slice(1)`).
Step 5 → **Delete**: `deleteMany({ _id: { $in: toDelete } })`. For huge sets, batch in chunks of a few thousand and run during a quiet window; take a backup first.
Step 6 → **Prevent**: `createIndex({ email: 1 }, { unique: true })`; use `collation` strength 2 or store a normalized `emailLower` for case-insensitive uniqueness.
Step 7 → **Memory note**: `$group` has a 100 MB per-stage RAM limit; for large collections add `{ allowDiskUse: true }`. If there are millions of ids per group, `$push` may exceed 16 MB — use `$sum` count only first, then fetch ids per offending key.
Step 8 → Alternative to avoid duplicates on import: `updateOne({ email }, { $setOnInsert: {...} }, { upsert: true })` (needs the unique index to be race-safe).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **"Duplicate" परिभाषित करो**: same `email`? same `(userId, productId)`? case-insensitive? पहले normalize करो (lowercase/trim) वरना `A@x.in` और `a@x.in` छूट जाएँगे।
Step 2 → **Group**: `$group: { _id: "$email", ids: { $push: "$_id" }, n: { $sum: 1 } }` — हर अलग email का एक bucket, `_id`s की list और count के साथ।
Step 3 → **Filter**: `$match: { n: { $gt: 1 } }` सिर्फ duplicates वाले buckets रखता है।
Step 4 → **Survivor चुनो**: group से पहले `$sort: { _id: 1 }` करो ताकि `ids[0]` सबसे पुराना हो; उसे रखो, बाकी (`ids.slice(1)`) delete करो।
Step 5 → **Delete**: `deleteMany({ _id: { $in: toDelete } })`। बड़े sets में कुछ हज़ार के chunks में, शांत समय पर चलाओ; पहले backup लो।
Step 6 → **रोकथाम**: `createIndex({ email: 1 }, { unique: true })`; case-insensitive uniqueness के लिए `collation` strength 2 या normalized `emailLower` रखो।
Step 7 → **Memory note**: `$group` की प्रति-stage 100 MB RAM limit है; बड़े collections में `{ allowDiskUse: true }`। अगर एक group में लाखों ids हों तो `$push` 16 MB पार कर सकता है — पहले सिर्फ `$sum` count निकालो, फिर गलत key की ids अलग से लाओ।
Step 8 → Import में duplicates से बचने का विकल्प: `updateOne({ email }, { $setOnInsert: {...} }, { upsert: true })` (race-safe होने के लिए unique index चाहिए)।

---

## 🟡 Real World Example
**Flipkart seller onboarding**: a CSV of 2 lakh sellers is imported twice by mistake, so many sellers have two or three rows with the same `gstin`. Before adding a unique index on `gstin`, ops runs the duplicates pipeline, keeps the oldest row of each seller, deletes the rest, and then enforces uniqueness so the next import cannot recreate the problem. **Razorpay** does the same for repeated webhook deliveries by keying events on `eventId`.

## 🟡 Real Example Hindi mein
**Flipkart seller onboarding**: 2 लाख sellers की CSV गलती से दो बार import हो गई, इसलिए कई sellers की एक ही `gstin` के दो-तीन rows हैं। `gstin` पर unique index लगाने से पहले ops duplicates pipeline चलाता है, हर seller की सबसे पुरानी row रखता है, बाकी हटाता है, फिर uniqueness लागू करता है ताकि अगला import समस्या दोबारा न बनाए। **Razorpay** बार-बार आने वाले webhook deliveries के लिए `eventId` पर यही करता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
use("dupes");
db.users.insertMany([
  { _id: 1, email: "a@x.in" }, { _id: 2, email: "b@x.in" },
  { _id: 3, email: "a@x.in" }, { _id: 4, email: "a@x.in" },
  { _id: 5, email: "b@x.in" }, { _id: 6, email: "c@x.in" }
]);

// Find duplicate emails with their ids and counts
db.users.aggregate([
  { $group: { _id: "$email", ids: { $push: "$_id" }, n: { $sum: 1 } } }, // bucket per email
  { $match: { n: { $gt: 1 } } },                                         // only repeated ones
  { $sort: { _id: 1 } }
]);
// Output: [ { _id: 'a@x.in', ids: [1,3,4], n: 3 }, { _id: 'b@x.in', ids: [2,5], n: 2 } ]
// (c@x.in appears once, so it is filtered out. Group order of ids follows scan order.)
```

## 💻 Code Example — Advanced

```javascript
// mongosh — remove duplicates, keep the OLDEST, then enforce uniqueness. Tested on 8.0.4
use("dupes");

// 1) Build the list of _ids to delete (everything except the first id of each group)
const toDelete = [];
db.users.aggregate([
  { $sort: { _id: 1 } },                                         // oldest first => ids[0] is the survivor
  { $group: { _id: "$email", ids: { $push: "$_id" } } },
  { $match: { "ids.1": { $exists: true } } }                     // has at least 2 ids (cheap "n > 1")
]).forEach(g => {
  g.ids.shift();                                                 // drop the survivor from the list
  toDelete.push(...g.ids);                                       // the rest are duplicates
});
toDelete;                                                         // Output: [ 5, 3, 4 ] (group order may vary)

// 2) Delete them (take a backup / dry-run by printing toDelete first!)
db.users.deleteMany({ _id: { $in: toDelete } }).deletedCount;    // Output: 3

// 3) Now the unique index can be created, and prevents future duplicates
db.users.createIndex({ email: 1 }, { unique: true });            // Output: 'email_1'
try { db.users.insertOne({ email: "a@x.in" }); } catch (e) { print(e.code); }  // Output: 11000

// 4) Creating the unique index on DIRTY data fails — that is why we cleaned first
db.u2.insertMany([{ _id: 1, email: "a@x.in" }, { _id: 2, email: "a@x.in" }]);
try { db.u2.createIndex({ email: 1 }, { unique: true }); }
catch (e) { print(e.code, e.codeName); }                         // Output: 11000 DuplicateKey

// 5) Multi-field duplicates and case-insensitive match
db.u2.aggregate([
  { $group: { _id: { e: { $toLower: "$email" }, city: "$city" }, n: { $sum: 1 } } },
  { $match: { n: { $gt: 1 } } }
], { allowDiskUse: true });                                       // allowDiskUse for big collections
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, lowercase: true, trim: true, unique: true }, // unique index + normalization
});
const User = mongoose.model('User', userSchema);

// Admin report: GET /admin/duplicates
app.get('/admin/duplicates', async (req, res) => {
  const dupes = await User.aggregate([
    { $group: { _id: '$email', ids: { $push: '$_id' }, n: { $sum: 1 } } },
    { $match: { n: { $gt: 1 } } },
    { $limit: 100 },                      // never return unbounded reports
  ]).allowDiskUse(true);
  res.json(dupes);
});

// Signup: rely on the unique index, convert error 11000 into a friendly 409
app.post('/signup', async (req, res) => {
  try {
    const u = await User.create({ email: req.body.email });
    res.status(201).json({ id: u._id });
  } catch (e) {
    if (e.code === 11000) return res.status(409).json({ error: 'email already registered' });
    throw e;
  }
});
// NOTE: `unique: true` in Mongoose is an index hint, not a validator. If the collection already has
// duplicates, index creation fails silently at startup (autoIndex error event) — clean data first.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Deleting all members of each duplicate group
```javascript
// Wrong — removes the survivor too, so the user vanishes completely
db.users.deleteMany({ _id: { $in: allIdsFromEveryDuplicateGroup } });

// Right — keep ids[0] (oldest) and delete only ids.slice(1)
g.ids.shift(); toDelete.push(...g.ids);
```

❌ Mistake 2: Ignoring case/whitespace
✅ Correct: `A@x.in` and `a@x.in ` are different strings. Normalize (`$toLower`, `$trim`) in the pipeline, and store the normalized form (Mongoose `lowercase: true, trim: true`) so the unique index works.

❌ Mistake 3: Relying on "check, then insert" in code
✅ Correct: Only a unique index is race-safe. Catch error 11000 instead.

❌ Mistake 4: One huge `$push` on a hot key
✅ Correct: A group with millions of ids can exceed the 16 MB document limit; count first (`$sum`), then page through ids of the specific key.

---

## 🧠 Tricky Interview Question

```javascript
// 'dupes' has [{email:"a@x.in"}, {email:"a@x.in"}]. You run:
db.users.createIndex({ email: 1 }, { unique: true })
// What happens? And how do you add uniqueness without first cleaning (legacy data)?
```
Answer: The build **fails** with `E11000 duplicate key error` and no index is created. You must remove the duplicates first. If you cannot immediately, you can add a **partial unique index** that only covers new/clean records, e.g. `createIndex({ email: 1 }, { unique: true, partialFilterExpression: { migrated: true } })`, and migrate documents gradually by setting `migrated: true` after cleaning each one. Another valid answer: add a `unique` index on a new field (`emailLower`) populated only for validated rows.

---

## ⚫ Interview Questions + Answers

Q1: How do you find duplicate documents by a field?
A1: `aggregate([{ $group: { _id: "$field", ids: { $push: "$_id" }, n: { $sum: 1 } } }, { $match: { n: { $gt: 1 } } }])`. For several fields, make `_id` an object: `{ a: "$a", b: "$b" }`.

Q2: How do you delete duplicates but keep one?
A2: Sort so the survivor comes first, group with `$push` of ids, drop the first id of each group, and `deleteMany({ _id: { $in: rest } })`. Alternatively, use `$group` with `$first: "$$ROOT"` to pick the survivor and `$out`/`$merge` into a clean collection, then swap.

Q3: How do you prevent duplicates permanently?
A3: A unique index (`{ unique: true }`), optionally compound, partial or with a case-insensitive collation `{ locale: "en", strength: 2 }`. Handle error 11000 in the app. For idempotent imports use upsert with `$setOnInsert`.

Q4: Why can `createIndex` with unique fail, and what is the error?
A4: Existing duplicates for the indexed key; the server returns `E11000 DuplicateKey` (code 11000) and aborts the build. Clean data first or use a partial index.

Q5: Any performance issues with `$group`?
A5: `$group` holds data in memory with a 100 MB per-stage limit (spills to disk only with `allowDiskUse: true`; newer versions can spill automatically depending on settings). Use `$match`/`$project` first and an index on the group key to help the scan.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Cleaning legacy data before adding a unique constraint
- Auditing imports, double submissions or retried webhooks

❌ Avoid when:
- You can prevent duplicates at write time (unique index + upsert), which is always cheaper than cleaning later
- The collection is enormous and live: run the cleanup in batches off-peak or on a secondary/snapshot copy

---

## 📊 Visual Diagram
```
FIND + REMOVE DUPLICATES
──────────────────────────────────────────────────────
 users                    $group by email
 ┌───┬────────┐
 │ 1 │ a@x.in │──┐
 │ 3 │ a@x.in │──┼─► a@x.in : ids [1,3,4] n=3  ──keep 1, delete 3,4
 │ 4 │ a@x.in │──┘
 │ 2 │ b@x.in │──┐
 │ 5 │ b@x.in │──┴─► b@x.in : ids [2,5]   n=2  ──keep 2, delete 5
 │ 6 │ c@x.in │─────► c@x.in : n=1 (filtered out by $match n>1)
 └───┴────────┘
 After cleaning:  createIndex({email:1},{unique:true})  → future dup = E11000
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Duplicate | Same key value in several docs | कई docs में एक जैसी key value |
| $group | Bucket documents by a key | Key के हिसाब से buckets बनाना |
| $push | Collect values into an array | Values को array में इकट्ठा करना |
| Unique index | Rejects repeated key values | दोहराई key values reject करता है |
| E11000 | DuplicateKey error code | Duplicate key error का code |
| Upsert | Update or insert if missing | Update, न मिले तो insert |
| allowDiskUse | Let stages spill to disk | Stage को disk पर spill करने देना |

---

## ⚡ 3-Line Summary
English:
1. Find duplicates with `$group` + `$push`/`$sum` then `$match n > 1`.
2. Sort first, keep `ids[0]`, delete the rest, and back up before deleting.
3. Enforce a unique index (normalized values) so duplicates cannot return; handle E11000.

Hindi:
1. Duplicates `$group` + `$push`/`$sum` और फिर `$match n > 1` से ढूँढो।
2. पहले sort करो, `ids[0]` रखो, बाकी delete करो, और delete से पहले backup लो।
3. Normalized values पर unique index लगाओ ताकि duplicates वापस न आएँ; E11000 संभालो।

---

## ➡️ Next Topic
**119. Paginated Search API with Filters** — filtered, sorted, paginated listing with skip vs keyset and `$facet` totals.
