# 04. var vs let vs const — Deep Comparison
# हिंदी में: var vs let vs const — पूरा अंतर एक जगह

---

## 🔵 Simple Definition (English)
This is the complete side-by-side comparison of all three declaration keywords — scope, hoisting, TDZ, re-declaration, re-assignment, and when to use each. This is **one of the most asked JavaScript interview topics**.

## 🔵 सरल परिभाषा (Hindi)
तीनों keywords का पूरा comparison — scope, hoisting, TDZ, redeclaration, reassignment। यह JavaScript interview में सबसे ज़्यादा पूछे जाने वाले topics में से एक है।

---

## 🔴 Problem it Solves
Knowing the difference prevents:
- Accidental variable leaking from loops/blocks
- Silent overwriting due to re-declaration
- Confusion over why `undefined` comes from nowhere
- The classic `var` in loop + setTimeout bug

## 🔴 यह क्यों बना? (Hindi)
इन differences को जानना bugs prevent करता है — loop से variable leak, accidental overwrite, mysterious undefined, और setTimeout loop bug।

---

## 🟢 Complete Comparison Table

```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│ Feature         │ var          │ let          │ const        │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Scope           │ Function     │ Block        │ Block        │
│ Hoisting        │ Yes (undef.) │ Yes (TDZ)    │ Yes (TDZ)    │
│ Re-declare      │ ✅ Allowed   │ ❌ Error     │ ❌ Error     │
│ Re-assign       │ ✅ Allowed   │ ✅ Allowed   │ ❌ Error     │
│ Global property │ Yes (window) │ No           │ No           │
│ Initialize req. │ No           │ No           │ Yes ⚠️       │
│ Use in 2024     │ ❌ Avoid     │ ✅ When needed│ ✅ Default  │
└─────────────────┴──────────────┴──────────────┴──────────────┘
```

## 🟢 कैसे काम करता है? (Hindi)
ऊपर के table में सब differences हैं। Key points:
- `var` पूरे function में accessible है
- `let`/`const` सिर्फ `{}` block में
- `var` hoist होकर `undefined` बनता है
- `let`/`const` hoist होते हैं लेकिन TDZ में — access किया तो error
- `const` बिना value के declare नहीं हो सकता

---

## 🟡 Real World Example
```javascript
// E-commerce checkout flow

// const: constants जो कभी नहीं बदलते
const TAX_RATE = 0.18;          // 18% GST
const MAX_CART_ITEMS = 10;

// let: values जो process में बदलती हैं
let subtotal = 0;
let discount = 0;
let finalAmount = 0;

// var का bug — real production issue
function calculateOldWay() {
  for (var i = 0; i < items.length; i++) {
    // var i leak करता है for loop से बाहर
  }
  console.log(i); // items.length — leaked!
}

// let से fix
function calculateNewWay() {
  for (let i = 0; i < items.length; i++) {
    subtotal += items[i].price;
  }
  // console.log(i); // ReferenceError — correctly contained
  finalAmount = subtotal * (1 + TAX_RATE) - discount;
}
```

## 🟡 Real Example Hindi mein
Zomato checkout: `const TAX_RATE = 0.05` — कभी नहीं बदलता। `let total = 0` — items add होती हैं तो बदलेगा। Loop counter `let i` — block में रहे। `var` use करने पर loop counter leak होकर bugs आते।

---

## 💻 Code Example — Basic
```javascript
// ══ SCOPE ════════════════════════════════════════

// var: Function scope
function testVar() {
  if (true) {
    var message = "I am var"; // var — function scope
  }
  console.log(message); // ✅ "I am var" — leaked from if block
}
testVar();

// let: Block scope
function testLet() {
  if (true) {
    let message = "I am let"; // let — block scope
    console.log(message);     // ✅ "I am let"
  }
  // console.log(message); // ❌ ReferenceError
}
testLet();

// ══ HOISTING ═════════════════════════════════════

console.log(a); // undefined (hoisted, initialized as undefined)
var a = 5;

// console.log(b); // ❌ ReferenceError: Cannot access 'b' before initialization
let b = 10;

// ══ RE-DECLARATION ═══════════════════════════════

var x = 1;
var x = 2; // ✅ No error (var allows this - dangerous!)
console.log(x); // 2

let y = 1;
// let y = 2; // ❌ SyntaxError: Identifier 'y' has already been declared

// ══ RE-ASSIGNMENT ════════════════════════════════

let count = 0;
count = 1;     // ✅ allowed
count++;       // ✅ allowed
console.log(count); // 2

const MAX = 100;
// MAX = 200;  // ❌ TypeError: Assignment to constant variable

// ══ GLOBAL OBJECT ════════════════════════════════

var globalVar = "I'm on window";
let globalLet = "I'm NOT on window";

console.log(window.globalVar); // "I'm on window" (in browser)
console.log(window.globalLet); // undefined
```

