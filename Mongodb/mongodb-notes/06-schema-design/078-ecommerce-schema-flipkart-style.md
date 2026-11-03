# 78. Designing an E-commerce Schema (Flipkart style)
# हिंदी में: E-commerce Schema Design (Flipkart जैसा)

---

## 🔵 Simple Definition (English)
Designing an **e-commerce schema** in MongoDB means deciding which collections you need (`products`, `users`, `orders`, `reviews`, `carts`) and for each relationship whether to **embed** the data or **reference** it by id. The rule is "model for your access patterns": data that is read together lives together (order + its line items), data that grows without bound or is shared across many parents (reviews, users) gets its own collection.

## 🔵 सरल परिभाषा (Hindi)
MongoDB में **e-commerce schema design** का मतलब है तय करना कि कौन-से collections चाहिए (`products`, `users`, `orders`, `reviews`, `carts`) और हर relationship के लिए data को **embed** करना है या id से **reference**। नियम है "access patterns के हिसाब से model करो": जो data साथ पढ़ा जाता है वो साथ रहता है (order + उसके line items), और जो data बिना limit बढ़ता है या कई parents में share होता है (reviews, users) उसका अलग collection।

---

## 🔴 Problem it Solves
A catalog like Flipkart has millions of products with wildly different attributes (a phone has RAM, a shirt has size), orders that must stay correct even if the product price changes tomorrow, and reviews that can reach hundreds of thousands per product. A naive port of a SQL design (one table per entity, JOIN everything) makes the product page and the order history slow, while naive "embed everything" blows past the 16 MB document limit and makes updates heavy. A good schema keeps the hot reads (product page, search listing, order history) to a **single query** and keeps unbounded data out of the parent document.

## 🔴 यह क्यों बना? (Hindi)
Flipkart जैसे catalog में लाखों products होते हैं जिनके attributes बहुत अलग होते हैं (phone में RAM, shirt में size), orders जो product का price कल बदलने पर भी सही रहने चाहिए, और reviews जो एक product पर लाखों हो सकते हैं। SQL design को सीधे port करने (हर entity की table, सब कुछ JOIN) से product page और order history slow हो जाते हैं, और "सब कुछ embed" करने से 16 MB document limit टूट जाती है। अच्छा schema hot reads (product page, listing, order history) को **एक query** में रखता है और unbounded data को parent document से बाहर।

---

## 🟢 How it Works — Step by Step

Step 1 → List the screens/queries first: product listing (filter by category + price), product page, "my orders", cart, "add review", admin sales report.
Step 2 → **products**: one document per product. Different attributes per category go in an `attrs` array of `{k, v}` (the **Attribute Pattern**) so one multikey index serves every filter. Keep `ratingAvg` and `ratingCount` precomputed on the product (**Computed Pattern**).
Step 3 → **orders**: embed the line `items` and the shipping address as a **snapshot** (name, `priceAtPurchase`, address copy). Orders must never change when the catalog changes, so duplication here is a feature, not a bug.
Step 4 → **reviews**: separate collection (unbounded). Reference `productId` + `userId`, and add a unique compound index so a user can review a product only once.
Step 5 → **users**: embed small bounded things (addresses, max ~10). Do not embed orders inside the user.
Step 6 → Add indexes that match the queries (ESR rule: Equality, Sort, Range) and decrement stock with a conditional atomic update.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पहले screens/queries की list बनाओ: product listing (category + price filter), product page, "my orders", cart, "review add", admin sales report।
Step 2 → **products**: हर product का एक document। अलग-अलग category के attributes `attrs` array में `{k, v}` की तरह रखो (**Attribute Pattern**) ताकि एक multikey index हर filter सँभाले। `ratingAvg` और `ratingCount` पहले से compute करके product पर रखो (**Computed Pattern**)।
Step 3 → **orders**: line `items` और shipping address को **snapshot** की तरह embed करो (name, `priceAtPurchase`, address की copy)। Catalog बदलने पर order नहीं बदलना चाहिए, इसलिए यहाँ duplication एक feature है।
Step 4 → **reviews**: अलग collection (unbounded)। `productId` + `userId` reference रखो और unique compound index लगाओ ताकि एक user एक product पर एक ही review दे।
Step 5 → **users**: छोटी bounded चीज़ें embed करो (addresses, max ~10)। Orders को user के अंदर embed मत करो।
Step 6 → Queries के हिसाब से indexes (ESR rule) और stock को conditional atomic update से घटाओ।

