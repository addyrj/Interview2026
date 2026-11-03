# 19. Update Operators — $set, $unset, $inc, $rename
# हिंदी में: Update Operators — $set, $unset, $inc, $rename

---

## 🔵 Simple Definition (English)
Field update operators change specific fields without rewriting the document: **`$set`** sets/adds a field, **`$unset`** removes a field, **`$inc`** adds a number (atomic counter), **`$rename`** renames a field. You can combine several operators in one update.

## 🔵 सरल परिभाषा (Hindi)
Field update operators पूरा document दोबारा लिखे बिना specific fields बदलते हैं: **`$set`** field set/add करता है, **`$unset`** field हटाता है, **`$inc`** number जोड़ता है (atomic counter), **`$rename`** field का नाम बदलता है। एक update में कई operators मिला सकते हैं।

---

## 🔴 Problem it Solves
Read-modify-write from the app (`get`, change in JS, `save`) is slow and racy: two requests incrementing a counter both read 5 and both write 6. `$inc` does it atomically in the database. `$unset` and `$rename` help evolve schemas without migrations scripts that rewrite everything by hand.

## 🔴 यह क्यों बना? (Hindi)
App में read-modify-write (`get`, JS में बदलो, `save`) धीमा और race-prone है: दो requests counter बढ़ाते हैं, दोनों 5 पढ़ती हैं और दोनों 6 लिखती हैं। `$inc` यह database में atomically करता है। `$unset` और `$rename` schema evolve करने में मदद करते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `$set: {a: v}` assigns `a` (creates it if missing; dot notation reaches nested fields).
Step 2 → `$unset: {a: ""}` deletes the field (the value given is ignored).
Step 3 → `$inc: {a: n}` adds n (negative to subtract); a missing field is created with value n; non-numeric field errors.
Step 4 → `$rename: {old: "new"}` moves the value to a new field name; if `old` does not exist nothing happens.
Step 5 → All operators in one update document are applied atomically to each matched doc; the same field cannot appear in two operators (conflict error).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `$set: {a: v}` `a` को assign करता है (न हो तो बनाता है; dot notation से nested fields)।
Step 2 → `$unset: {a: ""}` field हटाता है (दी गई value ignore होती है)।
Step 3 → `$inc: {a: n}` n जोड़ता है (घटाने के लिए negative); field न हो तो value n से बनती है; non-numeric field पर error।
Step 4 → `$rename: {old: "new"}` value को नए field name पर ले जाता है; `old` न हो तो कुछ नहीं होता।
Step 5 → एक update document के सभी operators हर matched doc पर atomically लागू होते हैं; एक ही field दो operators में नहीं आ सकती (conflict error)।

---

## 🟡 Real World Example
Flipkart's inventory service decrements stock with `updateOne({sku, stock:{$gte:1}}, {$inc:{stock:-1}})` – the filter plus `$inc` makes "never go below zero" atomic. A migration renames `mobileNo` to `phone` across all users using `$rename`, and removes the legacy `tempToken` field with `$unset`.

## 🟡 Real Example Hindi mein
Flipkart की inventory service stock `updateOne({sku, stock:{$gte:1}}, {$inc:{stock:-1}})` से घटाती है – filter और `$inc` मिलकर "zero से नीचे कभी नहीं" atomic बनाते हैं। Migration सभी users में `mobileNo` को `phone` में `$rename` से बदलता है, और पुराना `tempToken` field `$unset` से हटाता है।

---

## 💻 Code Example — Basic

```javascript
// mongod 8.0.4, database "mh"; doc { n: "c", p: 30, z: 2 } (z came from the previous note)
db.m.updateOne(
  { n: "c" },
  { $inc: { p: 5 },            // 30 + 5 = 35
    $rename: { z: "zz" },      // z -> zz
    $unset: { q: "" } }        // q does not exist -> no error, nothing happens
)
db.m.findOne({ n: "c" }, { _id: 0 })
// Output: { n: 'c', p: 35, zz: 2 }

db.m.updateOne({ n: "a" }, { $rename: { z: "zed" }, $unset: { p: "" } })
db.m.findOne({ n: "a" }, { _id: 0 })
// Output: { n: 'a', zed: 2 }       <- p removed, z renamed
```

## 💻 Code Example — Advanced

