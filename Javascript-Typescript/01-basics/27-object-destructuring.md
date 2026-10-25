# 27. Object Destructuring
# हिंदी में: Object Destructuring — Object से values को सीधे variables में निकालना

---

## 🔵 Simple Definition (English)
Object destructuring lets you pull values out of an object into variables in one line. The property names act as the guide: `const { name, age } = user;` creates `name` and `age` from `user.name` and `user.age`.

## 🔵 सरल परिभाषा (Hindi)
Object destructuring से किसी object की values को एक ही line में अलग-अलग variables में निकाला जा सकता है। Property का नाम ही variable का नाम बनता है। उदाहरण: `const { name, age } = user;`।

---

## 🔴 Problem it Solves
Before destructuring, every property needed its own line: `const name = user.name; const age = user.age;`. Deep data like `res.data.payment.id` had to be written again and again. Function options objects needed boilerplate such as `options.timeout ?? 5000` for every field. The code became long and easy to get wrong.

## 🔴 यह क्यों बना? (Hindi)
पहले हर property के लिए अलग line लिखनी पड़ती थी: `const name = user.name;`। Nested data जैसे `res.data.payment.id` बार-बार लिखना लंबा और गलती वाला था। Function में options object से values निकालने के लिए भी लंबा boilerplate लगता था।

---

## 🟢 How it Works — Step by Step

Step 1 → Write a pattern on the left side of `=` that looks like an object literal.
Step 2 → Each name in the pattern is looked up as a property key on the right-hand object.
Step 3 → The found value is stored in a new variable. Use `key: newName` to rename.
Step 4 → If the property is `undefined`, the default (`= value`) is used. `null` does NOT trigger the default.
Step 5 → `...rest` collects all remaining properties into a new object.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → `=` के बाएँ तरफ़ object जैसा pattern लिखो।
चरण 2 → Pattern का हर नाम right side वाले object में key की तरह ढूँढा जाता है।
चरण 3 → मिली value नए variable में जाती है। `key: naya_naam` से rename भी कर सकते हो।
चरण 4 → Property `undefined` हो तो default value लगती है। `null` पर default नहीं लगता।
चरण 5 → `...rest` बाकी सारी properties एक नए object में इकट्ठा कर देता है।

---

## 🟡 Real World Example
Zomato-style order webhook: the server receives a big payload, but the handler needs only a few fields.

```javascript
// Webhook payload from an order service (shape simplified)
const payload = { orderId: "ORD-88", customer: { name: "Riya", phone: "98xxxxxx01" }, total: 450 };
// Pull orderId, the nested customer name and phone, and status (with default) in ONE line
const { orderId, customer: { name, phone }, status = "PLACED" } = payload;
// status is missing in payload, so PLACED is used
```

Swiggy/Razorpay style code reads payloads like this all day. One line replaces five.

## 🟡 Real Example Hindi mein
Zomato के order webhook में पूरा payload आता है, लेकिन handler को सिर्फ़ कुछ fields चाहिए। `const { orderId, customer: { name, phone }, status = "PLACED" } = payload;` एक ही line में `orderId`, nested customer का `name` और `phone` निकाल लेता है। `status` payload में नहीं है, इसलिए default `PLACED` मिलता है।

---

## 💻 Code Example — Basic
```javascript
// Object Destructuring — basic examples
// Run: node 27-object-destructuring.js

// 1. Basic extraction: variable names must match property names
const user = { name: "Aditya", age: 25, city: "Mumbai" }; // a plain object
const { name, age } = user;      // create name and age from user.name and user.age
console.log(name, age);          // Aditya 25

// 2. Renaming: key: newVariableName
const { city: userCity } = user; // read property "city", store it in userCity
console.log(userCity);           // Mumbai
// console.log(city);            // ReferenceError — no variable "city" was created

// 3. Default values: used only when the property is undefined
const { role = "guest" } = user; // user has no "role", so the default is used
console.log(role);               // guest
const { age: years = 18 } = { age: undefined }; // undefined triggers the default
console.log(years);              // 18
const { age: y2 = 18 } = { age: null }; // null does NOT trigger the default
console.log(y2);                 // null

// 4. Nested destructuring: dig into an inner object
const order = { id: 101, restaurant: { name: "Biryani House", rating: 4.5 } };
const { restaurant: { name: shopName, rating } } = order; // go into restaurant
console.log(shopName, rating);   // Biryani House 4.5

// 5. Rest: collect everything else into a new object
const { id, ...others } = order; // id is taken out, others gets the rest
console.log(id, Object.keys(others)); // 101 [ 'restaurant' ]

// 6. Destructuring function parameters
function printUser({ name: n, city = "Unknown" }) { // destructure the argument
  console.log(`${n} lives in ${city}`);             // n is the renamed name
}
printUser(user);                 // Aditya lives in Mumbai
printUser({ name: "Riya" });     // Riya lives in Unknown

// 7. Assigning to EXISTING variables needs parentheses
let a = 1;
let b = 2;
({ a, b } = { a: 10, b: 20 });   // parentheses stop the { } from being a block
console.log(a, b);               // 10 20
```