## 💻 Code Example — Advanced
```javascript
// ══ THE CLASSIC LOOP BUG ═══════════════════════

// Problem: var in loop + async
function varLoopBug() {
  const buttons = document.querySelectorAll("button");
  
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
      alert("Button " + i); // Always alerts buttons.length!
    });
    // Why? var i is shared. By click time, loop is done, i = buttons.length
  }
}

// Fix 1: let (modern, clean)
function letLoopFix() {
  const buttons = document.querySelectorAll("button");
  
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
      alert("Button " + i); // Correct! let creates new i each iteration
    });
  }
}

// Fix 2: IIFE (old way before ES6)
function iifeLoopFix() {
  const buttons = document.querySelectorAll("button");
  
  for (var i = 0; i < buttons.length; i++) {
    (function(j) { // Immediately Invoked — captures i as j
      buttons[j].addEventListener("click", function() {
        alert("Button " + j); // j is captured per iteration
      });
    })(i);
  }
}

// ══ TEMPORAL DEAD ZONE (TDZ) DEEP DIVE ══════════

// TDZ exists from start of block to declaration line
{
  // TDZ for `myVar` starts here ↓
  // console.log(myVar); // ❌ ReferenceError (in TDZ)
  // console.log(myVar); // ❌ ReferenceError (still in TDZ)
  let myVar = "hello"; // TDZ ends here ↑
  console.log(myVar);  // ✅ "hello"
}

// Why TDZ? Prevents confusing undefined behavior of var
// This was a real source of bugs in old JS code

// ══ CONST WITH OBJECTS ═══════════════════════════

// Object.freeze — shallow immutability
const config = Object.freeze({
  apiUrl: "https://api.example.com",
  settings: {
    timeout: 5000 // nested object is NOT frozen
  }
});

config.apiUrl = "other.com";     // Silently fails (strict mode: TypeError)
config.settings.timeout = 9999;  // ✅ WORKS — nested not frozen!
console.log(config.apiUrl);         // "https://api.example.com" (unchanged)
console.log(config.settings.timeout); // 9999 (changed!)

// Deep freeze helper
function deepFreeze(obj) {
  Object.keys(obj).forEach(key => {
    if (typeof obj[key] === "object" && obj[key] !== null) {
      deepFreeze(obj[key]); // recursively freeze nested objects
    }
  });
  return Object.freeze(obj);
}

const deepFrozen = deepFreeze({ nested: { value: 42 } });
deepFrozen.nested.value = 99; // Silently fails
console.log(deepFrozen.nested.value); // 42 — truly immutable!

// ══ SWITCH STATEMENT SCOPE GOTCHA ════════════════

switch (action) {
  case "LOGIN":
    let user = getUser(); // ❌ SyntaxError if another case also declares 'user'
    break;
  case "LOGOUT":
    let user = null; // ❌ 'user' already declared in this switch block
    break;
}

// CORRECT: wrap each case in its own block
switch (action) {
  case "LOGIN": {          // {} creates a new block scope
    let user = getUser();  // ✅ scoped to this case only
    break;
  }
  case "LOGOUT": {
    let user = null;       // ✅ different scope
    break;
  }
}
```

---

## 🟠 React/Next.js Connection
```jsx
// React best practices align with let/const rules

// ✅ Components always const arrow functions
const Header = () => <h1>My App</h1>;

// ✅ Hooks return values are const (React controls them)
const [count, setCount] = useState(0);
const [user, setUser] = useState(null);

// ✅ Derived values are const
const isLoggedIn = user !== null;
const itemCount = cart.reduce((sum, item) => sum + item.qty, 0);

// ✅ useEffect cleanup example showing let scope
useEffect(() => {
  let isActive = true; // let: will be changed in cleanup

  fetchUser(userId).then(data => {
    if (isActive) { // prevents state update on unmounted component
      setUser(data);
    }
  });

  return () => {
    isActive = false; // cleanup: reassign let variable
  };
}, [userId]);

// Node.js patterns
// const router = require("express").Router(); — always const
// const db = require("./database");           — always const

// let for accumulated results in server handlers
app.get("/cart/total", async (req, res) => {
  let total = 0; // let: will be accumulated
  
  for (const item of req.user.cart) { // const in for-of (item doesn't reassign)
    total += item.price * item.quantity;
  }
  
  res.json({ total });
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `var` in 2024
```javascript
// WRONG: var anywhere in modern code
for (var i = 0; i < 10; i++) { /* ... */ }

// CORRECT: always let for counters
for (let i = 0; i < 10; i++) { /* ... */ }
```

❌ **Mistake 2:** Not using `const` as default
```javascript
// WRONG: using let for everything
let API_URL = "https://api.example.com"; // this never changes
let users = [];                           // reference never changes

