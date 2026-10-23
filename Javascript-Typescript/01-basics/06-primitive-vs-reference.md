# 06. Primitive vs Reference Types
# हिंदी में: Primitive vs Reference — Stack और Heap Memory

---

## 🔵 Simple Definition (English)
**Primitives** (string, number, boolean, null, undefined, symbol, bigint) are stored **by value** — copying creates a completely independent copy. **Reference types** (objects, arrays, functions) are stored **by reference** — copying gives you a pointer to the same data.

## 🔵 सरल परिभाषा (Hindi)
**Primitives** — value से store होते हैं। Copy करने पर independent copy। **Reference types** (objects, arrays) — reference (address) से। Copy करने पर दोनों same data point करते हैं — एक बदलो तो दोनों बदलते हैं।

---

## 🔴 Problem it Solves
Without knowing this:
```javascript
const a = { score: 10 };
const b = a;
b.score = 99;
console.log(a.score); // 99 — surprised?
```
This unexpected mutation is a source of many bugs in React state management, function parameters, and array operations.

## 🔴 यह क्यों बना? (Hindi)
यह समझे बिना React में state mutation bugs आते हैं, function में object pass करने पर original बदल जाता है, array copy करने पर दोनों एक ही array point करते हैं।

---

## 🟢 How it Works — Step by Step

```
PRIMITIVES — Stack Memory (fast, fixed size)
─────────────────────────────────────────────
let a = 5;
  Stack: | a | 5 |

let b = a;   // copy of VALUE
  Stack: | a | 5 |
         | b | 5 |  ← independent copy

b = 99;
  Stack: | a | 5 |  ← a unchanged
         | b | 99|

────────────────────────────────────────────
REFERENCE TYPES — Heap Memory (flexible size)
────────────────────────────────────────────
let obj1 = { x: 1 };
  Stack: | obj1 | ref#001 | ──→ Heap: { x: 1 }

let obj2 = obj1;  // copy of REFERENCE
  Stack: | obj1 | ref#001 | ──┐
         | obj2 | ref#001 | ──┴→ Heap: { x: 1 }  ← same location!

obj2.x = 99;
  Stack: | obj1 | ref#001 | ──┐
         | obj2 | ref#001 | ──┴→ Heap: { x: 99 } ← both see the change!
```

## 🟢 कैसे काम करता है? (Hindi)
- Primitives: Stack में directly value store होती है। `b = a` करने पर Stack में नई entry बनती है — independent।
- Objects: Heap में actual data, Stack में सिर्फ address (reference)। `obj2 = obj1` करने पर address copy होता है, data नहीं — दोनों same Heap location point करते हैं।

---

## 🟡 Real World Example
**React Shopping Cart Bug:**
```javascript
// Bug: direct mutation (reference type)
const cart = [{ id: 1, qty: 2 }];
const newCart = cart;    // same reference!
newCart[0].qty = 5;      // cart[0].qty भी 5 हो गया!
// React नहीं जानता state changed — re-render नहीं होगा

// Fix: new array बनाओ
const newCart = [...cart]; // spread = new array, new reference
newCart[0] = { ...cart[0], qty: 5 }; // new object for changed item
// अब React को पता चलेगा — different reference = state changed
```

## 🟡 Real Example Hindi mein
Zomato cart में item quantity बढ़ाना: अगर सीधे array mutate करो, React नहीं जानता state बदली — UI update नहीं। इसलिए नई array/object बनानी पड़ती है (spread operator से)।

---

## 💻 Code Example — Basic
```javascript
// ── PRIMITIVE: copy by VALUE ──────────

let price = 100;
let discountedPrice = price;  // VALUE copy
discountedPrice = discountedPrice * 0.9; // 10% discount

console.log(price);           // 100 — original unchanged
console.log(discountedPrice); // 90

// String (primitive)
let name1 = "Aditya";
let name2 = name1; // VALUE copy
name2 = "Rajan";
console.log(name1); // "Aditya" — unchanged
console.log(name2); // "Rajan"

// ── REFERENCE: copy by REFERENCE ──────

let user1 = { name: "Aditya", score: 100 };
let user2 = user1; // REFERENCE copy — same object!

user2.score = 999;
console.log(user1.score); // 999 — user1 also changed!
console.log(user2.score); // 999

// Checking same reference:
console.log(user1 === user2); // true — same object in memory

// ── Arrays (reference types) ──────────
let arr1 = [1, 2, 3];
let arr2 = arr1; // reference copy
arr2.push(4);
console.log(arr1); // [1, 2, 3, 4] — arr1 also changed!
```

