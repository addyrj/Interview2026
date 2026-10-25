# 170. Deep Clone an Object
# हिंदी में: Object की Deep Clone बनाना — Nested Data, Cycles और JSON trick की सीमाएँ

---

## 🔵 Simple Definition (English)
A deep clone is a full copy of an object, including every nested object and array. Changing the copy never changes the original. You build it by walking the structure and copying each level, instead of copying only the top level.

## 🔵 सरल परिभाषा (Hindi)
Deep clone का मतलब है object की पूरी copy, जिसमें हर nested object और array भी शामिल हों। Copy बदलने से original नहीं बदलता। इसके लिए हम structure में नीचे तक जाकर हर level की copy बनाते हैं, सिर्फ़ ऊपर की level नहीं।

---

## 🔴 Problem it Solves
**Problem Statement:** Given any plain JavaScript value (objects, arrays, dates, maps, sets, nested up to any depth, possibly with cycles), return a copy that shares no mutable parts with the original. Primitive values are returned as they are.

A shallow copy with `{ ...obj }` copies only the first level. Nested objects are still shared, so a change in one place shows up in the other. In a cart or a form state, this causes bugs that are hard to trace, because the UI changes even though nobody updated it.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** कोई भी JavaScript value दी हो (objects, arrays, dates, maps, sets, कितनी भी गहराई तक, और हो सकता है cycles भी हों), तो उसकी ऐसी copy लौटाओ जिसके mutable हिस्से original से साझा न हों। Primitive values सीधे लौटा दो।

`{ ...obj }` से सिर्फ़ पहली level copy होती है। अंदर के objects अभी भी साझा रहते हैं, तो एक जगह बदलाव दूसरी जगह दिख जाता है। Cart या form state में यह ऐसी bug देता है जिसे ढूँढना मुश्किल है, क्योंकि UI बदल जाता है और किसी ने update नहीं किया।

---

## 🟢 How it Works — Step by Step

Step 1 → If the value is a primitive or `null`, return it (primitives are already copied by value).
Step 2 → If it is an array, create a new array and deep clone each element.
Step 3 → If it is an object, create a new object with the same prototype.
Step 4 → Copy each own key, cloning its value recursively.
Step 5 → Remember every object you already cloned, so a cycle stops instead of looping forever.
Step 6 → Return the new copy.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → अगर value primitive या `null` है, तो उसे लौटा दो (primitives पहले से value से copy होते हैं)।
Step 2 → अगर वह array है, तो नई array बनाओ और हर element की deep clone करो।
Step 3 → अगर वह object है, तो उसी prototype वाला नया object बनाओ।
Step 4 → हर own key को copy करो, और उसकी value की recursively clone करो।
Step 5 → जो objects clone हो चुके हैं उन्हें याद रखो, ताकि cycle में फँसकर loop न चले।
Step 6 → नई copy लौटा दो।

---

## 🟡 Real World Example
Swiggy's cart state holds items, a delivery address, and applied coupons. When the user tries a coupon, the app makes a "preview" copy of the cart, so the real cart does not change until the user confirms. Razorpay's checkout builds a deep copy of the order payload before it adds the fee breakdown. The original order object must stay the same for audit logs.

Scenario: A cart has `items[0].qty = 2`. The preview adds one more dish to the copy only. The real cart still shows 2 dishes, and the preview shows 3.

## 🟡 Real Example Hindi mein
Swiggy की cart state में items, delivery address और applied coupons होते हैं। जब user coupon try करता है, तो app cart की एक "preview" copy बनाता है, ताकि user confirm न करे तब तक असली cart न बदले। Razorpay checkout भी fee breakdown जोड़ने से पहले order payload की deep copy बनाता है, क्योंकि audit log के लिए original object वैसा ही रहना चाहिए।

उदाहरण: Cart में `items[0].qty = 2` है। Preview में सिर्फ़ copy में एक dish जुड़ती है। असली cart में 2 dishes रहती हैं, और preview में 3 दिखती हैं।

---

## 💻 Code Example — Basic
```javascript
// Basic: recursive deep clone for plain objects and arrays
function deepCloneBasic(value) {
  if (value === null || typeof value !== "object") return value; // primitives and null are copied by value already
  if (Array.isArray(value)) return value.map((item) => deepCloneBasic(item)); // clone each element of the array
  const copy = {};                            // a brand new empty object
  for (const key of Object.keys(value)) {     // every own enumerable key of the object
    copy[key] = deepCloneBasic(value[key]);   // clone the value under this key, recursively
  }
  return copy;                                // the new, independent object
}

// Sample: an order with nested items and an address
const order = { id: 7, items: [{ name: "Dosa", qty: 2 }], address: { city: "Pune" } };
const cloned = deepCloneBasic(order);         // make the copy
cloned.items[0].qty = 5;                      // change the copy only
cloned.address.city = "Delhi";                // change the copy only
console.log(order.items[0].qty, order.address.city);   // Expected output: 2 Pune
console.log(cloned.items[0].qty, cloned.address.city); // Expected output: 5 Delhi

// Edge cases: primitives and null are returned unchanged
console.log(deepCloneBasic(null), deepCloneBasic(42), deepCloneBasic("hi")); // Expected output: null 42 hi
```

