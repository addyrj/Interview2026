# 160. Mongoose — Complete Guide
# हिंदी में: Mongoose — पूरी गाइड

---

## 🔵 Simple Definition (English)
**Mongoose** is an ODM (Object-Document Mapper) for MongoDB and Node.js. It sits on top of the native `mongodb` driver and adds: **Schemas** (defining document structure and validation rules), **Models** (classes compiled from schemas, used for CRUD), **Middleware/hooks**, **Population** (joining referenced documents), and built-in **validation** and **type casting** — things the raw MongoDB driver doesn't provide.

## 🔵 सरल परिभाषा (Hindi)
**Mongoose** MongoDB और Node.js के लिए एक ODM (Object-Document Mapper) है। ये native `mongodb` driver के ऊपर बैठता है और add करता है: **Schemas** (document structure + validation rules), **Models** (schemas से बने classes, CRUD के लिए), **Middleware/hooks**, **Population** (referenced documents को join करना), और built-in **validation** और **type casting** — जो raw MongoDB driver नहीं देता।

---

## 🔴 Problem it Solves
The native MongoDB driver is schema-less by design — it accepts ANY document shape, which means no automatic validation (a typo'd field name or wrong type silently gets saved), no easy way to reference related documents (manual `$lookup` aggregation needed), and no lifecycle hooks for common logic like password hashing. Mongoose adds a structured layer on top: schemas enforce shape and types at the application level, `populate()` makes referencing documents feel like SQL JOINs, and middleware (hooks) centralize cross-cutting logic.

## 🔴 यह क्यों बना? (Hindi)
Native MongoDB driver by design schema-less है — कोई भी document shape accept करता है, मतलब automatic validation नहीं (typo वाला field name silently save हो जाता), related documents reference करने का आसान तरीका नहीं (manual `$lookup` चाहिए), और common logic (password hashing) के लिए lifecycle hooks नहीं। Mongoose structured layer add करता है: schemas shape+types enforce करते, `populate()` SQL JOINs जैसा feel देता, middleware cross-cutting logic centralize करता।

---

## 🟢 How it Works — Step by Step

Step 1 → Install: `npm install mongoose`, connect with `mongoose.connect(uri)`.
Step 2 → Define a `Schema` describing fields, types, validation rules, and defaults.
Step 3 → Compile the schema into a `Model`: `mongoose.model('User', userSchema)` — this is your interface for CRUD.
Step 4 → Use the Model's static methods (`User.find()`, `User.create()`) or instance methods (`user.save()`) to interact with the DB.
Step 5 → Add middleware (`schema.pre('save', fn)`), virtuals, and `populate()` for references — all layered on top of the schema.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Install करो: `npm install mongoose`, `mongoose.connect(uri)` से connect करो।
Step 2 → `Schema` define करो — fields, types, validation rules, defaults।
Step 3 → Schema को `Model` में compile करो: `mongoose.model('User', userSchema)`।
Step 4 → Model के static methods (`User.find()`, `User.create()`) या instance methods (`user.save()`) से CRUD करो।
Step 5 → Middleware (`schema.pre('save', fn)`), virtuals, और references के लिए `populate()` add करो।

---

## 🟡 Real World Example
**Swiggy's user-profile service** uses Mongoose schemas to enforce that every `User` document has a valid email format, a required `phone` field matching a regex, and a `password` that gets auto-hashed via a `pre('save')` hook. Without Mongoose's schema validation, a buggy API endpoint could save a user with a malformed phone number directly to MongoDB — Mongoose catches this at the application layer BEFORE it ever reaches the database.

## 🟡 Real Example Hindi mein
**Swiggy की user-profile service** Mongoose schemas इस्तेमाल करती है ताकि हर `User` document में valid email format, required `phone` field (regex से match), और `password` हो जो `pre('save')` hook से auto-hash हो जाए। Mongoose की schema validation के बिना, एक buggy API endpoint malformed phone number directly MongoDB में save कर सकता था।

---

## 💻 Code Example — Basic

```javascript
// mongoose-basic.js
// npm install mongoose
const mongoose = require('mongoose');

async function main() {
  await mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/swiggy_demo');

  // Define schema: structure, types, validation
  const userSchema = new mongoose.Schema({
    name: { type: String, required: true, trim: true },
    email: { type: String, required: true, unique: true, lowercase: true },
    age: { type: Number, min: 18, max: 100 },
    createdAt: { type: Date, default: Date.now },
  });

  // Compile schema into a Model
  const User = mongoose.model('User', userSchema);

  // CREATE — validation runs automatically before saving
  const user = await User.create({ name: 'Rohit', email: 'ROHIT@Example.com', age: 25 });
  console.log('Created (email auto-lowercased):', user.email); // "rohit@example.com"

  // READ
  const found = await User.findOne({ email: 'rohit@example.com' });
  console.log('Found:', found.name);

  // UPDATE
  await User.updateOne({ email: 'rohit@example.com' }, { age: 26 });

  // Validation failure example
  try {
    await User.create({ name: 'Bad', email: 'bad@example.com', age: 10 }); // age < min(18)
  } catch (err) {
    console.log('Validation error:', err.message); // "Path `age` (10) is less than minimum allowed value (18)."
  }

  await mongoose.disconnect();
}

main();
```

## 💻 Code Example — Advanced

```javascript
// mongoose-advanced.js — Production patterns: hooks, virtuals, statics, methods, population
const mongoose = require('mongoose');

const orderSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }, // reference
  items: [{ productId: mongoose.Schema.Types.ObjectId, quantity: Number, price: Number }],
  status: { type: String, enum: ['pending', 'confirmed', 'delivered'], default: 'pending' },
}, { timestamps: true }); // adds createdAt/updatedAt automatically

// VIRTUAL — a computed field not stored in the DB
orderSchema.virtual('totalAmount').get(function () {
  return this.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
});

// INSTANCE METHOD — callable on a document instance
orderSchema.methods.markDelivered = async function () {
  this.status = 'delivered';
  return this.save();
};

// STATIC METHOD — callable on the Model itself
orderSchema.statics.findPendingForUser = function (userId) {
  return this.find({ userId, status: 'pending' });
};

// MIDDLEWARE (hook) — runs before every save
orderSchema.pre('save', function (next) {
  if (this.items.length === 0) {
    return next(new Error('Order must have at least one item')); // blocks save
  }
  next();
});

const Order = mongoose.model('Order', orderSchema);

async function run() {
  await mongoose.connect(process.env.MONGO_URI);

  try {
    const order = new Order({
      userId: new mongoose.Types.ObjectId(),
      items: [{ productId: new mongoose.Types.ObjectId(), quantity: 2, price: 150 }],
    });

    await order.save(); // pre('save') hook runs, validates items.length
    console.log('Total amount (virtual):', order.totalAmount); // 300, computed, not stored

    await order.markDelivered(); // instance method
    console.log('Status after delivery:', order.status);

    // POPULATE — fetch the referenced User document in place of the raw ObjectId
    const populated = await Order.findById(order._id).populate('userId', 'name email');
    console.log('Populated user field:', populated.userId);
  } catch (err) {
    console.error('Order save failed:', err.message);
  } finally {
    await mongoose.disconnect();
  }
}

run();
```

---

## 🟠 Express.js Integration

```javascript
// Express app using Mongoose models directly in route handlers
const express = require('express');
const mongoose = require('mongoose');
const app = express();
app.use(express.json());

mongoose.connect(process.env.MONGO_URI).then(() => console.log('Mongoose connected'));

const User = mongoose.model('User', new mongoose.Schema({
  name: String, email: { type: String, unique: true },
}));

app.post('/api/users', async (req, res) => {
  try {
    const user = await User.create(req.body); // schema validation runs automatically
    res.status(201).json(user);
  } catch (err) {
    if (err.name === 'ValidationError') return res.status(400).json({ error: err.message });
    if (err.code === 11000) return res.status(409).json({ error: 'Email already exists' });
    res.status(500).json({ error: 'Server error' });
  }
});

app.listen(3000);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Calling `.save()` after already using `updateOne`/`findOneAndUpdate` elsewhere, causing a version conflict
✅ Correct: Mongoose documents have a `__v` version key; mixing manual `updateOne` calls with later `.save()` on a stale in-memory document can throw `VersionError`. Prefer consistently using either query-based updates OR document-based `.save()` for a given workflow.

❌ Mistake 2: Forgetting `await mongoose.connect()` completes before queries run
```javascript
// Wrong — fires queries before the connection is established
mongoose.connect(uri);
User.find(); // may fail silently or queue indefinitely depending on bufferCommands setting

// Right — await the connection first
await mongoose.connect(uri);
const users = await User.find();
```

---

## 🧠 Tricky Interview Question

```javascript
const schema = new mongoose.Schema({ name: String });
const Model1 = mongoose.model('Item', schema);
const Model2 = mongoose.model('Item', schema); // called again with the same name!
```
Answer: This throws `OverwriteModelError: Cannot overwrite 'Item' model once compiled.` Mongoose keeps an internal registry of compiled models by name — calling `mongoose.model('Item', schema)` a SECOND time with the same name throws, because the model is already compiled. This commonly happens in tests or hot-reloading dev environments; the fix is to check `mongoose.models.Item || mongoose.model('Item', schema)` before compiling, or structure model files to only compile once per process.

---

## ⚫ Interview Questions + Answers

Q1: What is the relationship between a Mongoose Schema and a Model?
A1: A `Schema` is a BLUEPRINT describing field names, types, validation, and defaults — it's not directly usable for DB operations. A `Model` is created by COMPILING a schema with `mongoose.model(name, schema)` — it's the actual class/constructor you use to create documents, run queries (`find`, `updateOne`), and that enforces the schema's rules at runtime.

Q2: What's the difference between document middleware and query middleware in Mongoose?
A2: Document middleware (`schema.pre('save', fn)`) runs on `.save()`/`.remove()` calls on a DOCUMENT instance (`this` is the document). Query middleware (`schema.pre('findOneAndUpdate', fn)`) runs on QUERY methods like `updateOne`, `findOneAndUpdate`, `find` (`this` is the Query object, not a document) — these don't trigger document hooks like `pre('save')`, which is why hooks must sometimes be duplicated or `runValidators: true` set explicitly for query-based updates to validate data.

Q3: What does `populate()` do, and how is it different from a SQL JOIN?
A3: `populate()` replaces a referenced `ObjectId` field (declared with `ref: 'ModelName'`) with the actual referenced document, by running a SEPARATE query behind the scenes and merging results in the application layer — unlike SQL's JOIN, which happens in a single query at the database engine level. This means `populate()` is effectively 2+ round trips to MongoDB, which is fine for most use cases but can be less efficient than embedding data directly for very hot-path queries.

Q4: What are virtuals, and when would you use one?
A4: Virtuals are computed properties defined on a schema that are NOT persisted to the database — e.g., a `fullName` virtual combining `firstName` + `lastName`, or a `totalAmount` virtual computed from an `items` array. They behave like regular properties when accessed (`doc.totalAmount`) but require no extra storage and stay automatically in sync with the underlying stored fields.

Q5: How do you enforce schema validation on bulk update operations like `updateMany`?
A5: By default, Mongoose query-based updates (`updateOne`, `updateMany`, `findOneAndUpdate`) do NOT run schema validators unless you explicitly pass `{ runValidators: true }` in the options. Without it, invalid data can bypass validation when updating via queries (as opposed to loading a document and calling `.save()`, which always validates).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want schema-level structure, validation, and type casting on top of MongoDB's flexibility
- You need lifecycle hooks (password hashing, audit logging) and virtuals/computed fields
- Working with related/referenced documents and want `populate()` convenience

❌ Avoid when:
- You need absolute maximum raw performance and want to skip the validation/casting overhead Mongoose adds (use the native `mongodb` driver directly)
- Your data model is so dynamic that even defining a loose schema feels unnecessarily restrictive (though Mongoose supports `Mixed`/schemaless fields when truly needed)

---

## 📊 Visual Diagram
```
MONGOOSE ARCHITECTURE
──────────────────────────────────────────────
  mongoose.connect(uri)
       │
       ▼
  Schema (blueprint: fields, types, validation, defaults)
       │
       ▼
  mongoose.model('User', schema) ──▶ Model (compiled, usable class)
       │
       ├── Model.find() / create() / updateOne()   (static methods)
       ├── doc.save() / doc.markDelivered()          (instance methods)
       ├── schema.pre('save', fn)                      (hooks)
       ├── schema.virtual('x').get(fn)                 (computed fields)
       └── Model.find().populate('ref')                (joins via 2nd query)
       │
       ▼
  Native `mongodb` driver underneath
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Schema | Blueprint of document structure | Document structure का blueprint |
| Model | Compiled, usable class from schema | Schema से बना usable class |
| Hook/Middleware | Lifecycle callback | Lifecycle callback |
| Virtual | Computed, non-persisted field | Computed, non-persisted field |
| populate() | Resolve referenced documents | Referenced documents resolve करना |
| runValidators | Enables validation on query updates | Query updates पर validation enable करना |
| ref | Points to another model for population | दूसरे model की तरफ pointer |

---

## ⚡ 3-Line Summary
English:
1. Mongoose is an ODM adding schemas, validation, hooks, and `populate()` on top of MongoDB's native flexibility.
2. Schemas compile into Models — the actual interface for CRUD, validation, and instance/static methods.
3. Query-based updates (`updateMany`) skip document middleware/validation by default — pass `runValidators: true` explicitly if needed.

Hindi:
1. Mongoose एक ODM है जो MongoDB की native flexibility के ऊपर schemas, validation, hooks, `populate()` add करता है।
2. Schemas Models में compile होते हैं — CRUD, validation, instance/static methods का actual interface।
3. Query-based updates (`updateMany`) default में document middleware/validation skip करते — ज़रूरत हो तो `runValidators: true` pass करो।

---

## ➡️ Next Topic
**161. Mongoose Schema + Model** — Deep dive into field types, validators, defaults, and the schema-to-model compilation process.
