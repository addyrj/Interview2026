---

# Q265. Decorator Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write a `withLogging(fn)` decorator that adds logging around any function without modifying it, and stack it with `withTiming`-style wrappers.

---

## 💡 Quick Concept (2 lines only)
A decorator wraps an object/function to add behavior while keeping the same interface.
हिंदी: Decorator पुराने function को बदले बिना उसके ऊपर नया behavior जोड़ देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Decorator takes a function, returns a function
// Step 2: New function adds extra behavior around the call
// Step 3: Stack decorators by wrapping the result again

function withLogging(fn) {
  return function (...args) {                           // wrapper with same signature
    console.log(`call ${fn.name}(${args.join(', ')})`); // before-hook
    const result = fn.apply(this, args);                // call original
    console.log(`result ${result}`);                    // after-hook
    return result;                                      // preserve return value
  };
}

function withDouble(fn) {
  return (...args) => fn(...args) * 2;                  // modify result
}

function add(a, b) { return a + b; }                    // original function

// ============================================
// TEST CASES
// ============================================

const logged = withLogging(add);                        // decorated once
console.log(logged(2, 3));                              // Expected: call add(2, 3)
                                                        // Expected: result 5
                                                        // Expected: 5
const both = withLogging(withDouble(add));              // decorators stacked
console.log(both(2, 3));                                // Expected: call (2, 3)
                                                        // Expected: result 10
                                                        // Expected: 10
console.log(add(2, 3));                                 // Expected: 5 (original untouched)
```

---

## 🔍 Why This Works (3 lines max)
Functions are first-class, so a higher-order function can wrap them. The wrapper keeps the same signature so decorators compose.
हिंदी: Wrapper का signature वही रहता है, इसलिए decorators एक के ऊपर एक लग सकते हैं।

---

## ⚡ Alternative Solution
```javascript
// Object decorator: add features by composition
const coffee = { cost: () => 5 };                              // base
const withMilk = (c) => ({ cost: () => c.cost() + 2 });        // adds 2
console.log(withMilk(withMilk(coffee)).cost());                // Expected: 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to return result / lose `this`
// const bad = (fn) => (...a) => { fn(...a); };  // returns undefined!

// ✅ Correct: return fn.apply(this, args)
```

---

## 🎯 Interview Tip (1 line)
Mention HOCs in React and Express middleware wrapping are decorator-like.

---

## 🔗 Related Questions
→ Q266 (Proxy) | Q083 (Memoize) | Q085 (Compose)
