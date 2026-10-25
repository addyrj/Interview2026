# 173. Implement memoization
# हिंदी में: Memoization लागू करना — एक ही input के लिए result को याद रखना

---

## 🔵 Simple Definition (English)
Memoization stores the result of a function for each set of arguments. When the same arguments come again, the stored result is returned, and the function body does not run. It trades memory for speed.

## 🔵 सरल परिभाषा (Hindi)
Memoization किसी function के result को हर arguments के सेट के लिए सहेजता है। वही arguments दोबारा आएँ तो सहेजा हुआ result लौटता है, और function का body दोबारा नहीं चलता। यह memory देकर speed पाने का तरीका है।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `memoize(fn)` that returns a function with the same behavior as `fn`, but calls `fn` only once for each distinct set of arguments. Repeated calls with the same arguments return the cached value.

Expensive pure work repeats often. A price calculator for a menu may run the same tax formula thousands of times for the same 20 dishes. A recursive Fibonacci without a cache computes the same small values again and again, so `fib(40)` makes about 300 million calls.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `memoize(fn)` लिखो जो एक ऐसा function लौटाए जिसका व्यवहार `fn` जैसा ही हो, लेकिन हर अलग arguments के सेट के लिए `fn` सिर्फ़ एक बार चले। वही arguments दोबारा आएँ तो cache की value लौटे।

अक्सर एक ही भारी काम बार-बार होता है। Menu के 20 dishes के लिए tax formula हज़ारों बार चल सकता है। बिना cache के recursive Fibonacci छोटी values को बार-बार गिनता है, इसलिए `fib(40)` लगभग 300 million calls करता है।

---

## 🟢 How it Works — Step by Step

Step 1 → Create an empty cache (a `Map`) inside the closure.
Step 2 → Turn the arguments into a key, for example with `JSON.stringify`.
Step 3 → If the key is in the cache, return the stored value right away.
Step 4 → If not, call the original function with the arguments.
Step 5 → Store the result under the key, then return it.
Step 6 → Only pure functions (same input, same output, no side effects) are safe to memoize.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → Closure के अंदर एक खाली cache (`Map`) बनाओ।
Step 2 → Arguments को एक key में बदलो, जैसे `JSON.stringify` से।
Step 3 → अगर key cache में है, तो सहेजी हुई value तुरंत लौटाओ।
Step 4 → अगर नहीं है, तो original function को arguments के साथ बुलाओ।
Step 5 → Result को key के नीचे सहेजो, फिर लौटाओ।
Step 6 → सिर्फ़ pure functions (वही input, वही output, कोई side effect नहीं) को memoize करना सुरक्षित है।

---

## 🟡 Real World Example
Swiggy's delivery fee calculator uses the same distance-to-fee table for the same zone many times per minute, so the result is cached. Zomato's menu page caches the price calculation for the same dish with the same options. Node's `require` is a form of memoization too: a module loads once and later calls get the same object.

Scenario: A checkout page calls `priceWithTax(250, 0.05)` 500 times in one session. Memoization runs the formula once and returns the cached answer 499 times.

## 🟡 Real Example Hindi mein
Swiggy का delivery fee calculator एक ही zone के लिए distance-से-fee table हर मिनट कई बार इस्तेमाल करता है, इसलिए result cache होता है। Zomato का menu page एक ही dish और options के लिए price calculation cache करता है। Node का `require` भी memoization का रूप है: एक module एक बार load होता है, और बाद की calls वही object लौटाती हैं।

उदाहरण: Checkout page एक session में `priceWithTax(250, 0.05)` 500 बार बुलाता है। Memoization formula एक बार चलाता है और 499 बार cache का जवाब लौटाता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: memoize using a Map and JSON.stringify keys
function memoize(fn) {
  const cache = new Map();                   // stores key -> result
  return function (...args) {                // the wrapper with the same call shape as fn
    const key = JSON.stringify(args);        // turn the argument list into a string key
    if (cache.has(key)) return cache.get(key); // seen before: return the saved answer
    const result = fn.apply(this, args);     // not seen: compute it once
    cache.set(key, result);                  // save it for the next call with the same arguments
    return result;                           // return the new answer
  };
}

