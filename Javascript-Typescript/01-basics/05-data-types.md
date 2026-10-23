# 05. Data Types
# हिंदी में: JavaScript के Data Types — Primitive और Non-Primitive

---

## 🔵 Simple Definition (English)
JavaScript has **8 data types**: 7 primitives (stored by value) and 1 non-primitive (Object, stored by reference). Primitives: `string`, `number`, `boolean`, `null`, `undefined`, `symbol`, `bigint`. Non-primitive: `object` (includes arrays, functions, dates).

## 🔵 सरल परिभाषा (Hindi)
JavaScript में 8 data types हैं: 7 primitives (value से store होते हैं) और 1 non-primitive (Object, reference से)। Primitives: string, number, boolean, null, undefined, symbol, bigint। Non-primitive: object (arrays, functions, dates सब इसी में)।

---

## 🔴 Problem it Solves
Understanding types prevents:
- `0 == false` → true (type coercion surprises)
- `typeof null === "object"` (historic bug — know it!)
- Adding numbers getting concatenated strings: `"5" + 3 = "53"`
- Comparing objects: `{} === {}` is `false`

## 🔴 यह क्यों बना? (Hindi)
Types समझना इन bugs से बचाता है: `"5" + 3 = "53"` (string + number), `{} === {}` false क्यों, null का typeof "object" क्यों आता है।

---

## 🟢 How it Works — Step by Step

```
┌─────────────────────────────────────────────────────┐
│                  JavaScript Types                    │
├─────────────────────────────────────────────────────┤
│  PRIMITIVES (stored by VALUE in Stack)              │
│  ┌──────────┬─────────────────────────────────┐    │
│  │ string   │ "hello", 'world', `template`    │    │
│  │ number   │ 42, 3.14, NaN, Infinity, -0     │    │
│  │ boolean  │ true, false                     │    │
│  │ null     │ null (intentional empty)        │    │
│  │ undefined│ undefined (not yet assigned)    │    │
│  │ symbol   │ Symbol("id") — unique value     │    │
│  │ bigint   │ 9007199254740991n — huge numbers│    │
│  └──────────┴─────────────────────────────────┘    │
│                                                     │
│  NON-PRIMITIVE (stored by REFERENCE in Heap)        │
│  ┌──────────┬─────────────────────────────────┐    │
│  │ object   │ {}, [], function(){}, new Date()│    │
│  └──────────┴─────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### Memory: Stack vs Heap
```
Primitives (Stack — fast, fixed size):
  let a = 5;  → Stack: [a → 5]
  let b = a;  → Stack: [a → 5, b → 5]  (copy)
  b = 10;     → Stack: [a → 5, b → 10] (independent)

Objects (Heap — flexible size):
  let obj1 = {x: 1}; → Heap: {x:1} ← Stack: [obj1 → ref123]
  let obj2 = obj1;   → Heap: {x:1} ← Stack: [obj1 → ref123, obj2 → ref123]
  obj2.x = 99;       → Heap: {x:99}  Both obj1 and obj2 see x=99!
```

## 🟢 कैसे काम करता है? (Hindi)
- Primitives Stack में directly value store होती है — copy करने पर independent copy बनती है
- Objects Heap में store होते हैं, variable में सिर्फ address (reference) होता है — copy करने पर same object point होता है, original change हो जाता है

---

## 🟡 Real World Example
**User Form Validation:**
```javascript
const userData = {
  name: "Aditya",        // string
  age: 25,               // number
  isVerified: true,      // boolean
  phone: null,           // null: जान-बूझकर empty
  address: undefined,    // undefined: अभी भरा नहीं
  userId: Symbol("u1"),  // symbol: unique ID
};

// Type check before processing
if (typeof userData.name === "string" && userData.name.length > 0) {
  console.log("Valid name");
}
```

## 🟡 Real Example Hindi mein
Zomato profile: name = string, age = number, isDeliveryPartner = boolean, address = null (जानबूझकर empty), phone = undefined (user ने भरा नहीं)। हर type का अलग purpose है।

---

## 💻 Code Example — Basic
```javascript
// ── String ───────────────────────────
let firstName = "Aditya";            // double quotes
let lastName = 'Rajan';              // single quotes
let greeting = `Hello, ${firstName}`; // template literal
console.log(typeof firstName);       // "string"
console.log(firstName.length);       // 6

