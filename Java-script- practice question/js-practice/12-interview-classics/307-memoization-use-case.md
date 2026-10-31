---

# Q307. memoization real use case
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is memoization? Implement a generic `memoize` helper and show a real use case: caching an expensive pure function and speeding up recursive Fibonacci from exponential to linear time.

---

## 💡 Quick Concept (2 lines only)
Memoization caches a function's result per input, so repeated calls with the same arguments return instantly. It only works safely for pure functions.
हिंदी: Memoization में हर input का result याद रखा जाता है, ताकि वही call दोबारा आने पर तुरंत जवाब मिले।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: keep a cache (Map) in a closure
// Step 2: build a key from the arguments
// Step 3: if key exists return cached result, else compute, store, return

function memoize(fn) {
  const cache = new Map();                    // private cache: key -> result
  return function (...args) {
    const key = JSON.stringify(args);         // turn arguments into a string key
    if (cache.has(key)) {                     // cache hit?
      return cache.get(key);                  // return stored result, skip computation
    }
    const result = fn.apply(this, args);      // cache miss -> compute
    cache.set(key, result);                   // store for next time
    return result;                            // return fresh result
  };
}

// Use case 1: expensive function, count how often the real work happens
let computeCount = 0;                         // counts real computations
const slowSquare = memoize((n) => {
  computeCount++;                             // increments only on cache miss
  return n * n;                               // pretend this is expensive
});

// Use case 2: recursive Fibonacci (recursion calls the MEMOIZED version)
const fib = memoize((n) => (n < 2 ? n : fib(n - 1) + fib(n - 2))); // each n computed once

// ============================================
// TEST CASES
// ============================================

console.log(slowSquare(4));                   // Expected: 16
console.log(slowSquare(4));                   // Expected: 16 (from cache)
console.log(slowSquare(5));                   // Expected: 25
console.log(computeCount);                    // Expected: 2 (4 computed once, 5 once)
console.log(fib(10));                         // Expected: 55
console.log(fib(50));                         // Expected: 12586269025 (instant; naive would take minutes)
```

---

## 🔍 Why This Works (3 lines max)
The cache lives in a closure, so it survives between calls. Fibonacci recomputes the same subproblems exponentially; with a cache each `n` is computed once, giving O(n).
हिंदी: Cache closure में रहता है इसलिए calls के बीच बचा रहता है; Fibonacci में हर n सिर्फ़ एक बार compute होता है।

---

## ⚡ Alternative Solution
```javascript
// Single-argument memoize using an object key map (faster, no JSON.stringify)
const memo1 = (fn, cache = {}) => (x) => (x in cache ? cache[x] : (cache[x] = fn(x))); // check, else compute+store
const triple = memo1((x) => x * 3);   // memoized triple
console.log(triple(3), triple(3));    // 9 9

// Use WeakMap when keys are objects so cache entries can be garbage collected
const objCache = new WeakMap();       // key must be an object
const sizeOf = (o) => objCache.get(o) ?? (objCache.set(o, Object.keys(o).length), objCache.get(o)); // compute once
console.log(sizeOf({ a: 1, b: 2 })); // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: memoizing impure functions (result depends on time/random/global state)
const now = memoize(() => Date.now());   // always returns the first timestamp

// ❌ Wrong: recursion calls the un-memoized function, so no speedup
// function fibSlow(n) { return n < 2 ? n : fibSlow(n-1) + fibSlow(n-2); }
// const fastWrong = memoize(fibSlow);   // inner calls still go to fibSlow

// ✅ Correct: memoize pure functions and make recursion call the memoized name
```

---

## 🎯 Interview Tip (1 line)
Say: "Memoization trades memory for speed by caching pure-function results in a closure — I'd add a size limit or TTL for real apps."

---

## 🔗 Related Questions
→ Q083 (implement memoize) | Q144 (complete memoize) | Q215 (memoize async) | Q277 (memoization optimization)