## 💻 Code Example — Advanced
```javascript
// Advanced: handles Date, Map, Set, prototypes, symbols and circular references
function deepClone(value, seen = new WeakMap()) { // seen remembers copies made so far (cycle safety)
  if (value === null || typeof value !== "object") return value; // primitives and functions are returned as they are
  if (seen.has(value)) return seen.get(value);     // already copied: reuse the same copy so cycles stay cycles

  if (value instanceof Date) return new Date(value.getTime()); // a Date needs its own time value

  if (value instanceof Map) {                      // Map: clone every key and every value
    const map = new Map();                         // the new Map
    seen.set(value, map);                          // register it before recursing
    for (const [k, v] of value) map.set(deepClone(k, seen), deepClone(v, seen)); // copy each entry
    return map;
  }

  if (value instanceof Set) {                      // Set: clone every member
    const set = new Set();                         // the new Set
    seen.set(value, set);                          // register it before recursing
    for (const v of value) set.add(deepClone(v, seen)); // copy each member
    return set;
  }

  // Arrays get a new array; other objects keep their original prototype (class instances stay instances)
  const copy = Array.isArray(value) ? [] : Object.create(Object.getPrototypeOf(value));
  seen.set(value, copy);                           // register BEFORE recursing, so a cycle points back here
  for (const key of Reflect.ownKeys(value)) {      // own keys, including symbol keys
    copy[key] = deepClone(value[key], seen);       // clone each property value
  }
  return copy;                                     // the finished copy
}

// Test 1: a mix of types, plus a cycle (the object points to itself)
const user = { name: "Asha", joined: new Date(0), tags: new Set(["vip"]), scores: new Map([["math", 90]]) };
user.self = user;                                  // circular reference
const copy2 = deepClone(user);                     // deep copy
console.log(copy2 !== user, copy2.self === copy2); // Expected output: true true
// Test 2: the Date is a new object, not the same one
console.log(copy2.joined instanceof Date, copy2.joined !== user.joined); // Expected output: true true
// Test 3: Set and Map contents are copied
console.log(copy2.tags.has("vip"), copy2.scores.get("math"));           // Expected output: true 90

// Time:  O(n), where n is the number of values reachable from the input
// Space: O(n) for the copies plus the WeakMap that tracks what was copied
```

### Edge Cases
- `null`, numbers, strings and booleans are returned as they are.
- Functions are not cloned; the same function reference is kept, which is usually what you want.
- Circular references stay circular in the copy, so `copy.self === copy` is true.
- Class instances keep their prototype, so their methods still work.
- Non-enumerable properties are copied as ordinary properties in this version. Mention this if asked.

---

## 🟠 Express.js Integration
A restaurant service keeps a default cart template in memory. Each request needs a fresh copy of it, so one customer's changes never leak into another customer's cart.

```javascript
// Express.js: give every request its own copy of a shared default cart
const express = require("express");             // web framework
const app = express();                          // create the app
app.use(express.json());                        // parse JSON request bodies

// Shared template in memory: it must never be changed by a request
const DEFAULT_CART = { items: [{ sku: "A1", qty: 1, price: 250 }], coupon: null };

// POST /api/cart/preview  body: { "coupon": "FIRST50" }
app.post("/api/cart/preview", (req, res) => {
  // structuredClone is the built-in deep clone in modern Node (v17+); it handles Date, Map, Set and cycles
  const cart = structuredClone(DEFAULT_CART);   // private copy for this request only
  cart.coupon = req.body.coupon ?? null;        // apply the coupon to the copy
  if (cart.coupon === "FIRST50") {              // example rule: 50 percent off the first item
    cart.items[0].price = cart.items[0].price / 2; // change the copy, not DEFAULT_CART
  }
  res.json(cart);                               // 200 OK with the preview
});

// Start the server on PORT from the environment, or 3000
app.listen(process.env.PORT || 3000, () => {
  console.log("Cart API running");             // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `JSON.parse(JSON.stringify(x))` as a deep clone
✅ Correct: it turns Dates into strings, drops `undefined` and functions, turns `NaN` into `null`, and throws on cycles. Use a real deep clone or `structuredClone`.

```javascript
const data = { when: new Date(0), skip: undefined, n: NaN };

// Wrong: the Date is now a string, the undefined field is gone, and NaN became null
const bad = JSON.parse(JSON.stringify(data));
console.log(typeof bad.when, "skip" in bad, bad.n);       // Expected output: string false null

