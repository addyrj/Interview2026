# 82. Mongoose Basics — Connect + Schema + Model
# हिंदी में: Mongoose Basics — Connect + Schema + Model

---

## 🔵 Simple Definition (English)
**Mongoose** is an ODM (Object Document Mapper) for MongoDB and Node.js. You describe the shape of your data in a **Schema**, compile it into a **Model** (a class bound to one collection), and then use that model to create, query and update documents. Mongoose adds type casting, defaults, validation, middleware, populate and more on top of the native driver. (Tested here with Mongoose 9.x on MongoDB 8.0.4.)

## 🔵 सरल परिभाषा (Hindi)
**Mongoose** MongoDB और Node.js के लिए एक ODM (Object Document Mapper) है। आप data का shape एक **Schema** में बताते हैं, उसे **Model** (एक collection से जुड़ी class) में compile करते हैं और फिर उस model से documents बनाते, query और update करते हैं। Mongoose native driver के ऊपर type casting, defaults, validation, middleware, populate आदि जोड़ता है। (यहाँ Mongoose 9.x और MongoDB 8.0.4 पर test किया।)

---

## 🔴 Problem it Solves
MongoDB itself accepts any shape: `age: "twenty"` and `agee: 20` (a typo) are both stored happily. In a team codebase this means inconsistent data, typos that silently create new fields, and validation code scattered across route handlers. Mongoose centralises the contract: which fields exist, their types, which are required, their defaults, and gives each document helpful methods (`save()`, `toJSON()`), so the rules live in one place next to the model.

## 🔴 यह क्यों बना? (Hindi)
MongoDB खुद किसी भी shape को स्वीकार कर लेता है: `age: "twenty"` और `agee: 20` (typo) दोनों चुपचाप store हो जाते हैं। Team के codebase में इसका मतलब है inconsistent data, typos से अपने आप बनते नए fields और route handlers में बिखरा validation code। Mongoose contract को एक जगह रखता है: कौन-से fields हैं, उनके types, कौन-से required हैं, defaults क्या हैं, और हर document को उपयोगी methods (`save()`, `toJSON()`) देता है, ताकि नियम model के पास एक ही जगह रहें।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm install mongoose`.
Step 2 → `await mongoose.connect(uri)` opens the default connection (it wraps a `MongoClient` and pool). Check `mongoose.connection.readyState` (1 = connected). Handle `connection.on('error')` events after the initial connect.
Step 3 → `new mongoose.Schema({ ...fields }, { timestamps: true })` defines types and rules: `required`, `unique`, `lowercase`, `trim`, `enum`, `min`, `default`.
Step 4 → `mongoose.model('User', schema)` compiles the Model. The collection name is the **lowercased plural** (`User` -> `users`).
Step 5 → Use the model: `create`, `find`, `findOne`, `findById`, `updateOne`, `deleteOne`, or build `new User({...})` and call `.save()`.
Step 6 → Mongoose **casts** values to schema types (`"25"` -> `25`), applies defaults, **strips unknown fields** (strict mode) and adds `__v` (version key).
Step 7 → `unique: true` is not a validator; it builds a unique **index**. Call `Model.init()` (or wait for indexes) before relying on it in tests.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm install mongoose`।
Step 2 → `await mongoose.connect(uri)` default connection खोलता है (यह `MongoClient` और pool को wrap करता है)। `mongoose.connection.readyState` देखो (1 = connected)। पहले connect के बाद के लिए `connection.on('error')` handle करो।
Step 3 → `new mongoose.Schema({ ...fields }, { timestamps: true })` types और rules तय करता है: `required`, `unique`, `lowercase`, `trim`, `enum`, `min`, `default`।
Step 4 → `mongoose.model('User', schema)` Model compile करता है। Collection का नाम **lowercase plural** होता है (`User` -> `users`)।
Step 5 → Model इस्तेमाल करो: `create`, `find`, `findOne`, `findById`, `updateOne`, `deleteOne`, या `new User({...})` बनाकर `.save()` करो।
Step 6 → Mongoose values को schema type में **cast** करता है (`"25"` -> `25`), defaults लगाता है, **unknown fields हटा देता है** (strict mode) और `__v` (version key) जोड़ता है।
Step 7 → `unique: true` validator नहीं है; यह unique **index** बनाता है। Tests में इस पर निर्भर होने से पहले `Model.init()` call करो।

