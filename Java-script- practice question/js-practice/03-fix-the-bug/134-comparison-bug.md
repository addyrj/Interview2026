---

# Q134. Fix Comparison Bug (== vs ===)
# Category: Fix the Bug
# Difficulty: ⭐ Easy

---

## ❓ Question
`isEmptyInput` wrongly treats `0` and `false` as empty. Fix the comparison.

```javascript
// BUGGY CODE:
function isEmptyInput(v) {
  return v == '';        // 0 == '' is true, false == '' is true
}
console.log(isEmptyInput(0));     // true (wrong)
console.log(isEmptyInput(false)); // true (wrong)
```

---

## 💡 Quick Concept (2 lines only)
`==` converts types before comparing, giving surprises. `===` compares type AND value, so use it by default.
हिंदी: `==` type बदलकर compare करता है; `===` type और value दोनों देखता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function isEmptyInput(v) {
  return v === '';        // FIX: strict equality, no coercion
}

// Null/undefined check on purpose (the one good use of ==)
function isNil(v) {
  return v == null;       // true for both null and undefined only
}

// ============================================
// TEST CASES
// ============================================

console.log(isEmptyInput(0));         // Expected: false
console.log(isEmptyInput(false));     // Expected: false
console.log(isEmptyInput(''));        // Expected: true
console.log(isNil(undefined), isNil(0)); // Expected: true false
```

---

## 🔍 Why This Works (3 lines max)
`===` never coerces, so `0`, `false` and `''` stay different. `v == null` is a safe shorthand because it matches only null and undefined.
हिंदी: `===` में coercion नहीं होता, इसलिए `0`, `false` और `''` अलग रहते हैं।

---

## ⚡ Alternative Solution
```javascript
// Object.is also handles NaN and -0
console.log(Object.is(NaN, NaN)); // true
console.log(NaN === NaN);         // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong
console.log('1' == 1, null == 0, [] == false); // true false true
// ✅ Correct
console.log('1' === 1, null === 0, [] === false); // false false false
```

---

## 🎯 Interview Tip (1 line)
Say: "Always use ===; the only == I allow is `x == null` to check null or undefined."

---

## 🔗 Related Questions
→ Q027 (== vs === output) | Q028 (null == undefined) | Q135 (type coercion bug) | Q292 (== vs ===)
