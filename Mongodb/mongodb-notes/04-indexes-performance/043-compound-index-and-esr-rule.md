# 43. Compound Index + ESR Rule
# हिंदी में: Compound Index और ESR Rule

---

## 🔵 Simple Definition (English)
A **compound index** covers multiple fields in a defined order, e.g. `{ status: 1, city: 1, amount: 1 }`. It is sorted by the first field, then by the second within equal first values, and so on. The **ESR rule** tells you how to order fields: **E**quality fields first, then **S**ort fields, then **R**ange fields. Index **prefixes** (`status`; `status + city`) can also be used, but not a later field alone.

## 🔵 सरल परिभाषा (Hindi)
**Compound index** कई fields को तय क्रम में cover करता है, जैसे `{ status: 1, city: 1, amount: 1 }`। यह पहली field से sorted होता है, फिर बराबर पहली value के अंदर दूसरी field से, आदि। **ESR rule** बताता है fields का क्रम: पहले **E**quality fields, फिर **S**ort fields, फिर **R**ange fields। Index के **prefixes** (`status`; `status + city`) भी use हो सकते हैं, पर बाद वाली field अकेली नहीं।

---

## 🔴 Problem it Solves
Real queries filter on several fields and sort on another. Separate single indexes cannot be combined efficiently (MongoDB typically uses one index per query), so the planner picks one and scans/filters the rest. A well-ordered compound index lets one IXSCAN satisfy the filter AND the sort.

## 🔴 यह क्यों बना? (Hindi)
असली queries कई fields पर filter और किसी दूसरी पर sort करती हैं। अलग-अलग single indexes को मिलाया नहीं जा सकता (आम तौर पर एक query में एक index), इसलिए planner एक चुनकर बाकी को scan/filter करता है। सही क्रम वाला compound index एक ही IXSCAN में filter और sort दोनों पूरे करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Index `{ status: 1, city: 1, amount: 1 }` stores entries sorted by status, then city, then amount.
Step 2 → Equality on `status` and `city` pins one contiguous slice of the index.
Step 3 → Within that slice, entries are already sorted by `amount`, so `sort({ amount: 1 })` needs **no** SORT stage.
Step 4 → Prefix rule: queries on `status` or `status + city` use the index; a query on `city` alone cannot (COLLSCAN, verified).
Step 5 → ESR: Equality first (narrow), Sort next (avoid in-memory sort), Range last (a range breaks the ordering for later fields).
Step 6 → Direction matters in compound indexes: `sort({a:1,b:-1})` needs index `{a:1,b:-1}` (or its exact reverse `{a:-1,b:1}`).
Step 7 → Verify with `explain()` and compare keys/docs examined with `nReturned`.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Index `{ status: 1, city: 1, amount: 1 }` entries को status, फिर city, फिर amount से sorted रखता है।
Step 2 → `status` और `city` पर equality से index का एक continuous slice मिलता है।
Step 3 → उस slice में entries पहले से `amount` से sorted हैं, इसलिए `sort({ amount: 1 })` को SORT stage **नहीं** चाहिए।
Step 4 → Prefix rule: `status` या `status + city` की query index use करती है; सिर्फ `city` की नहीं (COLLSCAN, verified)।
Step 5 → ESR: Equality पहले (narrow), Sort अगला (memory sort से बचाव), Range अंत में (range बाद की fields का ordering तोड़ देती है)।
Step 6 → Compound index में direction मायने रखती है: `sort({a:1,b:-1})` के लिए `{a:1,b:-1}` (या उसका exact उल्टा) चाहिए।
Step 7 → `explain()` से keys/docs examined की `nReturned` से तुलना करो।

---

## 🟡 Real World Example
**Swiggy's** order dashboard: "show all `paid` orders in `Delhi`, sorted by `amount`". Query = equality on `status`, equality on `city`, sort on `amount`. The index `{ status: 1, city: 1, amount: 1 }` serves it with no in-memory sort. Support agents also filter by `status` only - the index prefix handles that, so no extra index is needed.

## 🟡 Real Example Hindi mein
**Swiggy** का order dashboard: "Delhi के सभी `paid` orders, `amount` से sorted"। Query = `status` पर equality, `city` पर equality, `amount` पर sort। Index `{ status: 1, city: 1, amount: 1 }` बिना memory sort के यह पूरा करता है। Support agents सिर्फ `status` से भी filter करते हैं - prefix से यह हो जाता है, अलग index नहीं चाहिए।

---

## 💻 Code Example — Basic

```javascript
// mongosh (verified on MongoDB 8.0.4). 5000 orders: statuses new/paid/shipped, cities Delhi/Pune/Mumbai/Goa
use idx_demo
db.orders.createIndex({ status: 1, city: 1, amount: 1 })   // E, E, S  (equality, equality, sort)

// 1) Full ESR match: filter + sort from the index
db.orders.find({ status: "paid", city: "Delhi" }).sort({ amount: 1 }).explain("executionStats")
// Plan: FETCH > IXSCAN(status_1_city_1_amount_1)   keys 417, docs 417, returned 417  <- no SORT stage

// 2) Prefix use: status only
db.orders.find({ status: "paid" }).sort({ amount: 1 })
// Plan: FETCH > SORT > IXSCAN  keys 1667 (index used for the filter; sorting amount NOT possible from the index because city sits between)

// 3) Skipping the first field: index is NOT usable
db.orders.find({ city: "Delhi" })
// Plan: COLLSCAN  keys 0, docs 5000, returned 1250
```

## 💻 Code Example — Advanced

