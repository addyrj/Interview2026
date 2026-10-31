---

# Q042. Destructuring Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const { a, b = 5, c: renamed = 7 } = { a: 1, c: undefined };
const [x, , y = 3, ...z] = [10, 20, undefined, 40, 50];
console.log(a, b, renamed);
console.log(x, y, z);
```

---

## 💡 Quick Concept (2 lines only)
Destructuring unpacks values; defaults apply only when the value is `undefined` (not null). `key: name` renames.
हिंदी: Destructuring में default सिर्फ undefined पर लगता है, और key: name से नाम बदला जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: a = 1 from the object
// Step 2: b missing -> default 5
// Step 3: c is undefined -> default 7, stored as `renamed`
// Step 4: array: x=10, skip 20, y undefined -> default 3, z gets the rest

const { a, b = 5, c: renamed = 7 } = { a: 1, c: undefined }; // object destructuring
const [x, , y = 3, ...z] = [10, 20, undefined, 40, 50];      // array destructuring
console.log(a, b, renamed); // 1 5 7
console.log(x, y, z);       // 10 3 [ 40, 50 ]

// ============================================
// TEST CASES
// ============================================

const { p = 1 } = { p: null };        // null is NOT undefined
console.log(p);                       // Expected: null
let m = 1, n = 2;                     // two variables
[m, n] = [n, m];                      // swap without temp
console.log(m, n);                    // Expected: 2 1
const { length } = 'hello';           // destructure a string
console.log(length);                  // Expected: 5
const { u: { v } } = { u: { v: 'deep' } }; // nested pattern
console.log(v);                       // Expected: deep

// ============================================
// OUTPUT:
// ============================================
// 1 5 7
// 10 3 [ 40, 50 ]
// null
// 2 1
// 5
// deep
```

---

## 🔍 Why This Works (3 lines max)
Patterns mirror the data shape; each target is assigned the matching value. Defaults trigger only for `undefined`, so `null`, 0 and "" are kept.
हिंदी: Pattern data की shape से मेल खाता है; null, 0 या "" पर default नहीं लगता।

---

## ⚡ Alternative Solution
```javascript
// Destructure directly in function parameters with defaults
const show = ({ name = 'Guest', age = 0 } = {}) => `${name}:${age}`; // safe default object
console.log(show({ name: 'A' })); // A:0
console.log(show());              // Guest:0
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: destructuring null/undefined throws
try {
  const { name } = null;
} catch (e) {
  console.log(e.name); // TypeError
}

// ✅ Correct: provide a fallback
const { name } = null ?? {};
console.log(name); // undefined
```

---

## 🎯 Interview Tip (1 line)
Say: "Defaults apply only for undefined, and I give function params a default {} so destructuring never throws."

---

## 🔗 Related Questions
→ Q043 (default parameter) | Q041 (rest parameter) | Q178 (destructuring tricks)
