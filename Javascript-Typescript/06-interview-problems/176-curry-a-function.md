# 176. Curry a Function
# हिंदी में: Function को Curry करना — Arguments को एक-एक करके देना और partial application

---

## 🔵 Simple Definition (English)
Currying turns a function that takes many arguments, like `f(a, b, c)`, into a chain of functions that each take one argument, like `f(a)(b)(c)`. You can also give some arguments now and the rest later, which is called partial application.

## 🔵 सरल परिभाषा (Hindi)
Currying एक ऐसे function को, जो कई arguments लेता है, जैसे `f(a, b, c)`, एक chain में बदल देता है जहाँ हर step एक argument लेता है, जैसे `f(a)(b)(c)`। आप कुछ arguments अभी दे सकते हैं और बाकी बाद में, इसे partial application कहते हैं।

---

## 🔴 Problem it Solves
**Problem Statement:** Write `curry(fn)` that returns a function. When it is called with fewer arguments than `fn` expects, it returns a new function that waits for the rest. When it has enough arguments, it calls `fn` and returns the result. Calls can be split in any way, such as `f(1)(2, 3)`.

Many real code paths need a function with one setting fixed. A pricing function needs `(region, plan, user)`, but a route only knows the region. Without currying, every caller writes a small wrapper. With currying, you prepare the function once for each region and reuse it.

## 🔴 यह क्यों बना? (Hindi)
**Problem Statement:** `curry(fn)` लिखो जो एक function लौटाए। जब इसे `fn` की ज़रूरत से कम arguments के साथ बुलाया जाए, तो यह एक नया function लौटाए जो बाकी arguments का इंतज़ार करे। जब पर्याप्त arguments हों, तो `fn` चलाकर result लौटाए। Calls किसी भी तरह बाँटी जा सकती हैं, जैसे `f(1)(2, 3)`।

अक्सर एक setting पहले से तय होती है। Pricing function को `(region, plan, user)` चाहिए, पर route को सिर्फ़ region पता है। बिना currying के हर caller अपना wrapper लिखता है। Currying से एक बार region के हिसाब से function तैयार करो और बार-बार इस्तेमाल करो।

---

## 🟢 How it Works — Step by Step

Step 1 → Collect the arguments given in this call.
Step 2 → Compare the collected count with `fn.length`, the number of parameters the function declares.
Step 3 → If there are enough, call `fn` with the collected arguments and return its result.
Step 4 → If not, return a new function that remembers the collected arguments.
Step 5 → When that new function is called, join its arguments with the remembered ones and repeat step 2.
Step 6 → Keep `this` so methods still work.

## 🟢 कैसे काम करता है? (Hindi)

Step 1 → इस call में दिए गए arguments इकट्ठे करो।
Step 2 → इकट्ठे arguments की गिनती की तुलना `fn.length` से करो, यानी function के declared parameters।
Step 3 → अगर पूरे हैं, तो `fn` को उन arguments के साथ चलाओ और result लौटाओ।
Step 4 → अगर नहीं, तो एक नया function लौटाओ जो दिए गए arguments याद रखे।
Step 5 → नया function बुलाने पर उसके arguments पुराने वाले के साथ जोड़ो, और step 2 दोहराओ।
Step 6 → `this` को सहेजो, ताकि methods भी काम करें।

---

## 🟡 Real World Example
Razorpay's fee logic depends on the merchant, the payment method and the amount. A checkout service builds `feeFor(merchant)` once per merchant, then `feeFor(merchant)(method)` for each payment method, and only the amount changes per request. Express middleware factories such as `requireRole("admin")` use the same idea: the role is fixed first, the request is handled later.

Scenario: A payment fee is `fee(merchantPlan, method, amount)`. The checkout caches `const cardFee = fee("gold")("card")` and calls `cardFee(1200)` for each order.

## 🟡 Real Example Hindi mein
Razorpay की fee logic merchant, payment method और amount पर निर्भर है। Checkout service हर merchant के लिए `feeFor(merchant)` एक बार बनाती है, फिर method के लिए `feeFor(merchant)(method)`, और हर request पर सिर्फ़ amount बदलता है। Express में `requireRole("admin")` जैसे middleware factories भी यही तरीका हैं: role पहले तय होता है, request बाद में संभाली जाती है।

उदाहरण: Payment fee `fee(merchantPlan, method, amount)` है। Checkout `const cardFee = fee("gold")("card")` एक बार बनाता है, और हर order के लिए `cardFee(1200)` बुलाता है।

---

## 💻 Code Example — Basic
```javascript
// Basic: curry by counting arguments against fn.length
function curry(fn) {
  return function curried(...args) {         // the wrapper that collects arguments
    if (args.length >= fn.length) {          // enough arguments for the original function?
      return fn.apply(this, args);           // yes: call it and return the result
    }
    return (...more) => curried.apply(this, [...args, ...more]); // no: return a function waiting for the rest
  };
}

// Sample: an add function with three parameters
const add3 = curry((a, b, c) => a + b + c);
console.log(add3(1)(2)(3), add3(1, 2)(3), add3(1)(2, 3)); // Expected output: 6 6 6

// Edge case: a function with one parameter is called as usual
const double = curry((n) => n * 2);
console.log(double(21));                     // Expected output: 42
```

