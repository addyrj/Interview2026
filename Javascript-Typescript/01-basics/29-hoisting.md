# 29. Hoisting
# हिंदी में: Hoisting — JavaScript Code Run होने से पहले क्या होता है

---

## 🔵 Simple Definition (English)
**Hoisting** is JavaScript's behavior of moving **variable and function declarations** to the top of their scope **before code runs**. Only the declaration is hoisted — not the value/initialization. This is why you can call a function before declaring it.

## 🔵 सरल परिभाषा (Hindi)
Hoisting JavaScript का behavior है जिसमें variable और function declarations code run होने से **पहले** अपने scope के top पर चली जाती हैं। सिर्फ declaration hoist होती है — value नहीं। इसीलिए function को declare करने से पहले call कर सकते हैं।

---

## 🔴 Problem it Solves (and creates!)
```javascript
// This works (function declaration hoisted):
sayHello(); // "Hello!" — works before declaration
function sayHello() { console.log("Hello!"); }

// This doesn't (var hoisted but not initialized):
console.log(x); // undefined (not an error, but surprising)
var x = 5;

// This crashes (let/const TDZ):
console.log(y); // ReferenceError: Cannot access 'y' before initialization
let y = 10;
```

---

## 🟢 How it Works — JavaScript Engine 2 Phases

```
Phase 1 — CREATION (Compilation):
  → Scans code
  → Registers var declarations → set to undefined
  → Registers function declarations → fully available
  → Registers let/const → in TDZ (Temporal Dead Zone)

Phase 2 — EXECUTION:
  → Runs code line by line
  → var gets value when assignment is reached
  → function declarations already available
  → let/const become available when declaration line runs (exit TDZ)
```

---

## 🟡 Real World Example
```javascript
// ❌ Common confusing bug:
function getUserRole() {
  console.log(role); // undefined — hoisted but not assigned yet!

  var role = "admin";

  console.log(role); // "admin"
}
getUserRole();

// JS sees it as:
function getUserRole() {
  var role; // hoisted to top
  console.log(role); // undefined
  role = "admin";    // assigned here
  console.log(role); // "admin"
}
```

---

## 💻 Code Example — Basic
```javascript
// ── VAR HOISTING ─────────────────────────

// What you write:
console.log(a); // undefined (not ReferenceError!)
var a = 10;
console.log(a); // 10

// What JavaScript actually executes (conceptually):
var a;          // hoisted
console.log(a); // undefined
a = 10;         // assignment stays here
console.log(a); // 10

// In a function:
function test() {
  console.log(b); // undefined
  var b = 20;
  console.log(b); // 20
}

// ── FUNCTION DECLARATION HOISTING ────────

// FULLY hoisted — can call before declaration:
sayHi(); // ✅ "Hi there!"

function sayHi() {
  console.log("Hi there!");
}

// The entire function body is hoisted:
greet("Aditya"); // ✅ "Hello, Aditya!"

function greet(name) {
  console.log(`Hello, ${name}!`);
}

// ── LET/CONST — TEMPORAL DEAD ZONE ───────

// TDZ: let/const are hoisted but NOT initialized
// Accessing before declaration → ReferenceError

// console.log(c); // ❌ ReferenceError: Cannot access 'c' before initialization
let c = 30;
console.log(c); // ✅ 30

// TDZ starts from beginning of scope until the declaration line:
{
  // TDZ for `d` starts here (even though code hasn't reached `let d` yet)
  // console.log(d); // ❌ ReferenceError — in TDZ
  let d = 40;         // TDZ ends here
  console.log(d);     // ✅ 40
}

// ── FUNCTION EXPRESSION HOISTING ─────────

// var function expression: var is hoisted (undefined), function is NOT
// greetExpr(); // ❌ TypeError: greetExpr is not a function

var greetExpr = function(name) {
  console.log(`Hello, ${name}!`);
};
greetExpr("Priya"); // ✅ works after assignment

// Arrow function (same as expression):
// arrowFn(); // ❌ TypeError: arrowFn is not a function
var arrowFn = (x) => x * 2;

// ── COMPARISON TABLE ─────────────────────
// var:               declared as undefined, assignable
// let/const:         declared but in TDZ (uninitialized), ReferenceError if accessed
// function decl:     fully hoisted (declaration + body)
// function expr/arrow: only var part is hoisted (as undefined)
```

