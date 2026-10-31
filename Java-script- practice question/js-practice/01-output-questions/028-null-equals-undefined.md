---

# Q028. null == undefined Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
What will the following code print?

```javascript
console.log(null == undefined);
console.log(null === undefined);
console.log(null == 0);
console.log(null >= 0);
```

---

## 💡 Quick Concept (2 lines only)
With `==`, null and undefined are equal only to each other (and themselves). Relational operators (`>=`) convert null to 0, so results look inconsistent.
हिंदी: null == undefined true है, पर null == 0 false; जबकि null >= 0 true क्योंकि वहाँ null को 0 बनाया जाता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: == treats null and undefined as equal (special rule)
// Step 2: === compares types too, so they differ
// Step 3: null == 0 is false (null only equals undefined/null with ==)
// Step 4: >= converts null to 0 numerically, so 0 >= 0 is true

console.log(null == undefined);  // special rule -> true
console.log(null === undefined); // different types -> false
console.log(null == 0);          // no coercion to number for == -> false
console.log(null >= 0);          // null becomes 0 -> true

// ============================================
// TEST CASES
// ============================================

console.log(null > 0);           // Expected: false (0 > 0)
console.log(undefined == 0);     // Expected: false
console.log(undefined >= 0);     // Expected: false (undefined -> NaN)
console.log(null == false);      // Expected: false

// ============================================
// OUTPUT:
// ============================================
// true
// false
// false
// true
// false
// false
// false
// false
```

---

## 🔍 Why This Works (3 lines max)
The spec has a dedicated rule: `null == undefined` is true and neither equals anything else under `==`. Relational comparison uses ToNumber, so null becomes 0 but undefined becomes NaN.
हिंदी: == में null/undefined सिर्फ आपस में बराबर हैं, लेकिन >= में null → 0 और undefined → NaN बनता है।

---

## ⚡ Alternative Solution
```javascript
// Idiomatic "is null or undefined" check using == null
const isNil = (v) => v == null; // true for both null and undefined only
console.log(isNil(null));       // true
console.log(isNil(undefined));  // true
console.log(isNil(0));          // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming null >= 0 means null == 0
console.log(null >= 0 && null <= 0); // true
console.log(null == 0);              // false (surprise!)

// ✅ Correct: be explicit about intent
console.log(Number(null) === 0);     // true
```

---

## 🎯 Interview Tip (1 line)
Say: "== null is the one acceptable loose check because it catches both null and undefined; elsewhere I use ===."

---

## 🔗 Related Questions
→ Q027 (== vs ===) | Q029 (NaN comparison) | Q293 (null vs undefined)