## 💻 Code Example — Advanced
```javascript
// Advanced: placeholders (_) so any argument can be skipped, plus an explicit arity option
const _ = Symbol("placeholder");             // a unique marker that means "leave this slot empty"

function curry(fn, arity = fn.length) {      // arity defaults to the declared parameter count
  // Guard: fn must be a function
  if (typeof fn !== "function") throw new TypeError("curry expects a function");
  // Guard: arity must be a non-negative whole number
  if (!Number.isInteger(arity) || arity < 0) throw new RangeError("arity must be a whole number >= 0");

  // make(saved) returns a function that remembers `saved` (an array that may contain placeholders)
  const make = (saved) => function (...incoming) {
    const merged = [];                       // the new argument list
    let k = 0;                               // index into the incoming arguments
    for (const slot of saved) {              // walk through the saved slots in order
      if (slot === _ && k < incoming.length) merged.push(incoming[k++]); // fill a placeholder with a new value
      else merged.push(slot);                // keep the saved value
    }
    while (k < incoming.length) merged.push(incoming[k++]); // any extra arguments go at the end

    const filled = merged.filter((x) => x !== _).length; // how many real values we have now
    if (filled >= arity) return fn.apply(this, merged);  // enough values: call the original
    return make(merged);                     // still missing values: return another waiting function
  };

  return make([]);                           // start with nothing saved
}

// Test 1: normal currying in any split
const volume = curry((l, w, h) => l * w * h);
console.log(volume(2)(3)(4), volume(2, 3)(4), volume(2)(3, 4)); // Expected output: 24 24 24

// Test 2: placeholders let us fix the middle argument first
console.log(volume(_, 3, _)(2)(4));          // Expected output: 24

// Test 3: a function with a custom arity (only 2 values needed, even though fn declares 3)
const pair = curry((a, b, c) => [a, b, c].filter((x) => x !== undefined).join("-"), 2);
console.log(pair("x")("y"));                 // Expected output: x-y

// Time:  O(k) per call, where k is the number of arguments collected so far
// Space: O(k) for the saved arguments in each returned function
```

### Edge Cases
- A function with no parameters has `fn.length === 0`, so it runs on the first call.
- Extra arguments beyond `fn.length` are passed through on the call that completes the set.
- Functions with default parameters or rest parameters report a shorter `fn.length`; pass the `arity` option when this matters.
- Calling a curried function with zero arguments returns a waiting function, not a result, when the function needs at least one.
- Placeholders count as missing values, so `volume(_, _, _)` still waits.

---

## 🟠 Express.js Integration
Express middleware is often a factory. `requireRole` takes the role first and returns a middleware with the usual `(req, res, next)` signature. The curried version does the same job with one generic helper.

```javascript
// Express.js: a curried authorization middleware, so the role is fixed first and the request later
const express = require("express");          // web framework
const app = express();                       // create the app

// Generic currying helper (same idea as the basic version, for the middleware signature)
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args); // all four values present: run
    return (...more) => curried.apply(this, [...args, ...more]); // wait for the rest
  };
}

// The function takes (role, req, res, next); the role is fixed when the route is declared
const requireRole = curry((role, req, res, next) => {
  const userRole = req.headers["x-user-role"];   // pretend the role comes from a verified token
  if (userRole !== role) {                       // wrong role for this route
    return res.status(403).json({ error: `requires role ${role}` }); // 403 Forbidden
  }
  next();                                        // role matches: continue to the route handler
});

// Each route fixes the role once, when it is declared
app.get("/admin/refunds", requireRole("admin"), (req, res) => {
  res.json({ refunds: [] });                     // 200 OK, only for admins
});

app.get("/seller/orders", requireRole("seller"), (req, res) => {
  res.json({ orders: [] });                      // 200 OK, only for sellers
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Auth-aware API running");       // printed when ready
});
```

---

## ⚠️ Common Mistakes to Avoid

❌ **Mistake 1:** Using `fn.length` on a function with default parameters
✅ Correct: default parameters are not counted by `fn.length`, so currying stops too early. Pass the arity explicitly.

```javascript
// Wrong: the function declares three parameters, but length counts only the first one before the default
const greet = (name, greeting = "Hello", punct = "!") => `${greeting}, ${name}${punct}`;
console.log(greet.length);                   // Expected output: 1

// Right: pass the real arity, so the curry waits for all three values
function curryWithArity(fn, arity) {
  return function curried(...args) {
    if (args.length >= arity) return fn.apply(this, args);
    return (...more) => curried.apply(this, [...args, ...more]);
  };
}
const greetRight = curryWithArity(greet, 3);
console.log(greetRight("Ravi")("Namaste")("?"));  // Expected output: Namaste, Ravi?
```