```javascript
// Nested field with dot notation + $inc creating a missing field
db.stats.insertOne({ _id: 1, views: 10 })
db.stats.updateOne({ _id: 1 }, { $set: { "meta.lastSeen": new Date() }, $inc: { likes: 1 } })
// meta created as embedded doc; likes missing -> created with value 1

// Atomic guarded decrement (inventory)
db.stock.insertOne({ sku: "S1", qty: 1 })
const r = db.stock.updateOne({ sku: "S1", qty: { $gte: 1 } }, { $inc: { qty: -1 } })
// r.modifiedCount: 1   -> second identical call:
db.stock.updateOne({ sku: "S1", qty: { $gte: 1 } }, { $inc: { qty: -1 } }).modifiedCount  // 0  (sold out, qty stays 0)

// Same field in two operators -> error
// db.m.updateOne({n:"a"}, { $set:{p:1}, $inc:{p:1} })  // Error: Updating the path 'p' would create a conflict at 'p'

// $inc on a string field -> error
// db.m.updateOne({n:"a"}, { $inc:{ n: 1 } })  // Error: Cannot apply $inc to a value of non-numeric type

// $set with an array/obj replaces the entire value
db.m.updateOne({ n: "c" }, { $set: { tags: ["x"] } })
```
(All verified on mongod 8.0.4: guarded decrement gave modifiedCount 1 then 0; the conflict error is "Updating the path 'p' would create a conflict at 'p'"; $inc on a string gives "Cannot apply $inc to a value of non-numeric type".)

---

## 🟠 Express.js / Mongoose Integration

```javascript
// POST /videos/:id/view  - atomic view counter
app.post('/videos/:id/view', async (req, res) => {
  await Video.updateOne({ _id: req.params.id }, { $inc: { views: 1 } }); // no read needed
  res.sendStatus(204);
});
// Mongoose: mongoose.set('strictQuery'...) irrelevant here; but update paths NOT in schema are
// stripped silently in strict mode - $set of an unknown field does nothing unless { strict: false }.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Updating without `$set` (document replace semantic confusion)
```javascript
db.m.updateOne({ n: "a" }, { p: 1 })              // Wrong: error (needs operators)
db.m.updateOne({ n: "a" }, { $set: { p: 1 } })    // Right
```

❌ Mistake 2: Read-modify-write counters
```javascript
const d = await C.findOne({_id}); await C.updateOne({_id}, {$set:{n: d.n + 1}}) // Wrong: race
await C.updateOne({_id}, {$inc:{n: 1}})                                          // Right
```

❌ Mistake 3: Expecting `$unset: {a: false}` to keep the field
✅ Correct: The value is ignored; `$unset` always removes.

---

## 🧠 Tricky Interview Question
Q: `$inc: { count: 1 }` on a document that has no `count`. Result?
Answer: The field is created with value 1 (`$inc` on a missing field behaves like `$set` to the increment). If `count` were a string, the update errors out.

---

## ⚫ Interview Questions + Answers

Q1: Difference between `$set` and replacing a document?
A1: `$set` touches only named fields; replacement swaps the whole doc except `_id`.

Q2: Is `$inc` atomic and safe for concurrency?
A2: Yes, per document.

Q3: What happens when `$rename` target already exists?
A3: Target value is overwritten by the source value, and the source field is removed.

Q4: Can `$rename` move to nested paths?
A4: Yes, e.g. `{$rename: {"a": "meta.a"}}` (not for array elements).

Q5: How to set a field to current time?
A5: `$currentDate: { updatedAt: true }` or `$set: { updatedAt: new Date() }`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Counters, partial updates, schema evolution

❌ Avoid `$rename` over huge collections when:
- Peak traffic – it rewrites every document (use off-peak migration)

---

## 📊 Visual Diagram
```
before: { n:"c", p:30, z:2 }
$inc    p:+5      → p: 35
$rename z → zz    → zz: 2
$unset  q         → (nothing)
after : { n:"c", p:35, zz:2 }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| $set | Set/add a field | Field set/add |
| $unset | Remove a field | Field हटाना |
| $inc | Atomic add | Atomic जोड़ना |
| $rename | Rename a field | Field का नाम बदलना |
| Atomic | All-or-nothing per doc | Per doc सब-या-कुछ नहीं |

---

## ⚡ 3-Line Summary
English:
1. `$set` writes, `$unset` removes, `$inc` adds atomically, `$rename` renames.
2. Never do read-modify-write for counters.
3. One field cannot appear in two operators in the same update.

Hindi:
1. `$set` लिखता है, `$unset` हटाता है, `$inc` atomically जोड़ता है, `$rename` नाम बदलता है।
2. Counters के लिए कभी read-modify-write मत करो।
3. एक ही update में एक field दो operators में नहीं आ सकती।

---

## ➡️ Next Topic
**20. Array Update Operators — $push, $pull, $addToSet, $pop**
