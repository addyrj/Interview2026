# 179. Group By in Array
# हिंदी में: Array में Group By करना — Items को Key के हिसाब से Buckets में बाँटना

---

## 🔵 Simple Definition (English)
"Group By" means taking a list of items and splitting them into buckets, where every item in a bucket shares the same key (like restaurant name, category, or city). The result is an object or Map where each key points to an array of matching items.

## 🔵 सरल परिभाषा (Hindi)
"Group By" का मतलब है किसी list के items को एक common key (जैसे restaurant का नाम, category या शहर) के हिसाब से अलग-अलग buckets में बाँट देना। नतीजा एक object या Map होता है, जहाँ हर key के सामने उसी key वाले items की array होती है।

---

## 🔴 Problem it Solves
**Problem Statement:** Given an array of objects and a key (or a function that computes a key), return an object where each group key maps to the array of items that produced it.

Example: 5 Zomato orders come in. The dashboard needs them grouped by restaurant name.

Without grouping, the code has to loop over the whole list again for every restaurant. That means more code, more bugs, and more time. One pass that builds buckets solves it cleanly.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** किसी array of objects और एक key (या key निकालने वाला function) दिया हो, तो एक object लौटाओ जिसमें हर group key के सामने उन items की array हो जो उस key पर आते हैं।

मान लो Zomato का admin dashboard चाहता है कि आज के सारे orders restaurant के हिसाब से दिखें। Grouping के बिना हर restaurant के लिए पूरी list दोबारा loop करनी पड़ती है। एक pass में grouping करने से code छोटा, साफ़ और तेज़ रहता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty result object (or Map) to hold the buckets.
Step 2 → Loop over every item in the array, once.
Step 3 → Read the group key from the item (for example `item.restaurant`).
Step 4 → If that key has no bucket yet, create an empty array for it.
Step 5 → Push the current item into the bucket for its key.
Step 6 → After the loop ends, return the result object.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक खाली result object (या Map) बनाओ जिसमें buckets रखे जाएँ।
Step 2 → Array के हर item पर एक बार loop चलाओ।
Step 3 → हर item से group key निकालो (जैसे `item.restaurant`)।
Step 4 → अगर उस key का bucket अभी नहीं है, तो उसके लिए खाली array बनाओ।
Step 5 → मौजूदा item को उसी key के bucket में push कर दो।
Step 6 → Loop खत्म होने पर result object return कर दो।

---

## 🟡 Real World Example
Swiggy and Zomato admin panels group orders by restaurant, city, or status. Razorpay groups transactions by merchant for settlement reports. Amazon sellers see sales grouped by SKU. All of these are the same problem: "one pass, buckets by key".

Scenario: A Zomato partner dashboard receives 5 orders in one minute. It must show how many orders each restaurant got and how much each restaurant earned. Grouping by restaurant name is step one, and then `reduce` on each bucket gives the totals.

## 🟡 Real Example Hindi mein
Swiggy और Zomato के admin panel orders को restaurant, शहर या status के हिसाब से group करते हैं। Razorpay settlement reports के लिए transactions को merchant के हिसाब से group करता है। Amazon seller को SKU के हिसाब से sales दिखाता है। ये सब एक ही तरीका है: "एक pass में key के हिसाब से buckets बनाओ"।

उदाहरण: एक Zomato partner dashboard में एक मिनट में 5 orders आते हैं। Dashboard को हर restaurant के orders की गिनती और कुल कमाई दिखानी है। पहला कदम है restaurant के नाम से group करना, फिर हर bucket पर `reduce` से totals निकालना।

---

