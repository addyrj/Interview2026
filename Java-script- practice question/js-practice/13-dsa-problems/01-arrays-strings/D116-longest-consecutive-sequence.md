---

# D116. Longest Consecutive Sequence
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #128 | Asked: Google, Amazon, Facebook, Microsoft

---

## ❓ Problem
Given an unsorted integer array, return the length of the longest run of consecutive integers (order in the array doesn't matter). Must run in O(n).

```
Input:  [100, 4, 200, 1, 3, 2]
Output: 4   (1, 2, 3, 4)
```

---

## 💡 Quick Concept (2 lines only)
Put all numbers in a Set. Only start counting from a number whose predecessor (n-1) is NOT in the set — that is a sequence start — then walk upward.
हिंदी: सिर्फ़ उसी number से गिनना शुरू करो जिसका n-1 set में नहीं है, फिर n+1, n+2... चलते जाओ।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Sorting — O(n log n) time
// ============================================

function longestConsecutiveSort(nums) {
  if (nums.length === 0) return 0;                   // empty array
  const sorted = [...new Set(nums)].sort((a, b) => a - b); // unique + sorted
  let best = 1, run = 1;                             // best and current run lengths
  for (let i = 1; i < sorted.length; i++) {          // scan neighbours
    if (sorted[i] === sorted[i - 1] + 1) run++;      // consecutive → extend
    else run = 1;                                    // gap → restart
    best = Math.max(best, run);                      // update best
  }
  return best;
}

// ============================================
// APPROACH 2: Hash Set, start only at sequence beginnings — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function longestConsecutive(nums) {
  const set = new Set(nums);                         // O(1) lookups
  let best = 0;                                      // longest run found
  for (const n of set) {                             // iterate unique numbers
    if (set.has(n - 1)) continue;                    // not a start → skip
    let cur = n;                                     // start of a run
    let length = 1;                                  // run length so far
    while (set.has(cur + 1)) {                       // extend while next exists
      cur++;                                         // move up
      length++;                                      // count it
    }
    best = Math.max(best, length);                   // update best
  }
  return best;
}

// ============================================
// TEST CASES
// ============================================

console.log(longestConsecutive([100, 4, 200, 1, 3, 2]));         // 4
console.log(longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1])); // 9
console.log(longestConsecutive([]));                 // 0
console.log(longestConsecutive([5]));                // 1
console.log(longestConsecutive([1, 2, 0, 1]));       // 3
console.log(longestConsecutiveSort([9, 1, 4, 7, 3, -1, 0, 5, 8, -1, 6])); // 7
```

---

## 🔍 Why It Works
```
set = {100, 4, 200, 1, 3, 2}
100: 99 absent → start → 100 only → 1
4:   3 present → skip
200: 199 absent → start → 1
1:   0 absent → start → 1,2,3,4 → 4  ← best
```
Each number is visited in the inner while loop at most once (only sequence starts walk), so total work is O(n).
हिंदी: हर number का inner loop सिर्फ़ एक बार चलता है, इसलिए कुल काम O(n) है।

---

## 📊 Complexity
```
Sorting:  Time O(n log n) | Space O(n)
Hash Set: Time O(n)       | Space O(n) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Longest increasing run of ADJACENT elements (subarray)
function longestIncreasingRun(nums) {
  if (!nums.length) return 0;                        // empty
  let best = 1, run = 1;                             // lengths
  for (let i = 1; i < nums.length; i++) {            // compare neighbours
    run = nums[i] > nums[i - 1] ? run + 1 : 1;       // extend or reset
    best = Math.max(best, run);                      // update best
  }
  return best;
}
console.log(longestIncreasingRun([1, 3, 5, 4, 7]));  // 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: starting the inner while loop from every number → O(n²) on [1..n]
// ❌ Wrong: not de-duplicating when sorting → duplicates break "consecutive" check
// ✅ Correct: skip any n where n-1 exists in the set
```

---

## 🎯 Interview Tip
Say: "Sorting is O(n log n), but the problem wants O(n) — use a set and only expand from sequence starts." Explain why that keeps total work linear.

---

## 🔗 Related Problems
→ D102 (Contains Duplicate) | D111 (Missing Number) | D001 (Two Sum)
