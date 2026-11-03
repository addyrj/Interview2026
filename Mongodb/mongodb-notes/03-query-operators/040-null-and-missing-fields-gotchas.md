# 40. Null and Missing Fields Gotchas
# हिंदी में: Null और Missing Fields की गड़बड़ियाँ

---

## 🔵 Simple Definition (English)
In MongoDB a field can be **present with a value**, **present with `null`**, or **completely missing**. These three states are different, but several operators treat `null` and missing the same. The biggest gotcha: `{ field: null }` matches **both** null values **and** missing fields. To separate them you need `$exists` and `$type`.

## 🔵 सरल परिभाषा (Hindi)
MongoDB में field की तीन स्थितियाँ हो सकती हैं: **value के साथ मौजूद**, **`null` के साथ मौजूद**, या **बिल्कुल गायब (missing)**। ये तीनों अलग हैं, पर कई operators `null` और missing को एक जैसा मानते हैं। सबसे बड़ी गड़बड़ी: `{ field: null }` **null values और missing fields दोनों** को match करता है। इन्हें अलग करने के लिए `$exists` और `$type` चाहिए।

---

## 🔴 Problem it Solves
Because MongoDB is schema-flexible, documents inserted years apart can differ: old users have no `phone`, some have `phone: null` after a form clear. If you do not understand the semantics, queries like "users without a phone" return surprising rows, and unique indexes treat missing as `null` (only one missing allowed!). Knowing these rules avoids bugs in filters, sorting and indexes.

## 🔴 यह क्यों बना? (Hindi)
MongoDB schema-flexible है, इसलिए सालों के अंतर से डाले documents अलग हो सकते हैं: पुराने users में `phone` नहीं है, कुछ में form clear होने पर `phone: null` है। Semantics न पता हों तो "बिना phone वाले users" जैसी query अजीब rows देती है, और unique index missing को `null` मानता है (सिर्फ एक missing allowed!)। ये नियम जानने से filters, sorting और indexes के bugs बचते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ f: null }` matches documents where `f` is `null` **or** `f` does not exist.
Step 2 → `{ f: { $exists: true } }` matches documents where the field exists, **including `null` values**.
Step 3 → `{ f: { $exists: false } }` matches only documents where the field is missing.
Step 4 → `{ f: { $type: "null" } }` (or `$type: 10`) matches only an explicit `null`.
Step 5 → `{ f: { $ne: null } }` matches documents where `f` exists and is not null.
Step 6 → Sorting: missing and null sort lowest (before all other values). In `mongosh`, an `undefined` value is stored as `null`.
Step 7 → Unique indexes treat missing as `null`, so two documents without the field collide. Use a sparse or partial index.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `{ f: null }` उन documents को match करता है जहाँ `f` `null` है **या** मौजूद ही नहीं है।
Step 2 → `{ f: { $exists: true } }` वहाँ match करता है जहाँ field मौजूद है, **`null` values समेत**।
Step 3 → `{ f: { $exists: false } }` सिर्फ वहाँ जहाँ field missing है।
Step 4 → `{ f: { $type: "null" } }` (या `$type: 10`) सिर्फ explicit `null` को match करता है।
Step 5 → `{ f: { $ne: null } }` वहाँ जहाँ `f` मौजूद है और null नहीं है।
Step 6 → Sorting: missing और null सबसे छोटे माने जाते हैं। `mongosh` में `undefined` को `null` के रूप में store किया जाता है।
Step 7 → Unique index missing को `null` मानता है, इसलिए बिना field के दो documents टकराते हैं। Sparse या partial index use करो।

---

## 🟡 Real World Example
**Razorpay** merchant profiles: older merchants have no `gstin` field, newer ones who skipped it have `gstin: null`, and verified ones have a string. The compliance team wants "merchants whose GSTIN is not provided" - `{ gstin: null }` correctly returns both older and skipped merchants, but the "data migration" team wants only the ones with explicit `null` to backfill, so they use `$type: "null"`.

## 🟡 Real Example Hindi mein
**Razorpay** merchant profiles: पुराने merchants में `gstin` field नहीं है, नए जिन्होंने skip किया उनमें `gstin: null` है, और verified में string है। Compliance team को "जिनका GSTIN नहीं दिया गया" चाहिए - `{ gstin: null }` पुराने और skip करने वाले दोनों देता है, पर migration team को सिर्फ explicit `null` वाले चाहिए तो `$type: "null"` use होता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4)
use null_demo
db.u.insertMany([
  { n: "a", phone: "1" },        // has a value
  { n: "b", phone: null },       // explicit null
  { n: "c" },                    // phone missing
  { n: "d", phone: undefined }   // mongosh stores this as null
])

db.u.find({ phone: null })                    // Output: b, c, d   (null OR missing)
db.u.find({ phone: { $exists: true } })       // Output: a, b, d   (present, nulls included)
db.u.find({ phone: { $exists: false } })      // Output: c         (only missing)
db.u.find({ phone: { $type: 10 } })           // Output: b, d      (only explicit null; same as $type: "null")
db.u.find({ phone: { $ne: null } })           // Output: a         (exists and not null)
db.u.find({ phone: { $type: "string" } })     // Output: a
db.u.find({ phone: { $in: [null] } })         // Output: b, c, d   (same as { phone: null })
```

