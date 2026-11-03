# 86. Mongoose Populate
# हिंदी में: Mongoose Populate

---

## 🔵 Simple Definition (English)
**`populate()`** replaces an `ObjectId` reference stored in one document with the actual referenced document(s) from another collection. You mark a schema path with `ref: 'ModelName'`, store only the id, and call `.populate('path')` on a query. It looks like a JOIN, but it is done by **Mongoose in your Node process** with an extra query (not by the database), so it costs one additional round trip per populated path.

## 🔵 सरल परिभाषा (Hindi)
**`populate()`** एक document में रखे `ObjectId` reference को दूसरी collection के असली referenced document(s) से बदल देता है। आप schema path पर `ref: 'ModelName'` लिखते हैं, सिर्फ id store करते हैं, और query पर `.populate('path')` call करते हैं। यह JOIN जैसा दिखता है, पर यह database नहीं बल्कि आपके Node process में **Mongoose** एक extra query चलाकर करता है, इसलिए हर populated path पर एक अतिरिक्त round trip लगता है।

---

## 🔴 Problem it Solves
When data is referenced (not embedded), an order contains only `user: ObjectId("...")` and `items.product: ObjectId("...")`. The API response needs the user's name and each product's name and price. Writing the extra `find` calls and stitching results by hand is repetitive and error-prone. `populate` automates the second query, the matching, and field selection, and keeps the code readable.

## 🔴 यह क्यों बना? (Hindi)
जब data reference होता है (embedded नहीं), तो order में सिर्फ `user: ObjectId("...")` और `items.product: ObjectId("...")` होता है। API response को user का नाम और हर product का नाम व price चाहिए। अतिरिक्त `find` calls लिखना और results को हाथ से जोड़ना दोहराव वाला और गलती-प्रवण है। `populate` दूसरी query, matching और field selection को automate करता है और code पढ़ने लायक रखता है।

---

## 🟢 How it Works — Step by Step

Step 1 → In the schema: `user: { type: Schema.Types.ObjectId, ref: 'User' }`. The string in `ref` must equal the registered **model name**.
Step 2 → Run the main query: `Order.findById(id)`. Mongoose gets the order with raw ids. In our test, without populate `o.user` was an `ObjectId`.
Step 3 → Add `.populate('user')`. Mongoose collects all `user` ids from the result set, then fires **one** `User.find({ _id: { $in: [...] } })` (not one per document).
Step 4 → Mongoose replaces the ids with documents. Options: `select` (fields), `match` (filter populated docs), `options` (`limit`, `sort`), `populate` (nested), `path`.
Step 5 → Arrays of refs and **sub-document paths** work: `.populate('items.product')`.
Step 6 → If a referenced doc is missing, a single ref becomes `null` (verified), and in an array it is removed (or `null` if the array is of sub-documents with `match`).
Step 7 → **Virtual populate** (`ref`, `localField`, `foreignField`) populates the "reverse" side (Department -> staff) without storing an id array on the parent.
Step 8 → `populate` works on `lean()` queries too; result is plain objects.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Schema में: `user: { type: Schema.Types.ObjectId, ref: 'User' }`। `ref` की string registered **model name** के बराबर होनी चाहिए।
Step 2 → मुख्य query चलाओ: `Order.findById(id)`। Mongoose को raw ids के साथ order मिलता है। हमारे test में populate के बिना `o.user` एक `ObjectId` था।
Step 3 → `.populate('user')` जोड़ो। Mongoose result set के सारे `user` ids इकट्ठा करता है और **एक** `User.find({ _id: { $in: [...] } })` चलाता है (हर document पर अलग नहीं)।
Step 4 → Mongoose ids को documents से बदल देता है। Options: `select` (fields), `match` (populated docs filter), `options` (`limit`, `sort`), `populate` (nested), `path`।
Step 5 → Refs के arrays और **sub-document paths** भी चलते हैं: `.populate('items.product')`।
Step 6 → Referenced doc न मिले तो single ref `null` हो जाता है (verified), और array में हट जाता है (या sub-documents वाले array में `match` के साथ `null`)।
Step 7 → **Virtual populate** (`ref`, `localField`, `foreignField`) "reverse" side (Department -> staff) को parent पर id array रखे बिना populate करता है।
Step 8 → `populate` `lean()` queries के साथ भी चलता है; result plain objects होते हैं।