## 💻 Code Example — Advanced
```javascript
// Advanced: destructuring real API payloads with defaults, validation and safe error handling

// Simulated payment gateway response (Razorpay-style shape, invented data)
const gatewayResponse = {
  status: "captured",                       // gateway status
  payment: {
    id: "pay_9A8B7C",                       // unique payment id
    amount: 49900,                          // amount in paise (integer)
    currency: "INR",                        // currency code
    notes: { orderId: "ord_1001" },         // merchant notes
  },
  meta: { region: "IN", attempt: 1 },       // fields we do not need here
};

// Destructure only what we need, with defaults for optional fields and nested defaults
function summarisePayment({
  status,                                   // required-ish, may be undefined
  payment: { id, amount, currency = "INR", notes: { orderId } = {} } = {},
} = {}) {                                   // whole argument defaults to {}
  // Validate the fields we depend on before using them
  if (!id || typeof amount !== "number") {
    // Throw a clear error so the caller can decide what to do
    throw new TypeError("Invalid payment payload: id and numeric amount are required");
  }
  const rupees = (amount / 100).toFixed(2); // convert paise to rupees as text
  // Return a clean summary; ?? gives "NA" when orderId is missing
  return { status, id, orderId: orderId ?? "NA", label: `${currency} ${rupees}` };
}

// Wrapper that never lets a bad payload crash the process
function safeSummarise(payload) {
  try {
    return { ok: true, data: summarisePayment(payload) }; // success shape
  } catch (err) {
    return { ok: false, error: err.message };             // failure shape
  }
}

console.log(safeSummarise(gatewayResponse));
// { ok: true, data: { status: 'captured', id: 'pay_9A8B7C', orderId: 'ord_1001', label: 'INR 499.00' } }
console.log(safeSummarise({ status: "failed" }));
// { ok: false, error: 'Invalid payment payload: ...' } — payment defaulted to {}
console.log(safeSummarise(null));
// { ok: false, error: ... } — null is not undefined, so the default {} is NOT used

// Destructuring inside a for...of loop over a list of orders
const orders = [
  { id: "ord_1", items: 2, total: 540 },   // first order
  { id: "ord_2", items: 1, total: 199 },   // second order
];
for (const { id: orderId, total } of orders) { // rename id to orderId while looping
  console.log(`${orderId} => ₹${total}`);    // print each order
}

// Computed key destructuring: the key name is decided at runtime
const field = "total";                       // key we want to read
const { [field]: dynamicValue } = orders[0]; // reads orders[0].total
console.log(dynamicValue);                   // 540
```

---

## 🟠 Express.js Integration
Express passes `req` and `res` to your handler. Destructuring is used in your handler code, not inside Express itself. The closest real usage is pulling fields from `req.params` and `req.body`.

```javascript
const express = require("express");        // import Express
const app = express();                     // create the app
app.use(express.json());                   // parse JSON bodies into req.body

// Route: cancel an order by id, with optional fields and defaults
app.post("/api/orders/:orderId/cancel", (req, res) => {
  // Pull the id from the URL and the options from the body in one go
  const { orderId } = req.params;          // route parameter
  const { reason = "not specified", notifyRider = true } = req.body ?? {}; // defaults
  // ?? {} protects against a missing body (req.body can be undefined)
  res.json({ orderId, reason, notifyRider, status: "CANCELLED" }); // send response
});

app.listen(3000);                          // start server on port 3000
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Destructuring `null` or `undefined` directly
✅ Correct: Give a fallback object before destructuring.

```javascript
// Wrong
const { data } = null;          // TypeError: Cannot destructure property 'data' of 'null'

// Right
const { data: safeData = {} } = null ?? {}; // fallback {} first, then default safeData = {}
```

❌ Mistake 2: Using the key name after renaming
✅ Correct: After `key: newName`, only `newName` exists as a variable.

```javascript
// Wrong
const user = { name: "Aditya" };
const { name: userName } = user;
console.log(name);              // ReferenceError: name is not defined

