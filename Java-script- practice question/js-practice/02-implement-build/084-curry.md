---

# Q084. Implement Curry
# Category: Implement / Build
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Implement a `curry(fn)` function. A curried function can be called with fewer arguments than it expects — it returns a new function for the remaining arguments. Only executes when all arguments are provided.

```javascript
function add(a, b, c) { return a + b + c; }
const curriedAdd = curry(add);

curriedAdd(1)(2)(3);  // 6
curriedAdd(1, 2)(3);  // 6
curriedAdd(1)(2, 3);  // 6
curriedAdd(1, 2, 3);  // 6
```

---

## 💡 Quick Concept (2 lines only)
Curry transforms a multi-argument function into a sequence of single-argument functions. If called with fewer args than expected, returns a partial function waiting for the rest.
हिंदी: Curry multi-argument function को chain of single-argument functions में convert करता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function curry(fn) {
  // Step 1: return a function that collects arguments
  return function curried(...args) {
    // Step 2: if we have enough arguments, call the original function
    if (args.length >= fn.length) {
      return fn.apply(this, args);
    }
    // Step 3: otherwise, return a function that collects more arguments
    return function(...moreArgs) {
      return curried.apply(this, args.concat(moreArgs));
    };
  };
}

// ============================================
// TEST CASES
// ============================================

function add(a, b, c) { return a + b + c; }
const curriedAdd = curry(add);

console.log(curriedAdd(1)(2)(3));    // Expected: 6
console.log(curriedAdd(1, 2)(3));    // Expected: 6
console.log(curriedAdd(1)(2, 3));    // Expected: 6
console.log(curriedAdd(1, 2, 3));    // Expected: 6

// Real-world use case: reusable validators
function validate(minLen, maxLen, str) {
  return str.length >= minLen && str.length <= maxLen;
}
const curriedValidate = curry(validate);

const isValidUsername = curriedValidate(3)(20);  // preset min=3, max=20
console.log(isValidUsername('Arjun'));   // true (5 chars)
console.log(isValidUsername('AB'));      // false (2 chars)
console.log(isValidUsername('a'.repeat(25))); // false (25 chars)

// Partial application with curry:
const add10 = curriedAdd(10);       // preset a=10
const add10and20 = curriedAdd(10, 20);  // preset a=10, b=20

console.log(add10(5)(3));    // 18 (10+5+3)
console.log(add10and20(7));  // 37 (10+20+7)
```

---

## 🔍 Why This Works (3 lines max)
`fn.length` returns the number of expected parameters. If collected args >= fn.length, call the function. Otherwise, return a new function that concatenates new args with already-collected args and calls curried again.
हिंदी: `fn.length` से expected args का count पता चलता है — पूरे args मिलें तो call करो, नहीं तो और args के लिए function return करो।

---

## ⚡ Alternative Solution
```javascript
// Arrow function version (shorter):
const curry = fn => {
  const curried = (...args) =>
    args.length >= fn.length
      ? fn(...args)
      : (...more) => curried(...args, ...more);
  return curried;
};

// Curry with placeholder support (advanced):
const _ = Symbol('placeholder');  // placeholder symbol

function curryWithPlaceholder(fn) {
  const arity = fn.length;
  
  return function curried(...args) {
    const filled = args.filter(a => a !== _);
    
    if (filled.length >= arity) {
      return fn(...filled);
    }
    
    return function(...newArgs) {
      let ni = 0;
      const merged = args.map(a => a === _ && ni < newArgs.length ? newArgs[ni++] : a);
      return curried(...merged, ...newArgs.slice(ni));
    };
  };
}

// Usage with placeholder:
const multiply = (a, b, c) => a * b * c;
const cm = curryWithPlaceholder(multiply);
cm(_, 2, _)(3, 4);  // 3 * 2 * 4 = 24 (placeholders filled left to right)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: only handling one argument at a time
function curry(fn) {
  return function(a) {
    return function(b) {
      return function(c) {
        return fn(a, b, c);  // hard-coded 3 args — not general!
      };
    };
  };
}

// ✅ Correct: use fn.length to handle any number of args dynamically

// ❌ Wrong: not handling rest args properly
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) return fn(...args);
    return (...more) => curried(...args, ...more);  // don't use apply, args is already spread
  };
}
// Actually this is fine — both spread and apply work

// ❌ Wrong: forgetting that arrow functions have fn.length = 0 for ...rest
const fn = (...args) => args.reduce((a,b) => a+b, 0);
console.log(fn.length);  // 0 — curry won't work with rest params!
```

---

## 🎯 Interview Tip (1 line)
Say: "Curry enables partial application — preset some args, get a specialized function; real use: validators, API callers, event handlers with preset config."

---

## 🔗 Related Questions
→ Q085 (compose) | Q086 (pipe) | Q088 (partial application) | Q083 (memoize) | Q306 (currying real use case)
