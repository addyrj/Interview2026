# 180. Find Intersection of Arrays
# हिंदी में: Arrays का Intersection निकालना — दो Lists में साझा Items ढूँढना

---

## 🔵 Simple Definition (English)
The intersection of two arrays is the set of values that appear in both arrays. Think of it as "what do these two lists have in common?" The answer should contain each shared value once, unless the problem asks for duplicates.

## 🔵 सरल परिभाषा (Hindi)
दो arrays का intersection उन values का समूह है जो दोनों arrays में मौजूद हों। आसान भाषा में: "इन दो lists में क्या-क्या common है?" जवाब में हर shared value आम तौर पर एक बार ही आनी चाहिए, जब तक problem duplicates न माँगे।

---

## 🔴 Problem it Solves
**Problem Statement:** Given two arrays `a` and `b`, return a new array that contains every value found in both, with no repeats. Keep the order of the first array. Do not modify the input arrays.

Example: `a = [1, 2, 2, 3]` and `b = [2, 3, 4]` should give `[2, 3]`.

A naive check ("for each item in `a`, scan all of `b`") works, but it becomes slow when both arrays have thousands of items. Ten thousand by ten thousand is one hundred million comparisons. The goal is to make each lookup almost instant.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** दो arrays `a` और `b` दिए हों, तो एक नई array लौटाओ जिसमें वो सारी values हों जो दोनों में हैं, बिना repeat के। पहली array का order बनाए रखो। Input arrays को change मत करो।

उदाहरण: `a = [1, 2, 2, 3]` और `b = [2, 3, 4]` का intersection `[2, 3]` होना चाहिए।

हर item के लिए पूरी `b` को scan करने का तरीका काम करता है, पर दोनों arrays बड़ी होने पर बहुत धीमा हो जाता है। दस हज़ार गुणा दस हज़ार यानी एक सौ million comparisons। लक्ष्य है हर lookup को लगभग तुरंत बनाना।

---

## 🟢 How it Works — Step by Step

Step 1 → Put the values of array `b` into a Set (fast lookup, O(1) per check).
Step 2 → Walk through array `a` in its original order.
Step 3 → For each item in `a`, ask the Set: "is this value in `b`?"
Step 4 → Also ask: "have I already added this value?" so duplicates are skipped.
Step 5 → If both answers are right, push the value into the result.
Step 6 → Return the result array.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Array `b` की values को एक Set में डालो (हर check O(1) होगा)।
Step 2 → Array `a` को उसके original order में देखो।
Step 3 → `a` के हर item के लिए Set से पूछो: "क्या यह `b` में है?"
Step 4 → यह भी पूछो: "क्या यह पहले ही result में जुड़ चुका है?" ताकि duplicates छूट जाएँ।
Step 5 → दोनों जवाब सही हों तो value को result में push कर दो।
Step 6 → Result array return कर दो।

---

## 🟡 Real World Example
Swiggy shows "Dishes available at both restaurants" when a user compares two menus. Instagram shows "mutual followers" between you and another account. Razorpay checks which payment methods two merchants share for a combined checkout. All of these are intersections on lists of IDs or names.

Scenario: A user compares the menus of "Biryani Blues" and "Punjab Grill". The app shows the dishes both restaurants serve, so the user knows where to order a shared favourite.

## 🟡 Real Example Hindi mein
Swiggy दो restaurants की तुलना करते समय "दोनों पर मिलने वाले dishes" दिखाता है। Instagram "mutual followers" दिखाता है। Razorpay दो merchants के बीच साझा payment methods निकालता है। ये सब IDs या नामों की lists पर intersection ही हैं।

उदाहरण: एक user "Biryani Blues" और "Punjab Grill" के menu compare करता है। App वो dishes दिखाता है जो दोनों restaurants बनाते हैं, ताकि user अपना पसंदीदा dish दोनों से चुन सके।

---

## 💻 Code Example — Basic
```javascript
// Two menus: each array lists dish names offered by a restaurant
const menuA = ["biryani", "paneer", "naan", "dal", "roti"];  // Biryani Blues
const menuB = ["dal", "pizza", "naan", "biryani", "samosa"]; // Punjab Grill

// Basic intersection: nested checks with includes (easy to read, slower for big arrays)
function intersectBasic(a, b) {
  const result = [];                           // collect the shared dishes here
  for (const item of a) {                      // check each dish of the first menu
    // includes() scans b; result.includes stops us adding the same dish twice
    if (b.includes(item) && !result.includes(item)) {
      result.push(item);                       // dish is in both and not yet added
    }
  }
  return result;                               // array of shared dishes
}

console.log(intersectBasic(menuA, menuB).join(", "));
// Expected output: biryani, naan, dal

// Also works with numbers
console.log(intersectBasic([1, 2, 3, 4], [3, 4, 5]).join(", "));
// Expected output: 3, 4
```

