# 34. typeof + instanceof
# हिंदी में: typeof और instanceof — Value का Type और Object का Class पहचानना

---

## 🔵 Simple Definition (English)
`typeof` is an operator that returns a string naming the type of a value (`"number"`, `"string"`, `"object"`, and so on). `instanceof` checks whether an object was built from a given constructor or class by looking through its prototype chain.

## 🔵 सरल परिभाषा (Hindi)
`typeof` एक operator है जो value के type का नाम string में लौटाता है (`"number"`, `"string"`, `"object"` आदि)। `instanceof` यह जाँचता है कि कोई object किसी constructor या class से बना है या नहीं, और इसके लिए वह prototype chain देखता है।

---

## 🔴 Problem it Solves
JavaScript is dynamically typed: a variable can hold anything at any time. A function that expects a number may get a string from a form, or `null` from a database. Without checks, code crashes deep inside with messages like "cannot read property of null". `typeof` and `instanceof` let you check input and choose the right branch before using it.

## 🔴 यह क्यों बना? (Hindi)
JavaScript dynamically typed है: कोई variable कभी भी कोई भी value रख सकता है। जो function number की उम्मीद करता है, उसे form से string या database से `null` आ सकता है। Check न हो तो code अंदर कहीं crash होता है, जैसे "cannot read property of null"। `typeof` और `instanceof` से इस्तेमाल से पहले input जाँचा जा सकता है।

---

## 🟢 How it Works — Step by Step

Step 1 → `typeof value` returns one of 8 strings: number, string, boolean, undefined, bigint, symbol, object, function.
Step 2 → `typeof null` is `"object"` — a bug from the first version of JavaScript, kept for compatibility.
Step 3 → `obj instanceof C` walks up `obj`'s prototype chain and checks whether `C.prototype` is on it.
Step 4 → Primitives like `"abc"` are not objects, so `"abc" instanceof String` is `false`.
Step 5 → Arrays need `Array.isArray`, because `typeof []` is `"object"`.

## 🟢 कैसे काम करता है? (Hindi)
चरण 1 → `typeof value` 8 strings में से एक लौटाता है: number, string, boolean, undefined, bigint, symbol, object, function।
चरण 2 → `typeof null` `"object"` है — JavaScript के पहले version की गलती, जो compatibility के लिए रखी गई।
चरण 3 → `obj instanceof C` `obj` की prototype chain ऊपर तक देखता है और जाँचता है कि `C.prototype` उसमें है या नहीं।
चरण 4 → `"abc"` जैसे primitives object नहीं हैं, इसलिए `"abc" instanceof String` `false` है।
चरण 5 → Arrays के लिए `Array.isArray` चाहिए, क्योंकि `typeof []` `"object"` है।

---

## 🟡 Real World Example
A payment API receives an amount from a mobile app. A string like `"499"` must be rejected, and `null` must not crash the handler. Error handling checks `instanceof` to decide the HTTP status.

```javascript
function chargeAmount(amount) {
  if (typeof amount !== "number") {          // reject "499" (string) and null early
    throw new TypeError("amount must be a number");
  }
  return amount * 100;                       // convert rupees to paise
}
```

Paytm, Razorpay and Swiggy backends validate inputs this way before touching money or orders.

## 🟡 Real Example Hindi mein
Payment API mobile app से amount लेता है। `"499"` (string) को reject करना है, और `null` से handler crash नहीं होना चाहिए। Error handling `instanceof` से तय करता है कि HTTP status क्या भेजना है। Paytm, Razorpay और Swiggy के backends पैसे या order को छूने से पहले ऐसे ही validate करते हैं।

---