```javascript
// ESR with a range and an $in: compare two field orders (both verified)
// Query: status = paid, city in (Delhi, Pune), sort by amount
db.orders.createIndex({ status: 1, amount: 1, city: 1 })     // E, S, (city as filter)

// Order E, E, S -> {status, city, amount}: $in on city = two index ranges, so MongoDB merges them
db.orders.find({ status: "paid", city: { $in: ["Delhi", "Pune"] } })
  .hint({ status: 1, city: 1, amount: 1 }).sort({ amount: 1 })
// Plan: FETCH > SORT_MERGE   keys 834  docs 834  returned 834  (merges two sorted ranges, no full blocking sort)

// Order E, S, R -> {status, amount, city}: one IXSCAN, sorted by amount straight from the index
db.orders.find({ status: "paid", city: { $in: ["Delhi", "Pune"] } })
  .hint({ status: 1, amount: 1, city: 1 }).sort({ amount: 1 })
// Plan: FETCH > IXSCAN   keys 885  docs 834  returned 834   <- no SORT stage, fewer docs examined

// Trade-off: the second form scanned 885 keys (it must check city inside the index) vs 834 for the first.
// Plans vary with data and version - always explain on YOUR data.

// Mixed sort directions need a matching index
db.orders.createIndex({ status: 1, amount: -1, createdAt: 1 })
// supports sort({status:1, amount:-1, createdAt:1}) and its exact reverse, but not sort({amount:1, createdAt:1})
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
const orderSchema = new mongoose.Schema({ status: String, city: String, amount: Number });
// ESR order: equality fields (status, city), then sort field (amount)
orderSchema.index({ status: 1, city: 1, amount: 1 });
const Order = mongoose.model('Order', orderSchema);

app.get('/api/orders', async (req, res) => {
  const { status, city } = req.query;
  const orders = await Order.find({ status, city }).sort({ amount: 1 }).limit(50); // served by one IXSCAN
  res.json(orders);
});

// Debug in Mongoose: .explain('executionStats')
// const plan = await Order.find({ status, city }).sort({ amount: 1 }).explain('executionStats');
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Putting the range field before the sort field
```javascript
// Wrong - range on amount first, then sort by createdAt -> in-memory sort
db.orders.createIndex({ status: 1, amount: 1, createdAt: 1 })
db.orders.find({ status: "paid", amount: { $gt: 50 } }).sort({ createdAt: 1 })
// Right (ESR) - equality, sort, range
db.orders.createIndex({ status: 1, createdAt: 1, amount: 1 })
```

❌ Mistake 2: Expecting `{ a:1, b:1 }` to serve a query on `b` alone
✅ Correct: only prefixes (`a`; `a,b`) work. Create `{ b: 1 }` separately if needed.

❌ Mistake 3: Too many fields in one index - large indexes slow writes and use RAM.

---

## 🧠 Tricky Interview Question

```javascript
db.orders.createIndex({ status: 1, city: 1, amount: 1 })
db.orders.find({ status: "paid" }).sort({ amount: 1 })
```
Answer: The index is used for the filter on `status` (prefix), but the sort on `amount` cannot be satisfied from the index because `city` sits between them and varies across the slice, so MongoDB adds a SORT stage (verified: FETCH > SORT > IXSCAN, 1667 keys). You would need `{ status: 1, amount: 1 }` for index-ordered output.

---

## ⚫ Interview Questions + Answers

Q1: State the ESR rule.
A1: Order compound index fields as Equality, Sort, Range. Equality narrows to a contiguous slice, sort keeps results ordered, and range last because it breaks ordering for later fields.

Q2: What is an index prefix?
A2: The leading fields of a compound index. `{a,b,c}` supports queries on `a`, `a+b`, `a+b+c`, not `b` or `c` alone.

Q3: Does direction matter in compound indexes?
A3: Yes for sorts on multiple fields: the sort pattern must match the index or its exact reverse.

Q4: How many indexes can one query use?
A4: Normally one index per query (plus `$or` can use one per clause; index intersection exists but is rarely chosen).

Q5: Can you have more than one multikey field in a compound index?
A5: No, at most one array field per compound index entry (inserting a doc with two arrays in the indexed fields errors: "cannot index parallel arrays", verified).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Queries filter on multiple fields and/or filter plus sort
- You can design around ESR

❌ Avoid when:
- Fields are rarely queried together
- Index grows huge compared to the benefit

---

## 📊 Visual Diagram
```
Index {status, city, amount} (sorted entries)

 new   | Delhi | 5
 paid  | Delhi | 3   <---- find({status:"paid", city:"Delhi"}) lands here
 paid  | Delhi | 9        entries already sorted by amount -> sort free
 paid  | Goa   | 2   <---- (city varies, so sort({amount}) with only status = SORT stage)
 paid  | Pune  | 7
 shipped | ...

 ESR:   Equality(status, city)  ->  Sort(amount)  ->  Range(last)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Compound index | Index on multiple fields | कई fields पर index |
| ESR | Equality, Sort, Range order | Equality, Sort, Range क्रम |
| Prefix | Leading index fields | शुरुआती index fields |
| SORT stage | In-memory sort in plan | Memory में sort |
| hint() | Force an index | Index force करना |

---

## ⚡ 3-Line Summary
English:
1. A compound index sorts by field 1, then 2, then 3; only prefixes are usable.
2. Order fields Equality, Sort, Range (ESR) to avoid in-memory sorts.
3. Always confirm plans with `explain()`; they vary with data and version.

Hindi:
1. Compound index field 1, फिर 2, फिर 3 से sorted होता है; सिर्फ prefixes use होते हैं।
2. Fields को Equality, Sort, Range (ESR) क्रम में रखो ताकि memory sort न हो।
3. Plans की पुष्टि हमेशा `explain()` से करो; ये data और version से बदलते हैं।

---

## ➡️ Next Topic
**44. Multikey Indexes (arrays)**
