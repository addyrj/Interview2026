---

# D110. Majority Element (Boyer-Moore)
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #169 | Asked: Amazon, Google, Microsoft, Adobe

---

## ❓ Problem
Return the element that appears more than ⌊n/2⌋ times. The majority element always exists.

```
Input:  [2, 2, 1, 1, 1, 2, 2]
Output: 2

Input:  [3, 2, 3]
Output: 3
```

---

## 💡 Quick Concept (2 lines only)
Boyer-Moore voting: keep a candidate and a count. Same number → count++, different → count--, count hits 0 → pick a new candidate. Majority survives all the cancellations.
हिंदी: Majority element बाकी सबको "cancel" करने के बाद भी बचा रहता है।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Hash map count — O(n) time, O(n) space
// ============================================

function majorityMap(nums) {
  const freq = new Map();                            // value → count
  for (const n of nums) {                            // count every value
    freq.set(n, (freq.get(n) || 0) + 1);             // increment
    if (freq.get(n) > nums.length / 2) return n;     // more than half → done
  }
  return -1;                                         // not reached for valid input
}

// ============================================
// APPROACH 2: Sorting — O(n log n) time
// ============================================

function majoritySort(nums) {
  const sorted = [...nums].sort((a, b) => a - b);    // numeric sort
  return sorted[Math.floor(nums.length / 2)];        // middle must be the majority
}

// ============================================
// APPROACH 3: Boyer-Moore Voting — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function majorityElement(nums) {
  let candidate = null;                              // current candidate
  let count = 0;                                     // its running vote balance
  for (const n of nums) {                            // single pass
    if (count === 0) candidate = n;                  // no candidate → adopt this one
    count += n === candidate ? 1 : -1;               // vote for or against
  }
  return candidate;                                  // survivor is the majority
}

// ============================================
// TEST CASES
// ============================================

console.log(majorityElement([2, 2, 1, 1, 1, 2, 2])); // 2
console.log(majorityElement([3, 2, 3]));             // 3
console.log(majorityElement([1]));                   // 1
console.log(majorityElement([6, 6, 6, 7, 7]));       // 6
console.log(majorityMap([3, 3, 4]));                 // 3
console.log(majoritySort([5, 1, 5, 5, 2]));          // 5
```

---

## 🔍 Why Boyer-Moore Works
```
[2,2,1,1,1,2,2]
n=2: count0 → cand=2, count=1
n=2: count=2
n=1: count=1
n=1: count=0
n=1: count0 → cand=1, count=1
n=2: count=0
n=2: count0 → cand=2, count=1
return 2
```
Each non-majority element cancels one majority vote at most. Since majority has more than half, at least one vote survives.
हिंदी: हर अलग element एक majority vote काटता है, पर majority आधे से ज़्यादा है, इसलिए बच जाता है।

---

## 📊 Complexity
```
Hash map:    Time O(n)      | Space O(n)
Sorting:     Time O(n log n)| Space O(n) copy
Boyer-Moore: Time O(n)      | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Majority Element II (LeetCode #229) — more than n/3 times (up to 2 answers)
function majorityElementII(nums) {
  let c1 = null, c2 = null, n1 = 0, n2 = 0;          // two candidates and counts
  for (const x of nums) {                            // first pass: find candidates
    if (x === c1) n1++;                              // vote for c1
    else if (x === c2) n2++;                         // vote for c2
    else if (n1 === 0) { c1 = x; n1 = 1; }           // free slot 1
    else if (n2 === 0) { c2 = x; n2 = 1; }           // free slot 2
    else { n1--; n2--; }                             // cancel both
  }
  const res = [];                                    // verified answers
  for (const c of [c1, c2]) {                        // second pass: verify counts
    if (c !== null && nums.filter((x) => x === c).length > nums.length / 3 && !res.includes(c)) res.push(c);
  }
  return res;
}
console.log(majorityElementII([1, 1, 1, 3, 3, 2, 2, 2])); // [ 1, 2 ]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: assuming Boyer-Moore result is valid when majority may NOT exist
// ✅ Correct: if existence isn't guaranteed, do a second pass to verify the count
```

---

## 🎯 Interview Tip
Say: "Hash map is the obvious O(n) space solution; Boyer-Moore voting does it in O(1) space." Mention the verification pass if the majority isn't guaranteed.

---

## 🔗 Related Problems
→ D102 (Contains Duplicate) | D111 (Missing Number) | D001 (Two Sum)
