# 182. Sort Array of Objects
# हिंदी में: Objects की Array को Sort करना — Comparator, Multi-key Sort और Default sort की गड़बड़

---

## 🔵 Simple Definition (English)
Sorting an array of objects means putting the objects in order based on one or more of their fields, such as rating, price, or name. You do it by passing a comparator function to `Array.prototype.sort` that tells JavaScript which of two objects should come first.

## 🔵 सरल परिभाषा (Hindi)
Objects की array को sort करने का मतलब है उसके objects को एक या ज़्यादा fields (जैसे rating, price या name) के हिसाब से क्रम में लगाना। इसके लिए `sort` को एक comparator function देते हैं, जो बताता है कि दो objects में से कौन पहले आए।

---

## 🔴 Problem it Solves
**Problem Statement:** Given an array of objects, return a new array sorted by a chosen field, in ascending or descending order. When two items tie on the first field, sort by a second field. Do not change the original array.

Without a proper comparator, the default `sort()` converts values to strings. Then `10` comes before `9`, and the list looks wrong to users. Sorting objects also needs a rule for ties, or the order can change unpredictably between runs.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** Objects की array दी हो, तो एक नई array लौटाओ जो चुने हुए field के हिसाब से sort हो, ascending या descending। अगर पहले field में दो items बराबर हों तो दूसरे field से sort करो। Original array मत बदलो।

बिना सही comparator के default `sort()` values को string मानकर sort करता है। तब `10` को `9` से पहले रख देता है और user को list गलत लगती है। Objects के लिए tie-breaking का नियम भी चाहिए, वरना order हर बार बदल सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Copy the array with `[...arr]` so the original is not changed.
Step 2 → Give `sort` a comparator `(a, b) => ...` that returns a negative, zero, or positive number.
Step 3 → A negative result means `a` comes first, positive means `b` comes first, zero means a tie.
Step 4 → For multiple keys, compare the first key; if it is a tie, compare the next key.
Step 5 → JavaScript's `sort` (TimSort in V8) calls the comparator and orders the items.
Step 6 → Ties keep their original relative order, because the sort is stable.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Original array न बदले, इसके लिए `[...arr]` से copy बनाओ।
Step 2 → `sort` को comparator `(a, b) => ...` दो, जो negative, zero या positive number लौटाए।
Step 3 → Negative का मतलब `a` पहले, positive का मतलब `b` पहले, zero का मतलब बराबर।
Step 4 → Multiple keys के लिए पहले key की तुलना करो; बराबर हों तो अगली key देखो।
Step 5 → JavaScript का `sort` (V8 में TimSort) comparator को call करके items को लगाता है।
Step 6 → बराबर items का आपसी क्रम बना रहता है, क्योंकि sort stable है।

---

## 🟡 Real World Example
Swiggy shows restaurants sorted by rating, then by delivery time when ratings tie. Amazon sorts search results by price low to high, then by review count. A Razorpay report sorts settlements by date, then by merchant name. Each of these is a comparator with a fallback key.

Scenario: A user opens the Swiggy list and chooses "Top rated". Punjab Grill (4.8) is first. Two restaurants with 4.5 come next, and the faster one (shorter ETA) should be shown first.

## 🟡 Real Example Hindi mein
Swiggy restaurants को rating के हिसाब से दिखाता है, और rating बराबर हो तो delivery time से। Amazon search results को price low-to-high और फिर review count से sort करता है। Razorpay settlement report को date और फिर merchant name से sort करता है। हर जगह एक comparator है जिसमें fallback key होती है।

उदाहरण: User "Top rated" चुनता है। Punjab Grill (4.8) सबसे ऊपर। दो restaurants 4.5 के हैं, तो जिसका ETA कम है वह पहले दिखना चाहिए।

---

