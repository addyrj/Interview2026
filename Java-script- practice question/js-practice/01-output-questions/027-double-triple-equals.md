---

# Q027. `==` vs `===` Output (Tricky)
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log(0 == false);
console.log(0 === false);
console.log('' == false);
console.log(null == undefined);
console.log(null === undefined);
console.log(NaN == NaN);
```

---

## 💡 Quick Concept (2 lines only)
`==` does type coercion — converts types to match before comparing. `===` is strict — no coercion, both value AND type must match.
हिंदी: `==` type convert करके compare करता है; `===` type और value दोनों exact match चाहिए।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

console.log(0 == false);        // true  ← false coerces to 0; 0 == 0
console.log(0 === false);       // false ← number vs boolean — different types

console.log('' == false);       // true  ← '' → 0, false → 0; 0 == 0
console.log(null == undefined); // true  ← special case: null == undefined is true
console.log(null === undefined); // false ← different types (null vs undefined)
console.log(NaN == NaN);        // false ← NaN is NEVER equal to anything, even itself

// ============================================
// OUTPUT:
// ============================================
// true
// false
// true
// true
// false
// false
```

---

## 🔍 Why This Works (3 lines max)
`==` coercion rules: boolean → number (false→0, true→1); string → number; null == undefined is a special spec exception. `NaN` is the only value in JS that's not equal to itself — use `Number.isNaN()` to check.
हिंदी: `==` में boolean → number convert होता है; null==undefined special case है; NaN खुद से कभी equal नहीं।

---

## ⚡ Alternative Solution
```javascript
// Tricky coercion chain:
console.log([] == false);    // true  — [] → '' → 0; false → 0
console.log([] == ![]);      // true  — [] == false → true (this is THE famous trick)
console.log({} == false);    // false — {} → '[object Object]' → NaN; NaN != 0

// Checking for NaN correctly:
console.log(Number.isNaN(NaN));      // true  ← correct way
console.log(Number.isNaN('hello'));  // false ← correct (isNaN('hello') = true, wrong!)
console.log(isNaN('hello'));         // true  ← WRONG — coerces string to NaN first

// null comparisons:
console.log(null == 0);       // false ← null only == undefined, nothing else
console.log(null == '');      // false
console.log(null == false);   // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: checking for null/undefined with ==
if (value == null) {
  // catches BOTH null AND undefined — actually works but confusing
}

// ✅ More explicit:
if (value === null || value === undefined) { ... }
// or: if (value == null) { ... }  — acceptable shorthand, just document it

// ❌ Wrong: checking NaN with ==
if (x == NaN) { }   // ALWAYS false — NaN is not equal to itself!
if (x === NaN) { }  // Also always false

// ✅ Correct:
if (Number.isNaN(x)) { }  // or if (x !== x) — NaN is the only value where this is true
```

---

## 🎯 Interview Tip (1 line)
Say: "Always use `===` in production; `null == undefined` is true (both nullish); `NaN !== NaN` — use `Number.isNaN()` to check."

---

## 🔗 Related Questions
→ Q028 (null == undefined) | Q029 (NaN comparison) | Q030 (type coercion) | Q292 (== vs === classic)
