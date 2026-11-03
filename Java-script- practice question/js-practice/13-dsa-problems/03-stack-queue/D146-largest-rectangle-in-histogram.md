---

# D146. Largest Rectangle in Histogram
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐⭐ Hard | LeetCode #84 | Asked: Amazon, Google, Microsoft, Flipkart

---

## ❓ Problem
Given bar heights of a histogram (each width 1), return the area of the largest rectangle.

```
Input:  [2,1,5,6,2,3]
Output: 10      // bars 5 and 6, height 5 x width 2
```

---

## 💡 Quick Concept (2 lines only)
Keep a stack of indices with increasing heights. When a shorter bar arrives, pop taller bars; each popped bar's rectangle extends from the new stack top + 1 to the current index - 1.
हिंदी: Increasing stack रखो; छोटा bar आते ही पिछले bars pop करके उनका area निकालो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — O(n^2) time, O(1) space
// ============================================

function largestRectBrute(heights) {
  let best = 0;                                      // max area
  for (let i = 0; i < heights.length; i++) {
    let minH = heights[i];                           // min height in the window
    for (let j = i; j < heights.length; j++) {
      minH = Math.min(minH, heights[j]);             // shrink to smallest bar
      best = Math.max(best, minH * (j - i + 1));     // area of window i..j
    }
  }
  return best;
}

// ============================================
// APPROACH 2: Monotonic stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function largestRectangleArea(heights) {
  const stack = [];                                  // indices, heights increasing
  let best = 0;                                      // max area
  const n = heights.length;

  for (let i = 0; i <= n; i++) {
    const cur = i === n ? 0 : heights[i];            // sentinel 0 flushes the stack at the end
    while (stack.length && cur < heights[stack[stack.length - 1]]) {
      const h = heights[stack.pop()];                // bar being closed
      const left = stack.length ? stack[stack.length - 1] : -1; // previous smaller index
      const width = i - left - 1;                    // span where h is the minimum
      best = Math.max(best, h * width);              // update answer
    }
    stack.push(i);                                   // push current index
  }
  return best;
}

// ============================================
// TEST CASES
// ============================================

console.log(largestRectangleArea([2,1,5,6,2,3]));    // 10
console.log(largestRectangleArea([2,4]));            // 4
console.log(largestRectangleArea([1,1,1,1]));        // 4
console.log(largestRectangleArea([6,5,4,3]));       // 12
console.log(largestRectangleArea([5]));              // 5
console.log(largestRectBrute([2,1,5,6,2,3]));        // 10
```

---

## 🔍 Why It Works
```
heights [2,1,5,6,2,3]
i=0 push0               [0]
i=1 (1<2) pop0: h=2,w=1 ->2 ; push1   [1]
i=2 push2  i=3 push3     [1,2,3]
i=4 (2<6) pop3: h=6,w=4-2-1=1 ->6
    (2<5) pop2: h=5,w=4-1-1=2 ->10 ; push4  [1,4]
i=5 push5                [1,4,5]
i=6 (0) pop5: 3x1=3, pop4: 2x(6-1-1)=8, pop1: 1x6=6
best = 10
```
हिंदी: Pop होने वाला bar अपने बाएँ-दाएँ छोटे bar तक फैलता है — वही उसकी width है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Stack:       Time O(n)   | Space O(n)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Maximal Rectangle in binary matrix (#85) —
//   build histogram per row, call largestRectangleArea on each row.
// VARIANT 2: Trapping Rain Water (#42) — also solvable with a stack.
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to flush the stack at the end (no sentinel)
// ✅ Loop to i === n with cur = 0

// ❌ Wrong: width = i - stackTop  (off by one)
// ✅ width = i - newTop - 1, with newTop = -1 when stack is empty
```

---

## 🎯 Interview Tip
Say: "For each bar I need the nearest smaller bar on both sides; the stack gives both in one pass." Draw the example and the sentinel 0 trick.

---

## 🔗 Related Problems
→ D143 (Daily Temperatures) | D144 (Next Greater Element) | D153 (Online Stock Span)
