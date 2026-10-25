# 194. Hoisting Output Questions
# हिंदी में: Hoisting Output Questions — declarations पहले कैसे setup होती हैं

---

## 🔵 Simple Definition (English)
Hoisting means that before any code runs, JavaScript registers `var`, `let`, `const`, `function` and `class` names in their scope. `var` starts as `undefined`, function declarations start with their full body, and `let`/`const` exist but cannot be read until their line runs (the temporal dead zone).

## 🔵 सरल परिभाषा (Hindi)
Hoisting का मतलब है कि कोई भी code चलने से पहले JavaScript अपने scope में `var`, `let`, `const`, `function` और `class` के नाम register कर लेता है। `var` शुरू में `undefined` होता है, function declaration अपनी पूरी body के साथ तैयार होता है, और `let`/`const` मौजूद होते हैं पर उनकी line चलने तक पढ़े नहीं जा सकते (temporal dead zone)।

---

## 🔴 Problem it Solves

**Problem statement:** Predict the output of each `console.log` below, without running the code.

```javascript
console.log(a);            // (1) ?
var a = 1;
console.log(typeof hello); // (2) ?
function hello() {}
console.log(typeof fn);    // (3) ?
var fn = function () {};
try { console.log(b); } catch (e) { console.log(e.name); } // (4) ?
let b = 2;
```

Answers: `undefined`, `function`, `undefined`, `ReferenceError`. Interviewers use this because it tests whether you know the difference between "name exists" and "value is ready". Bugs caused by this are common: a helper called before its `var` assignment, or a `const` used above its declaration, silently or loudly break at runtime.

## 🔴 यह क्यों बना? (Hindi)
पुराने `var` में function-scope और hoisting की वजह से कई अजीब bugs आते थे, जैसे block के अंदर declare हुआ variable बाहर भी `undefined` के रूप में दिखता था। ES2015 में `let` और `const` इसलिए आए ताकि block scope मिले और ready न होने वाली value गलती से न पढ़ी जा सके। इन्हें समझने के लिए hoisting का सही मॉडल ज़रूरी है।

---

## 🟢 How it Works — Step by Step

Step 1 → Engine enters a scope (file, function or block) और सारे declarations पहले scan करता है।
Step 2 → `var` नाम को `undefined` पर set करता है, ताकि उसे पढ़ने पर error न आए।
Step 3 → `function` declaration नाम के साथ पूरा function object पहले से तैयार रखता है।
Step 4 → `let`/`const`/`class` नाम को uninitialized (TDZ) mark करता है, पढ़ने पर ReferenceError।
Step 5 → Code line-by-line चलता है, और declaration की line पर value assign होती है।

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Engine किसी scope (file, function या block) में जाता है और सारे declarations पहले scan करता है।
Step 2 → `var` नाम को `undefined` पर set करता है, ताकि उसे पढ़ने पर error न आए।
Step 3 → `function` declaration नाम के साथ पूरा function object पहले से तैयार रखता है।
Step 4 → `let`/`const`/`class` नाम को uninitialized (TDZ) mark करता है, पढ़ने पर ReferenceError आता है।
Step 5 → Code line-by-line चलता है, और declaration की line पर value assign होती है।

---

## 🟡 Real World Example
Paytm के wallet service में एक helper `calculateCashback` को module के नीचे `const` में लिखा गया। ऊपर वाला function उसे startup पर call करता है, तो TDZ की वजह से ReferenceError आता है और server start नहीं होता। वही helper अगर `function calculateCashback()` declaration होता तो चल जाता, क्योंकि function declarations पूरी तरह hoist होती हैं।

Amazon के checkout code में `var` वाले flag को `if` block के अंदर set किया गया। Block के बाहर वह `undefined` दिखा और order summary गलत बना। `let` से block scope मिलने पर यह bug सामने ही आ जाता।