// Right
console.log(userName);          // Aditya
```

❌ Mistake 3: Expecting `null` to trigger a default
✅ Correct: Defaults only fire for `undefined`. Use `??` for `null` too.

```javascript
// Wrong
const { limit = 10 } = { limit: null };
console.log(limit);             // null — the default was skipped

// Right
const input = { limit: null };
const limitValue = input.limit ?? 10; // null or undefined both become 10
console.log(limitValue);        // 10
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print? (non-strict script)
const user = { name: "Aditya", address: { city: "Pune" } };
const { name, address: { city, zip = "411001" }, email = "none" } = user;
console.log(name, city, zip, email);      // (1)

const { a = 1, b = 2 } = { a: undefined, b: null };
console.log(a, b);                        // (2)

const { x: { y } = {} } = {};             // x is missing, so default {} is used
console.log(y);                           // (3)

const { address, ...rest } = user;        // take address out, rest gets the others
console.log(Object.keys(rest), address === user.address); // (4)
```
Answer:
```
Aditya Pune 411001 none      ← (1) zip and email fall back to their defaults
1 null                       ← (2) undefined -> default 1, but null stays null
undefined                    ← (3) y is read from {} which has no y
[ 'name' ] true              ← (4) rest has only name; address is the same reference
```
Explanation: defaults apply only when the value is `undefined`, so `b` keeps `null`. A nested pattern with a default (`x: { y } = {}`) lets you destructure a missing object safely. Rest copies the remaining own properties, but the values are the same references, so `address === user.address` is `true`.

---

## ⚫ Interview Questions + Answers

Q1: What is object destructuring?
A1: It is a syntax to extract property values from an object into variables, like `const { name } = user;`. The variable name must match the key unless you rename it with `key: newName`.

Q2: How do you rename while destructuring?
A2: Use `const { city: userCity } = user;`. The key `city` is read, but the variable is `userCity`. The name `city` is not created.

Q3: What is the difference between a default value and `??`?
A3: A default in destructuring applies only when the value is `undefined`. `??` applies for both `null` and `undefined`. Use `??` when `null` should also fall back.

Q4: How does rest work in object destructuring?
A4: `const { id, ...others } = obj;` removes `id` and copies every other own enumerable property into `others`. It creates a new object, but nested values are the same references.

Q5: What happens if you destructure `null` or `undefined`?
A5: It throws a TypeError because there are no properties to read. Protect it with a fallback object (`?? {}`) or a default in the parameter.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Pulling a few fields out of API responses, webhook payloads, or `req.body`
- Reading options objects in function parameters
- Looping over arrays of objects and needing 2-3 fields per item

❌ Avoid when:
- The data may be `null` and you have not added a fallback
- The path is very deep; `payment?.notes?.orderId` may be clearer for one value
- You destructure so many names that the reader cannot see where values come from

---

## 📊 Visual Diagram
```
const { name, city: c } = user;

   user = { name: "Aditya", city: "Pune", age: 25 }
             │                 │
             │                 └── key "city" ──► variable c   (renamed)
             └──────────────────── key "name" ──► variable name

   const { role = "guest" } = user;
   user has no "role"  ──► undefined  ──► default "guest" used
   user.role = null    ──► null       ──► default NOT used
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Destructuring | Extract values into variables using a pattern | Pattern से values निकालना |
| Rename | `key: newName` syntax | नाम बदलना |
| Default value | Fallback used when value is `undefined` | Default मान |
| Nested destructuring | Pattern inside a pattern | अंदर वाले object से निकालना |
| Rest (object) | `...others` collects remaining properties | बाकी properties इकट्ठा करना |
| Parameter destructuring | Destructuring in function arguments | Function argument से निकालना |
| Optional chaining | `obj?.prop` safe property access | सुरक्षित property access |

---

## ⚡ 3-Line Summary
**English:**
1. `const { a, b: renamed = 0 } = obj;` pulls values out in one line.
2. Defaults apply only for `undefined`; `null` needs `??`.
3. Always protect against `null` and `undefined` objects before destructuring.

**Hindi:**
1. `const { a, b: renamed = 0 } = obj;` एक line में values निकालता है।
2. Default सिर्फ़ `undefined` पर लगता है; `null` के लिए `??` चाहिए।
3. Destructuring से पहले `null` और `undefined` object से बचाव करो।

---

## ➡️ Next Topic
**28. Shorthand Properties + Computed Properties** — Object literal को छोटा और dynamic बनाना। Destructuring के बाद object बनाने का यह सबसे natural अगला कदम है।
