# 162. Mongoose CRUD
# हिंदी में: Mongoose CRUD — Create, Read, Update, Delete

---

## 🔵 Simple Definition (English)
Mongoose provides CRUD methods on every Model: `create()`/`save()` for Create, `find()`/`findOne()`/`findById()` for Read, `updateOne()`/`updateMany()`/`findByIdAndUpdate()` for Update, and `deleteOne()`/`deleteMany()`/`findByIdAndDelete()` for Delete. Queries can be chained (`.sort()`, `.limit()`, `.select()`) and executed either by `await`ing directly or calling `.exec()`.

## 🔵 सरल परिभाषा (Hindi)
Mongoose हर Model पर CRUD methods देता है: Create के लिए `create()`/`save()`, Read के लिए `find()`/`findOne()`/`findById()`, Update के लिए `updateOne()`/`updateMany()`/`findByIdAndUpdate()`, Delete के लिए `deleteOne()`/`deleteMany()`/`findByIdAndDelete()`। Queries chain हो सकती हैं (`.sort()`, `.limit()`, `.select()`) और `await` से या `.exec()` से चलती हैं।

---

## 🔴 Problem it Solves
Without a structured ORM/ODM, every CRUD operation against MongoDB means manually writing the native driver's slightly verbose API, handling `ObjectId` conversion, and losing out on automatic validation during updates. Mongoose's CRUD API wraps this in a more ergonomic, chainable, promise-based interface with validation integrated directly into `create`/`save`, consistent error shapes (`ValidationError`, `CastError`), and convenience methods like `findByIdAndUpdate` that combine lookup + update + validation in one call.

## 🔴 यह क्यों बना? (Hindi)
Structured ORM/ODM के बिना, हर CRUD operation में native driver की थोड़ी verbose API manually लिखनी पड़ती, `ObjectId` conversion manually handle करनी पड़ती, और updates के दौरान automatic validation नहीं मिलती। Mongoose का CRUD API इसे ज़्यादा ergonomic, chainable, promise-based interface में wrap करता है, validation `create`/`save` में built-in है, consistent error shapes (`ValidationError`, `CastError`) मिलते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → **Create**: `Model.create(data)` (validates + saves in one call) or `new Model(data)` + `doc.save()` (more control, e.g., modifying before saving).
Step 2 → **Read**: `find(filter)` returns an array; `findOne(filter)` returns the first match or `null`; `findById(id)` is shorthand for `findOne({ _id: id })`.
Step 3 → **Update**: `updateOne`/`updateMany` modify matching documents directly in the DB (skip validation unless `runValidators: true`); `findByIdAndUpdate(id, data, { new: true })` returns the UPDATED document when `new: true` is passed.
Step 4 → **Delete**: `deleteOne`/`deleteMany` remove matching documents; `findByIdAndDelete(id)` returns the deleted document.
Step 5 → **Query chaining**: `.find().sort({ createdAt: -1 }).limit(10).select('name email').lean()` — `.lean()` returns plain JS objects (faster, no Mongoose document overhead) when you don't need instance methods.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Create**: `Model.create(data)` या `new Model(data)` + `doc.save()`।
Step 2 → **Read**: `find(filter)` array देता है; `findOne(filter)` पहला match या `null`; `findById(id)` shorthand है।
Step 3 → **Update**: `updateOne`/`updateMany` DB में directly modify करते (validation skip by default); `findByIdAndUpdate(id, data, { new: true })` updated document return करता है।
Step 4 → **Delete**: `deleteOne`/`deleteMany` matching documents हटाते हैं; `findByIdAndDelete(id)` deleted document return करता है।
Step 5 → **Query chaining**: `.lean()` plain JS objects देता है — Mongoose document overhead के बिना, तेज़।

---