## 💻 Code Example — Basic
```javascript
// Sample data: restaurants on a food delivery app
const restaurants = [
  { name: "Biryani Blues", rating: 4.5, eta: 35 },  // rating out of 5, eta in minutes
  { name: "Punjab Grill", rating: 4.8, eta: 45 },
  { name: "Burger King", rating: 4.2, eta: 20 },
  { name: "Domino's", rating: 4.5, eta: 25 },
];

// Basic: sort by rating, highest first (b - a gives descending order)
const byRating = [...restaurants].sort((a, b) => b.rating - a.rating); // copy first, do not touch the original
console.log(byRating.map((r) => r.name).join(", "));
// Expected output: Punjab Grill, Biryani Blues, Domino's, Burger King
// (Biryani Blues and Domino's tie at 4.5; the stable sort keeps Biryani first because it came first)

// Basic: sort names alphabetically with localeCompare (handles letters and accents correctly)
const byName = [...restaurants].sort((a, b) => a.name.localeCompare(b.name));
console.log(byName.map((r) => r.name).join(", "));
// Expected output: Biryani Blues, Burger King, Domino's, Punjab Grill

// Basic: two keys: rating descending, then eta ascending for ties
const twoKeys = [...restaurants].sort((a, b) => {
  if (b.rating !== a.rating) return b.rating - a.rating; // different ratings: higher first
  return a.eta - b.eta;                                  // same rating: shorter eta first
});
console.log(twoKeys.map((r) => r.name).join(", "));
// Expected output: Punjab Grill, Domino's, Biryani Blues, Burger King
```

## 💻 Code Example — Advanced
```javascript
// Build a reusable comparator from a list of sort rules
// Each rule: { key: "fieldName", dir: 1 (asc) or -1 (desc), cmp?: custom compare function }
function byKeys(...rules) {
  // Guard: at least one rule is required
  if (rules.length === 0) throw new TypeError("byKeys needs at least one rule");

  return (a, b) => {                          // the comparator that sort() will call
    for (const { key, dir = 1, cmp } of rules) {  // check the rules in priority order
      const x = a[key];                       // value from object a
      const y = b[key];                       // value from object b
      let diff;                               // negative, zero, or positive
      if (cmp) {
        diff = cmp(x, y);                     // custom compare for special cases
      } else if (typeof x === "string") {
        diff = x.localeCompare(y);            // correct alphabetical compare for strings
      } else {
        diff = x - y;                         // numeric compare works for numbers
      }
      if (diff !== 0) return diff * dir;      // first non-tie decides; dir flips desc
    }
    return 0;                                 // all rules tie: keep original order (stable sort)
  };
}

// Sort: rating desc, then eta asc, then name asc
const ranked = [...restaurants].sort(
  byKeys({ key: "rating", dir: -1 }, { key: "eta", dir: 1 }, { key: "name", dir: 1 })
);
console.log(ranked.map((r) => r.name).join(", "));
// Expected output: Punjab Grill, Domino's, Biryani Blues, Burger King

// Schwartzian transform: compute an expensive key once per item, not once per comparison
const words = ["sandwich", "a", "pizza", "burger"];
const byLength = words
  .map((w) => [w.length, w])                  // step 1: decorate each word with its length once
  .sort((p, q) => p[0] - q[0] || p[1].localeCompare(q[1])) // step 2: sort pairs by length, then word
  .map(([, w]) => w);                         // step 3: undecorate back to plain words
console.log(byLength.join(", "));
// Expected output: a, pizza, burger, sandwich

// Time:  O(n log n) comparisons on average and in the worst case (TimSort in V8)
// Space: O(n) for the copy; the sort itself uses O(n) auxiliary memory in V8
```

### Edge Cases
```javascript
// Edge 1: empty array -> empty array
console.log(JSON.stringify([].sort((a, b) => a - b)));   // Expected output: []

// Edge 2: missing field gives undefined, and undefined - 4.5 is NaN, which breaks the comparator
console.log(Number.isNaN(undefined - 4.5));              // Expected output: true

// Edge 3: default sort puts undefined at the end, not in numeric order
console.log([3, undefined, 1].sort().length, [3, undefined, 1].sort()[2]); // Expected output: 3 undefined

// Edge 4: a stable sort keeps tied items in their original order
const tie = [{ n: "first", r: 4 }, { n: "second", r: 4 }];
console.log(tie.sort((a, b) => b.r - a.r).map((x) => x.n).join(","));   // Expected output: first,second
```

