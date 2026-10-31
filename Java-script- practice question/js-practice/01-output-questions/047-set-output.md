---

# Q047. Set Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```javascript
const s = new Set([1, 1, '1', NaN, NaN, {}, {}, [], []]);
console.log(s.size);
console.log([...new Set('aabbc')].join(''));
```

---

## 💡 Quick Concept (2 lines only)
A Set stores unique values using SameValueZero: NaN equals NaN, but two separate objects/arrays are different. 1 and '1' are different.
हिंदी: Set unique values रखता है; NaN एक ही गिना जाता है, पर अलग-अलग {} या [] अलग माने जाते हैं।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: 1 appears twice -> one entry
// Step 2: '1' is a different type -> separate entry
// Step 3: NaN twice -> one entry (SameValueZero)
// Step 4: {} and {} are different references -> 2 entries; [] same -> 2 entries
// Step 5: count = 1, '1', NaN, {}, {}, [], [] = 7

const s = new Set([1, 1, '1', NaN, NaN, {}, {}, [], []]); // build set
console.log(s.size);                          // 7
console.log([...new Set('aabbc')].join(''));  // abc

// ============================================
// TEST CASES
// ============================================

const a = new Set([1, 2, 3]);                 // set A
const b = new Set([2, 3, 4]);                 // set B
console.log([...a].filter((x) => b.has(x)));  // Expected: [ 2, 3 ] (intersection)
console.log([...new Set([...a, ...b])]);      // Expected: [ 1, 2, 3, 4 ] (union)
console.log(new Set([0, -0]).size);           // Expected: 1 (0 and -0 equal)
const ref = {};                               // one shared reference
console.log(new Set([ref, ref]).size);        // Expected: 1

// ============================================
// OUTPUT:
// ============================================
// 7
// abc
// [ 2, 3 ]
// [ 1, 2, 3, 4 ]
// 1
// 1
```

---

## 🔍 Why This Works (3 lines max)
Set uses SameValueZero: primitives compare by value, objects by reference. That is why NaN dedupes but `{}` literals never do. Set also preserves insertion order.
हिंदी: Primitives value से और objects reference से compare होते हैं, इसलिए {} duplicate नहीं हटते।

---

## ⚡ Alternative Solution
```javascript
// Dedupe with filter + indexOf (O(n^2), fails for NaN)
const arr = [1, 2, 2, 3, NaN, NaN];                       // sample
console.log(arr.filter((v, i) => arr.indexOf(v) === i));  // [ 1, 2, 3, NaN, NaN ]
console.log([...new Set(arr)]);                           // [ 1, 2, 3, NaN ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting Set to dedupe equal objects
const users = new Set([{ id: 1 }, { id: 1 }]);
console.log(users.size);   // 2

// ✅ Correct: dedupe by a primitive key using Map
const uniq = [...new Map([{ id: 1 }, { id: 1 }].map((u) => [u.id, u])).values()];
console.log(uniq.length);  // 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Set dedupes primitives by value (even NaN) but objects by reference, so for objects I key by an id."

---

## 🔗 Related Questions
→ Q046 (Map vs Object) | Q055 (remove duplicates) | Q247 (Set use cases)
