---

# Q044. Generator Output
# Category: Output Questions
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What will the following code print?

```javascript
function* gen() {
  const x = yield 1;
  console.log('x =', x);
  const y = yield x * 2;
  return x + y;
}
const g = gen();
console.log(g.next('ignored'));
console.log(g.next(10));
console.log(g.next(5));
console.log(g.next());
```

---

## 💡 Quick Concept (2 lines only)
A generator pauses at each `yield`; `next(v)` resumes it and makes the paused `yield` evaluate to `v`. The first `next()` argument is ignored.
हिंदी: Generator हर yield पर रुकता है; next(v) उसे आगे बढ़ाता है और v को yield की value बना देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: first next() runs to `yield 1` (argument ignored)
// Step 2: next(10) -> x = 10, logs, runs to `yield 20`
// Step 3: next(5) -> y = 5, returns 15 and finishes
// Step 4: next() after finish -> { value: undefined, done: true }

function* gen() {                   // generator function
  const x = yield 1;                // pause, later receives value
  console.log('x =', x);            // runs after 2nd next()
  const y = yield x * 2;            // pause with 20
  return x + y;                     // final return value
}
const g = gen();                    // creates iterator, runs nothing yet
console.log(g.next('ignored'));     // { value: 1, done: false }
console.log(g.next(10));            // logs "x = 10" then { value: 20, done: false }
console.log(g.next(5));             // { value: 15, done: true }
console.log(g.next());              // { value: undefined, done: true }

// ============================================
// TEST CASES
// ============================================

function* count() { yield 1; yield 2; yield 3; }  // simple generator
console.log([...count()]);                        // Expected: [ 1, 2, 3 ]
const it = count();                               // new iterator
it.next();                                        // consume 1
console.log(it.return(99));                       // Expected: { value: 99, done: true }

// ============================================
// OUTPUT:
// ============================================
// { value: 1, done: false }
// x = 10
// { value: 20, done: false }
// { value: 15, done: true }
// { value: undefined, done: true }
// [ 1, 2, 3 ]
// { value: 99, done: true }
```

---

## 🔍 Why This Works (3 lines max)
Calling a generator returns an iterator without running the body. Each `next(v)` resumes from the last `yield`, which evaluates to `v`. `return` marks done: true.
हिंदी: Generator call करने पर body नहीं चलती; हर next() अगले yield तक चलाता है।

---

## ⚡ Alternative Solution
```javascript
// Generators are iterable: use for...of (return value is ignored)
function* range(a, b) { for (let i = a; i <= b; i++) yield i; } // lazy range
for (const n of range(1, 3)) console.log(n);                    // 1 2 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting code to run on call
function* g() { console.log('started'); yield 1; }
const it = g();            // prints nothing yet

// ✅ Correct: body starts on first next()
it.next();                 // started
```

---

## 🎯 Interview Tip (1 line)
Say: "Generators are lazy, pausable functions; next(v) sends a value in and the first next() argument is discarded."

---

## 🔗 Related Questions
→ Q045 (Symbol output) | Q169 (explain generators) | Q253 (generator examples)