## 🟡 Real Example Hindi mein
Paytm के wallet service में एक helper `calculateCashback` को module के नीचे `const` में लिखा गया। ऊपर वाला function उसे startup पर call करता है, तो TDZ की वजह से ReferenceError आता है और server start नहीं होता। वही helper अगर `function calculateCashback()` declaration होता तो चल जाता, क्योंकि function declarations पूरी तरह hoist होती हैं।

Amazon के checkout code में `var` वाले flag को `if` block के अंदर set किया गया। Block के बाहर वह `undefined` दिखा और order summary गलत बना। `let` से block scope मिलने पर यह bug सामने ही आ जाता।

---

## 💻 Code Example — Basic
```javascript
// ── Hoisting: var, let/const, function declarations ──

console.log("var before decl:", x);        // x is hoisted as undefined, no error
var x = 10;                                // assignment runs here, at this line
console.log("var after decl:", x);         // 10

try {
  console.log("let before decl:", y);      // y exists but is in the TDZ (uninitialized)
} catch (err) {
  console.log("let TDZ:", err.name);       // ReferenceError
}
let y = 20;                                // y is initialized here
console.log("let after decl:", y);         // 20

console.log(greet("Aditya"));              // function declaration is fully hoisted, works above its line
function greet(name) {                     // full body is available from the start of the scope
  return `Hi ${name}`;                     // template string
}

try {
  notYet();                                // notYet is hoisted as undefined (var), so calling it fails
} catch (err) {
  console.log("arrow via var:", err.name); // TypeError: notYet is not a function
}
var notYet = () => "ok";                   // arrow function is assigned at runtime, not hoisted
```

**Expected output (verified with `node`):**
```
var before decl: undefined
var after decl: 10
let TDZ: ReferenceError
let after decl: 20
Hi Aditya
arrow via var: TypeError
```

## 💻 Code Example — Advanced
```javascript
// A small model of how an engine records scope names at scope entry.
// It shows why var is undefined, function is ready, and let/const are in the TDZ.

const TDZ = Symbol("uninitialized");        // marker: name exists but cannot be read yet

// decls: array of { kind: "var" | "let" | "const" | "function", name, value? }
// Returns a Map (name -> current value). Built in one pass: O(n) time and space.
function createScope(decls) {
  if (!Array.isArray(decls)) throw new TypeError("decls must be an array"); // validate input
  const record = new Map();                 // scope record: name -> value
  for (const d of decls) {                  // single pass over all declarations
    if (typeof d.name !== "string") throw new TypeError("name must be a string"); // validate name
    if (d.kind === "function") {            // function declarations are hoisted with their value
      record.set(d.name, d.value);          // ready immediately
    } else if (d.kind === "var") {          // var is hoisted as undefined
      if (!record.has(d.name)) record.set(d.name, undefined); // do not overwrite an existing name
    } else if (d.kind === "let" || d.kind === "const") { // block-scoped declarations
      if (record.has(d.name)) {             // any second declaration of this name in this scope
        throw new SyntaxError(`Identifier '${d.name}' has already been declared`); // engine rejects it
      }
      record.set(d.name, TDZ);              // exists, but not readable yet
    } else {
      throw new RangeError(`unknown kind: ${d.kind}`); // unsupported declaration kind
    }
  }
  return record;                            // return the scope record
}

// Reading a name follows the engine rules: missing, TDZ, or value.
function read(record, name) {
  if (!record.has(name)) throw new ReferenceError(`${name} is not defined`); // not in scope at all
  const value = record.get(name);           // current value (O(1) lookup)
  if (value === TDZ) {                      // let/const read before its line ran
    throw new ReferenceError(`Cannot access '${name}' before initialization`);
  }
  return value;                             // may be undefined for var
}

// The declaration line itself assigns the value.
function init(record, name, value) {
  record.set(name, value);                  // replace TDZ or undefined with the real value
  return record;                            // return record for chaining
}

// ── Test the model ──
const scope = createScope([
  { kind: "var", name: "a" },               // hoisted as undefined
  { kind: "function", name: "hello", value: () => "hi" }, // hoisted with value
  { kind: "let", name: "b" },               // TDZ until init
]);
console.log(read(scope, "a"));              // undefined
console.log(read(scope, "hello")());        // hi
try { read(scope, "b"); } catch (e) { console.log(e.name); } // ReferenceError
init(scope, "b", 2);                        // the let line runs
console.log(read(scope, "b"));              // 2

// Complexity: createScope O(n) time and space; read and init are O(1) average.
```

