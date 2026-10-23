---

# Q051. Reverse a String
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a function `reverseString(str)` that reverses a string. Do NOT use the built-in `reverse()` method for the main solution.

```javascript
reverseString('hello');    // 'olleh'
reverseString('Arjun');   // 'nujrA'
reverseString('a');       // 'a'
reverseString('');        // ''
```

---

## 💡 Quick Concept (2 lines only)
Iterate from end to start and build new string, OR split → reverse array → join. Understanding both loop and built-in approach shows depth.
हिंदी: String को end से start तक iterate करो — या split+reverse+join से करो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION 1: Loop (shows algorithm understanding)
// ============================================

function reverseString(str) {
  let result = '';
  
  // Step 1: iterate from last character to first
  for (let i = str.length - 1; i >= 0; i--) {
    result += str[i];  // Step 2: append each char to result
  }
  
  return result;
}

// ============================================
// SOLUTION 2: Reduce (functional approach)
// ============================================

function reverseStringReduce(str) {
  return str.split('').reduce((rev, char) => char + rev, '');
}

// ============================================
// SOLUTION 3: Recursion (shows recursion understanding)
// ============================================

function reverseStringRecursive(str) {
  if (str.length <= 1) return str;         // base case
  return str[str.length - 1] + reverseStringRecursive(str.slice(0, -1));
}

// ============================================
// TEST CASES
// ============================================

console.log(reverseString('hello'));        // Expected: 'olleh'
console.log(reverseString('Arjun'));        // Expected: 'nujrA'
console.log(reverseString('a'));            // Expected: 'a'
console.log(reverseString(''));             // Expected: ''
console.log(reverseString('racecar'));      // Expected: 'racecar' (palindrome)
console.log(reverseString('12345'));        // Expected: '54321'
console.log(reverseString('Hello World')); // Expected: 'dlroW olleH'
```

---

## 🔍 Why This Works (3 lines max)
Loop from `str.length - 1` to `0`, concatenating each char. Reduce builds reverse by prepending each char (`char + rev`). Both are O(n) time, O(n) space (new string).
हिंदी: End से start तक iterate करके new string बनाते हैं — O(n) time, O(n) space।

---

## ⚡ Alternative Solution
```javascript
// Built-in (one-liner — know this but explain the manual way first):
const reverse = str => str.split('').reverse().join('');
console.log(reverse('hello'));  // 'olleh'

// Two-pointer approach:
function reverseInPlace(str) {
  const arr = str.split('');  // strings are immutable — convert to array
  let left = 0, right = arr.length - 1;
  
  while (left < right) {
    [arr[left], arr[right]] = [arr[right], arr[left]];  // swap
    left++;
    right--;
  }
  
  return arr.join('');
}

// Using spread + reverse:
const reverse2 = str => [...str].reverse().join('');
// Handles Unicode better than split('') for emoji/multi-byte chars:
console.log([...'👋🏽'].reverse().join(''));  // '🏽👋' ← incorrect for emoji pair
// For proper Unicode: use Array.from(str) or [...str]
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: trying to reverse string in place (strings are immutable in JS)
let str = 'hello';
str[0] = 'H';  // silently fails! str is still 'hello'

// ✅ Must create new string or convert to array first

// ❌ Wrong: not handling edge cases
function reverse(str) {
  if (!str) return str;  // handle null/undefined
  // ...
}

// ❌ Wrong: using split('') for emoji (splits emoji into bytes)
'👋'.split('');    // ['👋'] — actually fine for this emoji
'👋🏽'.split(''); // ['👋', '🏽', '‍'] — oops! combines multiple code points
// ✅ Use [...str] or Array.from(str) for Unicode correctness
```

---

## 🎯 Interview Tip (1 line)
Say: "Show the loop version to demonstrate understanding, then mention split/reverse/join as production one-liner; mention Unicode edge case with spread operator."

---

## 🔗 Related Questions
→ Q052 (reverse words) | Q053 (palindrome) | Q054 (count vowels)
