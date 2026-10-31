---

# Q255. Optional Chaining Tricks
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show optional chaining (`?.`) tricks: property, bracket, method call, short-circuiting, and combining with `??`.

---

## 💡 Quick Concept (2 lines only)
`?.` stops and returns `undefined` if the left side is `null`/`undefined` instead of throwing a TypeError.
हिंदी: `?.` में अगर बाईं तरफ null/undefined हो तो error की जगह undefined मिलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Safe property access
// Step 2: Safe method / bracket access
// Step 3: Short circuit + defaults

const user = { profile: { name: 'Ria', tags: ['a'] }, greet() { return 'hi'; } }; // sample

// Trick 1: nested property
console.log(user?.profile?.name);                // Expected: Ria
console.log(user?.address?.city);                // Expected: undefined

// Trick 2: bracket access (dynamic keys, arrays)
const key = 'profile';                           // dynamic key
console.log(user?.[key]?.tags?.[0]);             // Expected: a

// Trick 3: optional method call
console.log(user.greet?.());                     // Expected: hi
console.log(user.missing?.());                   // Expected: undefined

// Trick 4: short-circuits the whole chain (args not evaluated)
let n = 0;                                       // counter
const nothing = null;                            // null object
nothing?.method(n++);                            // chain stops, n++ never runs
console.log(n);                                  // Expected: 0

// Trick 5: combine with ?? for defaults
console.log(user?.address?.city ?? 'Unknown');   // Expected: Unknown

// ============================================
// TEST CASES
// ============================================

console.log(null?.x, undefined?.x);              // Expected: undefined undefined
console.log(0?.toFixed(1), ''?.length);          // Expected: 0.0 0   (0 and '' are NOT nullish)
const o = { a: null };                           // property is null
console.log(o.a?.b.c.d);                         // Expected: undefined (whole chain skipped)
console.log(delete nothing?.x);                  // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
When the value before `?.` is nullish, evaluation of the rest of the chain is skipped and the result is `undefined`. Falsy values like `0`, `''`, `false` still continue normally.
हिंदी: सिर्फ null और undefined पर chain रुकती है, 0 या '' पर नहीं।

---

## ⚡ Alternative Solution
```javascript
// Old way: && chain
const city = user && user.address && user.address.city; // verbose guard
console.log(city);                               // Expected: undefined
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: optional chaining on assignment target
// user?.name = 'X';   // SyntaxError

// ✅ Correct: guard then assign
if (user) user.name = 'X';                       // explicit check
console.log(user.name);                          // Expected: X
```

---

## 🎯 Interview Tip (1 line)
Say: "?. only guards null/undefined, short-circuits the entire chain, and pairs with ?? for defaults — don't overuse it and hide real bugs."

---

## 🔗 Related Questions
→ Q039 (optional chaining output) | Q176 (explain optional chaining) | Q256 (nullish coalescing) | Q140 (fix null/undefined)
