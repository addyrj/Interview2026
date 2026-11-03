# 70. Embedding vs Referencing
# हिंदी में: Embedding बनाम Referencing

---

## 🔵 Simple Definition (English)
**Embedding** stores related data *inside* the parent document (a nested object or array). **Referencing** stores related data in a *separate collection* and keeps its `_id` in the parent (like a foreign key), joined later with `$lookup` or Mongoose `populate()`. Embedding gives one-read, single-document atomicity; referencing gives smaller documents, independent updates and no 16 MB growth risk. Choose per relationship, not per project.

## 🔵 सरल परिभाषा (Hindi)
**Embedding** में related data parent document के *अंदर* (nested object या array) रखा जाता है। **Referencing** में related data *अलग collection* में रखा जाता है और parent में उसका `_id` (foreign key जैसा) रहता है, जिसे बाद में `$lookup` या Mongoose `populate()` से जोड़ा जाता है। Embedding में एक read और single-document atomicity मिलती है; referencing में छोटे documents, independent updates और 16 MB growth का ख़तरा नहीं। फ़ैसला हर relationship के लिए अलग करो, पूरे project के लिए नहीं।

---

## 🔴 Problem it Solves
Wrong choice hurts both ways. Over-referencing (everything normalised) makes the hot read need several queries/joins and no atomic multi-collection updates without transactions. Over-embedding (everything nested) creates huge, ever-growing documents: each small update rewrites a big document, the working set bloats, concurrent writers contend on one doc and you eventually hit the **16 MB** cap. You need a clear rule to pick per relationship.

## 🔴 यह क्यों बना? (Hindi)
गलत चुनाव दोनों तरफ़ नुकसान करता है। Over-referencing (सब normalised) में hot read को कई queries/joins चाहिए और transactions के बिना multi-collection atomic update नहीं। Over-embedding (सब nested) से विशाल, लगातार बढ़ते documents बनते हैं: हर छोटा update बड़ा document rewrite करता है, working set फूलता है, कई writers एक doc पर टकराते हैं और आख़िर में **16 MB** cap आ जाता है। हर relationship के लिए चुनने का साफ़ नियम चाहिए।

---

## 🟢 How it Works — Step by Step

Step 1 → Ask: **Is it read together?** If the child is almost always shown with the parent, lean to embed.
Step 2 → Ask: **Is it bounded?** 1:1 and 1:few (addresses, phone numbers) embed; 1:many that grows without limit (reviews, orders, log lines) reference.
Step 3 → Ask: **Is it updated independently or shared?** If many parents share one child (a course shared by thousands of students) or the child changes often on its own, reference (or copy only stable fields).
Step 4 → Ask: **Do you need atomic updates across both?** Embedded = one document = atomic without a transaction.
Step 5 → Ask: **Is the child queried alone?** Embedded array items can be queried, but if you often need "all reviews for X across restaurants", a separate collection with an index is easier.
Step 6 → Reference with `child.parentId` (store the id on the *many* side) and index it; embed with arrays/objects. Mix when needed (Subset, Extended Reference: note 73).

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → पूछो: **क्या साथ पढ़ा जाता है?** अगर child लगभग हमेशा parent के साथ दिखता है तो embed की तरफ़ झुको।
Step 2 → पूछो: **क्या bounded है?** 1:1 और 1:few (addresses, phone numbers) embed; बिना सीमा बढ़ने वाला 1:many (reviews, orders, log lines) reference।
Step 3 → पूछो: **क्या independent update होता है या shared है?** अगर कई parents एक child share करते हैं (हज़ारों students का एक course) या child अपने आप बार-बार बदलता है, तो reference (या सिर्फ़ stable fields copy)।
Step 4 → पूछो: **क्या दोनों पर atomic update चाहिए?** Embedded = एक document = बिना transaction के atomic।
Step 5 → पूछो: **क्या child अकेला query होता है?** Embedded array items query हो सकते हैं, पर "सभी restaurants के X के reviews" बार-बार चाहिए तो index वाली अलग collection आसान है।
Step 6 → Reference में `child.parentId` (*many* side पर id) रखो और index लगाओ; embed में arrays/objects। ज़रूरत हो तो mix करो (Subset, Extended Reference: note 73)।

---

## 🟡 Real World Example
**Swiggy order document**: delivery address snapshot, items (name, qty, price at order time) and payment summary are **embedded** in the order — they are read with the order, bounded, and must freeze the price at purchase time. The **restaurant** is a *reference* (`restaurantId`) because it is shared by millions of orders and its details change independently. The full **rating/reviews** of a restaurant are in their own collection because they grow without bound.