## 💻 Code Example — Basic
```javascript
// typeof + instanceof — basic examples
// Run: node 34b-typeof-and-instanceof.js

// 1. typeof on primitives
console.log(typeof 42);            // "number"
console.log(typeof "hello");       // "string"
console.log(typeof true);          // "boolean"
console.log(typeof undefined);     // "undefined"
console.log(typeof 10n);           // "bigint" — BigInt literal
console.log(typeof Symbol("x"));   // "symbol"

// 2. The famous bug: typeof null is "object"
console.log(typeof null);          // "object" — historical bug, kept for compatibility
console.log(null === null);        // true — check null with === instead of typeof

// 3. typeof on functions, classes, arrays and objects
console.log(typeof function () {}); // "function"
console.log(typeof class {});       // "function" — classes are functions
console.log(typeof []);             // "object" — arrays are objects
console.log(typeof {});             // "object"

// 4. Arrays: use Array.isArray for a reliable check
console.log(Array.isArray([1, 2]));   // true
console.log(Array.isArray({ 0: 1 })); // false — looks like an array, but is not

// 5. typeof does not throw for undeclared variables
console.log(typeof notDeclaredAnywhere); // "undefined" — no ReferenceError

// 6. instanceof checks the prototype chain
class Order {}                       // a simple class
const o = new Order();               // create an instance
console.log(o instanceof Order);     // true — built from Order
console.log(o instanceof Object);    // true — Order.prototype inherits from Object.prototype
console.log([] instanceof Array);    // true
console.log([] instanceof Object);   // true — arrays inherit from Object too

// 7. Primitives are not instances
console.log("abc" instanceof String);             // false — a primitive
console.log(new String("abc") instanceof String); // true — a wrapper object

// 8. Object.prototype.toString gives a more detailed tag
console.log(Object.prototype.toString.call(new Date())); // [object Date]
console.log(Object.prototype.toString.call(null));       // [object Null]
```

## 💻 Code Example — Advanced
```javascript
// Advanced: universal type checker, custom errors with instanceof, Symbol.hasInstance

// 1. Universal type checker: combines typeof, null, arrays and the toString tag
function typeOf(value) {
  if (value === null) return "null";        // typeof null is "object", so handle it first
  if (Array.isArray(value)) return "array"; // typeof [] is "object", so check arrays next
  // Object.prototype.toString gives tags like [object Date], [object Map]
  const tag = Object.prototype.toString.call(value).slice(8, -1); // e.g. "Date"
  if (tag !== "Object") return tag.toLowerCase(); // date, map, regexp, number, string...
  return typeof value;                      // plain object, or primitive fallback
}
console.log(typeOf(null));          // null
console.log(typeOf([1]));           // array
console.log(typeOf(new Date()));    // date
console.log(typeOf(new Map()));     // map
console.log(typeOf(12));            // number
console.log(typeOf({}));            // object

// 2. Custom error classes + instanceof to pick the right response
class AppError extends Error {
  constructor(message, status) {
    super(message);                 // set the Error message
    this.name = "AppError";         // name shown in logs
    this.status = status;           // HTTP status to send back
  }
}
class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);            // validation problems are 400 Bad Request
    this.name = "ValidationError";  // more specific name
  }
}
function toResponse(err) {
  // instanceof walks the chain: ValidationError -> AppError -> Error
  if (err instanceof ValidationError) return { status: 400, msg: err.message };
  if (err instanceof AppError) return { status: err.status, msg: err.message };
  return { status: 500, msg: "Internal error" }; // unknown errors are hidden from users
}
console.log(toResponse(new ValidationError("Phone missing")));  // { status: 400, msg: 'Phone missing' }
console.log(toResponse(new AppError("Coupon expired", 410)));   // { status: 410, msg: 'Coupon expired' }
console.log(toResponse(new TypeError("boom")));                 // { status: 500, msg: 'Internal error' }

// 3. Symbol.hasInstance lets a class customise what instanceof means
class Serializable {
  // called by "x instanceof Serializable"; returns true for duck-typed objects
  static [Symbol.hasInstance](obj) {
    return obj !== null && typeof obj.toJSON === "function"; // has a toJSON method
  }
}
console.log({ toJSON() { return {}; } } instanceof Serializable); // true
console.log({} instanceof Serializable);                           // false

// 4. instanceof can fail across realms (iframes, vm contexts): use Array.isArray
const vm = require("vm");                  // built-in module to run code in a new context
const foreignArray = vm.runInNewContext("[1, 2, 3]"); // array from another realm
console.log(foreignArray instanceof Array); // false — it has a different Array constructor
console.log(Array.isArray(foreignArray));   // true — works across realms

// 5. Input guard for a payment amount
function assertAmount(amount) {
  // typeof first: reject strings like "499" that come from HTML forms
  if (typeof amount !== "number") {
    throw new TypeError(`amount must be number, got ${typeof amount}`);
  }
  if (!Number.isFinite(amount) || amount <= 0) { // reject NaN, Infinity and zero or less
    throw new RangeError("amount must be positive");
  }
  return amount;                           // safe to use
}
try {
  assertAmount("499");                     // wrong type
} catch (e) {
  console.log(e.message);                  // amount must be number, got string
}
```

