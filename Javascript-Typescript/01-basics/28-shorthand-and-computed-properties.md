# 28. Shorthand Properties + Computed Properties
# हिंदी में: Shorthand Properties और Computed Properties — Object literal को छोटा और dynamic बनाना

---

## 🔵 Simple Definition (English)
Shorthand properties let you write `{ name }` instead of `{ name: name }` when the key and the variable have the same name. Computed properties let you use `[expression]` as a key, so the key is decided at runtime.

## 🔵 सरल परिभाषा (Hindi)
Shorthand property में `{ name: name }` की जगह सिर्फ़ `{ name }` लिखते हैं, जब key और variable का नाम एक हो। Computed property में `[expression]` को key बनाया जाता है, यानी key runtime पर तय होती है।

---

## 🔴 Problem it Solves
Object literals used to repeat names: `{ name: name, city: city }`. Building objects with dynamic keys needed extra steps: create `{}` first, then `obj[key] = value` on the next line. This made config objects, form state and lookup tables verbose.

## 🔴 यह क्यों बना? (Hindi)
Object में `{ name: name, city: city }` जैसा दोहराव होता था। Dynamic key वाले object बनाने के लिए पहले खाली `{}` बनाना पड़ता था और फिर अगली line में `obj[key] = value` लिखना पड़ता था। Form state, config और lookup tables लंबे हो जाते थे।

---

## 🟢 How it Works — Step by Step

Step 1 → `{ name }` expands to `{ name: name }` — the variable name becomes the key.
Step 2 → Method shorthand `greet() {}` is the same as `greet: function () {}`.
Step 3 → `[expr]` is evaluated when the object is created; its string value becomes the key.
Step 4 → If two keys are the same, the last one wins and keeps the first position.
Step 5 → Symbol keys are hidden from `Object.keys`, `for...in` and `JSON.stringify`.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → `{ name }` का मतलब है `{ name: name }`, यानी variable का नाम ही key बनता है।
चरण 2 → Method shorthand `greet() {}` वैसा ही है जैसे `greet: function () {}`।
चरण 3 → `[expr]` object बनते समय evaluate होता है, और उसकी string value key बनती है।
चरण 4 → एक ही key दो बार आए तो आख़िरी value जीतती है, और key अपनी पहली जगह रखती है।
चरण 5 → Symbol keys `Object.keys`, `for...in` और `JSON.stringify` में नहीं दिखतीं।

---

## 🟡 Real World Example
A food-delivery app builds a filter query from user choices. The key names depend on the chosen filter, so computed keys are the natural fit.

```javascript
// Filter chosen by the user at runtime
const filterBy = "cuisine";                // "cuisine" or "rating" from UI
const cuisine = "South Indian";            // selected value
// Shorthand + computed: key comes from filterBy, value from the variable cuisine
const query = { city: "Pune", [filterBy]: cuisine }; // { city: 'Pune', cuisine: 'South Indian' }
```

Razorpay-style checkout also builds fields such as `{ [`${type}_id`]: id }` for different entity types.

## 🟡 Real Example Hindi mein
Food delivery app में user filter चुनता है, तो key का नाम runtime पर तय होता है। `{ city: "Pune", [filterBy]: cuisine }` में `filterBy` की value key बनती है और `cuisine` variable की value उसका मान। Razorpay जैसे checkout में भी `{ [`${type}_id`]: id }` जैसे fields बनते हैं।

---

## 💻 Code Example — Basic
```javascript
// Shorthand + Computed properties — basic examples
// Run: node 28-shorthand-and-computed-properties.js

// 1. Shorthand property: variable name becomes the key
const name = "Aditya";            // a variable
const city = "Mumbai";            // another variable
const user = { name, city };      // same as { name: name, city: city }
console.log(user);                // { name: 'Aditya', city: 'Mumbai' }

// 2. Method shorthand: no "function" keyword needed
const cart = {
  items: 0,                       // number of items in the cart
  add(qty) {                      // same as add: function (qty) { ... }
    this.items += qty;            // this = cart when called as cart.add()
    return this.items;           // return the new count
  },
};
console.log(cart.add(2));         // 2
console.log(cart.add(3));         // 5

// 3. Computed property name: [expression] becomes the key
const field = "email";            // a runtime value decides the key
const form = { [field]: "a@b.com", [`${field}Verified`]: false }; // two computed keys
console.log(form);                // { email: 'a@b.com', emailVerified: false }

// 4. Computed key from a function result
const today = new Date("2024-01-15T00:00:00Z").toISOString().slice(0, 10); // "2024-01-15"
const dailyCounter = { [`orders_${today}`]: 42 }; // key is "orders_2024-01-15"
console.log(dailyCounter);        // { 'orders_2024-01-15': 42 }

// 5. Computed method name
const action = "greet";           // the method name comes from a variable
const bot = {
  [action]() { return "Hello from bot!"; }, // method is named "greet"
};
console.log(bot.greet());         // Hello from bot!

// 6. Symbol as a computed key: unique and hidden from normal key listing
const SECRET = Symbol("secret");  // create a unique symbol
const vault = { [SECRET]: "hidden", visible: true }; // symbol key + string key
console.log(Object.keys(vault));  // [ 'visible' ] — symbol not listed
console.log(vault[SECRET]);       // hidden — still accessible with the symbol
```