## 🟡 Real Example Hindi mein
**Swiggy का order document**: delivery address snapshot, items (नाम, qty, order के समय की price) और payment summary order में **embedded** हैं — वे order के साथ पढ़े जाते हैं, bounded हैं, और purchase के समय की price freeze रखनी होती है। **Restaurant** *reference* (`restaurantId`) है क्योंकि वह लाखों orders में shared है और उसकी details अलग बदलती हैं। Restaurant के पूरे **reviews** अपनी collection में हैं क्योंकि वे बिना सीमा बढ़ते हैं।

---

## 💻 Code Example — Basic

```javascript
// mongosh (MongoDB 8.0.4)
use t70

// EMBEDDED: order with items and address inside one document
db.orders.insertOne({
  _id: "o1",
  restaurantId: "r1",                                         // REFERENCE to the shared restaurant
  address: { line: "12 MG Road", city: "Pune" },              // 1:1 embedded
  items: [                                                    // 1:few embedded, price frozen at order time
    { name: "Paneer Tikka", qty: 2, price: 220 },
    { name: "Butter Naan",  qty: 4, price: 50 }
  ],
  total: 640
})
// Read the whole order in ONE query - no join
db.orders.findOne({ _id: "o1" })
// Output: { _id: 'o1', restaurantId: 'r1', address: {...}, items: [ {...}, {...} ], total: 640 }

// Atomic update of a nested item - single document, so atomic without a transaction
db.orders.updateOne(
  { _id: "o1", "items.name": "Butter Naan" },                 // match the array element
  { $set: { "items.$.qty": 6 }, $inc: { total: 100 } }        // $ = the matched element
)
// Output: { acknowledged: true, insertedId: null, matchedCount: 1, modifiedCount: 1, upsertedCount: 0 }
```

## 💻 Code Example — Advanced

