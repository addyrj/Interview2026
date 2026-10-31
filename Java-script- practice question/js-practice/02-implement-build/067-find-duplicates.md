---

# Q067. Find Duplicates in Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `findDuplicates(arr)` that returns the values that appear more than once (each reported once).

```javascript
findDuplicates([1, 2, 2, 3, 3, 3]); // [2, 3]
```

---

## 💡 Quick Concept (2 lines only)
Track seen values in a Set; if a value is already seen, add it to a duplicates Set.
हिंदी: देखी हुई values Set में रखो, दोबारा दिखे तो उसे duplicates में डाल दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: seen Set + dupes Set
// Step 2: if item already seen -> it is a duplicate
// Step 3: return dupes as array

function findDuplicates(arr) {
  const seen = new Set();                 // values met so far
  const dupes = new Set();                // values met more than once
  for (const item of arr) {               // scan array
    if (seen.has(item)) dupes.add(item);  // seen before -> duplicate
    else seen.add(item);                  // first time -> remember
  }
  return [...dupes];                      // unique duplicates
}

// ============================================
// TEST CASES
// ============================================

console.log(findDuplicates([1, 2, 2, 3, 3, 3]));  // Expected: [ 2, 3 ]
console.log(findDuplicates(['a', 'b', 'a']));     // Expected: [ 'a' ]
console.log(findDuplicates([1, 2, 3]));           // Expected: []
console.log(findDuplicates([]));                  // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
The first sighting goes to `seen`, any later sighting goes to `dupes`. Using a Set for `dupes` avoids reporting a value three times. Time is O(n).
हिंदी: पहली बार seen में, दोबारा दिखे तो dupes में — Set होने से repeat नहीं होता।

---

## ⚡ Alternative Solution
```javascript
// filter + indexOf
const dup2 = (arr) => [...new Set(arr.filter((x, i) => arr.indexOf(x) !== i))]; // later occurrences only
console.log(dup2([1, 2, 2, 3, 3, 3])); // Expected: [ 2, 3 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: returns the duplicate value many times
console.log([1, 1, 1].filter((x, i, a) => a.indexOf(x) !== i)); // [ 1, 1 ]
// ✅ Correct: wrap in Set
console.log(findDuplicates([1, 1, 1])); // [ 1 ]
```

---

## 🎯 Interview Tip (1 line)
Explain the one-pass Set approach (O(n)) versus nested loops (O(n^2)).

---

## 🔗 Related Questions
→ Q055 (remove duplicates) | Q066 (count occurrences) | Q069 (unique values)