## 💻 Code Example — Advanced
```javascript
// Advanced: production-style patterns with shorthand and computed keys

// 1. Build a lookup table from an array (very common in API code)
const restaurants = [
  { id: "r1", name: "Biryani House", city: "Mumbai" }, // first record
  { id: "r2", name: "Dosa Corner", city: "Pune" },     // second record
];
// reduce builds an object keyed by id; mutating acc is O(n) (spreading would be O(n^2))
const byId = restaurants.reduce((acc, r) => {
  acc[r.id] = r;                  // computed key: the id of each restaurant
  return acc;                     // return the same accumulator every time
}, {});
console.log(Object.keys(byId));   // [ 'r1', 'r2' ]
console.log(byId.r2.name);        // Dosa Corner

// 2. Group orders by status with computed keys
const orders = [
  { id: 1, status: "delivered" }, // order 1
  { id: 2, status: "cancelled" }, // order 2
  { id: 3, status: "delivered" }, // order 3
];
const grouped = orders.reduce((acc, order) => {
  acc[order.status] ??= [];       // create the group array the first time (Node 15+)
  acc[order.status].push(order.id); // push the id into the right group
  return acc;                     // keep the accumulator
}, {});
console.log(grouped);             // { delivered: [ 1, 3 ], cancelled: [ 2 ] }

// 3. Immutable update: return a NEW object with one field changed
function withField(obj, key, value) {
  return { ...obj, [key]: value }; // spread copies, then computed key overrides
}
const base = { status: "preparing", eta: 20 }; // original object
const next = withField(base, "eta", 15);       // new object with eta 15
console.log(base.eta, next.eta);               // 20 15 — base is untouched

// 4. Whitelist dynamic keys before using them (security practice)
const ALLOWED_FIELDS = ["status", "eta"];      // only these may be updated
function updateOrder(order, field, value) {
  if (!ALLOWED_FIELDS.includes(field)) {       // reject unknown keys
    throw new Error(`Field not allowed: ${field}`);
  }
  return { ...order, [field]: value };         // safe: field is whitelisted
}
try {
  console.log(updateOrder(base, "eta", 10));   // { status: 'preparing', eta: 10 }
  updateOrder(base, "__proto__", "x");         // blocked before any change happens
} catch (err) {
  console.log("Blocked:", err.message);        // Blocked: Field not allowed: __proto__
}

// 5. Shorthand method that reads other properties through this
const paymentService = {
  retries: 3,                                  // config value
  describe() { return `Retries: ${this.retries}`; }, // this = paymentService
};
console.log(paymentService.describe());        // Retries: 3
```

---

## 🟠 Express.js Integration
Express does not use computed keys internally. Your route handlers use shorthand to build response objects, and computed keys to set header names dynamically.

```javascript
const express = require("express");          // import Express
const app = express();                       // create the app
app.use(express.json());                     // parse JSON bodies

const SERVICE = "orders";                    // name used in header
const orders = { o1: { status: "preparing", eta: 20 } }; // demo in-memory store

// Middleware: add a version header whose NAME is computed
app.use((req, res, next) => {
  res.set({ [`X-${SERVICE}-Version`]: "1.0" }); // header: X-orders-Version
  next();                                    // continue to the route
});

app.get("/api/orders/:id", (req, res) => {
  const id = req.params.id;                  // read id from the URL
  const order = orders[id];                  // look up the order
  if (!order) return res.status(404).json({ error: "Not found" });
  // Shorthand: { id } means { id: id }. Spread adds the rest of the order
  res.json({ id, ...order, servedBy: process.pid });
});

app.listen(3000);                            // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting the brackets for a computed key
✅ Correct: `[field]` uses the variable's value. `field` alone is a literal key.

```javascript
// Wrong
const field = "email";
const form = { field: "a@b.com" };   // key is literally "field"
console.log(form.email);             // undefined

// Right
const form2 = { [field]: "a@b.com" }; // key is the value of field: "email"
console.log(form2.email);            // a@b.com
```

❌ Mistake 2: Using an object as a computed key
✅ Correct: Object keys must be strings or symbols. Objects become `"[object Object]"`.

```javascript
// Wrong
const userA = { id: 1 };
const userB = { id: 2 };
const cache = { [userA]: "first", [userB]: "second" };
console.log(cache);                  // { '[object Object]': 'second' } — both collapsed