## 💻 Code Example — Advanced
```javascript
// ── HOW TO COPY PROPERLY ──────────────

const original = {
  name: "Aditya",
  address: {
    city: "Mumbai",
    pin: "400001"
  },
  hobbies: ["coding", "reading"]
};

// ── 1. Shallow Copy (only top level) ──
const shallow1 = { ...original };               // spread
const shallow2 = Object.assign({}, original);    // Object.assign

shallow1.name = "Rajan";               // ✅ original.name unchanged
shallow1.address.city = "Delhi";        // ❌ original.address.city ALSO changed!
// Why? address is a nested object — still same reference

console.log(original.name);             // "Aditya" (safe)
console.log(original.address.city);     // "Delhi" (mutated! shallow copy)

// ── 2. Deep Copy options ──────────────

// Option A: JSON.parse + JSON.stringify (simple, limited)
const deep1 = JSON.parse(JSON.stringify(original));
deep1.address.city = "Pune";
console.log(original.address.city); // "Mumbai" ✅ unchanged
// Limitation: functions, undefined, Date, RegExp are lost!

// Option B: structuredClone (modern, handles more)
const deep2 = structuredClone(original);
deep2.address.city = "Goa";
console.log(original.address.city); // "Mumbai" ✅
// Handles: nested objects, arrays, Date, Map, Set
// Limitation: cannot clone functions

// Option C: lodash cloneDeep (most complete)
// const deep3 = _.cloneDeep(original); // handles everything

// ── FUNCTION PARAMETERS ───────────────

// Primitive: function gets a COPY — can't affect original
function addTen(num) {
  num += 10;         // modifies local copy
  return num;
}
let x = 5;
addTen(x);
console.log(x); // 5 — unchanged

// Object: function gets the REFERENCE — can affect original!
function giveBonus(user) {
  user.score += 100;  // modifies the ORIGINAL object
}
let player = { name: "Alice", score: 50 };
giveBonus(player);
console.log(player.score); // 150 — changed by function!

// Safe: don't mutate, return new object
function giveBonusSafe(user) {
  return { ...user, score: user.score + 100 }; // new object
}
let player2 = { name: "Bob", score: 50 };
let updatedPlayer = giveBonusSafe(player2);
console.log(player2.score);      // 50 — unchanged
console.log(updatedPlayer.score); // 150

// ── EQUALITY COMPARISON ────────────────

// Primitives: compared by VALUE
console.log(5 === 5);           // true
console.log("hi" === "hi");     // true

// Objects: compared by REFERENCE
console.log({} === {});         // false! (different objects in memory)
console.log([] === []);         // false!

const a = { x: 1 };
const b = a;
console.log(a === b);           // true (same reference)

// Deep equality needs a function:
function deepEqual(obj1, obj2) {
  return JSON.stringify(obj1) === JSON.stringify(obj2);
  // Simple but has edge cases (key order, functions, etc.)
}
console.log(deepEqual({ x: 1 }, { x: 1 })); // true
```

---

## 🟠 React/Next.js Connection
```jsx
import { useState } from "react";

function Cart() {
  const [items, setItems] = useState([
    { id: 1, name: "Pizza", qty: 1 },
    { id: 2, name: "Burger", qty: 2 },
  ]);

  // ❌ WRONG: direct mutation (React won't re-render)
  const wrongUpdateQty = (id) => {
    const item = items.find(i => i.id === id);
    item.qty += 1; // mutating reference — same reference!
    setItems(items); // React sees same array reference → no re-render!
  };

  // ✅ CORRECT: new array + new object
  const updateQty = (id) => {
    setItems(items.map(item =>
      item.id === id
        ? { ...item, qty: item.qty + 1 } // NEW object for changed item
        : item
    )); // map returns NEW array → new reference → React re-renders!
  };

  // ✅ CORRECT: adding item
  const addItem = (newItem) => {
    setItems([...items, newItem]); // spread into NEW array
  };

  // ✅ CORRECT: removing item
  const removeItem = (id) => {
    setItems(items.filter(item => item.id !== id)); // filter returns NEW array
  };

  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>
          {item.name} × {item.qty}
          <button onClick={() => updateQty(item.id)}>+</button>
        </li>
      ))}
    </ul>
  );
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Mutating function parameters
```javascript
// WRONG: modifies original object
function processOrder(order) {
  order.status = "processing"; // mutates original!
  return order;
}

// CORRECT: create new object
function processOrder(order) {
  return { ...order, status: "processing" }; // new object
}
```

❌ **Mistake 2:** Shallow copy thinking it's deep copy
```javascript
// WRONG belief: spread does deep copy
const original = { settings: { theme: "dark" } };
const copy = { ...original };
copy.settings.theme = "light"; // still mutates original.settings!

