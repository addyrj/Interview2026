# 190. Implement Array.map, filter, reduce
# हिंदी में: Array.map, filter, reduce बनाना — Data बदलने के तीन मूल तरीके

---

## 🔵 Simple Definition (English)
`map` builds a new array by transforming every item. `filter` builds a new array with only the items that pass a test. `reduce` combines all items into one value, such as a sum, an object, or a new array. None of them change the original array.

## 🔵 सरल परिभाषा (Hindi)
`map` हर item को बदलकर एक नई array बनाता है। `filter` सिर्फ़ उन items की नई array बनाता है जो शर्त पास करते हैं। `reduce` सभी items को मिलाकर एक value बनाता है, जैसे sum, object या कोई नई array। ये तीनों original array को नहीं बदलते।

---

## 🔴 Problem it Solves
**Problem Statement:** Implement `myMap`, `myFilter`, and `myReduce` as methods on `Array.prototype`. They must call the callback with `(item, index, array)`, skip holes in sparse arrays, respect an optional `thisArg` for `map` and `filter`, and support an initial value for `reduce`. An empty array with no initial value must throw.

Before these methods, developers wrote loops for every transformation: a loop to double prices, another to keep veg items, and another to sum totals. Each loop repeated the same index logic and was easy to get wrong. These three methods express the intent directly, and they are the base of almost all data processing in Node APIs.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `Array.prototype` पर `myMap`, `myFilter` और `myReduce` बनाओ। Callback को `(item, index, array)` के साथ call करो, sparse arrays में holes को skip करो, `map` और `filter` में `thisArg` का सम्मान करो, और `reduce` में initial value सँभालो। खाली array और initial value न हो, तो throw करो।

इन methods से पहले हर transformation के लिए loop लिखा जाता था: prices double करने का loop, veg items रखने का loop, और totals जोड़ने का loop। हर loop में वही index का झंझट था और गलती आसानी से होती थी। ये तीन methods इरादा सीधे लिखते हैं, और Node APIs में ज़्यादातर data processing इन्हीं पर टिकी है।

---

## 🟢 How it Works — Step by Step

Step 1 → Check that the callback is a function; otherwise throw a TypeError.
Step 2 → Loop from index 0 to `length - 1`.
Step 3 → Skip holes with `i in this`, as the built-in does.
Step 4 → `map` stores each callback result at the same index in a new array.
Step 5 → `filter` pushes the item into a new array only when the callback returns a truthy value.
Step 6 → `reduce` starts from the initial value (or from the first item) and folds each item into an accumulator.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → जाँचो कि callback function है; वरना TypeError दो।
Step 2 → Index 0 से `length - 1` तक loop चलाओ।
Step 3 → Holes को `i in this` से skip करो, जैसे built-in करता है।
Step 4 → `map` हर callback का result नई array में उसी index पर रखता है।
Step 5 → `filter` item को नई array में तभी डालता है जब callback truthy value लौटाए।
Step 6 → `reduce` initial value (या पहले item) से शुरू करता है और हर item को accumulator में मिलाता है।

---

## 🟡 Real World Example
Swiggy's cart page uses `filter` to show only veg items when the user turns on the veg filter, `map` to build the list of item names for the order summary, and `reduce` to add up the bill. Flipkart's order service does the same to compute the grand total from line items.

Scenario: A cart has three items: Biryani (250), Dosa (90), and Paneer Tikka (180). The veg filter keeps Dosa and Paneer Tikka. `map` produces their names, and `reduce` gives the bill total of 270 for the veg items.

## 🟡 Real Example Hindi mein
Swiggy के cart page पर veg filter चालू होने पर `filter` सिर्फ़ veg items दिखाता है, order summary के लिए `map` नामों की list बनाता है, और `reduce` bill का total जोड़ता है। Flipkart का order service भी line items से grand total इसी तरह निकालता है।

उदाहरण: Cart में तीन items हैं: Biryani (250), Dosa (90), Paneer Tikka (180)। Veg filter Dosa और Paneer Tikka रखता है। `map` उनके नाम देता है, और `reduce` veg items का bill total 270 देता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: plain functions that take an array, showing the loop behind each method
function basicMap(arr, fn) {
  const out = [];                                 // the new array we will return
  for (let i = 0; i < arr.length; i++) {          // visit every index
    out.push(fn(arr[i], i, arr));                 // store the transformed value
  }
  return out;                                     // the new array, original untouched
}