// CORRECT: const by default, let only when you need to reassign
const API_URL = "https://api.example.com";
const users = []; // you can still push to this!
```

❌ **Mistake 3:** `const` object = immutable object
```javascript
// WRONG BELIEF:
const settings = { theme: "dark" };
// "settings won't change" — WRONG, properties can change

// CORRECT: const means reference won't change
settings.theme = "light"; // ✅ this works!

// If you need truly immutable: Object.freeze()
const frozen = Object.freeze({ theme: "dark" });
frozen.theme = "light"; // silently fails
```

---

## 🧠 Tricky Interview Output Question
```javascript
// What is the output?
var x = 1;
let y = 1;

if (true) {
  var x = 2;  // same x (var — function scope)
  let y = 2;  // different y (let — block scope)
  console.log(x, y); // ?
}

console.log(x, y); // ?
```
**Answer:**
```
2 2    ← inside block: var x is now 2, block-scoped let y is 2
2 1    ← outside: var x was changed to 2, outer let y is still 1
```
**Why:** `var x = 2` inside the `if` modifies the same `x` as outside (function scope). `let y = 2` inside the `if` creates a NEW `y` (block scope) — outer `y` is untouched.

---

## ⚫ Interview Questions + Answers

**Q1: What are all the differences between var, let, and const?**
A1: (Refer to the comparison table above.) Key points: var is function-scoped and can be re-declared; let and const are block-scoped and cannot be re-declared; const additionally cannot be re-assigned; var hoists to undefined while let/const hoist into TDZ; only var creates a property on the global window object.

**Q2: What is the Temporal Dead Zone?**
A2: TDZ is the phase between entering a block scope and reaching the actual `let`/`const` declaration. During this time, the engine knows the variable exists (it was hoisted) but accessing it throws ReferenceError. It exists to prevent the confusing `undefined` hoisting behavior of `var` — forcing developers to declare before use.

**Q3: Can you change the value of a const array or object?**
A3: Yes, you can mutate the contents — push to arrays, change object properties. What `const` prevents is re-assignment of the binding (pointing the variable to a new value). `const arr = []` → `arr.push(1)` works; `arr = [1]` throws TypeError. For true immutability use `Object.freeze()`.

**Q4: Why does var in a for loop cause issues with async code?**
A4: With `var`, there is one `i` shared across all iterations. By the time the async callback (setTimeout, click handler) executes, the loop has finished and `i` equals the final value. With `let`, each iteration gets a new binding of `i` (a new variable in a new block scope), so each callback captures the correct value.

**Q5: Should you always use const, or is let sometimes better?**
A5: Default to `const`. Use `let` only when you know the variable will be reassigned — loop counters, accumulator variables, flag variables. A common guideline: start with `const`, change to `let` only if you get an assignment error. Never use `var` in modern code.

---

## 🔷 Trade-offs / When to Use
✅ Use `const` by default:
- Module imports, function references
- Object/array containers (even if contents change)
- Configuration values, constants

✅ Use `let` specifically:
- Loop counters (`for`, `while`)
- Variables that change in conditionals or loops
- Accumulator variables (`let total = 0`)

❌ Never use `var`:
- No scoping advantage over let
- Creates confusing bugs
- ESLint `no-var` rule enforces this

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Scope | Where variable can be accessed | Variable कहाँ accessible |
| Block scope | Inside `{}` only | सिर्फ `{}` के अंदर |
| Function scope | Inside entire function | पूरे function में |
| Hoisting | Variable declaration moved to top | Declaration ऊपर जाना |
| TDZ | Can't access before declaration | Declaration से पहले access नहीं |
| Re-declare | Declare same name again | Same नाम से फिर declare करना |
| Re-assign | Change value with `=` | `=` से value बदलना |
| Immutable | Cannot be changed | नहीं बदल सकते |
| Object.freeze | Makes object properties immutable | Object को freeze करना |

---

## ⚡ 3-Line Summary
**English:**
1. `var` = function scope, hoists to undefined, can re-declare — avoid in modern JS.
2. `let` = block scope, TDZ, no re-declare, can re-assign — use for counters and changing values.
3. `const` = block scope, TDZ, no re-declare, no re-assign — use as your default choice.

**Hindi:**
1. `var` = function scope, undefined hoist, redeclare allowed — avoid करो।
2. `let` = block scope, TDZ, redeclare नहीं, reassign हो सकता — counters और changing values के लिए।
3. `const` = block scope, TDZ, redeclare नहीं, reassign नहीं — default choice बनाओ।

---

## ➡️ Next Topic
**05. Data Types** — JavaScript के 7 primitive types (string, number, boolean, null, undefined, symbol, bigint) और उनके behaviors।
