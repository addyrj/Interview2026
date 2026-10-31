---

# Q264. Strategy Pattern
# Category: Design Patterns
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `Cart` whose discount algorithm can be swapped at runtime (none, percent, flat) without if/else chains.

---

## 💡 Quick Concept (2 lines only)
Strategy puts interchangeable algorithms behind the same interface and lets you pick one at runtime.
हिंदी: Strategy में algorithm को function की तरह बदल सकते हैं, if/else की जरूरत नहीं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Each strategy is a function (total) => newTotal
// Step 2: Cart holds the current strategy
// Step 3: checkout() delegates to the strategy

const strategies = {
  none: (t) => t,                          // no discount
  percent10: (t) => t * 0.9,               // 10% off
  flat50: (t) => Math.max(0, t - 50),      // 50 off but never negative
};

class Cart {
  constructor(items, strategy = strategies.none) {
    this.items = items;                    // array of prices
    this.strategy = strategy;              // current discount strategy
  }
  setStrategy(s) { this.strategy = s; }    // swap at runtime
  checkout() {
    const total = this.items.reduce((a, b) => a + b, 0); // sum prices
    return this.strategy(total);           // delegate to strategy
  }
}

// ============================================
// TEST CASES
// ============================================

const cart = new Cart([100, 100]);         // total = 200
console.log(cart.checkout());              // Expected: 200
cart.setStrategy(strategies.percent10);    // switch strategy
console.log(cart.checkout());              // Expected: 180
cart.setStrategy(strategies.flat50);       // switch again
console.log(cart.checkout());              // Expected: 150
```

---

## 🔍 Why This Works (3 lines max)
The Cart never knows how a discount is computed; it only calls the strategy. New discounts are added without modifying Cart.
हिंदी: Cart सिर्फ strategy को call करता है, गणना कैसे होती है उसे पता नहीं।

---

## ⚡ Alternative Solution
```javascript
// Pass the strategy per call
const checkout = (items, discount) => discount(items.reduce((a, b) => a + b, 0)); // compute with given discount
console.log(checkout([10, 20], (t) => t / 2)); // Expected: 15
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: switch(type) inside checkout — must edit it for every new discount
// ✅ Correct: inject a function/object per algorithm
```

---

## 🎯 Interview Tip (1 line)
In JS, strategies are just first-class functions — e.g. the comparator passed to `Array.sort`.

---

## 🔗 Related Questions
→ Q262 (Factory) | Q275 (Template method) | Q065 (Sort objects)