---

## 🟠 Express.js Integration
An endpoint that reads a `sort` query such as `sort=-rating,eta` (a leading minus means descending). It whitelists the fields it allows and returns a 400 error for unknown fields.

```javascript
// Express.js: a restaurant list endpoint with safe, whitelisted sorting
const express = require("express");          // import Express
const app = express();                       // create the app

// Pretend database rows
const restaurants = [
  { name: "Biryani Blues", rating: 4.5, eta: 35 },
  { name: "Punjab Grill", rating: 4.8, eta: 45 },
  { name: "Burger King", rating: 4.2, eta: 20 },
  { name: "Domino's", rating: 4.5, eta: 25 },
];

// Only these fields may be used for sorting (never trust raw user input as a property name)
const SORTABLE = ["name", "rating", "eta"];

// Turn "-rating,eta" into [{ key: "rating", dir: -1 }, { key: "eta", dir: 1 }]
function parseSort(text) {
  return text.split(",").map((part) => {    // split the list on commas
    const dir = part.startsWith("-") ? -1 : 1; // leading minus means descending
    const key = part.replace(/^-/, "");     // remove the minus sign to get the field name
    return { key, dir };                    // one rule per field
  });
}

// GET /api/restaurants?sort=-rating,eta
app.get("/api/restaurants", (req, res) => {
  const sortParam = req.query.sort || "name"; // default sort is by name
  const rules = parseSort(sortParam);         // convert the query text to rules
  // Validate every requested field against the whitelist
  if (rules.some((r) => !SORTABLE.includes(r.key))) {
    return res.status(400).json({ error: `sort fields must be one of ${SORTABLE.join(", ")}` }); // 400
  }
  // Build the comparator from the rules and sort a copy of the data
  const sorted = [...restaurants].sort((a, b) => {
    for (const { key, dir } of rules) {       // apply rules in order
      const diff = typeof a[key] === "string"   // strings use localeCompare
        ? a[key].localeCompare(b[key])
        : a[key] - b[key];                    // numbers use subtraction
      if (diff !== 0) return diff * dir;      // first difference decides
    }
    return 0;                                 // all equal: keep order
  });
  res.json(sorted);                           // 200 OK with the sorted list
});

// Start the server on PORT from the environment, or 3000
app.listen(process.env.PORT || 3000, () => {
  console.log("Restaurant API running");      // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using the default `sort()` on numbers
```javascript
// Wrong: default sort compares values as strings, so "10" < "9"
console.log([10, 9, 1, 100].sort().join(","));   // Expected output: 1,10,100,9

// Right: give a numeric comparator
console.log([10, 9, 1, 100].sort((a, b) => a - b).join(",")); // Expected output: 1,9,10,100
```

❌ **Mistake 2:** Sorting the original array (state or props) in place
```javascript
// Wrong: sort mutates the array and returns the same reference
const state = [{ n: "b" }, { n: "a" }];
const wrong = state.sort((x, y) => x.n.localeCompare(y.n)); // state itself changed!
console.log(state === wrong, state[0].n);        // Expected output: true a

// Right: copy first, then sort the copy (important in React state and shared data)
const original = [{ n: "b" }, { n: "a" }];
const right = [...original].sort((x, y) => x.n.localeCompare(y.n));
console.log(original[0].n, right[0].n);          // Expected output: b a
```

❌ **Mistake 3:** Comparing strings with `<` or `sort()` when case matters
```javascript
// Wrong: default string sort uses code units, so uppercase letters come first
console.log(["b", "A", "a"].sort().join(" "));   // Expected output: A a b

