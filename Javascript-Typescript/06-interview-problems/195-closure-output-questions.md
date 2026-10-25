# 195. Closure Output Questions
# हिंदी में: Closure Output Questions — function अपने बाहर के variables कैसे याद रखता है

---

## 🔵 Simple Definition (English)
A closure is a function that keeps access to the variables of the scope where it was created, even after that outer function has returned. Output questions test whether you know that closures capture the variable itself (a binding), not a copy of its value at creation time.

## 🔵 सरल परिभाषा (Hindi)
Closure एक ऐसा function है जो उस scope के variables को याद रखता है जहाँ वह बना था, भले ही वह outer function return हो चुका हो। Output questions यह परखते हैं कि closure variable का "copy" नहीं, बल्कि variable (binding) ही पकड़ता है।

---

## 🔴 Problem it Solves

**Problem statement:** Predict the output of this code.

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log("var:", i), 0);   // (1) ?
}
for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log("let:", j), 0);   // (2) ?
}
```

Answer: `var: 3` printed three times, then `let: 0`, `let: 1`, `let: 2`. Interviewers ask this because it shows the difference between `var` (one shared binding) and `let` (a new binding per loop iteration), and it touches the event loop too. Closures are also needed in real code: private state, memoization, middleware factories and callbacks that remember a request id.

## 🔴 यह क्यों बना? (Hindi)
Callbacks (timers, events, network responses) बाद में चलते हैं, तब तक loop या function खत्म हो चुका होता है। अगर callback को उस समय की सही value चाहिए, तो उसे उस variable को याद रखना पड़ता है। Closure यही काम करता है। इसके बिना private state, memoization और middleware जैसी आम patterns संभव नहीं होतीं।

---

## 🟢 How it Works — Step by Step

Step 1 → Outer function call होता है और उसका local scope बनता है, जिसमें `count` जैसा variable होता है।
Step 2 → Inner function उसी scope का reference रखता है, इसे closure कहते हैं।
Step 3 → Outer function return हो जाता है, पर `count` memory में रहता है क्योंकि inner function उसे इस्तेमाल कर सकता है।
Step 4 → हर call inner function उसी binding को पढ़ता या बदलता है, copy को नहीं।
Step 5 → `let` in a `for` loop हर iteration के लिए नई binding बनाता है, `var` एक ही binding साझा करता है।

## 🟢 कैसे काम करता है? (Hindi)
Step 1 → Outer function call होता है और उसका local scope बनता है, जिसमें `count` जैसा variable होता है।
Step 2 → Inner function उसी scope का reference रखता है, इसे closure कहते हैं।
Step 3 → Outer function return हो जाता है, पर `count` memory में रहता है क्योंकि inner function उसे इस्तेमाल कर सकता है।
Step 4 → हर call inner function उसी binding को पढ़ता या बदलता है, copy को नहीं।
Step 5 → `for` loop में `let` हर iteration के लिए नई binding बनाता है, जबकि `var` एक ही binding साझा करता है।

---

## 🟡 Real World Example
Swiggy के cart service में "add to cart" button के लिए हर item का अपना handler बनता है, जो उस item का `itemId` याद रखता है। अगर handler `var` loop में बनें, तो सभी buttons आखिरी item का id भेजेंगे और गलत item cart में जाएगा। `let` या factory function से हर handler अपना id पकड़ता है।

Razorpay के dashboard में एक helper `makeRetry(attempt)` बनता है और retry logic अपने attempt number को closure में रखता है। हर retry सही backoff लेता है।

## 🟡 Real Example Hindi mein
Swiggy के cart service में "add to cart" button के लिए हर item का अपना handler बनता है, जो उस item का `itemId` याद रखता है। अगर handler `var` loop में बनें, तो सभी buttons आखिरी item का id भेजेंगे और गलत item cart में जाएगा। `let` या factory function से हर handler अपना id पकड़ता है।

Razorpay के dashboard में एक helper `makeRetry(attempt)` बनता है और retry logic अपने attempt number को closure में रखता है। हर retry सही backoff लेता है।

---

## 💻 Code Example — Basic
```javascript
// ── Closure basics: a function remembers variables from where it was created ──

