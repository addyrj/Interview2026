# 44. Multikey Indexes (arrays)
# हिंदी में: Multikey Indexes (arrays)

---

## 🔵 Simple Definition (English)
A **multikey index** is an index on a field that holds an **array**. MongoDB creates it automatically when you call `createIndex` on an array field - you do not declare it. It adds **one index entry per array element**, so a query like `{ tags: "t3" }` can find any document whose array contains `t3`. Limits: a compound index can include **at most one array field per document**.

## 🔵 सरल परिभाषा (Hindi)
**Multikey index** उस field पर index है जिसमें **array** है। `createIndex` array field पर करते ही MongoDB इसे अपने-आप multikey बना देता है। यह array के **हर element के लिए एक index entry** जोड़ता है, इसलिए `{ tags: "t3" }` जैसी query उन documents को ढूँढ लेती है जिनके array में `t3` है। सीमा: compound index में हर document में **एक से ज़्यादा array field नहीं** हो सकती।

---

## 🔴 Problem it Solves
Arrays (tags, categories, skills, items in cart) are everywhere in document models. Without a multikey index, "find all posts tagged `mongodb`" scans every document and every array. With one, each tag points directly to its documents.

## 🔴 यह क्यों बना? (Hindi)
Arrays (tags, categories, skills, cart items) document models में हर जगह होते हैं। Multikey index के बिना "tag `mongodb` वाले सब posts" हर document और हर array scan करता है। Index के साथ हर tag सीधे अपने documents की ओर जाता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Document `{ _id: 1, tags: ["t0", "t3"] }`.
Step 2 → `createIndex({ tags: 1 })` inserts an entry for `t0` and another for `t3`, both pointing to `_id: 1`.
Step 3 → `find({ tags: "t3" })` does an IXSCAN on the `t3` key; `explain` shows `isMultiKey: true`.
Step 4 → `$all`, `$in`, `$elemMatch` and `$size`-free queries use the entries; `$size` alone does not.
Step 5 → Compound multikey: `{ a: 1, tags: 1 }` is allowed (one array field). If two indexed fields are arrays in the same document, the insert fails ("cannot index parallel arrays", verified).
Step 6 → An array of subdocuments can be indexed through dotted paths: `createIndex({ "items.sku": 1 })`.
Step 7 → A multikey index can return the same document via multiple keys, but MongoDB deduplicates before returning. Multikey indexes cannot be covering for array fields' full value.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Document `{ _id: 1, tags: ["t0", "t3"] }`।
Step 2 → `createIndex({ tags: 1 })` `t0` और `t3` की अलग entries बनाता है, दोनों `_id: 1` की ओर।
Step 3 → `find({ tags: "t3" })` `t3` key पर IXSCAN करता है; `explain` में `isMultiKey: true` दिखता है।
Step 4 → `$all`, `$in`, `$elemMatch` इन entries का use करते हैं।
Step 5 → Compound multikey: `{ a: 1, tags: 1 }` allowed है (एक array field)। एक ही document में दो indexed fields array हों तो insert fail ("cannot index parallel arrays", verified)।
Step 6 → Subdocuments के array को dotted path से index करो: `createIndex({ "items.sku": 1 })`।
Step 7 → एक document कई keys से मिल सकता है, पर MongoDB return से पहले dedupe करता है।

---

## 🟡 Real World Example
**Flipkart** products carry `tags: ["5g", "amoled", "128gb"]`. A multikey index on `tags` powers filter chips: "show products tagged 5g". **Zomato** restaurant docs have `cuisines: ["North Indian", "Chinese"]`; the multikey index lets "Chinese" searches find all restaurants listing it.

## 🟡 Real Example Hindi mein
**Flipkart** products में `tags: ["5g", "amoled", "128gb"]` होते हैं। `tags` पर multikey index filter chips ("5g tag वाले products") चलाता है। **Zomato** के restaurant docs में `cuisines: ["North Indian", "Chinese"]` होता है; multikey index से "Chinese" search हर उस restaurant को ढूँढती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4). 5000 orders with tags ["t0".."t4", "t0".."t6"]
use idx_demo
db.orders.createIndex({ tags: 1 })     // Output: 'tags_1'  (becomes multikey because tags is an array)

const e = db.orders.find({ tags: "t3" }).explain("executionStats")
e.queryPlanner.winningPlan.inputStage.isMultiKey   // Output: true
e.executionStats.totalKeysExamined                 // Output: 1571  (one key per matching element)
e.executionStats.nReturned                         // Output: 1571

// Query operators that use the multikey index
db.orders.find({ tags: { $all: ["t1", "t2"] } })          // has both tags
db.orders.find({ tags: { $in: ["t1", "t9"] } })           // has any of the tags
db.orders.find({ tags: { $elemMatch: { $gte: "t1", $lt: "t3" } } }) // one element satisfies both bounds
```

## 💻 Code Example — Advanced

```javascript
// Parallel arrays restriction
db.bad.createIndex({ a: 1, b: 1 })
db.bad.insertOne({ a: [1, 2], b: [3, 4] })
// Error: cannot index parallel arrays [b] [a]   <- verified (insert is rejected)

