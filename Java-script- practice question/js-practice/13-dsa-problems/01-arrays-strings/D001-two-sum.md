---

# D001. Two Sum
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #1 | Asked: Amazon, Google, Flipkart, Atlassian

---

## ❓ Problem
Given an array of integers `nums` and an integer `target`, return indices of the two numbers that add up to `target`. Assume exactly one solution exists. You may NOT use the same element twice.

```javascript
twoSum([2, 7, 11, 15], 9);   // [0, 1]  (2+7=9)
twoSum([3, 2, 4], 6);        // [1, 2]  (2+4=6)
twoSum([3, 3], 6);           // [0, 1]
```

---

## 💡 Quick Concept (2 lines only)
Use a HashMap: for each number, check if `target - num` already exists in the map. One pass — O(n) time, O(n) space.
हिंदी: HashMap use करो — हर number के लिए `target - num` map में है क्या check करो। एक pass में answer।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²) time, O(1) space
// ============================================

function twoSumBrute(nums, target) {
  for (let i = 0; i < nums.length; i++) {
    for (let j = i + 1; j < nums.length; j++) {
      if (nums[i] + nums[j] === target) return [i, j];
    }
  }
  return [];
}
// Too slow — don't use in interview

// ============================================
// APPROACH 2: HashMap — O(n) time, O(n) space ✅ OPTIMAL
// ============================================

function twoSum(nums, target) {
  const map = new Map();  // stores { value: index }
  
  for (let i = 0; i < nums.length; i++) {
    const complement = target - nums[i];  // what do we need?
    
    if (map.has(complement)) {
      return [map.get(complement), i];    // found! return both indices
    }
    
    map.set(nums[i], i);  // store current number for future lookups
  }
  
  return [];
}

// ============================================
// TEST CASES
// ============================================

console.log(twoSum([2, 7, 11, 15], 9));  // [0, 1]
console.log(twoSum([3, 2, 4], 6));       // [1, 2]
console.log(twoSum([3, 3], 6));          // [0, 1]
console.log(twoSum([-1, -2, -3, -4, -5], -8)); // [2, 4] (-3+-5=-8)
```

---

## 🔍 Why HashMap Works
For each `nums[i]`, we need `target - nums[i]`. Instead of scanning the whole array again, we store every number we've seen in a Map. If `complement` is in the Map, we found our pair in O(1) lookup.
हिंदी: Map में देखा हुआ हर number store करो — complement found तो done; otherwise current store करो।

---

## 📊 Complexity
```
Brute Force: Time O(n²) | Space O(1)
HashMap:     Time O(n)  | Space O(n)  ← always use this
```

---

## ⚡ Variations (asked as follow-ups)

```javascript
// VARIANT 1: Return the VALUES (not indices)
function twoSumValues(nums, target) {
  const seen = new Set();
  for (const num of nums) {
    if (seen.has(target - num)) return [target - num, num];
    seen.add(num);
  }
}

// VARIANT 2: Array is SORTED → Two Pointers (O(1) space)
function twoSumSorted(nums, target) {
  let left = 0, right = nums.length - 1;
  while (left < right) {
    const sum = nums[left] + nums[right];
    if (sum === target) return [left, right];
    else if (sum < target) left++;
    else right--;
  }
  return [];
}

// VARIANT 3: All pairs (multiple solutions)
function twoSumAll(nums, target) {
  const map = new Map();
  const result = [];
  for (let i = 0; i < nums.length; i++) {
    const comp = target - nums[i];
    if (map.has(comp)) {
      for (const j of map.get(comp)) result.push([j, i]);
    }
    if (!map.has(nums[i])) map.set(nums[i], []);
    map.get(nums[i]).push(i);
  }
  return result;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: storing AFTER checking (misses same-index case like [3,3],6)
map.set(nums[i], i);      // store first
if (map.has(complement))  // then check — finds nums[i] itself!

// ✅ Correct: check THEN store
if (map.has(complement)) return [map.get(complement), i];
map.set(nums[i], i);  // store after check

// ❌ Wrong: using object instead of Map for index lookup
const obj = {};
obj[nums[i]] = i;  // key is string — obj[1] and obj['1'] are same
// Use Map for numeric keys to avoid coercion bugs
```

---

## 🎯 Interview Tip
Say: "Start by noting brute force is O(n²). Then ask: what if I store what I've seen? HashMap gives O(1) lookup → O(n) total. Mention two-pointer O(1) space works if array is sorted."

---

## 🔗 Related Problems
→ D002 (Three Sum) | D003 (Two Sum — Sorted) | D007 (Subarray Sum = K)
