# 03. Variables — var, let, const
# हिंदी में: Variables — JavaScript में Data Store करने के तीन तरीके

---

## 🔵 Simple Definition (English)
Variables are **named containers** that store data. JavaScript has three ways to declare them: `var` (old, function-scoped), `let` (modern, block-scoped, reassignable), and `const` (modern, block-scoped, not reassignable).

## 🔵 सरल परिभाषा (Hindi)
Variables वो डिब्बे हैं जिनमें data रखते हैं। JavaScript में तीन तरीके हैं: `var` (पुराना, function-scoped), `let` (आधुनिक, block-scoped, बदल सकते), `const` (आधुनिक, block-scoped, नहीं बदल सकते)।

---

## 🔴 Problem it Solves
Before `let`/`const` (ES6, 2015), only `var` existed:
- `var` leaked out of `if/for` blocks → unexpected bugs
- `var` could be re-declared accidentally → silent overwriting
- No way to say "this value should never change"

`let` and `const` fixed these with **block scoping** and **const protection**.

## 🔴 यह क्यों बना? (Hindi)
पहले सिर्फ `var` था जो if/for blocks से बाहर leak होता था, गलती से redeclare हो जाता था, और कोई const नहीं था। ES6 में `let` और `const` आए जो ये problems fix करते हैं।

---

## 🟢 How it Works — Step by Step

```
var   → function-scoped, hoisted (undefined), can redeclare, can reassign
let   → block-scoped,    hoisted (TDZ),        no redeclare,  can reassign
const → block-scoped,    hoisted (TDZ),        no redeclare,  no reassign
```

### Scope comparison
```javascript
function example() {
  if (true) {
    var x = 10;    // function scope — leaks outside if block
    let y = 20;    // block scope — stays inside {}
    const z = 30;  // block scope — stays inside {}
  }
  console.log(x);  // 10 — var leaked out
  console.log(y);  // ReferenceError — let didn't leak
  console.log(z);  // ReferenceError — const didn't leak
}
```

### Memory: how they are stored
```
var   → attached to function (or global) scope object
let   → stored in block scope (not on any object)
const → same as let, but marked as non-writable
```

## 🟢 कैसे काम करता है? (Hindi)
- `var`: function के अंदर कहीं भी declare करो, पूरे function में available
- `let`: सिर्फ उस `{}` block में available जहाँ declare हुआ
- `const`: `let` जैसा, लेकिन value को reassign नहीं कर सकते

---

## 🟡 Real World Example
**Shopping Cart (E-commerce):**
```javascript
// const: cart object बदलेगा नहीं (reference fix)
const cart = [];

// let: loop counter — block में रहे
for (let i = 0; i < products.length; i++) {
  cart.push(products[i]);
}

// var का पुराना bug:
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 100);
}
// Output: 5 5 5 5 5 — var leaked! loop खत्म हो गया

for (let i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 100);
}
// Output: 0 1 2 3 4 — let ने हर iteration का i capture किया
```

## 🟡 Real Example Hindi mein
Zomato में cart की list `const` में रखेंगे (reference नहीं बदलेगा), items add/remove होंगे। Loop counter के लिए `let` use करेंगे। `var` से पुराना bug था जहाँ setTimeout loop में सबको same `i` मिलता था।

---

## 💻 Code Example — Basic
```javascript
// ── var ──────────────────────────────
var name = "Aditya";       // declare and assign
var name = "Rajan";        // ✅ re-declare allowed (bad practice)
name = "Kumar";            // ✅ re-assign allowed
console.log(name);         // "Kumar"

// ── let ──────────────────────────────
let age = 25;              // declare and assign
// let age = 30;           // ❌ SyntaxError: already declared
age = 26;                  // ✅ re-assign allowed
console.log(age);          // 26

// ── const ─────────────────────────────
const PI = 3.14159;        // declare and assign
// PI = 3.14;              // ❌ TypeError: Assignment to constant variable
// const PI = 3;           // ❌ SyntaxError: already declared
console.log(PI);           // 3.14159

// const with objects (important!)
const user = { name: "Aditya" };
user.name = "Rajan";       // ✅ ALLOWED — object property change कर सकते
// user = {};              // ❌ NOT allowed — reference नहीं बदल सकते
console.log(user.name);    // "Rajan"
```

