---

# Q062. Find Intersection of Arrays
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `intersection(a, b)` that returns the unique values present in BOTH arrays.

```javascript
intersection([1, 2, 3, 4], [3, 4, 5]); // [3, 4]
```

---

## 💡 Quick Concept (2 lines only)
Put one array in a Set, then keep items from the other array that exist in the Set.
हिंदी: एक array का Set बनाओ और दूसरे array में से सिर्फ वही values रखो जो Set में हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: build a Set from array b (fast lookup)
// Step 2: filter array a by membership in the Set
// Step 3: wrap in Set to drop duplicates

function intersection(a, b) {
  const setB = new Set(b);                     // O(1) lookup structure
  const common = a.filter((x) => setB.has(x)); // keep items also in b
  return [...new Set(common)];                 // remove duplicates
}

// ============================================
// TEST CASES
// ============================================

console.log(intersection([1, 2, 3, 4], [3, 4, 5]));  // Expected: [ 3, 4 ]
console.log(intersection([1, 1, 2], [1, 1, 3]));     // Expected: [ 1 ]
console.log(intersection([1, 2], [3, 4]));           // Expected: []
console.log(intersection([], [1]));                  // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Set lookup is O(1), so the whole thing is O(n + m) instead of O(n * m). The final Set removes repeated matches.
हिंदी: Set lookup तेज़ होता है, इसलिए पूरा काम n+m steps में हो जाता है।

---

## ⚡ Alternative Solution
```javascript
// includes version (simple, O(n*m))
const inter2 = (a, b) => [...new Set(a.filter((x) => b.includes(x)))]; // check membership via includes
console.log(inter2([1, 2, 3], [2, 3, 4])); // Expected: [ 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: duplicates leak into result
console.log([1, 1, 2].filter((x) => [1, 2].includes(x))); // [ 1, 1, 2 ]
// ✅ Correct: dedupe the result
console.log(intersection([1, 1, 2], [1, 2])); // [ 1, 2 ]
```

---

## 🎯 Interview Tip (1 line)
Explain the Set optimization (O(n+m) vs O(n*m)) and clarify duplicate handling.

---

## 🔗 Related Questions
→ Q063 (difference) | Q055 (remove duplicates) | Q069 (unique values)
