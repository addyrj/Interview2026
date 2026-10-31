---

# Q198. Build Query String Builder
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `buildQuery(params)` that converts an object to a query string: encode keys/values, skip `null`/`undefined`, repeat keys for arrays (`tag=a&tag=b`), and use bracket notation for nested objects (`user[name]=Adi`).

```javascript
buildQuery({ q: 'js tips', page: 2, tags: ['a', 'b'] }); // "q=js%20tips&page=2&tags=a&tags=b"
```

---

## 💡 Quick Concept (2 lines only)
Recursively walk the object, collecting `encode(key)=encode(value)` pairs, then join with `&`.
हिंदी: Object पर recursion चलाओ, हर key-value को encode करो और `&` से जोड़ दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function buildQuery(params) {
  const pairs = [];                              // Step 1: collects "k=v" strings

  function walk(key, value) {
    if (value === undefined || value === null) return; // Step 2: skip empty values
    if (Array.isArray(value)) {
      value.forEach((v) => walk(key, v));        // Step 3: arrays repeat the same key
    } else if (typeof value === 'object') {
      Object.keys(value).forEach((k) => walk(`${key}[${k}]`, value[k])); // Step 4: nested -> brackets
    } else {
      pairs.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`); // Step 5: encode leaf
    }
  }

  Object.keys(params).forEach((k) => walk(k, params[k])); // start from top-level keys
  return pairs.join('&');                        // join all pairs
}

// ============================================
// TEST CASES
// ============================================

console.log(buildQuery({ q: 'js tips', page: 2, tags: ['a', 'b'] }));
// Expected: q=js%20tips&page=2&tags=a&tags=b
console.log(buildQuery({ user: { name: 'Adi', age: 25 }, skip: undefined, none: null }));
// Expected: user%5Bname%5D=Adi&user%5Bage%5D=25
console.log(buildQuery({ flag: false, zero: 0, text: 'a&b=c' }));
// Expected: flag=false&zero=0&text=a%26b%3Dc
console.log(buildQuery({}));                     // Expected: (empty string)
```

---

## 🔍 Why This Works (3 lines max)
`encodeURIComponent` escapes `& = space` so values cannot break the string. Recursion handles any nesting depth, and falsy-but-valid values like `0`/`false` are kept.
हिंदी: encode करने से `&` और `=` जैसे characters string नहीं तोड़ते, और `0`/`false` भी सुरक्षित रहते हैं।

---

## ⚡ Alternative Solution
```javascript
// Built-in for flat objects
const qs = new URLSearchParams({ q: 'js tips', page: 2 }).toString(); // "q=js+tips&page=2"
// Arrays: params.append('tags','a'); params.append('tags','b');
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: truthy check drops 0 and false; no encoding breaks on '&'
if (value) pairs.push(`${key}=${value}`);

// ✅ Correct: check null/undefined only, and always encodeURIComponent
if (value != null) pairs.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
```

---

## 🎯 Interview Tip (1 line)
Point out `encodeURI` vs `encodeURIComponent`, and that array/nested formats are conventions the backend must agree on.

---

## 🔗 Related Questions
→ Q197 (URL parser) | Q073 (flatten nested object) | Q189 (SPA router) | Q183 (retry API call)
