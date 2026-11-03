# 85. Mongoose Virtuals, Methods and Statics
# हिंदी में: Mongoose Virtuals, Methods और Statics

---

## 🔵 Simple Definition (English)
Three ways to add behaviour to a Mongoose model without storing extra data:
- **Virtual** — a computed property (`fullName`, `priceWithGst`) that exists on the document in JavaScript but is **not stored** in MongoDB.
- **Instance method** (`schema.methods.x`) — a function available on each **document** (`user.comparePassword()`).
- **Static** (`schema.statics.x`) — a function available on the **Model** (`User.findByEmail()`), plus **query helpers** (`schema.query.x`) for chainable queries.

## 🔵 सरल परिभाषा (Hindi)
Extra data store किए बिना Mongoose model में behaviour जोड़ने के तीन तरीके:
- **Virtual** — computed property (`fullName`, `priceWithGst`) जो JavaScript में document पर होती है पर MongoDB में **store नहीं** होती।
- **Instance method** (`schema.methods.x`) — हर **document** पर उपलब्ध function (`user.comparePassword()`)।
- **Static** (`schema.statics.x`) — **Model** पर उपलब्ध function (`User.findByEmail()`), और chainable queries के लिए **query helpers** (`schema.query.x`)।

---

## 🔴 Problem it Solves
Derived data (full name, price with tax, "isExpired") should not be stored because it goes stale and wastes space; but you also do not want to recompute it differently in 10 controllers. Likewise, query logic like "all cheap products" or password checking logic would be duplicated everywhere. Virtuals, methods and statics keep the logic next to the data, named and testable, with zero extra storage.

## 🔴 यह क्यों बना? (Hindi)
Derived data (full name, tax के साथ price, "isExpired") store नहीं करना चाहिए क्योंकि वह stale हो जाता है और जगह घेरता है; पर आप इसे 10 controllers में अलग-अलग तरीके से compute भी नहीं करना चाहते। इसी तरह "सारे सस्ते products" या password जाँचने का logic हर जगह दोहराना पड़ता। Virtuals, methods और statics logic को data के पास रखते हैं, नाम के साथ, test करने योग्य, और बिना extra storage के।

---

## 🟢 How it Works — Step by Step