function basicFilter(arr, fn) {
  const out = [];                                 // the new array of kept items
  for (let i = 0; i < arr.length; i++) {          // visit every index
    if (fn(arr[i], i, arr)) out.push(arr[i]);     // keep the item only when the test is truthy
  }
  return out;                                     // the filtered array
}

function basicReduce(arr, fn, start) {
  let acc = start;                                // the running total, starting from the initial value
  for (let i = 0; i < arr.length; i++) {          // visit every index
    acc = fn(acc, arr[i], i, arr);                // fold the current item into the accumulator
  }
  return acc;                                     // the final combined value
}

const prices = [250, 90, 180];                    // item prices in rupees
console.log(basicMap(prices, (p) => p * 2).join(",")); // Expected output: 500,180,360
console.log(basicFilter(prices, (p) => p > 100).join(",")); // Expected output: 250,180
console.log(basicReduce(prices, (sum, p) => sum + p, 0));   // Expected output: 520
```

## 💻 Code Example — Advanced
```javascript
// Advanced: myMap, myFilter, myReduce on Array.prototype, with holes and thisArg handled

// myMap: a new array with the callback result for every present index
Array.prototype.myMap = function (callback, thisArg) {
  // Guard: the callback must be a function
  if (typeof callback !== "function") throw new TypeError(`${callback} is not a function`);
  const result = new Array(this.length);          // same length, so holes stay holes
  for (let i = 0; i < this.length; i++) {         // visit each index
    if (i in this) {                              // skip holes, as the built-in does
      result[i] = callback.call(thisArg, this[i], i, this); // call with thisArg, item, index, array
    }
  }
  return result;                                  // the new array
};

// myFilter: a new array with only the items where the callback returns a truthy value
Array.prototype.myFilter = function (callback, thisArg) {
  if (typeof callback !== "function") throw new TypeError(`${callback} is not a function`);
  const result = [];                              // the kept items
  for (let i = 0; i < this.length; i++) {         // visit each index
    if (i in this && callback.call(thisArg, this[i], i, this)) { // present and passes the test
      result.push(this[i]);                       // keep it
    }
  }
  return result;                                  // the filtered array
};

// myReduce: fold the array into one value; uses the first item when no initial value is given
Array.prototype.myReduce = function (callback, ...init) {
  if (typeof callback !== "function") throw new TypeError(`${callback} is not a function`);
  let i = 0;                                      // the index we are at
  let acc;                                        // the accumulator
  if (init.length > 0) {                          // an initial value was passed (even if it is undefined)
    acc = init[0];                                // start from it
  } else {
    while (i < this.length && !(i in this)) i++;  // skip leading holes to find the first real item
    if (i >= this.length) throw new TypeError("Reduce of empty array with no initial value");
    acc = this[i];                                // the first real item becomes the start
    i++;                                          // continue from the next index
  }
  for (; i < this.length; i++) {                  // fold each remaining present item
    if (i in this) acc = callback(acc, this[i], i, this); // new accumulator from the callback
  }
  return acc;                                     // the final value
};

// ---- Tests: run with plain node ----
const orders = [                                  // sample cart items
  { item: "Biryani", price: 250, veg: false },
  { item: "Dosa", price: 90, veg: true },
  { item: "Paneer Tikka", price: 180, veg: true },
];
console.log(orders.myMap((o) => o.price).join(" ")); // Expected output: 250 90 180
console.log(orders.myFilter((o) => o.veg).myMap((o) => o.item).join(",")); // Expected output: Dosa,Paneer Tikka
console.log(orders.myReduce((sum, o) => sum + o.price, 0)); // Expected output: 520
console.log([1, 2, 3].myReduce((a, b) => a + b));  // Expected output: 6
console.log([1, , 3].myMap((x) => x * 2).hasOwnProperty(1)); // Expected output: false (hole kept)
console.log([1, 2, 3].myFilter(function (x) { return x > this.min; }, { min: 1 }).join(",")); // Expected output: 2,3
console.log([].myReduce((a, b) => a + b, "start")); // Expected output: start
try {
  [].myReduce((a, b) => a + b);                   // no initial value on an empty array
} catch (err) {
  console.log(err.message);                       // Expected output: Reduce of empty array with no initial value
}