## 💻 Code Example — Advanced
```javascript
// Optimized intersection: Set lookups, O(n + m) time, with input validation
function intersect(a, b) {
  // Guard: both inputs must be arrays, otherwise fail with a clear error
  if (!Array.isArray(a) || !Array.isArray(b)) {
    throw new TypeError("intersect expects two arrays");
  }
  const lookup = new Set(b);                   // build the Set from b once: O(m)
  const seen = new Set();                      // remember the values already added (dedupe)
  const result = [];                           // output array in a's order

  for (const item of a) {                      // single pass over a: O(n)
    // Skip if not in b (lookup.has is O(1)) or if we already added it
    if (!lookup.has(item) || seen.has(item)) continue;
    seen.add(item);                            // mark as added
    result.push(item);                         // keep the shared value
  }
  return result;                               // no duplicates, original order kept
}

// Multiset intersection: keep duplicates, but only as many times as BOTH arrays have them
function intersectMulti(a, b) {
  const counts = new Map();                    // value -> how many copies are left in b
  for (const x of b) {                         // count every value in b
    counts.set(x, (counts.get(x) ?? 0) + 1);   // ?? 0 handles the first time we see x
  }
  const result = [];                           // output with duplicates allowed
  for (const x of a) {                         // walk a in order
    const left = counts.get(x) ?? 0;           // how many copies of x are still available in b
    if (left > 0) {                            // one matching copy exists in b
      result.push(x);                          // use it
      counts.set(x, left - 1);                 // consume one copy from b's budget
    }
  }
  return result;
}

console.log(JSON.stringify(intersect([1, 2, 2, 3], [2, 3, 4])));
// Expected output: [2,3]
console.log(JSON.stringify(intersectMulti([1, 2, 2, 3], [2, 2, 2, 4])));
// Expected output: [2,2]

// Time:  O(n + m) — building the Set is O(m), scanning a is O(n), Set lookups are O(1) on average
// Space: O(m + k) — the Set for b plus the seen Set and result (k = result size)
```

### Edge Cases
```javascript
// Edge 1: either array empty -> empty result
console.log(JSON.stringify(intersect([], [1, 2])));    // Expected output: []

// Edge 2: no common values -> empty result
console.log(JSON.stringify(intersect([1, 2], [3, 4]))); // Expected output: []

// Edge 3: strict types: the number 1 and the string "1" are different values
console.log(JSON.stringify(intersect([1], ["1"])));    // Expected output: []

// Edge 4: objects compare by reference, not by content
const x = { id: 1 };                                   // one object
console.log(intersect([x], [x]).length);               // Expected output: 1 (same reference)
console.log(intersect([{ id: 1 }], [{ id: 1 }]).length); // Expected output: 0 (different references)
```

---

## 🟠 Express.js Integration
An API endpoint that receives two restaurant names, reads both menus, and returns the shared dishes. The route validates input and returns 404 for unknown restaurants.

```javascript
// Express.js: find the dishes two restaurants share
const express = require("express");          // import Express
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies (even though this route uses query strings)

// Pretend database of menus: real apps load these from a table
const menus = {
  "Biryani Blues": ["biryani", "paneer", "naan", "dal", "roti"],
  "Punjab Grill": ["dal", "pizza", "naan", "biryani", "samosa"],
};

// Same intersection idea: Set lookup, keeps a's order, no duplicates
function intersect(a, b) {
  const lookup = new Set(b);                 // fast membership test for b
  const seen = new Set();                    // avoid duplicate output
  return a.filter((item) => {                // keep items of a that qualify
    if (!lookup.has(item) || seen.has(item)) return false; // not shared or already added
    seen.add(item);                          // remember this one
    return true;                             // keep it in the result
  });
}

// GET /api/menus/common?a=Biryani Blues&b=Punjab Grill
app.get("/api/menus/common", (req, res) => {
  const { a, b } = req.query;                // read the two restaurant names from the URL
  if (!menus[a] || !menus[b]) {              // validate: both must exist in our data
    return res.status(404).json({ error: "restaurant not found" }); // 404 Not Found
  }
  res.json({ common: intersect(menus[a], menus[b]) }); // 200 OK with the shared dishes
});

// Start the server on PORT from the environment, or 3000
app.listen(process.env.PORT || 3000, () => {
  console.log("Menu API running");           // printed when the server is ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Comparing objects with `includes` or `Set` and expecting content equality
```javascript
// Wrong: two objects with the same data are different references
const left = [{ id: 1 }];
const right = [{ id: 1 }];
console.log(left.filter((x) => right.includes(x)).length); // Expected output: 0 — nothing matched!

// Right: compare a stable key (the id), then keep the original object
const rightIds = new Set(right.map((o) => o.id));          // Set of ids
console.log(left.filter((x) => rightIds.has(x.id)).length); // Expected output: 1
```

❌ **Mistake 2:** Forgetting that `includes` and `indexOf` treat NaN differently
```javascript
// Wrong: indexOf uses strict equality, and NaN !== NaN
console.log([NaN].filter((x) => [NaN].indexOf(x) !== -1).length); // Expected output: 0