---

## 🟡 Real World Example
On **Swiggy's** "Order details" screen the backend loads one `Order` (stores `user`, `restaurant`, `items.dish` as ids). With `populate('user', 'name phone')`, `populate('restaurant', 'name address')` and `populate('items.dish', 'name price')` the response includes names and prices without the order storing copies. Contrast this with the snapshot design in topic 78: for **historical** data (invoice) snapshots are right, while for **live** data (the restaurant's current display name and phone) populate keeps it up to date.

## 🟡 Real Example Hindi mein
**Swiggy** की "Order details" screen पर backend एक `Order` load करता है (जिसमें `user`, `restaurant`, `items.dish` ids के रूप में हैं)। `populate('user', 'name phone')`, `populate('restaurant', 'name address')` और `populate('items.dish', 'name price')` से response में नाम और price आ जाते हैं, order को copies रखनी नहीं पड़तीं। Topic 78 के snapshot design से तुलना करो: **historical** data (invoice) के लिए snapshot सही है, जबकि **live** data (restaurant का मौजूदा नाम और phone) के लिए populate उसे up to date रखता है।

---

## 💻 Code Example — Basic

```javascript
// populate-basic.js — real output (Mongoose 9, MongoDB 8.0.4). ObjectIds are random per run.
const mongoose = require('mongoose'); const { Schema } = mongoose;

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  await mongoose.connection.dropDatabase();

  // Referenced models
  const User = mongoose.model('User', new Schema({ name: String, email: String, password: String }));
  const Product = mongoose.model('Product', new Schema({ name: String, price: Number }));

  // Order stores ONLY ids; `ref` names the model to look up
  const Order = mongoose.model('Order', new Schema({
    user:  { type: Schema.Types.ObjectId, ref: 'User' },
    items: [{ product: { type: Schema.Types.ObjectId, ref: 'Product' }, qty: Number }],
    total: Number,
  }));

  const u = await User.create({ name: 'Aman', email: 'a@x.com', password: 'secret' });
  const [p1, p2] = await Product.create([{ name: 'Phone', price: 100 }, { name: 'Case', price: 10 }]);
  const o = await Order.create({
    user: u._id,
    items: [{ product: p1._id, qty: 1 }, { product: p2._id, qty: 2 }],
    total: 120,
  });

  // Without populate: just ObjectIds
  console.log(typeof o.user, o.user.constructor.name);
  // Output: object ObjectId

  // WITH populate: select picks fields; '-_id' excludes the id; sensitive `password` never selected
  const r = await Order.findById(o._id)
    .populate('user', 'name -_id')                                   // 1 extra query to users
    .populate({ path: 'items.product', select: 'name price' });      // 1 extra query to products
  console.log(JSON.stringify(r.toObject({ versionKey: false })));
  // Output (ids vary): {"_id":"...","user":{"name":"Aman"},
  //   "items":[{"product":{"_id":"...","name":"Phone","price":100},"qty":1,"_id":"..."},
  //            {"product":{"_id":"...","name":"Case","price":10},"qty":2,"_id":"..."}],"total":120}

  await mongoose.disconnect();
})();
```

## 💻 Code Example — Advanced

