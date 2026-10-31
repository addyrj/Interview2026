---

# Q055. Remove Duplicates from Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `removeDuplicates(arr)` that returns a new array with duplicates removed, keeping the first occurrence and original order.

```javascript
removeDuplicates([1, 2, 2, 3, 1]); // [1, 2, 3]
```

---

## 💡 Quick Concept (2 lines only)
A `Set` only stores unique values, so converting to a Set and back removes duplicates.
हिंदी: Set में duplicate values नहीं रहतीं, इसलिए Set बनाकर वापस array बना लो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: create a Set from the array (drops duplicates)
// Step 2: spread the Set back into an array
// Step 3: original order is preserved (Set keeps insertion order)

function removeDuplicates(arr) {
  return [...new Set(arr)]; // unique values in insertion order
}

// ============================================
// TEST CASES
// ============================================

console.log(removeDuplicates([1, 2, 2, 3, 1]));      // Expected: [ 1, 2, 3 ]
console.log(removeDuplicates(['a', 'b', 'a']));      // Expected: [ 'a', 'b' ]
console.log(removeDuplicates([]));                   // Expected: []
console.log(removeDuplicates([NaN, NaN, 0, -0]));    // Expected: [ NaN, 0 ]
```

---

## 🔍 Why This Works (3 lines max)
Set uses SameValueZero equality, so each value is stored once, and iteration follows insertion order. Time is O(n).
हिंदी: Set हर value एक ही बार रखता है और क्रम वही रहता है जिस क्रम में डाली गई।

---

## ⚡ Alternative Solution
```javascript
// filter + indexOf (O(n^2), no Set)
const dedupe = (arr) => arr.filter((v, i) => arr.indexOf(v) === i); // keep only first occurrence
console.log(dedupe([1, 2, 2, 3, 1])); // Expected: [ 1, 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: Set of objects does not dedupe by content
console.log([...new Set([{ a: 1 }, { a: 1 }])].length); // 2 (different references)
// ✅ Correct: dedupe by a key (e.g. JSON string or id)
const items = [{ id: 1 }, { id: 1 }];
console.log([...new Map(items.map((o) => [o.id, o])).values()].length); // 1
```

---

## 🎯 Interview Tip (1 line)
Mention Set is O(n) vs filter+indexOf O(n^2), and that objects need a key-based approach.

---

## 🔗 Related Questions
→ Q067 (find duplicates) | Q069 (get unique values) | Q066 (count occurrences)
