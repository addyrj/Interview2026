---

# Q259. Array.at() Method
# Category: ES6+ Features
# Difficulty: ⭐ Easy

---

## ❓ Question
Use `.at()` to read items from the end of arrays and strings, and compare it to bracket access.

---

## 💡 Quick Concept (2 lines only)
`.at(index)` accepts negative indexes that count from the end, so `.at(-1)` is the last element.
हिंदी: `.at(-1)` सीधे आखिरी element देता है, negative index पीछे से गिनता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Positive index works like []
// Step 2: Negative index counts from the end
// Step 3: Works on strings and typed arrays too

const arr = [10, 20, 30, 40];                    // sample array

console.log(arr.at(0));                          // Expected: 10
console.log(arr.at(-1));                         // Expected: 40  (last)
console.log(arr.at(-2));                         // Expected: 30  (second last)

// Old way to get last element
console.log(arr[arr.length - 1]);                // Expected: 40

// Out of range -> undefined (no error)
console.log(arr.at(10), arr.at(-10));            // Expected: undefined undefined

// Works on strings
console.log('hello'.at(-1));                     // Expected: o

// Works on typed arrays
console.log(new Uint8Array([1, 2, 3]).at(-1));   // Expected: 3

// ============================================
// TEST CASES
// ============================================

console.log([].at(-1));                          // Expected: undefined
console.log(arr.at());                           // Expected: 10   (index defaults to 0)
console.log(arr.at(1.9));                        // Expected: 20   (truncated)
console.log(arr.at('-1'));                       // Expected: 40   (string coerced)
console.log(arr[-1]);                            // Expected: undefined (bracket has no negatives)
```

---

## 🔍 Why This Works (3 lines max)
`at(n)` converts n to an integer; if negative, it uses `length + n`. Bracket access treats `-1` as a plain property name, which does not exist.
हिंदी: Negative index पर `at()` खुद `length + n` निकाल लेता है, bracket नहीं करता।

---

## ⚡ Alternative Solution
```javascript
// slice(-1) returns a one-element array
console.log(arr.slice(-1)[0]);                   // Expected: 40
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: negative bracket index
console.log(arr[-1]);                            // Expected: undefined

// ✅ Correct: use at()
console.log(arr.at(-1));                         // Expected: 40
```

---

## 🎯 Interview Tip (1 line)
Say: "at() is ES2022 sugar for relative indexing; it returns undefined out of range and doesn't mutate the array."

---

## 🔗 Related Questions
→ Q056 (find max) | Q070 (array rotation) | Q289 (efficient array operations) | Q258 (fromEntries)
