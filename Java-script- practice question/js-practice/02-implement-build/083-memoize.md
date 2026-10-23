---

# Q083. Implement Memoize
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a `memoize(fn)` function that caches the results of function calls. If the function is called again with the same arguments, return the cached result instead of re-computing.

```javascript
const memoFib = memoize(fibonacci);
memoFib(40);  // computes — slow
memoFib(40);  // returns from cache — instant
```

---

## 💡 Quick Concept (2 lines only)
Memoize caches function return values by their arguments. Same args = return cached result, skip computation. Classic performance optimization for pure/expensive functions.
हिंदी: Memoize result cache करता है — same arguments पर cache से return, function फिर से run नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function memoize(fn) {
  const cache = new Map();  // Step 1: cache to store results
  
  return function(...args) {
    const key = JSON.stringify(args);  // Step 2: create cache key from arguments
    
    if (cache.has(key)) {              // Step 3: cache hit?
      return cache.get(key);           // Step 4: return cached value
    }
    
    const result = fn.apply(this, args);  // Step 5: compute result
    cache.set(key, result);               // Step 6: store in cache
    return result;                        // Step 7: return result
  };
}

// ============================================
// TEST CASES
// ============================================

// Expensive function:
function slowSquare(n) {
  // Simulate slow computation
  let result = 0;
  for (let i = 0; i < n * 1000000; i++) result++;
  return result;
}

const memoSquare = memoize(slowSquare);

console.time('first call');
console.log(memoSquare(10));   // Computes — slow
console.timeEnd('first call'); // Expected: slow (~ms)

console.time('second call');
console.log(memoSquare(10));   // Cache hit — instant
console.timeEnd('second call'); // Expected: ~0ms

// Fibonacci memoization:
const memoFib = memoize(function fib(n) {
  if (n <= 1) return n;
  return memoFib(n - 1) + memoFib(n - 2);  // recursive calls benefit from cache
});

console.log(memoFib(40));  // Expected: 102334155 (fast with memoization)
```

---

## 🔍 Why This Works (3 lines max)
Cache maps argument keys to return values. `JSON.stringify(args)` creates a string key from any arguments. On repeat calls with same args, skip computation entirely and return stored value.
हिंदी: Cache में args का key और result store होता है — same args पर cache से return, computation skip।

---

## ⚡ Alternative Solution
```javascript
// Using object as cache (faster for primitive args):
function memoizeSimple(fn) {
  const cache = {};
  return function(...args) {
    const key = args.join(',');
    if (key in cache) return cache[key];
    return (cache[key] = fn.apply(this, args));
  };
}

// Memoize with max cache size (LRU-like):
function memoizeWithLimit(fn, maxSize = 100) {
  const cache = new Map();
  return function(...args) {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = fn.apply(this, args);
    if (cache.size >= maxSize) {
      const firstKey = cache.keys().next().value;
      cache.delete(firstKey);  // remove oldest entry
    }
    cache.set(key, result);
    return result;
  };
}

// WeakMap memoize for object arguments (no memory leak):
function memoizeObject(fn) {
  const cache = new WeakMap();  // GC-friendly: object keys auto-cleaned
  return function(obj) {        // works when single object argument
    if (cache.has(obj)) return cache.get(obj);
    const result = fn(obj);
    cache.set(obj, result);
    return result;
  };
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: JSON.stringify fails for functions/circular refs
const memoized = memoize(fn);
memoized(() => 'test');    // key = undefined — won't work
memoized({ a: 1, b: { c: 2 } });  // works for plain objects

// ❌ Wrong: memoizing functions with side effects
const getTime = memoize(() => Date.now());
getTime();  // caches first timestamp — always returns same value!
// Memoize only PURE functions (same input → always same output)

// ❌ Wrong: not handling 'this' in methods
const obj = { multiplier: 2 };
obj.double = memoize(function(n) { return n * this.multiplier; });
obj.double(5);  // Works, but cache key doesn't include 'this' — could return wrong cached value
```

---

## 🎯 Interview Tip (1 line)
Say: "Memoize works only for pure functions — same input must always produce same output; WeakMap for object args to prevent memory leaks."

---

## 🔗 Related Questions
→ Q084 (curry) | Q099 (LRU cache) | Q277 (memoization optimization) | Q307 (memoization real use case)
