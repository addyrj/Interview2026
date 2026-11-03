# 90. MongoDB with Express — REST API CRUD
# हिंदी में: Express के साथ MongoDB — REST API CRUD

---

## 🔵 Simple Definition (English)
A **REST API with CRUD** maps four database actions (Create, Read, Update, Delete) to HTTP verbs (`POST`, `GET`, `PATCH/PUT`, `DELETE`) on a resource URL like `/products`. **Express** handles routing and JSON parsing, **Mongoose** gives a schema + model, and **MongoDB** stores the documents. The API is the only door through which clients touch your data.

## 🔵 सरल परिभाषा (Hindi)
**CRUD के साथ REST API** चार database actions (Create, Read, Update, Delete) को HTTP verbs (`POST`, `GET`, `PATCH/PUT`, `DELETE`) से `/products` जैसे resource URL पर map करती है। **Express** routing और JSON parsing संभालता है, **Mongoose** schema + model देता है, और **MongoDB** documents store करता है। Client सिर्फ API के ज़रिए ही आपके data तक पहुँचता है।

---

## 🔴 Problem it Solves
Browsers and mobile apps cannot (and must never) talk to MongoDB directly — that would expose credentials and skip validation. You need a thin server layer that: validates input, converts HTTP requests into queries, maps errors to proper status codes (400, 404, 500), and hides internal fields. Without a consistent CRUD pattern every endpoint gets written differently, with duplicated try/catch blocks, un-validated `req.body` going straight into the DB, and `500` errors for what are really user mistakes (bad id, missing field).

## 🔴 यह क्यों बना? (Hindi)
Browser और mobile app सीधे MongoDB से बात नहीं कर सकते (और कभी करनी भी नहीं चाहिए) — इससे credentials expose होते और validation skip हो जाती। एक पतली server layer चाहिए जो: input validate करे, HTTP request को query में बदले, errors को सही status code (400, 404, 500) दे, और internal fields छुपाए। CRUD का consistent pattern न हो तो हर endpoint अलग लिखा जाता है — duplicate try/catch, बिना validate किया `req.body` सीधे DB में, और user की गलती (गलत id, missing field) पर भी `500` error।

---

## 🟢 How it Works — Step by Step

Step 1 → `npm i express mongoose`; connect to MongoDB ONCE at startup with `mongoose.connect(uri)`.
Step 2 → Define a **Schema** (types, `required`, `min`, `default`) and compile it into a **Model** (`mongoose.model('Product', schema)`).
Step 3 → Add `app.use(express.json())` so `req.body` is parsed from JSON.
Step 4 → Map verbs: `POST /products` → `Model.create`, `GET /products` → `find`, `GET /products/:id` → `findById`, `PATCH /products/:id` → `findByIdAndUpdate`, `DELETE /products/:id` → `findByIdAndDelete`.
Step 5 → Validate the `:id` with `mongoose.isValidObjectId` (else 400), return `404` when the document is null, `201` on create, `204` on delete.
Step 6 → Add one central error middleware that turns `ValidationError` into `400` and everything else into `500`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `npm i express mongoose`; startup पर MongoDB से सिर्फ एक बार `mongoose.connect(uri)` से connect करो।
Step 2 → **Schema** define करो (types, `required`, `min`, `default`) और उसे **Model** में compile करो (`mongoose.model('Product', schema)`)।
Step 3 → `app.use(express.json())` लगाओ ताकि `req.body` JSON से parse हो।
Step 4 → Verbs map करो: `POST` → `create`, `GET` list → `find`, `GET /:id` → `findById`, `PATCH` → `findByIdAndUpdate`, `DELETE` → `findByIdAndDelete`।
Step 5 → `:id` को `mongoose.isValidObjectId` से check करो (वरना 400), document null हो तो `404`, create पर `201`, delete पर `204`।
Step 6 → एक central error middleware जो `ValidationError` को `400` और बाकी सब को `500` बनाए।

---

## 🟡 Real World Example
**Swiggy's restaurant-partner dashboard** lets a restaurant owner manage menu items. The mobile app calls `POST /menu-items` to add "Paneer Tikka, ₹220", `PATCH /menu-items/:id` to change the price to ₹240 or mark stock 0, and `DELETE` to remove a retired dish. If the owner submits a negative price, the API returns `400` with a message instead of saving garbage; if the dish was already deleted on another phone, `GET` returns `404`. The same collection serves customers via a read-only `GET /menu-items?restaurantId=...`.

