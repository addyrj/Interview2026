# 168. Find Duplicate in Array
# हिंदी में: Array में Duplicate ढूँढना (Find Duplicate in Array)

---

## 🔵 Simple Definition (English)
Finding duplicates means checking an array and returning the values that appear more than once. You can return the first repeated value, all repeated values, or just `true` or `false`. The best solution uses a `Set` or `Map` to remember values, so each element is checked in constant time on average.

## 🔵 सरल परिभाषा (Hindi)
Duplicate ढूँढने का मतलब है array में देखना और उन values को लौटाना जो एक से ज़्यादा बार आती हैं। आप पहला repeated value, सारे repeated values, या सिर्फ़ `true`/`false` लौटा सकते हैं। सबसे अच्छा हल `Set` या `Map` से होता है, जो values याद रखते हैं और हर element औसतन constant time में जाँचा जाता है।

---

## 🔴 Problem it Solves
Without a clever structure, checking every pair costs O(n²) time, which becomes slow for thousands of records. Real systems receive bulk data, such as a seller's product list, and must reject duplicates quickly. This problem teaches you how a hash-based `Set` or `Map` turns a slow nested loop into a single pass.

## 🔴 यह क्यों बना? (Hindi)
सही structure के बिना हर जोड़ी जाँचने में O(n²) समय लगता है, जो हज़ारों records के लिए धीमा हो जाता है। असली systems में bulk data आता है, जैसे seller की product list, और duplicates को जल्दी reject करना होता है। यह सवाल सिखाता है कि hash-based `Set` या `Map` कैसे nested loop को एक ही pass में बदल देते हैं।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty `Set` to remember values you have seen.
Step 2 → Walk through the array once. If the value is already in the Set, it is a duplicate.
Step 3 → Otherwise add the value to the Set and continue. Return the result when the loop ends or early when you find what you need.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक खाली `Set` बनाओ, जिसमें देखी हुई values याद रहें।
Step 2 → Array को एक बार चलाओ। अगर value पहले से Set में है, तो वह duplicate है।
Step 3 → नहीं तो value Set में डालो और आगे बढ़ो। जो चाहिए वो मिलते ही early return करो।

---

## 🟡 Real World Example
Imagine Flipkart's seller portal accepting a bulk CSV upload of 50,000 product SKUs. If the same SKU appears twice, the catalog would show two products with the same identity, which breaks inventory and orders. The upload service runs a one-pass duplicate check using a `Set` and rejects the file with the first repeated SKU. Razorpay's KYC pipeline uses a similar idea when it looks for a PAN number that is already linked to another merchant account.

## 🟡 Real Example Hindi mein
मान लो Flipkart के seller portal पर seller 50,000 product SKUs वाली bulk CSV upload करता है। अगर एक SKU दो बार आ गया, तो catalog में दो products एक ही पहचान के साथ दिखेंगे, जिससे inventory और orders बिगड़ेंगे। Upload service `Set` से एक pass में duplicate check करती है और पहला repeated SKU बताकर file reject कर देती है। Razorpay की KYC pipeline भी ऐसा ही विचार इस्तेमाल करती है, जब पता करना होता है कि PAN पहले से किसी और merchant से जुड़ा है या नहीं।

---

## 💻 Code Example — Basic
```javascript
// Basic: brute force, compare every pair with nested loops
// Run with: node 168-basic.js
// Time: O(n²)   Space: O(d) where d is the number of duplicate values found

const assert = require("node:assert/strict");   // strict assertions

function findDuplicatesBrute(arr) {             // returns all values that repeat
  const dupes = [];                             // list to collect repeated values
  for (let i = 0; i < arr.length; i++) {        // outer loop: pick each element
    for (let j = i + 1; j < arr.length; j++) {  // inner loop: compare with elements after it
      if (arr[i] === arr[j] && !dupes.includes(arr[i])) { // equal and not recorded yet
        dupes.push(arr[i]);                     // record the duplicate value once
      }
    }
  }
  return dupes;                                 // return the list of duplicates
}

const data = [1, 2, 3, 2, 4, 1];                // sample input with 1 and 2 repeated
console.log(findDuplicatesBrute(data));         // prints: [ 1, 2 ]

// Self-checks
assert.deepEqual(findDuplicatesBrute([1, 2, 3]), []);       // no duplicates → empty array
assert.deepEqual(findDuplicatesBrute([]), []);              // empty input → empty array
assert.deepEqual(findDuplicatesBrute([5, 5, 5]), [5]);      // triple value reported once
assert.deepEqual(findDuplicatesBrute(["1", 1]), []);        // "1" and 1 are different values
console.log("basic checks passed");                          // prints: basic checks passed
```
Expected output:
```
[ 1, 2 ]
basic checks passed
```

