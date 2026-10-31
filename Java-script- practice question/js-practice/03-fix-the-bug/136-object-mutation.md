---

# Q136. Fix Object Mutation Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`withDiscount` mutates the original product object. Make it pure (return a new object, leave input unchanged).

```javascript
// BUGGY CODE:
function withDiscount(product) {
  product.price = product.price * 0.9;  // mutates caller's object
  return product;
}
const p = { name: 'Book', price: 100 };
withDiscount(p);
console.log(p.price);                   // 90 (original changed)
```

---

## 💡 Quick Concept (2 lines only)
Objects passed to functions are references, so editing them changes the caller's data. Return a new object using spread instead.
हिंदी: object reference से पास होता है, इसलिए बदलने पर original भी बदलता है — spread से नया object बनाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function withDiscount(product) {
  return { ...product, price: product.price * 0.9 }; // Step 1 (FIX): copy + override price
}

const p = Object.freeze({ name: 'Book', price: 100 }); // Step 2: freeze to catch accidental mutation

// ============================================
// TEST CASES
// ============================================

const d = withDiscount(p);                // new discounted object
console.log(d.price);                     // Expected: 90
console.log(p.price);                     // Expected: 100
console.log(d === p);                     // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
Spread creates a new object, then `price` overrides the copied value. The original is never touched, which is what React state and Redux require.
हिंदी: spread नया object बनाता है और original कभी नहीं बदलता — React state के लिए यही चाहिए।

---

## ⚡ Alternative Solution
```javascript
// Object.assign into an empty object
const withDiscount2 = (p) => Object.assign({}, p, { price: p.price * 0.9 });
console.log(withDiscount2({ price: 200 }).price); // 180
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: spread is shallow, nested objects are still shared
const o = { a: { n: 1 } }; const c = { ...o }; c.a.n = 2;
console.log(o.a.n); // 2
// ✅ Correct: copy nested level too
const c2 = { ...o, a: { ...o.a, n: 3 } };
```

---

## 🎯 Interview Tip (1 line)
Say: "I treat inputs as immutable — return new objects, use Object.freeze in dev to catch mutations."

---

## 🔗 Related Questions
→ Q072 (merge objects) | Q120 (deepFreeze) | Q128 (reference vs value) | Q137 (array mutation)