---

## 🟡 Real World Example
A **Zomato**-like user service defines a `User` model once: name (required, trimmed), email (required, unique, lowercase), phone, role (`user | admin`, default `user`). The signup endpoint calls `User.create(req.body)`. Even if a client sends `email: "AMAN@Mail.com "` or an extra `isAdmin: true` field, Mongoose lowercases and trims the email, and the unknown `isAdmin` is dropped by strict mode, so a malicious payload cannot grant admin rights. The database stays consistent no matter which service writes through the model.

## 🟡 Real Example Hindi mein
**Zomato** जैसी user service `User` model एक बार define करती है: name (required, trim), email (required, unique, lowercase), phone, role (`user | admin`, default `user`)। Signup endpoint `User.create(req.body)` call करता है। Client `email: "AMAN@Mail.com "` या extra `isAdmin: true` भेजे तब भी Mongoose email को lowercase और trim करता है और unknown `isAdmin` को strict mode हटा देता है, इसलिए malicious payload admin अधिकार नहीं दे सकता। कोई भी service model से लिखे, database consistent रहता है।

---

## 💻 Code Example — Basic

```javascript
// mongoose-basic.js   (npm install mongoose)  — output below is from a real run
const mongoose = require('mongoose');

(async () => {
  console.log('mongoose', mongoose.version);
  // Output: mongoose 9.11.4  (your minor version may differ)

  // CONNECT — database name is part of the URI; replicaSet only needed for rs deployments
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  await mongoose.connection.dropDatabase();            // demo only: start clean

  // SCHEMA — the contract for documents in the "users" collection
  const schema = new mongoose.Schema({
    name:  { type: String, required: true, trim: true },                 // trim removes outer spaces
    email: { type: String, required: true, unique: true, lowercase: true }, // unique -> creates an index
    age:   { type: Number, min: 0 },                                     // "25" will be cast to 25
    role:  { type: String, enum: ['user', 'admin'], default: 'user' },   // allowed values + default
  }, { timestamps: true });                                              // adds createdAt / updatedAt

  // MODEL — compiled class bound to the collection "users" (lowercase plural of "User")
  const User = mongoose.model('User', schema);
  await User.init();                                   // wait until the unique index is built

  // CREATE — note the dirty input: spaces, uppercase email, string age, unknown field
  const u = await User.create({ name: '  Aman ', email: 'AMAN@Mail.com', age: '25', extra: 'ignored' });
  console.log(u.name, u.email, typeof u.age, u.role, u.extra);
  // Output: Aman aman@mail.com number user undefined
  //         (trimmed, lowercased, cast to number, default role, unknown field dropped)

  console.log('collection:', User.collection.name);
  // Output: collection: users

  // READ
  const found = await User.findOne({ email: 'aman@mail.com' });
  console.log('found:', found.name, found.__v);
  // Output: found: Aman 0     (__v is the internal version key)

  // UPDATE through the document: change a field, then save() (only changed paths are sent)
  found.age = 26;
  await found.save();
  console.log('updated age:', (await User.findById(found._id)).age);
  // Output: updated age: 26

  await mongoose.disconnect();                         // closes the pool
})();
```

## 💻 Code Example — Advanced

