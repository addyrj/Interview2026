# 28. Scope — Global, Function, Block, Lexical
# हिंदी में: Scope — Variable कहाँ से Accessible है और कहाँ नहीं

---

## 🔵 Simple Definition (English)
**Scope** defines where a variable is accessible (visible) in your code. JavaScript has: **global scope** (everywhere), **function scope** (inside a function), **block scope** (inside `{}`), and **lexical scope** (inner functions access outer variables).

## 🔵 सरल परिभाषा (Hindi)
Scope define करता है कि variable code में कहाँ accessible (visible) है। JavaScript में: **global scope** (हर जगह), **function scope** (function के अंदर), **block scope** (`{}` के अंदर), और **lexical scope** (inner function outer variables access कर सके)।

---

## 🔴 Problem it Solves
Without scope, every variable would be global — functions would accidentally overwrite each other's variables. Scope keeps variables contained, prevents naming conflicts, and enables closures.

---

## 🟢 How it Works — Scope Chain
```
Outer (Global) scope
  └── Function scope
        └── Block scope
              └── Inner function scope

Inner can see outer. Outer CANNOT see inner.
When a variable is looked up: current scope → outer scope → ... → global
```

---

## 🟡 Real World Example
```javascript
// Global scope — accessible everywhere
const APP_NAME = "ZomatoClone";

function processOrder(orderId) {
  // Function scope — only inside processOrder
  const orderStatus = "preparing";

  if (orderId > 1000) {
    // Block scope — only inside this if block
    const discount = 50; // let/const = block scoped
    var promoApplied = true; // var = function scoped (escapes block!)
    console.log(discount); // ✅ accessible here
  }

  console.log(orderStatus);  // ✅ function scope
  console.log(APP_NAME);     // ✅ global scope
  console.log(promoApplied); // ✅ var escapes the if block!
  // console.log(discount);  // ❌ ReferenceError — block scoped
}
```

---

## 💻 Code Example — Basic
```javascript
// ── GLOBAL SCOPE ─────────────────────────

let globalMessage = "Hello from global";

function showMessage() {
  console.log(globalMessage); // ✅ can access global
}

showMessage(); // "Hello from global"

// Browser global: window object
// Node.js global: global object
// In browser: variables in global scope become properties of window
var x = 10;
console.log(window.x); // 10 (in browser only!)
// let/const do NOT become window properties

// ── FUNCTION SCOPE ───────────────────────

function calculate() {
  var result = 42;      // function scoped
  let precision = 2;   // also function scoped (block = function body)
  return result.toFixed(precision);
}

// console.log(result);   // ❌ ReferenceError — outside function
// console.log(precision); // ❌ ReferenceError — outside function

// ── BLOCK SCOPE ──────────────────────────

// let and const are BLOCK scoped
{
  let blockVar = "I'm block scoped";
  const blockConst = "Me too";
  var funcVar = "I escape the block!"; // var is NOT block scoped
  console.log(blockVar); // ✅
}
// console.log(blockVar);  // ❌ ReferenceError
// console.log(blockConst);// ❌ ReferenceError
console.log(funcVar);      // ✅ "I escape the block!"

// if blocks:
if (true) {
  let a = 1;
  var b = 2;
}
// console.log(a); // ❌ ReferenceError
console.log(b);    // ✅ 2 (var escapes if block)

// for loop variable scope:
for (let i = 0; i < 3; i++) { /* i is block-scoped */ }
// console.log(i); // ❌ ReferenceError with let

for (var j = 0; j < 3; j++) { /* j is function-scoped */ }
console.log(j); // ✅ 3 (var leaks out of for loop)

// ── LEXICAL (STATIC) SCOPE ───────────────
// Functions remember the scope where they were DEFINED, not where called

const outerVar = "I'm outer";

function outer() {
  const outerFunc = "outer function var";

  function inner() {
    // inner can see: its own scope + outer() scope + global scope
    console.log(outerVar);   // ✅ global
    console.log(outerFunc);  // ✅ outer function scope
  }

  inner();
}

outer();

// ── SCOPE CHAIN EXAMPLE ──────────────────

const level1 = "L1";

function level2() {
  const l2 = "L2";

  function level3() {
    const l3 = "L3";

    function level4() {
      // Can access all outer scopes:
      console.log(level1); // ✅ global
      console.log(l2);     // ✅ level2's scope
      console.log(l3);     // ✅ level3's scope
      // l4 doesn't exist yet in this level
    }

    level4();
  }

  level3();
}

level2();
```

