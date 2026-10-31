---

# Q074. Get Value by Path String
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `get(obj, path, defaultValue)` that reads a nested value using a path like `'a.b[0].c'`. Return `defaultValue` if any part is missing (like lodash `_.get`).

```javascript
get({ a: { b: [{ c: 5 }] } }, 'a.b[0].c'); // 5
```

---

## 💡 Quick Concept (2 lines only)
Convert the path into a list of keys, then walk down the object one key at a time, stopping safely on null/undefined.
हिंदी: path को keys की list में बदलो और एक-एक करके object में नीचे उतरो, बीच में undefined मिले तो रुक जाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: turn 'a.b[0].c' into ['a','b','0','c']
// Step 2: walk keys with a loop
// Step 3: return default if value missing

function get(obj, path, defaultValue) {
  const keys = path.replace(/\[(\w+)\]/g, '.$1').split('.').filter(Boolean); // normalize brackets then split
  let current = obj;                                   // start at root
  for (const key of keys) {                            // each path segment
    if (current === null || current === undefined) return defaultValue; // can't go deeper
    current = current[key];                            // step into key
  }
  return current === undefined ? defaultValue : current; // fallback if missing
}

// ============================================
// TEST CASES
// ============================================

const data = { a: { b: [{ c: 5 }], z: 0 } };
console.log(get(data, 'a.b[0].c'));        // Expected: 5
console.log(get(data, 'a.z', 'none'));     // Expected: 0
console.log(get(data, 'a.x.y', 'none'));   // Expected: none
console.log(get(data, 'a.b[3].c', null));  // Expected: null
```

---

## 🔍 Why This Works (3 lines max)
Replacing `[0]` with `.0` lets one `split('.')` handle objects and arrays. Checking for null/undefined before each step prevents "cannot read property of undefined" errors.
हिंदी: [0] को .0 बनाकर एक ही split चलता है, और हर step पर null check से crash नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// Optional chaining works only when the path is fixed at write-time
console.log(data?.a?.b?.[0]?.c ?? 'none'); // Expected: 5
// reduce version
const get2 = (o, p, d) =>
  p.replace(/\[(\w+)\]/g, '.$1').split('.').reduce((acc, k) => acc?.[k], o) ?? d; // safe walk + default
console.log(get2(data, 'a.b[0].c', 'none')); // Expected: 5
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using || for default hides valid falsy values like 0
console.log(0 || 'none'); // 'none'  (0 lost)
// ✅ Correct: only treat undefined as missing
console.log(get(data, 'a.z', 'none')); // 0
```

---

## 🎯 Interview Tip (1 line)
Show you handle bracket notation, missing keys, and falsy-but-valid values like 0.

---

## 🔗 Related Questions
→ Q073 (flatten object) | Q075 (omit keys) | Q039 (optional chaining output)