// Array of subdocuments: index a dotted path
db.carts.insertMany([
  { user: "u1", items: [{ sku: "P1", qty: 2 }, { sku: "P2", qty: 1 }] },
  { user: "u2", items: [{ sku: "P2", qty: 5 }] }
])
db.carts.createIndex({ "items.sku": 1 })
db.carts.find({ "items.sku": "P2" })   // both carts match, served by multikey IXSCAN

// $elemMatch for conditions on the SAME element
db.carts.find({ items: { $elemMatch: { sku: "P2", qty: { $gte: 5 } } } })   // only u2
// Without $elemMatch, {"items.sku":"P2","items.qty":{$gte:5}} could match different elements
// (sku P2 from one element and qty>=5 from another).

// Mix an ordinary field with ONE array field in a compound index
db.orders.createIndex({ status: 1, tags: 1 })   // OK, only one array field
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const productSchema = new mongoose.Schema({
  name: String,
  tags: [String],                       // array of strings
  items: [{ sku: String, qty: Number }] // array of subdocuments
});
productSchema.index({ tags: 1 });       // multikey automatically
productSchema.index({ 'items.sku': 1 });
const Product = mongoose.model('Product', productSchema);

// GET /api/products?tags=5g,amoled  -> products having ALL the tags
app.get('/api/products', async (req, res) => {
  const tags = (req.query.tags || '').split(',').filter(Boolean);
  const query = tags.length ? { tags: { $all: tags } } : {};
  res.json(await Product.find(query).limit(20));
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Matching two conditions on array subdocuments without `$elemMatch`
```javascript
// Wrong - may match different elements for sku and qty
db.carts.find({ "items.sku": "P2", "items.qty": { $gte: 5 } })
// Right
db.carts.find({ items: { $elemMatch: { sku: "P2", qty: { $gte: 5 } } } })
```

❌ Mistake 2: Compound index on two array fields (parallel arrays error).
✅ Correct: at most one array field per compound index; index the second separately.

❌ Mistake 3: Huge unbounded arrays - each element is an index entry, so big arrays make large indexes and slow writes.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.createIndex({ tags: 1 })
db.orders.find({ tags: "t3" }).explain("executionStats").executionStats.totalKeysExamined
// vs nReturned?
```
Answer: Both are `1571` here, because each document has `t3` at most once. If a document had `["t3","t3"]`, the index would contain duplicates for it, yet the result is deduplicated, so keys examined can exceed `nReturned`. Also note the index is "multikey" only after an array value is actually indexed.

---

## ⚫ Interview Questions + Answers

Q1: How do you create a multikey index?
A1: Just `createIndex` on an array field; MongoDB marks it multikey automatically and creates one entry per element.

Q2: What is the parallel arrays restriction?
A2: A compound index cannot have more than one indexed field holding an array in the same document; such an insert fails.

Q3: Why use `$elemMatch`?
A3: To require that multiple conditions hold on the same array element.

Q4: Can multikey indexes be covered queries?
A4: Not for the array field values themselves (the index stores elements, not whole arrays), so those queries still FETCH.

Q5: What is the downside?
A5: Index size and write cost grow with array length; avoid unbounded arrays.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Querying by elements inside bounded arrays (tags, roles, cuisines)

❌ Avoid when:
- Arrays grow unbounded (comments, logs) - model as a separate collection
- Need two array fields in one compound index

---

## 📊 Visual Diagram
```
doc1 tags:["t0","t3"]      Index entries (tags_1)
doc2 tags:["t3","t5"]      t0 -> doc1
doc3 tags:["t1"]           t1 -> doc3
                           t3 -> doc1, doc2     <- find({tags:"t3"}) reads this key
                           t5 -> doc2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Multikey | Index entry per array element | Array element के लिए entry |
| Parallel arrays | Two arrays in compound index | Compound index में दो arrays |
| $elemMatch | Same-element match | एक ही element पर match |
| $all | Contains all values | सभी values मौजूद |
| isMultiKey | Explain flag | Explain में flag |

---

## ⚡ 3-Line Summary
English:
1. Indexing an array field automatically creates a multikey index with one entry per element.
2. Only one array field per compound index (parallel arrays error).
3. Use `$elemMatch` for same-element conditions; avoid unbounded arrays.

Hindi:
1. Array field पर index अपने-आप multikey बनता है, हर element की एक entry।
2. Compound index में सिर्फ एक array field (parallel arrays error)।
3. Same-element conditions के लिए `$elemMatch`; unbounded arrays से बचो।

---

## ➡️ Next Topic
**45. Unique, Sparse and Partial Indexes**
