---

# Q038. Nullish Coalescing Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
console.log(null ?? 'default');
console.log(0 ?? 'default');
console.log('' ?? 'default');
console.log(undefined ?? null ?? 'last');
```

---

## 💡 Quick Concept (2 lines only)
`??` returns the right side only when the left is null or undefined. Unlike `||`, it keeps 0, "" and false.
हिंदी: ?? सिर्फ null/undefined पर right side देता है; 0, "" और false को valid मानता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: null is nullish -> fallback 'default'
// Step 2: 0 is not nullish -> keeps 0
// Step 3: '' is not nullish -> keeps ''
// Step 4: undefined -> go right; null -> go right; 'last'

console.log(null ?? 'default');            // 'default'
console.log(0 ?? 'default');               // 0
console.log('' ?? 'default');              // '' (prints an empty line)
console.log(undefined ?? null ?? 'last');  // 'last'

// ============================================
// TEST CASES
// ============================================

console.log(false ?? true);                // Expected: false
console.log(0 || 'fallback');              // Expected: fallback (|| differs)
let a;                                     // undefined variable
a ??= 5;                                   // assign only if nullish
console.log(a);                            // Expected: 5

// ============================================
// OUTPUT:
// ============================================
// default
// 0
// (empty line)
// last
// false
// fallback
// 5
```

---

## 🔍 Why This Works (3 lines max)
`??` checks only for null/undefined, while `||` checks for any falsy value. This avoids bugs when valid values like 0 or an empty string are provided.
हिंदी: ?? सिर्फ null/undefined देखता है, इसलिए 0 और खाली string जैसे valid values नहीं खोते।

---

## ⚡ Alternative Solution
```javascript
// Manual equivalent of a ?? b
const nullish = (a, b) => (a !== null && a !== undefined ? a : b); // explicit check
console.log(nullish(0, 9));     // 0
console.log(nullish(null, 9));  // 9
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: mixing ?? with || / && without parentheses
// const v = a ?? b || c;   // SyntaxError

// ✅ Correct: add parentheses
const a = null, b = 0, c = 3;
console.log((a ?? b) || c); // 3
```

---

## 🎯 Interview Tip (1 line)
Say: "?? falls back only on null/undefined, so 0, '' and false survive; || would overwrite them."

---

## 🔗 Related Questions
→ Q037 (short circuit) | Q039 (optional chaining) | Q177 (nullish coalescing explained)
