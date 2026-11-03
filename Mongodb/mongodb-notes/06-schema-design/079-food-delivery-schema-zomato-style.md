# 79. Designing a Food Delivery Schema (Zomato style)
# हिंदी में: Food Delivery Schema Design (Zomato जैसा)

---

## 🔵 Simple Definition (English)
A **food-delivery schema** models restaurants (with a GeoJSON location), menu items, customers, riders and orders that move through a lifecycle (`PLACED -> ACCEPTED -> PICKED_UP -> DELIVERED`). The key MongoDB ideas are: a `2dsphere` index for "restaurants near me", orders that embed their items as a price snapshot with a `statusHistory` array, and **guarded updates** (`updateOne({ _id, status: "PLACED" }, ...)`) so state transitions are atomic and cannot go backwards.

## 🔵 सरल परिभाषा (Hindi)
**Food-delivery schema** restaurants (GeoJSON location के साथ), menu items, customers, riders और orders को model करता है जो एक lifecycle से गुज़रते हैं (`PLACED -> ACCEPTED -> PICKED_UP -> DELIVERED`)। MongoDB के मुख्य idea हैं: "मेरे पास के restaurants" के लिए `2dsphere` index, orders में items का price snapshot और `statusHistory` array, और **guarded updates** (`updateOne({ _id, status: "PLACED" }, ...)`) ताकि state transitions atomic रहें और पीछे न जा सकें।

---

## 🔴 Problem it Solves
Food delivery has three tricky needs at once: **geo queries** (open restaurants within 5 km), **fast-changing order state** touched by customer, restaurant and rider apps concurrently (two riders must not be assigned to one order), and **menu availability** that flips constantly. If you model it naively (read order, change status in app code, write back) two actors overwrite each other. If you model menus embedded inside restaurants, one hot restaurant document gets rewritten for every "item sold out" toggle.

## 🔴 यह क्यों बना? (Hindi)
Food delivery में तीन मुश्किल ज़रूरतें एक साथ होती हैं: **geo queries** (5 km के अंदर खुले restaurants), **तेज़ी से बदलती order state** जिसे customer, restaurant और rider apps एक साथ छूते हैं (एक order को दो riders assign नहीं होने चाहिए), और **menu availability** जो लगातार बदलती है। Naive तरीके (order पढ़ो, app में status बदलो, वापस लिखो) में दो actors एक-दूसरे को overwrite कर देते हैं। Menu को restaurant के अंदर embed करने पर हर "item sold out" toggle पर पूरा hot restaurant document दोबारा लिखना पड़ता है।

---

## 🟢 How it Works — Step by Step

Step 1 → **restaurants**: store `location` as a GeoJSON `Point` (`[longitude, latitude]` order!) and create a `2dsphere` index.
Step 2 → **menuItems**: separate collection with `restaurantId`, index `{ restaurantId, category }`. Toggling `available` touches only one small document. Variants (half/full) are embedded because they are bounded and always read with the item.
Step 3 → **orders**: embed `items` as snapshot (name + price at order time), keep `restaurantId`, `customerId`, `riderId` (null until assigned), `status` and `statusHistory`.
Step 4 → **State machine via guarded update**: include the expected current status in the filter. If it does not match, `matchedCount` is 0 and you know somebody else already moved the order.
Step 5 → **Rider assignment**: `findOneAndUpdate({ _id, riderId: null }, { $set: { riderId } })` is a compare-and-set. Only one rider wins.
Step 6 → Index for each dashboard: `{ restaurantId, status, placedAt:-1 }` for the restaurant app, `{ customerId, placedAt:-1 }` for order history.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → **restaurants**: `location` को GeoJSON `Point` की तरह रखो (`[longitude, latitude]` क्रम!) और `2dsphere` index बनाओ।
Step 2 → **menuItems**: अलग collection, `restaurantId` के साथ, index `{ restaurantId, category }`। `available` toggle करने पर सिर्फ एक छोटा document बदलता है। Variants (half/full) embed होते हैं क्योंकि वे bounded हैं और item के साथ ही पढ़े जाते हैं।
Step 3 → **orders**: `items` को snapshot की तरह embed करो (order के समय का name + price), साथ में `restaurantId`, `customerId`, `riderId` (assign होने तक null), `status` और `statusHistory`।
Step 4 → **Guarded update से state machine**: filter में अपेक्षित current status डालो। मेल न खाए तो `matchedCount` 0 आता है और पता चलता है कि किसी और ने order आगे बढ़ा दिया।
Step 5 → **Rider assignment**: `findOneAndUpdate({ _id, riderId: null }, { $set: { riderId } })` एक compare-and-set है। सिर्फ एक rider जीतता है।
Step 6 → हर dashboard के लिए index: restaurant app के लिए `{ restaurantId, status, placedAt:-1 }`, order history के लिए `{ customerId, placedAt:-1 }`।

