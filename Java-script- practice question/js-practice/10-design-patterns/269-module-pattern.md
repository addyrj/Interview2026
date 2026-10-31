---

# Q269. Module Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use an IIFE to build a `counter` module with private state and a public API. Show that private data cannot be accessed directly.

---

## 💡 Quick Concept (2 lines only)
Module pattern uses an IIFE + closure to create private variables and expose only a public interface.
हिंदी: IIFE और closure से private data बनता है, बाहर सिर्फ चुने हुए methods दिखते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Wrap code in an IIFE
// Step 2: Declare private variables/functions inside
// Step 3: Return an object with public methods

const counter = (function () {
  let count = 0;                          // private state (closure)

  function log(msg) {                     // private helper
    return `[counter] ${msg}`;
  }

  return {                                // public API
    increment() { count++; return log(`now ${count}`); }, // changes private state
    decrement() { count--; return log(`now ${count}`); }, // changes private state
    get value() { return count; },        // read-only access
  };
})();                                     // invoked immediately

// ============================================
// TEST CASES
// ============================================

console.log(counter.increment());         // Expected: [counter] now 1
console.log(counter.increment());         // Expected: [counter] now 2
console.log(counter.decrement());         // Expected: [counter] now 1
console.log(counter.value);               // Expected: 1
console.log(counter.count);               // Expected: undefined (private)
console.log(typeof counter.log);          // Expected: undefined
```

---

## 🔍 Why This Works (3 lines max)
Variables inside the IIFE are in a function scope that only the returned methods close over. Nothing outside can reach them.
हिंदी: Closure की वजह से सिर्फ returned methods ही private variables तक पहुंच सकते हैं।

---

## ⚡ Alternative Solution
```javascript
// Modern: class with private fields
class Counter {
  #count = 0;                               // truly private
  inc() { return ++this.#count; }           // public method
}
const c = new Counter();                    // instance
c.inc();                                    // 1
console.log(c.inc());                       // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: exposing the variable by returning it by value and expecting live updates
// return { count };   // copy at return time, stays 0

// ✅ Correct: use a getter / method that reads the closure variable
```

---

## 🎯 Interview Tip (1 line)
Say ES modules replaced this pattern, but it is the foundation of closures and encapsulation in old code.

---

## 🔗 Related Questions
→ Q270 (Revealing module) | Q161 (Closure) | Q305 (IIFE use case)