## 💻 Code Example — Advanced
```javascript
// Advanced: one pass with Set (first duplicate) and Map (all duplicates)
// Run with: node 168-advanced.js
// Time: O(n)   Space: O(n) for the Set or Map

const assert = require("node:assert/strict");   // strict assertions

// Returns the FIRST value that repeats while scanning left to right, or undefined
function firstDuplicate(arr) {                  // stops as soon as it finds a repeat
  const seen = new Set();                       // Set uses SameValueZero: 1 and "1" differ, NaN equals NaN
  for (const value of arr) {                    // walk the array once
    if (seen.has(value)) return value;          // value seen before → first duplicate, exit early
    seen.add(value);                            // remember this value for later checks
  }
  return undefined;                             // loop finished, no duplicate found
}

// Returns every value that appears more than once, in first-seen order
function findAllDuplicates(arr) {               // counts occurrences with a Map
  const counts = new Map();                     // value → how many times it appeared
  for (const value of arr) {                    // one pass to count
    counts.set(value, (counts.get(value) ?? 0) + 1); // add 1 to the current count (default 0)
  }
  return [...counts]                            // turn Map entries into [value, count] pairs
    .filter(([, count]) => count > 1)           // keep only values that appear more than once
    .map(([value]) => value);                   // keep just the value
}

const data = [1, 2, 3, 2, 4, 1];               // sample input
assert.equal(firstDuplicate(data), 2);          // 2 repeats before 1 does (index 3 vs 5)
assert.deepEqual(findAllDuplicates(data), [1, 2]); // both repeated values, in first-seen order
assert.equal(firstDuplicate([3, 1, 3, 1]), 3);  // first repeat found while scanning is 3
assert.equal(firstDuplicate([1, 2, 3]), undefined); // no duplicate → undefined

// Edge cases handled by Set and Map
assert.ok(Number.isNaN(firstDuplicate([NaN, 1, NaN]))); // Set treats NaN as equal to NaN, so NaN repeats are detected
assert.equal(firstDuplicate([1, "1"]), undefined); // number 1 and string "1" are different

console.log(firstDuplicate(data));              // prints: 2
console.log("advanced checks passed");         // prints: advanced checks passed
```
Expected output:
```
2
advanced checks passed
```

---

## 🟠 Express.js Integration
A bulk SKU upload endpoint validates the input type, then calls the one-pass duplicate check and returns HTTP 409 Conflict when a repeat exists. Install with `npm i express` before running.

```javascript
// Express route: POST /api/skus/validate with JSON body { "skus": ["A1", "B2", ...] }
const express = require("express");                 // import Express
const app = express();                              // create the application
app.use(express.json());                            // parse JSON bodies

// One-pass duplicate finder (same as firstDuplicate above)
function firstDuplicate(arr) {                      // returns first repeated value or undefined
  const seen = new Set();                           // remember values seen so far
  for (const v of arr) {                            // check each SKU once
    if (seen.has(v)) return v;                      // repeat found → return it
    seen.add(v);                                    // otherwise remember it
  }
  return undefined;                                 // no repeats
}

app.post("/api/skus/validate", (req, res) => {      // handle POST requests
  const { skus } = req.body ?? {};                  // read the "skus" array
  if (!Array.isArray(skus)) {                       // validate it is an array
    return res.status(400).json({ error: "skus must be an array" }); // 400 Bad Request
  }
  if (!skus.every((s) => typeof s === "string")) {  // every SKU must be a string
    return res.status(400).json({ error: "every SKU must be a string" }); // 400
  }
  const dup = firstDuplicate(skus);                 // find the first repeated SKU
  if (dup !== undefined) {                          // a duplicate exists
    return res.status(409).json({ error: "duplicate SKU", sku: dup }); // 409 Conflict
  }
  return res.json({ ok: true, count: skus.length }); // all SKUs are unique
});

app.listen(3003, () => console.log("sku API on 3003")); // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `indexOf` inside `filter` returns every extra copy, not each duplicate value once
✅ Correct: Collect unique duplicate values with a `Set`.

```javascript
// Wrong: each extra occurrence is returned, so 1 appears twice in the result
const arr = [1, 2, 1, 1];                           // 1 appears three times
const wrong = arr.filter((x, i) => arr.indexOf(x) !== i); // keeps every non-first occurrence
console.log(wrong);                                 // prints: [ 1, 1 ] (duplicated)

// Right: put the repeats in a Set so each value appears once
const right = [...new Set(arr.filter((x, i) => arr.indexOf(x) !== i))]; // unique repeats
console.log(right);                                 // prints: [ 1 ]
```

❌ Mistake 2: Using a plain object as the lookup table
✅ Correct: Use `Set` or `Map`, because object keys are always strings.

```javascript
// Wrong: object keys turn 1 and "1" into the same key "1"
const seenObj = {};                                 // plain object used as a set
const wrongDup = [1, "1"].find((v) => {             // find returns the first "duplicate"
  if (seenObj[v]) return true;                      // key "1" already exists for both
  seenObj[v] = true;                                // store the key
  return false;
});
console.log(wrongDup, typeof wrongDup);             // prints: 1 string (wrong: they are different)