**Expected output:**
```
undefined
hi
ReferenceError
2
```

---

## 🟣 Express.js Integration
In Express, a helper that is a function declaration can be called from a route handler above its line, because the whole module scope is hoisted. A helper written as a `const` arrow is only safe to call after its line has run. Calling it during startup, before its line, throws a TDZ error.

```javascript
// npm install express
const express = require("express");                 // import Express
const app = express();                              // create the app

app.get("/price/:amount", (req, res) => {           // handler runs later, after the module is fully set up
  const amount = Number(req.params.amount);         // params are strings, convert to number
  if (!Number.isFinite(amount) || amount < 0) {     // validate before using the value
    return res.status(400).json({ error: "amount must be a positive number" }); // reject
  }
  res.json({ amount, gst: calcGst(amount) });       // calcGst is a hoisted function declaration
});

function calcGst(amount) {                          // hoisted: usable from the route above
  return Math.round(amount * GST_RATE * 100) / 100; // round to paise
}

const GST_RATE = 0.18;                              // const: TDZ until this line runs at startup
// Safe: calcGst runs on requests, long after GST_RATE is initialized.
// Unsafe: calling calcGst(1) at module top, above this line, would throw ReferenceError.

app.listen(3000, () => console.log("listening on 3000")); // start the server
```

**Verified:** `GET /price/100` returns `{"amount":100,"gst":18}`, and `GET /price/-1` returns `400`.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Thinking `let` and `const` are not hoisted.
✅ Correct: They are hoisted into the scope, but they stay in the TDZ until their declaration line runs.

```javascript
// Wrong: expects the value to be undefined, like var
try {
  console.log(total);                       // ReferenceError: TDZ
} catch (e) { console.log("wrong belief:", e.name); }
let total = 5;

// Right: declare before use, or read it only after the line
let total2 = 5;                             // declared first
console.log("right:", total2);              // 5
```

❌ Mistake 2: Thinking a `var` holding a function is hoisted like a function declaration.
✅ Correct: Only the name of `var` is hoisted, as `undefined`. The assignment runs at its line. Function declarations are hoisted with their body.

```javascript
// Wrong: calling a var-assigned function above its line
try {
  sayHi();                                  // TypeError: sayHi is not a function
} catch (e) { console.log("wrong:", e.name); }
var sayHi = function () { return "hi"; };   // assigned only here

// Right: use a function declaration
console.log("right:", sayHi2());            // works above the line
function sayHi2() { return "hi"; }          // fully hoisted
```

**Edge cases (keep in mind):**
- A function declaration inside a block (`if (...) { function f(){} }`) behaves differently in sloppy and strict mode. See the tricky question below.
- `var` inside a `for` loop is function-scoped, so it leaks outside the loop.
- A `class` declaration is hoisted like `let`, so using it before its line throws a ReferenceError.
- Duplicate `let` in the same scope is a SyntaxError at parse time, before any code runs.

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: var inside a function shadows the outer var, and block functions leak in sloppy mode
var x = 1;                                  // module-level x
function outer() {
  console.log(x);                           // (A) ?
  var x = 2;                                // local x, hoisted to the top of outer
  console.log(x);                           // (B) ?
}
outer();