---

## 🟠 Express.js Integration
Express error middleware receives the error object. Use `instanceof` to pick the status code, and `typeof` to check untrusted request fields before using them.

```javascript
const express = require("express");           // import Express
const app = express();                        // create the app
app.use(express.json());                      // parse JSON bodies

class PaymentError extends Error {}           // custom error for failed payments

app.post("/api/pay", (req, res, next) => {
  try {
    const { amount, currency = "INR" } = req.body ?? {}; // untrusted input
    if (typeof amount !== "number") {         // typeof check on client data
      return res.status(400).json({ error: "amount must be a number" });
    }
    if (amount > 100000) {                    // business rule
      throw new PaymentError("amount exceeds limit");
    }
    res.json({ ok: true, amount, currency }); // success response
  } catch (err) {
    next(err);                                // pass the error to error middleware
  }
});

// Error middleware: has four parameters, so Express treats it as an error handler
app.use((err, req, res, next) => {
  if (err instanceof PaymentError) {          // instanceof picks the right branch
    return res.status(402).json({ error: err.message });
  }
  res.status(500).json({ error: "Something went wrong" }); // hide unknown details
});

app.listen(3000);                             // start the server
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Checking an object with `typeof` only, so `null` passes
✅ Correct: `typeof null` is `"object"`, so add a `!== null` check.

```javascript
// Wrong
function getCity(user) {
  if (typeof user === "object") {     // true for null too
    return user.address.city;         // TypeError when user is null
  }
}

// Right
function getCityRight(user) {
  if (typeof user === "object" && user !== null) return user.address?.city;
  return undefined;                   // null or non-object input
}
```

❌ Mistake 2: Using `typeof` to detect arrays
✅ Correct: `typeof` returns `"object"` for arrays and objects. Use `Array.isArray`.

```javascript
// Wrong
const items = [1, 2, 3];
console.log(typeof items === "object");   // true — but this does not tell you it is an array

// Right
console.log(Array.isArray(items));        // true
```

❌ Mistake 3: Using `instanceof` on primitive values
✅ Correct: Primitives are not instances of their wrapper classes. Use `typeof` for primitives.

```javascript
// Wrong
const name = "Riya";
console.log(name instanceof String);      // false — primitive, not an object

// Right
console.log(typeof name === "string");    // true
```

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: what will each console.log print? (non-strict script)
console.log(typeof null, typeof NaN, typeof []);     // (1)
console.log(typeof typeof 1);                        // (2)
console.log(null instanceof Object);                 // (3)
console.log([] instanceof Object, Object.create(null) instanceof Object); // (4)
console.log(typeof undeclaredVar === "undefined");   // (5)
```
Answer:
```
object number object      ← (1) null is the famous bug; NaN is a number; arrays are objects
string                    ← (2) typeof always returns a string, and typeof "x" is "string"
false                     ← (3) null is not an object, so it has no prototype chain
true false                ← (4) arrays inherit from Object; an object with no prototype does not
true                      ← (5) typeof does not throw for undeclared names
```
Explanation: `typeof NaN` is `"number"` because `NaN` is a special numeric value. `typeof typeof 1` evaluates `typeof 1` first, which gives `"number"`, and then `typeof "number"` gives `"string"`. `instanceof` needs an object on the left; `null` is not one, so the answer is `false`. `Object.create(null)` creates an object without `Object.prototype` in its chain, so `instanceof Object` is `false`, even though `typeof` says `"object"`.

