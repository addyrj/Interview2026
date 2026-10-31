---

# Q164. Explain Hoisting with Example
# Category: Tricky Concepts
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain hoisting in JavaScript. How do `var`, `let`, `const`, function declarations, function expressions and classes behave before their declaration line?

---

## 💡 Quick Concept (2 lines only)
Before running, JS allocates memory for declarations in the scope. `var` is set to `undefined`, functions are fully available, `let`/`const`/`class` exist but stay in the Temporal Dead Zone.
हिंदी: Hoisting में declarations scope के ऊपर चली जाती हैं — var = undefined, function पूरा, let/const = TDZ error।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: var -> hoisted, initialised to undefined
// Step 2: function declaration -> hoisted with body
// Step 3: let/const/class -> hoisted but in TDZ (ReferenceError)

console.log(a);                    // var is hoisted -> undefined
var a = 10;                        // assignment happens here, not earlier

console.log(sayHi());              // function declaration fully hoisted
function sayHi() { return 'hi'; }  // body available before this line

try {
  console.log(b);                  // let is in TDZ
} catch (e) {
  console.log(e.name);             // ReferenceError
}
let b = 5;                         // TDZ ends here

try {
  fnExpr();                        // var fnExpr is undefined, not a function
} catch (e) {
  console.log(e.name);             // TypeError
}
var fnExpr = function () {};       // function expression is NOT hoisted with body

try {
  new Foo();                       // class is in TDZ like let
} catch (e) {
  console.log(e.name);             // ReferenceError
}
class Foo {}                       // class declaration

// ============================================
// TEST CASES
// ============================================

// Expected output (in order):
// undefined
// hi
// ReferenceError
// TypeError
// ReferenceError
```

---

## 🔍 Why This Works (3 lines max)
During the creation phase of an execution context, JS registers all declarations. `var` gets `undefined`, function declarations get their body, `let`/`const`/`class` stay uninitialised until their line runs.
हिंदी: Execution शुरू होने से पहले declarations register हो जाती हैं, पर let/const अपनी line तक use नहीं हो सकते।

---

## ⚡ Alternative Solution
```javascript
// What the engine effectively sees:
var x;                             // declaration moved up
console.log(x);                    // Expected: undefined
x = 7;                             // assignment stays in place
console.log(x);                    // Expected: 7
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Believing "hoisting moves code to the top" and let is not hoisted
let v = 'outer';
function test() {
  // console.log(v);  // ReferenceError! inner let v is hoisted (TDZ) and shadows outer
  let v = 'inner';
  return v;
}
console.log(test()); // inner

// ✅ Declare variables at the top of scope and prefer const/let
```

---

## 🎯 Interview Tip (1 line)
Say: "Everything is hoisted; the difference is initialisation — var gets undefined, let/const stay in TDZ."

---

## 🔗 Related Questions
→ Q001 (var hoisting) | Q002 (let TDZ) | Q132 (hoisting bug) | Q303 (hoisting 5 scenarios)