```javascript
// mongoose-advanced.js — duplicate errors, cast errors, connection events, options
const mongoose = require('mongoose');

// Connection options worth knowing in production
const opts = {
  maxPoolSize: 20,                 // concurrent sockets (driver option)
  serverSelectionTimeoutMS: 5000,  // fail in 5s instead of hanging if no server is reachable
  autoIndex: process.env.NODE_ENV !== 'production', // do not auto-build indexes on every prod boot
};

// Events AFTER the initial connect (initial failures reject the connect() promise)
mongoose.connection.on('connected', () => console.log('mongo connected'));
mongoose.connection.on('disconnected', () => console.warn('mongo disconnected'));
mongoose.connection.on('error', (err) => console.error('mongo error', err.message));

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0', opts);
  const User = mongoose.model('User');                 // model compiled in the Basic example (same process in your app)

  // 1) DUPLICATE KEY (unique index) -> MongoServerError with code 11000
  try {
    await User.create({ name: 'Dup', email: 'aman@mail.com' });
  } catch (e) {
    console.log('dup code', e.code);
    // Output: dup code 11000
  }

  // 2) CAST ERROR: "xyz" cannot become an ObjectId
  try {
    await User.findById('xyz');
  } catch (e) {
    console.log(e.name, e.kind);
    // Output: CastError ObjectId
  }

  // 3) readyState: 0 disconnected, 1 connected, 2 connecting, 3 disconnecting
  console.log('readyState', mongoose.connection.readyState);
  // Output: readyState 1

  // 4) Mongoose 9: findOneAndUpdate returns the NEW doc via returnDocument (the `new` option is deprecated)
  const updated = await User.findOneAndUpdate(
    { email: 'aman@mail.com' }, { $set: { role: 'admin' } }, { returnDocument: 'after' });
  console.log(updated.role);   // admin

  // 5) lean() skips hydration -> plain object, faster for read-only responses
  const plain = await User.findOne({ email: 'aman@mail.com' }).lean();
  console.log(typeof plain.save);  // undefined (plain object has no document methods)

  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// app.js — typical structure: connect first, then listen
const express = require('express');
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  name:  { type: String, required: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true },
  role:  { type: String, enum: ['user', 'admin'], default: 'user' },
}, { timestamps: true });
const User = mongoose.model('User', userSchema);

const app = express();
app.use(express.json());

app.post('/api/users', async (req, res) => {
  try {
    // Pick allowed fields explicitly — never pass req.body straight in for sensitive fields like role
    const { name, email } = req.body;
    const user = await User.create({ name, email });
    res.status(201).json(user);
  } catch (err) {
    if (err.code === 11000) return res.status(409).json({ error: 'Email already registered' });
    if (err.name === 'ValidationError') return res.status(400).json({ error: err.message });
    res.status(500).json({ error: 'Server error' });
  }
});

app.get('/api/users/:id', async (req, res) => {
  if (!mongoose.isValidObjectId(req.params.id)) return res.status(400).json({ error: 'Bad id' });
  const user = await User.findById(req.params.id).lean();
  user ? res.json(user) : res.status(404).json({ error: 'Not found' });
});

mongoose.connect(process.env.MONGO_URI)
  .then(() => app.listen(3000, () => console.log('Listening')))
  .catch((e) => { console.error('DB connect failed', e.message); process.exit(1); });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Treating `unique: true` as validation
```javascript
// Wrong — expecting a ValidationError. unique only builds an index; the error comes from the DB
// as MongoServerError code 11000, and only after the index finished building.
const e = await User.create(dup).catch(x => x);
e.name;  // 'MongoServerError', not 'ValidationError'

// Right — catch code 11000 and map it to HTTP 409
```

❌ Mistake 2: Starting the server before the DB is connected
```javascript
// Wrong — requests arrive while Mongoose buffers commands, then time out after 10s
app.listen(3000); mongoose.connect(uri);