```javascript
// mongosh — REFERENCED: restaurants + reviews with a $lookup join
use t70
db.restaurants.insertOne({ _id: "r1", name: "Meghana Foods", city: "Bengaluru" })
db.reviews.insertMany([
  { _id: 1, restaurantId: "r1", userId: "u1", stars: 5 },
  { _id: 2, restaurantId: "r1", userId: "u2", stars: 4 },
  { _id: 3, restaurantId: "r1", userId: "u3", stars: 3 }
])
db.reviews.createIndex({ restaurantId: 1 })                   // the reference field on the MANY side must be indexed

db.restaurants.aggregate([
  { $match: { _id: "r1" } },
  { $lookup: { from: "reviews", localField: "_id", foreignField: "restaurantId", as: "reviews" } },
  { $project: { name: 1, avgStars: { $avg: "$reviews.stars" }, n: { $size: "$reviews" } } }
])
// Output: [ { _id: 'r1', name: 'Meghana Foods', avgStars: 4, n: 3 } ]

// Measuring size so you can SEE the embed-growth risk: bsonsize returns bytes
db.big.insertOne({ _id: 1, items: [] })
for (let i = 0; i < 1000; i++) db.big.updateOne({ _id: 1 }, { $push: { items: { n: i, note: "x".repeat(50) } } })
db.big.aggregate([{ $project: { count: { $size: "$items" }, bytes: { $bsonSize: "$$ROOT" } } }])
// Output: [ { _id: 1, count: 1000, bytes: 77916 } ]  - grows linearly; 16 MB (16,777,216) is the hard cap
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const mongoose = require('mongoose');
const express = require('express');
const { Schema } = mongoose;

// EMBEDDED sub-documents (items) + REFERENCE (restaurant)
const orderSchema = new Schema({
  restaurant: { type: Schema.Types.ObjectId, ref: 'Restaurant', index: true },   // reference
  items: [{ name: String, qty: Number, price: Number }],                          // embedded array
  total: Number
});
const Order = mongoose.model('Order', orderSchema);
const Restaurant = mongoose.model('Restaurant', new Schema({ name: String }));
const Review = mongoose.model('Review', new Schema({
  restaurant: { type: Schema.Types.ObjectId, ref: 'Restaurant', index: true },
  stars: Number
}));

const app = express();

// populate() = app-side join (one extra query). Tested: returns restaurant {_id, name} inside each review
app.get('/rev/:id', async (req, res) => {
  const rows = await Review.find({ restaurant: req.params.id }).populate('restaurant', 'name').lean();
  res.json(rows);
});
// Real output: [{"_id":"...","restaurant":{"_id":"...","name":"Meghana"},"stars":5,"__v":0}, ...]
// (ObjectIds differ on every run)
// Note: populate runs a 2nd query, not a database JOIN; for heavy joins prefer aggregate()+$lookup.
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Embedding an unbounded array
```javascript
// Wrong — every review pushed into the restaurant: unbounded, rewrites big doc, 16 MB cap
db.restaurants.updateOne({ _id: "r1" }, { $push: { reviews: review } })
// Right — insert into reviews collection; keep only the latest 5 in the parent (Subset pattern)
db.reviews.insertOne({ restaurantId: "r1", ...review })
```

❌ Mistake 2: Referencing without an index on the reference field
```javascript
// Wrong — find({restaurantId:"r1"}) does a COLLSCAN on millions of reviews
// Right
db.reviews.createIndex({ restaurantId: 1 })
```
✅ Also: referencing for data that must be frozen in time (price at purchase) — copy it (embed) instead; otherwise old orders change when the price changes.

---

## 🧠 Tricky Interview Question

A `students` collection embeds a copy of each course (`{ courseId, title, syllabus }`). The course title is edited. What breaks, and what's the fix?

Answer: Each student has their own copy, so `updateMany` must touch every student enrolled, and until it finishes (non-atomic across documents without a transaction) readers see mixed old/new titles; missed copies stay stale forever. Fix: keep only `courseId` (reference) and `$lookup` the title, or embed only stable fields (Extended Reference: `{ courseId, title }`) accepting that a title change triggers a background `updateMany({ "courses.courseId": id }, { $set: { "courses.$[c].title": newTitle } }, { arrayFilters: [{ "c.courseId": id }] })`. Duplicate only what rarely changes.

---

## ⚫ Interview Questions + Answers

Q1: Give three situations where embedding is right.
A1: (1) 1:1 data (profile + address), (2) 1:few bounded lists (phone numbers, order line items), (3) data that must be read together or updated atomically with its parent.

Q2: When is referencing right?
A2: Unbounded 1:many (reviews, events), data shared across many parents (many-to-many), large rarely-needed data (documents, history), or data updated independently at high frequency.

Q3: How many references should an array of ids hold?
A3: Keep it bounded (hundreds, not millions). For N:N where one side is small (student has ≤ 50 courseIds) store ids on that side; for unbounded, store the reference on the "many" side (`review.restaurantId`) — "reference from the many to the one."

Q4: `$lookup` vs `populate()`?
A4: `$lookup` joins inside the database in one aggregation round trip; Mongoose `populate()` runs a second query and stitches in the app. `populate` is simpler for simple cases; `$lookup` is better for filtering/aggregating on joined data.

Q5: How does embedding affect atomicity and write amplification?
A5: Single-document writes are atomic (even across nested fields), so no transaction needed. But the whole document may be rewritten/oplogged more than the changed field, so very large documents with frequent small updates are costly.

---

## 🔷 When to Use + When Not to Use
✅ Embed when:
- Read together, bounded (1:1, 1:few), updated together, need atomicity or point-in-time snapshots

✅ Reference when:
- Unbounded growth, shared across parents, large/rare, independently updated, queried on its own

❌ Avoid:
- Embedding arrays that grow forever; referencing everything and joining on every request

---

## 📊 Visual Diagram
```
EMBEDDED                          REFERENCED
────────                          ──────────
orders                            restaurants        reviews
 └ { _id: o1,                      { _id: r1 }  ◄──── { restaurantId: r1,
     address: {...},               { _id: r2 }          stars: 5 }
     items: [ {...}, {...} ] }                          { restaurantId: r1, ...}
   one read, atomic               two reads / $lookup / populate
   grows with the array           child grows independently, indexed
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Embedding | Nested data inside parent | Parent के अंदर nested data |
| Referencing | Store another doc's `_id` | दूसरे doc का `_id` रखना |
| `$lookup` | In-DB left outer join | DB के अंदर join |
| `populate` | Mongoose app-level join | Mongoose का app-level join |
| 1:few / 1:many | Small bounded / large unbounded relation | छोटा / बड़ा relation |
| Single-doc atomicity | One doc update is all-or-nothing | एक doc का update atomic |
| Working set | Data/indexes actively used in RAM | RAM में सक्रिय data |

---

## ⚡ 3-Line Summary
English:
1. Embed data that is read together, bounded and needs atomic updates; reference data that is unbounded, shared or independently updated.
2. Put the reference on the "many" side and index it; use `$lookup` or `populate()` to join.
3. Watch the 16 MB cap and write amplification, and duplicate only fields that rarely change.

Hindi:
1. जो data साथ पढ़ा जाता है, bounded है और atomic update चाहिए उसे embed करो; unbounded, shared या अलग से बदलने वाला data reference करो।
2. Reference "many" side पर रखो और index लगाओ; join के लिए `$lookup` या `populate()`।
3. 16 MB cap और write amplification पर नज़र रखो, और सिर्फ़ कम बदलने वाले fields duplicate करो।

---

## ➡️ Next Topic
**71. One-to-One, One-to-Many, Many-to-Many Modeling** — concrete schemas for each cardinality, including one-to-squillions.
