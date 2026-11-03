---

# D103. Product of Array Except Self
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #238 | Asked: Amazon, Facebook, Microsoft, Apple

---

## ❓ Problem
Given `nums`, return an array `answer` where `answer[i]` is the product of all elements except `nums[i]`. Do NOT use division; solve in O(n).

```
Input:  [1, 2, 3, 4]
Output: [24, 12, 8, 6]
```

---

## 💡 Quick Concept (2 lines only)
answer[i] = (product of everything left of i) × (product of everything right of i). Build left products in one pass, multiply right products in a second pass.
हिंदी: हर index के लिए left का product × right का product — दो pass में।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²) time, O(1) extra space
// ============================================

function productBrute(nums) {
  const res = [];                                   // output array
  for (let i = 0; i < nums.length; i++) {           // for each index
    let prod = 1;                                   // running product
    for (let j = 0; j < nums.length; j++) {         // multiply all others
      if (j !== i) prod *= nums[j];                 // skip the current index
    }
    res.push(prod);                                 // store result
  }
  return res;
}

// ============================================
// APPROACH 2: Prefix + Suffix arrays — O(n) time, O(n) space
// ============================================

function productArrays(nums) {
  const n = nums.length;                            // length
  const left = new Array(n).fill(1);                // left[i] = product before i
  const right = new Array(n).fill(1);               // right[i] = product after i
  for (let i = 1; i < n; i++) left[i] = left[i - 1] * nums[i - 1];          // build prefix
  for (let i = n - 2; i >= 0; i--) right[i] = right[i + 1] * nums[i + 1];   // build suffix
  return nums.map((_, i) => left[i] * right[i]);    // combine both sides
}

// ============================================
// APPROACH 3: Output array as prefix — O(n) time, O(1) extra space ✅ PREFERRED
// ============================================

function productExceptSelf(nums) {
  const n = nums.length;                            // length
  const res = new Array(n).fill(1);                 // res starts as all 1s
  let prefix = 1;                                   // product of elements to the left
  for (let i = 0; i < n; i++) {                     // left → right pass
    res[i] = prefix;                                // store product of left side
    prefix *= nums[i];                              // include current for next index
  }
  let suffix = 1;                                   // product of elements to the right
  for (let i = n - 1; i >= 0; i--) {                // right → left pass
    res[i] *= suffix;                               // multiply with right side product
    suffix *= nums[i];                              // include current for next index
  }
  return res;                                       // final answer
}

// ============================================
// TEST CASES
// ============================================

console.log(productExceptSelf([1, 2, 3, 4]));       // [ 24, 12, 8, 6 ]
console.log(productExceptSelf([1, 2, 0, 4]));       // [ 0, 0, 8, 0 ]
console.log(productExceptSelf([2, 3]));             // [ 3, 2 ]
console.log(productArrays([1, 2, 3, 4]));           // [ 24, 12, 8, 6 ]
console.log(productBrute([1, 2, 3, 4]));            // [ 24, 12, 8, 6 ]
```

---

## 🔍 Why It Works
```
nums   = [1, 2, 3, 4]
pass 1 (left products):  [1, 1, 2, 6]
pass 2 (multiply by right products; suffix goes 1,4,12,24):
  i=3: 6*1  = 6   suffix=4
  i=2: 2*4  = 8   suffix=12
  i=1: 1*12 = 12  suffix=24
  i=0: 1*24 = 24
result = [24, 12, 8, 6]
```
हिंदी: पहले pass में left product भरो, दूसरे pass में right product से गुणा करो।

---

## 📊 Complexity
```
Brute Force:    Time O(n²) | Space O(1)
Prefix/Suffix:  Time O(n)  | Space O(n)
Single output:  Time O(n)  | Space O(1) extra ← preferred (output not counted)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Division approach (only if division allowed, handle zeros)
function productDivision(nums) {
  let prod = 1, zeros = 0;                          // product of non-zeros, zero count
  for (const n of nums) n === 0 ? zeros++ : (prod *= n); // accumulate
  return nums.map((n) => {                          // build answer
    if (zeros > 1) return 0;                        // two zeros → everything 0
    if (zeros === 1) return n === 0 ? prod : 0;     // only the zero slot is non-zero
    return prod / n;                                // no zeros → divide
  });
}
console.log(productDivision([1, 2, 3, 4]));         // [ 24, 12, 8, 6 ]
console.log(productDivision([-1, 1, 0, -3, 3]));    // [ 0, 0, 9, 0, 0 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: dividing total product by nums[i] — breaks on zeros, banned in the problem
// ❌ Wrong: updating prefix BEFORE storing — includes nums[i] itself
prefix *= nums[i]; res[i] = prefix;

// ✅ Correct: store first, then update
res[i] = prefix; prefix *= nums[i];
```

---

## 🎯 Interview Tip
Say: "Two passes — left products then right products — O(n) time, O(1) extra space because I reuse the output array." Mention zeros are handled automatically.

---

## 🔗 Related Problems
→ D002 (Maximum Subarray) | D115 (Trapping Rain Water) | D104 (Rotate Array)
