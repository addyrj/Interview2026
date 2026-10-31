---

# Q053. Check Palindrome
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `isPalindrome(str)` that returns `true` if the string reads the same forwards and backwards. Ignore case, spaces and punctuation.

```javascript
isPalindrome('A man, a plan, a canal: Panama'); // true
```

---

## 💡 Quick Concept (2 lines only)
Clean the string (lowercase, only letters/digits) then compare it with its reverse, or use two pointers.
हिंदी: string साफ करो, फिर उसे उल्टे से compare करो — बराबर है तो palindrome है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: normalize (lowercase + remove non-alphanumeric)
// Step 2: use two pointers from both ends
// Step 3: any mismatch -> false, else true

function isPalindrome(str) {
  const clean = str.toLowerCase().replace(/[^a-z0-9]/g, ''); // keep letters/digits only
  let left = 0;                       // start pointer
  let right = clean.length - 1;       // end pointer
  while (left < right) {              // until pointers meet
    if (clean[left] !== clean[right]) return false; // mismatch found
    left++;                           // move left forward
    right--;                          // move right backward
  }
  return true;                        // all matched
}

// ============================================
// TEST CASES
// ============================================

console.log(isPalindrome('racecar'));                       // Expected: true
console.log(isPalindrome('A man, a plan, a canal: Panama')); // Expected: true
console.log(isPalindrome('hello'));                         // Expected: false
console.log(isPalindrome(''));                              // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
After cleaning, a palindrome's first and last characters must match, then the second and second-last, and so on. Two pointers check this in O(n) time with no extra reversed string.
हिंदी: दोनों सिरों से अक्षर मिलाते चलो, एक भी अलग मिला तो palindrome नहीं।

---

## ⚡ Alternative Solution
```javascript
// Reverse and compare (shorter)
const isPal = (s) => {
  const c = s.toLowerCase().replace(/[^a-z0-9]/g, ''); // clean string
  return c === [...c].reverse().join('');              // compare with reverse
};
console.log(isPal('Madam')); // Expected: true
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to clean case/punctuation
console.log('Madam' === 'Madam'.split('').reverse().join('')); // false ('madaM')
// ✅ Correct: lowercase first
const m = 'Madam'.toLowerCase();
console.log(m === m.split('').reverse().join('')); // true
```

---

## 🎯 Interview Tip (1 line)
Offer the two-pointer approach (O(1) extra space after cleaning) and ask whether to ignore punctuation/case.

---

## 🔗 Related Questions
→ Q051 (reverse string) | Q052 (reverse words) | Q054 (count vowels)