---

## 🟡 Real World Example
When you open an iPhone on **Flipkart**, the page needs name, price, specs, stock and rating in one go: that is one `products` read by `_id`. The first page of reviews is a separate indexed query (`productId` + newest first) with `limit(10)`. When you place an order, Flipkart stores `priceAtPurchase`; even if the iPhone price drops during Big Billion Days, your old invoice still shows what you paid. On "My Orders" the app reads `orders` by `userId` sorted by `placedAt` desc; each order already contains its items, so no join is needed.

## 🟡 Real Example Hindi mein
**Flipkart** पर iPhone खोलने पर page को name, price, specs, stock और rating एक साथ चाहिए: यानी `_id` से `products` का एक read। Reviews का पहला page अलग indexed query है (`productId` + newest first, `limit(10)`)। Order देते समय Flipkart `priceAtPurchase` रखता है; Big Billion Days में price गिरे तब भी आपके पुराने invoice में वही price दिखता है जो आपने दिया था। "My Orders" में `userId` से `orders` को `placedAt` desc sort करके पढ़ा जाता है; हर order में items पहले से हैं, इसलिए join नहीं चाहिए।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4 (standalone/replica set both fine)
const d = db.getSiblingDB("flipkart");   // pick (and lazily create) the database
d.dropDatabase();                          // clean slate for the demo

// PRODUCTS: attribute pattern -> varying specs live in one array of {k, v}
d.products.insertMany([
  { _id: "P1", name: "iPhone 15", category: "mobiles", brand: "Apple", price: 79900,
    attrs: [{ k: "ram", v: "6GB" }, { k: "storage", v: "128GB" }],
    ratingAvg: 4.6, ratingCount: 1200, stock: 50 },
  { _id: "P2", name: "Boat Rockerz", category: "audio", brand: "boAt", price: 1299,
    attrs: [{ k: "battery", v: "60h" }], ratingAvg: 4.1, ratingCount: 8000, stock: 500 },
  { _id: "P3", name: "Redmi Note 13", category: "mobiles", brand: "Xiaomi", price: 17999,
    attrs: [{ k: "ram", v: "8GB" }, { k: "storage", v: "128GB" }],
    ratingAvg: 4.3, ratingCount: 5000, stock: 0 }
]);

// Listing page index: Equality (category) first, then Range (price)
d.products.createIndex({ category: 1, price: 1 });
// One multikey index serves EVERY attribute filter (ram, storage, battery...)
d.products.createIndex({ "attrs.k": 1, "attrs.v": 1 });

// USERS: small bounded list (addresses) is embedded
d.users.insertOne({ _id: "U1", name: "Aman",
  addresses: [{ label: "home", city: "Pune", pin: "411001" }] });

// REVIEWS: unbounded -> separate collection, referencing product and user
d.reviews.insertMany([
  { productId: "P1", userId: "U1", stars: 5, text: "Great" },
  { productId: "P1", userId: "U2", stars: 4, text: "Good" }
]);
// One review per user per product, enforced by the database
d.reviews.createIndex({ productId: 1, userId: 1 }, { unique: true });