## 🟡 Real World Example
**Paytm's merchant-transactions dashboard** uses `.lean()` extensively for read-only list views (fetching thousands of transactions for display): `Transaction.find({ merchantId }).sort({ createdAt: -1 }).limit(50).lean()`. Since the dashboard only displays data and never calls instance methods on these documents, skipping Mongoose's document hydration overhead with `.lean()` noticeably speeds up large list responses. For actual transaction mutations (refunds), they use `findById` + `.save()` to get full validation and hooks.

## 🟡 Real Example Hindi mein
**Paytm का merchant-transactions dashboard** read-only list views के लिए `.lean()` बहुत इस्तेमाल करता है — सिर्फ display के लिए data चाहिए, instance methods नहीं चाहिए, तो Mongoose document hydration overhead skip करके response तेज़ होता है। Actual mutations (refunds) के लिए `findById` + `.save()` इस्तेमाल करते हैं, पूरी validation और hooks के साथ।

---

## 💻 Code Example — Basic

```javascript
// mongoose-crud-basic.js
const mongoose = require('mongoose');

const Product = mongoose.model('Product', new mongoose.Schema({
  name: String, price: Number, inStock: { type: Boolean, default: true },
}));

async function main() {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/crud_demo');

  // CREATE
  const product = await Product.create({ name: 'Keyboard', price: 1200 });
  console.log('Created:', product._id);

  // READ — find many, with filter + sort + limit
  const cheapProducts = await Product.find({ price: { $lt: 2000 } }).sort({ price: 1 }).limit(5);
  console.log('Cheap products:', cheapProducts.map(p => p.name));

  // READ ONE by ID
  const found = await Product.findById(product._id);
  console.log('Found by ID:', found.name);

  // UPDATE — findByIdAndUpdate with { new: true } returns the UPDATED doc
  const updated = await Product.findByIdAndUpdate(product._id, { price: 1100 }, { new: true, runValidators: true });
  console.log('Updated price:', updated.price);

  // DELETE
  await Product.findByIdAndDelete(product._id);
  const checkDeleted = await Product.findById(product._id);
  console.log('After delete:', checkDeleted); // null

  await mongoose.disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// mongoose-crud-advanced.js — Production patterns: lean queries, bulkWrite, pagination, atomic updates
const mongoose = require('mongoose');

const Transaction = mongoose.model('Transaction', new mongoose.Schema({
  merchantId: mongoose.Schema.Types.ObjectId,
  amount: Number,
  status: { type: String, enum: ['pending', 'completed', 'refunded'], default: 'pending' },
}, { timestamps: true }));

// ─── 1. LEAN QUERY for fast read-only lists (skips Mongoose document overhead) ──
async function getMerchantTransactions(merchantId, page = 1, pageSize = 50) {
  return Transaction.find({ merchantId })
    .sort({ createdAt: -1 })
    .skip((page - 1) * pageSize)
    .limit(pageSize)
    .select('amount status createdAt') // only fetch needed fields
    .lean(); // returns plain JS objects, NOT full Mongoose documents — faster
}

// ─── 2. ATOMIC UPDATE using findOneAndUpdate with condition (avoids race conditions) ──
async function refundTransaction(transactionId) {
  // Only refund if currently "completed" — atomic check-and-update in one DB operation
  const result = await Transaction.findOneAndUpdate(
    { _id: transactionId, status: 'completed' }, // condition acts as a guard
    { status: 'refunded' },
    { new: true }
  );
  if (!result) {
    throw new Error('Transaction not found or not in a refundable state');
  }
  return result;
}

// ─── 3. BULK WRITE — multiple different operations in ONE round trip ───────────
async function bulkUpdateStatuses(updates) {
  // updates: [{ id, newStatus }, ...]
  const operations = updates.map((u) => ({
    updateOne: {
      filter: { _id: u.id },
      update: { status: u.newStatus },
    },
  }));
  const result = await Transaction.bulkWrite(operations);
  console.log(`Bulk updated ${result.modifiedCount} transactions`);
  return result;
}

// ─── 4. COUNT + EXISTS for cheap checks without fetching full documents ─────────
async function hasAnyPendingTransactions(merchantId) {
  const count = await Transaction.countDocuments({ merchantId, status: 'pending' });
  return count > 0;
}

async function run() {
  await mongoose.connect(process.env.MONGO_URI);
  try {
    const txn = await Transaction.create({ merchantId: new mongoose.Types.ObjectId(), amount: 500, status: 'completed' });

    const refunded = await refundTransaction(txn._id);
    console.log('Refunded:', refunded.status);

    const list = await getMerchantTransactions(txn.merchantId);
    console.log('Lean transactions list:', list);
  } catch (err) {
    console.error('CRUD operation failed:', err.message);
  } finally {
    await mongoose.disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express REST API with pagination and lean reads
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

app.get('/api/transactions', async (req, res) => {
  const page = Number(req.query.page) || 1;
  const transactions = await Transaction.find({ merchantId: req.query.merchantId })
    .sort({ createdAt: -1 })
    .skip((page - 1) * 50)
    .limit(50)
    .lean();
  res.json(transactions);
});

app.patch('/api/transactions/:id/refund', async (req, res) => {
  try {
    const updated = await Transaction.findOneAndUpdate(
      { _id: req.params.id, status: 'completed' },
      { status: 'refunded' },
      { new: true }
    );
    if (!updated) return res.status(409).json({ error: 'Not refundable' });
    res.json(updated);
  } catch {
    res.status(400).json({ error: 'Invalid transaction ID' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `find-then-update` pattern instead of atomic `findOneAndUpdate` for state transitions
```javascript
// Wrong — race condition: two concurrent refund requests could both pass the check
const txn = await Transaction.findById(id);
if (txn.status === 'completed') {
  txn.status = 'refunded';
  await txn.save(); // another request could have already changed status between find and save!
}

