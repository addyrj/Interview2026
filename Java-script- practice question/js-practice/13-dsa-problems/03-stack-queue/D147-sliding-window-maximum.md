---

# D147. Sliding Window Maximum (Deque)
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐⭐ Hard | LeetCode #239 | Asked: Amazon, Google, Microsoft, Uber

---

## ❓ Problem
Given an array `nums` and window size `k`, return the maximum of each sliding window of size `k`.

```
Input:  nums = [1,3,-1,-3,5,3,6,7], k = 3
Output: [3,3,5,5,6,7]
```

---

## 💡 Quick Concept (2 lines only)
Keep a deque of indices whose values are in decreasing order. Remove indices that left the window from the front, and smaller values from the back; the front is always the max.
हिंदी: Deque में indices रखो (values घटती हुई) — front हमेशा window का maximum है।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — O(n*k) time
// ============================================

function maxSlidingWindowBrute(nums, k) {
  const res = [];                                    // answers
  for (let i = 0; i + k <= nums.length; i++) {
    res.push(Math.max(...nums.slice(i, i + k)));     // max of each window
  }
  return res;
}

// ============================================
// APPROACH 2: Monotonic deque — O(n) time, O(k) space ✅ PREFERRED
// ============================================

function maxSlidingWindow(nums, k) {
  const res = [];                                    // answers
  const dq = [];                                     // indices, values decreasing
  let head = 0;                                      // front pointer (avoids O(n) shift)

  for (let i = 0; i < nums.length; i++) {
    // 1) drop front index if it slid out of the window
    if (dq.length > head && dq[head] <= i - k) head++;

    // 2) drop back indices with values smaller than the new one (never the max again)
    while (dq.length > head && nums[dq[dq.length - 1]] < nums[i]) dq.pop();

    dq.push(i);                                      // add current index

    // 3) window is full -> front is the max
    if (i >= k - 1) res.push(nums[dq[head]]);
  }
  return res;
}

// ============================================
// TEST CASES
// ============================================

console.log(maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3)); // [3,3,5,5,6,7]
console.log(maxSlidingWindow([1], 1));                 // [1]
console.log(maxSlidingWindow([9,11], 2));              // [11]
console.log(maxSlidingWindow([4,3,2,1], 2));           // [4,3,2]
console.log(maxSlidingWindow([1,2,3,4], 4));           // [4]
console.log(maxSlidingWindowBrute([1,3,-1,-3,5,3,6,7], 3)); // [3,3,5,5,6,7]
```

---

## 🔍 Why It Works
```
nums [1,3,-1,-3,5,3,6,7], k=3
i=0 dq[0]            i=1 3>1 pop -> dq[1]
i=2 dq[1,2]  -> max 3
i=3 dq[1,2,3] -> max 3
i=4 idx1 out; 5 pops all -> dq[4] -> max 5
i=5 dq[4,5] -> 5
i=6 6 pops all -> dq[6] -> 6
i=7 dq[7] -> 7
```
हिंदी: जो element नए बड़े element से छोटा है वो कभी max नहीं बनेगा, इसलिए उसे हटा दो।

---

## 📊 Complexity
```
Brute force: Time O(n*k) | Space O(1) extra
Deque:       Time O(n)   | Space O(k)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Sliding window minimum — flip the comparison (> instead of <)
// VARIANT 2: Shortest subarray with sum >= K (#862) — deque on prefix sums
// VARIANT 3: Queue with getMax in O(1) — same deque trick
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing values in the deque -> cannot tell when an item left the window
// ✅ Store indices

// ❌ Wrong: using array.shift() inside the loop -> O(n) each, hidden O(n*k)
// ✅ Use a head pointer or a linked-list deque
```

---

## 🎯 Interview Tip
Say: "The deque stays decreasing, so the front is the max. Each index enters and leaves once — O(n)." Explain why smaller older elements are useless.

---

## 🔗 Related Problems
→ D146 (Largest Rectangle in Histogram) | D143 (Daily Temperatures) | D141 (Queue using Stacks)