// ── Number ───────────────────────────
let price = 299.99;
let count = 42;
let notANumber = NaN;                // Not a Number (invalid math result)
let infinite = Infinity;             // 1/0 = Infinity
let negZero = -0;                    // exists! -0 === 0 is true
console.log(typeof price);           // "number"
console.log(isNaN(notANumber));      // true
console.log(isFinite(infinite));     // false

// ── Boolean ──────────────────────────
let isLoggedIn = true;
let hasDiscount = false;
console.log(typeof isLoggedIn);      // "boolean"

// ── null ─────────────────────────────
let selectedItem = null;             // intentionally no value
console.log(typeof null);            // "object" ← famous JS bug!
console.log(selectedItem === null);  // true (correct way to check null)

// ── undefined ────────────────────────
let userProfile;                     // declared but not assigned
console.log(userProfile);            // undefined
console.log(typeof userProfile);     // "undefined"

function greet(name) {
  console.log(name);                 // undefined if not passed
}
greet(); // undefined

// ── Symbol ───────────────────────────
const id1 = Symbol("userId");
const id2 = Symbol("userId");
console.log(id1 === id2);            // false — every Symbol is unique!
console.log(typeof id1);             // "symbol"

// ── BigInt ───────────────────────────
const hugeNumber = 9007199254740991n; // n suffix = BigInt
const bigCalc = BigInt(9007199254740991) + 1n;
console.log(typeof hugeNumber);       // "bigint"
// console.log(hugeNumber + 1);       // ❌ TypeError: mix BigInt + Number

// ── Object (non-primitive) ───────────
let user = { name: "Aditya", age: 25 }; // object
let colors = ["red", "green", "blue"];   // array (also object)
let today = new Date();                  // Date (also object)
let fn = function() {};                  // function (typeof = "function")

console.log(typeof user);    // "object"
console.log(typeof colors);  // "object" (not "array"!)
console.log(typeof today);   // "object"
console.log(typeof fn);      // "function" (special case)
```

## 💻 Code Example — Advanced
```javascript
// ── TYPE CHECKING properly ──────────────

function getType(value) {
  if (value === null) return "null";          // null special case
  if (Array.isArray(value)) return "array";   // array before object
  if (value instanceof Date) return "date";   // Date check
  return typeof value;                        // rest: string/number/boolean/undefined/symbol/bigint/object/function
}

console.log(getType(null));       // "null"
console.log(getType([]));         // "array"
console.log(getType(new Date())); // "date"
console.log(getType(42));         // "number"
console.log(getType("hello"));    // "string"
console.log(getType({}));         // "object"

// ── PRIMITIVE vs REFERENCE behavior ──────

// Primitives — copied by VALUE
let a = 10;
let b = a;    // b gets a COPY of 10
b = 99;
console.log(a); // 10 — unchanged! b is independent

// Objects — copied by REFERENCE
let obj1 = { score: 10 };
let obj2 = obj1;    // obj2 points to SAME object
obj2.score = 99;
console.log(obj1.score); // 99 — obj1 changed too!

// How to copy an object correctly:
// Shallow copy:
let obj3 = { ...obj1 };         // spread operator
let obj4 = Object.assign({}, obj1);

// Deep copy:
let obj5 = JSON.parse(JSON.stringify(obj1)); // simple but loses functions/dates
let obj6 = structuredClone(obj1);            // modern, handles more types

// ── NaN quirks ──────────────────────────
console.log(NaN === NaN);     // false! NaN is not equal to itself
console.log(isNaN("hello"));  // true — converts to number first
console.log(Number.isNaN("hello")); // false — strict, no conversion

// Safe NaN check:
function isSafeNumber(val) {
  return typeof val === "number" && !Number.isNaN(val);
}