// Sample: a price formula that counts how many times it really runs
let calls = 0;                               // counts real computations
const priceWithTax = memoize((price, rate) => {
  calls++;                                   // this line runs only on a cache miss
  return Math.round(price * (1 + rate));     // round to whole rupees
});
console.log(priceWithTax(100, 0.18), priceWithTax(100, 0.18), calls); // Expected output: 118 118 1

// Edge case: different arguments are different keys
console.log(priceWithTax(250, 0.1), calls);  // Expected output: 275 2
```

## 💻 Code Example — Advanced
```javascript
// Advanced: LRU cache with a size limit, hit/miss statistics, and clear()
function memoize(fn, { maxSize = 100 } = {}) {
  // Guard: fn must be a function
  if (typeof fn !== "function") throw new TypeError("fn must be a function");
  // Guard: maxSize must be a positive whole number
  if (!Number.isInteger(maxSize) || maxSize < 1) throw new RangeError("maxSize must be a positive integer");

  const cache = new Map();                   // Map keeps insertion order, we use that order as LRU order
  let hits = 0;                              // how many calls were answered from the cache
  let misses = 0;                            // how many calls ran fn

  function memoized(...args) {               // the wrapper
    const key = JSON.stringify(args);        // key built from all arguments
    if (cache.has(key)) {                    // cache hit
      hits++;                                // count it
      const value = cache.get(key);          // read the value
      cache.delete(key);                     // move the key to the end: it is now the most recently used
      cache.set(key, value);
      return value;                          // answer from memory
    }
    misses++;                                // cache miss: real work is needed
    const value = fn.apply(this, args);      // compute the answer once
    cache.set(key, value);                   // store the newest entry at the end
    if (cache.size > maxSize) {              // over the limit?
      const oldest = cache.keys().next().value; // the first key is the least recently used
      cache.delete(oldest);                  // evict it to free memory
    }
    return value;                            // the fresh answer
  }

  memoized.stats = () => ({ hits, misses, size: cache.size }); // inspect the cache
  memoized.clear = () => {                   // empty the cache and reset the counters
    cache.clear();
    hits = 0;
    misses = 0;
  };
  return memoized;                           // the wrapper with stats and clear
}

// Test 1: Fibonacci with a cache; each n is computed once
const fib = memoize((n) => (n < 2 ? n : fib(n - 1) + fib(n - 2)), { maxSize: 1000 });
console.log(fib(50));                        // Expected output: 12586269025
console.log(JSON.stringify(fib.stats()));    // Expected output: {"hits":48,"misses":51,"size":51}

// Test 2: LRU eviction. The least recently used key (3) is removed when the cache is full.
const square = memoize((x) => x * x, { maxSize: 2 });
square(2); square(3); square(2);             // 2 is now the most recently used
square(4);                                   // cache is over the limit: 3 is evicted
console.log(JSON.stringify(square.stats())); // Expected output: {"hits":1,"misses":3,"size":2}

// Time:  O(1) average per call for Map lookup (plus JSON.stringify of the arguments)
// Space: O(maxSize) entries in the cache
```

### Edge Cases
- Calls with the same values but different object identities are different keys in `Map`, because the key is a string built from the values.
- `undefined` and `null` both turn into `null` inside arrays by `JSON.stringify`, so they share a key (see the mistakes section).
- Functions and symbols inside arguments are dropped by `JSON.stringify`, so calls that differ only in those look the same.
- With `maxSize: 1`, only the last result is kept, which can still help for repeated calls.
- A function that returns a Promise is memoized as the Promise; a rejected Promise stays cached too, so cache failures carefully.

---

## 🟠 Express.js Integration
An expensive report query is the same for every request in the same minute. Memoizing the loader inside the route saves database time. The cache has a small TTL so the data does not stay stale for long.

```javascript
// Express.js: cache an expensive menu query for 60 seconds per restaurant
const express = require("express");          // web framework
const app = express();                       // create the app

