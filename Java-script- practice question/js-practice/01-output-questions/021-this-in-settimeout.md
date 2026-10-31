---

# Q021. this in setTimeout
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print (Node.js)?

```javascript
const obj = {
  name: 'A',
  run() {
    setTimeout(function () { console.log(this.name); }, 0);
    setTimeout(() => console.log(this.name), 0);
    setTimeout(function () { console.log(this.name); }.bind(this), 0);
  },
};
obj.run();
```

---

## 💡 Quick Concept (2 lines only)
A regular function passed to `setTimeout` is not called as a method of `obj`, so it loses `this`; arrows and `bind` keep it.
हिंदी: setTimeout में दिया regular function obj का method बनकर call नहीं होता, इसलिए this खो देता है; arrow या bind इसे बचाते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: regular callback -> this is the Timeout object (window in browsers)
// Step 2: arrow callback -> inherits run's this = obj
// Step 3: bind(this) forces this = obj

const obj = {
  name: 'A',                                       // property
  run() {
    setTimeout(function () {
      console.log(this.name);                      // Timeout object has no name
    }, 0);
    setTimeout(() => console.log(this.name), 0);   // lexical this -> obj
    setTimeout(function () {
      console.log(this.name);                      // bound to obj
    }.bind(this), 0);
  },
};
obj.run();                                         // schedule all three

// ============================================
// TEST CASES
// ============================================

// Output order (timers fire in creation order):
// undefined
// A
// A
```

---

## 🔍 Why This Works (3 lines max)
Timers invoke callbacks as plain functions, so `this` is not obj. Arrow functions take `this` from `run`, and `bind` fixes it explicitly. In browsers the first one reads `window.name` (usually an empty string).
हिंदी: Browser में पहला callback window.name पढ़ता है (अक्सर खाली string), Node में undefined।

---

## ⚡ Alternative Solution
```javascript
// Old-school: save this in a variable
const o2 = {
  name: 'B',
  run() {
    const self = this;                             // keep reference
    setTimeout(function () { console.log(self.name); }, 10); // Expected: B
  },
};
o2.run();
```

---

## ⚠️ Common Mistake
```javascript
// ❌ setTimeout(function () { this.count++ }, 0)  // this is not your object
// ✅ Use an arrow function inside the method
```

---

## 🎯 Interview Tip (1 line)
Say: "Callbacks are called without a receiver; use arrow, bind, or a self variable to keep this."

---

## 🔗 Related Questions
→ Q018 (this regular function) | Q019 (this arrow) | Q022 (this in event listener) | Q124 (fix this binding bug)
