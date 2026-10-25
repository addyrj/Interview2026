# 181. Remove Duplicates from Array
# हिंदी में: Array से Duplicates हटाना — हर Value को सिर्फ़ एक बार रखना

---

## 🔵 Simple Definition (English)
Removing duplicates means keeping only the first occurrence of each value in an array and dropping the repeats. For example, `[1, 2, 2, 3, 1]` becomes `[1, 2, 3]`. For objects, "duplicate" usually means the same key (like the same `id`), not the same reference.

## 🔵 सरल परिभाषा (Hindi)
Array से duplicates हटाने का मतलब है हर value की पहली occurrence रखना और बाकी repeats छोड़ देना। जैसे `[1, 2, 2, 3, 1]` बन जाएगा `[1, 2, 3]`। Objects के मामले में "duplicate" का मतलब आम तौर पर एक ही key (जैसे एक ही `id`) से है, एक ही reference से नहीं।

---

## 🔴 Problem it Solves
**Problem Statement:** Given an array, return a new array that contains each distinct value once, in the order of first appearance. For arrays of objects, return one object per unique key (for example, one per `id`).

Duplicates appear everywhere: a payment provider can send the same webhook twice, a user can click "Add to cart" twice, and a data import can contain the same row many times. Left alone, these cause double charges, double counts, and messy UI lists.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक array दिया हो, तो एक नई array लौटाओ जिसमें हर अलग value सिर्फ़ एक बार हो, पहली occurrence के order में। Objects की array हो तो हर unique key (जैसे हर `id`) के लिए एक object रखो।

Duplicates हर जगह आते हैं: payment provider एक ही webhook दो बार भेज सकता है, user दो बार "Add to cart" दबा सकता है, और data import में एक ही row कई बार हो सकती है। इन्हें न रोका जाए तो double charge, गलत गिनती और UI में गड़बड़ होती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty result array and an empty Set called `seen`.
Step 2 → Walk through the input array from left to right.
Step 3 → For each value, check whether `seen` already has it.
Step 4 → If not, add the value to `seen` and to the result.
Step 5 → If yes, skip it. This keeps the first occurrence only.
Step 6 → Return the result array.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक खाली result array और एक खाली Set `seen` बनाओ।
Step 2 → Input array को बाएँ से दाएँ देखो।
Step 3 → हर value के लिए check करो कि `seen` में वो पहले से है या नहीं।
Step 4 → अगर नहीं है, तो value को `seen` और result दोनों में डाल दो।
Step 5 → अगर है, तो उसे छोड़ दो। इससे सिर्फ़ पहली occurrence बचती है।
Step 6 → Result array return कर दो।

---

## 🟡 Real World Example
Razorpay and Stripe send webhooks that may arrive more than once. The server must process each `event.id` only once, or a payment could be marked captured twice. Amazon's cart merges duplicate SKUs into one line. Swiggy's import of partner menus removes repeated dish rows before saving.

Scenario: A payment gateway sends a batch of three events, and two of them have the same id `evt_1`. The server should process two unique events and report one duplicate.

## 🟡 Real Example Hindi mein
Razorpay और Stripe ऐसे webhooks भेजते हैं जो एक से ज़्यादा बार आ सकते हैं। Server को हर `event.id` सिर्फ़ एक बार process करना चाहिए, वरना एक ही payment दो बार captured दिख सकती है। Amazon का cart एक ही SKU की lines को एक line में मिला देता है। Swiggy partner menu import करते समय repeated dish rows हटाकर save करता है।

उदाहरण: एक payment gateway तीन events भेजता है, जिनमें से दो का id `evt_1` है। Server को दो unique events process करने हैं और एक duplicate की रिपोर्ट करनी है।

---

## 💻 Code Example — Basic
```javascript
// Sample data with repeats
const nums = [1, 2, 2, 3, 1, 4, 3];          // 2, 1, and 3 appear more than once

// Basic approach: includes() checks the result array before each push
function removeDupBasic(arr) {
  const result = [];                          // will hold the unique values
  for (const x of arr) {                      // visit every value in order
    if (!result.includes(x)) {                // not added yet?
      result.push(x);                         // keep the first occurrence
    }
  }
  return result;                              // unique values, first-seen order
}

console.log(removeDupBasic(nums).join(", "));
// Expected output: 1, 2, 3, 4

// Works for strings too
console.log(removeDupBasic(["a", "b", "a", "c"]).join(""));
// Expected output: abc
```