---

## 🟡 Real World Example
When you open **Zomato** at 8 PM in Bengaluru, the home screen runs `$near` on `restaurants.location` with `$maxDistance: 5000` and `isOpen: true`. Tapping a restaurant loads its `menuItems` by `restaurantId`. If the restaurant marks "Butter Chicken" as out of stock, only that one menu document flips `available: false`. After you pay, an `orders` document is created with a price snapshot. The restaurant's tablet calls an update guarded by `status: "PLACED"` to accept it; nearby riders get a push, and whoever taps first wins the compare-and-set on `riderId: null`, the others get "order already taken".

## 🟡 Real Example Hindi mein
रात 8 बजे बेंगलुरु में **Zomato** खोलने पर home screen `restaurants.location` पर `$near` चलाता है `$maxDistance: 5000` और `isOpen: true` के साथ। Restaurant पर tap करने से उसके `menuItems` `restaurantId` से load होते हैं। Restaurant "Butter Chicken" को out of stock mark करे तो सिर्फ वही एक menu document `available: false` होता है। Payment के बाद price snapshot वाला `orders` document बनता है। Restaurant का tablet `status: "PLACED"` से guarded update करके accept करता है; पास के riders को push जाता है और जो पहले tap करे वही `riderId: null` का compare-and-set जीतता है, बाकियों को "order already taken" मिलता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh — tested on MongoDB 8.0.4
const d = db.getSiblingDB("zomato");
d.dropDatabase();

// RESTAURANTS: GeoJSON point is [longitude, latitude] (NOT lat, lng)
d.restaurants.insertMany([
  { _id: "R1", name: "Punjabi Tadka", cuisines: ["North Indian", "Mughlai"],
    location: { type: "Point", coordinates: [77.5946, 12.9716] }, rating: 4.3, isOpen: true },
  { _id: "R2", name: "Dosa Corner", cuisines: ["South Indian"],
    location: { type: "Point", coordinates: [77.6200, 12.9800] }, rating: 4.0, isOpen: true }
]);
d.restaurants.createIndex({ location: "2dsphere" });   // REQUIRED for $near / $geoWithin queries

// MENU ITEMS: separate collection, variants embedded (bounded + read together)
d.menuItems.insertMany([
  { restaurantId: "R1", name: "Paneer Tikka", price: 220, veg: true, category: "Starters",
    variants: [{ size: "half", price: 120 }, { size: "full", price: 220 }], available: true },
  { restaurantId: "R1", name: "Butter Chicken", price: 340, veg: false, category: "Mains", available: true },
  { restaurantId: "R2", name: "Masala Dosa", price: 90, veg: true, category: "Mains", available: false }
]);
d.menuItems.createIndex({ restaurantId: 1, category: 1 });   // "show menu of restaurant X"

// ORDER with price snapshot + status history
d.orders.insertOne({
  _id: "O1", customerId: "C1", restaurantId: "R1", riderId: null, status: "PLACED",
  items: [{ menuItemId: "M1", name: "Paneer Tikka", price: 220, qty: 2 }],   // snapshot
  total: 440,
  statusHistory: [{ status: "PLACED", at: new Date("2025-02-01T12:00:00Z") }],
  placedAt: new Date("2025-02-01T12:00:00Z")
});
d.orders.createIndex({ restaurantId: 1, status: 1, placedAt: -1 });  // restaurant dashboard
d.orders.createIndex({ customerId: 1, placedAt: -1 });               // customer history

// Restaurants open within 5 km of a user standing at (77.60, 12.97)
d.restaurants.find({
  isOpen: true,
  location: { $near: { $geometry: { type: "Point", coordinates: [77.60, 12.97] }, $maxDistance: 5000 } }
}, { name: 1, _id: 0 }).toArray();
// Output: [ { name: 'Punjabi Tadka' }, { name: 'Dosa Corner' } ]   (nearest first)

// Vegetarian items that are currently available at R1
d.menuItems.find({ restaurantId: "R1", available: true, veg: true }, { name: 1, price: 1, _id: 0 }).toArray();
// Output: [ { name: 'Paneer Tikka', price: 220 } ]
```

## 💻 Code Example — Advanced

```javascript
// mongosh — continues from the Basic example

