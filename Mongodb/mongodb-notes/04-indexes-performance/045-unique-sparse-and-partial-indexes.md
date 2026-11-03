# 45. Unique, Sparse and Partial Indexes
# हिंदी में: Unique, Sparse और Partial Indexes

---

## 🔵 Simple Definition (English)
- **Unique index**: rejects a second document with the same indexed value (duplicate key error code `11000`).
- **Sparse index**: only indexes documents that **have** the field (skips missing ones; `null` is still indexed).
- **Partial index**: only indexes documents matching a `partialFilterExpression` (more flexible, smaller, and recommended over sparse).

## 🔵 सरल परिभाषा (Hindi)
- **Unique index**: उसी indexed value वाला दूसरा document reject करता है (duplicate key error code `11000`)।
- **Sparse index**: सिर्फ उन documents को index करता है जिनमें field **मौजूद** है (missing छोड़ देता है; `null` फिर भी index होता है)।
- **Partial index**: सिर्फ उन documents को index करता है जो `partialFilterExpression` से match करते हैं (ज़्यादा flexible, छोटा, और sparse से बेहतर माना जाता है)।

---

## 🔴 Problem it Solves
Uniqueness (one account per email) must be enforced by the database, not by app code, because concurrent requests can race. But optional fields break plain unique indexes: missing is treated as `null`, so only ONE document without the field is allowed. Sparse/partial indexes fix that, and partial indexes also save space by indexing only the relevant subset (e.g., only `paid` orders).

## 🔴 यह क्यों बना? (Hindi)
Uniqueness (एक email पर एक account) database को enforce करनी चाहिए, app code को नहीं, क्योंकि concurrent requests race कर सकती हैं। पर optional fields plain unique index को तोड़ देते हैं: missing को `null` माना जाता है, इसलिए बिना field वाला सिर्फ एक document allowed है। Sparse/partial indexes इसे ठीक करते हैं, और partial index सिर्फ ज़रूरी subset (जैसे सिर्फ `paid` orders) index करके जगह भी बचाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `createIndex({ email: 1 }, { unique: true })` - every future insert/update is checked against existing keys.
Step 2 → If existing data already has duplicates (or several missing values), index creation fails with `DuplicateKey` (verified with two docs lacking `email`).
Step 3 → Fix with `{ unique: true, sparse: true }`: documents without `email` are not in the index, so any number can lack it.
Step 4 → Or with a partial index: `partialFilterExpression: { email: { $exists: true } }` (same effect, explicit; works for `$type`, `$gt`, equality too).
Step 5 → Partial index is used by a query only if the query's filter is guaranteed to be within the index's filter. E.g. index filter `status: "paid"` serves `{ amount: 5, status: "paid" }` but not `{ amount: 5 }`.
Step 6 → Sparse index caveat: a sort or query that needs missing documents will not use it (it would miss them); hinting forces it and returns incomplete results.
Step 7 → Compound unique: `{ restaurantId: 1, name: 1 }` is unique on the PAIR.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `createIndex({ email: 1 }, { unique: true })` - हर आगे का insert/update मौजूदा keys से check होता है।
Step 2 → पहले से duplicates (या कई missing values) हों तो index बनाना `DuplicateKey` से fail होता है (दो बिना-`email` docs से verified)।
Step 3 → `{ unique: true, sparse: true }` से fix: बिना `email` वाले documents index में नहीं होते, इसलिए कितने भी बिना field के हो सकते हैं।
Step 4 → या partial index: `partialFilterExpression: { email: { $exists: true } }` (वही असर, ज़्यादा साफ़)।
Step 5 → Partial index तभी use होता है जब query का filter index के filter के अंदर पक्का हो। Index filter `status: "paid"` हो तो `{ amount: 5, status: "paid" }` use करेगा पर `{ amount: 5 }` नहीं।
Step 6 → Sparse caveat: जो query missing documents चाहती है वह इसे use नहीं करेगी; hint से force करने पर अधूरे results आते हैं।
Step 7 → Compound unique: `{ restaurantId: 1, name: 1 }` जोड़ी पर unique है।

---

## 🟡 Real World Example
**Razorpay** merchants: `email` is mandatory and unique, but `gstin` is optional and must be unique when present. `gstin` gets a unique partial index (`gstin` exists) so thousands of merchants without GSTIN are fine, while duplicates of a real GSTIN are blocked. For `payments`, a partial index on `{ status: "failed" }` keeps a tiny index for the retry job instead of indexing all crores of payments.

## 🟡 Real Example Hindi mein
**Razorpay** merchants में `email` ज़रूरी और unique है, पर `gstin` optional है और मौजूद होने पर unique होना चाहिए। `gstin` पर unique partial index (जहाँ `gstin` exists) बनता है, इसलिए बिना GSTIN वाले हज़ारों merchants ठीक हैं और असली GSTIN का duplicate रुकता है। `payments` में `{ status: "failed" }` पर partial index retry job के लिए छोटा index रखता है, करोड़ों payments का पूरा index नहीं।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4)
use uniq_demo
db.users.insertMany([{ email: "a@x.com" }, { name: "noemail" }, { name: "noemail2" }])

// 1) Plain unique FAILS: two docs lack email -> both look like null
db.users.createIndex({ email: 1 }, { unique: true })
// MongoServerError: Index build failed ... E11000 duplicate key (codeName DuplicateKey)