// ── Number precision issues ──────────────
console.log(0.1 + 0.2);           // 0.30000000000000004 — floating point!
console.log(0.1 + 0.2 === 0.3);   // false!

// Solution: use epsilon or round
const isEqual = Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON;
console.log(isEqual); // true

// Or for currency: use integers (paise, cents)
const price1 = 10; // ₹0.10 stored as 10 paise
const price2 = 20; // ₹0.20 stored as 20 paise
const total = (price1 + price2) / 100; // ₹0.30 — accurate!

// ── Type Coercion surprises ──────────────
console.log(1 + "2");    // "12" — number coerced to string
console.log("5" - 2);   // 3   — string coerced to number (- forces number)
console.log(true + 1);  // 2   — true = 1
console.log(false + 1); // 1   — false = 0
console.log(null + 1);  // 1   — null = 0
console.log(undefined + 1); // NaN — undefined + number = NaN
```

---

## 🟠 React/Next.js Connection
```jsx
import PropTypes from "prop-types"; // old way — runtime type checking

// TypeScript (modern way) — compile-time type safety
interface User {
  id: number;
  name: string;
  email: string;
  isVerified: boolean;
  avatar: string | null; // can be string or null
  age?: number;           // optional — can be undefined
}

// React component with TypeScript
const UserCard = ({ user }: { user: User }) => {
  // TypeScript knows exact types
  const displayName = user.name.toUpperCase(); // safe: name is always string
  
  return (
    <div>
      <h2>{displayName}</h2>
      {/* user.avatar could be null — handle it */}
      {user.avatar !== null && <img src={user.avatar} alt={user.name} />}
      {/* user.age could be undefined — handle it */}
      {user.age !== undefined && <span>Age: {user.age}</span>}
    </div>
  );
};