// Time:  O(n) for each method (one pass over the array; reduce does one callback per item)
// Space: O(n) for map and filter results; O(1) extra for reduce unless the accumulator grows
```

### Edge Cases
```javascript
// These checks use the native methods; our versions must return the same results

// Edge 1: map on an empty array returns an empty array, not undefined
console.log(JSON.stringify([].map((x) => x)));    // Expected output: []

// Edge 2: the callback receives the index and the whole array as extra arguments
console.log(["a", "b"].map((v, i, arr) => i + arr.length).join(",")); // Expected output: 2,3

// Edge 3: filter with Boolean removes all falsy values
console.log([0, "", 1, null, "x"].filter(Boolean).join(",")); // Expected output: 1,x

// Edge 4: reduce with an initial value on an empty array returns that value
console.log([].reduce((a, b) => a + b, 0));       // Expected output: 0

// Edge 5: map keeps holes as holes
console.log(1 in [1, , 3].map((x) => x * 2));     // Expected output: false
```

---

## 🟠 Express.js Integration
In an Express API, these methods shape data before it leaves the server. An endpoint can filter orders by a query parameter, map them to a response shape, and reduce them to totals. The example uses the built-in methods, which are what you would ship; the custom ones above are for interviews.

```javascript
// Express.js: an order summary endpoint built from filter, map, and reduce
const express = require("express");               // import Express
const app = express();                            // create the app

// Sample orders (in a real app this comes from the database)
const orders = [
  { id: 1, item: "Biryani", price: 250, veg: false, status: "delivered" }, // one order
  { id: 2, item: "Dosa", price: 90, veg: true, status: "delivered" },      // another order
  { id: 3, item: "Paneer Tikka", price: 180, veg: true, status: "pending" }, // a pending order
];

// GET /api/orders/summary?veg=true&status=delivered
app.get("/api/orders/summary", (req, res) => {
  const wantVeg = req.query.veg;                  // read the optional veg filter from the query
  const wantStatus = req.query.status;            // read the optional status filter
  const selected = orders
    .filter((o) => wantVeg === undefined || o.veg === (wantVeg === "true")) // keep veg orders when asked
    .filter((o) => !wantStatus || o.status === wantStatus);                  // keep matching status when asked

  const names = selected.map((o) => o.item);      // the item names for the response
  const total = selected.reduce((sum, o) => sum + o.price, 0); // add up the prices, starting at 0

  res.json({ count: selected.length, names, total }); // 200 OK with the summary
});