// Pretend slow database call (in real life this is a SQL or MongoDB query)
async function loadMenu(restaurantId) {
  await new Promise((r) => setTimeout(r, 200)); // simulate 200 ms of database time
  return { restaurantId, dishes: ["Paneer Tikka", "Dal Makhani"] }; // sample data
}

// Small time-based cache: a memoize that also expires entries after ttlMs
function memoizeWithTtl(fn, ttlMs) {
  const cache = new Map();                   // key -> { value, expiresAt }
  return async (key) => {                    // async because the loader is async
    const now = Date.now();                  // current time
    const hit = cache.get(key);              // look up the key
    if (hit && hit.expiresAt > now) return hit.value; // fresh entry: return it without a database call
    const value = await fn(key);             // expired or missing: load again
    cache.set(key, { value, expiresAt: now + ttlMs }); // store with a new expiry time
    return value;                            // return the fresh value
  };
}

const cachedMenu = memoizeWithTtl(loadMenu, 60 * 1000); // 60 seconds

// GET /api/restaurants/:id/menu
app.get("/api/restaurants/:id/menu", async (req, res) => {
  try {
    const menu = await cachedMenu(req.params.id); // cached or fresh
    res.json(menu);                          // 200 OK
  } catch (err) {
    res.status(500).json({ error: "menu unavailable" }); // 500 Internal Server Error
  }
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Menu cache API running");    // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Memoizing with object arguments, where each new object is a new cache key in a `Map` keyed by reference
✅ Correct: use a stable primitive id as the key, or build the key from the values.

```javascript
// Wrong: a Map keyed by object reference never hits for new objects
const cacheByRef = new Map();
const total = (order) => {
  if (cacheByRef.has(order)) return cacheByRef.get(order); // only the same object hits
  const t = order.items.length;
  cacheByRef.set(order, t);
  return t;
};
console.log(total({ items: [1, 2] }), total({ items: [1, 2] }), cacheByRef.size); // Expected output: 2 2 2

// Right: key by the value that identifies the order (or by JSON of its content)
const cacheByKey = new Map();
const totalRight = (order) => {
  const key = order.id;                     // stable primitive id
  if (cacheByKey.has(key)) return cacheByKey.get(key);
  const t = order.items.length;
  cacheByKey.set(key, t);
  return t;
};
console.log(totalRight({ id: "o1", items: [1, 2] }), totalRight({ id: "o1", items: [1, 2] }), cacheByKey.size); // Expected output: 2 2 1
```

❌ **Mistake 2:** Keys that collide, such as `undefined` and `null` inside arrays
✅ Correct: include the type in the key, so different types never share one key.

```javascript
// Wrong: JSON.stringify([undefined]) and JSON.stringify([null]) are both "[null]"
function memoize(fn) {                       // the basic memoize, repeated so this block runs alone
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (!cache.has(key)) cache.set(key, fn(...args));
    return cache.get(key);
  };
}
let runs = 0;                                // counts real computations
const label = memoize((v) => { runs++; return String(v); });
console.log(label(undefined), label(null), runs); // Expected output: undefined undefined 1 (wrong: null gets the undefined answer)

// Right: a key that also records the type of each argument
const typedKey = (args) => JSON.stringify(args.map((a) => [typeof a, a === undefined ? "undefined" : a]));
console.log(typedKey([undefined]) !== typedKey([null])); // Expected output: true
```

---

## 🧠 Tricky Interview Question
```javascript
function memoize(fn) {                       // basic memoize (JSON keys keep types), so this block runs alone
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);
    if (!cache.has(key)) cache.set(key, fn(...args));
    return cache.get(key);
  };
}
let count = 0;
const add = memoize((a, b) => { count++; return a + b; });
console.log(add(1, 2), add("1", 2), count);
console.log(add(1, 2), add(1, 2), count);
```
Answer:
```
3 12 2   ← add(1,2) runs (count 1); add("1",2) is a different key (count 2), and "1" + 2 is "12"
3 3 2    ← both calls with (1,2) come from the cache, so count stays 2
```
Two traps: `JSON.stringify` keeps types (`1` and `"1"` are different keys), and a cache hit does not run the body, so the counter does not change. Students who expect `"12"` to be `3` or the counter to be `3` have usually forgotten one of these.

---

## ⚫ Interview Questions + Answers

**Q1: What makes a function safe to memoize?**
A1: It must be pure: the same arguments always give the same result, and it must not depend on time, random numbers, or outside state. Memoizing `Date.now()` returns a stale time.

**Q2: Why does the advanced version delete and re-insert a key on a hit?**
A2: A `Map` keeps insertion order. Re-inserting moves the key to the end, so the first key is always the least recently used. That gives a simple LRU cache.

**Q3: What is the difference between memoization and caching?**
A3: Memoization is caching the result of a function for given inputs. Caching is the broader idea and can cover HTTP responses, database rows and files, with expiry rules that memoization often does not need.

**Q4: How do you memoize a recursive function such as Fibonacci?**
A4: Make the recursive calls go through the memoized function. Then each smaller value is computed once, and the work changes from exponential to linear.

**Q5: What is the time and space complexity?**
A5: O(1) average time per call for a Map lookup, plus the cost of building the key. Space is O(maxSize) in the advanced version, or unbounded in the basic version.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- The function is pure and expensive, such as a tax or price formula, or a parser
- The same inputs repeat often, such as a dish, zone, or user id
- A recursive function recomputes the same subproblems

❌ Avoid when:
- The function depends on time, random values, or outside state
- The inputs are almost always different, so the cache never hits and only uses memory
- The arguments are huge objects that are costly to turn into keys

---

## 📊 Visual Diagram
```
fib(4) without memo          fib(4) with memo (each box computed once)

          fib(4)                      fib(4)
        /        \                   /      \
    fib(3)      fib(2)            fib(3)    fib(2)  <- fib(2) from cache
    /    \      /    \            /    \
 fib(2) fib(1) fib(1) fib(0)   fib(2) fib(1)
 /   \
fib(1) fib(0)

 calls: 9                       calls that run the body: 5
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Memoization | Caching a function's result for given inputs | Inputs के लिए result सहेजना |
| Pure function | Same input gives same output, no side effects | वही input, वही output, कोई side effect नहीं |
| Cache hit | The answer was already stored | Answer पहले से सहेजा हुआ है |
| Cache miss | The answer must be computed | Answer नए सिरे से निकालना है |
| LRU | Least Recently Used: evict the oldest unused entry | सबसे पुराना और कम इस्तेमाल हुआ entry हटाना |
| TTL | Time to live: how long an entry stays valid | Entry कितनी देर valid रहे |

---

## ⚡ 3-Line Summary
English:
1. Memoization stores results by arguments, so repeated calls skip the work.
2. Use it only for pure functions, and watch the key: types and object identity matter.
3. Add a size limit or TTL in production, so the cache does not grow forever.

Hindi:
1. Memoization arguments के हिसाब से result सहेजता है, ताकि दोहराए गए calls काम न करें।
2. इसे सिर्फ़ pure functions पर इस्तेमाल करो, और key पर ध्यान दो: types और object की पहचान मायने रखती है।
3. Production में size limit या TTL रखो, ताकि cache अनंत तक न बढ़े।

---

## ➡️ Next Topic
**174. Implement Promise.all** — memoization reuses finished answers; the next problem runs many async tasks together and waits for all of them.
