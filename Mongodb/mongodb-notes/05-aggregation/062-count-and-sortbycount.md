# 62. $count, $sortByCount
# हिंदी में: $count, $sortByCount

---

## 🔵 Simple Definition (English)
**`$count`** is a stage that counts the documents reaching it and outputs one document `{ <name>: N }`. **`$sortByCount`** groups by an expression, counts each group and sorts by count descending: a shortcut for `$group` + `$sum: 1` + `$sort`.

## 🔵 सरल परिभाषा (Hindi)
**`$count`** एक stage है जो अपने तक पहुँचे documents गिनता है और एक document `{ <name>: N }` देता है। **`$sortByCount`** किसी expression से group करता है, हर group गिनता है और count के हिसाब से घटते क्रम में sort करता है: `$group` + `$sum: 1` + `$sort` का shortcut।

---

## 🔴 Problem it Solves
Frequency questions ("orders per city", "how many delivered") are extremely common. Writing a three-stage pipeline each time is noisy. These two stages make counting one line, and the code is easier to read in reviews.

## 🔴 यह क्यों बना? (Hindi)
Frequency वाले सवाल ("city-wise orders", "कितने delivered") बहुत common हैं। हर बार तीन-stage pipeline लिखना भारी लगता है। ये दो stages गिनती को एक line का बना देते हैं और code review में पढ़ना आसान होता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ $count: "deliveredOrders" }` takes a field NAME (string), not a field path (no `$`).
Step 2 → Output is `{ deliveredOrders: 4 }`; if no documents arrive, NO document is output.
Step 3 → `{ $sortByCount: "$city" }` equals `$group {_id:"$city", count:{$sum:1}}` then `$sort {count:-1}`.
Step 4 → Output field names are `_id` (the value) and `count`.
Step 5 → Ties have no defined order; add `$sort` with `_id` if you need repeatable output.
Step 6 → For counts of a whole collection use `countDocuments()` or `estimatedDocumentCount()`, which are cheaper.

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → `{ $count: "deliveredOrders" }` में field का NAME (string) देते हैं, field path नहीं (`$` नहीं)।
Step 2 → Output `{ deliveredOrders: 4 }` होता है; अगर कोई document न आए तो कोई document output नहीं होता।
Step 3 → `{ $sortByCount: "$city" }` = `$group {_id:"$city", count:{$sum:1}}` फिर `$sort {count:-1}`।
Step 4 → Output fields `_id` (value) और `count` होते हैं।
Step 5 → बराबर counts का order तय नहीं; repeatable output चाहिए तो `_id` के साथ `$sort` लगाओ।
Step 6 → पूरी collection की गिनती के लिए `countDocuments()` या `estimatedDocumentCount()` सस्ते हैं।

---

## 🟡 Real World Example
**Swiggy's ops dashboard** shows "orders by status" (delivered, cancelled, pending) sorted by size using `$sortByCount: "$status"`, and a KPI card "delivered today" using `$match` + `$count`.

## 🟡 Real Example Hindi mein
**Swiggy का ops dashboard** `$sortByCount: "$status"` से "status के हिसाब से orders" (delivered, cancelled, pending) बड़े से छोटे क्रम में दिखाता है, और "आज delivered" KPI card `$match` + `$count` से बनता है।

---

## 💻 Code Example — Basic

```javascript
// mongosh, MongoDB 8.0.4, shop.orders
db.orders.aggregate([
  { $match: { status: "delivered" } },             // only delivered
  { $count: "deliveredOrders" }                    // name of the output field
])
// Output (real): { deliveredOrders: 4 }

db.orders.aggregate([ { $sortByCount: "$city" } ]) // count orders per city, biggest first
// Output (real):
// { _id: 'Mumbai', count: 3 }
// { _id: 'Delhi',  count: 2 }
// { _id: 'Pune',   count: 1 }
```

## 💻 Code Example — Advanced

```javascript
// Equivalent long form of $sortByCount (same result)
db.orders.aggregate([
  { $group: { _id: "$city", count: { $sum: 1 } } },
  { $sort: { count: -1, _id: 1 } }                 // _id tiebreaker makes it repeatable
])

// Count with a missing result handled in Node
const r = await db.collection("orders").aggregate([
  { $match: { city: "Nowhere" } },
  { $count: "n" }
]).toArray();
const n = r[0]?.n ?? 0;                            // r is [] when nothing matched, so default to 0