// Right: localeCompare follows the human alphabet order
console.log(["b", "A", "a"].sort((x, y) => x.localeCompare(y)).join(" ")); // Expected output: a A b
```

---

## 🧠 Tricky Interview Question
```javascript
const nums = [10, 9, 1, 100];
console.log(nums.sort());                        // ?

const copy = [3, 1, 2];
const same = copy.sort((a, b) => a - b);         // ?
console.log(copy, same === copy);                // ?
```
Answer:
```
[ 1, 10, 100, 9 ]    ← default sort compares "1", "10", "100", "9" as strings
[ 1, 2, 3 ] true     ← sort sorts in place and returns the same array reference
```
Two lessons: the default comparator is string-based, and `sort` mutates the array it is called on. Interviewers often ask this to check whether you know that `sort` returns the same reference, not a new array.

---

## ⚫ Interview Questions + Answers

**Q1: Why does `[10, 9, 1].sort()` give a wrong order?**
A1: Without a comparator, `sort` converts each value to a string and compares UTF-16 code units. `"10"` comes before `"9"` because `"1"` is less than `"9"`. Pass `(a, b) => a - b` for numbers.

**Q2: What does a comparator need to return?**
A2: A negative number if `a` should come before `b`, a positive number if `b` should come before `a`, and zero if they are equal. Only the sign matters.

**Q3: Is Array.prototype.sort stable?**
A3: Yes, since ES2019. Items that compare equal keep their original relative order. That is why sorting by rating and then by name in two passes works, and why a multi-key comparator is more direct.

**Q4: How do you sort by several fields?**
A4: Compare the first field; if the result is not zero, return it. Otherwise compare the next field, and so on. `byKeys` in the advanced example does exactly this, with a direction for each rule.

**Q5: What is the time complexity of sort?**
A5: O(n log n) comparisons in V8, which uses TimSort. Space is O(n) because the copy and the sort's temporary buffer grow with the input.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You must present a list in a clear order (price, rating, date, name)
- You need a secondary order for ties
- The data fits in memory and the list is shown once

❌ Avoid when:
- The data is huge and paged; sort in the database with `ORDER BY` and an index
- You need to sort the same big list many times; cache the sorted result or keep it sorted on insert
- You want to sort with comparators that are inconsistent (NaN, random); results become unpredictable

---

## 📊 Visual Diagram
```
Input (name, rating, eta)
  Biryani Blues  4.5  35
  Punjab Grill   4.8  45
  Burger King    4.2  20
  Domino's       4.5  25

Rule 1: rating DESC    -> Punjab 4.8 | Biryani 4.5 | Domino's 4.5 | Burger 4.2
Rule 2: eta ASC (ties) -> Biryani 4.5 (35 min) vs Domino's 4.5 (25 min) -> Domino's first

Final:  Punjab Grill, Domino's, Biryani Blues, Burger King
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Comparator | Function that orders two items | दो items को क्रम में रखने वाला function |
| Stable sort | Ties keep original relative order | बराबर items का क्रम बना रहना |
| Multi-key sort | Sorting by several fields in priority order | कई fields से priority के साथ sort |
| localeCompare | Locale-aware string comparison | Language के हिसाब से string तुलना |
| Mutation | Changing the original array | Original array को बदलना |
| Schwartzian transform | Compute the key once, sort, then clean up | Key एक बार निकालकर sort करना |

---

## ⚡ 3-Line Summary
English:
1. Always pass a comparator to `sort`, because the default sort compares values as strings.
2. Copy the array with `[...arr]` before sorting, since `sort` mutates and returns the same array.
3. For several fields, compare one field at a time and return the first non-zero difference.

Hindi:
1. `sort` को हमेशा comparator दो, क्योंकि default sort values को string मानकर sort करता है।
2. Sort से पहले `[...arr]` से copy बनाओ, क्योंकि `sort` original को बदल देता है।
3. कई fields के लिए एक-एक करके तुलना करो और पहला non-zero फ़र्क लौटाओ।

---

## ➡️ Next Topic
**183. Count Character Frequency** — now that you can order objects, the next problem counts how often each character appears in a string, using objects and Maps.
