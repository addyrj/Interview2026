# 169. Flatten Nested Array
# हिंदी में: Nested Array को Flat करना — Recursion, Stack और flat() का असली काम

---

## 🔵 Simple Definition (English)
Flattening an array means turning `[1, [2, [3]]]` into `[1, 2, 3]`, so every value sits at the top level. You can do it with recursion or with an explicit stack, and you can limit how many levels get opened.

## 🔵 सरल परिभाषा (Hindi)
Array को flatten करने का मतलब है `[1, [2, [3]]]` को `[1, 2, 3]` बनाना, यानी हर value top level पर आ जाए। यह recursion या explicit stack से होता है, और हम तय कर सकते हैं कि कितनी levels खोलनी हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Given an array that may contain other arrays at any depth, return one array with all non-array values in their original left-to-right order. Optionally flatten only up to a given depth. In the interview, do not use the built-in `flat` inside the solution.

Real data is often nested. An order API returns `orders -> items -> variants`, but the checkout table needs one flat list of SKUs. Without a flatten step, every screen repeats its own nested loops, and each loop is a new chance for a bug.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** एक array दिया है जिसमें कितनी भी गहराई तक arrays हो सकते हैं। एक ऐसी array लौटाओ जिसमें सभी non-array values बाएँ से दाएँ उसी क्रम में हों। चाहो तो सिर्फ़ एक निश्चित depth तक flatten करो। Interview में solution के अंदर built-in `flat` इस्तेमाल मत करो।

Real data अक्सर nested होता है। Order API `orders -> items -> variants` जैसा structure देती है, लेकिन checkout table को SKUs की एक सीधी list चाहिए। Flatten step न हो तो हर screen अपने nested loops लिखती है, और हर loop में एक नई bug की संभावना होती है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty result array.
Step 2 → Read the input one item at a time, from left to right.
Step 3 → If the item is an array, flatten it again (recursion) and add its values.
Step 4 → If the item is a plain value, push it straight into the result.
Step 5 → When every item has been read, return the result.
Step 6 → In the explicit stack version, push children in reverse, so `pop` returns them in the original order.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → एक खाली result array बनाओ।
Step 2 → Input को बाएँ से दाएँ, एक item एक बार में पढ़ो।
Step 3 → अगर item एक array है, तो उसे फिर से flatten करो (recursion) और उसकी values जोड़ो।
Step 4 → अगर item सामान्य value है, तो उसे सीधे result में push करो।
Step 5 → सारे items पढ़ने के बाद result लौटाओ।
Step 6 → Explicit stack वाले version में children को उल्टे क्रम में push करो, ताकि `pop` original क्रम दे।

---

## 🟡 Real World Example
Zomato's menu API returns `sections -> categories -> dishes`. The cart page needs one list to count the total items. Swiggy's order summary works the same way: the bill has grouped line items, and the summary shows one flat list of charges. The flatten step runs once on the server before the response goes out.

Scenario: A restaurant menu is `[["Paneer Tikka", "Dal Makhani"], ["Butter Naan", ["Garlic Naan", "Tandoori Roti"]]]`. The app must show 5 dishes in order, and the badge must say 5.

## 🟡 Real Example Hindi mein
Zomato का menu API `sections -> categories -> dishes` लौटाता है। Cart page पर कुल items गिनने के लिए एक flat list चाहिए। Swiggy के order summary में भी grouped line items होते हैं, और charges की एक flat list दिखानी होती है। Flatten का काम server पर एक बार होता है, response भेजने से पहले।

उदाहरण: एक restaurant का menu है `[["Paneer Tikka", "Dal Makhani"], ["Butter Naan", ["Garlic Naan", "Tandoori Roti"]]]`। App को क्रम में 5 dishes दिखानी हैं, और badge पर 5 लिखा होना चाहिए।

---

## 💻 Code Example — Basic
```javascript
// Basic: recursive flatten, every array at any depth is opened
function flattenBasic(arr) {
  const result = [];                          // empty container for the flat values
  for (const item of arr) {                   // look at each item from left to right
    if (Array.isArray(item)) {                // is this item itself an array?
      result.push(...flattenBasic(item));     // yes: flatten it first, then add its values
    } else {
      result.push(item);                      // no: a plain value goes straight in
    }
  }
  return result;                              // the flat array
}

// Sample: a nested menu with three levels of arrays
const menu = ["Paneer Tikka", ["Dal Makhani", ["Butter Naan", ["Garlic Naan"]]]];
console.log(flattenBasic(menu).join(", "));   // Expected output: Paneer Tikka, Dal Makhani, Butter Naan, Garlic Naan

// Edge cases: empty input, empty nested arrays, and null/undefined values
console.log(flattenBasic([]).length);                  // Expected output: 0
console.log(flattenBasic([[], [[]]]).length);          // Expected output: 0
console.log(JSON.stringify(flattenBasic([null, [undefined]]))); // Expected output: [null,null]
```

