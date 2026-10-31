---

# Q248. Symbol — 3 Use Cases
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 3 real use cases of `Symbol`: collision-free keys, hidden properties, and well-known symbols (`Symbol.iterator`).

---

## 💡 Quick Concept (2 lines only)
A Symbol is a unique, immutable primitive often used as a property key that can never collide with other keys.
हिंदी: Symbol हमेशा unique होता है, इसलिए property key के तौर पर collision नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Unique symbols are never equal
// Step 2: Use as hidden object keys
// Step 3: Customize behaviour with well-known symbols

// Use case 1: Collision-free keys / enum-like constants
const RED = Symbol('red');                       // unique value with description
const RED2 = Symbol('red');                      // same description, different symbol
console.log(RED === RED2, RED.description);      // Expected: false red

// Use case 2: Hidden (non-enumerable-ish) property
const id = Symbol('id');                         // private-style key
const user = { name: 'Ria', [id]: 101 };         // computed symbol key
console.log(Object.keys(user));                  // Expected: [ 'name' ]
console.log(JSON.stringify(user));               // Expected: {"name":"Ria"}
console.log(user[id]);                           // Expected: 101

// Use case 3: Symbol.iterator makes an object iterable
const range = {
  from: 1, to: 3,                                // bounds
  [Symbol.iterator]() {                          // iterator factory
    let cur = this.from, end = this.to;          // state
    return { next: () => cur <= end ? { value: cur++, done: false } : { value: undefined, done: true } };
  },
};
console.log([...range]);                         // Expected: [ 1, 2, 3 ]

// ============================================
// TEST CASES
// ============================================

console.log(Symbol.for('app') === Symbol.for('app')); // Expected: true
console.log(Object.getOwnPropertySymbols(user).length); // Expected: 1
console.log(typeof Symbol());                    // Expected: symbol
console.log(String(RED));                        // Expected: Symbol(red)
```

---

## 🔍 Why This Works (3 lines max)
Every `Symbol()` call returns a new unique value, and symbol keys are skipped by `Object.keys`, `for...in` and `JSON.stringify`. `Symbol.for` uses a global registry for shared symbols.
हिंदी: Symbol keys `Object.keys` और JSON में नहीं दिखतीं, पर `getOwnPropertySymbols` से मिल जाती हैं।

---

## ⚡ Alternative Solution
```javascript
// Customize string conversion with Symbol.toPrimitive
const money = {
  amount: 50,
  [Symbol.toPrimitive](hint) { return hint === 'number' ? this.amount : `$${this.amount}`; },
};
console.log(+money, `${money}`);                 // Expected: 50 $50
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using new with Symbol
// const s = new Symbol('x');   // TypeError: Symbol is not a constructor

// ✅ Correct: call it as a function
const s = Symbol('x');                           // valid
console.log(s.toString());                       // Expected: Symbol(x)
```

---

## 🎯 Interview Tip (1 line)
Say: "Symbols avoid key collisions and power protocols like `Symbol.iterator` — but they are not truly private."

---

## 🔗 Related Questions
→ Q045 (Symbol output) | Q171 (Symbol use case) | Q174 (iterators) | Q253 (generators)