if (true) {                                 // a block
  function inner() { return "block"; }      // function declaration inside a block
}
console.log(typeof inner);                  // (C) ? (sloppy mode, CommonJS file)
```

Answer: `(A) undefined`, `(B) 2`, `(C) function`.
Why: Inside `outer`, the local `var x` is hoisted to the top of the function, so the outer `x = 1` is hidden and the first read gives `undefined`. The second read sees the assignment `2`. For (C), in sloppy mode the engine (Annex B semantics) also creates a `var`-like binding in the enclosing function scope for a function declared inside a block, so `typeof inner` is `"function"` after the block. In strict mode (`"use strict"`), the same code gives `"undefined"`.

---

## ⚫ Interview Questions + Answers

Q1: What is the value of a `var` before its line runs?
A1: `undefined`. The name is hoisted, but no value is assigned until the assignment line runs.

Q2: What is the TDZ?
A2: The temporal dead zone is the time from the start of a scope until the `let`/`const`/`class` declaration line runs. Reading the name in that window throws a ReferenceError.

Q3: Are function declarations hoisted with their body?
A3: Yes. A function declaration is ready from the start of its scope, so it can be called above its line. A function expression or arrow stored in `var` is not.

Q4: Why does `var` inside a `for` loop leak outside?
A4: `var` is function-scoped, not block-scoped. The loop body does not create a new binding, so the variable stays visible after the loop.

Q5: Does hoisting move the code itself?
A5: No. Hoisting is a setup step: the engine records names at scope entry. The code stays in place and runs line by line.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You want helper functions that can be called from above in a module (use function declarations).
- You need to explain why a name is `undefined` or throws a ReferenceError in an interview.
- You are reviewing old code and want to replace `var` with `let` or `const` safely.

❌ Avoid when:
- You rely on `var` hoisting for control flow. Declare and assign at the top of the scope instead.
- You store helper functions in `const` arrows and call them during module startup before their line.
- You use function declarations inside blocks in strict code and expect them to exist outside the block.

---

## 📊 Visual Diagram
```
 Scope entry (before any line runs)
 ┌───────────────────────────────────────────────┐
 │ name        │ state after hoisting             │
 ├───────────────────────────────────────────────┤
 │ a (var)     │ undefined                        │
 │ hello (fn)  │ function (full body ready)       │
 │ b (let)     │ <TDZ: exists, not readable>      │
 └───────────────────────────────────────────────┘
 Line runs:  var a = 1  → a = 1
             let b = 2  → b leaves TDZ, value 2
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Hoisting | Registering declared names at scope entry | Hoisting |
| `var` | Function-scoped, hoisted as `undefined` | var |
| `let` / `const` | Block-scoped, hoisted but in TDZ until initialized | let / const |
| TDZ | Time from scope start to declaration line, reads throw | टेम्पोरल डेड ज़ोन |
| Function declaration | Hoisted with its full body | फ़ंक्शन डिक्लेरेशन |
| Function expression | Stored in a variable, not hoisted with value | फ़ंक्शन एक्सप्रेशन |
| Scope | The region where a name is visible | स्कोप |
| ReferenceError | Error when a name is read in TDZ or does not exist | रेफ़रेंस एरर |

---

## ⚡ 3-Line Summary
English: Before any line runs, the engine records every declared name in its scope.
English: `var` is `undefined`, function declarations are fully ready, and `let`/`const` throw a ReferenceError until their line runs.
English: Use function declarations for hoisted helpers, and declare `let`/`const` before you use them.

Hindi: कोई भी line चलने से पहले engine scope के सारे declared नाम register कर लेता है।
Hindi: `var` `undefined` होता है, function declarations पूरी तरह तैयार होती हैं, और `let`/`const` अपनी line चलने तक ReferenceError देते हैं।
Hindi: Hoisted helpers के लिए function declarations इस्तेमाल करें, और `let`/`const` को इस्तेमाल से पहले declare करें।

---

## ➡️ Next Topic
195. Closure Output Questions — hoisting के बाद closures पढ़ना सही है, क्योंकि closure की ज़्यादातर tricky output questions इस सवाल पर टिकते हैं कि कौन सा variable किस scope में बना और loop या `var` ने उसे कैसे बदला।