// Simpler alternatives for plain counts
await db.collection("orders").countDocuments({ status: "delivered" }); // 4, exact, filter allowed
await db.collection("orders").estimatedDocumentCount();                // fast metadata count, no filter
```

---

## 🟠 Express.js / Mongoose Integration

```javascript
// GET /api/stats/status (Mongoose)
app.get("/api/stats/status", async (req, res) => {
  const rows = await Order.aggregate([{ $sortByCount: "$status" }]);
  res.json(rows);   // [{"_id":"delivered","count":4},{"_id":"cancelled","count":1},{"_id":"pending","count":1}] (tie order may vary)
});

// Mongoose shortcut for plain counts
const delivered = await Order.countDocuments({ status: "delivered" });  // 4
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using a `$` path in `$count`
```javascript
{ $count: "$n" }   // Wrong — error: the count field cannot be a $-prefixed path
{ $count: "n" }    // Right
```

❌ Mistake 2: Assuming `$count` returns 0 for empty input
✅ It returns no document. Handle `r[0]?.n ?? 0`.

❌ Mistake 3: Using aggregation to count a whole collection
✅ `estimatedDocumentCount()` / `countDocuments()` are faster and simpler.

---

## 🧠 Tricky Interview Question
Q: Does `$sortByCount: "$city"` need the `$`?
Answer: Yes, it takes an expression, so `"$city"` is a field path. `$count` is the opposite: it takes a plain output field NAME. Mixing them up is a frequent mistake. Also `$sortByCount` always names the count field `count`, you cannot rename it.

---

## ⚫ Interview Questions + Answers

Q1: What does `$sortByCount` expand to?
A1: `{ $group: { _id: <expr>, count: { $sum: 1 } } }` then `{ $sort: { count: -1 } }`.

Q2: Difference between `countDocuments` and `estimatedDocumentCount`?
A2: `countDocuments(filter)` is exact and runs an aggregation; `estimatedDocumentCount()` uses collection metadata, is fast, and takes no filter.

Q3: What if no documents reach `$count`?
A3: No output document.

Q4: Can `$sortByCount` take an object expression?
A4: Yes, any expression: `{ $sortByCount: { $toLower: "$city" } }`. For a compound key use `{ $sortByCount: { $mergeObjects: [{ c: "$city" }, { s: "$status" }] } }` (a bare `{ city: "$city" }` object is rejected). Real output: `{ _id: { c: 'Mumbai', s: 'delivered' }, count: 3 }`.

Q5: How to count array elements per group?
A5: `$unwind` first, or `$sum: { $size: "$items" }` inside `$group`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Quick frequency tables, dashboards, KPI cards

❌ Avoid when:
- A plain `countDocuments` is enough
- You need extra accumulators (use `$group`)

---

## 📊 Visual Diagram
```
 orders ──► $sortByCount "$city" ──► { Mumbai:3 } { Delhi:2 } { Pune:1 }

 orders ──► $match delivered ──► $count "deliveredOrders" ──► { deliveredOrders: 4 }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `$count` | Counts docs into a named field | नामित field में गिनती |
| `$sortByCount` | Group, count, sort desc | Group, गिनती, घटता sort |
| Frequency table | Value and its count | Value और उसकी गिनती |
| `countDocuments` | Exact count helper | Exact गिनती helper |
| `estimatedDocumentCount` | Metadata-based count | Metadata से अनुमानित गिनती |
| Tiebreaker | Extra sort key for ties | Ties के लिए अतिरिक्त key |

---

## ⚡ 3-Line Summary
English:
1. `$count: "name"` gives one doc with the total; `$sortByCount: "$field"` gives a frequency table.
2. `$count` outputs nothing for empty input, so default to 0 in code.
3. Use `countDocuments` for plain counts.

Hindi:
1. `$count: "name"` कुल गिनती वाला एक doc देता है; `$sortByCount: "$field"` frequency table देता है।
2. खाली input पर `$count` कुछ output नहीं करता, इसलिए code में default 0 रखो।
3. साधारण गिनती के लिए `countDocuments` इस्तेमाल करो।

---

## ➡️ Next Topic
**63. $unionWith and $merge/$out** — combining collections and saving pipeline results.
