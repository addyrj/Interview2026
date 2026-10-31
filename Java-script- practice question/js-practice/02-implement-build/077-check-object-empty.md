---

# Q077. Check If Object Is Empty
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `isEmpty(obj)` that returns `true` if a plain object has no own enumerable keys.
Handle `null`/`undefined` safely.

```javascript
isEmpty({});        // true
isEmpty({ a: 1 }); // false
```

---

## 💡 Quick Concept (2 lines only)
An object is empty when `Object.keys(obj).length === 0`. Guard against `null` first, otherwise it throws.
हिंदी: Object खाली तब है जब उसमें कोई own key नहीं है — पहले null check ज़रूर करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: return true for null / undefined (nothing inside)
// Step 2: make sure value is really a plain object
// Step 3: count own enumerable keys
// Step 4: empty if count is 0

function isEmpty(obj) {
  if (obj === null || obj === undefined) return true;      // nothing to check
  if (typeof obj !== 'object') return false;               // numbers/strings are not "empty objects"
  return Object.keys(obj).length === 0;                    // no own keys => empty
}

// ============================================
// TEST CASES
// ============================================

console.log(isEmpty({}));            // Expected: true
console.log(isEmpty({ a: 1 }));      // Expected: false
console.log(isEmpty(null));          // Expected: true
console.log(isEmpty({ a: undefined })); // Expected: false (key exists)
console.log(isEmpty([]));            // Expected: true (array with no items)
```

---

## 🔍 Why This Works (3 lines max)
`Object.keys` returns only own enumerable keys, so zero length means nothing is stored. The null guard avoids a TypeError.
हिंदी: Object.keys की length 0 मतलब object खाली; null guard से error नहीं आता।

---

## ⚡ Alternative Solution
```javascript
// for...in with hasOwnProperty exits early (faster for huge objects)
function isEmpty2(obj) {
  for (const key in obj) {                                  // loop over keys
    if (Object.prototype.hasOwnProperty.call(obj, key)) {   // own key found
      return false;                                         // so not empty
    }
  }
  return true;                                              // no keys found
}

console.log(isEmpty2({}));       // Expected: true
console.log(isEmpty2({ x: 1 })); // Expected: false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: comparing with {} checks reference, always false
console.log({} === {});            // false

// ❌ Wrong: JSON.stringify trick fails for Date, undefined values
console.log(JSON.stringify({ a: undefined }) === '{}'); // true (but key exists!)

// ✅ Correct: Object.keys(obj).length === 0
console.log(Object.keys({ a: undefined }).length === 0); // false
```

---

## 🎯 Interview Tip (1 line)
Mention that `{} === {}` is false (reference compare) and that you handle `null`, symbols and arrays as edge cases.

---

## 🔗 Related Questions
→ Q078 (deep equal) | Q079 (count key occurrences) | Q075 (omit keys)