---

## ⚫ Interview Questions + Answers

Q1: Why does `typeof null` return "object"?
A1: It is a bug from the first JavaScript implementation, where values were tagged with a type code and the code for objects was 0, which null matched. The bug was never fixed because it would break existing code. Check `null` with `=== null`.

Q2: What does `typeof` return for a class and for a function?
A2: Both return `"function"`. Classes are special functions in JavaScript, so `typeof SomeClass` is `"function"`.

Q3: How does `instanceof` work internally?
A3: It checks `Symbol.hasInstance` first. If it is not overridden, it walks the prototype chain of the left operand and looks for `Constructor.prototype`. If found, it returns `true`.

Q4: When is `instanceof` unreliable?
A4: It fails across realms (iframes, `vm` contexts), because each realm has its own `Array` or `Error` constructor. It also fails when the prototype chain was changed with `Object.setPrototypeOf`. Use `Array.isArray` or a tag check from `Object.prototype.toString` in those cases.

Q5: What is the difference between `typeof` and `instanceof`?
A5: `typeof` gives the primitive type name and cannot tell apart arrays, dates or custom classes, since they are all `"object"`. `instanceof` tells you which constructor built an object, but it does not work for primitives.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Validating input from users, forms and APIs before doing math or string work
- Choosing an error response by custom error class (`err instanceof ValidationError`)
- Checking for a function before calling it (`typeof callback === "function"`)

❌ Avoid when:
- You need to detect arrays with `typeof`; use `Array.isArray`
- You need to check values across iframes or `vm` contexts with `instanceof`
- You rely on `instanceof` for primitives; use `typeof`

---

## 📊 Visual Diagram
```
  typeof value → string
  ─────────────────────────────────────────────────────
  42          → "number"      "hi"       → "string"
  true        → "boolean"     undefined  → "undefined"
  Symbol()    → "symbol"      10n        → "bigint"
  function{}  → "function"    null       → "object"  ← bug
  []          → "object"      {}         → "object"

  obj instanceof C  (prototype chain walk)
  ─────────────────────────────────────────────────────
  o ──► Order.prototype ──► Object.prototype ──► null
        ▲
        └── C.prototype = Order.prototype  →  true
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `typeof` | Operator that returns a type name string | Type का नाम लौटाने वाला operator |
| `instanceof` | Checks prototype chain for a constructor | Constructor की prototype chain जाँचना |
| Primitive | Simple value: number, string, boolean and others | सरल value |
| Prototype chain | Links from an object to its parent prototypes | Object से parent prototypes की कड़ी |
| `Array.isArray` | Reliable check for arrays | Array जाँचने का भरोसेमंद तरीका |
| `Symbol.hasInstance` | Hook that customises `instanceof` | `instanceof` बदलने वाला hook |
| Realm | Separate global environment (iframe, vm) | अलग global environment |

---

## ⚡ 3-Line Summary
**English:**
1. `typeof` returns the primitive type name, but `typeof null` and `typeof []` are both `"object"`.
2. `instanceof` walks the prototype chain to check a constructor, and it is `false` for primitives.
3. Use `=== null`, `Array.isArray` and `typeof` for primitives, and `instanceof` for custom classes and errors.

**Hindi:**
1. `typeof` primitive type का नाम लौटाता है, लेकिन `typeof null` और `typeof []` दोनों `"object"` हैं।
2. `instanceof` constructor जाँचने के लिए prototype chain देखता है, और primitives के लिए `false` है।
3. `null` के लिए `=== null`, arrays के लिए `Array.isArray`, primitives के लिए `typeof` और custom classes व errors के लिए `instanceof` इस्तेमाल करो।

---

## ➡️ Next Topic
**35. Prototypes and Prototype Chain** — `instanceof` prototype chain पर निर्भर करता है। अगला topic बताता है कि यह chain कैसे बनती है और objects एक-दूसरे से properties कैसे लेते हैं।
