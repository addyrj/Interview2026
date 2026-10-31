---

# Q270. Revealing Module Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Rewrite a cart module so ALL functions are defined privately and only selected ones are "revealed" at the bottom in a single return object.

---

## 💡 Quick Concept (2 lines only)
Define everything privately, then reveal public names at the end by mapping them to private functions.
हिंदी: सब कुछ private लिखो और आखिर में एक return में चुनिंदा चीजें public कर दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Write all functions privately
// Step 2: Return an object mapping public names to them
// Step 3: Internal calls use private names, not the object

const cart = (function () {
  const items = [];                                  // private data

  function add(name, price) {                        // private function
    items.push({ name, price });                     // mutate private array
    return items.length;                             // return count
  }

  function total() {                                 // private function
    return items.reduce((s, i) => s + i.price, 0);   // sum prices
  }

  function summary() {                               // private, uses other privates
    return `${items.length} items, total ${total()}`; // direct call, not via cart.total
  }

  return { add, total, summary };                    // reveal only these
})();

// ============================================
// TEST CASES
// ============================================

cart.add('pen', 10);                                 // add item
cart.add('book', 40);                                // add item
console.log(cart.total());                           // Expected: 50
console.log(cart.summary());                         // Expected: 2 items, total 50
console.log(cart.items);                             // Expected: undefined
console.log(Object.keys(cart));                      // Expected: [ 'add', 'total', 'summary' ]
```

---

## 🔍 Why This Works (3 lines max)
Functions call each other by their private names, so overriding `cart.total` outside will not break `summary`. The return object is a clear public contract.
हिंदी: Public नाम बाद में बदल भी दो तो अंदर के functions पर असर नहीं पड़ता।

---

## ⚡ Alternative Solution
```javascript
// Same idea with ES module exports (file-level privacy)
// function secret() {}  export function pub() { return secret(); }
const pub = () => 'ok';       // stand-in for an exported function
console.log(pub());           // Expected: ok
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: calling this.total() inside a revealed function; breaks when detached
// const { summary } = cart;  summary();  // `this` is undefined

// ✅ Correct: call private total() directly (see solution)
```

---

## 🎯 Interview Tip (1 line)
Highlight the benefit: consistent, readable public API at the bottom; downside: public overrides don't affect privates.

---

## 🔗 Related Questions
→ Q269 (Module pattern) | Q161 (Closure) | Q305 (IIFE use case)