// ORDERS: items + address are SNAPSHOTS (price at purchase, copied address)
d.orders.insertOne({
  _id: "O1", userId: "U1", status: "PLACED", placedAt: new Date("2025-01-10"),
  shipTo: { city: "Pune", pin: "411001" },
  items: [
    { productId: "P1", name: "iPhone 15",    priceAtPurchase: 79900, qty: 1 },
    { productId: "P2", name: "Boat Rockerz", priceAtPurchase: 1299,  qty: 2 }
  ],
  total: 82498
});
d.orders.createIndex({ userId: 1, placedAt: -1 });   // "My Orders" query

// Query 1: phones under 20000 (uses category_1_price_1)
d.products.find({ category: "mobiles", price: { $lt: 20000 } }, { name: 1, price: 1, _id: 0 }).toArray();
// Output: [ { name: 'Redmi Note 13', price: 17999 } ]

// Query 2: filter by attribute, both k and v must match the SAME array element
d.products.find({ attrs: { $elemMatch: { k: "ram", v: "8GB" } } }, { name: 1, _id: 0 }).toArray();
// Output: [ { name: 'Redmi Note 13' } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — continues from the Basic example (same data)

// 1) ATOMIC STOCK DECREMENT: the filter checks stock, the $inc changes it, in ONE operation.
//    No "read stock, then write stock" race between two buyers of the last unit.
d.products.updateOne({ _id: "P1", stock: { $gte: 1 } }, { $inc: { stock: -1 } });
// Output: { acknowledged: true, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
d.products.updateOne({ _id: "P3", stock: { $gte: 1 } }, { $inc: { stock: -1 } });
// Output: matchedCount: 0, modifiedCount: 0   <- P3 has stock 0, so the order must be rejected

// 2) MY ORDERS: newest first, served fully by index { userId: 1, placedAt: -1 }
d.orders.find({ userId: "U1" }, { status: 1, total: 1 }).sort({ placedAt: -1 }).limit(5).toArray();
// Output: [ { _id: 'O1', status: 'PLACED', total: 82498 } ]

// 3) ADMIN REPORT: revenue per product from embedded items ($unwind explodes the items array)
d.orders.aggregate([
  { $unwind: "$items" },                                      // one doc per line item
  { $group: { _id: "$items.productId",                        // group by product
              revenue: { $sum: { $multiply: ["$items.priceAtPurchase", "$items.qty"] } } } },
  { $sort: { revenue: -1 } }                                  // biggest first
]).toArray();
// Output: [ { _id: 'P1', revenue: 79900 }, { _id: 'P2', revenue: 2598 } ]

// 4) COMPUTED PATTERN: running average rating updated with a pipeline update
//    new avg = (oldAvg * oldCount + newStars) / (oldCount + 1)  — no need to re-scan reviews
d.products.updateOne({ _id: "P1" }, [
  { $set: {
      ratingAvg: { $round: [ { $divide: [
        { $add: [ { $multiply: ["$ratingAvg", "$ratingCount"] }, 5 ] },   // 5 = new star rating
        { $add: ["$ratingCount", 1] } ] }, 3 ] },
      ratingCount: { $add: ["$ratingCount", 1] } } }
]);
d.products.findOne({ _id: "P1" }, { ratingAvg: 1, ratingCount: 1 });
// Output: { _id: 'P1', ratingAvg: 4.6, ratingCount: 1201 }

// 5) Duplicate review is rejected by the unique index
try { d.reviews.insertOne({ productId: "P1", userId: "U1", stars: 1 }); }
catch (e) { print(e.code); }          // Output: 11000 (E11000 duplicate key)
// (ObjectIds and dates differ on your machine; every number above is real tested output.)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Mongoose models mirroring the design above (tested with Mongoose 9 on MongoDB 8.0.4)
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

// Product: attribute pattern + precomputed rating
const Product = mongoose.model('Product', new Schema({
  name: String, category: String, brand: String, price: Number, stock: Number,
  attrs: [{ _id: false, k: String, v: String }],    // _id:false avoids useless sub-ids
  ratingAvg: { type: Number, default: 0 }, ratingCount: { type: Number, default: 0 },
}));

