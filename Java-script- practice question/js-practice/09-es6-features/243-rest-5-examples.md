---

# Q243. Rest — 5 Examples
# Category: ES6+ Features
# Difficulty: ⭐ Easy

---

## ❓ Question
Show 5 uses of the rest operator (`...`) in functions, array destructuring and object destructuring.

---

## 💡 Quick Concept (2 lines only)
Rest collects the "remaining" items into one real array (or object). It appears in parameters or on the left of destructuring.
हिंदी: Rest बचे हुए सारे elements को इकट्ठा करके एक array/object बना देता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Rest in function parameters
// Step 2: Rest in array / object destructuring
// Step 3: Compare with legacy `arguments`

// 1. Variadic sum using rest parameter
const sum = (...nums) => nums.reduce((t, n) => t + n, 0); // nums is a real array
console.log(sum(1, 2, 3, 4));                    // Expected: 10

// 2. Named param + rest
function tag(label, ...items) {                  // label first, rest after
  return `${label}: ${items.join(',')}`;         // join remaining items
}
console.log(tag('nums', 1, 2, 3));               // Expected: nums: 1,2,3

// 3. Rest in array destructuring
const [head, ...tail] = [1, 2, 3, 4];            // head=1, tail=rest
console.log(head, tail);                         // Expected: 1 [ 2, 3, 4 ]

// 4. Rest in object destructuring (omit a key)
const { password, ...safeUser } = { id: 1, name: 'Ria', password: 'x' }; // drop password
console.log(safeUser);                           // Expected: { id: 1, name: 'Ria' }

// 5. Rest vs arguments object
function legacy() { return Array.isArray(arguments); }   // arguments is array-like
const modern = (...args) => Array.isArray(args);         // rest is a real array
console.log(legacy(1, 2), modern(1, 2));         // Expected: false true

// ============================================
// TEST CASES
// ============================================

console.log(sum());                              // Expected: 0
const [only, ...none] = [1];                     // nothing left for rest
console.log(none);                               // Expected: []
console.log(sum.length);                         // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Rest must be the LAST element of the parameter list or pattern. It gathers every unmatched value into a new array (or object).
हिंदी: Rest हमेशा आखिरी में आता है और बचे हुए सब values ले लेता है।

---

## ⚡ Alternative Solution
```javascript
// Using arguments (old way) converted to array
function oldSum() {
  return Array.from(arguments).reduce((t, n) => t + n, 0); // convert then reduce
}
console.log(oldSum(1, 2, 3));                    // Expected: 6
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: rest not last
// function bad(...a, b) {}   // SyntaxError: Rest parameter must be last

// ✅ Correct: rest at the end
function good(b, ...a) { return [b, a]; }        // rest last
console.log(good(1, 2, 3));                      // Expected: [ 1, [ 2, 3 ] ]
```

---

## 🎯 Interview Tip (1 line)
Say: "Rest collects, spread expands — same `...` syntax, opposite direction."

---

## 🔗 Related Questions
→ Q041 (rest parameter output) | Q179 (spread vs rest) | Q241 (destructuring) | Q242 (spread)