## 💻 Code Example — Advanced

```javascript
// Truly missing vs null using aggregation expressions
db.u.aggregate([
  { $match: { $expr: { $eq: [{ $type: "$phone" }, "missing"] } } },  // $type returns the string "missing"
  { $project: { n: 1, _id: 0 } }
])
// Output: [ { n: 'c' } ]

// Sort order: null / missing come first in ascending sort
db.u.find().sort({ phone: 1 })   // order: b, c, d, a  (null/missing first, "1" last)

// Fill missing/null with a default when reading
db.u.aggregate([
  { $project: { n: 1, phone: { $ifNull: ["$phone", "N/A"] } } }   // $ifNull catches null AND missing
])

// Unique index trap: two docs without the field collide
db.users.insertMany([{ email: "a@x.com" }, { name: "noemail" }, { name: "noemail2" }])
db.users.createIndex({ email: 1 }, { unique: true })
// Error: E11000 duplicate key (the two missing emails both look like null)   <- verified
db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { email: { $exists: true } } })
// Works: only documents that have email are indexed
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Express: users who have NOT provided a phone (null or missing)
app.get('/api/users/no-phone', async (req, res) => {
  const users = await db.collection('users').find({ phone: null }).toArray();
  res.json(users);
});

// Mongoose: undefined fields are omitted on save, null is stored as null
const userSchema = new mongoose.Schema({
  phone: { type: String, default: null },   // default null so the field always exists
});
// strict mode removes unknown fields; use $type: 'null' via the filter to find explicit nulls
await User.find({ phone: { $type: 'null' } });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `{ field: null }` to find only explicit nulls
```javascript
// Wrong - also returns documents where the field is missing
db.u.find({ phone: null })
// Right - only explicit null
db.u.find({ phone: { $type: "null" } })
```

❌ Mistake 2: Using `$exists: true` to find "has a real value"
✅ Correct: `$exists: true` also matches `null`. Use `{ phone: { $ne: null } }` (or `$type: "string"`).

❌ Mistake 3: Unique index on an optional field without sparse/partial option - the second missing value triggers a duplicate key error.

---

## 🧠 Tricky Interview Question

```javascript
db.u.find({ phone: null }).count()     // documents: "1", null, (missing), undefined
db.u.find({ phone: { $exists: false } }).count()
```
Answer: The first returns `3` (explicit null, missing, and `undefined` stored as null); the second returns `1` (only the missing one). The lesson: `null` equality is "null or missing", while `$exists: false` is strictly missing.

---

## ⚫ Interview Questions + Answers

Q1: Does `{ a: null }` match documents without `a`?
A1: Yes. It matches both `a: null` and a missing `a`.

Q2: How do you match only documents where the field is explicitly null?
A2: `{ a: { $type: "null" } }` (BSON type 10).

Q3: Does `$exists: true` exclude nulls?
A3: No. It only checks that the field is present; null is a present value.

Q4: Why does a unique index fail on an optional field?
A4: Missing is indexed as `null`, so a second document without the field duplicates the first. Use `sparse: true` or a partial index with `$exists: true`.

Q5: How is null sorted?
A5: Null and missing are lowest in ascending order, so they appear first.

---

## 🔷 When to Use + When Not to Use
✅ Use these checks when:
- Optional fields exist in old and new data
- You need unique indexes on optional fields

❌ Avoid:
- Mixing `null`, `""` and missing for the same meaning - pick one convention (and enforce with schema validation)

---

## 📊 Visual Diagram
```
doc              {phone:null}  $exists:true  $exists:false  $type:null  $ne:null
{phone:"1"}          no            yes            no            no         yes
{phone:null}         YES           yes            no            YES        no
{phone: missing}     YES           no             YES           no         no
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| null | Explicit empty value | साफ़ तौर पर खाली value |
| Missing field | Field not in document | Document में field नहीं |
| $exists | Checks field presence | Field की मौजूदगी जाँचता है |
| $type | Checks BSON type | BSON type जाँचता है |
| $ifNull | Default for null/missing | null/missing के लिए default |

---

## ⚡ 3-Line Summary
English:
1. `{ f: null }` matches null AND missing.
2. `$exists: true` includes nulls; `$type: "null"` is explicit null only; `$exists: false` is missing only.
3. Unique indexes treat missing as null - use sparse/partial indexes.

Hindi:
1. `{ f: null }` null और missing दोनों को match करता है।
2. `$exists: true` में null भी आता है; `$type: "null"` सिर्फ explicit null; `$exists: false` सिर्फ missing।
3. Unique index missing को null मानता है - sparse/partial index use करो।

---

## ➡️ Next Topic
**41. What are Indexes + How B-Tree Works in MongoDB**
