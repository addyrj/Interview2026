---

# Q171. Explain Symbol Use Case
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a Symbol and what problems does it solve? Show unique keys, hidden properties and well-known symbols.

---

## 💡 Quick Concept (2 lines only)
A Symbol is a unique, immutable primitive often used as an object key that can never collide with other keys. Symbol keys are skipped by `for...in`, `Object.keys` and `JSON.stringify`.
हिंदी: Symbol हमेशा unique होता है, इसलिए property नाम टकराते नहीं और key आम loops में नहीं दिखती।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Every Symbol() call creates a unique value
// Step 2: Use as object key to avoid name collision / hide metadata
// Step 3: Well-known symbols customise language behaviour

console.log(Symbol('id') === Symbol('id'));  // false -> always unique
console.log(Symbol.for('app') === Symbol.for('app')); // true -> global registry

// Use case 1: collision-free / hidden property
const ID = Symbol('id');                     // unique key
const user = { name: 'Aditya', [ID]: 101 }; // symbol as computed key
console.log(Object.keys(user));              // [ 'name' ]
console.log(JSON.stringify(user));           // {"name":"Aditya"}
console.log(user[ID]);                       // 101
console.log(Object.getOwnPropertySymbols(user).length); // 1

// Use case 2: constants that cannot be confused
const RED = Symbol('red');                   // enum-like value
const BLUE = Symbol('blue');                 // another value
console.log(RED === BLUE);                   // false
console.log(RED.toString());                 // Symbol(red)
console.log(RED.description);                // red

// Use case 3: well-known symbol - make object iterable
const team = {
  members: ['A', 'B'],                       // data
  [Symbol.iterator]() {                      // custom iteration
    let i = 0;                               // index state
    const m = this.members;                  // capture list
    return { next: () => i < m.length ? { value: m[i++], done: false } : { value: undefined, done: true } };
  }
};
console.log([...team]);                      // [ 'A', 'B' ]

// Use case 4: customise primitive conversion
const money = { [Symbol.toPrimitive]: hint => hint === 'number' ? 100 : '$100' };
console.log(+money, `${money}`);             // 100 $100

// ============================================
// TEST CASES
// ============================================
// Expected output:
// false
// true
// [ 'name' ]
// {"name":"Aditya"}
// 101
// 1
// false
// Symbol(red)
// red
// [ 'A', 'B' ]
// 100 $100
```

---

## 🔍 Why This Works (3 lines max)
Symbols are compared by identity, not by description, so two libraries can add keys to one object safely. Enumeration APIs ignore symbol keys, making them good for metadata.
हिंदी: Symbol identity से compare होता है, इसलिए दो libraries की keys कभी नहीं टकरातीं।

---

## ⚡ Alternative Solution
```javascript
// Private-ish state without symbols: WeakMap or #private fields
class A { #secret = 1; get() { return this.#secret; } } // true privacy
console.log(new A().get());                  // Expected: 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Thinking symbol keys are truly private
const S = Symbol('s'); const o = { [S]: 1 };
console.log(Object.getOwnPropertySymbols(o)); // [ Symbol(s) ] -> still discoverable

// ✅ Use #private fields or WeakMap for real privacy
```

---

## 🎯 Interview Tip (1 line)
Say: "Symbols give unique, non-enumerable keys and power protocols like Symbol.iterator and Symbol.toPrimitive; they are hidden, not private."

---

## 🔗 Related Questions
→ Q045 (Symbol output) | Q174 (iterators) | Q248 (Symbol 3 use cases) | Q170 (WeakMap use case)
