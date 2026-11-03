# 39. distinct() and Query Patterns
# हिंदी में: distinct() और Query Patterns

---

## 🔵 Simple Definition (English)
**`distinct(field, filter)`** returns an array of the unique values of a field across the documents that match a filter. For array fields it unwraps the array and returns the unique elements. It is a quick way to build dropdown filters ("all cities"), but it returns a single array limited by the 16 MB BSON document size, so for large cardinality use `$group` in the aggregation pipeline.

## 🔵 सरल परिभाषा (Hindi)
**`distinct(field, filter)`** उन documents में से, जो filter से match करते हैं, किसी field की unique values का array लौटाता है। Array fields के लिए यह array खोलकर unique elements देता है। Dropdown filters ("सभी cities") बनाने का तेज़ तरीका है, लेकिन result एक ही array में आता है जो 16 MB BSON limit तक सीमित है; ज़्यादा unique values हों तो aggregation में `$group` use करो।

---

## 🔴 Problem it Solves
Without `distinct`, you would fetch all documents and dedupe them in JavaScript - wasting network and memory. `distinct` does the dedupe on the server (and can use an index on the field for a fast scan), sending only unique values.

## 🔴 यह क्यों बना? (Hindi)
`distinct` के बिना सारे documents लाकर JavaScript में dedupe करना पड़ता - network और memory की बर्बादी। `distinct` server पर dedupe करता है (और field के index का फायदा ले सकता है), सिर्फ unique values भेजता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Call `db.orders.distinct("city")` - MongoDB scans (using an index if one exists on `city`) and collects unique values.
Step 2 → Optionally pass a filter: `distinct("city", { status: "paid" })` - only matching documents contribute.
Step 3 → If the field is an array, each element is considered separately (`tags: ["a","b"]` contributes `a` and `b`).
Step 4 → Documents where the field is missing contribute nothing; `null` values are included as `null` where stored.
Step 5 → Result is one array in one response, so a huge number of unique values can exceed 16 MB. Switch to `$group` (cursor-based) in that case.
Step 6 → For counts per value, use `$group` with `$sum: 1` - `distinct` cannot count.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `db.orders.distinct("city")` call करो - MongoDB scan करता है (index हो तो उसका use) और unique values इकट्ठा करता है।
Step 2 → Optional filter: `distinct("city", { status: "paid" })` - सिर्फ matching documents गिने जाते हैं।
Step 3 → Field array हो तो हर element अलग माना जाता है।
Step 4 → जिन documents में field नहीं है वे कुछ contribute नहीं करते।
Step 5 → Result एक ही array में आता है, इसलिए बहुत ज़्यादा unique values 16 MB से बड़ी हो सकती हैं; तब `$group` (cursor) use करो।
Step 6 → हर value की count चाहिए तो `$group` + `$sum: 1`; `distinct` गिन नहीं सकता।

---

## 🟡 Real World Example
**Flipkart's** search page filter sidebar: "Brand" and "Colour" checkboxes. The backend calls `products.distinct("brand", { category: "mobiles" })` to list the available brands. For "how many products per brand" (the number next to each checkbox), it uses `$group`.

## 🟡 Real Example Hindi mein
**Flipkart** के search page के filter sidebar में "Brand" और "Colour" checkboxes होते हैं। Backend `products.distinct("brand", { category: "mobiles" })` से उपलब्ध brands की list निकालता है। हर checkbox के पास की गिनती के लिए `$group` use होता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4)
use shop_demo
db.orders.insertMany([
  { city: "Delhi", status: "paid", tags: ["a", "b"] },
  { city: "Delhi", status: "paid", tags: ["b"] },
  { city: "Pune",  status: "new",  tags: [] },
  { city: "Pune",  status: "paid" }                 // no tags field at all
])

db.orders.distinct("city")                          // Output: [ 'Delhi', 'Pune' ]
db.orders.distinct("tags")                          // Output: [ 'a', 'b' ]  (array unwrapped, empty/missing ignored)
db.orders.distinct("city", { status: "paid" })      // Output: [ 'Delhi', 'Pune' ]

// How many documents match a filter / total?
db.orders.countDocuments({ status: "paid" })        // Output: 3 (accurate, uses filter)
db.orders.estimatedDocumentCount()                  // Output: 4 (fast, from metadata, no filter)
```

## 💻 Code Example — Advanced

```javascript
// Number of unique cities (large cardinality safe way, cursor based)
db.orders.aggregate([
  { $group: { _id: "$city" } },     // one doc per unique city
  { $count: "n" }                   // count them
])
// Output: [ { n: 2 } ]

// Unique values WITH counts - something distinct() cannot do
db.orders.aggregate([
  { $group: { _id: "$city", n: { $sum: 1 } } },
  { $sort: { _id: 1 } }
])
// Output: [ { _id: 'Delhi', n: 2 }, { _id: 'Pune', n: 2 } ]

