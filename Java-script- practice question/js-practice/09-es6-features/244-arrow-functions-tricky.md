---

# Q244. Arrow Functions — Tricky
# Category: ES6+ Features
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Predict the output of these tricky arrow function cases: `this` in methods, returning object literals, `arguments`, `new`, and `this` inside timers.

---

## 💡 Quick Concept (2 lines only)
Arrow functions have no own `this`, `arguments`, `prototype`, and cannot be used with `new`; they capture `this` lexically.
हिंदी: Arrow function का अपना `this` नहीं होता, वो आसपास के scope से `this` लेता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: this in object method (arrow vs regular)
// Step 2: implicit return of object literal
// Step 3: arguments / new / timers

// 1. Arrow as object method -> this is NOT the object
const obj = {
  name: 'Ria',                                   // property
  arrow: () => typeof this,                      // this = module.exports in Node
  regular() { return this.name; },               // this = obj
};
console.log(obj.regular());                      // Expected: Ria
console.log(obj.arrow());                        // Expected: object

// 2. Returning object literal needs parentheses
const bad = () => { id: 1 };                     // braces = function body, label `id`
const good = () => ({ id: 1 });                  // parentheses = object literal
console.log(bad(), good());                      // Expected: undefined { id: 1 }

// 3. No own arguments object (uses outer one)
function outer() {
  const inner = () => arguments[0];              // arrow reads outer's arguments
  return inner(99);                              // 99 ignored, outer arg used
}
console.log(outer(5));                           // Expected: 5

// 4. Arrow cannot be a constructor
const Arrow = () => {};                          // arrow function
try { new Arrow(); } catch (e) { console.log(e.constructor.name); } // Expected: TypeError
console.log(Arrow.prototype);                    // Expected: undefined

// 5. Arrow keeps this inside setTimeout (lexical)
const timer = {
  v: 42,                                         // data
  run() { setTimeout(() => console.log(this.v), 0); }, // arrow uses run's this
};
timer.run();                                     // Expected: 42  (printed last, async)

// ============================================
// TEST CASES
// ============================================

console.log((() => {}).name === '');             // Expected: true
const fn = () => 1;                              // name inferred from variable
console.log(fn.name);                            // Expected: fn
console.log(typeof (() => {}).call);             // Expected: function
```

---

## 🔍 Why This Works (3 lines max)
Arrows resolve `this` and `arguments` from the enclosing scope at definition time, so `call/apply/bind` cannot change them. `{` after `=>` starts a function body, not an object.
हिंदी: Arrow में `this` define होते समय fix हो जाता है, `bind` भी उसे नहीं बदल सकता।

---

## ⚡ Alternative Solution
```javascript
// Fix object-method this with shorthand method
const counter = {
  n: 0,
  inc() { return ++this.n; },                    // regular method: this = counter
};
console.log(counter.inc(), counter.inc());       // Expected: 1 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: arrow as prototype/event method needing own this
// Person.prototype.hi = () => this.name;   // this is NOT the instance

// ✅ Correct: use a regular function
function Person(n) { this.name = n; }            // constructor
Person.prototype.hi = function () { return this.name; }; // regular function
console.log(new Person('Aman').hi());            // Expected: Aman
```

---

## 🎯 Interview Tip (1 line)
Say: "Use arrows for callbacks that need outer `this`; use regular functions for methods, constructors and prototypes."

---

## 🔗 Related Questions
→ Q019 (this in arrow) | Q124 (fix this binding) | Q298 (arrow vs regular) | Q165 (this 5 examples)
