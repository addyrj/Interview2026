---

# Q292. == vs ===
# Category: Interview Classics
# Difficulty: ⭐ Easy

---

## ❓ Question
Explain the difference between `==` (loose equality) and `===` (strict equality). Show examples where they differ, and explain why `NaN` never equals itself.

---

## 💡 Quick Concept (2 lines only)
`==` converts (coerces) types before comparing; `===` compares value AND type with no conversion.
हिंदी: `==` पहले type बदलता है फिर compare करता है; `===` type और value दोनों सीधे compare करता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: === never converts types -> different types are always false
// Step 2: == converts types using the Abstract Equality algorithm
// Step 3: null == undefined is the ONLY special case that is true without coercion to number
// Step 4: NaN is the only value not equal to itself -> use Number.isNaN / Object.is

// Helper to print a comparison label and both results
function compare(label, a, b) {
  // Print label, loose result, strict result
  console.log(label, '| ==:', a == b, '| ===:', a === b); // log both results
}

// ============================================
// TEST CASES
// ============================================

compare('1 vs "1"      ', 1, '1');          // Expected: 1 vs "1"       | ==: true  | ===: false
compare('0 vs false    ', 0, false);        // Expected: 0 vs false     | ==: true  | ===: false
compare('"" vs 0       ', '', 0);           // Expected: "" vs 0        | ==: true  | ===: false
compare('null vs undef ', null, undefined); // Expected: null vs undef  | ==: true  | ===: false
compare('null vs 0     ', null, 0);         // Expected: null vs 0      | ==: false | ===: false
compare('[] vs false   ', [], false);       // Expected: [] vs false    | ==: true  | ===: false
compare('NaN vs NaN    ', NaN, NaN);        // Expected: NaN vs NaN     | ==: false | ===: false

console.log(Number.isNaN(NaN)); // Expected: true  (correct NaN check)
console.log(Object.is(NaN, NaN)); // Expected: true  (same-value equality)
console.log(Object.is(0, -0)); // Expected: false (=== says true here)
console.log({} == {}); // Expected: false (objects compare by reference)
```

---

## 🔍 Why This Works (3 lines max)
`==` runs coercion rules (string/boolean -> number, object -> primitive), which gives surprising results. `===` skips all that, so results are predictable. `NaN` is defined by IEEE-754 as unequal to everything, even itself.
हिंदी: `==` में छुपा type conversion होता है इसलिए गड़बड़ होती है; `===` हमेशा safe है।

---

## ⚡ Alternative Solution
```javascript
// Object.is — like === but treats NaN as equal and distinguishes +0/-0
console.log(Object.is(NaN, NaN)); // true  <- === gives false
console.log(Object.is(0, -0));    // false <- === gives true

// The one accepted use of == : check null OR undefined in one go
const value = undefined;          // sample value
console.log(value == null);       // true  (matches both null and undefined)
console.log(value === null || value === undefined); // true (explicit version)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: trusting == with mixed types
if (userInput == 0) { /* '' and '0' and false all pass this! */ }

// ❌ Wrong: checking NaN with equality
if (result === NaN) { /* NEVER true */ }

// ✅ Correct
if (userInput === 0) { /* only the number 0 */ }
if (Number.isNaN(result)) { /* correct NaN check */ }
```

---

## 🎯 Interview Tip (1 line)
Say: "I always use `===`; the only `==` I allow is `x == null` to check null/undefined together."

---

## 🔗 Related Questions
→ Q027 (== vs === output) | Q028 (null == undefined) | Q029 (NaN comparison) | Q030 (type coercion)