## 🟡 Real Example Hindi mein
**Swiggy के restaurant-partner dashboard** में restaurant owner अपने menu items manage करता है। App `POST /menu-items` से "Paneer Tikka, ₹220" add करती है, `PATCH /menu-items/:id` से price ₹240 करती है या stock 0 करती है, और `DELETE` से बंद हुई dish हटाती है। Owner negative price भेजे तो API garbage save करने की जगह message के साथ `400` देती है; dish पहले ही दूसरे फोन से delete हो चुकी हो तो `GET` पर `404` मिलता है। वही collection customers को read-only `GET /menu-items?restaurantId=...` से serve होती है।

---

## 💻 Code Example — Basic

Tested against MongoDB 8.0.4 + Mongoose + Express (Node 24). The full script below was run end to end.

```javascript
// api.js — npm i express mongoose
const express = require('express');           // web framework
const mongoose = require('mongoose');         // ODM: schema + model + validation

// 1. Schema = shape + rules of every document in the collection
const productSchema = new mongoose.Schema({
  name:  { type: String, required: true, trim: true }, // trim removes spaces around the name
  price: { type: Number, required: true, min: 0 },     // negative prices rejected
  stock: { type: Number, default: 0 },                 // default used when client omits it
}, { timestamps: true });                              // auto createdAt / updatedAt

// 2. Model = class bound to the "products" collection
const Product = mongoose.model('Product', productSchema);

const app = express();
app.use(express.json());                       // parse JSON bodies into req.body

// CREATE — 201 Created
app.post('/products', async (req, res, next) => {
  try { res.status(201).json(await Product.create(req.body)); } // runs validation, then insert
  catch (e) { next(e); }                       // hand errors to the central handler
});

// READ ALL — .lean() returns plain objects (faster, no Mongoose document overhead)
app.get('/products', async (req, res, next) => {
  try { res.json(await Product.find().sort({ createdAt: -1 }).lean()); }
  catch (e) { next(e); }
});

// READ ONE — validate the id first, else Mongoose throws a CastError
app.get('/products/:id', async (req, res, next) => {
  try {
    if (!mongoose.isValidObjectId(req.params.id)) return res.status(400).json({ error: 'Invalid id' });
    const p = await Product.findById(req.params.id).lean();
    if (!p) return res.status(404).json({ error: 'Not found' });   // valid id, no document
    res.json(p);
  } catch (e) { next(e); }
});

// UPDATE — returnDocument:'after' gives the NEW doc; runValidators re-checks min/required
app.patch('/products/:id', async (req, res, next) => {
  try {
    const p = await Product.findByIdAndUpdate(
      req.params.id, { $set: req.body },
      { returnDocument: 'after', runValidators: true });
    if (!p) return res.status(404).json({ error: 'Not found' });
    res.json(p);
  } catch (e) { next(e); }
});

// DELETE — 204 No Content on success
app.delete('/products/:id', async (req, res, next) => {
  try {
    const p = await Product.findByIdAndDelete(req.params.id);
    if (!p) return res.status(404).json({ error: 'Not found' });
    res.status(204).end();
  } catch (e) { next(e); }
});

// Central error middleware (4 arguments = Express error handler)
app.use((err, req, res, next) => {
  if (err.name === 'ValidationError') return res.status(400).json({ error: err.message });
  res.status(500).json({ error: 'Server error' });   // never leak err.stack to clients
});

mongoose.connect('mongodb://127.0.0.1:27017/shop').then(() => app.listen(3000));
```

Output of the real test run (ObjectIds and timestamps differ on every run):
```text
POST   /products     201 {"name":"Paneer Tikka","price":220,"stock":10,"_id":"6ae9...","createdAt":"...","updatedAt":"...","__v":0}
POST   /products     400 {"error":"Product validation failed: price: Path `price` is required."}
GET    /products/:id 200 {"_id":"6ae9...","name":"Paneer Tikka","price":220,"stock":10,...}
GET    /products/xyz 400 {"error":"Invalid id"}
PATCH  /products/:id 200 {... "price":240 ...}
PATCH  /products/:id 400 {"error":"Validation failed: price: Path `price` (-5) is less than minimum allowed value (0)."}
DELETE /products/:id 204
GET    /products/:id 404 {"error":"Not found"}
```