// Right — atomic check-and-update as part of the query's filter itself
await Transaction.findOneAndUpdate({ _id: id, status: 'completed' }, { status: 'refunded' });
```

❌ Mistake 2: Using `.lean()` then trying to call instance methods on the result
✅ Correct: `.lean()` returns PLAIN JavaScript objects, not Mongoose documents — calling `doc.save()` or any custom instance method on a lean result throws `TypeError: doc.save is not a function`. Only use `.lean()` for read-only data you won't mutate via Mongoose.

---

## 🧠 Tricky Interview Question

```javascript
const result = await Transaction.updateMany({ status: 'pending' }, { status: 'cancelled' });
console.log(result);
```
Answer: The result is an object like `{ acknowledged: true, matchedCount: N, modifiedCount: M }` — NOT the updated documents themselves. `updateMany` (like the native driver) reports counts, not data. Also note: `matchedCount` (how many matched the filter) can differ from `modifiedCount` (how many actually changed) — e.g., if a document already had `status: 'cancelled'`, it's matched by a broader filter but wouldn't count as "modified" if the update made no actual change... though in this specific example all pending docs WOULD change, so matchedCount === modifiedCount here. The key interview point is distinguishing `matchedCount` vs `modifiedCount`.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between `Model.create()` and `new Model() + doc.save()`?
A1: `Model.create(data)` is a shorthand that instantiates AND saves in one call, returning the saved document (or throwing on validation failure) — convenient for simple creates. `new Model(data)` + `doc.save()` gives you a document instance you can inspect/modify BEFORE persisting (e.g., run custom logic, set computed fields) — useful when creation isn't a single atomic step.

Q2: Why does `findByIdAndUpdate` need `{ new: true }`, and what's the default without it?
A2: By default, `findByIdAndUpdate`/`findOneAndUpdate` return the document as it was BEFORE the update (the old version) — this mirrors MongoDB's native `findOneAndUpdate` default behavior. Passing `{ new: true }` tells Mongoose to return the document AFTER applying the update, which is almost always what application code actually wants.

Q3: What does `.lean()` do, and what's the trade-off?
A3: `.lean()` tells Mongoose to skip hydrating query results into full Mongoose Document instances, returning plain JavaScript objects instead. Trade-off: you lose access to instance methods, virtuals, and change-tracking (`isModified()`), but gain significant performance (less memory, faster serialization) — ideal for read-only operations like API responses or exports where you never call `.save()` on the result.

Q4: How do you perform a condition-guarded atomic update to avoid race conditions?
A4: Include the GUARD CONDITION directly in the `findOneAndUpdate`/`updateOne` filter itself, not in a separate `if` check after a `find`. E.g., `findOneAndUpdate({ _id, status: 'completed' }, { status: 'refunded' })` — MongoDB atomically checks the filter AND applies the update as one indivisible operation, so a concurrent request can't slip in between the check and the update.

Q5: What's the benefit of `bulkWrite()` over looping individual `updateOne`/`create` calls?
A5: `bulkWrite()` sends MULTIPLE different operations (mix of inserts, updates, deletes) to MongoDB in a SINGLE network round trip, which MongoDB executes far more efficiently than N separate round trips. For batch jobs updating hundreds/thousands of documents with different values each, `bulkWrite` is dramatically faster than looping individual calls.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Standard application CRUD needs with validation, hooks, and typed-ish document access
- Read-heavy list/export endpoints — pair with `.lean()` for performance
- Concurrent state-transition logic — use atomic `findOneAndUpdate` with guard conditions

❌ Avoid when:
- You need raw performance beyond what Mongoose's abstraction allows for extremely hot paths — consider the native `mongodb` driver directly for those specific queries
- Doing large bulk data migrations — consider `bulkWrite` or direct driver access over looping Mongoose calls

---

## 📊 Visual Diagram
```
MONGOOSE CRUD METHODS
──────────────────────────────────────────────
CREATE:  Model.create(data)             → validated + saved
         new Model(data); doc.save()    → manual control before save

