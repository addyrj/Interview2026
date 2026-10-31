---

# Q135. Fix Type Coercion Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Values from an input are strings, so `+` concatenates instead of adding. Fix `total`.

```javascript
// BUGGY CODE:
const a = '10';                 // from input.value
const b = '20';
const total = a + b;            // '1020'
console.log(total);
console.log([5, 25, 100].sort()); // [100, 25, 5] (string sort)
```

---

## 💡 Quick Concept (2 lines only)
`+` with a string concatenates, and `sort()` compares as strings by default. Convert with `Number()` and pass a numeric comparator.
हिंदी: string के साथ `+` जोड़ता नहीं, चिपकाता है — `Number()` से बदलो और sort में comparator दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

const a = '10';                          // Step 1: string inputs
const b = '20';

const total = Number(a) + Number(b);     // Step 2 (FIX): convert to numbers first
const sorted = [5, 25, 100].sort((x, y) => x - y); // Step 3 (FIX): numeric comparator
const safe = Number('abc');              // Step 4: invalid input becomes NaN

// ============================================
// TEST CASES
// ============================================

console.log(total);                      // Expected: 30
console.log(sorted);                     // Expected: [ 5, 25, 100 ]
console.log(Number.isNaN(safe));         // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
`Number()` turns numeric strings into real numbers so `+` adds. The comparator `x - y` makes `sort` compare values instead of text.
हिंदी: `Number()` से `+` असली जोड़ करता है और comparator से sort संख्याओं पर चलता है।

---

## ⚡ Alternative Solution
```javascript
// Unary plus and parseInt
console.log(+'10' + +'20');          // 30
console.log(parseInt('42px', 10));   // 42 (parses leading digits)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: other operators coerce, only + concatenates
console.log('10' - '2', '10' + 2);   // 8 '102'
// ✅ Correct: be explicit
console.log(Number('10') + 2);       // 12
```

---

## 🎯 Interview Tip (1 line)
Say: "Convert explicitly at the boundary (input, JSON, URL) and validate with Number.isNaN."

---

## 🔗 Related Questions
→ Q030 (type coercion output) | Q031 (string + number) | Q134 (comparison bug) | Q289 (efficient array operations)
