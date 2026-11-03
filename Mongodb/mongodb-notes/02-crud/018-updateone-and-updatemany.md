# 18. updateOne and updateMany
# हिंदी में: updateOne और updateMany

---

## 🔵 Simple Definition (English)
`updateOne(filter, update, options)` modifies the **first** document matching the filter; `updateMany` modifies **all** matches. The update document must use update operators (`$set`, `$inc`, ...) or be an aggregation pipeline array. Option `upsert: true` inserts a new document if nothing matches. Both return `matchedCount`, `modifiedCount`, `upsertedCount`, `upsertedId`.

## 🔵 सरल परिभाषा (Hindi)
`updateOne(filter, update, options)` filter से match होने वाले **पहले** document को बदलता है; `updateMany` **सभी** matches को बदलता है। Update document में update operators (`$set`, `$inc`, ...) होने चाहिए या aggregation pipeline array। `upsert: true` option से कुछ match न हो तो नया document insert होता है। दोनों `matchedCount`, `modifiedCount`, `upsertedCount`, `upsertedId` लौटाते हैं।

---

## 🔴 Problem it Solves
Rewriting a whole document to change one field wastes bandwidth and risks overwriting concurrent changes. Update operators change only specific fields atomically on the server. `updateMany` handles bulk changes (e.g., "mark all expired coupons inactive") in one round trip, and `upsert` removes the check-then-insert race.

## 🔴 यह क्यों बना? (Hindi)
एक field बदलने के लिए पूरा document दोबारा लिखना bandwidth बर्बाद करता है और concurrent changes overwrite होने का जोखिम है। Update operators server पर सिर्फ़ चुनी fields atomically बदलते हैं। `updateMany` bulk changes (जैसे "सभी expired coupons inactive करो") एक round trip में करता है, और `upsert` check-then-insert वाली race condition हटाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Server finds documents using the filter (an index makes this fast).
Step 2 → `updateOne` stops at the first match (natural order, not guaranteed meaningful – sort is not available, use `findOneAndUpdate` for that).
Step 3 → Update operators are applied atomically **per document**.
Step 4 → Result: `matchedCount` (found), `modifiedCount` (actually changed – 0 if the value was identical).
Step 5 → With `upsert: true` and no match, a new doc is built from the equality fields in the filter plus the update; `upsertedId` is returned.
Step 6 → `updateMany` is NOT atomic across documents (unless in a transaction); a failure midway leaves partial updates.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Server filter से documents ढूँढता है (index हो तो तेज़)।
Step 2 → `updateOne` पहले match पर रुक जाता है (natural order; sort उपलब्ध नहीं, उसके लिए `findOneAndUpdate`)।
Step 3 → Update operators हर document पर **per-document** atomically लागू होते हैं।
Step 4 → Result: `matchedCount` (मिले), `modifiedCount` (वास्तव में बदले – value वही थी तो 0)।
Step 5 → `upsert: true` और कोई match नहीं हो तो filter की equality fields + update से नया doc बनता है; `upsertedId` मिलता है।
Step 6 → `updateMany` documents के बीच atomic नहीं है (transaction के बिना); बीच में fail हुआ तो partial updates रह जाते हैं।

---

## 🟡 Real World Example
Razorpay's settlement job runs `updateMany({status:"CAPTURED", settledAt:null, capturedAt:{$lt: cutoff}}, {$set:{status:"SETTLED", settledAt: new Date()}})` at midnight. A webhook handler uses `updateOne({paymentId}, {$set:{...}}, {upsert:true})` so a retried webhook never creates a duplicate record.

## 🟡 Real Example Hindi mein
Razorpay का settlement job आधी रात को `updateMany({status:"CAPTURED", settledAt:null, capturedAt:{$lt: cutoff}}, {$set:{status:"SETTLED", settledAt: new Date()}})` चलाता है। Webhook handler `updateOne({paymentId}, {$set:{...}}, {upsert:true})` इस्तेमाल करता है ताकि webhook दोबारा आने पर duplicate record न बने।

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh"; m has docs with p=10 twice
db.m.updateOne({ p: 10 }, { $set: { z: 1 } })
// Output: { acknowledged: true, insertedId: null, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
//          only ONE of the two p:10 docs was changed

db.m.updateMany({ p: 10 }, { $set: { z: 2 } })
// Output: { acknowledged: true, insertedId: null, matchedCount: 2, modifiedCount: 2, upsertedCount: 0 }
//          both p:10 docs changed
```

## 💻 Code Example — Advanced

```javascript
// UPSERT: no doc has n:"zz", so one is inserted
db.m.updateOne({ n: "zz" }, { $set: { p: 1 } }, { upsert: true })
// Output: { acknowledged: true, insertedId: ObjectId('...'), matchedCount: 0, modifiedCount: 0, upsertedCount: 1 }
//          (insertedId varies per run). New doc = { _id, n: "zz", p: 1 }  <- n copied from the filter