// Right: structuredClone keeps the Date object, the undefined field and NaN
const good = structuredClone(data);              // built-in deep clone (Node 17 and later)
console.log(good.when instanceof Date, "skip" in good, Number.isNaN(good.n)); // Expected output: true true true
```

❌ **Mistake 2:** Thinking the spread operator makes a deep copy
✅ Correct: `{ ...obj }` copies only the top level. Nested objects are shared.

```javascript
// Wrong: the nested items array is still shared between the two objects
const order = { items: [{ qty: 2 }] };
const shallow = { ...order };                   // only the top level is copied
shallow.items[0].qty = 9;                       // changes the shared nested object
console.log(order.items[0].qty);                // Expected output: 9

// Right: a deep clone creates new nested objects too
const original = { items: [{ qty: 2 }] };
const safe = structuredClone(original);         // built-in deep clone: nested objects are new too
safe.items[0].qty = 9;                          // change the copy only
console.log(original.items[0].qty);             // Expected output: 2
```

---

## 🧠 Tricky Interview Question
```javascript
const a = { n: 1, inner: { m: 2 } };
const b = { ...a };                              // shallow copy
b.inner.m = 99;                                  // change through the copy
console.log(a.inner.m);                          // ?

const c = JSON.parse(JSON.stringify({ d: new Date(0), u: undefined, n: NaN })); // ?
console.log(typeof c.d, c.u, c.n);               // ?
```
Answer:
```
99                     ← the spread copied only the top level, so inner is still shared
string undefined null  ← JSON turned the Date into text, removed u (so c.u is undefined), and turned NaN into null
```
Explain both traps: shallow copies share nested objects, and the JSON trick loses types. Interviewers want you to name these two limits, not only write the code.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between a shallow copy and a deep copy?**
A1: A shallow copy copies the first level only, so nested objects are shared. A deep copy copies every level, so the copy shares no mutable objects with the original.

**Q2: Why does a deep clone need a WeakMap or a Set of seen objects?**
A2: Circular references make the walk loop forever. Remembering which objects were already copied lets the clone return the existing copy at the second visit, so the cycle is preserved.

**Q3: What does `structuredClone` support, and what does it not?**
A3: It supports plain objects, arrays, Date, Map, Set, RegExp, typed arrays and cycles. It does not copy functions, class prototypes or DOM nodes. It throws a `DataCloneError` for functions.

**Q4: Why not use JSON for deep cloning?**
A4: JSON drops `undefined` and functions, turns Dates into strings, turns `NaN` and `Infinity` into `null`, does not keep Map or Set, and throws on cycles.

**Q5: What is the time complexity of a deep clone?**
A5: O(n), where n is the number of values reachable from the input. Every value is visited once. The extra space is the copy itself plus the map of seen objects.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need to change a copy of state (Redux reducers, form previews, undo history)
- A default template is shared, and each request needs its own version
- The data has nested objects and you must avoid side effects on the original

❌ Avoid when:
- The data is a large, flat list; a shallow copy with `[...list]` is faster and enough
- You only need to read the data; copying costs time and memory for no benefit
- The object holds resources such as sockets, file handles or DOM nodes; they cannot be copied meaningfully

---

## 📊 Visual Diagram
```
Original:  order ──► items ──► [ { qty: 2 } ]
                 └─► address ──► { city: "Pune" }

Shallow:   copy ──► items ──► [ { qty: 2 } ]   <- SAME nested objects (shared!)

Deep:      copy ──► items ──► [ { qty: 2 } ]   <- NEW nested objects (independent)
                 └─► address ──► { city: "Pune" }

seen map:  order -> copy   (a cycle back to order returns copy, not a new loop)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shallow copy | Copies only the top level | सिर्फ़ ऊपर की level की copy |
| Deep copy | Copies every nested level | हर nested level की copy |
| Circular reference | An object that points back to itself | ऐसा object जो खुद को ही refer करे |
| WeakMap | A map that does not keep its keys alive | ऐसा map जो keys को जीवित नहीं रखता |
| structuredClone | Built-in deep clone in modern Node | Node में built-in deep clone |
| Prototype | The object that a class instance inherits from | वह object जिससे instance methods लेता है |

---

## ⚡ 3-Line Summary
English:
1. A deep clone copies every nested level, so changing the copy never changes the original.
2. Track copied objects in a WeakMap, so circular references do not loop forever.
3. Avoid the JSON trick, because it loses Dates, functions, `undefined` and `NaN`; use `structuredClone` instead.

Hindi:
1. Deep clone हर nested level को copy करता है, इसलिए copy बदलने से original नहीं बदलता।
2. Copied objects को WeakMap में रखो, ताकि circular references में loop न बने।
3. JSON वाली trick मत लो, क्योंकि उसमें Date, functions, `undefined` और `NaN` खो जाते हैं; `structuredClone` इस्तेमाल करो।

---

## ➡️ Next Topic
**171. Implement debounce** — after cloning data safely, the next problem controls how often a function runs when a user types or resizes the window.