// Common query patterns
db.orders.find({ status: "paid" }).sort({ city: 1 }).skip(0).limit(10)       // pagination (skip is slow for deep pages)
db.orders.find({ city: { $in: ["Delhi", "Pune"] } }, { city: 1, _id: 0 })    // projection
db.orders.findOne({ status: "new" })                                          // single doc
// Range-based pagination (better than skip): remember last _id
// db.orders.find({ _id: { $gt: lastId } }).sort({ _id: 1 }).limit(10)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// Filter options endpoint with native driver
app.get('/api/filters/cities', async (req, res) => {
  const cities = await db.collection('orders').distinct('city', { status: 'paid' });
  res.json(cities.sort());                         // distinct returns unsorted - sort in app
});

// Mongoose equivalent
const brands = await Product.distinct('brand', { category: 'mobiles' }); // returns a Promise<array>

// With counts, use aggregate
const counts = await Product.aggregate([
  { $match: { category: 'mobiles' } },
  { $group: { _id: '$brand', n: { $sum: 1 } } },
  { $sort: { n: -1 } },
]);
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `distinct` on a field with millions of unique values (e.g., `userId`)
```javascript
// Wrong - one giant array, can hit the 16 MB limit and block memory
db.orders.distinct("userId")
// Right - stream via aggregation (cursor), optionally with allowDiskUse
db.orders.aggregate([{ $group: { _id: "$userId" } }], { allowDiskUse: true })
```

❌ Mistake 2: Assuming `distinct` returns sorted values
✅ Correct: the order is not guaranteed; sort in code (or use `$group` + `$sort`).

❌ Mistake 3: Using `skip()` with huge offsets for pagination - it still scans skipped docs. Use range-based (`_id > last`) pagination.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.distinct("tags")   // documents: tags ["a","b"], ["b"], [], (missing)
```
Answer: `[ 'a', 'b' ]`. `distinct` flattens arrays and returns each unique element, not the arrays themselves. Empty arrays and missing fields add nothing. (Verified.)

---

## ⚫ Interview Questions + Answers

Q1: What does `distinct` do with array fields?
A1: It unwraps the array and returns unique elements across all documents, not unique arrays.

Q2: What is the limit of `distinct`?
A2: The result must fit in one 16 MB BSON document. For high-cardinality fields use `$group`.

Q3: `countDocuments` vs `estimatedDocumentCount`?
A3: `countDocuments(filter)` is accurate and runs an aggregation using the filter; `estimatedDocumentCount()` reads collection metadata, is very fast but takes no filter and can be slightly off (e.g., after unclean shutdown or in sharded clusters with orphans).

Q4: Can `distinct` use an index?
A4: Yes. An index on the field lets MongoDB read unique keys from the index (DISTINCT_SCAN) instead of fetching documents.

Q5: Why is `skip` pagination bad at scale?
A5: MongoDB still walks past all skipped documents, so deep pages are slow. Range pagination on an indexed field (`_id`) is O(page size).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Small or medium set of unique values (filters, dropdowns)
- You need only the values, not counts

❌ Avoid when:
- High-cardinality fields
- You need counts, sorting or further processing - use `$group`

---

## 📊 Visual Diagram
```
Documents                          distinct("city")
 {city: Delhi}  ─┐
 {city: Delhi}  ─┼──► dedupe on server ──► [ "Delhi", "Pune" ]
 {city: Pune}   ─┤
 {city: Pune}   ─┘

 distinct("tags") on tags:["a","b"],["b"],[]  ──►  [ "a", "b" ]
 $group + $sum    ──►  [ {Delhi:2}, {Pune:2} ]  (with counts)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| distinct | Unique values of a field | Field की unique values |
| Cardinality | Number of unique values | Unique values की संख्या |
| $group | Pipeline grouping stage | Grouping stage |
| Projection | Choose fields to return | Return होने वाले fields चुनना |
| Range pagination | Paginate using last seen key | आखिरी key से pagination |

---

## ⚡ 3-Line Summary
English:
1. `distinct(field, filter)` returns unique values (arrays are unwrapped).
2. Result is a single array under 16 MB and unsorted - not for high cardinality.
3. Use `$group` for counts or big data; use range pagination instead of large `skip`.

Hindi:
1. `distinct(field, filter)` unique values देता है (arrays खुल जाते हैं)।
2. Result एक array है, 16 MB से कम और unsorted - ज़्यादा cardinality के लिए नहीं।
3. Counts या बड़े data के लिए `$group`; बड़े `skip` की जगह range pagination।

---

## ➡️ Next Topic
**40. Null and Missing Fields Gotchas** - how `null`, missing and `$exists` behave differently.
