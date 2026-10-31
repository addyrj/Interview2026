---

# Q166. Explain call, apply and bind
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain the difference between `call`, `apply` and `bind`. When would you use each?

---

## 💡 Quick Concept (2 lines only)
All three set `this` explicitly. `call(thisArg, a, b)` and `apply(thisArg, [a, b])` invoke immediately; `bind(thisArg, a)` returns a NEW function to call later.
हिंदी: call/apply तुरंत चलाते हैं (args अलग/array में), bind नया function लौटाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Define a function that depends on this
// Step 2: call -> args one by one, runs now
// Step 3: apply -> args as array, runs now
// Step 4: bind -> returns new function, runs later

function intro(greeting, punct) {                // uses this.name
  return `${greeting}, ${this.name}${punct}`;    // build string
}

const person = { name: 'Aditya' };               // object to use as this

console.log(intro.call(person, 'Hello', '!'));   // call: separate args
console.log(intro.apply(person, ['Hi', '?']));   // apply: array args

const boundIntro = intro.bind(person, 'Hey');    // bind: this + first arg preset
console.log(boundIntro('.'));                    // remaining arg supplied later

// Borrowing methods
const nums = [3, 9, 4];                          // plain array
console.log(Math.max.apply(null, nums));         // apply spreads array into args
const arrLike = { 0: 'a', 1: 'b', length: 2 };   // array-like object
console.log(Array.prototype.join.call(arrLike, '-')); // borrow join

// bind cannot be re-bound
const once = intro.bind({ name: 'First' });      // bound to First
console.log(once.call({ name: 'Second' }, 'Yo', '')); // still First

// ============================================
// TEST CASES
// ============================================
// Expected output:
// Hello, Aditya!
// Hi, Aditya?
// Hey, Aditya.
// 9
// a-b
// Yo, First
```

---

## 🔍 Why This Works (3 lines max)
Each sets the `this` value for the function's execution. `bind` stores `this` (and preset args) in a new wrapper function, so it is permanent and cannot be overridden by `call`.
हिंदी: तीनों `this` तय करते हैं; bind उसे हमेशा के लिए नए function में lock कर देता है।

---

## ⚡ Alternative Solution
```javascript
// Modern: spread replaces apply
const arr = [5, 1, 8];                           // numbers
console.log(Math.max(...arr));                   // Expected: 8
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Forgetting bind returns a function, not a result
function f() { return this.v; }
const r = f.bind({ v: 1 });
console.log(r);   // [Function: bound f]

// ✅ Call it
console.log(r()); // 1
```

---

## 🎯 Interview Tip (1 line)
Say: "call = Comma separated, apply = Array, bind = returns new function; bind is used for callbacks and partial application."

---

## 🔗 Related Questions
→ Q023 (call/apply/bind output) | Q107 (implement call) | Q109 (implement bind) | Q124 (this binding bug)