// $setOnInsert: values applied ONLY when upsert inserts
db.m.updateOne({ n: "yy" }, { $set: { p: 2 }, $setOnInsert: { createdAt: new Date() } }, { upsert: true })

// Pipeline-style update: use other fields of the same doc
db.m.updateMany({}, [ { $set: { pTax: { $multiply: ["$p", 1.18] } } } ])   // adds 18% GST field

// arrayFilters: update only matching array elements
db.orders.updateOne(
  { _id: 1 },
  { $set: { "items.$[it].qty": 10 } },          // $[it] = identifier
  { arrayFilters: [ { "it.sku": "A1" } ] }      // which elements
)

// Re-running the same update: matched but not modified
db.m.updateOne({ n: "zz" }, { $set: { p: 1 } })  // matchedCount: 1, modifiedCount: 0 (value identical)
```
(All of these were executed on mongod 8.0.4; the pipeline update gave e.g. pTax 23.599999999999998 for p=20 - floating point.)

---

## 🟠 Express.js / Mongoose Integration

```javascript
// PATCH /users/:id  - update only provided fields
app.patch('/users/:id', async (req, res) => {
  const { name, city } = req.body;                       // whitelist fields, never pass req.body directly
  const r = await User.updateOne({ _id: req.params.id }, { $set: { name, city } }); // Mongoose casts id
  if (r.matchedCount === 0) return res.status(404).json({ error: 'not found' });
  res.json({ modified: r.modifiedCount });
});
// Bulk: await Coupon.updateMany({ expiresAt: { $lt: new Date() } }, { $set: { active: false } });
// Note: Mongoose update* skips document middleware; validators need { runValidators: true }.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting the operator (replaces nothing / errors)
```javascript
db.m.updateOne({ n: "a" }, { z: 5 })            // Wrong: Error - update document requires atomic operators
db.m.updateOne({ n: "a" }, { $set: { z: 5 } })  // Right
```

❌ Mistake 2: Using `updateOne` when many docs should change
✅ Correct: `updateMany`, and double check the filter – an empty filter `{}` updates EVERYTHING.

❌ Mistake 3: Treating `matchedCount` as changed rows
✅ Correct: Check `modifiedCount` for actual changes.

❌ Mistake 4: Upsert without a unique index
✅ Correct: Concurrent upserts can insert duplicates; back them with a unique index.

---

## 🧠 Tricky Interview Question
Q: `updateOne({n:"zz"}, {$set:{p:1}})` run twice. What are the two results?
Answer: If the doc does not exist, the first run (with upsert) inserts it: upsertedCount 1. A second identical run returns `matchedCount: 1, modifiedCount: 0` (verified), because nothing needed to change. Matched is not modified.

---

## ⚫ Interview Questions + Answers

Q1: updateOne vs replaceOne?
A1: `updateOne` modifies fields via operators; `replaceOne` swaps the entire document (keeping `_id`).

Q2: Is updateMany atomic?
A2: Each document update is atomic, the whole operation is not. Use a transaction for all-or-nothing.

Q3: What does upsert build?
A3: A doc from equality conditions in the filter, plus operators applied; `$setOnInsert` fields only on insert.

Q4: How to update the first doc by order?
A4: `findOneAndUpdate` with `sort`; `updateOne` has no sort option on 8.0 (newer versions may add one).

Q5: How to avoid duplicate upserts?
A5: Unique index and retry on E11000.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Partial field changes, bulk status changes, idempotent upserts

❌ Avoid when:
- You need all-or-nothing across documents without a transaction

---

## 📊 Visual Diagram
```
updateOne(filter, {$set:..})      updateMany(filter, {$set:..})
   [d1*][d2*][d3 ]                    [d1*][d2*][d3 ]
     ▲ first match only                ▲ ▲ every match
   matched:1 modified:1              matched:2 modified:2
   no match + upsert:true  ──►  insert new doc (upsertedId)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| upsert | Update or insert | Update या insert |
| matchedCount | Docs found | मिले documents |
| modifiedCount | Docs changed | बदले documents |
| $setOnInsert | Only on upsert insert | सिर्फ़ upsert insert पर |
| arrayFilters | Pick array elements | Array elements चुनना |

---

## ⚡ 3-Line Summary
English:
1. `updateOne` changes the first match, `updateMany` all matches, with operators.
2. `matchedCount` differs from `modifiedCount`; `upsert` inserts when nothing matches.
3. Whitelist fields and beware empty filters.

Hindi:
1. `updateOne` पहला match बदलता है, `updateMany` सभी, operators के साथ।
2. `matchedCount` और `modifiedCount` अलग हैं; कुछ match न हो तो `upsert` insert करता है।
3. Fields whitelist करो और खाली filter से सावधान रहो।

---

## ➡️ Next Topic
**19. Update Operators — $set, $unset, $inc, $rename**