// Right: includes (and Set) use SameValueZero, which treats NaN as equal to NaN
console.log([NaN].filter((x) => [NaN].includes(x)).length);       // Expected output: 1
```

❌ **Mistake 3:** Returning duplicates when the problem wants a set
```javascript
// Wrong: filter alone keeps every copy from a
const dupA = [2, 2, 3];
const dupB = [2, 3];
console.log(dupA.filter((x) => dupB.includes(x)).join(","));   // Expected output: 2,2,3

// Right: track what you already added
const seenOnce = new Set();
console.log(dupA.filter((x) => dupB.includes(x) && !seenOnce.has(x) && seenOnce.add(x)).join(",")); // Expected output: 2,3
```

---

## 🧠 Tricky Interview Question
```javascript
const a = [NaN, 1];                    // array with NaN
const b = [NaN, 2];                    // array with NaN

console.log(a.filter((x) => b.indexOf(x) !== -1));  // ?
console.log(a.filter((x) => b.includes(x)));        // ?
console.log(new Set(b).has(NaN));                   // ?
```
Answer:
```
[]        ← indexOf uses ===, and NaN === NaN is false, so nothing matches
[ NaN ]   ← includes uses SameValueZero, where NaN equals NaN
true      ← Set also uses SameValueZero, so NaN is found
```
A common interview trap: `indexOf` misses NaN, but `includes` and `Set` do not. When you write an intersection, pick `Set` or `includes` and you avoid this silent bug.

---

## ⚫ Interview Questions + Answers

**Q1: How do you find the intersection of two arrays in JavaScript?**
A1: Put one array in a Set, then filter the other array by `set.has(item)`. This is O(n + m) time and is the standard answer.

**Q2: Why is a Set faster than includes for lookups?**
A2: `includes` scans the array one by one, which is O(m) per check. A Set uses a hash table, so `has` is O(1) on average. For n checks, Set gives O(n) total, while repeated `includes` gives O(n * m).

**Q3: How do you handle duplicates in the intersection?**
A3: Decide what the problem means. For a set-style answer, track seen values in another Set. For a multiset answer (keep each duplicate as many times as both arrays have it), use a count Map and decrement the count on each match, as `intersectMulti` does.

**Q4: Does the order of the result matter?**
A4: Usually not, but a good answer keeps the order of the first array. Filtering the first array does that automatically. If you build the Set from the smaller array and iterate the larger one, the order follows the larger array, so mention that trade-off.

**Q5: What happens when the arrays contain objects?**
A5: Objects are compared by reference. Two equal-looking objects are not the same value, so the intersection is empty. Compare a unique key such as `id` instead, or use the same object references in both arrays.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You compare two lists of IDs, names, or tags (followers, dishes, skills)
- The arrays can be large, so O(n * m) is too slow
- You need a membership check many times over the same list

❌ Avoid when:
- Both arrays are tiny (under about 20 items); `includes` is clear and fast enough
- You must intersect sorted arrays with very little memory; two pointers on sorted input use O(1) extra space
- You need to intersect many arrays at once; then count occurrences across all of them with one Map

---

## 📊 Visual Diagram
```
a = [ biryani, paneer, naan, dal, roti ]        b = [ dal, pizza, naan, biryani, samosa ]

Step 1: build Set from b
        lookup = { dal, pizza, naan, biryani, samosa }

Step 2: walk a and filter
        biryani  -> in lookup? YES -> keep       result: [ biryani ]
        paneer   -> in lookup? no  -> skip       result: [ biryani ]
        naan     -> in lookup? YES -> keep       result: [ biryani, naan ]
        dal      -> in lookup? YES -> keep       result: [ biryani, naan, dal ]
        roti     -> in lookup? no  -> skip       result: [ biryani, naan, dal ]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Intersection | Values present in both arrays | दोनों arrays में मौजूद values |
| Set | Collection with unique values and O(1) lookup | Unique values का fast structure |
| Membership test | Checking if a value exists in a collection | Value collection में है या नहीं |
| Multiset | Collection where duplicates are counted | Duplicates गिनने वाला collection |
| SameValueZero | Equality rule used by includes and Set | includes और Set का equality नियम |
| Reference equality | Objects are equal only if they are the same object | Objects सिर्फ़ तभी equal जब वही object हो |

---

## ⚡ 3-Line Summary
English:
1. Intersection = values present in both arrays; put one array in a Set and filter the other.
2. This makes the check O(1) per item, so the total time is O(n + m) instead of O(n * m).
3. Watch for duplicates, object references, and NaN (`includes` finds it, `indexOf` does not).

Hindi:
1. Intersection = दोनों arrays में मौजूद values; एक array को Set में डालो और दूसरी को filter करो।
2. इससे हर check O(1) होता है, यानी कुल time O(n + m) रहता है, O(n * m) नहीं।
3. Duplicates, object references और NaN का ध्यान रखो (`includes` NaN पकड़ता है, `indexOf` नहीं)।

---

## ➡️ Next Topic
**181. Remove Duplicates from Array** — same Set thinking, applied to one array. You also learn when to dedupe objects by a key instead of by value.