## 💻 Code Example — Basic
```javascript
// Sample data: orders coming into a Zomato-style partner dashboard
const orders = [
  { id: 1, restaurant: "Burger King", amount: 250 },   // order 1
  { id: 2, restaurant: "Domino's", amount: 480 },      // order 2
  { id: 3, restaurant: "Burger King", amount: 180 },   // order 3
  { id: 4, restaurant: "Biryani Blues", amount: 620 }, // order 4
  { id: 5, restaurant: "Domino's", amount: 300 },      // order 5
];

// Basic groupBy: takes an array and the NAME of the key to group by
function groupBy(arr, key) {
  const result = {};                       // empty object that will hold the buckets
  for (const item of arr) {                // visit every item exactly once
    const groupKey = item[key];            // read the group value, e.g. "Domino's"
    if (!result[groupKey]) {               // no bucket for this key yet?
      result[groupKey] = [];               // create an empty array as the bucket
    }
    result[groupKey].push(item);           // put the item into its bucket
  }
  return result;                           // return the grouped object
}

// Use it: group orders by restaurant
const byRestaurant = groupBy(orders, "restaurant");

// Print the keys (object keys keep insertion order for string keys)
console.log(Object.keys(byRestaurant).join(", "));
// Expected output: Burger King, Domino's, Biryani Blues

// Count how many orders each restaurant received
console.log(byRestaurant["Burger King"].length); // Expected output: 2
console.log(byRestaurant["Domino's"].length);    // Expected output: 2
```

## 💻 Code Example — Advanced
```javascript
// Advanced groupBy: accepts a key NAME or a FUNCTION, uses Map, validates input
function groupByAdvanced(arr, keyOrFn) {
  // Guard: fail fast with a clear message if the first argument is not an array
  if (!Array.isArray(arr)) {
    throw new TypeError("groupBy: first argument must be an array");
  }
  // Build a key getter: a function is used as-is, a string becomes a property read
  const getKey = typeof keyOrFn === "function"
    ? keyOrFn                              // caller gave a function like o => o.amount > 300
    : (item) => item[keyOrFn];             // caller gave "restaurant" -> read item.restaurant

  const groups = new Map();                // Map keeps insertion order and allows ANY key type
  for (const item of arr) {                // single pass over the data
    const k = getKey(item);                // compute the group key for this item
    if (!groups.has(k)) {                  // first time we meet this key?
      groups.set(k, []);                   // create its bucket
    }
    groups.get(k).push(item);              // append the item to its bucket
  }
  // Convert the Map to a plain object only at the end, for printing or JSON
  return Object.fromEntries(groups);
}

// Group by a computed key: "premium" (amount > 300) or "regular"
const byTier = groupByAdvanced(orders, (o) => (o.amount > 300 ? "premium" : "regular"));

// Show only the order ids inside each tier
const tierIds = Object.fromEntries(
  Object.entries(byTier).map(([tier, list]) => [tier, list.map((o) => o.id)])
);
console.log(JSON.stringify(tierIds));
// Expected output: {"regular":[1,3,5],"premium":[2,4]}

// Aggregate: total revenue per restaurant, using reduce on each bucket
const revenue = Object.fromEntries(
  Object.entries(groupByAdvanced(orders, "restaurant")).map(([name, list]) => [
    name,
    list.reduce((sum, o) => sum + o.amount, 0), // add up the amounts in this bucket
  ])
);
console.log(JSON.stringify(revenue));
// Expected output: {"Burger King":430,"Domino's":780,"Biryani Blues":620}

// Time:  O(n) — one pass; Map get/set are O(1) on average
// Space: O(n) — the buckets together hold every item once
```

### Edge Cases
```javascript
// Edge 1: empty input gives an empty object
const empty = Object.fromEntries(new Map()); // no groups at all
console.log(JSON.stringify(empty));          // Expected output: {}

// Edge 2: a missing key becomes a bucket named "undefined"
const missing = Object.fromEntries(new Map([[undefined, [{ a: 1 }]]]));
console.log(Object.keys(missing).join());    // Expected output: undefined

// Edge 3: plain object keys are strings, so 1 and "1" collapse into one key
console.log(Object.keys({ 1: "num", "1": "str" }).length); // Expected output: 1

// Edge 4: a Map keeps 1 and "1" as two different keys
console.log(new Map([[1, "num"], ["1", "str"]]).size);     // Expected output: 2
```

