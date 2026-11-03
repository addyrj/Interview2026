---

# D144. Next Greater Element
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #496 | Asked: Amazon, Microsoft, Adobe, Walmart

---

## ❓ Problem
For each element of `nums1` (a subset of `nums2`), find the next greater element to its right in `nums2`. If none, return -1.

```
Input:  nums1 = [4,1,2], nums2 = [1,3,4,2]
Output: [-1,3,-1]
```

---

## 💡 Quick Concept (2 lines only)
Scan `nums2` once with a decreasing stack; when a bigger number arrives, it is the next greater for every smaller value popped. Store results in a map, then look up `nums1`.
हिंदी: nums2 पर एक बार stack चलाओ, map में answer रखो, फिर nums1 के लिए lookup करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — O(n*m) time
// ============================================

function nextGreaterBrute(nums1, nums2) {
  return nums1.map(x => {
    let i = nums2.indexOf(x);                 // find x in nums2
    for (let j = i + 1; j < nums2.length; j++) {
      if (nums2[j] > x) return nums2[j];      // first greater on right
    }
    return -1;                                // none found
  });
}

// ============================================
// APPROACH 2: Monotonic stack + map — O(n+m) ✅ PREFERRED
// ============================================

function nextGreaterElement(nums1, nums2) {
  const map = new Map();                      // value -> next greater
  const stack = [];                           // decreasing values

  for (const num of nums2) {
    // num is greater than stack top -> it is the answer for those values
    while (stack.length && num > stack[stack.length - 1]) {
      map.set(stack.pop(), num);              // record answer
    }
    stack.push(num);                          // wait for its own greater
  }
  // leftover stack values have no greater element -> default -1
  return nums1.map(x => (map.has(x) ? map.get(x) : -1));
}

// ============================================
// TEST CASES
// ============================================

console.log(nextGreaterElement([4,1,2], [1,3,4,2]));   // [-1,3,-1]
console.log(nextGreaterElement([2,4], [1,2,3,4]));     // [3,-1]
console.log(nextGreaterElement([1], [1]));             // [-1]
console.log(nextGreaterBrute([4,1,2], [1,3,4,2]));     // [-1,3,-1]

// ============================================
// VARIANT: Circular array (LeetCode #503)
// ============================================

function nextGreaterCircular(nums) {
  const n = nums.length;
  const res = new Array(n).fill(-1);          // default -1
  const stack = [];                           // indices
  for (let i = 0; i < 2 * n; i++) {           // go around twice
    const cur = nums[i % n];
    while (stack.length && cur > nums[stack[stack.length - 1]]) {
      res[stack.pop()] = cur;                 // resolve
    }
    if (i < n) stack.push(i);                 // push only in first pass
  }
  return res;
}
console.log(nextGreaterCircular([1,2,1]));             // [2,-1,2]
```

---

## 🔍 Why It Works
```
nums2 = [1,3,4,2]
1 -> push            [1]
3 > 1 -> map{1:3}    [3]
4 > 3 -> map{3:4}    [4]
2 -> push            [4,2]
leftover 4,2 -> -1
nums1 [4,1,2] -> [-1,3,-1]
```
हिंदी: जो element stack में बचे रह गए उनका कोई बड़ा element नहीं मिला, इसलिए -1।

---

## 📊 Complexity
```
Brute force: Time O(n*m) | Space O(1)
Stack + map: Time O(n+m) | Space O(n)
```

---

## ⚡ Variations
```
- Circular array (#503): loop 2n times with index % n (shown above)
- Next smaller element: flip the comparison
- Previous greater element: scan from the right
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: looking for the next greater in nums1 instead of nums2
// ❌ Wrong: forgetting that leftover stack values must map to -1
// ✅ Use map.has(x) ? map.get(x) : -1
```

---

## 🎯 Interview Tip
Say: "Each element is pushed and popped at most once, so linear time." Offer to extend to the circular version by iterating 2n.

---

## 🔗 Related Problems
→ D143 (Daily Temperatures) | D146 (Largest Rectangle in Histogram) | D153 (Online Stock Span)