// Right: use a Map when keys are objects
const cacheMap = new Map([[userA, "first"], [userB, "second"]]);
console.log(cacheMap.get(userA));    // first
```

❌ Mistake 3: Letting user input choose any key
✅ Correct: Whitelist allowed keys. Otherwise a client can send `__proto__` or overwrite fields you never meant to expose.

```javascript
// Wrong
function update(obj, key, value) {
  return { ...obj, [key]: value }; // any key accepted, including unexpected ones
}

// Right
const ALLOWED = ["status", "eta"];
function updateSafe(obj, key, value) {
  if (!ALLOWED.includes(key)) throw new Error("Field not allowed");
  return { ...obj, [key]: value };
}
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print? (non-strict script)
const key = "a";
const obj = { a: 1, [key]: 2, a: 3, ["b" + 1]: 4 };  // (1) duplicates and computed keys
console.log(obj);

const sym = Symbol("s");
const o2 = { [sym]: "x", y: 1 };                       // (2) symbol key
console.log(Object.keys(o2), JSON.stringify(o2));

console.log({ ["1"]: "one", 1: "uno" }[1]);            // (3) numeric key vs string key
```
Answer:
```
{ a: 3, b1: 4 }             ← (1) "a" appears 3 times in the literal; last value wins
[ 'y' ] {"y":1}             ← (2) Object.keys and JSON skip symbol keys
uno                         ← (3) 1 and "1" are the same key; the later one wins
```
Explanation: In an object literal, duplicate keys are allowed (even in strict mode). The key `a` keeps its first position but takes the last value, `3`. Computed `["b" + 1]` becomes the key `b1`. Symbols are a separate key type, so they never appear in `Object.keys` or `JSON.stringify`. Numeric keys are converted to strings, so `1` and `"1"` collide.

---

## ⚫ Interview Questions + Answers

Q1: What is shorthand property syntax?
A1: When the key and variable have the same name, you can write `{ name }` instead of `{ name: name }`. It works for functions too, and it keeps object creation short.

Q2: What is the difference between method shorthand and an arrow function property?
A2: `greet() {}` gets its own `this`, decided by how it is called. An arrow function `greet: () => {}` does not have its own `this`; it uses the `this` of the surrounding scope. For object methods that read other properties, use method shorthand.

Q3: Can a computed key be any expression?
A3: Yes. Anything inside `[ ]` is evaluated when the object is created. The result is converted to a string (or stays a symbol) and used as the key.

Q4: Why are Symbol keys useful?
A4: A symbol is always unique, so it cannot collide with a string key. It is also hidden from `Object.keys`, `for...in` and `JSON.stringify`, which is useful for internal metadata.

Q5: What happens when the same key appears twice?
A5: The last value wins, but the key keeps the position of its first appearance. Object keys are unique, so the earlier value is overwritten.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Building response objects from variables (`res.json({ id, status })`)
- The key name is decided at runtime (filters, headers, per-entity fields)
- Creating immutable updates like `{ ...obj, [key]: value }`

❌ Avoid when:
- Keys come from untrusted input without a whitelist
- You need object-valued keys; use a `Map` instead
- The computed key makes code hard to read; a simple `if` may be clearer

---

## 📊 Visual Diagram
```
const name = "A";
const obj  = { name, [key]: val, greet() { ... } };
               │      │             │
               │      │             └── method shorthand (no "function")
               │      └──────────────── computed key: key evaluated first
               └─────────────────────── shorthand: name: name

Runtime with key = "city", val = 99:
   { name: "A", city: 99, greet: [function] }
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Shorthand property | `{ name }` for `{ name: name }` | छोटा property syntax |
| Method shorthand | `greet() {}` without `function` | बिना `function` वाला method |
| Computed property | `[expr]` used as a key | Runtime पर बनी key |
| Symbol key | Unique key that is hidden from normal listing | छुपी हुई unique key |
| Duplicate key | Same key repeated; last value wins | दोहराई गई key |
| Whitelist | Only allowed values are accepted | अनुमति वाली सूची |
| Accumulator | The object built inside `reduce` | `reduce` में बनने वाला object |

---

## ⚡ 3-Line Summary
**English:**
1. `{ name }` is shorthand for `{ name: name }`; `greet() {}` is shorthand for a method.
2. `[expr]` lets the key be computed at runtime, and it can be a string or a symbol.
3. Whitelist dynamic keys from user input, and use `Map` when keys are objects.

**Hindi:**
1. `{ name }`, `{ name: name }` का shorthand है; `greet() {}` method का shorthand है।
2. `[expr]` से key runtime पर बनती है, और वह string या symbol हो सकती है।
3. User input से आने वाली dynamic keys को whitelist करो, और object keys के लिए `Map` इस्तेमाल करो।

---

## ➡️ Next Topic
**29. Strings — Methods** — `slice`, `split`, `replace`, `padStart` और दूसरे string methods। Object keys अक्सर strings होती हैं, इसलिए अगला topic उन्हें सही तरीके से handle करना सिखाएगा।
