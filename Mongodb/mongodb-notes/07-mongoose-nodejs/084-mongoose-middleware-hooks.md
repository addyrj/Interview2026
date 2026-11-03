# 84. Mongoose Middleware (hooks)
# हिंदी में: Mongoose Middleware (hooks)

---

## 🔵 Simple Definition (English)
**Mongoose middleware** (also called **hooks**) are functions that run automatically **before** (`pre`) or **after** (`post`) a Mongoose operation such as `validate`, `save`, `find`, `updateOne`, `deleteOne` or `aggregate`. They let you put cross-cutting logic (hash password, generate slug, hide soft-deleted rows, write audit logs) in the schema once, instead of repeating it in every route. In Mongoose 9, hooks are plain (async) functions: you **throw** to abort and you no longer call `next()`.

## 🔵 सरल परिभाषा (Hindi)
**Mongoose middleware** (जिन्हें **hooks** भी कहते हैं) ऐसे functions हैं जो किसी Mongoose operation जैसे `validate`, `save`, `find`, `updateOne`, `deleteOne` या `aggregate` से **पहले** (`pre`) या **बाद में** (`post`) अपने आप चलते हैं। इनसे cross-cutting logic (password hash, slug बनाना, soft-deleted rows छुपाना, audit logs) एक बार schema में रखा जाता है, हर route में दोहराना नहीं पड़ता। Mongoose 9 में hooks साधारण (async) functions हैं: abort करने के लिए **throw** करो, और अब `next()` call नहीं करना पड़ता।

---

## 🔴 Problem it Solves
Rules like "always hash the password before saving", "never return soft-deleted users", "update `updatedBy` on every change" would otherwise be copy-pasted into dozens of controllers, and one forgotten place causes a security bug (plain-text password stored, deleted record exposed). Hooks attach the behaviour to the model, so it runs for every code path that uses the model.

## 🔴 यह क्यों बना? (Hindi)
"Save से पहले हमेशा password hash करो", "soft-deleted users कभी return मत करो", "हर बदलाव पर `updatedBy` update करो" जैसे नियम वरना दर्जनों controllers में copy-paste करने पड़ते, और एक जगह भूलने से security bug (plain-text password store, deleted record expose) हो जाता है। Hooks behaviour को model से जोड़ देते हैं, इसलिए model इस्तेमाल करने वाले हर code path पर यह चलता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Four hook families: **document** (`validate`, `save`, `updateOne`, `deleteOne`, `init`), **query** (`find`, `findOne`, `updateOne`, `updateMany`, `findOneAndUpdate`, `deleteOne`, `deleteMany`, `countDocuments`), **aggregate**, and **model** (`insertMany`).
Step 2 → Register with `schema.pre('save', fn)` / `schema.post('save', fn)` **before** calling `mongoose.model()`.
Step 3 → Order for `doc.save()`: `pre('validate')` -> validation -> `pre('save')` -> database write -> `post('save')`. Verified output: `validate, save`.
Step 4 → In a **document** hook `this` is the document; in a **query** hook `this` is the Query (so use `this.where()`, `this.set()`, `this.getFilter()`), and in an **aggregate** hook `this` is the Aggregate (`this.pipeline()`).
Step 5 → To abort an operation, `throw new Error(...)` (or reject the promise) inside a `pre` hook. Mongoose 9 removed callbacks / `next` from hooks.
Step 6 → Document middleware vs query middleware for `updateOne`/`deleteOne`: they exist in both forms. Use `{ document: true, query: false }` to target the document form (`doc.deleteOne()`).
Step 7 → **Not triggered by**: `Model.collection.*` raw calls, `bulkWrite` (no document hooks), and `Model.insertMany` triggers `insertMany` + per-doc `validate` but **not** `save` hooks. Verified output: `insertMany, validate`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → चार hook families: **document** (`validate`, `save`, `updateOne`, `deleteOne`, `init`), **query** (`find`, `findOne`, `updateOne`, `updateMany`, `findOneAndUpdate`, `deleteOne`, `deleteMany`, `countDocuments`), **aggregate**, और **model** (`insertMany`)।
Step 2 → `schema.pre('save', fn)` / `schema.post('save', fn)` को `mongoose.model()` call करने से **पहले** register करो।
Step 3 → `doc.save()` का क्रम: `pre('validate')` -> validation -> `pre('save')` -> database write -> `post('save')`। Verified output: `validate, save`।
Step 4 → **Document** hook में `this` document है; **query** hook में `this` Query है (इसलिए `this.where()`, `this.set()`, `this.getFilter()` इस्तेमाल करो), और **aggregate** hook में `this` Aggregate है (`this.pipeline()`)।
Step 5 → Operation रोकने के लिए `pre` hook में `throw new Error(...)` करो (या promise reject करो)। Mongoose 9 ने hooks से callbacks / `next` हटा दिया है।
Step 6 → `updateOne`/`deleteOne` के document और query दोनों रूप होते हैं। Document रूप (`doc.deleteOne()`) चाहिए तो `{ document: true, query: false }` दो।
Step 7 → **इनसे trigger नहीं होते**: `Model.collection.*` raw calls, `bulkWrite` (document hooks नहीं), और `Model.insertMany` `insertMany` + हर doc का `validate` चलाता है पर `save` hooks **नहीं**। Verified output: `insertMany, validate`।