## 💻 Code Example — Advanced
```javascript
// 1) Unique values with a Set: O(n) time, O(n) space
function uniqueValues(arr) {
  // Guard: only arrays are accepted
  if (!Array.isArray(arr)) throw new TypeError("uniqueValues expects an array");
  return [...new Set(arr)];                   // Set keeps the first occurrence and drops repeats
}

// 2) Unique objects by a key (e.g. id): O(n) time, O(n) space
function uniqueBy(arr, keyFn) {
  // Guard: the key function must be a function
  if (!Array.isArray(arr) || typeof keyFn !== "function") {
    throw new TypeError("uniqueBy(arr, keyFn): arr must be an array and keyFn a function");
  }
  const seen = new Set();                     // keys we have already accepted
  const out = [];                             // result list of unique objects
  for (const item of arr) {                   // single pass over the data
    const k = keyFn(item);                    // compute the identity key, e.g. item.id
    if (!seen.has(k)) {                       // first time we see this key?
      seen.add(k);                            // remember it
      out.push(item);                         // keep the whole object
    }
  }
  return out;                                 // one object per unique key
}

// 3) In-place dedupe for a SORTED array: O(n) time, O(1) extra space
function dedupeSortedInPlace(arr) {
  if (arr.length === 0) return 0;             // nothing to do for an empty array
  let write = 1;                              // next free slot for a unique value (index 0 is always kept)
  for (let read = 1; read < arr.length; read++) { // scan from the second item
    if (arr[read] !== arr[write - 1]) {       // differs from the last value we kept?
      arr[write] = arr[read];                 // copy the new unique value forward
      write++;                                // move the write position forward
    }
  }
  arr.length = write;                         // cut off the leftover tail
  return write;                               // the new length
}

console.log(JSON.stringify(uniqueValues([1, 2, 2, 3, 1, 4, 3]))); // Expected output: [1,2,3,4]

const events = [
  { id: "evt_1", type: "payment.captured" },  // first delivery
  { id: "evt_2", type: "refund.created" },    // different event
  { id: "evt_1", type: "payment.captured" },  // duplicate delivery of evt_1
];
console.log(uniqueBy(events, (e) => e.id).length); // Expected output: 2

const sorted = [1, 1, 2, 2, 2, 3];            // already sorted
const newLen = dedupeSortedInPlace(sorted);   // modifies the array itself
console.log(newLen, sorted.join(","));        // Expected output: 3 1,2,3

// Time:  O(n) for the Set and uniqueBy versions; the in-place version is O(n) too
// Space: O(n) for Set-based versions, O(1) extra for the in-place sorted version
```

### Edge Cases
```javascript
// Edge 1: empty array -> empty array
console.log(JSON.stringify(uniqueValues([])));          // Expected output: []

// Edge 2: NaN is unique once, because Set treats NaN as equal to NaN
console.log(uniqueValues([NaN, NaN, 1]).length);        // Expected output: 2

// Edge 3: 1 and "1" are different values, so both stay
console.log(JSON.stringify(uniqueValues([1, "1", 1]))); // Expected output: [1,"1"]

// Edge 4: objects dedupe by reference in a Set, so two equal-looking objects both stay
console.log(uniqueValues([{ a: 1 }, { a: 1 }]).length); // Expected output: 2 (use uniqueBy instead)

// Edge 5: null and undefined are separate values
console.log(uniqueValues([null, undefined, null]).length); // Expected output: 2
```

---

## 🟠 Express.js Integration
A webhook endpoint that receives a batch of payment events, removes duplicates by `id`, and reports how many were processed. The handler validates the body first, so a bad request never reaches the logic.

```javascript
// Express.js: webhook endpoint that drops duplicate events
const express = require("express");          // import Express
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies into req.body

// Keep only the first event for each id (same idea as uniqueBy)
function uniqueById(events) {
  const seen = new Set();                    // ids that are already accepted
  return events.filter((e) => {              // keep an event only if its id is new
    if (seen.has(e.id)) return false;        // duplicate delivery -> drop it
    seen.add(e.id);                          // first time -> remember the id
    return true;                             // keep this event
  });
}

// POST /api/webhooks/payments   body: { "events": [ { "id": "...", "type": "..." } ] }
app.post("/api/webhooks/payments", (req, res) => {
  const events = req.body.events;            // the batch sent by the payment provider
  if (!Array.isArray(events)) {              // validate the shape before doing any work
    return res.status(400).json({ error: "events must be an array" }); // 400 Bad Request
  }
  const fresh = uniqueById(events);          // remove duplicate deliveries
  res.json({                                 // 200 OK with a small report
    received: events.length,                 // how many events arrived
    processed: fresh.length,                 // how many unique events we will handle
    duplicatesDropped: events.length - fresh.length, // the difference is the duplicate count
  });
});

// Start the server on PORT from the environment, or 3000
app.listen(process.env.PORT || 3000, () => {
  console.log("Webhook API running");        // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `includes` on arrays of objects
```javascript
// Wrong: each object literal is a new reference, so includes never finds a duplicate
const list = [{ id: 1 }, { id: 1 }];
const wrong = [];
for (const o of list) if (!wrong.includes(o)) wrong.push(o);
console.log(wrong.length);                   // Expected output: 2 (duplicates survived)

// Right: dedupe by the key that defines identity
const right = [];
const ids = new Set();
for (const o of list) {
  if (!ids.has(o.id)) { ids.add(o.id); right.push(o); } // check the id, not the reference
}
console.log(right.length);                   // Expected output: 1
```

❌ **Mistake 2:** Mutating the array while looping over it with `splice`
```javascript
// Wrong: splice shifts the next item into the current index, so the loop skips it
const arr = [2, 2, 2, 3];
try {
  for (let i = 0; i < arr.length; i++) {     // i keeps moving forward
    if (arr[i] === arr[i + 1]) arr.splice(i, 1); // remove a repeat, but skip the next value
  }
} catch (e) { console.log(e.message); }
console.log(arr.join(","));                  // Expected output: 2,2,3 (still has a duplicate!)