function makeCounter(start = 0) {           // outer function with its own local variable
  let count = start;                        // private variable, not visible outside
  return {                                  // return functions that close over count
    increment() { count += 1; return count; }, // each call changes the same count
    decrement() { count -= 1; return count; }, // shares the same count binding
    value() { return count; },              // read access only
  };
}

const c1 = makeCounter();                   // first closure, its own count (starts at 0)
const c2 = makeCounter(10);                 // second closure, separate count (starts at 10)
console.log(c1.increment());                // 1
console.log(c1.increment());                // 2
console.log(c2.decrement());                // 9
console.log(c1.value(), c2.value());        // 2 9  (independent state)
console.log(c1.count);                      // undefined: count is not a property, it is private

// ── Closures in loops: var shares one binding, let makes one per iteration ──

const withVar = [];                         // array of functions
for (var i = 0; i < 3; i++) {               // var: one i for the whole loop
  withVar.push(() => i);                    // each function captures the SAME i
}
console.log(withVar.map(f => f()));         // [ 3, 3, 3 ]  (loop finished, i is 3)

const withLet = [];                         // array of functions
for (let j = 0; j < 3; j++) {               // let: a NEW j for every iteration
  withLet.push(() => j);                    // each function captures its own j
}
console.log(withLet.map(f => f()));         // [ 0, 1, 2 ]

// ── Fix for var with an IIFE (old style) ──
const fixed = [];                           // array of functions
for (var k = 0; k < 3; k++) {               // still var
  fixed.push((function (captured) {         // IIFE creates a new scope per iteration
    return () => captured;                  // closure captures the parameter copy
  })(k));                                   // pass the current value now
}
console.log(fixed.map(f => f()));           // [ 0, 1, 2 ]
```

**Expected output (verified with `node`):**
```
1
2
9
2 9
undefined
[ 3, 3, 3 ]
[ 0, 1, 2 ]
[ 0, 1, 2 ]
```

## 💻 Code Example — Advanced
```javascript
// memoize: a closure holds the cache, so callers cannot touch it.
// Adds an LRU (least recently used) limit using Map insertion order.

function memoize(fn, { maxSize = 100 } = {}) {    // returns a new function that closes over fn, cache, maxSize
  if (typeof fn !== "function") throw new TypeError("fn must be a function"); // validate input
  if (!Number.isInteger(maxSize) || maxSize < 1) { // validate the size limit
    throw new RangeError("maxSize must be an integer >= 1");
  }
  const cache = new Map();                        // private cache, only the closure can see it
  return function memoized(...args) {             // the returned function
    const key = JSON.stringify(args);             // key from arguments (works for JSON-safe args)
    if (cache.has(key)) {                         // cache hit: O(1) average
      const value = cache.get(key);               // read the stored result
      cache.delete(key);                          // remove and re-insert to mark as most recent
      cache.set(key, value);                      // Map keeps insertion order, so this is now last
      return value;                               // return the cached result, fn not called
    }
    const value = fn.apply(this, args);           // cache miss: run the real function once
    cache.set(key, value);                        // store the result for next time
    if (cache.size > maxSize) {                   // over the limit: evict least recently used
      cache.delete(cache.keys().next().value);    // first key in the Map is the oldest
    }
    return value;                                 // return the fresh result
  };
}

// ── Demo: count how many times the real function runs ──
let calls = 0;                                    // counter lives outside, closure reads it
const square = memoize(n => { calls += 1; return n * n; }, { maxSize: 2 }); // cache holds 2 results
console.log(square(3), square(3), calls);         // 9 9 1  (second call is a hit)
square(4);                                        // miss, cache = {3, 4}
square(5);                                        // miss, cache = {3, 4, 5} -> evict 3
console.log(square(3), calls);                    // 9 4  (3 was evicted, so it is recomputed)

// Complexity: get/set O(1) average; cache uses O(maxSize) memory.
// Caveat: JSON.stringify key ignores functions and treats {a:undefined} like {}.
```

**Expected output:**
```
9 9 1
9 4
```

---

## 🟣 Express.js Integration
A middleware factory is a closure in everyday Express code. `rateLimit(options)` returns a middleware that keeps its own `hits` Map. Each route that calls the factory gets an independent counter, with no global variable.

```javascript
// npm install express
const express = require("express");                   // import Express
const app = express();                                // create the app

