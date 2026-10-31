---

# Q080. Transform Object Keys
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `transformKeys(obj, fn)` that returns a new object with every key (deeply) renamed by `fn`.
Example: convert snake_case keys from an API into camelCase.

```javascript
transformKeys({ first_name: 'A', address: { zip_code: 1 } }, toCamel);
// { firstName: 'A', address: { zipCode: 1 } }
```

---

## 💡 Quick Concept (2 lines only)
Loop over entries, apply `fn` to each key, and recurse into nested objects and arrays.
हिंदी: हर key पर function लगाओ और nested objects/arrays में भी यही दोहराओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: arrays => transform each item
// Step 2: non-objects => return as is
// Step 3: for objects => map each key with fn, recurse on value

function transformKeys(value, fn) {
  if (Array.isArray(value)) {                               // handle arrays of objects
    return value.map(item => transformKeys(item, fn));      // transform each element
  }
  if (value === null || typeof value !== 'object') {        // primitives stay unchanged
    return value;
  }
  const result = {};                                        // new object (no mutation)
  for (const [key, val] of Object.entries(value)) {         // loop over entries
    result[fn(key)] = transformKeys(val, fn);               // new key + recursed value
  }
  return result;                                            // transformed copy
}

// helper: snake_case -> camelCase
const toCamel = (s) => s.replace(/_([a-z])/g, (_, c) => c.toUpperCase());

// ============================================
// TEST CASES
// ============================================

const api = { first_name: 'Adi', address: { zip_code: 123 }, tags_list: [{ tag_name: 'js' }] };

console.log(JSON.stringify(transformKeys(api, toCamel)));
// Expected: {"firstName":"Adi","address":{"zipCode":123},"tagsList":[{"tagName":"js"}]}

console.log(JSON.stringify(transformKeys({ a: 1, b: 2 }, k => k.toUpperCase())));
// Expected: {"A":1,"B":2}

console.log(transformKeys(5, toCamel)); // Expected: 5
```

---

## 🔍 Why This Works (3 lines max)
Each key goes through `fn` and each value is processed recursively, so any depth is covered. A new object is returned.
हिंदी: Keys बदलती हैं, values recursion से प्रोसेस होती हैं, और original object नहीं बदलता।

---

## ⚡ Alternative Solution
```javascript
// Shallow version with Object.fromEntries (one level only)
const shallowTransform = (obj, fn) =>
  Object.fromEntries(Object.entries(obj).map(([k, v]) => [fn(k), v]));

console.log(shallowTransform({ a_b: 1 }, k => k.toUpperCase())); // Expected: { A_B: 1 }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: mutating the original object and forgetting arrays
function bad(obj, fn) {
  for (const k in obj) { obj[fn(k)] = obj[k]; delete obj[k]; } // mutation + may delete new key
}

// ✅ Correct: build a new object and handle arrays (see solution)
```

---

## 🎯 Interview Tip (1 line)
Give a real use case: "API snake_case to frontend camelCase" and mention handling arrays and immutability.

---

## 🔗 Related Questions
→ Q073 (flatten object) | Q076 (pick keys) | Q071 (deep clone)
