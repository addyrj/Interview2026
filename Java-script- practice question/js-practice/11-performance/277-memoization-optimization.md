---

# Q277. Memoization Optimization
# Category: Performance
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Optimize recursive `fib(n)` from exponential to linear using memoization, and count function calls to prove it.

---

## 💡 Quick Concept (2 lines only)
Memoization caches results by input so repeated calls return instantly instead of recomputing.
हिंदी: Memoization पुराने results को याद रखता है, दोबारा गणना नहीं करता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Count calls in the naive version
// Step 2: Add a cache Map keyed by n
// Step 3: Compare call counts

let naiveCalls = 0;                               // counter for naive
function fibNaive(n) {
  naiveCalls++;                                   // count each call
  return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2); // exponential recursion
}

let memoCalls = 0;                                // counter for memo
function fibMemo(n, cache = new Map()) {
  memoCalls++;                                    // count each call
  if (n < 2) return n;                            // base case
  if (cache.has(n)) return cache.get(n);          // cache hit: O(1)
  const v = fibMemo(n - 1, cache) + fibMemo(n - 2, cache); // compute once
  cache.set(n, v);                                // store result
  return v;                                       // return value
}

// ============================================
// TEST CASES
// ============================================

console.log(fibNaive(20), naiveCalls);            // Expected: 6765 21891
console.log(fibMemo(20), memoCalls);              // Expected: 6765 39
console.log(fibMemo(50));                         // Expected: 12586269025
```

---

## 🔍 Why This Works (3 lines max)
Naive fib recomputes the same subproblems O(2^n) times. With a cache each n is computed once, giving O(n) time at the cost of O(n) memory.
हिंदी: Cache से हर n सिर्फ एक बार compute होता है, इसलिए O(2^n) से O(n) हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// Generic memoize wrapper
const memoize = (fn) => {
  const cache = new Map();                        // key -> result
  return (...args) => {
    const key = JSON.stringify(args);             // simple key from args
    if (!cache.has(key)) cache.set(key, fn(...args)); // compute if missing
    return cache.get(key);                        // return cached
  };
};
const sq = memoize((x) => { console.log('computing'); return x * x; }); // logs only on miss
console.log(sq(4), sq(4));                        // Expected: computing  then  16 16
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: memoizing impure functions (Date.now, random) or unbounded cache growth
// ✅ Correct: memoize pure functions only, bound the cache (LRU) if inputs are unlimited
```

---

## 🎯 Interview Tip (1 line)
State the trade-off: memoization trades memory for speed; mention React's useMemo and bounded caches.

---

## 🔗 Related Questions
→ Q083 (Implement memoize) | Q215 (Memoize async) | Q307 (Memoization use case)