---

## 🟠 Express.js Integration
Expose the grouping logic as an API. The route validates the field name (never trust the query), then groups the data and returns JSON.

```javascript
// Express.js: expose groupBy as a REST endpoint
const express = require("express");          // import the Express framework
const app = express();                       // create the Express application
app.use(express.json());                     // parse JSON request bodies into req.body

// Pretend database: in a real app these rows come from MongoDB or PostgreSQL
const orders = [
  { id: 1, restaurant: "Burger King", amount: 250 },
  { id: 2, restaurant: "Domino's", amount: 480 },
  { id: 3, restaurant: "Burger King", amount: 180 },
];

// Same groupBy idea as the basic example, written compactly
function groupBy(arr, key) {
  const result = {};                         // buckets object
  for (const item of arr) {                  // one pass over the data
    (result[item[key]] ??= []).push(item);   // create the bucket if missing, then push
  }
  return result;                             // grouped object
}

// POST /api/orders/group   body: { "by": "restaurant" }
app.post("/api/orders/group", (req, res) => {
  const { by } = req.body;                   // read the field to group by
  const allowed = ["restaurant", "amount"];  // whitelist: never group by arbitrary user input
  if (!allowed.includes(by)) {               // validate before using the value
    return res.status(400).json({ error: `by must be one of ${allowed.join(", ")}` }); // 400 Bad Request
  }
  res.json(groupBy(orders, by));             // 200 OK with the grouped JSON
});

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Grouping API running");       // printed once the server is ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Pushing into a bucket that was never created
```javascript
// Wrong: result[o.restaurant] is undefined the first time, so push() crashes
try {
  const result = {};                              // empty result
  for (const o of orders) {
    result[o.restaurant].push(o);                 // TypeError on the very first order
  }
} catch (e) {
  console.log(e.message);  // Expected output: Cannot read properties of undefined (reading 'push')
}

// Right: create the bucket if it is missing, then push
const right = {};                                 // fresh result
for (const o of orders) {
  (right[o.restaurant] ??= []).push(o);           // ??= assigns [] only when the bucket is null/undefined
}
console.log(right["Domino's"].length);            // Expected output: 2
```

❌ **Mistake 2:** Filling buckets with one shared array
```javascript
// Wrong: Array(2).fill([]) puts the SAME array reference in both slots
const shared = Array(2).fill([]);                 // both slots point to one array
shared[0].push("Burger King");                    // change slot 0...
console.log(shared[1]);                           // Expected output: [ 'Burger King' ] — slot 1 changed too!

// Right: create a NEW array for each bucket
const separate = Array.from({ length: 2 }, () => []); // a fresh [] per call of the arrow
separate[0].push("Burger King");                  // change slot 0 only
console.log(separate[1]);                         // Expected output: []
```

❌ **Mistake 3:** Using a plain object when keys may be numbers and strings
```javascript
// Wrong: a plain object turns both keys into the string "1"
const wrong = {};
for (const it of [{ k: 1 }, { k: "1" }]) (wrong[it.k] ??= []).push(it);
console.log(Object.keys(wrong).length);           // Expected output: 1 (two items merged!)

// Right: a Map keeps the value types distinct
const right2 = new Map();
for (const it of [{ k: 1 }, { k: "1" }]) {
  if (!right2.has(it.k)) right2.set(it.k, []);    // separate bucket per exact key
  right2.get(it.k).push(it);
}
console.log(right2.size);                         // Expected output: 2
```

---

## 🧠 Tricky Interview Question
```javascript
const items = [{ t: 1 }, { t: "1" }, { t: 2 }];  // note: 1 (number) and "1" (string)
const groups = {};                                // plain object

for (const it of items) {
  (groups[it.t] ??= []).push(it);                 // group by t
}