// 1) GUARDED STATE TRANSITION: only move PLACED -> ACCEPTED, and log it in history atomically
d.orders.updateOne(
  { _id: "O1", status: "PLACED" },                               // expected current state
  { $set: { status: "ACCEPTED" },                                // new state
    $push: { statusHistory: { status: "ACCEPTED", at: new Date("2025-02-01T12:01:00Z") } } });
// Output: { acknowledged: true, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }

// Same call again (e.g. double tap / retry): order is no longer PLACED
d.orders.updateOne({ _id: "O1", status: "PLACED" }, { $set: { status: "ACCEPTED" } });
// Output: matchedCount: 0, modifiedCount: 0   <- idempotent, nothing overwritten

// 2) COMPARE-AND-SET RIDER ASSIGNMENT: succeeds only while riderId is still null
d.orders.findOneAndUpdate(
  { _id: "O1", riderId: null },
  { $set: { riderId: "D7" } },
  { returnDocument: "after", projection: { riderId: 1, status: 1 } });
// Output: { _id: 'O1', riderId: 'D7', status: 'ACCEPTED' }
// A second rider running the same call gets null back (document no longer matches).

// 3) Restaurant analytics: orders and revenue per restaurant for accepted orders
d.orders.aggregate([
  { $match: { status: "ACCEPTED" } },                                       // WHERE
  { $group: { _id: "$restaurantId", orders: { $sum: 1 }, revenue: { $sum: "$total" } } }  // GROUP BY
]).toArray();
// Output: [ { _id: 'R1', orders: 1, revenue: 440 } ]
// (Every output line above is real output from mongod 8.0.4; dates/ObjectIds vary.)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const express = require('express');
const mongoose = require('mongoose');
const { Schema } = mongoose;

const orderSchema = new Schema({
  customerId: String, restaurantId: String,
  riderId: { type: String, default: null },
  status: { type: String, enum: ['PLACED', 'ACCEPTED', 'PICKED_UP', 'DELIVERED'], default: 'PLACED' },
  items: [{ _id: false, name: String, price: Number, qty: Number }],
  total: Number,
  statusHistory: [{ _id: false, status: String, at: { type: Date, default: Date.now } }],
}, { timestamps: { createdAt: 'placedAt', updatedAt: false } });
orderSchema.index({ restaurantId: 1, status: 1, placedAt: -1 });
const Order = mongoose.model('Order', orderSchema);

// Allowed transitions — the "state machine" lives in ONE place
const NEXT = { PLACED: 'ACCEPTED', ACCEPTED: 'PICKED_UP', PICKED_UP: 'DELIVERED' };

const app = express();
app.use(express.json());

app.patch('/api/orders/:id/advance', async (req, res) => {
  const { from } = req.body;                                // client states what it saw
  const to = NEXT[from];
  if (!to) return res.status(400).json({ error: 'Invalid transition' });
  const order = await Order.findOneAndUpdate(
    { _id: req.params.id, status: from },                   // guard
    { $set: { status: to }, $push: { statusHistory: { status: to } } },
    { returnDocument: 'after' });
  if (!order) return res.status(409).json({ error: 'Order already moved on' });
  res.json(order);
});