// CORRECT for nested objects:
const copy = structuredClone(original); // deep copy
```

❌ **Mistake 3:** Comparing objects with ===
```javascript
// WRONG:
const isEqual = obj1 === obj2; // only true if same reference, not same content

// CORRECT ways:
// Simple: JSON.stringify (watch out for edge cases)
const isEqual = JSON.stringify(obj1) === JSON.stringify(obj2);
// Production: use lodash isEqual
import isEqual from "lodash/isEqual";
const isSame = isEqual(obj1, obj2);
```

---

## 🧠 Tricky Interview Output Question
```javascript
function modify(obj, num) {
  obj.value = 100;
  num = 100;
}

let myObj = { value: 1 };
let myNum = 1;

modify(myObj, myNum);

console.log(myObj.value); // ?
console.log(myNum);       // ?
```
**Answer:**
```
100    ← object passed by reference, function modified original
1      ← primitive passed by value, function's local copy changed, original unchanged
```
**Why:** `obj` inside the function is a reference to `myObj` — same object. `num` is a copy of `myNum` — changing it doesn't affect `myNum`.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between pass-by-value and pass-by-reference in JavaScript?**
A1: Primitives are passed by value — functions get a copy, can't affect the original. Objects are passed by reference — functions get the reference, can modify the original's properties. Note: even for objects, you can't change what the variable points to from inside a function (reassigning the parameter locally doesn't affect the outside variable).

**Q2: How do you create a copy of an object without modifying the original?**
A2: For shallow copies: spread operator `{...obj}` or `Object.assign({}, obj)` — these only copy top-level properties; nested objects are still shared. For deep copies: `structuredClone(obj)` (modern, handles most types), `JSON.parse(JSON.stringify(obj))` (simple but loses functions/undefined/Date), or `lodash.cloneDeep` (most complete).

**Q3: Why does React require immutable state updates?**
A3: React uses reference equality to detect state changes. If you mutate an existing object/array, the reference stays the same — React thinks nothing changed and skips re-render. By creating a new array/object, you give React a new reference, and it knows to re-render. This is why spread operator and map/filter (which return new arrays) are essential in React state updates.

**Q4: What does `{} === {}` return and why?**
A4: `false`. Each `{}` creates a new object in a different location in the heap. The `===` operator compares references for objects, not contents. Two objects with identical properties are still different objects unless one is literally the same reference as the other.

**Q5: What is a shallow copy vs deep copy?**
A5: A shallow copy creates a new top-level object but nested objects are still shared (same reference). A deep copy creates completely independent copies at all levels — nested objects are also new copies. Use deep copy when you need to modify nested properties without affecting the original.

---

## 🔷 Trade-offs / When to Use
✅ Shallow copy when:
- Flat objects (no nested objects/arrays)
- React state updates for flat objects
- Performance is critical (deep copy is expensive)

✅ Deep copy when:
- Nested data structures you want to fully isolate
- Configuration objects shared between modules
- Undo/history functionality

❌ Never:
- Mutate objects/arrays in React state directly
- Mutate function parameters (side effects)
- Compare objects with === to check content equality

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Stack | Fast, fixed-size memory | तेज़, fixed-size memory |
| Heap | Flexible memory for objects | Objects के लिए flexible memory |
| Reference | Memory address / pointer | Memory address |
| Shallow copy | Top-level copy, nested shared | ऊपर की copy, nested shared |
| Deep copy | Fully independent copy at all levels | पूरी independent copy |
| Mutation | Changing existing data in place | Existing data बदलना |
| Immutability | Not changing, creating new | नहीं बदलना, नया बनाना |
| structuredClone | Modern built-in deep clone | Modern built-in deep copy |

---

## ⚡ 3-Line Summary
**English:**
1. Primitives live in the stack, copied by value — independent copies; objects live in the heap, copied by reference — both point to same data.
2. Mutating an object inside a function affects the original — avoid this, always return new objects.
3. React requires new references for state — never mutate state directly, use spread/map/filter to create new arrays/objects.

**Hindi:**
1. Primitives stack में value से copy — independent; objects heap में reference से copy — same data point करते हैं।
2. Function में object mutate करने पर original बदलता है — नए object return करो।
3. React के लिए नई reference चाहिए — state को directly mutate मत करो, spread/map/filter से नया बनाओ।

---

## ➡️ Next Topic
**07. Type Conversion + Type Coercion** — Explicit (Number("5")) vs implicit ("5" + 3 = "53") type changes, और why `[] + {}` का output surprising होता है।