READ:    Model.find(filter)             → array
         Model.findOne(filter)          → first match or null
         Model.findById(id)             → shorthand for findOne({_id})
         .lean()                        → plain JS objects, faster

UPDATE:  Model.updateOne/updateMany     → { matchedCount, modifiedCount }
         Model.findByIdAndUpdate(id, data, { new: true })  → returns updated doc

DELETE:  Model.deleteOne/deleteMany     → { deletedCount }
         Model.findByIdAndDelete(id)    → returns deleted doc

BULK:    Model.bulkWrite([ops])         → mixed ops, 1 round trip
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| create() | Instantiate + save in one call | Instantiate + save एक call में |
| lean() | Return plain JS objects | Plain JS objects return करना |
| findByIdAndUpdate | Atomic find-and-update by ID | ID से atomic find-and-update |
| { new: true } | Return updated doc, not old | पुराना नहीं, updated doc return |
| matchedCount | Docs matching the filter | Filter से matching docs |
| modifiedCount | Docs actually changed | Actually बदले हुए docs |
| bulkWrite | Multiple ops in one round trip | एक round trip में multiple ops |

---

## ⚡ 3-Line Summary
English:
1. Mongoose CRUD methods (`create`, `find`, `updateOne`, `deleteOne`) mirror the native driver but add validation and chainable queries.
2. Use `.lean()` for fast, read-only queries, and atomic `findOneAndUpdate` with guard conditions to avoid race conditions in state transitions.
3. `bulkWrite()` batches mixed operations into one round trip — far faster than looping individual calls for bulk data changes.

Hindi:
1. Mongoose CRUD methods (`create`, `find`, `updateOne`, `deleteOne`) native driver जैसे हैं पर validation + chainable queries के साथ।
2. Fast read-only queries के लिए `.lean()`, race conditions से बचने के लिए guard condition वाला `findOneAndUpdate` इस्तेमाल करो।
3. `bulkWrite()` mixed operations को एक round trip में batch करता है — bulk changes के लिए looping से बहुत तेज़।

---

## ➡️ Next Topic
**163. Mongoose Middleware (Hooks)** — pre/post hooks for save, validate, remove, and query operations.