## 💻 Code Example — Advanced
```javascript
// ── CLOSURE — SCOPE REMEMBERED ──────────

function makeCounter(initial = 0) {
  let count = initial; // in makeCounter's function scope

  return {
    increment: () => ++count,  // closure: remembers `count`
    decrement: () => --count,  // closure: remembers `count`
    getCount:  () => count,    // closure: remembers `count`
  };
}

const counter1 = makeCounter(0);
const counter2 = makeCounter(10); // separate closure

counter1.increment(); // 1
counter1.increment(); // 2
counter2.increment(); // 11

console.log(counter1.getCount()); // 2 — private to counter1
console.log(counter2.getCount()); // 11 — private to counter2

// ── CLASSIC CLOSURE BUG WITH VAR ─────────

// WRONG: var in for loop shares same scope
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// Output: 3, 3, 3 (NOT 0, 1, 2!)
// Why: var i is function-scoped — all callbacks share same i
// By the time callbacks run (after 100ms), loop is done, i=3

// FIX 1: use let (block-scoped — each iteration gets own i)
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 100);
}
// Output: 0, 1, 2 ✅

// FIX 2: IIFE (Immediately Invoked Function Expression)
for (var i = 0; i < 3; i++) {
  ((j) => setTimeout(() => console.log(j), 100))(i);
}
// Output: 0, 1, 2 ✅ — each IIFE captures its own j

// ── MODULE SCOPE ─────────────────────────
// ES Modules have their own scope (nothing leaks to global)

// file: math.js
const PI = 3.14159; // module scoped
export function area(r) { return PI * r * r; }
// PI is NOT accessible outside this module unless exported

// ── SCOPE AND HOISTING ───────────────────

console.log(hoisted);  // undefined (var is hoisted, value isn't)
var hoisted = "hello";

// console.log(notHoisted); // ❌ ReferenceError (TDZ — let/const)
let notHoisted = "world";

// Function declarations are fully hoisted:
sayHi(); // ✅ "Hi!" — called before declaration
function sayHi() { console.log("Hi!"); }

// Function expressions are NOT:
// greet(); // ❌ TypeError: greet is not a function
var greet = function() { console.log("Hello!"); };
```

---

## 🟠 React/Next.js Connection
```jsx
// ── COMPONENT SCOPE ───────────────────────

// Each component function has its own scope
function Counter() {
  let count = 0;  // function scope — resets on every render!
  // That's why we need useState — it persists OUTSIDE render

  const [persistedCount, setPersistedCount] = useState(0); // survives renders
}

// ── CLOSURES IN EVENT HANDLERS ────────────

function ShoppingCart({ items }) {
  // handleRemove "closes over" setItems — lexical scope
  const [cartItems, setCartItems] = useState(items);

  // This function is defined in ShoppingCart's scope
  // and "captures" setCartItems via closure
  const handleRemove = (id) => {
    setCartItems(prev => prev.filter(item => item.id !== id));
  };

  return (
    <ul>
      {cartItems.map(item => (
        <li key={item.id}>
          {item.name}
          <button onClick={() => handleRemove(item.id)}>Remove</button>
          {/* ↑ arrow function closes over item.id (lexical scope) */}
        </li>
      ))}
    </ul>
  );
}

// ── MODULE SCOPE IN NEXT.JS ───────────────

// lib/constants.js — module scope, doesn't pollute global
const MAX_CART_SIZE = 10;
const FREE_DELIVERY_THRESHOLD = 500;

export { MAX_CART_SIZE, FREE_DELIVERY_THRESHOLD };

// ── BLOCK SCOPE IN HANDLERS ───────────────
app.post("/api/checkout", async (req, res) => {
  const { userId, cartId } = req.body;

  // Each request has its own function scope
  // No chance of one request's variables bleeding into another
  const cart = await Cart.findById(cartId);
  const order = await Order.create({ userId, items: cart.items });

  res.json({ orderId: order.id });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Accidentally creating global variables
```javascript
function calculate() {
  result = 42; // No var/let/const → implicit global! (strict mode prevents this)
}
calculate();
console.log(result); // 42 — leaked to global scope!

