---

# Q298. arrow vs regular function
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
List the key differences between arrow functions and regular functions: `this`, `new`, `prototype`, and use as object methods. Prove each with code.

---

## 💡 Quick Concept (2 lines only)
Arrow functions have no own `this`, `arguments`, `prototype` and cannot be used with `new`; they inherit `this` from where they are written.
हिंदी: Arrow function का अपना `this` नहीं होता, वह आसपास (lexical) से लेता है; `new` भी नहीं चलता।

---

## ✅ Answer / Solution

```javascript
'use strict'; // strict mode so a lost `this` is undefined (not the global object)

// ============================================
// SOLUTION
// ============================================

// Step 1: regular function -> `this` depends on HOW it is called
// Step 2: arrow function -> `this` is fixed by WHERE it is defined
// Step 3: arrows cannot be constructors and have no prototype

const team = {
  name: 'Alpha',                                   // data used through `this`
  regularMethod() { return this.name; },           // good: this = team when called as team.x()
  arrowMethod: () => typeof this,                  // bad: this is the outer (module) scope, not team
  listRegular() {
    // callback is a regular function -> loses this in strict mode
    return ['x'].map(function () { return typeof this; }); // this is undefined here
  },
  listArrow() {
    // callback is an arrow -> keeps this from listArrow (the team object)
    return ['x'].map(() => this.name);             // this = team
  },
};

function RegularFn() {}                            // regular function
const arrowFn = () => {};                          // arrow function

// ============================================
// TEST CASES
// ============================================

console.log(team.regularMethod());                 // Expected: Alpha
console.log(team.arrowMethod());                   // Expected: object  (module.exports, NOT team)
console.log(team.listRegular());                   // Expected: [ 'undefined' ]
console.log(team.listArrow());                     // Expected: [ 'Alpha' ]
console.log(typeof RegularFn.prototype);           // Expected: object
console.log(arrowFn.prototype);                    // Expected: undefined
try { new arrowFn(); } catch (e) { console.log(e instanceof TypeError); } // Expected: true
console.log((function () { return arguments.length; })(1, 2, 3)); // Expected: 3
console.log(((...args) => args.length)(1, 2, 3));  // Expected: 3 (use rest instead of arguments)
```

---

## 🔍 Why This Works (3 lines max)
A regular function gets a fresh `this` per call (decided by the caller). An arrow captures `this` once from its surrounding scope, which is great for callbacks but wrong for object methods and constructors.
हिंदी: Regular function में `this` call करने के तरीके से तय होता है; arrow में लिखने की जगह से।

---

## ⚡ Alternative Solution
```javascript
// Fixing lost `this` in a regular callback without arrow: bind
const timer = {
  label: 'T1',
  start() {
    return ['a'].map(function () { return this.label; }.bind(this)); // bind sets this = timer
  },
};
console.log(timer.start()); // [ 'T1' ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: arrow as object method / event handler needing its own this
const counter = { count: 0, inc: () => { this.count++; } }; // `this` is NOT counter

// ❌ Wrong: arrow as constructor
// const User = (n) => { this.n = n; }; new User('a'); // TypeError

// ✅ Correct: shorthand method for objects, arrow for inner callbacks
const counter2 = { count: 0, inc() { this.count++; return this.count; } };
console.log(counter2.inc()); // 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Arrows for callbacks (lexical `this`), regular functions for methods and constructors — arrows have no `this`, `arguments`, `prototype`, or `new`."

---

## 🔗 Related Questions
→ Q018 (this regular) | Q019 (this arrow) | Q124 (fix this binding) | Q244 (arrow functions tricky)