```javascript
// populate-advanced.js — match, lean, virtual populate, missing refs, doc.populate()
const mongoose = require('mongoose'); const { Schema } = mongoose;

(async () => {
  await mongoose.connect('mongodb://127.0.0.1:27116/mongoose_demo?replicaSet=rs0');
  const Order = mongoose.model('Order'); const User = mongoose.model('User');  // from Basic example

  // 1) `match` filters the POPULATED docs only; parents are still returned (non-matching refs become null)
  const filtered = await Order.findOne()
    .populate({ path: 'items.product', select: 'name', match: { price: { $gte: 50 } } });
  console.log(filtered.items.map(i => i.product && i.product.name));
  // Output: [ 'Phone', null ]       <- 'Case' (price 10) was filtered out but the line item stays

  // 2) populate + lean(): plain objects, faster, no document methods
  const lean = await Order.findOne().populate('user', 'name -_id').populate('items.product', 'name').lean();
  console.log(lean.items.map(i => i.product.name), lean.user.name);
  // Output: [ 'Phone', 'Case' ] Aman

  // 3) VIRTUAL POPULATE (reverse reference): Department.staff comes from Employee.dept
  const deptSchema = new Schema({ name: String }, { toJSON: { virtuals: true } });
  deptSchema.virtual('staff', { ref: 'Emp', localField: '_id', foreignField: 'dept' });  // define BEFORE mongoose.model()
  const Dept = mongoose.model('Dept', deptSchema);
  const Emp = mongoose.model('Emp', new Schema({ name: String, dept: Schema.Types.ObjectId }));
  const d = await Dept.create({ name: 'Eng' });
  await Emp.create([{ name: 'E1', dept: d._id }, { name: 'E2', dept: d._id }]);
  const dd = await Dept.findById(d._id).populate('staff', 'name -_id -dept');
  console.log(dd.toJSON().staff);
  // Output: [ { name: 'E1' }, { name: 'E2' } ]       (no id array stored on Dept)

  // 4) MISSING referenced doc -> null, not an error
  const ghost = await Order.create({ user: new mongoose.Types.ObjectId(), total: 1 });
  console.log('missing ref ->', (await Order.findById(ghost._id).populate('user')).user);
  // Output: missing ref -> null

  // 5) Populate an already-loaded document
  const o = await Order.findOne({ total: 120 });
  await o.populate('user');
  console.log('doc.populate:', o.user.name);
  // Output: doc.populate: Aman

  // 6) Limit populated array size (per-parent limits need `perDocumentLimit`)
  // .populate({ path: 'staff', options: { perDocumentLimit: 5, sort: { name: 1 } } })
  await mongoose.disconnect();
})();
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Order } = require('./models');                 // from the Basic example

const app = express();

// Order details — few docs, populate is perfect here
app.get('/api/orders/:id', async (req, res) => {
  if (!mongoose.isValidObjectId(req.params.id)) return res.status(400).json({ error: 'Bad id' });
  const order = await Order.findById(req.params.id)
    .populate('user', 'name email -_id')               // never expose password: select explicit fields
    .populate({ path: 'items.product', select: 'name price' })
    .lean();
  order ? res.json(order) : res.status(404).json({ error: 'Not found' });
});

// Order LIST — populate on a big list issues $in queries with thousands of ids; paginate!
app.get('/api/users/:id/orders', async (req, res) => {
  const page = Math.max(1, Number(req.query.page) || 1);
  const orders = await Order.find({ user: req.params.id })
    .sort({ _id: -1 }).skip((page - 1) * 20).limit(20)  // bounded: at most 20 parents
    .populate('items.product', 'name')
    .lean();
  res.json(orders);
});
// For analytics over many orders prefer aggregate() + $lookup (see topic 87), or embed a snapshot.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Wrong `ref` string
```javascript
// Wrong — model registered as 'User', ref says 'Users' => MissingSchemaError / nothing populates
user: { type: Schema.Types.ObjectId, ref: 'Users' }

// Right — ref must equal the first argument given to mongoose.model()
user: { type: Schema.Types.ObjectId, ref: 'User' }
```

❌ Mistake 2: Populating everything everywhere
```javascript
// Wrong — each populate = another query; leaks fields like password
await Order.find().populate('user').populate('items.product').populate('restaurant');

