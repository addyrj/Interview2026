---

# Q054. Count Vowels in String
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Write `countVowels(str)` that returns how many vowels (a, e, i, o, u) are in a string. Case-insensitive.

```javascript
countVowels('Hello World'); // 3
```

---

## 💡 Quick Concept (2 lines only)
Loop through characters and check membership in a vowel set, or use a regex match.
हिंदी: हर अक्षर को देखो, अगर वो a, e, i, o, u में है तो गिनती बढ़ाओ।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: create a Set of vowels for O(1) lookup
// Step 2: loop over lowercase characters
// Step 3: increment counter when char is a vowel

function countVowels(str) {
  const vowels = new Set(['a', 'e', 'i', 'o', 'u']); // fast lookup
  let count = 0;                         // vowel counter
  for (const ch of str.toLowerCase()) {  // iterate each character
    if (vowels.has(ch)) count++;         // vowel found -> increment
  }
  return count;                          // total vowels
}

// ============================================
// TEST CASES
// ============================================

console.log(countVowels('Hello World')); // Expected: 3
console.log(countVowels('AEIOU'));       // Expected: 5
console.log(countVowels('rhythm'));      // Expected: 0
console.log(countVowels(''));            // Expected: 0
```

---

## 🔍 Why This Works (3 lines max)
Lowercasing makes the check case-insensitive, and the Set gives constant-time lookup per character. Total work is O(n).
हिंदी: lowercase करने से capital भी गिने जाते हैं, Set से check तेज़ होता है।

---

## ⚡ Alternative Solution
```javascript
// Regex one-liner
const countV = (s) => (s.match(/[aeiou]/gi) || []).length; // match returns null if none
console.log(countV('Hello World')); // Expected: 3
console.log(countV('xyz'));         // Expected: 0
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: match() returns null when nothing matches -> crash
// 'xyz'.match(/[aeiou]/gi).length  // TypeError: Cannot read properties of null
// ✅ Correct: fallback to empty array
console.log(('xyz'.match(/[aeiou]/gi) || []).length); // 0
```

---

## 🎯 Interview Tip (1 line)
Handle uppercase and the no-match (null) case, and mention the Set vs regex trade-off.

---

## 🔗 Related Questions
→ Q051 (reverse string) | Q053 (palindrome) | Q066 (count occurrences)