// API response type checking (Node.js)
app.post("/api/order", (req, res) => {
  const { amount, items } = req.body;

  // Runtime type validation at API boundary
  if (typeof amount !== "number" || !Array.isArray(items)) {
    return res.status(400).json({ error: "Invalid input types" });
  }

  // Now safe to use
  const total = amount * 1.18; // GST
  res.json({ total });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `typeof` to check for null or array
```javascript
// WRONG:
if (typeof value === "object") { /* also true for null and arrays! */ }

// CORRECT:
if (value !== null && typeof value === "object" && !Array.isArray(value)) {
  // this is a plain object
}
```

❌ **Mistake 2:** Comparing NaN with ===
```javascript
// WRONG:
if (result === NaN) { /* NEVER true! NaN !== NaN */ }

// CORRECT:
if (Number.isNaN(result)) { /* use Number.isNaN */ }
```

❌ **Mistake 3:** Floating point arithmetic for money
```javascript
// WRONG:
const total = 0.1 + 0.2; // 0.30000000000000004
if (total === 0.3) { /* false! */ }

// CORRECT: store in smallest unit (paise/cents)
const total = 10 + 20; // 30 paise
const display = (total / 100).toFixed(2); // "0.30"
```

---

## 🧠 Tricky Interview Output Question
```javascript
console.log(typeof null);
console.log(typeof undefined);
console.log(typeof NaN);
console.log(typeof []);
console.log(typeof function(){});
console.log(null == undefined);
console.log(null === undefined);
```
**Answer:**
```
"object"     ← null's typeof is a bug (historical, can't fix)
"undefined"
"number"     ← NaN is type number!
"object"     ← arrays are objects
"function"   ← functions get special typeof treatment
true         ← == loose equality: null and undefined are "equal"
false        ← === strict: different types
```

---

## ⚫ Interview Questions + Answers

**Q1: What are all the data types in JavaScript?**
A1: 8 types total. 7 primitives: string, number, boolean, null, undefined, symbol, bigint. 1 non-primitive: object (which includes arrays, functions, dates, regex, and plain objects). Primitives are stored by value (stack), objects by reference (heap).

**Q2: What is the difference between null and undefined?**
A2: `undefined` means a variable has been declared but not yet assigned a value — it's JavaScript's default. `null` is an explicit assignment meaning "intentionally empty" — a developer sets it. `typeof undefined` is `"undefined"`, `typeof null` is `"object"` (a bug). Both are falsy, and `null == undefined` is true but `null === undefined` is false.

**Q3: Why is typeof null === "object"?**
A3: It's a JavaScript bug from 1995 that was never fixed for backward compatibility. In the original JS engine, all values had a type tag — null's tag was 0 (the same as objects). Despite proposals to fix it, changing it would break too much existing code, so it remains.

**Q4: What is NaN and how do you check for it?**
A4: NaN (Not a Number) is the result of invalid numeric operations like `"hello" * 2` or `0/0`. Its type is `"number"`. The weird part: `NaN !== NaN` — it's the only value not equal to itself. To check: use `Number.isNaN(val)` (strict, no type coercion) rather than `isNaN(val)` (converts to number first, giving false positives for strings).

**Q5: What is the difference between primitive and reference types?**
A5: Primitives (string, number, boolean, null, undefined, symbol, bigint) are stored directly in the stack by value. Copying them creates an independent copy. Reference types (objects, arrays, functions) are stored in the heap; variables hold a reference (pointer) to the heap address. Copying an object copies the reference — both variables point to the same data, so mutations affect both.

---

## 🔷 Trade-offs / When to Use
✅ Use primitives when:
- Simple values that don't need methods
- Values that should be compared by value

✅ Use objects when:
- Grouping related data
- Need methods and behavior
- Large, complex data structures

❌ Watch out for:
- Floating point: never use for currency — store in integers
- null vs undefined: be deliberate about which you use
- NaN: always use Number.isNaN() not ===

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Primitive | Value type, stored in stack | Value type, stack में |
| Reference type | Stored in heap, variable holds pointer | Heap में, pointer hold करता है |
| NaN | Not a Number — invalid math result | Invalid math का result |
| null | Intentional absence of value | जान-बूझकर कोई value नहीं |
| undefined | Variable declared, not assigned | Declare हुआ, value नहीं दी |
| Symbol | Unique identifier | हमेशा unique value |
| BigInt | Integer larger than Number.MAX_SAFE_INTEGER | बड़े integers के लिए |
| Type coercion | Automatic type conversion | Automatic type बदलना |

---

## ⚡ 3-Line Summary
**English:**
1. JS has 7 primitives (stored by value) and objects (stored by reference) — this difference causes most type bugs.
2. `typeof null === "object"` is a historic bug; always use `=== null` to check for null.
3. Never use floating point for money calculations — store values as integers (paise/cents).

**Hindi:**
1. JS में 7 primitives (value से) और objects (reference से) — यही difference ज़्यादातर bugs की जड़ है।
2. `typeof null === "object"` एक bug है — null check के लिए `=== null` use करो।
3. Money calculations में floating point मत use करो — integers (paise/cents) में store करो।

---

## 📚 Go Deeper — External Resources

| Type | Link | What you'll learn |
|------|------|-------------------|
| 📺 YouTube | [Akshay Saini — Data Types in JS](https://www.youtube.com/results?search_query=javascript+data+types+akshay+saini+namaste) | Primitive vs reference, stack vs heap visuals |
| 📺 YouTube | [Fireship — JavaScript Types](https://www.youtube.com/results?search_query=javascript+data+types+explained+fireship) | Quick visual summary, type coercion |
| 📝 Article | [javascript.info — Data Types](https://javascript.info/types) | Complete reference with interactive examples |
| 📝 Article | [MDN — JavaScript data types](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures) | Authoritative reference for all types |
| 🐙 GitHub | [getify/You-Dont-Know-JS — Types & Grammar](https://github.com/getify/You-Dont-Know-JS/blob/1st-ed/types%20%26%20grammar/README.md) | The deepest free treatment of JS types |

---

## ➡️ Next Topic
**06. Primitive vs Reference Types** — Stack vs Heap memory, by-value vs by-reference का deep dive, copy करते समय क्या होता है।
