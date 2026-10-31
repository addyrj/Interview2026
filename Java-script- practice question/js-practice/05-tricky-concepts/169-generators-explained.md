---

# Q169. Explain Generators
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is a generator function? Show `yield`, passing values into a generator with `next(value)`, infinite sequences and `yield*`.

---

## 💡 Quick Concept (2 lines only)
A generator (`function*`) can pause at `yield` and resume later, returning an iterator. Each `next()` runs until the next `yield`.
हिंदी: Generator बीच में रुक (yield) सकता है और बाद में वहीं से फिर चल सकता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: function* returns an iterator, nothing runs yet
// Step 2: next() runs until yield and returns { value, done }
// Step 3: next(x) makes the paused yield evaluate to x

function* simple() {                       // generator function
  yield 1;                                 // pause 1
  yield 2;                                 // pause 2
  return 3;                                // final value (done: true)
}
const g = simple();                        // no code executed yet
console.log(g.next());                     // { value: 1, done: false }
console.log(g.next());                     // { value: 2, done: false }
console.log(g.next());                     // { value: 3, done: true }
console.log(g.next());                     // { value: undefined, done: true }

// Two-way communication
function* chat() {
  const name = yield 'Name?';              // pause, receive value
  const age = yield `Hi ${name}, age?`;    // pause again
  return `${name} is ${age}`;              // final result
}
const c = chat();                          // create iterator
console.log(c.next().value);               // Name?
console.log(c.next('Aditya').value);       // Hi Aditya, age?
console.log(c.next(25).value);             // Aditya is 25

// Infinite lazy sequence
function* ids() {
  let i = 1;                               // state kept between pauses
  while (true) yield i++;                  // never ends, but lazy
}
const it = ids();                          // create iterator
console.log(it.next().value, it.next().value, it.next().value); // 1 2 3

// Delegation and spread
function* inner() { yield 'a'; yield 'b'; } // inner generator
function* outer() { yield* inner(); yield 'c'; } // yield* delegates
console.log([...outer()]);                 // [ 'a', 'b', 'c' ]

// ============================================
// TEST CASES
// ============================================
// Expected output:
// { value: 1, done: false }
// { value: 2, done: false }
// { value: 3, done: true }
// { value: undefined, done: true }
// Name?
// Hi Aditya, age?
// Aditya is 25
// 1 2 3
// [ 'a', 'b', 'c' ]
```

---

## 🔍 Why This Works (3 lines max)
The engine saves the function's execution state at each `yield`. `next(v)` restores it and injects `v` as the result of the paused `yield`. Values are produced on demand (lazy).
हिंदी: Engine हर yield पर state save करता है, next() उसे वापस चालू करता है, और values ज़रूरत पर बनती हैं।

---

## ⚡ Alternative Solution
```javascript
// Generators make objects iterable easily
const range = {
  from: 1, to: 4,                          // bounds
  *[Symbol.iterator]() {                   // generator as iterator
    for (let i = this.from; i <= this.to; i++) yield i; // emit each number
  }
};
console.log([...range]);                   // Expected: [ 1, 2, 3, 4 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Expecting return value inside for...of / spread
function* f() { yield 1; return 2; }
console.log([...f]);   // TypeError: f is not iterable (forgot to call f())
console.log([...f()]); // [ 1 ]  -> return value 2 is ignored

// ✅ Use yield for values you want iterated
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators are pausable functions returning iterators; they power lazy sequences, custom iteration and were the base for async/await."

---

## 🔗 Related Questions
→ Q044 (generator output) | Q149 (complete generator) | Q174 (iterators) | Q253 (generator 5 examples)