---

## 🟡 Real World Example
In a **Flipkart**-style seller portal, the `Product` model has: `pre('save')` that generates a URL slug from the title and rounds prices; a `pre(/^find/)` hook that adds `{ isDeleted: false }` so soft-deleted products never leak into any listing; a `pre('aggregate')` hook that prepends the same `$match` to analytics pipelines; and a `post('save')` that publishes a "product updated" event to a queue for search re-indexing. Developers writing new endpoints get all of this for free.

## 🟡 Real Example Hindi mein
**Flipkart** जैसे seller portal में `Product` model में है: `pre('save')` जो title से URL slug बनाता है और price round करता है; `pre(/^find/)` hook जो `{ isDeleted: false }` जोड़ देता है ताकि soft-deleted products किसी listing में न दिखें; `pre('aggregate')` hook जो वही `$match` analytics pipelines के आगे जोड़ता है; और `post('save')` जो search re-indexing के लिए queue में "product updated" event भेजता है। नए endpoints लिखने वाले developers को यह सब मुफ्त में मिलता है।

---

## 💻 Code Example — Basic

```javascript
// hooks-basic.js — real output from Mongoose 9.11 + MongoDB 8.0.4
const mongoose = require('mongoose');

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const log = [];                                           // we record the order hooks fire in

  const schema = new mongoose.Schema({
    name: String, password: String,
    deleted: { type: Boolean, default: false }, slug: String,
  });

  // DOCUMENT hook: runs before validation
  schema.pre('validate', function () { log.push('pre validate'); });

  // DOCUMENT hook: runs before the DB write. `this` = the document. No next() in Mongoose 9.
  schema.pre('save', function () {
    log.push('pre save');
    this.slug = this.name.toLowerCase().replace(/\s+/g, '-');            // derive a slug
    if (this.isModified('password')) this.password = 'hashed:' + this.password; // only re-hash when changed
  });

  // POST hook: runs after a successful write; receives the saved doc
  schema.post('save', function (doc) { log.push('post save ' + doc.slug); });

  // ABORT by throwing: stops the save, the error rejects create()/save()
  schema.pre('save', function () { if (this.name === 'bad') throw new Error('bad name'); });

  const U = mongoose.model('Hook', schema);
  await U.deleteMany({});

  const a = await U.create({ name: 'Rahul Sharma', password: 'pw' });
  console.log(log.join(' | '));
  // Output: pre validate | pre save | post save rahul-sharma
  console.log(a.slug, a.password);
  // Output: rahul-sharma hashed:pw      (real apps use bcrypt/argon2 here)

  try { await U.create({ name: 'bad' }); } catch (e) { console.log('aborted:', e.message); }
  // Output: aborted: bad name

  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// hooks-advanced.js — query, aggregate, document-delete and the "which operations trigger which hook" table
const mongoose = require('mongoose');

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const log = [];
  const schema = new mongoose.Schema({ name: String, deleted: { type: Boolean, default: false } });

  // QUERY hook: `this` is the Query. Hide soft-deleted docs from every find()
  schema.pre('find', function () { this.where({ deleted: false }); });

  // QUERY hook on findOneAndUpdate: inject a field into every update
  schema.pre('findOneAndUpdate', function () { this.set({ updatedBy: 'system' }); });

  // QUERY form of updateOne (fires for Model.updateOne, NOT for doc.save())
  schema.pre('updateOne', function () { log.push('pre updateOne (query hook)'); });

  // DOCUMENT form of deleteOne (fires for doc.deleteOne(), not Model.deleteOne())
  schema.pre('deleteOne', { document: true, query: false }, function () { log.push('pre deleteOne (document)'); });

  // AGGREGATE hook: prepend a $match so analytics also ignore soft-deleted docs
  schema.pre('aggregate', function () { this.pipeline().unshift({ $match: { deleted: false } }); });

  const U = mongoose.model('Hook2', schema);
  await U.deleteMany({});
  const a = await U.create({ name: 'Active' });
  await U.create({ name: 'Ghost', deleted: true });

  console.log('find count (soft delete hidden):', (await U.find()).length);
  // Output: find count (soft delete hidden): 1
  console.log('agg count:', (await U.aggregate([{ $count: 'n' }]))[0].n);
  // Output: agg count: 1

  await U.updateOne({ _id: a._id }, { name: 'X' });
  console.log(log.join(' | '));            // Output: pre updateOne (query hook)
  log.length = 0;

  await a.deleteOne();
  console.log(log.join(' | '));            // Output: pre deleteOne (document)

  // WHICH OPERATION FIRES WHICH HOOK (verified with a logging schema):
  //   Model.create(doc)            -> validate, save
  //   Model.insertMany([...])      -> insertMany, validate         (NO save hook)
  //   Model.updateOne(...)         -> updateOne                    (query hook only)
  //   Model.findOneAndUpdate(...)  -> findOneAndUpdate
  //   Model.updateMany(...)        -> updateMany
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');               // npm i bcryptjs

const userSchema = new mongoose.Schema({
  email: { type: String, required: true, unique: true, lowercase: true },
  password: { type: String, required: true, select: false },   // never returned by default
  deletedAt: { type: Date, default: null },
});

// Hash only when the password field was set/changed (not on every save)
userSchema.pre('save', async function () {
  if (!this.isModified('password')) return;
  this.password = await bcrypt.hash(this.password, 10);
});

// Soft delete: every find* query skips deleted rows unless opted-out with .setOptions({ withDeleted: true })
userSchema.pre(/^find/, function () {
  if (!this.getOptions().withDeleted) this.where({ deletedAt: null });
});

// Audit trail after a successful save
userSchema.post('save', function (doc) {
  console.log(`audit: user ${doc._id} saved at ${new Date().toISOString()}`);
});

const User = mongoose.model('User', userSchema);
const app = express();
app.use(express.json());

app.post('/api/signup', async (req, res) => {
  const user = await User.create({ email: req.body.email, password: req.body.password });
  res.status(201).json({ id: user._id, email: user.email });     // password never leaves the server
});

// Soft delete endpoint: just stamps deletedAt
app.delete('/api/users/:id', async (req, res) => {
  await User.updateOne({ _id: req.params.id }, { deletedAt: new Date() });
  res.sendStatus(204);
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using an arrow function in a hook that needs `this`
```javascript
// Wrong — `this` is undefined/outer scope, not the document
schema.pre('save', () => { this.slug = 'x'; });