## 💻 Code Example — Advanced

```javascript
// Production patterns: router, whitelist fields, filtering, pagination, duplicate key, async wrapper
const router = require('express').Router();

// Wrapper removes try/catch from every route (Express 5 does this natively; Express 4 needs it)
const wrap = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

// Pick only allowed fields — blocks mass-assignment like { role: 'admin' } or { _id: ... }
const pick = (obj, keys) => Object.fromEntries(keys.filter(k => k in obj).map(k => [k, obj[k]]));

router.get('/', wrap(async (req, res) => {
  const { minPrice, q, page = 1, limit = 10 } = req.query;
  const filter = {};                                            // build filter only from provided params
  if (minPrice) filter.price = { $gte: Number(minPrice) };      // price >= minPrice
  if (q) filter.name = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i'); // escape regex chars!
  const lim = Math.min(Number(limit), 50);                      // cap page size (DoS protection)
  const [items, total] = await Promise.all([
    Product.find(filter).sort({ _id: -1 }).skip((page - 1) * lim).limit(lim).lean(),
    Product.countDocuments(filter),                             // run in parallel
  ]);
  res.json({ items, total, page: Number(page), pages: Math.ceil(total / lim) });
}));

router.post('/', wrap(async (req, res) => {
  const body = pick(req.body, ['name', 'price', 'stock']);      // whitelist
  res.status(201).json(await Product.create(body));
}));

// Duplicate key (unique index) -> 409 Conflict instead of 500
router.use((err, req, res, next) => {
  if (err.code === 11000) return res.status(409).json({ error: 'Duplicate', key: err.keyValue });
  next(err);
});
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Graceful startup and shutdown — connect first, listen after, close pool on SIGTERM
async function start() {
  await mongoose.connect(process.env.MONGO_URI, { maxPoolSize: 20 }); // pool reused by all requests
  const server = app.listen(process.env.PORT || 3000);
  process.on('SIGTERM', async () => {        // Kubernetes / PM2 sends SIGTERM on deploy
    server.close();                           // stop accepting new requests
    await mongoose.disconnect();              // drain and close the pool
    process.exit(0);
  });
}
start().catch((e) => { console.error(e); process.exit(1); });
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Passing `req.body` blindly to `$set` / `create`
```javascript
// Wrong — client can send { "price": 1, "isAdmin": true } or operators like { "$where": ... }
await Product.findByIdAndUpdate(id, req.body);

// Right — whitelist the fields you accept
await Product.findByIdAndUpdate(id, { $set: pick(req.body, ['name','price','stock']) },
  { returnDocument: 'after', runValidators: true });
