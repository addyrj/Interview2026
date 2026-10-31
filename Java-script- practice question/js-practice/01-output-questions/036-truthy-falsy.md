---

# Q036. Truthy / Falsy Output
# Category: Output Questions
# Difficulty: ⭐ Easy

---

## ❓ Question
Which of these print "truthy"?

```javascript
const values = [0, '', '0', [], {}, null, undefined, NaN, -1, ' '];
```

---

## 💡 Quick Concept (2 lines only)
Falsy values are: false, 0, -0, 0n, "", null, undefined, NaN. Everything else (including [] and {}) is truthy.
हिंदी: सिर्फ 8 falsy values हैं (false, 0, "", null, undefined, NaN आदि); बाकी सब, यहाँ तक कि [] और {}, truthy हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: put sample values in an array
// Step 2: loop through them
// Step 3: use Boolean(value) to check truthiness

const values = [0, '', '0', [], {}, null, undefined, NaN, -1, ' ']; // test values

values.forEach((v) => {                                // iterate each value
  console.log(JSON.stringify(v), Boolean(v) ? 'truthy' : 'falsy'); // print label
});

// ============================================
// TEST CASES
// ============================================

console.log(Boolean('false'));  // Expected: true  (non-empty string)
console.log(Boolean(0n));       // Expected: false (BigInt zero)
console.log(!!document_like()); // Expected: true  (function returns object)
function document_like() { return {}; } // helper returning an object

// ============================================
// OUTPUT:
// ============================================
// 0 falsy
// "" falsy
// "0" truthy
// [] truthy
// {} truthy
// null falsy
// undefined falsy
// null falsy      <- NaN prints "null" via JSON.stringify
// -1 truthy
// " " truthy
// true
// false
// true
```

---

## 🔍 Why This Works (3 lines max)
`Boolean(v)` applies the ToBoolean rule: only the fixed falsy list returns false. Objects and arrays are always truthy, even when empty. Note JSON.stringify(NaN) prints "null" and JSON.stringify(undefined) prints undefined.
हिंदी: Boolean() fixed falsy list देखता है; खाली array/object भी truthy ही होते हैं।

---

## ⚡ Alternative Solution
```javascript
// Filter out falsy values in one line
const cleaned = [0, 1, '', 'a', null, 2, undefined].filter(Boolean); // keep truthy only
console.log(cleaned); // [ 1, 'a', 2 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming empty array is falsy
if ([]) console.log('runs!');       // runs! (array is truthy)

// ✅ Correct: check length
if ([].length) console.log('no');   // not executed
else console.log('empty array');    // empty array
```

---

## 🎯 Interview Tip (1 line)
Say: "Only false, 0, -0, 0n, '', null, undefined and NaN are falsy; empty arrays, objects and the string '0' are truthy."

---

## 🔗 Related Questions
→ Q037 (short circuit) | Q068 (remove falsy values) | Q038 (nullish coalescing)
