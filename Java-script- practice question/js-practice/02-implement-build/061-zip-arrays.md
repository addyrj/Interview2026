---

# Q061. Zip Two Arrays Together
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `zip(a, b)` that pairs elements at the same index from two arrays. Stop at the shorter array.

```javascript
zip([1, 2, 3], ['a', 'b', 'c']); // [[1,'a'], [2,'b'], [3,'c']]
```

---

## 💡 Quick Concept (2 lines only)
Loop up to the shorter length and combine `a[i]` with `b[i]` as a pair.
हिंदी: छोटे array की length तक चलो और हर index के दोनों elements की जोड़ी बना दो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: find shorter length
// Step 2: loop that many times
// Step 3: push [a[i], b[i]] pair

function zip(a, b) {
  const len = Math.min(a.length, b.length); // stop at shorter array
  const result = [];                        // output pairs
  for (let i = 0; i < len; i++) {           // each index
    result.push([a[i], b[i]]);              // pair same-index items
  }
  return result;                            // zipped array
}

// ============================================
// TEST CASES
// ============================================

console.log(zip([1, 2, 3], ['a', 'b', 'c'])); // Expected: [ [ 1, 'a' ], [ 2, 'b' ], [ 3, 'c' ] ]
console.log(zip([1, 2], ['a', 'b', 'c']));    // Expected: [ [ 1, 'a' ], [ 2, 'b' ] ]
console.log(zip([], [1]));                    // Expected: []
// Bonus: build object from keys + values
console.log(Object.fromEntries(zip(['x', 'y'], [10, 20]))); // Expected: { x: 10, y: 20 }
```

---

## 🔍 Why This Works (3 lines max)
Using `Math.min` prevents reading past the shorter array. Each pair keeps the original order, and pairs can feed `Object.fromEntries`.
हिंदी: Math.min से हम छोटे array के आगे नहीं जाते, इसलिए undefined जोड़े नहीं बनते।

---

## ⚡ Alternative Solution
```javascript
// map version (uses first array length; slice b to be safe)
const zip2 = (a, b) => a.slice(0, b.length).map((x, i) => [x, b[i]]); // pair via index
console.log(zip2([1, 2, 3], ['a', 'b'])); // Expected: [ [ 1, 'a' ], [ 2, 'b' ] ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: mapping over the longer array adds undefined
console.log([1, 2, 3].map((x, i) => [x, ['a'][i]])); // [ [1,'a'], [2,undefined], [3,undefined] ]
// ✅ Correct: limit to the shorter length
console.log(zip([1, 2, 3], ['a'])); // [ [ 1, 'a' ] ]
```

---

## 🎯 Interview Tip (1 line)
Ask whether to truncate or pad with `undefined` for unequal lengths, then state your choice.

---

## 🔗 Related Questions
→ Q060 (chunk) | Q062 (intersection) | Q080 (transform keys)