## 💻 Code Example — Advanced
```javascript
// ── var का scope bug ──────────────────
function varScopeBug() {
  console.log(x); // undefined (hoisted, not error)
  
  if (true) {
    var x = "inside if"; // var — function scope
  }
  
  console.log(x); // "inside if" — leaked out of if block!
}
varScopeBug();

// ── let block scope — correct behavior ──
function letBlockScope() {
  // console.log(y); // ❌ ReferenceError: TDZ (Temporal Dead Zone)
  
  if (true) {
    let y = "inside if"; // let — block scope
    console.log(y);      // ✅ "inside if"
  }
  
  // console.log(y); // ❌ ReferenceError — y doesn't exist here
}
letBlockScope();

// ── Classic var vs let in loops ──────
// PROBLEM with var:
const varFunctions = [];
for (var i = 0; i < 3; i++) {
  varFunctions.push(() => console.log(i)); // all capture same i
}
varFunctions[0](); // 3 — not 0!
varFunctions[1](); // 3 — not 1!
varFunctions[2](); // 3 — not 2!
// var i is shared, loop finished at i=3

// SOLUTION with let:
const letFunctions = [];
for (let j = 0; j < 3; j++) {
  letFunctions.push(() => console.log(j)); // each iteration gets its own j
}
letFunctions[0](); // 0 ✅
letFunctions[1](); // 1 ✅
letFunctions[2](); // 2 ✅
// let creates new binding per iteration

// ── const with arrays/objects ──────
const config = {
  apiUrl: "https://api.example.com",
  timeout: 5000,
};

// Properties change कर सकते हो
config.timeout = 10000;        // ✅ allowed
config.newProp = "added";      // ✅ allowed
// config = {};                // ❌ TypeError

// Freeze करो अगर truly immutable चाहिए
const frozenConfig = Object.freeze({
  apiUrl: "https://api.example.com",
  timeout: 5000,
});
frozenConfig.timeout = 9999;   // silently fails (strict mode में error)
console.log(frozenConfig.timeout); // still 5000
```

---

## 🟠 React/Next.js Connection
```jsx
import { useState, useEffect } from "react";

// const — components हमेशा const functions होते हैं
const ProductCard = ({ product }) => {
  // let — useState से आने वाली values reassign होती हैं internally
  const [quantity, setQuantity] = useState(1); // const (state object)
  
  // const — computed values जो render में बदलती नहीं
  const totalPrice = product.price * quantity;
  const isExpensive = totalPrice > 1000;
  
  useEffect(() => {
    // let — loop में block scoping जरूरी
    for (let i = 0; i < quantity; i++) {
      console.log(`Tracking item ${i + 1}`);
    }
  }, [quantity]);

  return (
    <div>
      <p>Price: ₹{totalPrice}</p>
      {isExpensive && <span>Premium Item</span>}
      <button onClick={() => setQuantity(q => q + 1)}>Add More</button>
    </div>
  );
};

// Node.js (server) में best practice:
// const fs = require("fs");          — module imports हमेशा const
// const express = require("express"); — same
// const app = express();              — app instance const
// let port = process.env.PORT || 3000; — port let (environment से बदल सकता)
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** `var` को modern code में use करना
```javascript
// WRONG:
for (var i = 0; i < buttons.length; i++) {
  buttons[i].onclick = function() { alert(i); }; // always alerts last i
}

// CORRECT:
for (let i = 0; i < buttons.length; i++) {
  buttons[i].onclick = function() { alert(i); }; // correct i each time
}
```

❌ **Mistake 2:** `const` का मतलब सोचना कि object immutable है
```javascript
// WRONG belief:
const user = { name: "Aditya" };
// "const है तो user कभी नहीं बदलेगा" — WRONG!
user.name = "Rajan"; // यह allowed है!

// CORRECT understanding:
// const = reference नहीं बदलेगा, properties बदल सकती हैं
// Truly immutable चाहिए? → Object.freeze() use करो
```

❌ **Mistake 3:** `let`/`const` को declare से पहले access करना
```javascript
// WRONG:
console.log(myVar); // undefined (var hoisting)
console.log(myLet); // ❌ ReferenceError (TDZ!)
var myVar = 5;
let myLet = 10;

