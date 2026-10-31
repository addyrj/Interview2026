---

# Q176. Explain Optional Chaining
# Category: Tricky Concepts
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain the optional chaining operator `?.` for property access, method calls and array indexes. What does it return and when does it short-circuit?

---

## 💡 Quick Concept (2 lines only)
`a?.b` returns `undefined` instead of throwing if `a` is `null` or `undefined`, and the rest of the chain is skipped. It works for `a?.b`, `a?.[i]` and `a?.()`.
हिंदी: `?.` में अगर बीच का value null/undefined हो तो error की जगह undefined मिलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Put ?. before the access that might fail
// Step 2: If left side is null/undefined -> whole chain gives undefined
// Step 3: Combine with ?? for default values

const user = {
  name: 'Aditya',                              // simple field
  address: { city: 'Delhi' },                  // nested object
  greet() { return 'hello'; },                 // method
  tags: ['js']                                 // array
};

console.log(user.address?.city);               // Delhi
console.log(user.profile?.age);                // undefined (no throw)
console.log(user.profile?.address.city);       // undefined (short-circuits whole chain)
console.log(user.greet?.());                   // hello
console.log(user.fly?.());                     // undefined (method missing)
console.log(user.tags?.[0]);                   // js
console.log(user.nothing?.[0]);                // undefined

// Falsy but valid values are NOT skipped
const cfg = { count: 0, label: '' };           // falsy values
console.log(cfg.count?.toString());            // "0"  (0 is not null/undefined)
console.log(cfg.label?.length);                // 0

// Default with nullish coalescing
console.log(user.profile?.age ?? 'unknown');   // unknown

// Without optional chaining
try { user.profile.age; } catch (e) { console.log(e.name); } // TypeError

// Works with delete and short-circuit side effects
let calls = 0;                                 // counter
const nothing = null;                          // null object
nothing?.[calls++];                            // not evaluated
console.log(calls);                            // 0

// ============================================
// TEST CASES
// ============================================
// Expected output:
// Delhi
// undefined
// undefined
// hello
// undefined
// js
// undefined
// 0
// 0
// unknown
// TypeError
// 0
```

---

## 🔍 Why This Works (3 lines max)
The operator checks only for `null`/`undefined` (not all falsy values). On a hit, evaluation of the entire remaining chain stops and `undefined` is produced.
हिंदी: यह सिर्फ null/undefined चेक करता है, और मिलते ही पूरी chain रोक देता है।

---

## ⚡ Alternative Solution
```javascript
// Old way: && chains
const city = user && user.address && user.address.city; // verbose
console.log(city);                             // Expected: Delhi
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Overusing ?. hides real bugs and can't be used on assignment
// user?.name = 'x';  // SyntaxError

// ✅ Use only where data is truly optional; check before assigning
if (user) user.name = 'x';
```

---

## 🎯 Interview Tip (1 line)
Say: "?. guards null/undefined only, short-circuits the whole chain, and pairs with ?? for defaults."

---

## 🔗 Related Questions
→ Q039 (optional chaining output) | Q177 (nullish coalescing) | Q255 (optional chaining tricks) | Q140 (null/undefined bug)
