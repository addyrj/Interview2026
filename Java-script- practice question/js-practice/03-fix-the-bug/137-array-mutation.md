---

# Q137. Fix Array Mutation Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
`getTop3` should return the 3 highest scores without reordering the original array. Fix it.

```javascript
// BUGGY CODE:
function getTop3(scores) {
  return scores.sort((a, b) => b - a).slice(0, 3); // sort mutates scores
}
const s = [5, 9, 1, 7];
getTop3(s);
console.log(s);   // [9, 7, 5, 1] (original changed)
```

---

## 💡 Quick Concept (2 lines only)
`sort`, `reverse`, `push`, `splice` mutate the array in place. Copy first with spread/slice, or use `toSorted()`.
हिंदी: `sort` original array को बदल देता है — पहले copy बनाओ या `toSorted()` use करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

function getTop3(scores) {
  return [...scores]               // Step 1 (FIX): copy so original stays intact
    .sort((a, b) => b - a)         // Step 2: sort the copy descending
    .slice(0, 3);                  // Step 3: take top three
}

// ============================================
// TEST CASES
// ============================================

const s = [5, 9, 1, 7];
console.log(getTop3(s));           // Expected: [ 9, 7, 5 ]
console.log(s);                    // Expected: [ 5, 9, 1, 7 ]
console.log(getTop3([2]));         // Expected: [ 2 ]
```

---

## 🔍 Why This Works (3 lines max)
Spread creates a new array, so sorting changes only the copy. Callers keep their original order.
हिंदी: spread नई array बनाता है, इसलिए sort सिर्फ copy को बदलता है।

---

## ⚡ Alternative Solution
```javascript
// Node 20+: non-mutating toSorted
const top = (arr) => arr.toSorted((a, b) => b - a).slice(0, 3);
console.log(top([5, 9, 1, 7])); // [ 9, 7, 5 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: const does not make the array immutable
const arr = [1, 2]; arr.push(3);
console.log(arr); // [1, 2, 3]
// ✅ Correct: create a new array
const arr2 = [...arr, 4];
```

---

## 🎯 Interview Tip (1 line)
Say: "I know which array methods mutate (sort, reverse, splice, push) and copy before using them."

---

## 🔗 Related Questions
→ Q104 (bubble sort) | Q112 (Array.map) | Q136 (object mutation) | Q289 (efficient array operations)