// CORRECT: हमेशा declare करने के बाद use करो
let myLet = 10;
console.log(myLet); // 10 ✅
```

---

## 🧠 Tricky Interview Output Question
```javascript
let x = 1;

function outer() {
  let x = 2;
  function inner() {
    let x = 3;
    console.log(x); // ?
  }
  inner();
  console.log(x); // ?
}

outer();
console.log(x); // ?
```
**Answer:**
```
3   ← inner's x
2   ← outer's x
1   ← global x
```
**Why:** Each `let` creates its own block-scoped variable. `inner` has its own `x`, so it doesn't touch `outer`'s or global's `x`. This is lexical scoping.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between var, let, and const?**
A1: `var` is function-scoped, hoisted as `undefined`, can be re-declared and re-assigned. `let` is block-scoped, hoisted but in TDZ (accessing before declaration is a ReferenceError), cannot be re-declared, can be re-assigned. `const` is like `let` but also cannot be re-assigned. For objects/arrays with `const`, the reference is fixed but properties can change.

**Q2: Why should you avoid using var?**
A2: Three reasons: (1) Function scope causes variables to leak out of if/for blocks, causing bugs. (2) It can be accidentally re-declared without error, silently overwriting values. (3) Hoisting to `undefined` makes code order confusing. `let` and `const` are predictable, block-scoped, and the modern standard.

**Q3: Is const truly immutable?**
A3: No. `const` only prevents re-assignment of the binding (you can't point the variable to a new value). For primitives (numbers, strings) this means the value can't change. For objects and arrays, the reference is fixed but properties/elements can be changed freely. To make an object truly immutable, use `Object.freeze()` — though it's shallow (nested objects aren't frozen).

**Q4: What happens when you use let in a for loop vs var?**
A4: With `var`, a single `i` variable is shared across all iterations. When callbacks (like setTimeout) run after the loop, they all see the final value of `i`. With `let`, JavaScript creates a new `i` binding for each iteration, so each callback captures its own `i`. This is the classic closure-in-a-loop problem.

**Q5: What is the Temporal Dead Zone (TDZ)?**
A5: The TDZ is the period between entering a block scope and the `let`/`const` declaration being reached. During this time, the variable is "hoisted" (known to exist) but cannot be accessed — any attempt throws a ReferenceError. This is intentional: it prevents the confusing `undefined` behavior of `var` hoisting.

---

## 🔷 Trade-offs / When to Use
✅ Use `const` when:
- Default choice for everything
- Module imports, component definitions
- Config objects, arrays you'll mutate but not reassign

✅ Use `let` when:
- Variable needs to be reassigned (counters, accumulated values)
- Loop variables

❌ Avoid `var` always:
- No valid reason in modern JavaScript
- Linters (ESLint `no-var` rule) can enforce this

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Variable | Named container for data | Data रखने का नाम वाला डिब्बा |
| Declaration | Creating a variable (`let x`) | Variable बनाना |
| Assignment | Giving a value (`x = 5`) | Value देना |
| Scope | Where variable is accessible | Variable कहाँ accessible है |
| Block scope | Accessible only inside `{}` | सिर्फ `{}` के अंदर |
| Function scope | Accessible inside whole function | पूरे function में |
| Hoisting | Variable moved to top conceptually | Variable ऊपर चला जाता है |
| TDZ | Temporal Dead Zone — can't access before declaration | Declaration से पहले access नहीं |
| Re-assign | Change the value | Value बदलना |
| Re-declare | Declare again with same name | Same नाम से फिर declare |

---

## ⚡ 3-Line Summary
**English:**
1. `var` is function-scoped and hoists to `undefined` — avoid it in modern JS.
2. `let` is block-scoped, can be reassigned, throws ReferenceError if accessed before declaration (TDZ).
3. `const` is like `let` but can't be reassigned — use it by default; objects/arrays declared with `const` can still have their contents mutated.

**Hindi:**
1. `var` function-scoped है, undefined पर hoist होता है — modern JS में avoid करो।
2. `let` block-scoped है, reassign हो सकता है, declaration से पहले ReferenceError देता है।
3. `const` default choice होनी चाहिए — reference fix रहता है, object properties बदल सकती हैं।

---

## ➡️ Next Topic
**04. var vs let vs const — Differences (Deep Dive)** — scope, hoisting, TDZ का और गहरा comparison, real interview questions।