// Order: snapshot of items so later price changes never rewrite history
const Order = mongoose.model('Order', new Schema({
  userId: { type: Schema.Types.ObjectId, ref: 'User', index: true },
  status: { type: String, default: 'PLACED' },
  items: [{ _id: false, productId: Schema.Types.ObjectId, name: String, priceAtPurchase: Number, qty: Number }],
  total: Number,
}, { timestamps: true }));

const app = express();
app.use(express.json());

app.post('/api/orders', async (req, res) => {
  const { userId, items } = req.body;                // [{ productId, qty }]
  const lines = [];
  for (const it of items) {
    // atomic conditional decrement: succeeds only if enough stock is left
    const p = await Product.findOneAndUpdate(
      { _id: it.productId, stock: { $gte: it.qty } },
      { $inc: { stock: -it.qty } },
      { returnDocument: 'after' });                   // Mongoose 9 uses returnDocument, not new:true
    if (!p) return res.status(409).json({ error: `Out of stock: ${it.productId}` });
    lines.push({ productId: p._id, name: p.name, priceAtPurchase: p.price, qty: it.qty });
  }
  const total = lines.reduce((s, l) => s + l.priceAtPurchase * l.qty, 0);
  res.status(201).json(await Order.create({ userId, items: lines, total }));
});
// NOTE: if the 2nd item fails, the 1st stock is already decremented. For all-or-nothing use
// a transaction (see topic 88) or compensate by restoring stock.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Referencing the product from the order and reading the price live
```javascript
// Wrong — order stores only productId; invoice changes when the catalog price changes
{ userId: "U1", items: [{ productId: "P1", qty: 1 }] }

// Right — snapshot the fields that must stay historically true
{ userId: "U1", items: [{ productId: "P1", name: "iPhone 15", priceAtPurchase: 79900, qty: 1 }] }
```

❌ Mistake 2: Embedding reviews inside the product document
```javascript
// Wrong — array grows forever -> big doc, hot-spot writes, 16 MB limit risk
{ _id: "P1", reviews: [ /* 300000 reviews */ ] }

// Right — separate collection + unique index + paginated reads
db.reviews.createIndex({ productId: 1, createdAt: -1 });
db.reviews.find({ productId: "P1" }).sort({ createdAt: -1 }).limit(10);
```

❌ Mistake 3: Read stock, check in app code, then write it back
✅ Correct: use `updateOne({ _id, stock: { $gte: qty } }, { $inc: { stock: -qty } })` and check `modifiedCount`. Single-document updates are atomic.

---

## 🧠 Tricky Interview Question

**Q:** Why not store the whole order history inside the `users` document so "My Orders" is a single read?

**Answer:** Because it is an **unbounded array**. A heavy buyer accumulates thousands of orders, so the user document keeps growing (towards the 16 MB limit), every order write rewrites/relocates a larger document, the document is loaded entirely into the WiredTiger cache just to show the profile name, and you cannot efficiently paginate or index across all orders (e.g., "all orders in status SHIPPED" for ops). Keep `orders` as its own collection with index `{ userId: 1, placedAt: -1 }`; that is still one indexed query for "My Orders", but bounded per page. Rule: embed bounded and read-together; reference unbounded or independently queried.

---

## ⚫ Interview Questions + Answers

Q1: What is the Attribute Pattern and why use it for products?
A1: Instead of one field per attribute (`ram`, `storage`, `battery`, ...) which would need an index per field, store attributes as an array of `{k, v}` pairs and create one index on `{"attrs.k":1, "attrs.v":1}`. Filtering works with `$elemMatch` so key and value match the same element. It keeps documents polymorphic and indexes manageable.

Q2: Should order line items embed or reference products?
A2: Embed a snapshot (name, price at purchase, qty) plus keep `productId` for navigation. Orders are historical records; they must not change when the product changes. The small duplication is intentional.