console.log(Object.keys(groups));                 // ?
console.log(groups["1"].length);                  // ?
```
Answer:
```
[ '1', '2' ]   ← both the number 1 and the string "1" became the key "1"
2              ← so the bucket "1" holds two items
```
Object property keys are always strings (or Symbols). The number `1` is converted to `"1"` before lookup, so `groups[1]` and `groups["1"]` are the same slot. A `Map` does not convert keys, which is why it is the safer choice for grouping by mixed-type values.

---

## ⚫ Interview Questions + Answers

**Q1: How would you group an array of objects by a property?**
A1: Create an empty object, loop once over the array, read `item[key]` as the group key, create an empty array if the bucket is missing, then push the item. Total time is O(n).

**Q2: Why use a Map instead of an object for grouping?**
A2: A Map keeps keys exactly as given (number `1` and string `"1"` stay different), allows any value as a key (objects, booleans, undefined), and keeps insertion order. An object converts keys to strings and can clash with inherited names like `constructor` or `toString`.

**Q3: What is the time and space complexity of groupBy?**
A3: Time O(n) because each item is visited once and Map operations are O(1) on average. Space O(n) because the buckets together store every item once.

**Q4: How do you group by a computed key, not just a property?**
A4: Pass a function instead of a string, for example `o => o.amount > 300 ? "premium" : "regular"`. The function returns the key for each item, and the rest of the algorithm stays the same.

**Q5: Does Array.prototype.reduce make grouping easier?**
A5: Yes, and it is a common one-liner: `arr.reduce((acc, o) => { (acc[o.restaurant] ??= []).push(o); return acc; }, {})`. It is the same algorithm written as a fold. Use the loop when readability matters more than brevity.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to show data in sections (orders by status, products by category)
- You aggregate per group next (totals, counts, averages)
- The data already fits in memory and you need the result right away

❌ Avoid when:
- The dataset is huge and lives in a database; use SQL `GROUP BY` instead so the database does the work
- You only need a count of distinct keys; a Set or a counting Map is lighter
- Keys can be mixed types and you use a plain object; use a Map

---

## 📊 Visual Diagram
```
INPUT ARRAY (one pass, left to right)            OUTPUT GROUPS
┌───────────────────────────────────┐           ┌───────────────────────────────┐
│ #1  Burger King    250            │ ───────►  │ "Burger King"   → [#1, #3]    │
│ #2  Domino's       480            │ ───────►  │ "Domino's"      → [#2, #5]    │
│ #3  Burger King    180            │ ───────►  │ "Biryani Blues" → [#4]        │
│ #4  Biryani Blues  620            │           └───────────────────────────────┘
│ #5  Domino's       300            │
└───────────────────────────────────┘
Each item: read key -> find bucket (create if new) -> push
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Group key | The value an item is grouped by | Group की key |
| Bucket | Array that holds items of one group | एक group की array |
| Accumulator | The result object built during the loop | जमा होता हुआ result |
| Map | Key-value store that keeps key types as they are | Keys को जैसा है वैसा रखने वाला structure |
| Coercion | Converting a key to a string in plain objects | Key को string में बदलना |
| Fold / reduce | Combine a list into one value step by step | List को एक value में समेटना |

---

## ⚡ 3-Line Summary
English:
1. Group By splits an array into buckets, one bucket per key, in a single pass.
2. Create the bucket with `??=` before you push, and use a Map when keys can be mixed types.
3. Time O(n), space O(n); for huge data, let the database do `GROUP BY`.

Hindi:
1. Group By एक pass में array को key के हिसाब से buckets में बाँटता है।
2. Push से पहले bucket `??=` से बनाओ, और mixed type की keys हों तो Map इस्तेमाल करो।
3. Time O(n), space O(n); बहुत बड़े data के लिए database का `GROUP BY` इस्तेमाल करो।

---

## 🧭 Next Topic
**180. Find Intersection of Arrays** — the next problem in this set. It uses the same Set and Map thinking to find values that two arrays share.
