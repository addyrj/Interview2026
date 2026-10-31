---

# Q063. Find Difference of Arrays
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `difference(a, b)` that returns items in `a` that are NOT in `b`. Also write `symmetricDifference(a, b)` returning items in only one of them.

```javascript
difference([1, 2, 3, 4], [3, 4, 5]); // [1, 2]
```

---

## 💡 Quick Concept (2 lines only)
Put `b` in a Set, then keep items of `a` that the Set does not contain.
हिंदी: b का Set बनाओ और a में से वो items रखो जो उस Set में नहीं हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: build a Set from b
// Step 2: filter a for items NOT in the Set
// Step 3: symmetric = diff(a,b) + diff(b,a)

function difference(a, b) {
  const setB = new Set(b);                      // fast lookup
  return a.filter((x) => !setB.has(x));         // keep items missing from b
}

function symmetricDifference(a, b) {
  return [...difference(a, b), ...difference(b, a)]; // items unique to each side
}

// ============================================
// TEST CASES
// ============================================

console.log(difference([1, 2, 3, 4], [3, 4, 5]));          // Expected: [ 1, 2 ]
console.log(difference([1, 2], [1, 2]));                   // Expected: []
console.log(difference([5, 6], []));                       // Expected: [ 5, 6 ]
console.log(symmetricDifference([1, 2, 3], [2, 3, 4]));    // Expected: [ 1, 4 ]
```

---

## 🔍 Why This Works (3 lines max)
`filter` with a negated Set check removes everything found in `b` in O(n + m). Symmetric difference just applies it in both directions.
हिंदी: filter में उल्टी शर्त लगाने से b वाली values हट जाती हैं।

---

## ⚡ Alternative Solution
```javascript
// includes version
const diff2 = (a, b) => a.filter((x) => !b.includes(x)); // simple but O(n*m)
console.log(diff2([1, 2, 3], [2])); // Expected: [ 1, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: difference is NOT symmetric
console.log(difference([1, 2], [2, 3])); // [ 1 ]  (3 is ignored)
console.log(difference([2, 3], [1, 2])); // [ 3 ]
// ✅ Correct: use symmetricDifference when you need both sides
console.log(symmetricDifference([1, 2], [2, 3])); // [ 1, 3 ]
```

---

## 🎯 Interview Tip (1 line)
State that order matters (a minus b is not b minus a) and mention the Set-based O(n+m) approach.

---

## 🔗 Related Questions
→ Q062 (intersection) | Q055 (remove duplicates) | Q067 (find duplicates)