## 💻 Code Example — Advanced
```javascript
// Advanced: iterative flatten with an explicit stack and an optional depth limit
function flattenDepth(arr, depth = Infinity) {
  // Guard: the input must be an array
  if (!Array.isArray(arr)) throw new TypeError("flattenDepth expects an array");
  // Guard: depth must be a non-negative number (Infinity is allowed)
  if (typeof depth !== "number" || depth < 0) throw new RangeError("depth must be a number >= 0");

  const result = [];                          // flat output
  const stack = [];                           // work list of [value, level] pairs
  for (let i = arr.length - 1; i >= 0; i--) { // push from the end so the first item is popped first
    stack.push([arr[i], 0]);                  // every top-level item starts at level 0
  }

  while (stack.length > 0) {                  // keep going until no work is left
    const [item, level] = stack.pop();        // take the next item (last in, first out)
    if (Array.isArray(item) && level < depth) { // open the array only if the depth limit allows it
      for (let i = item.length - 1; i >= 0; i--) { // push children in reverse to keep their order
        stack.push([item[i], level + 1]);     // each child is one level deeper
      }
    } else {
      result.push(item);                      // a plain value, or an array we must not open
    }
  }
  return result;                              // the flat result
}

// Test 1: full flatten
console.log(JSON.stringify(flattenDepth([1, [2, [3, [4]]], 5])));    // Expected output: [1,2,3,4,5]
// Test 2: only one level is opened
console.log(JSON.stringify(flattenDepth([1, [2, [3, [4]]], 5], 1))); // Expected output: [1,2,[3,[4]],5]
// Test 3: 20000 levels of nesting (recursion could overflow the call stack; this version does not)
let deep = [0];                               // start with a single value
for (let i = 0; i < 20000; i++) deep = [deep]; // wrap it in one more array, 20000 times
console.log(JSON.stringify(flattenDepth(deep))); // Expected output: [0]

// Time:  O(n), where n is the number of values and arrays visited
// Space: O(n) for the output array and the stack (the stack holds at most the pending children)
```

### Edge Cases
- Empty array `[]` gives `[]`, because there is nothing to open.
- Nested empty arrays `[[], [[]]]` disappear completely, so the result is `[]`.
- `null` and `undefined` are plain values, so they stay in the result.
- A depth of `0` returns a copy of the input with no changes.
- Sparse holes like `[, 1]` are read as `undefined` by `for...of`. The built-in `flat()` removes them instead, so the two can differ.

---

## 🟠 Express.js Integration
A checkout service receives a nested cart from the frontend and returns one flat list of dishes. The endpoint validates the input and only accepts a `depth` value when the client sends one.

```javascript
// Express.js: flatten nested menu sections before sending them to the client
const express = require("express");          // web framework for Node.js
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies into req.body

// POST /api/menu/flatten  body: { "sections": [...], "depth": 2 }
app.post("/api/menu/flatten", (req, res) => {
  const { sections, depth } = req.body;      // read the fields from the request body
  if (!Array.isArray(sections)) {            // validate the type of the main input
    return res.status(400).json({ error: "sections must be an array" }); // 400 Bad Request
  }
  const limit = depth === undefined ? Infinity : Number(depth); // no depth means a full flatten
  if (Number.isNaN(limit) || limit < 0) {    // validate the depth value
    return res.status(400).json({ error: "depth must be a number >= 0" }); // 400 Bad Request
  }
  // Production code can use the built-in flat; the custom version above is for interviews
  const dishes = sections.flat(limit);       // flatten up to the requested depth
  res.json({ count: dishes.length, dishes }); // 200 OK with the count and the flat list
});

// Start the server on PORT from the environment, or 3000
app.listen(process.env.PORT || 3000, () => {
  console.log("Menu API running");          // printed when the server is ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Thinking `concat` flattens everything
✅ Correct: `concat` only opens one level of each argument. Use a recursive helper or `flat(Infinity)` for deep nesting.

```javascript
// Wrong: the nested array inside stays nested
console.log(JSON.stringify([].concat([1, [2, [3]]])));    // Expected output: [1,[2,[3]]]

// Right: flat with Infinity opens every level
console.log(JSON.stringify([1, [2, [3]]].flat(Infinity))); // Expected output: [1,2,3]
```

❌ **Mistake 2:** Using `typeof item === "object"` to detect arrays
✅ Correct: `typeof null` is also `"object"`, so `null` would be treated as an array. Use `Array.isArray`.

```javascript
// Wrong: null passes the typeof check, and for...of on null throws
function badFlatten(arr) {
  const out = [];                             // result list
  for (const x of arr) {                      // iterate the input
    if (typeof x === "object") out.push(...badFlatten(x)); // null also matches here
    else out.push(x);                         // plain value
  }
  return out;
}
try { badFlatten([1, null]); } catch (e) { console.log(e.name); } // Expected output: TypeError

