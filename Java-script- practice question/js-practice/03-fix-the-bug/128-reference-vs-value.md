---

# Q128. Fix Reference vs Value Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Editing `copy.address.city` also changes `original`. Make `copy` independent.

```javascript
// BUGGY CODE:
const original = { name: 'Aman', address: { city: 'Delhi' } };
const copy = { ...original };      // shallow copy
copy.address.city = 'Pune';
console.log(original.address.city); // 'Pune' (unexpected!)
```

---

## 💡 Quick Concept (2 lines only)
Objects are copied by reference. Spread makes a SHALLOW copy — nested objects are still shared. Use `structuredClone` for a deep copy.
हिंदी: spread सिर्फ ऊपरी level copy करता है, अंदर वाले object वही रहते हैं — deep copy करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const original = { name: 'Aman', address: { city: 'Delhi' } }; // Step 1: source object

const copy = structuredClone(original);   // Step 2 (FIX): deep clone, nested object duplicated
copy.address.city = 'Pune';               // Step 3: modify only the copy

// ============================================
// TEST CASES
// ============================================

console.log(original.address.city);       // Expected: Delhi
console.log(copy.address.city);           // Expected: Pune
console.log(original.address === copy.address); // Expected: false
```

---

## 🔍 Why This Works (3 lines max)
`structuredClone` recursively duplicates nested objects, so no reference is shared. Changing the copy cannot affect the original.
हिंदी: structuredClone हर nested object की नई copy बनाता है, इसलिए original सुरक्षित रहता है।

---

## ⚡ Alternative Solution
```javascript
// Copy only the nested level you change
const copy2 = { ...original, address: { ...original.address, city: 'Goa' } };
console.log(original.address.city, copy2.address.city); // Delhi Goa
// JSON trick (loses Date/undefined/functions)
const copy3 = JSON.parse(JSON.stringify(original));
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assignment copies the reference only
const a = { x: 1 }; const b = a; b.x = 2;
console.log(a.x); // 2
// ✅ Correct
const c = { ...a }; c.x = 3;
console.log(a.x); // 2
```

---

## 🎯 Interview Tip (1 line)
Say: "Primitives copy by value, objects by reference; spread/Object.assign are shallow, structuredClone is deep."

---

## 🔗 Related Questions
→ Q071 (deep clone) | Q136 (object mutation) | Q260 (structuredClone) | Q294 (shallow vs deep copy)
