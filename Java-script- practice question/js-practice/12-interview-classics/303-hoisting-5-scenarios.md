---

# Q303. hoisting — 5 scenarios
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 hoisting scenarios: `var`, `let`/`const` (TDZ), function declaration, function expression, and `class`. Predict what each one prints or throws.

---

## 💡 Quick Concept (2 lines only)
Declarations are processed before code runs. `var` becomes `undefined`, function declarations are fully usable, `let`/`const`/`class` exist but are locked in the TDZ.
हिंदी: Code चलने से पहले declarations register हो जाते हैं; `var` = undefined, function पूरा मिलता है, `let/const/class` TDZ में error देते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: var -> hoisted and initialized with undefined
// Step 2: let/const -> hoisted but uninitialized (Temporal Dead Zone)
// Step 3: function declaration -> hoisted with its body
// Step 4: function expression -> only the variable is hoisted (as undefined)
// Step 5: class -> hoisted but in TDZ like let

// Helper: run a function and print either its result or the error name
function attempt(label, fn) {
  try {
    console.log(label, '->', fn());        // print the returned value
  } catch (e) {
    console.log(label, '->', e.name);      // print ReferenceError / TypeError
  }
}

// Scenario 1: var
attempt('1 var', () => { const r = typeof a1; var a1 = 5; return r + ' / ' + a1; }); // reads before assignment

// Scenario 2: let (TDZ)
attempt('2 let', () => { const r = b2; let b2 = 5; return r; }); // read inside TDZ

// Scenario 3: function declaration
attempt('3 declaration', () => { return sayHi(); function sayHi() { return 'hi'; } }); // callable before definition

// Scenario 4: function expression stored in var
attempt('4 expression', () => { const r = typeof greet; var greet = function () {}; return r; }); // only var is hoisted
attempt('4b calling it', () => { greet2(); var greet2 = function () {}; }); // calling undefined

// Scenario 5: class
attempt('5 class', () => { const o = new Box(); class Box {} return o; }); // class is in TDZ

// ============================================
// TEST CASES (Expected output)
// ============================================
// 1 var -> undefined / 5
// 2 let -> ReferenceError
// 3 declaration -> hi
// 4 expression -> undefined
// 4b calling it -> TypeError
// 5 class -> ReferenceError
```

---

## 🔍 Why This Works (3 lines max)
During the creation phase the engine scans declarations. `var` gets `undefined`, functions get their body, and `let/const/class` get no value until their line runs. Touching them early throws `ReferenceError`.
हिंदी: Creation phase में engine सब declarations देख लेता है; `let/const/class` की line आने तक वे इस्तेमाल नहीं हो सकते।

---

## ⚡ Alternative Solution
```javascript
// Same-name priority: function declaration beats var declaration (before assignment)
console.log(typeof dup); // function  (function hoisted over var)
var dup = 1;             // assignment overwrites it afterwards
function dup() {}        // hoisted first
console.log(typeof dup); // number
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming function expressions are hoisted like declarations
// run(); var run = function () {};   // TypeError: run is not a function

// ❌ Wrong: assuming let is NOT hoisted (it is, but in TDZ)
// let x = 'outer'; { console.log(x); let x = 'inner'; } // ReferenceError

// ✅ Correct: declare first, then use
const run2 = () => 'ok';
console.log(run2()); // ok
```

---

## 🎯 Interview Tip (1 line)
Say: "Everything is hoisted; the difference is initialization — var gets undefined, functions get their body, let/const/class stay in the TDZ."

---

## 🔗 Related Questions
→ Q001-Q005 (hoisting outputs) | Q132 (fix hoisting bug) | Q164 (explain hoisting) | Q291 (var vs let vs const)
