---

# D143. Daily Temperatures (Monotonic Stack)
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #739 | Asked: Amazon, Google, Microsoft, Meesho

---

## ❓ Problem
Given an array `temperatures`, return an array `answer` where `answer[i]` is the number of days you must wait after day `i` for a warmer temperature. If none, put 0.

```
Input:  [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]
```

---

## 💡 Quick Concept (2 lines only)
Keep a stack of indices with decreasing temperatures. When today is warmer than the temperature at the stack top, pop it — its answer is today's index minus that index.
हिंदी: Stack में indices रखो; आज का temperature बड़ा हो तो pop करो और दूरी answer में लिखो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — O(n^2) time, O(1) extra space
// ============================================

function dailyTemperaturesBrute(temps) {
  const res = new Array(temps.length).fill(0);       // default 0 = no warmer day
  for (let i = 0; i < temps.length; i++) {
    for (let j = i + 1; j < temps.length; j++) {     // scan future days
      if (temps[j] > temps[i]) {                     // first warmer day
        res[i] = j - i;                              // distance
        break;                                       // stop at first
      }
    }
  }
  return res;
}

// ============================================
// APPROACH 2: Monotonic decreasing stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function dailyTemperatures(temps) {
  const res = new Array(temps.length).fill(0);       // answers
  const stack = [];                                  // indices with unresolved answers

  for (let i = 0; i < temps.length; i++) {
    // today is warmer than the day on top -> resolve those days
    while (stack.length && temps[i] > temps[stack[stack.length - 1]]) {
      const idx = stack.pop();                       // earlier colder day
      res[idx] = i - idx;                            // wait time
    }
    stack.push(i);                                   // today waits for its warmer day
  }
  return res;                                        // leftover indices stay 0
}

// ============================================
// TEST CASES
// ============================================

console.log(dailyTemperatures([73,74,75,71,69,72,76,73])); // [1,1,4,2,1,1,0,0]
console.log(dailyTemperatures([30,40,50,60]));             // [1,1,1,0]
console.log(dailyTemperatures([30,60,90]));                // [1,1,0]
console.log(dailyTemperatures([90,80,70]));                // [0,0,0]
console.log(dailyTemperatures([50]));                      // [0]
console.log(dailyTemperaturesBrute([73,74,75,71,69,72,76,73])); // [1,1,4,2,1,1,0,0]
```

---

## 🔍 Why It Works
```
temps: 73 74 75 71 69 72 76 73
i=0 push0           stack [0]
i=1 74>73 pop0 ->1  stack [1]
i=2 75>74 pop1 ->1  stack [2]
i=3 71 push         stack [2,3]
i=4 69 push         stack [2,3,4]
i=5 72>69 pop4->1, 72>71 pop3->2   stack [2,5]
i=6 76>72 pop5->1, 76>75 pop2->4   stack [6]
```
हिंदी: Stack में temperatures घटते क्रम में रहते हैं; हर index एक बार push और एक बार pop होता है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Monotonic stack: Time O(n) | Space O(n)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Previous warmer day (scan right-to-left or pop condition reversed)
// VARIANT 2: Next Greater Element -> D144
// VARIANT 3: Online Stock Span -> D153
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing temperatures in the stack — you lose the day index
stack.push(temps[i]);

// ❌ Wrong: using >= so equal temperatures are resolved (equal is NOT warmer)
// ✅ Store indices and use strict >
```

---

## 🎯 Interview Tip
Say: "This is the classic monotonic stack pattern — each index is pushed and popped once, so O(n)." Name the pattern; it unlocks Next Greater Element and Histogram.

---

## 🔗 Related Problems
→ D144 (Next Greater Element) | D146 (Largest Rectangle in Histogram) | D153 (Online Stock Span)