// Right — paginate, select only needed fields, or embed/snapshot hot data
await Order.find().limit(20).populate('user', 'name');
```

❌ Mistake 3: Treating populate as a database JOIN
✅ Correct: it runs separate queries in your Node process. You cannot filter or sort the parent by a populated field's value (`Order.find().populate('user').where('user.name')` does nothing). Use `$lookup` in aggregation when you need that.

---

## 🧠 Tricky Interview Question

**Q:** You call `Order.find({ status: 'PLACED' }).populate({ path: 'user', match: { city: 'Pune' } })`. You expected only Pune orders, but orders from other cities are still returned. Why?

**Answer:** `match` in populate filters only the **populated documents**, not the parent query. Orders whose user does not match still come back, with `user: null`. The parent query already ran before populate. To truly filter by user city, either (a) first query users in Pune and use `Order.find({ user: { $in: puneUserIds } })`, (b) filter the returned array in JS (`orders.filter(o => o.user)`), or (c) use an aggregation with `$lookup` + `$match`. This is a typical sign that populate is not a JOIN.

---

## ⚫ Interview Questions + Answers

Q1: How many queries does `populate` run for 100 orders?
A1: One for the orders plus one additional `find({ _id: { $in: [...] } })` per populated path (it batches ids; it is not N+1). Two populated paths => 3 queries total.

Q2: Populate vs `$lookup`?
A2: `populate` is client-side (Mongoose), simple, works across databases/collections with multiple round trips. `$lookup` is server-side in one aggregation, can filter/group on joined data, but is harder to read, and cannot be used across databases and needs care with sharded collections. Choose populate for response shaping, `$lookup` for reporting.

Q3: Should I reference or embed when I will always populate?
A3: If you always populate the same small, rarely changing data, embedding (or an extended-reference/snapshot with a few fields) is often better: one read, no extra queries. Reference when data is large, shared, unbounded or changes independently.

Q4: How do you hide sensitive fields when populating?
A4: Pass a `select` string/object (`'name -_id'`), use `select: false` in the referenced schema (password), or `options: { select }`. Never return whole user docs.

Q5: What does `perDocumentLimit` do?
A5: A normal `limit` in populate applies to the whole batched query, not per parent. `perDocumentLimit` makes Mongoose issue extra queries so each parent gets at most N populated children.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Referenced data is large, shared or changes independently
- Single-document or small paginated reads that need related fields
- You want clean code for shaping API responses

❌ Avoid when:
- You need to filter/sort/aggregate parents by fields of the related doc (use `$lookup` or denormalize)
- Large lists with multiple populates (N large `$in` queries; consider embedding hot fields)
- Historical records (invoices): store snapshots instead

---

## 📊 Visual Diagram
```
POPULATE = EXTRA QUERIES, NOT A DB JOIN
──────────────────────────────────────────────────────
 Order.find().populate('user').populate('items.product')

 Query 1: orders             → [{ user: U1, items:[{product:P1},{product:P2}] }, ...]
 Query 2: users    $in [U1..]  → { U1: {name:"Aman"} }          (1 query for ALL orders)
 Query 3: products $in [P1,P2] → { P1:{...}, P2:{...} }
 Mongoose stitches results in Node:

 { user:{name:"Aman"}, items:[{product:{name:"Phone"}}, {product:{name:"Case"}}] }

 match:{price:{$gte:50}} → filters populated docs only → other refs become null
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `ref` | Name of the referenced model | Referenced model का नाम |
| populate | Replace ids with documents | Ids को documents से बदलना |
| Virtual populate | Reverse reference without stored ids | बिना stored ids के reverse reference |
| `match` | Filter populated docs | Populated docs को filter करना |
| `select` | Choose returned fields | लौटने वाले fields चुनना |
| `$lookup` | Server-side join in aggregation | Aggregation में server-side join |
| `perDocumentLimit` | Per-parent limit on children | हर parent पर children की limit |

---

## ⚡ 3-Line Summary
English:
1. `ref` + `populate()` swaps stored ObjectIds for real documents using extra queries run by Mongoose, not by MongoDB.
2. Use `select`, pagination and `lean()` to keep it cheap and safe; `match` only filters populated docs, not parents.
3. For filtering/aggregating by related data use `$lookup`; for historical records use snapshots.

Hindi:
1. `ref` + `populate()` stored ObjectIds को असली documents से बदलता है, extra queries के ज़रिए जो MongoDB नहीं बल्कि Mongoose चलाता है।
2. इसे सस्ता और सुरक्षित रखने के लिए `select`, pagination और `lean()` इस्तेमाल करो; `match` सिर्फ populated docs को filter करता है, parents को नहीं।
3. Related data के आधार पर filter/aggregate करना हो तो `$lookup`; historical records के लिए snapshots।

---

## ➡️ Next Topic
**87. Mongoose Aggregation + lean()** — running pipelines through Mongoose and reading data fast with `lean()`.
