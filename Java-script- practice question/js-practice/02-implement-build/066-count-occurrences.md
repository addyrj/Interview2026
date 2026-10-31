---

# Q066. Count Occurrences in Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `countOccurrences(arr)` that returns an object with how many times each value appears.

```javascript
countOccurrences(['a', 'b', 'a']); // { a: 2, b: 1 }
```

---

## 💡 Quick Concept (2 lines only)
Use a frequency map: for every item, increase its counter (start at 0).
हिंदी: हर value की गिनती एक object में रखो, दिखने पर +1 करते जाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: start with empty frequency object
// Step 2: for each item read current count (default 0)
// Step 3: add 1 and store

function countOccurrences(arr) {
  const freq = {};                       // value -> count
  for (const item of arr) {              // visit every element
    freq[item] = (freq[item] || 0) + 1;  // increment count
  }
  return freq;                           // frequency map
}

// ============================================
// TEST CASES
// ============================================

console.log(countOccurrences(['a', 'b', 'a']));       // Expected: { a: 2, b: 1 }
console.log(countOccurrences([1, 2, 2, 3, 3, 3]));    // Expected: { '1': 1, '2': 2, '3': 3 }
console.log(countOccurrences([]));                    // Expected: {}
console.log(countOccurrences('hello'.split('')));     // Expected: { h: 1, e: 1, l: 2, o: 1 }
```

---

## 🔍 Why This Works (3 lines max)
`freq[item] || 0` handles the first sighting, then `+ 1` counts it. One pass gives O(n) time.
हिंदी: पहली बार दिखने पर count 0 मानकर +1 होता है, एक ही loop में काम पूरा।

---

## ⚡ Alternative Solution
```javascript
// reduce + Map (keeps types like numbers vs strings)
const countMap = (arr) => arr.reduce((m, x) => m.set(x, (m.get(x) || 0) + 1), new Map()); // Map counter
console.log(countMap([1, '1', 1])); // Expected: Map(2) { 1 => 2, '1' => 1 }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: plain object keys are strings, 1 and '1' collide
const o = {};
[1, '1'].forEach((x) => (o[x] = (o[x] || 0) + 1));
console.log(o); // { '1': 2 }
// ✅ Correct: use Map when types matter
console.log(countMap([1, '1'])); // Map(2) { 1 => 1, '1' => 1 }
```

---

## 🎯 Interview Tip (1 line)
Call it a "frequency map" and note that Map preserves key types while plain objects stringify keys.

---

## 🔗 Related Questions
→ Q067 (find duplicates) | Q079 (count key occurrences) | Q054 (count vowels)
