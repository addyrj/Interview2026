---

# Q247. Set — 5 Use Cases
# Category: ES6+ Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 practical uses of `Set`: dedupe, union, intersection, difference, and fast membership check.

---

## 💡 Quick Concept (2 lines only)
`Set` stores unique values of any type, keeps insertion order, and `has()` is O(1) on average.
हिंदी: Set में duplicate values नहीं रहतीं और `has()` बहुत तेज़ चलता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Dedupe with Set
// Step 2: Set algebra using spread + filter
// Step 3: Fast lookups

// 1. Remove duplicates from array
const nums = [1, 2, 2, 3, 3, 3];                 // has duplicates
console.log([...new Set(nums)]);                 // Expected: [ 1, 2, 3 ]

// 2. Union
const A = new Set([1, 2, 3]);                    // set A
const B = new Set([3, 4]);                       // set B
console.log([...new Set([...A, ...B])]);         // Expected: [ 1, 2, 3, 4 ]

// 3. Intersection
console.log([...A].filter(x => B.has(x)));       // Expected: [ 3 ]

// 4. Difference (A - B)
console.log([...A].filter(x => !B.has(x)));      // Expected: [ 1, 2 ]

// 5. Fast membership check / visited tracking
const visited = new Set();                       // seen values
const hasDup = arr => arr.some(v => visited.has(v) || !visited.add(v)); // add returns the Set (truthy)
console.log(hasDup([1, 2, 3]));                  // Expected: false
console.log(hasDup([4, 5, 4]));                  // Expected: true

// ============================================
// TEST CASES
// ============================================

console.log(new Set('hello').size);              // Expected: 4
console.log(new Set([NaN, NaN]).size);           // Expected: 1
console.log(new Set([{}, {}]).size);             // Expected: 2
console.log(new Set([0, -0]).size);              // Expected: 1
```

---

## 🔍 Why This Works (3 lines max)
Set compares with SameValueZero so NaN equals NaN and 0 equals -0, but two different object references stay distinct. Lookups hash the value, hence O(1).
हिंदी: Object हर बार अलग reference होता है, इसलिए दो `{}` Set में दो बार आते हैं।

---

## ⚡ Alternative Solution
```javascript
// Dedupe with filter + indexOf (O(n^2), older style)
const uniq = [1, 1, 2].filter((v, i, arr) => arr.indexOf(v) === i); // keep first occurrence
console.log(uniq);                               // Expected: [ 1, 2 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: expecting Set to dedupe objects by content
const s = new Set([{ id: 1 }, { id: 1 }]);       // two separate references
console.log(s.size);                             // Expected: 2

// ✅ Correct: dedupe by a primitive key
const byId = [...new Map([{ id: 1 }, { id: 1 }].map(o => [o.id, o])).values()]; // key by id
console.log(byId.length);                        // Expected: 1
```

---

## 🎯 Interview Tip (1 line)
Say: "Set gives O(1) lookup and automatic uniqueness — I use it for dedupe, visited tracking and set algebra."

---

## 🔗 Related Questions
→ Q047 (Set output) | Q055 (remove duplicates) | Q062 (intersection) | Q246 (Map)