// Right: Set keeps the types apart
const seenSet = new Set();                          // Set compares values by type and value
const rightDup = [1, "1"].find((v) => {             // same scan, but using Set
  if (seenSet.has(v)) return true;                  // only true for the same type and value
  seenSet.add(v);                                   // remember this value
  return false;
});
console.log(rightDup);                              // prints: undefined (correct: no duplicate)
```

---

## 🧠 Tricky Interview Question
```javascript
// What will each line print?
const nums = [1, "1", 1, NaN, NaN];                 // mixed types and NaN
const seen = new Set();                             // remember values
const dups = [];                                    // collect duplicates
for (const n of nums) {                             // one pass
  if (seen.has(n)) dups.push(n);                    // already seen → duplicate
  else seen.add(n);                                 // otherwise remember it
}
console.log(dups);                                  // ?
console.log(seen.size);                             // ?
console.log(NaN === NaN);                           // ?
```
Answer:
```
[ 1, NaN ]   ← the second 1 and the second NaN are duplicates; "1" is not a repeat of 1
3            ← the Set holds 1, "1", and NaN
false        ← NaN is the only value not equal to itself with ===
```
Explanation: `Set` uses the SameValueZero rule. It compares by type and value, so `1` and `"1"` are different, and `NaN` equals `NaN`. The `===` operator follows different rules, which is why `NaN === NaN` is `false`. Knowing the difference between these rules is a common interview check.

---

## ⚫ Interview Questions + Answers

**Q1: What is the simplest correct way to find duplicates?**
A1: Use a `Set`. Loop through the array, check `seen.has(value)`, and add the value if it is new. It takes O(n) time and O(n) space.

**Q2: Why is the nested-loop approach slower?**
A2: Comparing every pair takes O(n²) comparisons. For 10,000 items that is about 50 million comparisons, while the Set approach needs about 10,000 lookups.

**Q3: What is the difference between returning the first duplicate and all duplicates?**
A3: The first duplicate stops as soon as a repeat is found, so it can exit early. All duplicates must scan the whole array, usually with a `Map` of counts, and then filter the counts that are greater than 1.

**Q4: How do `Set` and `Map` handle NaN and mixed types?**
A4: Both use SameValueZero. `NaN` is considered equal to `NaN`, while `1` and `"1"` are different keys. Plain objects convert keys to strings, which breaks this.

**Q5: Is there an O(1) space solution for arrays of numbers from 1 to n?**
A5: Yes. For values in the range 1 to n, you can mark visited positions by negating the value at index `|value| - 1`, or use cycle detection (Floyd's algorithm), as in LeetCode 287. These tricks need the value range to be known, so they are not general.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must detect repeated IDs, emails, or SKUs in a large list
- You need one pass and can afford O(n) extra memory
- You need to report the first repeat for user-friendly error messages

❌ Avoid when:
- Memory is extremely tight and the values are in a known small range (use an in-place marking trick)
- The array is tiny and readability matters more than speed (a simple loop is fine)
- You need duplicates across multiple requests or servers (use a database unique constraint)

---

## 📊 Visual Diagram
```
Input: [1, 2, 3, 2, 4, 1]

index:   0   1   2   3   4   5
value:   1   2   3   2   4   1

Scan with a Set (seen):
  1 → not in {}        add → {1}
  2 → not in {1}       add → {1,2}
  3 → not in {1,2}     add → {1,2,3}
  2 → IN {1,2,3}       DUPLICATE → firstDuplicate returns 2 and stops

Count with a Map (findAllDuplicates):
  1→2, 2→2, 3→1, 4→1   keep count > 1  →  [1, 2]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Set | Collection of unique values | Unique values का collection |
| Map | Key-value store with any key type | किसी भी type की key वाला store |
| SameValueZero | Rule used by Set and Map | Set और Map का equality नियम |
| Hash lookup | Average O(1) check for presence | औसतन O(1) में मौजूदगी जाँच |
| Early exit | Return as soon as the answer is known | जवाब मिलते ही रुक जाना |
| Brute force | Check every pair | हर जोड़ी जाँचना |
| Conflict (409) | HTTP status for duplicate data | Duplicate data के लिए HTTP status |

---

## ⚡ 3-Line Summary
English:
1. A single pass with a `Set` finds the first duplicate in O(n) time.
2. A `Map` of counts finds all duplicates, and nested loops are only for tiny inputs.
3. `Set` treats `NaN` as equal to itself and keeps `1` and `"1"` apart, so it is the safe choice.

Hindi:
1. एक pass में `Set` से पहला duplicate O(n) समय में मिलता है।
2. सारे duplicates के लिए counts वाला `Map` लो; nested loops सिर्फ़ छोटे inputs के लिए हैं।
3. `Set` `NaN` को खुद के बराबर मानता है और `1` व `"1"` को अलग रखता है, इसलिए यह सुरक्षित विकल्प है।

---

## ➡️ Next Topic
**169. Flatten Nested Array** — अगला सवाल nested arrays को एक level तक या पूरी तरह flat करना सिखाता है, और recursion बनाम iteration का फ़र्क भी दिखाता है।