// Start the server on PORT from the environment, or 3000 by default
app.listen(process.env.PORT || 3000, () => {
  console.log("Order summary API running");     // ready message
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using a block body in `map` and forgetting `return`
✅ **Correct:** Return the value, either with an expression body or an explicit `return`

```javascript
// Wrong: the block body does not return, so every result is undefined
const doubledWrong = [1, 2].map((x) => { x * 2; });   // the value is computed and thrown away
console.log(doubledWrong);                             // Expected output: [ undefined, undefined ]

// Right: return the value explicitly (or use an expression body)
const doubledRight = [1, 2].map((x) => { return x * 2; }); // explicit return
console.log(doubledRight.join(","));                   // Expected output: 2,4
```

❌ **Mistake 2:** Calling `reduce` on an empty array without an initial value
✅ **Correct:** Always pass an initial value when the array might be empty

```javascript
// Wrong: with no initial value, reduce has no first item to start from and throws
try {
  const empty = [];                                    // an empty cart
  console.log(empty.reduce((sum, p) => sum + p));      // throws TypeError
} catch (err) {
  console.log(err.name);                               // Expected output: TypeError
}

// Right: start from 0, so an empty cart gives a total of 0
const safeTotal = [].reduce((sum, p) => sum + p, 0);   // initial value 0
console.log(safeTotal);                                // Expected output: 0
```

---

## 🧠 Tricky Interview Question
```javascript
const arr = [1, , 3];                                  // array with a hole at index 1
console.log(arr.map((x) => x * 2));                    // ?
console.log(arr.reduce((a, b) => a + b));              // ?
console.log([1, 2, 3].filter((x) => x > 1).length, [3, 1, 2].reduce((a, b) => (a > b ? a : b))); // ?
```
Answer: `[ 2, <1 empty item>, 6 ]`, `4`, and `2 3`.
`map` skips the hole, so the result keeps a hole at index 1 instead of putting `undefined` there. `reduce` with no initial value skips the hole too, so it starts from `1` and adds `3`, giving `4`. The last line prints the filtered length (`2`) and the largest value (`3`). The lesson: holes are skipped by these methods, and `reduce` without an initial value uses the first real item.

---

## ⚫ Interview Questions + Answers

**Q1: Why does `map` always return an array of the same length?**
A1: It stores one result per index. Holes stay holes, so the length is the same as the input length.

**Q2: How is `filter` different from `find`?**
A2: `filter` returns every item that passes the test, as a new array. `find` returns only the first match, or `undefined`.

**Q3: What is the accumulator in `reduce`?**
A3: The value carried from one call to the next. It starts as the initial value or the first item, and the callback returns the new accumulator each time.

**Q4: Why is `i in this` used instead of checking the value?**
A4: `in` detects holes in sparse arrays, which are missing indices. A value check would wrongly skip real `undefined` or `null` items.

**Q5: What is the time complexity of these methods?**
A5: O(n), because each method visits each index once. The callback's own cost adds to it.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You transform, select, or summarise a list in memory (prices, names, totals)
- You want code that states the intent instead of index bookkeeping
- You chain steps such as `filter` then `map` then `reduce` on small or medium lists

❌ Avoid when:
- The list is huge and you only need the first match; use a loop or `find` that stops early
- You chain many passes over a very large array; each pass creates a new array, so combine steps or use a single loop
- You need to change the original array in place; these methods return new arrays, so use a loop or `splice`

---

## 📊 Visual Diagram
```
input:   [ 250, 90, 180 ]          (Biryani, Dosa, Paneer)

map(x => x * 2)
          [ 500, 180, 360 ]         same length, new values

filter(x => x > 100)
          [ 250, 180 ]              shorter, only passing items

reduce((sum, x) => sum + x, 0)
  acc: 0 -> 250 -> 340 -> 520       one final value

Original array: [ 250, 90, 180 ]    unchanged in all three cases
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Callback | Function passed to another function | दूसरे function को दिया गया function |
| Transform | Turn each item into a new value | हर item को नई value में बदलना |
| Predicate | A callback that returns true or false | True या false लौटाने वाला callback |
| Accumulator | The running value inside `reduce` | `reduce` के अंदर चलने वाली value |
| Sparse array | An array with missing indices (holes) | ऐसी array जिसमें कुछ indices खाली हों |
| `thisArg` | The value of `this` inside the callback | Callback के अंदर `this` की value |
| Immutable update | Returning a new array instead of changing the old one | पुरानी array बदलने के बजाय नई array लौटाना |

---

## ⚡ 3-Line Summary
English:
1. `map` transforms every item, `filter` keeps items that pass a test, and `reduce` folds them into one value.
2. All three return new values, visit each index once (O(n)), and skip holes in sparse arrays.
3. Always return a value from `map`, and give `reduce` an initial value when the array may be empty.

Hindi:
1. `map` हर item बदलता है, `filter` शर्त पास करने वाले items रखता है, और `reduce` उन्हें एक value में मिलाता है।
2. तीनों नई values लौटाते हैं, हर index पर एक बार चलते हैं (O(n)), और sparse arrays के holes को skip करते हैं।
3. `map` से हमेशा value लौटाओ, और array खाली हो सकती हो तो `reduce` को initial value दो।

---

## ➡️ Next Topic
**193. Event Loop Output Questions** — topics 191 and 192 are not in this repo yet, so this is the next written topic. With array transforms done, you can now trace how callbacks and promises are scheduled, which is the next big source of interview output questions.
