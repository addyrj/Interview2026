# 42. Single Field Index
# हिंदी में: Single Field Index

---

## 🔵 Simple Definition (English)
A **single field index** indexes one field of a collection: `createIndex({ field: 1 })` (ascending) or `-1` (descending). It supports equality, range and sort on that field. For a single-field index the direction does not matter for sorting, because MongoDB can read a B-tree forwards or backwards. It also works on nested fields with dot notation (`"address.city"`) and on embedded documents (matching the whole subdocument exactly).

## 🔵 सरल परिभाषा (Hindi)
**Single field index** collection की एक field पर index है: `createIndex({ field: 1 })` (ascending) या `-1` (descending)। यह उस field पर equality, range और sort को support करता है। Single-field index में sort के लिए direction मायने नहीं रखती, क्योंकि MongoDB B-tree को आगे या पीछे दोनों तरफ पढ़ सकता है। यह nested fields (`"address.city"`) और embedded documents (पूरे subdocument का exact match) पर भी चलता है।

---

## 🔴 Problem it Solves
The most common slow query is a filter or sort on one field (`email`, `userId`, `createdAt`). A single field index turns the COLLSCAN into an IXSCAN with minimal design effort and small storage cost.

## 🔴 यह क्यों बना? (Hindi)
सबसे आम slow query एक field (`email`, `userId`, `createdAt`) पर filter या sort होती है। Single field index थोड़े से प्रयास और कम storage में COLLSCAN को IXSCAN बना देता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Pick the field in your most frequent filter/sort: e.g. `userId`.
Step 2 → `db.orders.createIndex({ userId: 1 })` builds a sorted B-tree on that field.
Step 3 → Query `{ userId: 42 }` becomes an index lookup (keys examined = matches).
Step 4 → Range `{ userId: { $gte: 10, $lt: 20 } }` walks a contiguous key range.
Step 5 → `sort({ userId: -1 })` reuses the same index in reverse - no in-memory sort.
Step 6 → Nested field: `createIndex({ "address.city": 1 })` and query with `"address.city": "Pune"`.
Step 7 → Default index name is `field_1` / `field_-1`; give custom names with `{ name: "..." }`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → सबसे ज़्यादा इस्तेमाल होने वाले filter/sort की field चुनो: जैसे `userId`।
Step 2 → `db.orders.createIndex({ userId: 1 })` उस field पर sorted B-tree बनाता है।
Step 3 → Query `{ userId: 42 }` index lookup बन जाती है।
Step 4 → Range `{ userId: { $gte: 10, $lt: 20 } }` keys की continuous range चलती है।
Step 5 → `sort({ userId: -1 })` वही index उल्टा पढ़ता है - memory sort नहीं।
Step 6 → Nested field: `createIndex({ "address.city": 1 })` और query में `"address.city": "Pune"`।
Step 7 → Default नाम `field_1` / `field_-1`; custom नाम `{ name: "..." }` से।

---

## 🟡 Real World Example
**Zomato** looks up users by `phone` at login. `users.createIndex({ phone: 1 }, { unique: true })` gives instant login lookups and prevents two accounts with the same phone number.

## 🟡 Real Example Hindi mein
**Zomato** login पर users को `phone` से खोजता है। `users.createIndex({ phone: 1 }, { unique: true })` login lookup को तुरंत बनाता है और एक ही phone पर दो accounts भी रोकता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4), 5000 orders from the previous topic
use idx_demo

db.orders.createIndex({ userId: 1 })          // Output: 'userId_1'
db.orders.createIndex({ createdAt: -1 })      // descending; direction is irrelevant for a single-field sort
db.orders.createIndex({ "address.city": 1 })  // nested field with dot notation (quote it!)

// Equality: COLLSCAN -> IXSCAN
db.orders.find({ userId: 42 }).explain("executionStats").executionStats
// totalKeysExamined: 10, totalDocsExamined: 10, nReturned: 10

// Range + sort reusing the same index backwards
db.orders.find({ userId: { $gte: 10, $lt: 20 } }).sort({ userId: -1 }).explain("executionStats").executionStats
// totalKeysExamined: 100, totalDocsExamined: 100, nReturned: 100, no SORT stage
```

## 💻 Code Example — Advanced

```javascript
// Custom name and options
db.orders.createIndex({ status: 1 }, { name: "idx_status", background: true })
// "background" is ignored since MongoDB 4.2 (all builds use the optimized build process) - harmless

