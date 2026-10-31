---

# Q174. Explain Iterators
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Explain the iterator and iterable protocols. How does `for...of` work, and how do you make a custom object iterable?

---

## 💡 Quick Concept (2 lines only)
An iterable has a `[Symbol.iterator]()` method returning an iterator; an iterator has `next()` returning `{ value, done }`. `for...of`, spread and destructuring use this protocol.
हिंदी: Iterable में `[Symbol.iterator]()` होता है जो ऐसा iterator देता है जिसका `next()` {value, done} लौटाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Get iterator by calling obj[Symbol.iterator]()
// Step 2: Call next() repeatedly until done is true
// Step 3: for...of / spread / destructuring automate this

const arr = ['a', 'b'];                       // arrays are iterable
const it = arr[Symbol.iterator]();            // manually get iterator
console.log(it.next());                       // { value: 'a', done: false }
console.log(it.next());                       // { value: 'b', done: false }
console.log(it.next());                       // { value: undefined, done: true }

// Custom iterable: countdown
const countdown = {
  from: 3,                                    // start value
  [Symbol.iterator]() {                       // makes object iterable
    let n = this.from;                        // private counter
    return {
      next() {                                // iterator method
        return n > 0
          ? { value: n--, done: false }       // emit and decrement
          : { value: undefined, done: true }; // finished
      }
    };
  }
};
console.log([...countdown]);                  // [ 3, 2, 1 ]
for (const x of countdown) console.log(x);    // 3 then 2 then 1
const [first, ...rest] = countdown;           // destructuring uses iterator
console.log(first, rest);                     // 3 [ 2, 1 ]

// Built-ins that are iterable
console.log([...'hi']);                       // [ 'h', 'i' ] (string)
console.log([...new Set([1, 1, 2])]);         // [ 1, 2 ] (Set)
console.log([...new Map([['k', 1]])]);        // [ [ 'k', 1 ] ] (Map)

// Plain objects are NOT iterable
try { [...{ a: 1 }]; } catch (e) { console.log(e.name); } // TypeError

// ============================================
// TEST CASES
// ============================================
// Expected output:
// { value: 'a', done: false }
// { value: 'b', done: false }
// { value: undefined, done: true }
// [ 3, 2, 1 ]
// 3
// 2
// 1
// 3 [ 2, 1 ]
// [ 'h', 'i' ]
// [ 1, 2 ]
// [ [ 'k', 1 ] ]
// TypeError
```

---

## 🔍 Why This Works (3 lines max)
`for...of` calls `[Symbol.iterator]()` once, then `next()` until `done: true`. Anything implementing this contract (arrays, strings, Maps, Sets, custom objects) works with spread and destructuring.
हिंदी: for...of पहले iterator लेता है, फिर done: true आने तक next() बुलाता रहता है।

---

## ⚡ Alternative Solution
```javascript
// Generator makes custom iterables shorter
const countdown2 = {
  from: 3,                                    // start
  *[Symbol.iterator]() {                      // generator method
    for (let n = this.from; n > 0; n--) yield n; // emit values
  }
};
console.log([...countdown2]);                 // Expected: [ 3, 2, 1 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ for...of on a plain object
// for (const v of { a: 1 }) {}   // TypeError: not iterable

// ✅ Iterate its entries (arrays are iterable)
for (const [k, v] of Object.entries({ a: 1 })) console.log(k, v); // a 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Iterable = has Symbol.iterator; iterator = has next() returning {value, done}; generators create iterators for free."

---

## 🔗 Related Questions
→ Q169 (generators) | Q171 (Symbol use case) | Q268 (iterator pattern) | Q253 (generator examples)
