# 163. Mongoose Middleware (Hooks)
# हिंदी में: Mongoose Middleware (Hooks) — Lifecycle Events

---

## 🔵 Simple Definition (English)
**Mongoose Middleware** (also called hooks) are functions that run automatically before (`pre`) or after (`post`) certain operations — `save`, `validate`, `remove`, `deleteOne`, and query methods like `findOneAndUpdate`. They're attached to the SCHEMA (not the model), and let you run code like password hashing, slug generation, or cascading cleanup without repeating it in every controller.

## 🔵 सरल परिभाषा (Hindi)
**Mongoose Middleware** (hooks) वो functions हैं जो operations से पहले (`pre`) या बाद (`post`) automatically चलते हैं — `save`, `validate`, `remove`, `deleteOne`, और query methods जैसे `findOneAndUpdate`। ये SCHEMA पर attach होते हैं (model पर नहीं), और password hashing, slug generation, cascading cleanup जैसा code हर controller में बार-बार लिखने से बचाते हैं।

---

## 🔴 Problem it Solves
Without middleware, any cross-cutting logic that should ALWAYS happen around a document operation (hashing a password before every save, deleting a user's related posts when the user is deleted, logging every update) must be manually called at every call site — easy to forget in one place. Mongoose middleware attaches this logic to the SCHEMA itself, so it runs automatically no matter where in the codebase the triggering operation is called from.

## 🔴 यह क्यों बना? (Hindi)
Middleware के बिना, हर document operation के आस-पास चलने वाला cross-cutting logic (password hash करना, user delete होने पर उसके posts delete करना, हर update log करना) हर call site पर manually call करना पड़ता — कहीं भूलना आसान। Mongoose middleware इस logic को SCHEMA पर attach करता है, जो automatically चलता है चाहे operation कहीं से भी triggered हो।

---

## 🟢 How it Works — Step by Step

Step 1 → Document middleware: `schema.pre('save', function(next) {...})` — `this` refers to the document being saved; call `next()` to continue, or pass an error to `next(err)` to abort.
Step 2 → Query middleware: `schema.pre('findOneAndUpdate', function(next) {...})` — `this` refers to the Query object, not a document; used for `update`/`find`/`delete` family methods.
Step 3 → Aggregate middleware: `schema.pre('aggregate', function(next) {...})` — modifies the aggregation pipeline before it runs.
Step 4 → `post` hooks run AFTER the operation succeeds — useful for logging, notifications, or triggering dependent writes.
Step 5 → Async hooks either accept a `next` callback OR return a Promise (modern style) — Mongoose supports both; mixing styles in the same hook causes bugs.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Document middleware: `schema.pre('save', function(next) {...})` — `this` document है; `next()` से continue, `next(err)` से abort।
Step 2 → Query middleware: `schema.pre('findOneAndUpdate', function(next) {...})` — `this` Query object है, document नहीं।
Step 3 → Aggregate middleware: `schema.pre('aggregate', ...)` — pipeline चलने से पहले modify करता है।
Step 4 → `post` hooks operation सफल होने के बाद चलते हैं — logging, notifications के लिए।
Step 5 → Async hooks `next` callback या Promise return कर सकते — दोनों styles mix करने से bugs आते हैं।

---

## 🟡 Real World Example
**Swiggy's user-authentication service** uses a `pre('save')` hook on the `User` schema to hash passwords: `userSchema.pre('save', async function(next) { if (this.isModified('password')) { this.password = await bcrypt.hash(this.password, 10); } next(); })`. It also uses a `pre('findOneAndDelete')` hook (query middleware) that cascades: when a `Restaurant` document is deleted, it automatically deletes all its `MenuItem` documents, preventing orphaned records across the app without needing every delete call site to remember this cleanup.

## 🟡 Real Example Hindi mein
**Swiggy की user-authentication service** `pre('save')` hook से password hash करती है। साथ ही `pre('findOneAndDelete')` query middleware से — जब `Restaurant` delete होता है, उसके सारे `MenuItem` documents automatically delete हो जाते हैं, orphaned records से बचाव, बिना हर delete call site में याद रखे।

---

## 💻 Code Example — Basic

```javascript
// mongoose-hooks-basic.js
// npm install mongoose bcrypt
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
  email: { type: String, unique: true, required: true },
  password: { type: String, required: true },
});

// DOCUMENT middleware — 'this' is the document being saved
userSchema.pre('save', async function (next) {
  // only hash if password field is new or changed — avoid re-hashing an already-hashed value
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 10);
  next(); // MUST call next() to continue, or the save hangs forever
});

// POST hook — runs after successful save, useful for logging
userSchema.post('save', function (doc) {
  console.log(`User saved with id: ${doc._id}`);
});

const User = mongoose.model('User', userSchema);

async function main() {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/hooks_demo');

  const user = await User.create({ email: 'kavya@example.com', password: 'plainPassword123' });
  console.log('Stored hash (not plaintext):', user.password);

  const isMatch = await bcrypt.compare('plainPassword123', user.password);
  console.log('Password verified:', isMatch);

  await mongoose.disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// mongoose-hooks-advanced.js — query middleware for cascading deletes + error handling
const mongoose = require('mongoose');

const restaurantSchema = new mongoose.Schema({ name: String });
const menuItemSchema = new mongoose.Schema({ name: String, restaurantId: mongoose.Schema.Types.ObjectId });

const MenuItem = mongoose.model('MenuItem', menuItemSchema);

// QUERY middleware — 'this' is the Query, not a document; runs before findOneAndDelete executes
restaurantSchema.pre('findOneAndDelete', async function (next) {
  try {
    // this.getFilter() gives access to the query's filter conditions
    const restaurant = await this.model.findOne(this.getFilter());
    if (restaurant) {
      // cascading cleanup: delete all menu items belonging to this restaurant
      await MenuItem.deleteMany({ restaurantId: restaurant._id });
      console.log(`Cascaded delete: removed menu items for restaurant ${restaurant._id}`);
    }
    next();
  } catch (err) {
    next(err); // pass error to next() to abort the operation
  }
});

// VALIDATION hook that can ABORT the save by throwing/passing an error
restaurantSchema.pre('save', function (next) {
  if (this.name && this.name.trim().length < 3) {
    return next(new Error('Restaurant name must be at least 3 characters'));
  }
  next();
});

const Restaurant = mongoose.model('Restaurant', restaurantSchema);

async function run() {
  await mongoose.connect(process.env.MONGO_URI);

  try {
    const restaurant = await Restaurant.create({ name: 'Spice Villa' });
    await MenuItem.create({ name: 'Butter Chicken', restaurantId: restaurant._id });
    await MenuItem.create({ name: 'Naan', restaurantId: restaurant._id });

    console.log('Menu items before delete:', await MenuItem.countDocuments({ restaurantId: restaurant._id })); // 2

    // Deleting the restaurant triggers the pre('findOneAndDelete') cascading hook
    await Restaurant.findOneAndDelete({ _id: restaurant._id });

    console.log('Menu items after cascading delete:', await MenuItem.countDocuments({ restaurantId: restaurant._id })); // 0

    // Trying to save an invalid restaurant — blocked by the pre('save') hook
    await Restaurant.create({ name: 'A' }); // throws: name too short
  } catch (err) {
    console.error('Operation blocked:', err.message);
  } finally {
    await mongoose.disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express registration route — hook handles hashing transparently
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

app.post('/api/register', async (req, res) => {
  try {
    // pre('save') hook hashes the password automatically — controller never touches bcrypt directly
    const user = await User.create({ email: req.body.email, password: req.body.password });
    res.status(201).json({ id: user._id, email: user.email }); // password field never returned
  } catch (err) {
    if (err.code === 11000) return res.status(409).json({ error: 'Email already registered' });
    res.status(400).json({ error: err.message });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting to call `next()` in a callback-style hook
```javascript
// Wrong — hangs forever, the save() Promise never resolves
schema.pre('save', function (next) {
  this.updatedAt = Date.now();
  // next() is never called!
});

// Right — always call next() to signal completion
schema.pre('save', function (next) {
  this.updatedAt = Date.now();
  next();
});
```

❌ Mistake 2: Expecting `pre('save')` hooks to run on query-based operations like `updateOne`
✅ Correct: `pre('save')` only fires on `.save()`/`Model.create()` — it does NOT run for `Model.updateOne()`, `findOneAndUpdate()`, etc. Those need SEPARATE query middleware (`pre('findOneAndUpdate', ...)`) if you need similar logic there.

---

## 🧠 Tricky Interview Question

```javascript
userSchema.pre('save', function (next) {
  console.log('Hook A');
  next();
});
userSchema.pre('save', function (next) {
  console.log('Hook B');
  next();
});
await User.create({ email: 'x@x.com', password: 'pwd' });
```
Answer: Output is `"Hook A"` then `"Hook B"` — Mongoose runs multiple `pre` hooks of the SAME TYPE in the ORDER they were registered (FIFO), and each must call `next()` before the next hook in the chain runs. If any hook calls `next(err)` instead, the chain stops immediately and the save is aborted with that error — subsequent hooks (including the actual save) never execute.

---

## ⚫ Interview Questions + Answers

Q1: What's the difference between document middleware and query middleware in Mongoose?
A1: Document middleware (`pre('save')`, `pre('validate')`, `pre('remove')`) runs when calling methods DIRECTLY on a document instance (`doc.save()`) — inside, `this` refers to the document. Query middleware (`pre('find')`, `pre('findOneAndUpdate')`, `pre('updateMany')`) runs for Model-level QUERY methods — inside, `this` refers to the Query object, which has methods like `getFilter()`/`getUpdate()` instead of document fields directly.

Q2: How do you abort an operation from within a hook?
A2: In callback style, call `next(someError)` instead of `next()` — Mongoose stops the chain and rejects the triggering Promise with that error. In Promise/async style, simply `throw` an error (or return a rejected Promise) — Mongoose propagates it the same way. Either approach prevents the underlying save/update/delete from executing.

Q3: Why doesn't `pre('save')` fire when you call `Model.updateOne()`?
A3: `updateOne`/`updateMany`/`findOneAndUpdate` are QUERY-based operations that send an update command directly to MongoDB without loading a full Mongoose document — they never call `.save()` internally, so document middleware tied to `save` simply never triggers. If you need hook-like behavior for these, you must register separate QUERY middleware for the specific method name (e.g., `pre('updateOne', ...)`).

Q4: What's a practical use case for `post` hooks?
A4: Side effects that should happen only AFTER an operation definitively succeeds — e.g., sending a welcome email after a user is created (`post('save')`), logging an audit entry after an update, invalidating a cache entry after a delete, or triggering a downstream event/message queue publish. Since `post` hooks run after success, they won't fire if the main operation (or an earlier `pre` hook) failed.

Q5: What happens if you mix callback-style (`next`) and Promise-style (`async`) incorrectly in the same hook?
A5: If an `async` function also accepts and calls a `next` callback AND returns a Promise, Mongoose can get confused about when the hook is "done," potentially causing the next hook/operation to run before intended side effects finish, or double-execution in edge cases. Best practice: pick ONE style per hook — either declare `async function(next)` and ONLY call `next()`, never `return`ing a value, or declare `async function()` with no `next` param and just `await`/`throw` — don't combine both signaling mechanisms.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Logic must ALWAYS run around a specific operation regardless of caller (password hashing, cascading deletes, audit logging)
- You want centralized validation/business rules tied to the data model itself

❌ Avoid when:
- The logic is specific to ONE particular API endpoint's business flow, not a model-wide invariant — keep that in the controller/service layer
- Overusing hooks creates hidden "magic" that makes tracing bugs harder across a large codebase — document middleware behavior clearly for your team

---

## 📊 Visual Diagram
```
MONGOOSE HOOK LIFECYCLE (document middleware, for .save())
──────────────────────────────────────────────
  doc.save() called
        │
        ▼
  pre('validate')  →  schema validation runs
        │
        ▼
  pre('save')      →  (can call next(err) to abort)
        │
        ▼
     actual INSERT/UPDATE in MongoDB
        │
        ▼
  post('save')     →  side effects (logging, notifications)
        │
        ▼
     resolved Promise returned to caller

QUERY MIDDLEWARE (separate pipeline, for find/update/delete methods):
  Model.findOneAndDelete(filter)
        │
        ▼
  pre('findOneAndDelete')  →  this = Query object, this.getFilter()
        │
        ▼
     actual DELETE command
        │
        ▼
  post('findOneAndDelete')
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| pre hook | Runs before the operation | Operation से पहले चलता है |
| post hook | Runs after the operation | Operation के बाद चलता है |
| document middleware | Hooks on doc.save()/remove() | doc.save()/remove() पर hooks |
| query middleware | Hooks on query methods | Query methods पर hooks |
| next() | Signals hook completion | Hook पूरा होने का signal |
| isModified() | Checks if field changed | Field बदला या नहीं check |
| cascading delete | Auto-deleting related data | Related data auto-delete |

---

## ⚡ 3-Line Summary
English:
1. Mongoose middleware (`pre`/`post` hooks) attaches lifecycle logic to the schema, running automatically around save, validate, remove, and query operations.
2. Document middleware (`this` = document) only fires for `.save()`/`create()`; query middleware is needed separately for `updateOne`/`findOneAndUpdate`/etc.
3. Always call `next()` (or properly resolve/throw in async style) — forgetting it hangs the operation forever.

Hindi:
1. Mongoose middleware (`pre`/`post` hooks) schema पर lifecycle logic attach करता है, save, validate, remove, query operations के आस-पास automatically चलता है।
2. Document middleware सिर्फ `.save()`/`create()` पर चलता है; query operations के लिए अलग query middleware चाहिए।
3. हमेशा `next()` call करो (या async style में properly resolve/throw करो) — भूलने से operation हमेशा के लिए hang हो जाता है।

---

## ➡️ Next Topic
**164. Mongoose Population (Joins)** — Resolving referenced documents with `populate()`, nested population, and performance trade-offs.
