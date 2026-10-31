---

# Q143. Complete Curry Function
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks so `curry(fn)` lets you call `f(1)(2)(3)`, `f(1, 2)(3)` etc.

```javascript
function curry(fn) {
  return function curried(...args) {
    if (args.length ____ fn.____) {       // enough arguments collected?
      return fn.apply(this, ____);        // call original
    }
    return function (...next) {           // otherwise wait for more
      return curried.apply(this, args.____(next));
    };
  };
}
```

---

## 💡 Quick Concept (2 lines only)
Currying turns `f(a, b, c)` into `f(a)(b)(c)`. Keep collecting arguments until you have `fn.length` of them.
हिंदी: Currying में arguments धीरे-धीरे जमा होते हैं और पूरे होने पर function चलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function curry(fn) {
  return function curried(...args) {            // Step 1: collect args so far
    if (args.length >= fn.length) {             // blanks 1+2: enough args (fn.length = arity)
      return fn.apply(this, args);              // blank 3: run original
    }
    return function (...next) {                 // Step 2: need more args
      return curried.apply(this, args.concat(next)); // blank 4: merge and retry
    };
  };
}

// ============================================
// TEST CASES
// ============================================

const add = (a, b, c) => a + b + c;             // 3-arg function
const f = curry(add);                           // curried version
console.log(f(1)(2)(3));                        // Expected: 6
console.log(f(1, 2)(3));                        // Expected: 6
console.log(f(1)(2, 3));                        // Expected: 6
```

---

## 🔍 Why This Works (3 lines max)
`fn.length` is the number of declared parameters. Each call appends arguments; once enough exist the real function runs.
हिंदी: `fn.length` parameters की संख्या बताता है; पूरे arguments मिलते ही असली function चलता है।

---

## ⚡ Alternative Solution
```javascript
// Compact arrow version
const curry2 = (fn, ...a) => (a.length >= fn.length ? fn(...a) : (...b) => curry2(fn, ...a, ...b));
console.log(curry2(add)(1)(2)(3)); // 6
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: default/rest params make fn.length smaller
// const g = (a, b = 2) => a + b;  // g.length === 1
// ✅ Correct: pass arity explicitly if needed: curry(fn, arity)
```

---

## 🎯 Interview Tip (1 line)
Say: "Curry compares collected args with fn.length — useful for reusable partial functions like logger('error')."

---

## 🔗 Related Questions
→ Q084 (implement curry) | Q088 (partial application) | Q306 (currying use case)