// Right: build a new array, or walk backwards when removing in place
const clean = [2, 2, 2, 3].filter((x, i, a) => a.indexOf(x) === i); // keep first occurrence
console.log(clean.join(","));                // Expected output: 2,3
```

❌ **Mistake 3:** Forgetting that `Set` keeps the first occurrence, not the last
```javascript
// Wrong idea: "the last value wins" is not what Set does
const values = [{ v: "old" }, { v: "new" }];
const keyed = new Map(values.map((o) => [1, o])); // same key 1 each time
console.log(keyed.get(1).v);                 // Expected output: new (Map keeps the LAST set value)

// Right: if you want the first occurrence, skip the later ones
const firstWins = new Map();
for (const o of values) if (!firstWins.has(1)) firstWins.set(1, o);
console.log(firstWins.get(1).v);             // Expected output: old
```

---

## 🧠 Tricky Interview Question
```javascript
console.log(new Set([1, "1", 1, null, null, undefined, NaN, NaN]).size); // ?
console.log(new Set([{}, {}]).size);                                     // ?
console.log([...new Set([3, 1, 3, 2, 1])].join(","));                    // ?
```
Answer:
```
5   ← 1, "1", null, undefined, NaN are five different values (NaN counts once)
2   ← two separate object literals are two different references
3,1,2  ← the Set keeps the first occurrence in insertion order
```
Set uses the SameValueZero rule. That means `1` and `"1"` are different, `NaN` equals `NaN`, and objects compare by reference. The same rule makes `Set` a great dedupe tool for primitives and a poor one for objects unless you dedupe by a key.

---

## ⚫ Interview Questions + Answers

**Q1: What is the simplest way to remove duplicates from an array?**
A1: `[...new Set(arr)]`. A Set stores only unique values and keeps insertion order, so spreading it back gives the unique values in first-seen order.

**Q2: How do you remove duplicate objects?**
A2: A Set compares objects by reference, so it will not help. Use a Set of the identity key (such as `id`) and keep the first object for each key, as `uniqueBy` does.

**Q3: What is the time complexity of the includes-based approach?**
A3: O(n²) in the worst case, because each `includes` scans the result array. The Set approach is O(n) time and O(n) space.

**Q4: Can you remove duplicates without extra memory?**
A4: Yes, but only on a sorted array. Equal values sit next to each other, so a two-pointer scan removes repeats in place with O(1) extra space, as `dedupeSortedInPlace` shows.

**Q5: Why does the splice-in-a-loop approach fail?**
A5: After `splice`, the next item moves into the current index, but the loop index moves forward, so one item is skipped. Build a new array with `filter` or `Set` instead.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need unique IDs, tags, or emails from user input or imports
- You process webhooks or events that may be delivered more than once
- You need first-seen order preserved for the UI

❌ Avoid when:
- You need the last occurrence instead of the first; build the Map so later values overwrite, or reverse the array first
- The array is already sorted and you must avoid extra memory; use the two-pointer method
- You want to dedupe objects by content (deep equality); a Set cannot do that, so define a key function or serialize carefully

---

## 📊 Visual Diagram
```
input:   [ 1 ]  [ 2 ]  [ 2 ]  [ 3 ]  [ 1 ]  [ 4 ]  [ 3 ]
           │      │      │      │      │      │      │
seen?:    new    new    dup    new    dup    new    dup
           ▼      ▼             ▼             ▼
result:  [ 1 ] [ 2 ] ─────── [ 3 ] ─────── [ 4 ]

output:  [ 1, 2, 3, 4 ]     (first occurrence kept, order preserved)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Dedupe | Removing repeated values | Repeat values हटाना |
| First occurrence | The first place a value appears | Value का पहला आना |
| SameValueZero | Equality rule used by Set and includes | Set और includes का equality नियम |
| Identity key | Field that decides if two objects are the same | वो field जिससे पता चले दो objects एक हैं |
| Idempotent | Doing it twice gives the same result | दो बार करने पर भी वही नतीजा |
| In-place | Changing the same array without a copy | उसी array को बदलना, नई copy के बिना |

---

## ⚡ 3-Line Summary
English:
1. `[...new Set(arr)]` removes duplicate primitives in one line and keeps first-seen order.
2. For objects, dedupe by a key such as `id`, because a Set compares references.
3. Use a two-pointer scan for sorted arrays when memory is tight; use a Set for everything else.

Hindi:
1. `[...new Set(arr)]` एक line में primitive duplicates हटाता है और पहली occurrence का order रखता है।
2. Objects के लिए `id` जैसी key से dedupe करो, क्योंकि Set references compare करता है।
3. Sorted array और कम memory हो तो two-pointer इस्तेमाल करो; बाकी जगह Set।

---

## ➡️ Next Topic
**182. Sort Array of Objects** — once the data is clean, the next step is ordering it. You will learn comparator functions, multi-key sorting, and why the default `sort()` gives surprising results.
