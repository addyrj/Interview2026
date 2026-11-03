---

# D108. Valid Palindrome
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #125 | Asked: Facebook, Microsoft, Amazon, Infosys

---

## ❓ Problem
After lowercasing and removing all non-alphanumeric characters, check if the string reads the same forwards and backwards.

```
Input:  "A man, a plan, a canal: Panama"
Output: true

Input:  "race a car"
Output: false
```

---

## 💡 Quick Concept (2 lines only)
Two pointers from both ends; skip non-alphanumerics, compare lowercase characters, move inward.
हिंदी: दोनों तरफ से pointer चलाओ, बेकार characters skip करो, बाकी compare करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Clean + reverse — O(n) time, O(n) space
// ============================================

function isPalindromeClean(s) {
  const cleaned = s.toLowerCase().replace(/[^a-z0-9]/g, ''); // keep only letters/digits
  const reversed = cleaned.split('').reverse().join('');     // reverse it
  return cleaned === reversed;                               // same? palindrome
}

// ============================================
// APPROACH 2: Two pointers — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function isAlnum(ch) {
  return /[a-z0-9]/i.test(ch);                       // true for letters and digits
}

function isPalindrome(s) {
  let left = 0;                                      // start pointer
  let right = s.length - 1;                          // end pointer
  while (left < right) {                             // until they cross
    while (left < right && !isAlnum(s[left])) left++;    // skip junk on the left
    while (left < right && !isAlnum(s[right])) right--;  // skip junk on the right
    if (s[left].toLowerCase() !== s[right].toLowerCase()) return false; // mismatch
    left++;                                          // move inward
    right--;                                         // move inward
  }
  return true;                                       // all pairs matched
}

// ============================================
// TEST CASES
// ============================================

console.log(isPalindrome('A man, a plan, a canal: Panama')); // true
console.log(isPalindrome('race a car'));             // false
console.log(isPalindrome(' '));                      // true
console.log(isPalindrome('0P'));                     // false
console.log(isPalindrome(''));                       // true
console.log(isPalindromeClean('No lemon, no melon')); // true
```

---

## 🔍 Why It Works
```
"A man, a plan..."
left='A' right='a' → equal (case-insensitive)
left='m' right='m' → equal
... meets in the middle → true
```
Only alphanumeric characters matter, so we skip the rest in-place instead of building a new string.
हिंदी: नई string बनाए बिना, pointers से ही junk skip करके O(1) space में काम हो जाता है।

---

## 📊 Complexity
```
Clean+reverse: Time O(n) | Space O(n)
Two pointers:  Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Valid Palindrome II (LeetCode #680) — may delete at most one char
function validPalindromeII(s) {
  const check = (l, r) => {                          // plain palindrome check on range
    while (l < r) { if (s[l++] !== s[r--]) return false; } // compare ends
    return true;                                     // range is palindrome
  };
  let l = 0, r = s.length - 1;                       // pointers
  while (l < r) {                                    // scan
    if (s[l] !== s[r]) return check(l + 1, r) || check(l, r - 1); // try skipping either side
    l++; r--;                                        // move inward
  }
  return true;                                       // already palindrome
}
console.log(validPalindromeII('abca'));              // true
console.log(validPalindromeII('abc'));               // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting lowercase → 'A' !== 'a'
// ❌ Wrong: regex /\W/ keeps underscores — '_' counts as a word char
// ✅ Correct: use /[^a-z0-9]/ after lowercasing
```

---

## 🎯 Interview Tip
Say: "Two pointers give O(1) space. Empty or all-punctuation strings count as palindromes." Be ready for the "delete one character" follow-up.

---

## 🔗 Related Problems
→ D106 (Valid Anagram) | D104 (Rotate Array) | D109 (Longest Common Prefix)
