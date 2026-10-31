---

# Q076. Pick Keys From Object
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement `pick(obj, keys)` that returns a NEW object containing only the listed keys.
Keys that don't exist in `obj` should be ignored. Original object must not change.

```javascript
pick({ a: 1, b: 2, c: 3 }, ['a', 'c']); // { a: 1, c: 3 }
```

---

## 💡 Quick Concept (2 lines only)
Loop over the wanted keys and copy only those that exist in the source object. Opposite of `omit` (Q075).
हिंदी: pick सिर्फ चुनी हुई keys वाला नया object बनाता है, original object वैसा ही रहता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: accept object and array of keys to keep
// Step 2: create an empty result object
// Step 3: copy a key only if it exists as OWN property
// Step 4: return the new object

function pick(obj, keys) {
  const result = {};                                   // new object to hold picked keys
  for (const key of keys) {                            // go through every wanted key
    if (Object.prototype.hasOwnProperty.call(obj, key)) { // check key exists on obj itself
      result[key] = obj[key];                          // copy the value
    }
  }
  return result;                                       // return the picked object
}

// ============================================
// TEST CASES
// ============================================

const user = { id: 1, name: 'Aditya', age: 25, role: 'dev' }; // sample data

console.log(pick(user, ['name', 'age']));  // Expected: { name: 'Aditya', age: 25 }
console.log(pick(user, ['name', 'xyz']));  // Expected: { name: 'Aditya' }
console.log(pick(user, []));               // Expected: {}
console.log(user.id);                      // Expected: 1  (original untouched)
```

---

## 🔍 Why This Works (3 lines max)
We build a fresh object so the original is never mutated. `hasOwnProperty` skips missing keys and inherited ones.
हिंदी: हम नया object बनाते हैं और सिर्फ मौजूद keys copy करते हैं, इसलिए original safe रहता है।

---

## ⚡ Alternative Solution
```javascript
// Functional one-liner using reduce
const pick2 = (obj, keys) =>
  keys.reduce((acc, k) => {            // loop over keys with accumulator
    if (k in obj) acc[k] = obj[k];     // copy if key exists
    return acc;                        // pass accumulator forward
  }, {});

// Or using Object.fromEntries
const pick3 = (obj, keys) =>
  Object.fromEntries(keys.filter(k => k in obj).map(k => [k, obj[k]]));

console.log(pick2({ a: 1, b: 2 }, ['a'])); // Expected: { a: 1 }
console.log(pick3({ a: 1, b: 2 }, ['b'])); // Expected: { b: 2 }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: adds undefined for missing keys
function badPick(obj, keys) {
  const r = {};
  keys.forEach(k => { r[k] = obj[k]; }); // { name: 'x', xyz: undefined }
  return r;
}

// ✅ Correct: check the key exists before copying
function goodPick(obj, keys) {
  const r = {};
  keys.forEach(k => { if (k in obj) r[k] = obj[k]; });
  return r;
}
```

---

## 🎯 Interview Tip (1 line)
Say: "I return a new object (immutability) and skip missing keys instead of creating `undefined` entries."

---

## 🔗 Related Questions
→ Q075 (omit keys) | Q072 (merge objects) | Q080 (transform keys)
