# 57. $unwind
# हिंदी में: $unwind

---

## 🔵 Simple Definition (English)
**`$unwind`** takes an array field and outputs one document per array element, copying all other fields. An order with 2 items becomes 2 documents, each holding one item. It is the standard way to group, count or join on array contents.

## 🔵 सरल परिभाषा (Hindi)
**`$unwind`** किसी array field को लेकर हर element के लिए एक document देता है, बाकी सारे fields copy होते हैं। 2 items वाला order 2 documents बन जाता है, हर एक में एक item। Array के अंदर की values पर group, count या join करने का यही standard तरीका है।

---

## 🔴 Problem it Solves
`$group` cannot count individual array elements when they are packed inside one array. "Most ordered dish" needs every dish as its own row. `$unwind` flattens arrays so normal stages work on elements.

## 🔴 यह क्यों बना? (Hindi)
जब elements एक array में बंद हों तो `$group` उन्हें अलग-अलग नहीं गिन सकता। "सबसे ज़्यादा order होने वाली dish" के लिए हर dish अपनी row में चाहिए। `$unwind` arrays को flatten करता है ताकि normal stages elements पर चल सकें।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ $unwind: "$items" }` (path needs `$`).
Step 2 → For each input doc, one output doc per element; `items` becomes the single element (not an array).
Step 3 → By default, docs where the field is missing, null, or an empty array are DROPPED.
Step 4 → `preserveNullAndEmptyArrays: true` keeps them (field omitted for empty arrays).
Step 5 → `includeArrayIndex: "i"` adds the element's position (null for preserved empties).
Step 6 → After `$unwind`, usually `$group` back to aggregate.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `{ $unwind: "$items" }` (path में `$` ज़रूरी)।
Step 2 → हर input doc से हर element के लिए एक output doc; `items` अब array नहीं, अकेला element होता है।
Step 3 → Default में जिन docs में field missing, null या खाली array हो वो हट जाते हैं।
Step 4 → `preserveNullAndEmptyArrays: true` से वे रह जाते हैं (खाली array में field हट जाता है)।
Step 5 → `includeArrayIndex: "i"` element की position जोड़ता है (preserved खाली के लिए null)।
Step 6 → `$unwind` के बाद आमतौर पर `$group` से वापस aggregate करते हैं।

---

## 🟡 Real World Example
**Zomato's "most popular dishes"**: each order stores `items: ["biryani","raita"]`. `$unwind: "$items"` then `$group` by dish with `$sum: 1` gives dish popularity per city. Tags arrays (`["veg","spicy"]`) on menu items use the same trick.

## 🟡 Real Example Hindi mein
**Zomato की "most popular dishes"**: हर order में `items: ["biryani","raita"]` होता है। `$unwind: "$items"` फिर dish से `$group` और `$sum: 1` से city-wise popularity मिलती है। Menu items के tags arrays (`["veg","spicy"]`) पर भी यही trick चलती है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders
db.orders.aggregate([
  { $match: { _id: { $in: [1, 3, 6] } } },         // order 6 has an EMPTY items array
  { $unwind: "$items" },                           // one doc per item
  { $project: { customer: 1, items: 1 } }
])
// Output (real) — order 6 vanished because its array is empty:
// { _id: 1, customer: 'Aarav', items: 'biryani' }
// { _id: 1, customer: 'Aarav', items: 'raita' }
// { _id: 3, customer: 'Aarav', items: 'tea' }
// { _id: 3, customer: 'Aarav', items: 'samosa' }
```

## 💻 Code Example — Advanced