Step 1 → **Virtual getter**: `schema.virtual('fullName').get(function () { return ... })`. `this` is the document.
Step 2 → **Virtual setter**: `.set(function (v) { ... })` lets you assign `doc.fullName = 'Priya Singh'` and have it split into real fields (`first`, `last`).
Step 3 → Virtuals are **not included** in `toJSON()`/`toObject()` by default. Enable with `{ toJSON: { virtuals: true }, toObject: { virtuals: true } }`. Mongoose also adds an `id` string virtual by default.
Step 4 → Virtuals **cannot be queried** (`find({ fullName })` does not work, as they are not in the DB) and are **absent from `.lean()` results** (verified).
Step 5 → **Instance methods**: `schema.methods.discounted = function (pct) {...}`; call on a document: `p.discounted(10)`.
Step 6 → **Statics**: `schema.statics.findCheap = function (max) { return this.find(...) }`; here `this` is the Model.
Step 7 → **Query helpers**: `schema.query.byFirst = function (n) { return this.where(...) }` give chainable `Model.find().byFirst('A')`.
Step 8 → **Never use arrow functions** for these: `this` is lost (verified: `this` inside an arrow in the schema file was the module's `this`, an empty object, not the document).
Step 9 → **Populate virtuals**: a virtual with `ref`, `localField`, `foreignField` creates a "reverse reference" that `populate()` can fill (see topic 86).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **Virtual getter**: `schema.virtual('fullName').get(function () { return ... })`। `this` document है।
Step 2 → **Virtual setter**: `.set(function (v) { ... })` से आप `doc.fullName = 'Priya Singh'` assign कर सकते हैं और वह असली fields (`first`, `last`) में बँट जाता है।
Step 3 → Virtuals `toJSON()`/`toObject()` में default रूप से **शामिल नहीं** होते। `{ toJSON: { virtuals: true }, toObject: { virtuals: true } }` से चालू करो। Mongoose default रूप से `id` string virtual भी जोड़ता है।
Step 4 → Virtuals को **query नहीं** कर सकते (`find({ fullName })` काम नहीं करता क्योंकि वे DB में नहीं हैं) और वे **`.lean()` results में नहीं** होते (verified)।
Step 5 → **Instance methods**: `schema.methods.discounted = function (pct) {...}`; document पर call: `p.discounted(10)`।
Step 6 → **Statics**: `schema.statics.findCheap = function (max) { return this.find(...) }`; यहाँ `this` Model है।
Step 7 → **Query helpers**: `schema.query.byFirst = function (n) { return this.where(...) }` से chainable `Model.find().byFirst('A')` मिलता है।
Step 8 → इनके लिए **arrow functions कभी नहीं**: `this` खो जाता है (verified: schema file में arrow के अंदर `this` document नहीं, module का खाली object था)।
Step 9 → **Populate virtuals**: `ref`, `localField`, `foreignField` वाला virtual "reverse reference" बनाता है जिसे `populate()` भर सकता है (topic 86 देखो)।

---

## 🟡 Real World Example
A **Zomato**-like `MenuItem` model keeps only `basePrice` and `gstPct` in MongoDB. A virtual `priceWithGst` computes the customer-facing price on the fly (so changing the GST rate never needs a data migration). An instance method `item.discounted(pct)` applies promo codes. A static `MenuItem.findVegUnder(200)` powers the "Veg under 200" shelf, and a query helper `.inRestaurant(id)` chains onto any query. All screens share one definition, so prices are consistent across the app.

## 🟡 Real Example Hindi mein
**Zomato** जैसे `MenuItem` model में MongoDB में सिर्फ `basePrice` और `gstPct` रहते हैं। Virtual `priceWithGst` customer को दिखने वाली price उसी समय compute करता है (GST rate बदलने पर data migration नहीं चाहिए)। Instance method `item.discounted(pct)` promo codes लगाता है। Static `MenuItem.findVegUnder(200)` "Veg under 200" shelf को चलाता है, और query helper `.inRestaurant(id)` किसी भी query में chain हो जाता है। सभी screens एक ही definition इस्तेमाल करती हैं, इसलिए price पूरे app में consistent रहती है।

---

## 💻 Code Example — Basic

```javascript
// virtuals-basic.js — real output (Mongoose 9, MongoDB 8.0.4). ObjectIds differ on your machine.
const mongoose = require('mongoose');

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');

  const s = new mongoose.Schema(
    { first: String, last: String, price: Number, gstPct: { type: Number, default: 18 } },
    { toJSON: { virtuals: true }, toObject: { virtuals: true } }   // include virtuals in JSON output
  );

  // VIRTUAL with getter AND setter — nothing named fullName is stored in MongoDB
  s.virtual('fullName')
    .get(function () { return `${this.first} ${this.last}`; })            // computed on read
    .set(function (v) { [this.first, this.last] = v.split(' '); });       // splits on write

  // VIRTUAL computed from numbers
  s.virtual('priceWithGst').get(function () {
    return Math.round(this.price * (1 + this.gstPct / 100));
  });

  // INSTANCE METHOD — callable on a document; `this` = the document
  s.methods.discounted = function (pct) { return this.price * (1 - pct / 100); };

  // STATIC — callable on the Model; `this` = the Model
  s.statics.findCheap = function (max) { return this.find({ price: { $lt: max } }); };

  // QUERY HELPER — chainable: Model.find().byFirst('A')
  s.query.byFirst = function (n) { return this.where({ first: n }); };

  const P = mongoose.model('Virt', s);
  await P.deleteMany({});

  const p = new P({ price: 1000 });
  p.fullName = 'Priya Singh';                                   // setter fills first + last
  console.log(p.first, '|', p.last, '|', p.fullName, '|', p.priceWithGst);
  // Output: Priya | Singh | Priya Singh | 1180

  await p.save();
  await P.create({ first: 'A', last: 'B', price: 5000 });

  console.log(JSON.stringify(p.toJSON()));
  // Output: {"price":1000,"gstPct":18,"_id":"<id>","first":"Priya","last":"Singh","__v":0,
  //          "fullName":"Priya Singh","priceWithGst":1180,"id":"<id>"}   (virtuals + the default `id` appear)

  console.log('method:', p.discounted(10));                        // Output: method: 900
  console.log('static:', (await P.findCheap(2000)).length);        // Output: static: 1
  console.log('query helper:', (await P.find().byFirst('A')).length); // Output: query helper: 1
  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// virtuals-advanced.js — what virtuals can NOT do, plus the arrow-function trap
const mongoose = require('mongoose');
(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const P = mongoose.model('Virt');                    // compiled in the Basic example

  // 1) Virtuals are NOT stored: look at the raw document the driver sees
  console.log('virtual in DB?', Object.keys(await P.collection.findOne({ first: 'Priya' })).join(','));
  // Output: virtual in DB? _id,price,gstPct,first,last,__v     (no fullName, no priceWithGst)

  // 2) Virtuals can NOT be used in queries
  console.log('virtual query works?', (await P.find({ fullName: 'Priya Singh' })).length);
  // Output: virtual query works? 0     (the filter goes to MongoDB as-is, no stored field named fullName exists, so 0 matches)

  // 3) lean() returns plain objects => NO virtuals, NO methods
  console.log('lean has virtual?', (await P.findOne({ first: 'Priya' }).lean()).fullName);
  // Output: lean has virtual? undefined
  //   (use the mongoose-lean-virtuals plugin if you need them with lean())

  // 4) Arrow functions break `this`
  const arrow = new mongoose.Schema({ n: Number });
  arrow.methods.bad = () => typeof this;               // `this` here is the module-level `this`
  console.log('arrow this:', mongoose.model('Arr', arrow).hydrate({ n: 1 }).bad());
  // Output: arrow this: object        (an empty module `this`, NOT the document: n is not accessible)

  // 5) Practical pattern: password check as an instance method + findByEmail static
  const userSchema = new mongoose.Schema({ email: String, passwordHash: String });
  userSchema.methods.verify = async function (plain) {
    // return bcrypt.compare(plain, this.passwordHash);   // real code uses bcrypt
    return plain === this.passwordHash;                  // demo only
  };
  userSchema.statics.findByEmail = function (email) {
    return this.findOne({ email: email.toLowerCase() });  // centralises normalisation
  };
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');

const menuItemSchema = new mongoose.Schema({
  name: String, basePrice: Number, veg: Boolean, restaurantId: String,
  gstPct: { type: Number, default: 5 },
}, { toJSON: { virtuals: true } });                       // send virtuals to API clients

menuItemSchema.virtual('priceWithGst').get(function () {
  return Math.round(this.basePrice * (1 + this.gstPct / 100));
});
menuItemSchema.statics.findVegUnder = function (limit) {
  return this.find({ veg: true, basePrice: { $lt: limit } }).sort({ basePrice: 1 });
};
menuItemSchema.query.inRestaurant = function (id) { return this.where({ restaurantId: id }); };
menuItemSchema.methods.discounted = function (pct) { return Math.round(this.priceWithGst * (1 - pct / 100)); };

const MenuItem = mongoose.model('MenuItem', menuItemSchema);
const app = express();

app.get('/api/shelves/veg-under/:limit', async (req, res) => {
  // statics + query helper chain naturally; response includes virtual priceWithGst
  const items = await MenuItem.findVegUnder(Number(req.params.limit)).inRestaurant(req.query.restaurantId || 'R1');
  res.json(items);
});

app.get('/api/items/:id/price', async (req, res) => {
  const item = await MenuItem.findById(req.params.id);   // must NOT be lean() to keep the virtual + method
  if (!item) return res.sendStatus(404);
  res.json({ price: item.priceWithGst, promo10: item.discounted(10) });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Arrow function for method / virtual / static
```javascript
// Wrong — this is not the document
schema.methods.total = () => this.price * this.qty;

// Right
schema.methods.total = function () { return this.price * this.qty; };
```

❌ Mistake 2: Expecting virtuals in `lean()` results or in queries
```javascript
// Wrong
await P.find({ fullName: 'Priya Singh' });        // virtual is not in the DB
(await P.findOne().lean()).fullName;              // undefined

// Right — query the real fields, or plug in mongoose-lean-virtuals
await P.find({ first: 'Priya', last: 'Singh' });
```

❌ Mistake 3: Forgetting `toJSON: { virtuals: true }`
✅ Correct: `res.json(doc)` calls `doc.toJSON()`; without the schema option your API response silently omits virtuals like `priceWithGst`.

---

## 🧠 Tricky Interview Question

**Q:** Your API returns `priceWithGst` correctly in `/items/:id` but the same field is `undefined` in `/items` (the list endpoint). Same schema. What changed?

**Answer:** The list endpoint uses `.lean()` for speed. `lean()` skips document hydration, so it returns plain objects from the driver: no virtuals, no instance methods, no getters, no defaults applied on read. Options: remove `lean()` (accept the hydration cost), compute the value in an aggregation (`$project` with `$round`/`$multiply`), use `mongoose-lean-virtuals`, or calculate it in a mapping function. The virtual never existed in MongoDB, which is exactly why lean results lack it.

---

## ⚫ Interview Questions + Answers

Q1: Virtual vs stored field, how to choose?
A1: Store data you must query/sort/index on or that is expensive to recompute. Use a virtual for cheap derived values that depend on stored fields and must always be current. A virtual cannot be indexed or used in `find` filters.

Q2: `methods` vs `statics`?
A2: `methods` are available on documents (`this` = document) and operate on one record; `statics` are on the Model (`this` = Model) and typically run queries across many records. Query helpers are chainable pieces of a query.

Q3: Why `id` appears in my JSON even though I never defined it?
A3: Mongoose adds an `id` virtual that returns `_id` as a string. Disable it with `{ id: false }` in schema options.

Q4: How do you make setters/getters for stored fields (not virtual)?
A4: Use `get` / `set` options on a path: `{ type: Number, get: v => Math.round(v), set: v => v * 100 }`. Path getters apply on read (include with `toJSON: { getters: true }`).

Q5: What is a populate virtual?
A5: A virtual with `ref`, `localField` and `foreignField` that lets `populate()` load documents referencing this one (e.g., `Department.staff` filled from `Employee.dept`) without storing an array of ids.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Derived values are cheap and must always match stored data
- Query logic or per-document behaviour is repeated across your code
- You want chainable, named query pieces (`byRestaurant`, `active`)

❌ Avoid when:
- You need to filter, sort or index by the derived value (store it, or compute in aggregation)
- You rely on `lean()` for performance and need the computed field (compute in pipeline instead)
- The logic is heavy or IO-bound (keep in a service)

---

## 📊 Visual Diagram
```
VIRTUALS vs METHODS vs STATICS
──────────────────────────────────────────────────────
 Stored in MongoDB:   { first:"Priya", last:"Singh", price:1000, gstPct:18 }
                              │
          ┌───────────────────┼───────────────────────┐
          ▼                   ▼                       ▼
 VIRTUAL (on doc)     METHOD (on doc)         STATIC (on Model)
 doc.fullName         doc.discounted(10)      Model.findCheap(2000)
 doc.priceWithGst     this = document         this = Model
 not stored           one record              many records
 not in lean()        not in lean()           QUERY HELPER:
 not queryable                                Model.find().byFirst('A')
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Virtual | Computed, non-stored property | Computed, बिना store की property |
| Getter / setter | Read / write interceptors | Read / write interceptors |
| Instance method | Function on a document | Document पर function |
| Static | Function on the model | Model पर function |
| Query helper | Chainable query function | Chain होने वाला query function |
| `lean()` | Return plain objects | Plain objects लौटाना |
| Populate virtual | Reverse reference via virtual | Virtual से reverse reference |

---

## ⚡ 3-Line Summary
English:
1. Virtuals are computed, never stored, and need `toJSON: { virtuals: true }` to appear in API output.
2. `methods` act on one document, `statics` on the model, `query` helpers chain onto queries; always use `function`, not arrows.
3. Virtuals disappear with `lean()` and cannot be queried, so store or aggregate what you need to filter on.

Hindi:
1. Virtuals computed होते हैं, कभी store नहीं होते, और API output में दिखने के लिए `toJSON: { virtuals: true }` चाहिए।
2. `methods` एक document पर, `statics` model पर, `query` helpers queries में chain होते हैं; हमेशा `function` इस्तेमाल करो, arrow नहीं।
3. Virtuals `lean()` के साथ गायब हो जाते हैं और query नहीं हो सकते, इसलिए जिस पर filter करना हो उसे store करो या aggregate करो।

---

## ➡️ Next Topic
**86. Mongoose Populate** — "joining" referenced documents with `populate()` and its trade-offs.