Q3: How do you avoid overselling the last unit?
A3: Use a conditional atomic update `{ _id, stock: { $gte: qty } }` with `$inc`, and check whether `matchedCount` is 1. Single-document operations are atomic, so two concurrent buyers cannot both succeed for the last item. For multi-document consistency (stock + order + payment) use a transaction.

Q4: Why keep `ratingAvg`/`ratingCount` on the product instead of computing from reviews each time?
A4: Computing needs an aggregation over possibly millions of reviews on every product page view. The Computed Pattern updates the numbers incrementally at write time (writes are rarer than reads), making reads O(1).

Q5: Which indexes does this design need?
A5: `products {category, price}` for listing, `products {attrs.k, attrs.v}` for filters, `reviews {productId, userId}` unique, `reviews {productId, createdAt}` for pagination, `orders {userId, placedAt:-1}`. Follow ESR: equality fields, then sort, then range.

---

## 🔷 When to Use + When Not to Use
✅ Use this design when:
- The catalog is polymorphic (many categories with different attributes)
- Reads (product page, order history) vastly outnumber writes
- Orders need an immutable historical snapshot

❌ Avoid / change when:
- You need multi-entity ACID on every operation at huge scale (consider transactions carefully, or a relational store for payments/ledger)
- Attributes are few and fixed (then plain top-level fields are simpler than the attribute pattern)
- Inventory is very high-contention (use a dedicated inventory service/reservation flow)

---

## 📊 Visual Diagram
```
E-COMMERCE SCHEMA (FLIPKART STYLE)
─────────────────────────────────────────────────────────
 users                      products
 { _id, name,               { _id, name, category, price,
   addresses:[...] } ◄──┐     attrs:[{k,v}], stock,
   (embedded, bounded)  │     ratingAvg, ratingCount }
                        │          ▲
          userId (ref)  │          │ productId (ref)
                        │          │
 orders ────────────────┘     reviews
 { _id, userId, status,       { productId, userId, stars, text }
   shipTo:{...},               unique(productId,userId)
   items:[{productId,name,     (separate: unbounded)
     priceAtPurchase,qty}],
   total }
   (items EMBEDDED as snapshot)

 EMBED  = bounded + read together   |  REFERENCE = unbounded / shared
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Nesting related data inside a document | Related data को document के अंदर रखना |
| Referencing | Storing another document's id | दूसरे document की id रखना |
| Attribute Pattern | Variable specs as array of `{k, v}` | बदलते specs को `{k, v}` array में रखना |
| Computed Pattern | Pre-calculate values at write time | Write के समय values पहले से compute करना |
| Snapshot | Copy of data frozen at a point in time | किसी समय के data की frozen copy |
| Multikey index | Index over array elements | Array elements पर index |
| ESR rule | Equality, Sort, Range index order | Index fields का क्रम: Equality, Sort, Range |

---

## ⚡ 3-Line Summary
English:
1. Design from access patterns: embed what is read together and bounded (order items), reference what is unbounded or shared (reviews, users).
2. Snapshot price/address in orders, use the Attribute Pattern for polymorphic specs, and precompute ratings.
3. Use conditional atomic updates for stock and indexes that follow the ESR rule.

Hindi:
1. Access patterns से design करो: जो साथ पढ़ा जाए और bounded हो उसे embed करो (order items), जो unbounded या shared हो उसे reference करो (reviews, users)।
2. Orders में price/address का snapshot रखो, polymorphic specs के लिए Attribute Pattern और ratings पहले से compute करो।
3. Stock के लिए conditional atomic updates और ESR rule वाले indexes इस्तेमाल करो।

---

## ➡️ Next Topic
**79. Designing a Food Delivery Schema (Zomato style)** — restaurants with geo search, menus, orders with status history and rider assignment.
