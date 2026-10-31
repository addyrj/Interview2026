---

# Q079. Count Key Occurrences
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `countKey(obj, key)` that counts how many times `key` appears anywhere in a deeply nested object (including inside arrays).

```javascript
countKey({ a: 1, b: { a: 2, c: { a: 3 } } }, 'a'); // 3
```

---

## 💡 Quick Concept (2 lines only)
Walk the object recursively; add 1 whenever the current level has the key, then recurse into every object/array value.
हिंदी: Nested object में recursion से चलकर हर level पर key गिनते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: base case — non-objects have 0 keys
// Step 2: count the key at the current level
// Step 3: recurse into every child value
// Step 4: return total

function countKey(obj, key) {
  if (obj === null || typeof obj !== 'object') return 0;   // primitives contain no keys
  let count = 0;                                           // running total
  if (!Array.isArray(obj) && Object.prototype.hasOwnProperty.call(obj, key)) {
    count += 1;                                            // key found at this level
  }
  for (const child of Object.values(obj)) {                // go through every value
    count += countKey(child, key);                         // add counts from deeper levels
  }
  return count;                                            // total occurrences
}

// ============================================
// TEST CASES
// ============================================

const data = { a: 1, b: { a: 2, c: { a: 3 } }, d: [{ a: 4 }, { x: 1 }] }; // sample

console.log(countKey(data, 'a'));      // Expected: 4
console.log(countKey(data, 'x'));      // Expected: 1
console.log(countKey(data, 'zzz'));    // Expected: 0
console.log(countKey(null, 'a'));      // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Each call handles one level and delegates children to itself. Arrays are traversed through `Object.values` but never counted as having the key.
हिंदी: हर call एक level देखती है और बाकी levels के लिए खुद को दोबारा call करती है।

---

## ⚡ Alternative Solution
```javascript
// Iterative version using an explicit stack (no recursion limit)
function countKeyIter(root, key) {
  const stack = [root];                          // start with the root
  let count = 0;                                 // total
  while (stack.length) {                         // until stack empty
    const cur = stack.pop();                     // take next node
    if (cur === null || typeof cur !== 'object') continue; // skip primitives
    if (!Array.isArray(cur) && key in cur) count++;        // count key here
    stack.push(...Object.values(cur));           // queue children
  }
  return count;
}

console.log(countKeyIter({ a: 1, b: { a: 2 } }, 'a')); // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: only checks the top level
const bad = (obj, key) => (key in obj ? 1 : 0);   // misses nested keys

// ❌ Wrong: recursing into null crashes (typeof null === 'object')
// ✅ Correct: guard `obj === null` before Object.values(obj)
```

---

## 🎯 Interview Tip (1 line)
Say: "Recursion with a clear base case; I can convert to an iterative stack to avoid call-stack overflow on deep data."

---

## 🔗 Related Questions
→ Q066 (count occurrences in array) | Q073 (flatten nested object) | Q074 (get value by path)
