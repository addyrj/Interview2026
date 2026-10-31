---

# Q258. Object.fromEntries
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use `Object.fromEntries` with `Object.entries` to transform, filter and rebuild objects; also convert Map and URLSearchParams.

---

## 💡 Quick Concept (2 lines only)
`Object.fromEntries(iterable)` builds an object from `[key, value]` pairs — the reverse of `Object.entries`.
हिंदी: `fromEntries` [key, value] pairs की list से वापस object बनाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: object -> entries (array of pairs)
// Step 2: map/filter the pairs
// Step 3: fromEntries -> object

const prices = { apple: 10, banana: 5, cherry: 20 }; // sample data

// 1. Basic: pairs to object
console.log(Object.fromEntries([['a', 1], ['b', 2]])); // Expected: { a: 1, b: 2 }

// 2. Transform values (double)
const doubled = Object.fromEntries(
  Object.entries(prices).map(([k, v]) => [k, v * 2]) // change each value
);
console.log(doubled);                            // Expected: { apple: 20, banana: 10, cherry: 40 }

// 3. Filter keys by value
const expensive = Object.fromEntries(
  Object.entries(prices).filter(([, v]) => v > 8) // keep price > 8
);
console.log(expensive);                          // Expected: { apple: 10, cherry: 20 }

// 4. Transform keys (uppercase)
const upper = Object.fromEntries(
  Object.entries(prices).map(([k, v]) => [k.toUpperCase(), v]) // rename keys
);
console.log(upper);                              // Expected: { APPLE: 10, BANANA: 5, CHERRY: 20 }

// 5. Map -> object
console.log(Object.fromEntries(new Map([['x', 1]]))); // Expected: { x: 1 }

// 6. Query string -> object
console.log(Object.fromEntries(new URLSearchParams('q=js&page=2'))); // Expected: { q: 'js', page: '2' }

// ============================================
// TEST CASES
// ============================================

console.log(Object.fromEntries([]));             // Expected: {}
console.log(Object.fromEntries([['k', 1], ['k', 2]])); // Expected: { k: 2 }  (later wins)
console.log(Object.fromEntries(Object.entries({ a: 1 })));  // Expected: { a: 1 }
console.log(Object.fromEntries('ab'.split('').map((c, i) => [c, i]))); // Expected: { a: 0, b: 1 }
```

---

## 🔍 Why This Works (3 lines max)
`entries` turns an object into an array so you can use `map/filter/reduce`, then `fromEntries` turns it back. Duplicate keys overwrite earlier ones.
हिंदी: Object को array बनाओ, map/filter करो, फिर `fromEntries` से वापस object बना लो।

---

## ⚡ Alternative Solution
```javascript
// Same transform using reduce
const doubledR = Object.entries(prices).reduce((acc, [k, v]) => {
  acc[k] = v * 2;                                // build manually
  return acc;                                    // pass accumulator
}, {});
console.log(doubledR.apple);                     // Expected: 20
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: map returns values, not pairs
// Object.fromEntries(Object.entries(prices).map(([k, v]) => v * 2));  // TypeError

// ✅ Correct: return [key, value] pairs
console.log(Object.fromEntries(Object.entries({ a: 1 }).map(([k, v]) => [k, v + 1]))); // Expected: { a: 2 }
```

---

## 🎯 Interview Tip (1 line)
Say: "entries -> map/filter -> fromEntries is the idiomatic way to transform, pick or omit object keys."

---

## 🔗 Related Questions
→ Q075 (omit keys) | Q076 (pick keys) | Q080 (transform object keys) | Q246 (Map)
