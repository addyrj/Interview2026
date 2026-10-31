---

# Q073. Flatten Nested Object
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `flattenObject(obj)` that converts a nested object into a single-level object with dot-separated keys.

```javascript
flattenObject({ a: 1, b: { c: 2, d: { e: 3 } } }); // { a: 1, 'b.c': 2, 'b.d.e': 3 }
```

---

## 💡 Quick Concept (2 lines only)
Recurse through the object while carrying a key prefix; write leaf values using the full path.
हिंदी: recursion में path (prefix) साथ रखो और leaf value को पूरे dotted key के साथ लिखो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: walk each key with the current prefix
// Step 2: if value is a plain object -> recurse with longer prefix
// Step 3: else store value under the full path key

function flattenObject(obj, prefix = '', result = {}) {
  for (const key of Object.keys(obj)) {                    // each own key
    const path = prefix ? `${prefix}.${key}` : key;        // build dotted path
    const val = obj[key];                                  // current value
    if (val !== null && typeof val === 'object' && !Array.isArray(val)) {
      flattenObject(val, path, result);                    // go deeper
    } else {
      result[path] = val;                                  // leaf -> store
    }
  }
  return result;                                           // flat object
}

// ============================================
// TEST CASES
// ============================================

console.log(flattenObject({ a: 1, b: { c: 2, d: { e: 3 } } })); // Expected: { a: 1, 'b.c': 2, 'b.d.e': 3 }
console.log(flattenObject({ x: [1, 2], y: null }));             // Expected: { x: [ 1, 2 ], y: null }
console.log(flattenObject({}));                                 // Expected: {}
console.log(flattenObject({ a: { b: { c: { d: 1 } } } }));      // Expected: { 'a.b.c.d': 1 }
```

---

## 🔍 Why This Works (3 lines max)
The prefix grows with each level so every leaf gets a unique path key. A shared `result` object collects all leaves in one traversal.
हिंदी: हर level पर prefix बढ़ता है, इसलिए हर leaf का unique पूरा path बन जाता है।

---

## ⚡ Alternative Solution
```javascript
// reduce + Object.entries version
const flat2 = (o, p = '') =>
  Object.entries(o).reduce((acc, [k, v]) => {
    const key = p ? `${p}.${k}` : k;                                   // build path
    return v && typeof v === 'object' && !Array.isArray(v)
      ? { ...acc, ...flat2(v, key) }                                   // merge nested result
      : { ...acc, [key]: v };                                          // add leaf
  }, {});
console.log(flat2({ a: { b: 1 }, c: 2 })); // Expected: { 'a.b': 1, c: 2 }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: typeof null === 'object' -> recursing into null crashes
// Object.keys(null) // TypeError
// ✅ Correct: check val !== null before recursing
console.log(flattenObject({ a: null })); // { a: null }
```

---

## 🎯 Interview Tip (1 line)
Mention the `typeof null` trap and decide up front how arrays are treated (kept whole vs indexed keys).

---

## 🔗 Related Questions
→ Q059 (deep flatten array) | Q074 (get by path) | Q080 (transform keys)