## 💻 Code Example — Advanced
```javascript
// ── HOISTING IN DIFFERENT SCOPES ─────────

var globalVar = "global";

function outer() {
  // var declared inside function is hoisted to top of outer()
  // console.log(localVar); // undefined (hoisted within outer)
  // var localVar = "local";

  // Function declaration hoisted within outer():
  inner(); // ✅ works

  function inner() {
    console.log("inner called");
  }
}

outer();

// ── CLASS HOISTING ────────────────────────
// Classes are NOT hoisted (similar to let — TDZ)

// const instance = new MyClass(); // ❌ ReferenceError: Cannot access before initialization

class MyClass {
  constructor() { this.value = 42; }
}

const instance = new MyClass(); // ✅ after declaration

// ── DUPLICATE VAR DECLARATIONS ───────────

var x = 1;
var x = 2; // ✅ no error with var (just overwrites)
console.log(x); // 2

// let x = 3; // ❌ SyntaxError: Identifier 'x' has already been declared

// ── FUNCTION DECLARATION OVERRIDES VAR ───

var foo; // var declaration
function foo() { return "I'm a function"; } // function declaration

console.log(typeof foo); // "function" — function wins over var

var foo = 10; // assignment after function declaration
console.log(typeof foo); // "number" — assignment wins

// ── HOISTING IN CONDITIONAL BLOCKS ───────

// Function declarations in blocks: behavior differs by environment!
// In strict mode (ES2015+): block-scoped
// In non-strict: implementation-defined — avoid!

if (true) {
  function blockFunc() { return "block function"; } // AVOID this pattern!
}

// PREFERRED: use function expressions in blocks
let getFunc;
if (true) {
  getFunc = function() { return "safe function"; };
}

// ── PRACTICAL: WHY THIS MATTERS IN INTERVIEWS ────

// Can you spot the bug?
function processUser(isAdmin) {
  if (isAdmin) {
    var permission = "read-write";
  }
  console.log(permission); // What prints?
  // "read-write" if isAdmin is true
  // undefined if isAdmin is false (var is hoisted to function scope!)
}

processUser(false); // undefined — permission exists but is undefined
processUser(true);  // "read-write"

// Fix: use let (block-scoped)
function processUserFixed(isAdmin) {
  if (isAdmin) {
    let permission = "read-write";
    console.log(permission); // use it here
  }
  // permission not accessible here — intentional!
}
```

---

## 🟠 React/Next.js Connection
```jsx
// ── HOISTING IS WHY THIS WORKS ────────────

// You can use utility functions declared below in the component:
function ProductCard({ product }) {
  const price = formatCurrency(product.price); // ✅ called before declaration

  return <div>₹{price}</div>;
}

// Function declaration hoisted to top of module scope:
function formatCurrency(amount) {
  return new Intl.NumberFormat("en-IN").format(amount);
}

// ── WHY HOOKS MUST BE AT TOP LEVEL ────────
// React relies on call order — hoisting awareness helps understand this

// WRONG (not hoisting-related, but scope-related confusion):
function Component({ isLoggedIn }) {
  if (isLoggedIn) {
    const [data, setData] = useState(null); // ❌ hooks inside condition — wrong!
  }
}

// CORRECT: hooks always at top level, outside conditions
function Component({ isLoggedIn }) {
  const [data, setData] = useState(null); // ✅ always called, every render
  // Conditionally use the value, not the hook
  if (!isLoggedIn) return null;
  return <div>{data}</div>;
}

// ── NODE.JS: AVOID IMPLICIT GLOBALS ──────
// In Node.js modules, top-level 'this' and implicit globals work differently
// Always use 'use strict' or ES modules

"use strict"; // prevents implicit globals

function badFunction() {
  // oops = "I forgot var"; // ❌ ReferenceError in strict mode
  const safe = "properly declared"; // ✅
}
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Relying on var hoisting (leads to undefined surprises)
```javascript
function calculate() {
  console.log(result); // undefined — NOT an error but unexpected!
  // ... many lines of code ...
  var result = 42;
}

// CORRECT: declare variables at top, or use let/const
function calculate() {
  let result; // explicitly undefined, clear intent
  result = 42;
  console.log(result); // 42
}
```

❌ **Mistake 2:** Calling arrow functions before assignment
```javascript
// WRONG: treated as var (hoisted as undefined)
greet("Aditya"); // ❌ TypeError: greet is not a function
var greet = (name) => `Hello, ${name}`;

// CORRECT: use function declaration if you need to call before
function greet(name) { return `Hello, ${name}`; }
greet("Aditya"); // ✅ works anywhere in scope
```

❌ **Mistake 3:** Using `typeof` to avoid TDZ check
```javascript
// typeof on undeclared var = "undefined" (no error)
console.log(typeof undeclared); // "undefined" (no error)

