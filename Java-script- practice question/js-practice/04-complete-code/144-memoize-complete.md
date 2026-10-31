---

# Q144. Complete Memoize Function
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks to cache results by arguments.

```javascript
function memoize(fn) {
  const cache = new ____();               // storage
  return function (...args) {
    const key = JSON.____(args);          // build cache key
    if (cache.____(key)) return cache.get(key); // hit
    const result = fn.apply(this, ____);  // compute
    cache.____(key, result);              // save
    return result;
  };
}
```

---

## 💡 Quick Concept (2 lines only)
Memoization stores results per input so repeated calls return instantly without recomputing.
हिंदी: Memoization पुराने results याद रखता है ताकि वही calculation दोबारा न करनी पड़े।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function memoize(fn) {
  const cache = new Map();                      // blank 1: Map as store
  return function (...args) {
    const key = JSON.stringify(args);           // blank 2: args -> string key
    if (cache.has(key)) return cache.get(key);  // blank 3: return cached value
    const result = fn.apply(this, args);        // blank 4: compute on miss
    cache.set(key, result);                     // blank 5: store result
    return result;                              // return value
  };
}

// ============================================
// TEST CASES
// ============================================

let calls = 0;                                  // count real computations
const slowSquare = memoize((n) => { calls++; return n * n; }); // memoized fn
console.log(slowSquare(4));                     // Expected: 16
console.log(slowSquare(4));                     // Expected: 16 (cached)
console.log(calls);                             // Expected: 1
```

---

## 🔍 Why This Works (3 lines max)
The closure keeps one Map across calls. The first call computes and stores; same arguments later hit the cache.
हिंदी: closure में Map बचा रहता है, इसलिए समान arguments पर cached result मिलता है।

---

## ⚡ Alternative Solution
```javascript
// Single-argument memoize (faster, no JSON)
const memo1 = (fn, c = new Map()) => (x) => c.has(x) ? c.get(x) : (c.set(x, fn(x)), c.get(x));
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: `if (cache[key])` fails when the result is 0 or false
// ✅ Correct: cache.has(key)
```

---

## 🎯 Interview Tip (1 line)
Say: "Memoize only pure functions; consider cache size limits (LRU) and unserializable arguments."

---

## 🔗 Related Questions
→ Q083 (implement memoize) | Q277 (memoization optimization) | Q307 (memoization use case) | Q152 (complete LRU)