// CORRECT: always declare variables
function calculate() {
  const result = 42; // ✅ stays inside function
}
// Always use 'use strict' or ES modules (implicit strict)
```

❌ **Mistake 2:** var leaking from if/for blocks
```javascript
if (true) {
  var leaked = "I leak";
}
console.log(leaked); // "I leak" — var escapes if block!

// CORRECT: use let/const
if (true) {
  let contained = "I'm contained";
}
// console.log(contained); // ❌ ReferenceError ✅
```

❌ **Mistake 3:** var in loops + async (the classic bug)
```javascript
// WRONG: all setTimeout callbacks close over same 'i'
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 1000); // 5,5,5,5,5

// CORRECT: let creates new binding per iteration
for (let i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 1000); // 0,1,2,3,4
}
```

---

## 🧠 Tricky Interview Output Question
```javascript
var x = 1;

function outer() {
  var x = 2;

  function inner() {
    var x = 3;
    console.log(x); // A
  }

  inner();
  console.log(x); // B
}

outer();
console.log(x); // C
```
**Answer:**
```
3  ← A: inner's own x
2  ← B: outer's x (inner's x is gone)
1  ← C: global x (outer's x is gone)
```
**Why:** Each function has its own `x`. No shadowing confusion — each scope has its own copy.

---

## ⚫ Interview Questions + Answers

**Q1: What are the different types of scope in JavaScript?**
A1: (1) **Global scope** — variables declared outside any function/block; accessible everywhere. (2) **Function scope** — `var`, function params, and nested functions; accessible only within that function. (3) **Block scope** — `let`/`const` inside `{}`; accessible only within that block. (4) **Module scope** — each ES module has its own scope; nothing leaks to global unless exported. (5) **Lexical scope** — inner functions can access outer scope variables (basis of closures).

**Q2: What is lexical scope?**
A2: Lexical (static) scope means a function's scope is determined by **where it's written in the code**, not where it's called. So an inner function always has access to variables in its outer function — this is fixed at write time, not call time. This is the foundation of closures: a function "closes over" (remembers) the scope where it was defined.

**Q3: What is the difference between var, let, and const in terms of scope?**
A3: `var` is **function-scoped** — it leaks out of `if`, `for`, `while` blocks, only stopped by function boundaries. `let` and `const` are **block-scoped** — contained within any `{}`. `var` is hoisted (initialized to `undefined`); `let`/`const` are hoisted but in TDZ (Temporal Dead Zone — uninitialized). Always prefer `const`, then `let`.

**Q4: What is a closure?**
A4: A closure is a function that "closes over" (remembers) variables from its outer scope, even after the outer function has returned. Example: a counter factory returns an increment function — that function retains access to the `count` variable in the outer scope. This enables private state, module patterns, and React hooks.

**Q5: Why does `var` in a for loop cause the "3,3,3" bug with setTimeout?**
A5: `var` is function-scoped, not block-scoped. All iterations share the same `var i` binding. By the time the setTimeout callbacks fire (after the loop finishes), `i` is already `3`. `let` fixes this because it creates a new binding per iteration — each closure captures its own independent copy of `i`.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Scope | Where a variable is accessible | Variable कहाँ accessible है |
| Global scope | Accessible everywhere | हर जगह accessible |
| Function scope | Inside a function | Function के अंदर |
| Block scope | Inside `{}` | `{}` के अंदर |
| Lexical scope | Inner sees outer (by location) | Inner outer का access रखे |
| Scope chain | Looking up outer scopes | Outer scopes में देखना |
| Closure | Function + its outer scope | Function + outer scope memory |
| Hoisting | Variable/function moved to top | Variable/function ऊपर जाना |

---

## ⚡ 3-Line Summary
**English:**
1. Scope = where a variable is visible; `var` = function scope, `let`/`const` = block scope — prefer block scope.
2. Lexical scope: inner functions always access outer variables — this is how closures work.
3. Classic `var` + loop bug: all closures share same var — fix with `let` (new binding per iteration).

**Hindi:**
1. Scope = variable कहाँ visible है; `var` = function scope, `let`/`const` = block scope — block scope prefer करो।
2. Lexical scope: inner functions outer variables access करते हैं — closures इसी से बनती हैं।
3. Classic `var` + loop bug: सब closures same var share करते हैं — `let` से fix (हर iteration नई binding)।

---

## ➡️ Next Topic
**29. Hoisting** — Variables और functions code run होने से पहले कैसे "उठाए" जाते हैं।