// Right
schema.pre('save', function () { this.slug = 'x'; });
```

❌ Mistake 2: Expecting `pre('save')` to run on updates or `insertMany`
```javascript
// Wrong assumption — none of these fire pre('save'):
await User.updateOne({ _id }, { password: 'new' });   // query hook 'updateOne' only
await User.insertMany([{ ... }]);                       // 'insertMany' + 'validate' only (verified)
// So passwords set this way are NOT hashed!

// Right — load, set, save() — or hash inside a pre('updateOne')/pre('insertMany') hook as well
const u = await User.findById(_id).select('+password'); u.password = 'new'; await u.save();
```

❌ Mistake 3: Registering hooks after compiling the model
✅ Correct: call `schema.pre(...)` before `mongoose.model('X', schema)`. Hooks added later are ignored.

---

## 🧠 Tricky Interview Question

**Q:** You added `schema.pre('find', ...)` to hide soft-deleted users. Why does `User.findOne({ _id })` and `User.findById(id)` still return deleted users?

**Answer:** `pre('find')` only fires for the `find` operation. `findOne`, `findById` (which calls `findOne`), `countDocuments`, `findOneAndUpdate` etc. have their own hook names. Register a regex hook instead, `schema.pre(/^find/, fn)`, to cover every method starting with "find", and add `countDocuments`/`aggregate` explicitly. Remember `aggregate` needs its own `pre('aggregate')` that prepends a `$match`, since aggregation pipelines bypass query middleware. We verified that `pre('aggregate')` made the count 1 instead of 2.

---

## ⚫ Interview Questions + Answers

Q1: What is the order of events on `doc.save()`?
A1: `pre('validate')` -> validators -> `post('validate')` -> `pre('save')` -> DB write -> `post('save')`. We measured the order `validate, save` for `create()`.

Q2: Document vs query middleware, what is `this`?
A2: In document middleware `this` is the document, in query middleware it is the Query object (`this.getFilter()`, `this.where()`, `this.set()`), and in aggregate middleware it is the Aggregate (`this.pipeline()`). For `updateOne`/`deleteOne` both forms exist; pick with `{ document, query }` options.

Q3: How do you abort an operation from a pre hook?
A3: Throw an error (or return a rejected promise). In Mongoose 9 there is no `next(err)`; older callback-style hooks used `next(err)`.

Q4: Does `insertMany` run `pre('save')`?
A4: No. It fires `insertMany` and `validate` per doc only (verified). `bulkWrite` fires no document middleware at all. If you rely on hashing/slug creation in `save`, use `create`/`save` or replicate the logic in `pre('insertMany')`.

Q5: Where would you put soft-delete filtering?
A5: In `pre(/^find/)` plus `pre('countDocuments')` and `pre('aggregate')` hooks, with an escape hatch option (like `withDeleted`) for admin screens. Also remember populate runs `find` internally.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Behaviour must apply to every write/read of a model (hashing, slugs, soft delete, audit)
- You need to react after persistence (events, cache invalidation) with `post` hooks

❌ Avoid when:
- Logic is business-process specific (put it in a service layer, hooks are hidden "magic")
- Heavy or slow work (network calls) inside `pre('save')`: it blocks the write path
- Bulk operations: hooks don't fire for `bulkWrite` or raw collection calls, so don't rely on them there

---

## 📊 Visual Diagram
```
HOOK TIMELINE FOR doc.save()
──────────────────────────────────────────────────────
 pre('validate') ─► validators ─► post('validate')
        │
        ▼
 pre('save')  ◄── throw here to ABORT
        │
        ▼
   ┌───────────── MongoDB write ─────────────┐
        │
        ▼
 post('save')

 WHO FIRES WHAT
 create()/save()      : validate, save
 insertMany()         : insertMany, validate (no save)
 updateOne() (Model)  : updateOne (query hook)
 find()/findOne()     : find / findOne   → use /^find/
 aggregate()          : aggregate (this.pipeline())
 bulkWrite / raw      : NO document hooks
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Middleware / hook | Function run before/after an operation | Operation से पहले/बाद चलने वाला function |
| `pre` | Runs before the operation | Operation से पहले |
| `post` | Runs after the operation | Operation के बाद |
| Query middleware | `this` is the Query | जहाँ `this` Query होता है |
| Document middleware | `this` is the document | जहाँ `this` document होता है |
| Soft delete | Mark deleted instead of removing | हटाने की जगह deleted mark करना |
| `isModified()` | Was this path changed? | क्या यह path बदला? |

---

## ⚡ 3-Line Summary
English:
1. Hooks (`pre`/`post`) attach cross-cutting logic to schema operations; in Mongoose 9 they are plain functions and you throw to abort.
2. Know the types: document (`save`), query (`find`, `updateOne`), aggregate, model (`insertMany`); `this` differs for each.
3. `save` hooks do not fire for updates, `insertMany` or `bulkWrite`; use regex hooks and explicit aggregate hooks for soft delete.

Hindi:
1. Hooks (`pre`/`post`) schema operations से cross-cutting logic जोड़ते हैं; Mongoose 9 में ये साधारण functions हैं और abort के लिए throw करना है।
2. प्रकार जानो: document (`save`), query (`find`, `updateOne`), aggregate, model (`insertMany`); हर में `this` अलग है।
3. `save` hooks updates, `insertMany` या `bulkWrite` पर नहीं चलते; soft delete के लिए regex hooks और अलग aggregate hook इस्तेमाल करो।

---

## ➡️ Next Topic
**85. Mongoose Virtuals, Methods and Statics** — computed fields and reusable model/document behaviour.