// Right — listen after connect resolves (see Express section)
```

❌ Mistake 3: Passing `req.body` straight to `create`/`updateOne`
✅ Correct: whitelist fields. Strict mode only drops fields not in the schema; if `role` IS in the schema, a client can set `role: 'admin'` unless you pick the allowed fields yourself.

---

## 🧠 Tricky Interview Question

**Q:** You define `mongoose.model('Person', schema)`. In MongoDB Compass you cannot find a collection called `Person`. Why, and how do you control the name?

**Answer:** Mongoose **pluralizes and lowercases** the model name: `Person` -> `people` (it uses an inflection library, so irregular words are handled), `User` -> `users`. Our test printed `collection: users`. To control the name either pass it as the third argument, `mongoose.model('Person', schema, 'persons')`, or set `new Schema({...}, { collection: 'persons' })`. Beware that in dev a typo in the model name quietly creates a brand-new empty collection instead of an error.

---

## ⚫ Interview Questions + Answers

Q1: What are Schema, Model and Document in Mongoose?
A1: A **Schema** declares fields, types, validators, indexes and hooks. A **Model** is the compiled class tied to a collection, used for queries (`User.find`). A **Document** is an instance of a Model representing one record, with methods like `save()` and `toObject()`.

Q2: What is strict mode?
A2: By default (`strict: true`) fields not in the schema are silently dropped on save/update (our `extra` field vanished). `strict: 'throw'` raises an error instead; `strict: false` stores them.

Q3: What does `timestamps: true` do?
A3: Adds `createdAt` and `updatedAt` Date fields and keeps `updatedAt` current on saves and update operations.

Q4: What is `__v`?
A4: The version key, used by Mongoose for optimistic concurrency on array modifications. You can disable with `versionKey: false` (e.g., for time-series collections).

Q5: Why does Mongoose buffer commands and what are the risks?
A5: Before the connection is ready Mongoose queues operations so you can define models and call methods early. If the connection never succeeds, the queued operations time out (about 10 seconds) with a buffering timeout error. Connect first or handle the failure explicitly.

---

## 🔷 When to Use + When Not to Use
✅ Use Mongoose when:
- You want schema-level contracts, casting, defaults and validation in code
- Your team wants hooks, virtuals, populate and model methods
- Building typical CRUD APIs with Express/NestJS

❌ Avoid / reconsider when:
- Maximum raw throughput ETL/ingestion (use the native driver, topic 81)
- Highly dynamic, schema-less documents where a schema fights you (`strict: false` or use the driver)
- You need a feature the ODM has not exposed yet (use `Model.collection` or `connection.db` for the raw driver)

---

## 📊 Visual Diagram
```
MONGOOSE LAYERS
──────────────────────────────────────────────────────
 Your code:  User.create({...})   user.save()   User.find({...})
                    │
                    ▼
 ┌──────────── Mongoose ────────────┐
 │ Schema  → types, required, enum   │   casting ("25" → 25)
 │ Model   → "User" ↔ collection     │   defaults, trim, lowercase
 │ Hooks / Validators / Populate     │   strict: drops unknown keys
 └──────────────┬───────────────────┘
                ▼
 Native mongodb driver (MongoClient + connection pool)
                ▼
 mongod  →  collection "users"  { _id, name, email, age, role, createdAt, updatedAt, __v }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| ODM | Maps objects to documents | Objects को documents से map करना |
| Schema | Declares fields and rules | Fields और rules की घोषणा |
| Model | Class bound to a collection | Collection से जुड़ी class |
| Document | One instance of a model | Model का एक instance |
| Casting | Auto type conversion | Type का अपने आप बदलना |
| Strict mode | Drops unknown fields | Unknown fields हटाना |
| `__v` | Internal version key | Internal version key |

---

## ⚡ 3-Line Summary
English:
1. `mongoose.connect()` opens the pool; a Schema defines the contract; `mongoose.model()` gives you a Model bound to a lowercase plural collection.
2. Mongoose casts, trims, applies defaults and drops unknown fields; `unique` is an index, not a validator.
3. Connect before listening, whitelist input fields and handle `ValidationError`, `CastError` and error code 11000.

Hindi:
1. `mongoose.connect()` pool खोलता है; Schema contract बनाता है; `mongoose.model()` lowercase plural collection से जुड़ा Model देता है।
2. Mongoose cast करता है, trim करता है, defaults लगाता है और unknown fields हटाता है; `unique` index है, validator नहीं।
3. Listen करने से पहले connect करो, input fields whitelist करो और `ValidationError`, `CastError` व error code 11000 को handle करो।

---

## ➡️ Next Topic
**83. Mongoose Validation and Custom Validators** — built-in validators, custom sync/async validators and update validators.