// Embedded document index matches the WHOLE subdocument, field order matters
db.shops.createIndex({ location: 1 })
db.shops.insertOne({ name: "A", location: { city: "Pune", pin: 411001 } })
db.shops.find({ location: { city: "Pune", pin: 411001 } })   // uses index (exact subdocument match)
db.shops.find({ location: { pin: 411001, city: "Pune" } })   // NO match: field order differs
// For individual subfields, index the dotted path instead: createIndex({ "location.city": 1 })

// Case-insensitive lookups need a collation index
db.users.createIndex({ email: 1 }, { collation: { locale: "en", strength: 2 } })
db.users.find({ email: "A@X.com" }).collation({ locale: "en", strength: 2 })  // must use same collation to use index
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const userSchema = new mongoose.Schema({
  email: { type: String, unique: true, index: true }, // unique index (creates { email: 1 } unique)
  phone: { type: String, index: true },               // plain single field index
  address: { city: { type: String, index: true } },   // nested path index "address.city"
});
const User = mongoose.model('User', userSchema);

app.get('/api/users/by-phone/:phone', async (req, res) => {
  const user = await User.findOne({ phone: req.params.phone }).lean(); // lean() -> plain object, faster
  user ? res.json(user) : res.status(404).json({ error: 'Not found' });
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting quotes around dotted fields
```javascript
// Wrong - SyntaxError in JavaScript
db.orders.createIndex({ address.city: 1 })
// Right
db.orders.createIndex({ "address.city": 1 })
```

❌ Mistake 2: Creating both `{ a: 1 }` and `{ a: 1, b: 1 }`
✅ Correct: the compound index already serves queries on the prefix `a` - drop the redundant single index.

❌ Mistake 3: Querying an embedded document with a different field order than the one stored/indexed.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.createIndex({ createdAt: 1 })
db.orders.find().sort({ createdAt: -1 }).limit(5)   // does it need a SORT stage?
```
Answer: No. A B-tree can be traversed backwards, so an ascending single-field index serves a descending sort with no in-memory sort. Direction matters only in compound indexes where multiple sort fields have mixed directions.

---

## ⚫ Interview Questions + Answers

Q1: Does ascending vs descending matter for a single field index?
A1: No for sorting; the index can be read in either direction.

Q2: How do you index a nested field?
A2: Use dot notation in quotes: `createIndex({ "address.city": 1 })`.

Q3: What happens if you index an embedded document directly?
A3: Queries must match the whole subdocument exactly, including field order, to use that index; usually index the specific subfields instead.

Q4: How do you list or remove indexes?
A4: `getIndexes()`, `dropIndex("name")`, `dropIndexes()`.

Q5: Does an index speed up `$regex`?
A5: Only a case-sensitive prefix regex (`/^abc/`) can bound the index range; unanchored or case-insensitive regex scans the whole index.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Frequent equality, range or sort queries on one field
- Lookups by unique identifiers (email, phone)

❌ Avoid when:
- Queries combine several fields - use a compound index
- The field has very low selectivity (e.g., boolean)

---

## 📊 Visual Diagram
```
createIndex({ userId: 1 })

 sorted keys:  1 -> 2 -> 3 -> ... -> 42 -> ... -> 500
                                     |
 find({userId:42})  ----------------┘  (10 pointers)  ->  10 documents
 sort({userId:-1})  ----------------->  read the same list backwards
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Single field index | Index on one field | एक field पर index |
| Dot notation | Path to nested field | Nested field का path |
| Collation | Language/case rules | Language/case नियम |
| Selectivity | How narrow the filter is | Filter कितना narrow है |
| Prefix | Leading fields of an index | Index की शुरुआती fields |

---

## ⚡ 3-Line Summary
English:
1. `createIndex({ field: 1 })` speeds up equality, range and sort on one field.
2. Direction is irrelevant for single-field sorts; quote dotted paths.
3. Avoid redundant indexes; compound indexes cover their prefixes.

Hindi:
1. `createIndex({ field: 1 })` एक field पर equality, range और sort तेज़ करता है।
2. Single-field sort में direction मायने नहीं रखती; dotted paths को quotes में लिखो।
3. Redundant indexes से बचो; compound index अपने prefix को भी cover करता है।

---

## ➡️ Next Topic
**43. Compound Index + ESR Rule**