// 2) Unique + sparse works
db.users.createIndex({ email: 1 }, { unique: true, sparse: true })   // Output: 'email_1'
db.users.insertOne({ email: "b@x.com" })                              // ok, acknowledged
db.users.insertOne({ email: "a@x.com" })
// MongoServerError: E11000 duplicate key error collection: uniq_demo.users index: email_1 (code 11000)

// 3) Replace with the partial-index version (preferred)
db.users.dropIndexes()                                                // drops all except _id
db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { email: { $exists: true } } })
db.users.insertOne({ name: "x3" })                                    // ok: not in the index
```

## 💻 Code Example — Advanced

```javascript
// Partial index on a subset of a big collection
db.orders.createIndex({ amount: 1 }, { partialFilterExpression: { status: "paid" }, name: "p" })

// Query that includes the partial condition -> uses the small index
db.orders.find({ amount: 5, status: "paid" }).explain("executionStats")
// FETCH > IXSCAN(p)  keys 17 docs 17 returned 17    <- verified

// Query WITHOUT status: "paid" cannot use it (could miss unpaid orders)
db.orders.find({ amount: 5 }).explain("executionStats")
// COLLSCAN  docs 5000 returned 50                   <- verified

// Unique per pair
db.menu.createIndex({ restaurantId: 1, name: 1 }, { unique: true })

// Unique only among ACTIVE documents (soft-delete pattern)
db.accounts.createIndex(
  { email: 1 },
  { unique: true, partialFilterExpression: { deleted: false } }
)
// Deleted accounts (deleted: true) can reuse an email; active ones cannot duplicate
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const userSchema = new mongoose.Schema({
  email: { type: String, unique: true, sparse: true },   // unique + sparse shortcut
  gstin: String,
});
// Partial unique index via schema.index
userSchema.index({ gstin: 1 }, { unique: true, partialFilterExpression: { gstin: { $type: 'string' } } });
const User = mongoose.model('User', userSchema);

app.post('/api/users', async (req, res) => {
  try {
    res.status(201).json(await User.create(req.body));
  } catch (err) {
    if (err.code === 11000) return res.status(409).json({ error: 'Duplicate', key: err.keyValue }); // 409 Conflict
    res.status(500).json({ error: err.message });
  }
});
// Note: "unique" in a Mongoose schema is an INDEX, not a validator. Make sure indexes are built.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Unique index on an optional field without sparse/partial
```javascript
// Wrong - second doc without the field fails with E11000 (missing == null)
db.users.createIndex({ email: 1 }, { unique: true })
// Right
db.users.createIndex({ email: 1 }, { unique: true, partialFilterExpression: { email: { $exists: true } } })
```

❌ Mistake 2: Check-then-insert in application code for uniqueness
✅ Correct: rely on the unique index; two parallel requests can both pass an app-level check. Handle error 11000.

❌ Mistake 3: Expecting a partial index to serve a query that does not include its filter condition.

---

## 🧠 Tricky Interview Question

```javascript
db.u.insertOne({ email: null })
db.u.insertOne({ email: null })   // with unique+sparse index on email
```
Answer: The second insert **fails** with E11000. Sparse skips only *missing* fields; an explicit `null` value is still indexed, so two `null`s collide. A partial index with `$type: "string"` (or `$exists: true` plus non-null) is the way to ignore nulls too.

---

## ⚫ Interview Questions + Answers

Q1: What does a unique index do with missing fields?
A1: Treats a missing field as `null`, so only one document can lack it; use sparse or partial to allow many.

Q2: Sparse vs partial?
A2: Sparse indexes only documents where the field exists; partial uses an arbitrary filter expression and is the more powerful, recommended option (you cannot combine both options in one index).

Q3: What error code signals a unique violation?
A3: `11000` (E11000 duplicate key error); respond with HTTP 409.

Q4: When is a partial index used by the planner?
A4: Only if the query predicate implies the index's filter expression.

Q5: Benefit of partial indexes besides uniqueness?
A5: Smaller index = less RAM and faster writes (for example only index active/paid/failed documents).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Enforcing uniqueness (email, phone, order number)
- Indexing a small hot subset of a huge collection

❌ Avoid when:
- Queries rarely include the partial filter
- Collection is tiny

---

## 📊 Visual Diagram
```
Documents                 Unique (plain)   Unique+Sparse   Partial(exists)
{email:"a"}                 indexed          indexed         indexed
{email:"b"}                 indexed          indexed         indexed
{ }  (missing)              null key         skipped         skipped
{ }  (missing) again        DUPLICATE!       ok              ok
{email:null} twice          DUPLICATE        DUPLICATE       DUPLICATE ($exists true still matches null)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Unique index | No duplicate values | Duplicate values नहीं |
| Sparse | Skip docs missing the field | Field न होने पर skip |
| Partial | Index only matching docs | सिर्फ matching docs index |
| E11000 | Duplicate key error | Duplicate key error |
| partialFilterExpression | Filter deciding what is indexed | क्या index होगा तय करने वाला filter |

---

## ⚡ 3-Line Summary
English:
1. Unique indexes enforce uniqueness at the database level; handle error 11000.
2. Missing counts as null, so optional unique fields need sparse or (better) partial indexes.
3. Partial indexes are also small, fast indexes for hot subsets, used only when the query implies the filter.

Hindi:
1. Unique index database स्तर पर uniqueness enforce करता है; error 11000 handle करो।
2. Missing को null माना जाता है, इसलिए optional unique fields को sparse या (बेहतर) partial index चाहिए।
3. Partial index hot subset के लिए छोटा, तेज़ index भी है, जो तभी use होता है जब query उसके filter को imply करे।

---

## ➡️ Next Topic
**46. TTL Indexes**