app.post('/api/orders/:id/claim', async (req, res) => {
  const order = await Order.findOneAndUpdate(
    { _id: req.params.id, riderId: null, status: 'ACCEPTED' },   // compare-and-set
    { $set: { riderId: req.body.riderId } }, { returnDocument: 'after' });
  order ? res.json(order) : res.status(409).json({ error: 'Order already taken' });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Swapping latitude and longitude
```javascript
// Wrong — GeoJSON order is [lng, lat]; this puts Bengaluru in the Indian Ocean / errors out of range
location: { type: "Point", coordinates: [12.9716, 77.5946] }

// Right
location: { type: "Point", coordinates: [77.5946, 12.9716] }
```

❌ Mistake 2: Read-modify-write on order status
```javascript
// Wrong — two apps read PLACED, both write; last writer silently wins
const o = await Order.findById(id); o.status = 'ACCEPTED'; await o.save();

// Right — guard with the expected current status in the filter
await Order.updateOne({ _id: id, status: 'PLACED' }, { $set: { status: 'ACCEPTED' } });
```

❌ Mistake 3: `$near` without a `2dsphere` index
✅ Correct: `$near` **requires** a geospatial index; without it the query errors. Create it before querying.

---

## 🧠 Tricky Interview Question

**Q:** Two riders tap "Accept delivery" for the same order at the same millisecond. How do you guarantee only one gets it without transactions?

**Answer:** Put the condition in the filter of a **single-document atomic update**: `findOneAndUpdate({ _id, riderId: null }, { $set: { riderId } })`. MongoDB serializes writes to one document, so exactly one operation sees `riderId: null` and matches; the second finds `riderId` already set, matches nothing and returns `null` (or `matchedCount: 0`). No lock, no transaction needed. This works because both the check and the write happen inside the same document-level atomic operation, unlike "read, check in JS, write".

---

## ⚫ Interview Questions + Answers

Q1: Should menu items be embedded in the restaurant document?
A1: Usually no. Menus are large, change often (availability toggles), and a restaurant can have hundreds of items. A separate `menuItems` collection keeps writes small and avoids rewriting the hot restaurant doc. Small bounded pieces like `variants` are fine to embed.

Q2: Which index supports "restaurants near me"?
A2: A `2dsphere` index on a GeoJSON field, queried with `$near`/`$geoNear` (sorted by distance) or `$geoWithin` (no sort). Coordinates are `[longitude, latitude]`.

Q3: Why store `statusHistory` as an array inside the order?
A3: It is bounded (a handful of states), always read together with the order, and `$push` on it is atomic with the status change in the same update. It gives an audit trail for support disputes without another collection.

Q4: Why snapshot item names and prices in the order?
A4: Menus change; an order is a historical fact. Snapshots keep invoices and refunds correct and avoid joining back to `menuItems`.

Q5: How would you handle live rider location at scale?
A5: Do not update the order doc on every ping. Write pings to a **time-series collection** (next topic) keyed by `riderId`, and keep only the latest position on the rider document if the map needs it.

---

## 🔷 When to Use + When Not to Use
✅ Use this design when:
- You need geo search plus flexible, frequently changing menus
- Status changes come from multiple actors concurrently (guarded updates)
- Orders are read as a whole (items + history in one document)

❌ Avoid / change when:
- Payments and settlements need strict multi-table accounting (keep ledger in a transactional store or use multi-document transactions)
- Order documents would carry very large unbounded logs (move logs to their own collection)

---

## 📊 Visual Diagram
```
FOOD DELIVERY SCHEMA (ZOMATO STYLE)
──────────────────────────────────────────────────────
 restaurants  (2dsphere on location)      riders
 { _id, name, cuisines,                   { _id, name, lastLocation }
   location:{Point},  isOpen }                   ▲
        ▲                                         │ riderId (null → set once)
        │ restaurantId                            │
 menuItems                         orders ────────┘
 { restaurantId, name, price,      { _id, customerId, restaurantId,
   veg, available,                   riderId, status,
   variants:[...embedded] }          items:[snapshot], total,
                                     statusHistory:[{status,at}] }

 STATE MACHINE (guarded updates):
 PLACED ──► ACCEPTED ──► PICKED_UP ──► DELIVERED
   updateOne({_id, status:"PLACED"}, {$set:{status:"ACCEPTED"}})
   matchedCount 0  ==> someone else already moved it
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| GeoJSON | Standard format for geographic shapes | Geographic shapes का standard format |
| 2dsphere | Index for earth-surface geo queries | पृथ्वी की सतह पर geo queries का index |
| `$near` | Find documents sorted by distance | Distance से sorted documents ढूँढना |
| Guarded update | Update whose filter checks the expected state | ऐसा update जिसका filter अपेक्षित state जाँचता है |
| Compare-and-set | Atomic "set only if still unchanged" | "बदला नहीं हो तभी set करो" atomic ऑपरेशन |
| Snapshot | Frozen copy of data in an order | Order में data की frozen copy |
| Status history | Array logging every state change | हर state change का log array |

---

## ⚡ 3-Line Summary
English:
1. Use a GeoJSON `Point` plus a `2dsphere` index for nearby restaurants; keep menus in their own collection.
2. Embed order items as a price snapshot with a `statusHistory` array.
3. Make state changes and rider assignment atomic with guarded `updateOne`/`findOneAndUpdate` filters.

Hindi:
1. पास के restaurants के लिए GeoJSON `Point` और `2dsphere` index इस्तेमाल करो; menus को अलग collection में रखो।
2. Order items को price snapshot की तरह और `statusHistory` array के साथ embed करो।
3. State changes और rider assignment को guarded `updateOne`/`findOneAndUpdate` filters से atomic बनाओ।

---

## ➡️ Next Topic
**80. Time-Series Collections** — storing high-volume rider GPS pings and sensor data efficiently with bucketing and automatic expiry.
