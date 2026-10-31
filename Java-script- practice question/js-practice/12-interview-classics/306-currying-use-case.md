---

# Q306. currying real use case
# Category: Interview Classics
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What is currying? Implement a generic `curry` function and show a real use case: creating reusable, pre-configured functions (API URL builder and logger).

---

## 💡 Quick Concept (2 lines only)
Currying turns `f(a, b, c)` into `f(a)(b)(c)`, so you can fix some arguments early and reuse the resulting function.
हिंदी: Currying में function को एक-एक argument लेने वाले functions की chain बना देते हैं ताकि कुछ arguments पहले fix हो जाएँ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: read how many arguments the original function needs (fn.length)
// Step 2: collect arguments across calls until we have enough
// Step 3: when enough, call the original; otherwise return another function

function curry(fn) {
  return function curried(...args) {            // collects args of this call
    if (args.length >= fn.length) {             // enough arguments collected?
      return fn.apply(this, args);              // yes -> run the original function
    }
    return (...more) => curried.apply(this, [...args, ...more]); // no -> wait for more
  };
}

// Real use case 1: reusable API URL builders
const buildUrl = curry((base, resource, id) => `${base}/${resource}/${id}`); // 3-arg function
const api = buildUrl('https://api.example.com');   // base fixed once
const usersApi = api('users');                     // resource fixed
const postsApi = api('posts');                     // another pre-configured function

// Real use case 2: logger with preset level
const log = curry((level, module, msg) => `[${level}] ${module}: ${msg}`); // 3-arg function
const logError = log('ERROR');                     // level fixed

// ============================================
// TEST CASES
// ============================================

const add3 = curry((a, b, c) => a + b + c);        // simple curried sum

console.log(add3(1)(2)(3));                        // Expected: 6
console.log(add3(1, 2)(3));                        // Expected: 6
console.log(add3(1)(2, 3));                        // Expected: 6
console.log(usersApi(7));                          // Expected: https://api.example.com/users/7
console.log(postsApi(42));                         // Expected: https://api.example.com/posts/42
console.log(logError('auth')('token expired'));    // Expected: [ERROR] auth: token expired
```

---

## 🔍 Why This Works (3 lines max)
`curried` keeps the collected arguments in a closure and compares their count with `fn.length`. Each partial call returns a new function, so every step is a reusable, pre-configured function.
हिंदी: Closure पहले के arguments याद रखता है; जब ज़रूरी arguments पूरे हों तभी असली function चलता है।

---

## ⚡ Alternative Solution
```javascript
// Manual currying with arrow functions (fixed arity, no helper needed)
const discount = (rate) => (price) => price - price * rate; // two-step function
const tenOff = discount(0.1);                                // preset 10% discount
console.log(tenOff(200));                                    // 180
console.log([100, 50].map(tenOff));                          // [ 90, 45 ] — works great with map
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: currying a function with default/rest params (fn.length is 0 or short)
const bad = curry((a, b = 2) => a + b);
// bad(1) runs immediately because fn.length === 1

// ✅ Correct: use explicit params, or pass arity: curryN(fn, 2)
const good = curry((a, b) => a + b);
console.log(good(1)(2)); // 3
```

---

## 🎯 Interview Tip (1 line)
Say: "Currying lets me pre-fill arguments to build specialised functions like `logError` or `usersApi` — and it's built on closures plus `fn.length`."

---

## 🔗 Related Questions
→ Q084 (implement curry) | Q088 (partial application) | Q143 (complete curry) | Q161 (closure)