```javascript
// Keep empty-array docs and record the position
db.orders.aggregate([
  { $match: { _id: 6 } },
  { $unwind: { path: "$items", preserveNullAndEmptyArrays: true, includeArrayIndex: "i" } }
])
// Output (real): { _id: 6, customer: 'Meera', city: 'Pune', status: 'pending',
//                  amount: 75, ts: ISODate('2025-02-04T00:00:00.000Z'), i: null }
// (no "items" field at all; i is null)

// Popularity: unwind then group
db.orders.aggregate([
  { $unwind: "$items" },
  { $group: { _id: "$items", n: { $sum: 1 } } },
  { $sort: { n: -1, _id: 1 } },                    // _id breaks ties so output is repeatable
  { $limit: 3 }
])
// Output (real): { _id: 'biryani', n: 1 }, { _id: 'coke', n: 1 }, { _id: 'dosa', n: 1 }
// (every dish appears once in this tiny sample)
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/stats/dishes — top dishes (Mongoose, tested on mongod 8.0.4)
app.get("/api/stats/dishes", async (req, res) => {
  const rows = await Order.aggregate([
    { $unwind: "$items" },                         // one row per dish ordered
    { $sortByCount: "$items" },                    // group + count + sort desc in one stage
    { $limit: 5 }
  ]);
  res.json(rows);                                  // e.g. [{ _id: "tea", count: 1 }, ...] (all counts are 1 in the sample, tie order varies)
});
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Forgetting `$` in the path
```javascript
{ $unwind: "items" }    // Wrong — error: path must be prefixed with $
{ $unwind: "$items" }   // Right
```

❌ Mistake 2: Silently losing documents
✅ Empty/missing arrays are dropped by default. Use `preserveNullAndEmptyArrays: true` if the parent must survive (we saw order 6 vanish).

❌ Mistake 3: Unwinding then summing parent fields
✅ After unwinding an order with 2 items, `amount` is duplicated in 2 rows. `$sum: "$amount"` would double count. Sum parent values BEFORE unwinding or use `$addToSet` carefully.

---

## 🧠 Tricky Interview Question
Q: Order 1 has amount 450 and 2 items. After `$unwind: "$items"` and `$group: {_id:null, t:{$sum:"$amount"}}` what is the contribution of order 1?
Answer: 900 (450 counted twice) because unwind duplicated the order once per item. This is the classic double-counting bug. Compute totals before `$unwind`, or group by `_id` first.

---

## ⚫ Interview Questions + Answers

Q1: What does `$unwind` do to an array of N elements?
A1: Produces N documents; the field holds one element in each.

Q2: What happens to a non-array value?
A2: Since 3.2 a non-array, non-null, non-missing operand is treated as a single-element array.

Q3: How to keep documents with empty arrays?
A3: `preserveNullAndEmptyArrays: true`.

Q4: How can you avoid unwind for simple array math?
A4: Use array expressions: `$size`, `$filter`, `$map`, `$reduce`, `$sum` on arrays, which avoid multiplying documents.

Q5: How does `$unwind` pair with `$lookup`?
A5: `$lookup` returns an array; `$unwind` turns it into a single embedded object (inner-join behaviour when empties are dropped).

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Counting or grouping by array elements (tags, items, categories)
- Flattening `$lookup` results

❌ Avoid when:
- `$size`, `$filter`, `$map` can answer without exploding documents
- Arrays are huge (output multiplies)

---

## 📊 Visual Diagram
```
 { _id:1, items:["biryani","raita"] }
              │  $unwind "$items"
              ▼
 { _id:1, items:"biryani" }
 { _id:1, items:"raita"   }

 { _id:6, items:[] }  ──►  dropped (unless preserveNullAndEmptyArrays)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$unwind` | Array to many docs | Array को कई docs में बदलना |
| `path` | Array field to unwind | Unwind होने वाला field |
| `preserveNullAndEmptyArrays` | Keep docs with no elements | बिना elements वाले docs रखना |
| `includeArrayIndex` | Adds element position | Element की position जोड़ना |
| Double counting | Parent values repeated | Parent values का दोहराव |
| `$sortByCount` | Group + count + sort | Group, गिनती, sort एक साथ |

---

## ⚡ 3-Line Summary
English:
1. `$unwind` makes one document per array element.
2. Empty or missing arrays are dropped unless you set `preserveNullAndEmptyArrays`.
3. Beware double counting parent fields after unwinding.

Hindi:
1. `$unwind` हर array element के लिए एक document बनाता है।
2. खाली या missing arrays हट जाते हैं जब तक `preserveNullAndEmptyArrays` न लगाओ।
3. Unwind के बाद parent fields का double counting से सावधान रहो।

---

## ➡️ Next Topic
**58. $lookup — Joins in MongoDB** — pulling related documents from another collection.