// Right: Array.isArray only matches real arrays
function goodFlatten(arr) {
  const out = [];                             // result list
  for (const x of arr) {                      // iterate the input
    if (Array.isArray(x)) out.push(...goodFlatten(x)); // only real arrays are opened
    else out.push(x);                         // null and objects are kept as values
  }
  return out;
}
console.log(JSON.stringify(goodFlatten([1, null]))); // Expected output: [1,null]
```

---

## 🧠 Tricky Interview Question
```javascript
const arr = [1, [2, [3, [4]]]];
console.log(JSON.stringify(arr.flat()));                    // ?
console.log(JSON.stringify(arr.flat(2)));                   // ?
console.log([, "a"].flat().length);                         // ?
console.log(JSON.stringify([].concat(...[[1], [2, [3]]]))); // ?
```
Answer:
```
[1,2,[3,[4]]]   ← flat() opens one level by default: 2 and [3,[4]] move up, [4] stays inside
[1,2,3,[4]]     ← flat(2) opens two levels: [4] is still one level too deep
1               ← flat() removes holes, so the sparse [, "a"] has only one real value
[1,2,[3]]       ← spread gives two arguments; concat opens one level of each: 2 and [3] move up
```
The trap is that `flat()` and `concat` both open only one level by default, and that `flat` removes holes while `for...of` does not. Explain the depth argument instead of just giving the numbers.

---

## ⚫ Interview Questions + Answers

**Q1: Why use recursion for flatten, and when is it risky?**
A1: Recursion matches the shape of nested data, so the code is short and easy to read. It is risky for very deep nesting, because each level adds a call frame and the stack can overflow. An explicit stack avoids that limit.

**Q2: How do you flatten only one level?**
A2: Use the depth argument in the advanced version, or call `arr.flat(1)`. In the recursive version, pass the level down and stop opening arrays when the level reaches the limit.

**Q3: What is the difference between `flat()` and `flatMap()`?**
A3: `flat()` flattens an existing array. `flatMap(fn)` maps each item with `fn` and then flattens one level. Use `flatMap` when each item expands into several results, such as splitting sentences into words.

**Q4: Why does the stack version push children in reverse?**
A4: A stack is last in, first out. Pushing children from last to first makes the first child the next one popped, so the original left-to-right order is kept.

**Q5: What is the time complexity?**
A5: O(n), where n is the total number of values and arrays. Every node is visited once. The output and the stack together use O(n) space in the worst case.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need one flat list from grouped API data (sections, categories, line items)
- The nesting depth is unknown or changes between responses
- You want to limit how many levels are opened, using a depth argument

❌ Avoid when:
- The structure is an object, not an array; use an object flatten instead (topic 178)
- Order of items does not matter and you only need unique values; a `Set` may be simpler
- The data is so large that a streaming parser should handle it without building one big array

---

## 📊 Visual Diagram
```
Input:  [1, [2, [3, [4]]], 5]

Stack (top on the right, pop takes from the top):
  push 5, [2,[3,[4]]], 1         -> pop 1  -> result: [1]
  pop [2,[3,[4]]]  open it       -> push [3,[4]], 2
  pop 2                          -> result: [1, 2]
  pop [3,[4]]      open it       -> push [4], 3
  pop 3                          -> result: [1, 2, 3]
  pop [4]          open it       -> push 4
  pop 4                          -> result: [1, 2, 3, 4]
  pop 5                          -> result: [1, 2, 3, 4, 5]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Recursion | A function calling itself on smaller input | Function का खुद को smaller input पर call करना |
| Explicit stack | A manual list used instead of the call stack | Call stack की जगह अपनी list |
| Depth | How many array levels are opened | कितनी array levels खोली गईं |
| Base case | The condition where recursion stops | वह शर्त जहाँ recursion रुकता है |
| Sparse hole | An empty slot in an array, like `[, 1]` | Array में खाली slot |
| Spread (`...`) | Expands an array into separate values | Array को अलग-अलग values में बदलना |

---

## ⚡ 3-Line Summary
English:
1. Flatten opens every nested array and keeps the plain values in their original order.
2. Use `Array.isArray` to detect arrays, and use a depth limit or a stack when nesting is deep.
3. `concat` and `flat()` open only one level by default, so pass `Infinity` for a full flatten.

Hindi:
1. Flatten हर nested array को खोलता है और plain values को उनके मूल क्रम में रखता है।
2. Array पहचानने के लिए `Array.isArray` इस्तेमाल करो, और गहरी nesting में depth limit या stack रखो।
3. `concat` और `flat()` डिफ़ॉल्ट रूप से एक ही level खोलते हैं, इसलिए पूरा flatten करने के लिए `Infinity` दो।

---

## ➡️ Next Topic
**170. Deep Clone an Object** — after flattening arrays, the next problem is copying nested data safely, so that changing the copy never changes the original.
