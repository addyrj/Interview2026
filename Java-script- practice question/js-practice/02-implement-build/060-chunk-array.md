---

# Q060. Chunk Array into Groups
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `chunk(arr, size)` that splits an array into smaller arrays of length `size`. The last chunk may be shorter.

```javascript
chunk([1, 2, 3, 4, 5], 2); // [[1, 2], [3, 4], [5]]
```

---

## 💡 Quick Concept (2 lines only)
Step through the array in jumps of `size` and slice out each piece.
हिंदी: array पर size-size की छलांग लगाओ और हर बार slice काटकर नया chunk बनाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: validate size
// Step 2: loop with index jumping by size
// Step 3: push slice(i, i + size) into result

function chunk(arr, size) {
  if (size <= 0) throw new Error('size must be > 0'); // guard invalid size
  const result = [];                          // list of chunks
  for (let i = 0; i < arr.length; i += size) { // jump by size
    result.push(arr.slice(i, i + size));      // take one chunk
  }
  return result;                              // all chunks
}

// ============================================
// TEST CASES
// ============================================

console.log(chunk([1, 2, 3, 4, 5], 2));   // Expected: [ [ 1, 2 ], [ 3, 4 ], [ 5 ] ]
console.log(chunk([1, 2, 3, 4], 4));      // Expected: [ [ 1, 2, 3, 4 ] ]
console.log(chunk([1, 2, 3], 5));         // Expected: [ [ 1, 2, 3 ] ]
console.log(chunk([], 3));                // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
`slice` never goes past the array end, so the last chunk is automatically shorter. The loop runs `ceil(n / size)` times.
हिंदी: slice array के अंत से आगे नहीं जाता, इसलिए आखिरी chunk अपने आप छोटा बनता है।

---

## ⚡ Alternative Solution
```javascript
// Array.from version
const chunk2 = (arr, size) =>
  Array.from({ length: Math.ceil(arr.length / size) }, (_, i) => // number of chunks
    arr.slice(i * size, i * size + size));                         // slice each chunk
console.log(chunk2([1, 2, 3, 4, 5], 2)); // Expected: [ [ 1, 2 ], [ 3, 4 ], [ 5 ] ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: size 0 gives an infinite loop (i += 0)
// for (let i = 0; i < arr.length; i += 0) {}
// ✅ Correct: validate size first
try { chunk([1, 2], 0); } catch (e) { console.log(e.message); } // size must be > 0
```

---

## 🎯 Interview Tip (1 line)
Mention validating size and that `slice` is non-mutating so the input stays unchanged.

---

## 🔗 Related Questions
→ Q061 (zip arrays) | Q058 (flatten array) | Q070 (array rotation)
