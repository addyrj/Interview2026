---

# D007. Three Sum
# Category: DSA — Two Pointers
# Difficulty: ⭐⭐ Medium | LeetCode #15 | Asked: Google, Amazon, Uber, PhonePe

---

## ❓ Problem
Given an integer array `nums`, return all unique triplets `[nums[i], nums[j], nums[k]]` such that they sum to 0. No duplicate triplets in the result.

```javascript
threeSum([-1, 0, 1, 2, -1, -4]);  // [[-1,-1,2],[-1,0,1]]
threeSum([0, 1, 1]);               // []
threeSum([0, 0, 0]);               // [[0,0,0]]
```

---

## 💡 Quick Concept (2 lines only)
Sort array. Fix one element, use Two Pointers for the remaining two. Skip duplicates to avoid duplicate triplets.
हिंदी: Array sort करो — एक element fix करो, बाकी दो के लिए Two Pointers use करो, duplicates skip करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n³) — too slow
// ============================================

// ============================================
// APPROACH 2: Sort + Two Pointers — O(n²) ✅
// ============================================

function threeSum(nums) {
  const result = [];
  
  // Step 1: Sort the array
  nums.sort((a, b) => a - b);
  
  for (let i = 0; i < nums.length - 2; i++) {
    // Step 2: Skip duplicate 'i' values
    if (i > 0 && nums[i] === nums[i - 1]) continue;
    
    // Step 3: Early exit — smallest possible sum already > 0
    if (nums[i] > 0) break;
    
    let left = i + 1;
    let right = nums.length - 1;
    
    while (left < right) {
      const sum = nums[i] + nums[left] + nums[right];
      
      if (sum === 0) {
        result.push([nums[i], nums[left], nums[right]]);
        
        // Step 4: Skip duplicates for left and right
        while (left < right && nums[left] === nums[left + 1]) left++;
        while (left < right && nums[right] === nums[right - 1]) right--;
        
        left++;
        right--;
      } else if (sum < 0) {
        left++;   // need larger sum
      } else {
        right--;  // need smaller sum
      }
    }
  }
  
  return result;
}

// ============================================
// TEST CASES
// ============================================

console.log(threeSum([-1, 0, 1, 2, -1, -4]));
// [[-1,-1,2],[-1,0,1]]

console.log(threeSum([0, 0, 0]));
// [[0,0,0]]

console.log(threeSum([0, 1, 1]));
// []

console.log(threeSum([-2, 0, 0, 2, 2]));
// [[-2,0,2]]  — duplicates handled

// WALKTHROUGH for [-1,0,1,2,-1,-4]:
// After sort: [-4,-1,-1,0,1,2]
// i=0, nums[i]=-4: left=1,right=5: sum=-4-1+2=-3<0,left++
//                  left=2,right=5: sum=-4-1+2=-3<0,left++
//                  ... no triplet with -4
// i=1, nums[i]=-1: left=2,right=5: sum=-1-1+2=0 → push [-1,-1,2]
//                  skip dup: left=3,right=4: sum=-1+0+1=0 → push [-1,0,1]
// i=2, nums[i]=-1: skip (dup of i=1)
// i=3, nums[i]=0: left=4,right=5: 0+1+2=3>0, right--; no more
// Result: [[-1,-1,2],[-1,0,1]] ✅
```

---

## 🔍 Why Two Pointers Work After Sorting
After sorting, for a fixed `nums[i]`, we need `nums[left] + nums[right] = -nums[i]`. Since array is sorted, if sum is too small, move left up; if too large, move right down. Sorting also groups duplicates for easy skipping.
हिंदी: Sort के बाद two pointers: sum small → left++, sum large → right--; adjacent duplicates skip करो।

---

## 📊 Complexity
```
Time:  O(n log n) [sort] + O(n²) [two loops] = O(n²)
Space: O(1) (excluding output)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Four Sum (LeetCode #18)
function fourSum(nums, target) {
  nums.sort((a, b) => a - b);
  const result = [];
  
  for (let i = 0; i < nums.length - 3; i++) {
    if (i > 0 && nums[i] === nums[i-1]) continue;
    
    for (let j = i + 1; j < nums.length - 2; j++) {
      if (j > i + 1 && nums[j] === nums[j-1]) continue;
      
      let left = j + 1, right = nums.length - 1;
      while (left < right) {
        const sum = nums[i] + nums[j] + nums[left] + nums[right];
        if (sum === target) {
          result.push([nums[i], nums[j], nums[left], nums[right]]);
          while (left < right && nums[left] === nums[left+1]) left++;
          while (left < right && nums[right] === nums[right-1]) right--;
          left++; right--;
        } else if (sum < target) left++;
        else right--;
      }
    }
  }
  return result;
}

// VARIANT 2: Three Sum Closest (LeetCode #16)
function threeSumClosest(nums, target) {
  nums.sort((a, b) => a - b);
  let closest = nums[0] + nums[1] + nums[2];
  
  for (let i = 0; i < nums.length - 2; i++) {
    let left = i + 1, right = nums.length - 1;
    while (left < right) {
      const sum = nums[i] + nums[left] + nums[right];
      if (Math.abs(sum - target) < Math.abs(closest - target)) closest = sum;
      if (sum < target) left++;
      else right--;
    }
  }
  return closest;
}
console.log(threeSumClosest([-1,2,1,-4], 1));  // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not sorting first
// Two pointers REQUIRES sorted array to work correctly

// ❌ Wrong: not skipping duplicates for the outer loop
for (let i = 0; i < nums.length; i++) {  // no duplicate skip!
  // [-1,-1,-1,0,1,2] → -1 processed 3 times → duplicate triplets
}
// ✅ if (i > 0 && nums[i] === nums[i-1]) continue;  ← skip outer duplicates
// ✅ skip inner duplicates AFTER finding a match

// ❌ Wrong: using Set to dedupe (expensive, error-prone)
const seen = new Set();
result.push([a,b,c]);
// Then filter duplicates with Set — O(n) per check, string comparison issues
// ✅ Better: sort + skip duplicates inline

// ❌ Wrong: comparing objects in Set (fails!)
seen.has([1,2,3])  // false — different array reference each time
```

---

## 🎯 Interview Tip
Say: "Three Sum = sort + fix one element + two pointer for the pair. Key: skip duplicates at all 3 levels (i, left, right). Time O(n²) — optimal for this problem."

---

## 🔗 Related Problems
→ D001 (Two Sum) | D008 (Container With Most Water) | D009 (Trapping Rain Water)