// BUT typeof on let in TDZ = ReferenceError!
// console.log(typeof tdzVar); // ❌ ReferenceError
let tdzVar = 5;
```

---

## 🧠 Tricky Interview Output Question
```javascript
console.log(a); // ?
console.log(b); // ?
console.log(typeof c); // ?

var a = 1;
let b = 2;
const c = 3;

function test() {
  console.log(d); // ?
  var d = 4;
  console.log(d); // ?
}
test();
```
**Answer:**
```
undefined     ← var a hoisted, value not yet assigned
ReferenceError ← let b in TDZ — program stops here!
```
If let b line is removed:
```
undefined     ← var a
"undefined"   ← typeof c (c is in TDZ but typeof doesn't throw)
undefined     ← d inside test() — hoisted to function top
4             ← after assignment
```

---

## ⚫ Interview Questions + Answers

**Q1: What is hoisting in JavaScript?**
A1: Hoisting is the JavaScript engine's behavior during the compilation phase — before execution, it scans the code and: (1) Registers `var` declarations, setting them to `undefined`. (2) Registers function declarations fully (declaration + body). (3) Registers `let`/`const` declarations but keeps them in the Temporal Dead Zone (uninitialized). Only declarations are hoisted — assignments/initializations stay in place.

**Q2: What is the Temporal Dead Zone (TDZ)?**
A2: TDZ is the period from the start of a block scope until the `let`/`const` declaration line is reached. During TDZ, the variable exists in scope (hoisted) but is uninitialized — accessing it throws `ReferenceError`. This is stricter than `var`'s `undefined` behavior and catches more bugs. TDZ encourages declaring variables before using them.

**Q3: What is the difference between function declarations and function expressions in terms of hoisting?**
A3: Function **declarations** are fully hoisted — the entire function body is available from the start of the scope, so you can call them before the declaration line. Function **expressions** (assigned to `var`) only hoist the `var` part (set to `undefined`) — calling them before assignment gives `TypeError: fn is not a function`. Arrow functions assigned to `let`/`const` throw `ReferenceError` (TDZ).

**Q4: Why is hoisting considered a footgun (source of bugs)?**
A4: `var` hoisting makes variables exist with `undefined` value before their assignment, which can lead to subtle bugs — code that doesn't crash but gives wrong results. The classic example: accessing a `var` before its assignment returns `undefined` instead of an error, making bugs harder to track. `let`/`const` solve this with TDZ — they fail loudly with `ReferenceError` instead of silently returning `undefined`.

**Q5: How do you write code that avoids hoisting-related issues?**
A5: (1) Use `const` and `let` instead of `var`. (2) Declare variables at the top of their scope. (3) Use function expressions/arrows when you want to avoid accidental hoisting. (4) Enable strict mode (`"use strict"`) or use ES modules (implicit strict). (5) Declare all variables before use — treat hoisting as an implementation detail, not a feature.

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hoisting | Declarations moved to top of scope | Declarations scope के top पर जाना |
| TDZ | Temporal Dead Zone — let/const uninitialized | TDZ — let/const uninitialized phase |
| Creation phase | Scanning and registering declarations | Code scan और declarations register |
| Execution phase | Running code line by line | Line by line code run |
| Fully hoisted | Declaration + body available | Declaration + body available |
| Initialized | Variable has a value (not uninitialized) | Variable को value मिल गई |

---

## ⚡ 3-Line Summary
**English:**
1. Hoisting: `var` declarations → `undefined` before execution; function declarations → fully available; `let`/`const` → TDZ (ReferenceError if accessed).
2. Only declarations are hoisted — not assignments. `var x = 5` hoists `var x` but `x = 5` stays in place.
3. Avoid hoisting bugs: use `const`/`let`, declare at top of scope, never rely on var's undefined hoisting.

**Hindi:**
1. Hoisting: `var` declarations → `undefined` पहले; function declarations → fully available; `let`/`const` → TDZ (ReferenceError)।
2. सिर्फ declarations hoist होती हैं — assignments नहीं। `var x = 5` में `var x` hoist होता है, `x = 5` वहीं रहता है।
3. Bugs avoid करो: `const`/`let` use करो, scope के top पर declare करो, var की undefined hoisting पर rely मत करो।

---

## ➡️ Next Topic
**30. Closures** — Functions जो अपने outer scope को याद रखती हैं — JavaScript की सबसे powerful feature।