// Factory: returns a middleware. `hits` and the limits live in this closure.
function rateLimit({ windowMs = 60_000, max = 5 } = {}) { // default: 5 requests per minute
  const hits = new Map();                             // ip -> { count, windowStart }, private
  return (req, res, next) => {                        // middleware: runs once per request
    const ip = req.ip;                                // client address provided by Express
    const now = Date.now();                           // current time in milliseconds
    const entry = hits.get(ip);                       // data from earlier requests, if any
    if (!entry || now - entry.windowStart >= windowMs) { // no entry or window expired
      hits.set(ip, { count: 1, windowStart: now });   // start a fresh window for this ip
      return next();                                  // allow the request
    }
    entry.count += 1;                                 // same window: count this request
    if (entry.count > max) {                          // over the limit
      const retry = Math.ceil((entry.windowStart + windowMs - now) / 1000); // seconds left
      res.set("Retry-After", String(retry));          // tell the client when to retry
      return res.status(429).json({ error: "too many requests" }); // 429 Too Many Requests
    }
    next();                                           // within the limit: continue to the route
  };
}

// Only this route gets the limit. Each factory call creates its own closure.
app.get("/coupon", rateLimit({ windowMs: 60_000, max: 3 }), (req, res) => {
  res.json({ code: "SAVE10" });                       // the protected response
});

app.listen(3000, () => console.log("listening on 3000")); // start the server
```

**Verified:** four quick `GET /coupon` calls return `200` three times, then `429` with a `Retry-After` header. Memory note: the `hits` Map grows with every IP, so production code needs cleanup (TTL) or a shared store such as Redis.

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: Using `var` in a loop with a callback and expecting each callback to see its own index.
✅ Correct: Use `let` in the loop header (new binding per iteration), or pass the value into a factory function.

```javascript
// Wrong: all three callbacks read the same i, which is 3 when they run
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log("wrong:", i), 0);      // prints 3, 3, 3
}

// Right: let gives each iteration its own j
for (let j = 0; j < 3; j++) {
  setTimeout(() => console.log("right:", j), 0);      // prints 0, 1, 2
}
```

❌ Mistake 2: Thinking a closure copies the value at creation time.
✅ Correct: A closure captures the variable, so it sees the latest value. To freeze a value, copy it into a new `const`.

```javascript
// Wrong: expects the old rate, but the closure reads the current variable
let rate = 5;                                         // mutable variable
const getRate = () => rate;                           // captures the variable, not the number 5
rate = 9;                                             // update after the closure was created
console.log("wrong:", getRate());                      // 9

// Right: take a snapshot with const
let rate2 = 5;                                        // mutable variable
const snapshot = rate2;                               // copy the current value into a new binding
const getSnapshot = () => snapshot;                   // captures the snapshot binding
rate2 = 9;                                            // this does not affect snapshot
console.log("right:", getSnapshot());                 // 5
```

**Edge cases (keep in mind):**
- A closure keeps its whole outer scope alive, so a large array in that scope can stay in memory.
- A closure that is called after its outer scope returned still works, and that is the point of closures.
- A closure that reads a `let` before its line runs throws a ReferenceError (TDZ), like any other name.
- `this` is not captured by a regular function. Arrow functions capture the surrounding `this`.

---

## 🧠 Tricky Interview Question
```javascript
// Tricky: var vs let in a loop, plus a closure that reads a later update
var fns = [];                                         // array of functions
for (var i = 0; i < 3; i++) {                         // var: one shared i
  fns.push(function () { return i; });                // closure reads the shared i
}
console.log(fns.map(f => f()));                       // (A) ?  (printed as [ 3, 3, 3 ])

const adders = [];                                    // array of functions
for (let k = 0; k < 3; k++) {                         // let: new k per iteration
  adders.push(x => x + k);                            // closure captures this iteration's k
}
console.log(adders.map(f => f(10)));                  // (B) ?