❌ **Mistake 2:** Forgetting that a curried call with too few arguments returns a function, not a value
✅ Correct: check that the final call has all the arguments before using the result.

```javascript
function curry(fn) {                         // basic curry, repeated so this block runs alone
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args);
    return (...more) => curried.apply(this, [...args, ...more]);
  };
}

// Wrong: the result is still a function, so using it as a number gives text, not a sum
const add = curry((a, b) => a + b);
const partial = add(1);                      // only one argument so far
console.log(typeof partial);                 // Expected output: function
console.log(typeof (partial + 1));           // Expected output: string (the function was turned into text)

// Right: supply the last argument before using the value
console.log(add(1)(2) + 1);                  // Expected output: 4
```

---

## 🧠 Tricky Interview Question
```javascript
function curry(fn) {                         // basic curry, so this block runs alone
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args);
    return (...more) => curried.apply(this, [...args, ...more]);
  };
}
const f = curry((a, b, c) => `${a}${b}${c}`);
console.log(f(1)(2)(3));                     // ?
console.log(typeof f(1));                    // ?
console.log(f(1, 2)(3, 4));                  // ?
const g = curry(() => "no args");
console.log(g());                            // ?
```
Answer:
```
123          ← each call adds arguments until there are three
function     ← f(1) is not enough, so it returns a waiting function
123          ← extra arguments (4) are ignored by the string template, which uses only a, b, c
no args      ← fn.length is 0, so the first call runs the function immediately
```
The trap is the last line: a function with no parameters does not need currying at all. Students often expect `g()` to return a function. Explain that `curry` checks `fn.length` before it decides.

---

## ⚫ Interview Questions + Answers

**Q1: What is the difference between currying and partial application?**
A1: Currying always turns a function into one-argument steps. Partial application fixes some arguments and returns a function for the rest. The curry helper here supports both, because a partial call simply returns a waiting function.

**Q2: How does the basic `curry` know when to call the function?**
A2: It compares the number of collected arguments with `fn.length`. When they are equal or more, it calls the original function.

**Q3: What is the time complexity?**
A3: O(k) per call, where k is the number of arguments collected so far. Each call copies the saved arguments into a new array.

**Q4: Why is `this` passed along with `apply`?**
A4: So that curried methods on objects keep their receiver. Without `apply(this, ...)`, `this` would be `undefined` inside the function in strict mode.

**Q5: Where is currying used in real code?**
A5: Middleware factories, configuration functions such as `fee(plan)(method)`, and functional libraries such as Ramda, which curry all their functions so they can be composed.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You create several functions that differ only in one fixed value
- You want to compose functions, where each step receives one argument
- You build middleware factories, such as role checks or validators

❌ Avoid when:
- The function has many optional or variadic arguments; currying makes the signature hard to read
- Performance matters in a tight loop; each partial call creates new closures
- The team is not used to the style; a plain wrapper with a clear name is easier to maintain

---

## 📊 Visual Diagram
```
add3 = curry((a, b, c) => a + b + c)

add3(1)          -> waiting for [b, c]         (saved: [1])
  (2)            -> waiting for [c]            (saved: [1, 2])
    (3)          -> 3 values -> fn(1, 2, 3) = 6

add3(1, 2)(3)    -> saved [1, 2] -> then fn(1, 2, 3) = 6
add3(1)(2, 3)    -> saved [1]    -> then fn(1, 2, 3) = 6
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Currying | Turning f(a, b, c) into f(a)(b)(c) | Function को एक-एक argument की chain बनाना |
| Partial application | Fixing some arguments now and the rest later | कुछ arguments अभी देकर बाकी बाद में देना |
| Arity | The number of parameters a function expects | Function कितने parameters लेता है |
| fn.length | The declared parameter count (before defaults) | Default से पहले declared parameters की गिनती |
| Placeholder | A marker that leaves a slot open | वह marker जो slot खाली रखता है |
| Closure | A function that remembers saved values | Saved values याद रखने वाला function |

---

## ⚡ 3-Line Summary
English:
1. Currying turns `f(a, b, c)` into a chain, so each call can supply some of the arguments.
2. The helper compares the collected arguments with `fn.length` and calls the function when they are enough.
3. Watch out for default parameters, which `fn.length` does not count; pass the arity when needed.

Hindi:
1. Currying `f(a, b, c)` को chain में बदलता है, ताकि हर call कुछ arguments दे सके।
2. Helper इकट्ठे arguments की तुलना `fn.length` से करता है, और पूरे होने पर function चलाता है।
3. Default parameters पर ध्यान दो, क्योंकि `fn.length` उन्हें नहीं गिनता; ज़रूरत हो तो arity खुद दो।

---

## ➡️ Next Topic
**177. Compose Functions** — currying makes one-argument functions easy to chain; the next problem chains them into a single pipeline, where the output of one step feeds the next.