```

❌ Mistake 2: Forgetting `runValidators: true` on updates
✅ Correct: Schema validators run on `save()`/`create()` automatically but NOT on `findByIdAndUpdate` unless you pass `{ runValidators: true }`. Without it, `price: -5` gets saved silently.

❌ Mistake 3: Treating null as success
✅ Correct: `findById` returns `null` for a missing document (no error). Always check and return `404`, otherwise you send `200 null`.

❌ Mistake 4: Using the deprecated `{ new: true }`
✅ Correct: Mongoose prints a deprecation warning (seen in our test run); use `{ returnDocument: 'after' }`.

---

## 🧠 Tricky Interview Question

Q: `GET /products/12345` throws `CastError` and returns 500. Why, and what is the cleanest fix?

Answer: `findById('12345')` tries to cast the string into an `ObjectId`, which needs 24 hex characters (or 12 bytes), so Mongoose throws `CastError` before even querying. Fix by validating with `mongoose.isValidObjectId(id)` and returning `400`, or by handling `err.name === 'CastError'` in the central error middleware. Note: a valid-looking but non-existing id is different — that returns `null` and must become `404`. Also beware that `isValidObjectId` accepts any 12-character string; use `ObjectId.isValid` plus a regex `/^[0-9a-f]{24}$/` if you need strictness.

---

## ⚫ Interview Questions + Answers

Q1: Which HTTP status codes should a CRUD API return?
A1: `201` for create (with the new resource), `200` for read/update, `204` for delete, `400` for validation/bad id, `404` for missing resource, `409` for duplicate unique key, `500` for unexpected server errors.

Q2: PUT vs PATCH?
A2: `PUT` replaces the whole resource (`replaceOne`/`findOneAndReplace`, missing fields vanish); `PATCH` updates only given fields with `$set`. Most partial updates should be `PATCH`.

Q3: Why `.lean()`?
A3: It skips building full Mongoose documents (getters, virtuals, `save()` method), returning plain JS objects. It is much faster and lighter on memory for read-only endpoints, but you lose virtuals and instance methods.

Q4: Where should validation live — Mongoose or Express layer?
A4: Both have roles. Mongoose schema validators are the last line of defence (data integrity). A request-layer validator (Zod/Joi/express-validator) rejects bad input early, gives nicer error messages, and also protects fields that are not in the schema. Production APIs use both.

Q5: How do you prevent NoSQL injection in an Express + Mongo API?
A5: Never pass raw `req.body`/`req.query` objects as filters (`{ email: { $ne: null } }` bypasses login). Cast to strings (`String(req.body.email)`), validate with a schema library, enable Mongoose `sanitizeFilter: true`, and whitelist fields.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need a standard resource-oriented backend for web/mobile clients
- Entities map cleanly to collections (products, orders, users)
- You want schema-level validation on top of flexible documents

❌ Avoid when:
- You need complex, graph-like queries across many resources — consider GraphQL or a dedicated query layer
- A heavy reporting workload — expose aggregation endpoints separately, not via plain CRUD
- Real-time updates are the main feature — add WebSockets/SSE (fed by change streams) instead of polling CRUD

---

## 📊 Visual Diagram
```
  Client (Swiggy app)
      │  POST /products  {name, price}
      ▼
  ┌──────────────────────┐
  │ Express              │  express.json() → req.body
  │  router → controller │
  └─────────┬────────────┘
            │ Product.create(body)         ◄── Mongoose validates
            ▼
  ┌──────────────────────┐
  │ Mongoose Model       │  schema: required, min, default
  └─────────┬────────────┘
            │ insertOne (driver, pooled connection)
            ▼
  ┌──────────────────────┐
  │ MongoDB (products)   │
  └─────────┬────────────┘
            ▼
   201 {_id, name, ...}   |   400 ValidationError   |   404 null
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| CRUD | Create, Read, Update, Delete | बनाओ, पढ़ो, बदलो, हटाओ |
| REST | Resource URLs + HTTP verbs | Resource URL + HTTP verbs वाला API style |
| Schema | Shape and rules of documents | Documents की shape और rules |
| Model | Class bound to a collection | Collection से जुड़ी class |
| `lean()` | Return plain JS objects | Plain JS objects लौटाना (तेज़) |
| CastError | Bad type conversion (e.g. invalid id) | गलत type conversion error |
| Middleware | Function in the request pipeline | Request pipeline का function |
| Mass assignment | Client sets fields it shouldn't | Client का अनचाहे fields set करना |

---

## ⚡ 3-Line Summary
English:
1. Map POST/GET/PATCH/DELETE to Mongoose `create/find/findByIdAndUpdate/findByIdAndDelete` and return correct status codes (201, 200, 204, 400, 404).
2. Validate ids, whitelist body fields, use `runValidators` and `returnDocument: 'after'`, and handle errors in one middleware.
3. Connect once at startup, reuse the pool, and close it gracefully on shutdown.

Hindi:
1. POST/GET/PATCH/DELETE को Mongoose के `create/find/findByIdAndUpdate/findByIdAndDelete` से map करो और सही status code (201, 200, 204, 400, 404) लौटाओ।
2. Id validate करो, body के fields whitelist करो, `runValidators` और `returnDocument: 'after'` लगाओ, और errors एक middleware में संभालो।
3. Startup पर एक बार connect करो, pool reuse करो, और shutdown पर gracefully बंद करो।

---

## ➡️ Next Topic
**91. MongoDB with Next.js (connection caching)** — Why serverless/hot-reload environments exhaust connections and how a cached global connection fixes it.