let shared = "before";                                // variable captured below
const show = () => shared;                            // closure over the binding
shared = "after";                                     // change happens before the call
console.log(show());                                  // (C) ?
```

Answer: `(A) [ 3, 3, 3 ]`, `(B) [ 10, 11, 12 ]`, `(C) after`.
Why: `var i` is one binding, and when the functions run after the loop, `i` is `3`, so all return `3`. Each `let k` iteration creates a fresh binding (0, 1, 2), so the adders return `10, 11, 12`. For (C), the closure captured the variable `shared`, not its value at creation time, so it returns the latest assignment, `"after"`.

---

## ⚫ Interview Questions + Answers

Q1: What is a closure in one sentence?
A1: A function bundled with references to the variables of the scope it was created in, so it can use them after the outer function returns.

Q2: Why does `var` in a `for` loop break `setTimeout` callbacks?
A2: `var` creates one binding for the whole function. All callbacks share it, and by the time they run, the loop has ended and the value is the final one.

Q3: How do you fix the loop problem without `let`?
A3: Wrap the body in an IIFE or a factory function, and pass the current value as an argument so each callback gets its own copy.

Q4: Does a closure copy the variables it uses?
A4: No. It keeps a reference to the variable binding, so it sees the latest value of that variable.

Q5: Can closures cause memory leaks?
A5: Yes. A closure keeps its entire outer scope alive, including large objects it does not use, so a long-lived closure can hold memory longer than expected.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You need private state, such as a counter, a cache or a configuration held behind functions.
- You build middleware or handler factories that differ only by their options.
- You schedule callbacks that must remember the value at the time they were created (use `let` or a factory).

❌ Avoid when:
- A class with explicit fields is clearer for a large amount of state.
- A long-lived closure captures a big object you do not need. Copy only what is used.
- You capture a loop variable with `var` and a callback that runs later.

---

## 📊 Visual Diagram
```
makeCounter(0) call
 ┌───────────────────────────────┐
 │ scope of makeCounter          │
 │   count = 0  ◄─────────┐      │
 │                        │      │
 │  increment() ──────────┤ closure keeps the binding alive
 │  value()     ──────────┘      │
 └───────────────────────────────┘
 makeCounter returns, but `count` lives on inside the closures.

Loop with var:  one binding i ──► fn1, fn2, fn3   (all read 3 later)
Loop with let:  i=0 ► fn1   i=1 ► fn2   i=2 ► fn3  (each reads its own value)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Closure | Function plus references to its outer scope's variables | क्लोज़र |
| Binding | The named slot that holds a variable's current value | बाइंडिंग |
| Lexical scope | Scope decided by where the code is written | लेक्सिकल स्कोप |
| Private state | Data reachable only through the closure's functions | प्राइवेट स्टेट |
| IIFE | Immediately invoked function expression, used to create a new scope | IIFE |
| Memoization | Caching results of a pure function using a closure | मेमोइज़ेशन |
| LRU | Least recently used eviction policy | LRU |
| Factory function | Function that returns a new closure with its own state | फ़ैक्टरी फ़ंक्शन |

---

## ⚡ 3-Line Summary
English: A closure keeps access to the variables of the scope where it was created, even after that scope has returned.
English: Closures capture the variable itself, so `var` in a loop shares one binding, while `let` gives each iteration its own.
English: Use closures for private state, memoization and middleware factories, and copy values when you need a snapshot.

Hindi: Closure उस scope के variables तक पहुँच बनाए रखता है जहाँ वह बना था, भले ही वह scope return हो चुका हो।
Hindi: Closure variable को पकड़ता है, इसलिए loop में `var` एक ही binding साझा करता है, जबकि `let` हर iteration को अपनी binding देता है।
Hindi: Private state, memoization और middleware factories के लिए closures इस्तेमाल करें, और snapshot चाहिए तो value को copy करें।

---

## ➡️ Next Topic
196. this Output Questions — closures के बाद `this` पढ़ना सही है, क्योंकि closures variables को पकड़ते हैं, जबकि `this` function call के तरीके पर तय होता है। दोनों को अलग समझना interview में अक्सर साथ पूछा जाता है।
