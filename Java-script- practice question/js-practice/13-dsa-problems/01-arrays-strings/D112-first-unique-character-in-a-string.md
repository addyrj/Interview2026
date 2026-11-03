---

# D112. First Unique Character in a String
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #387 | Asked: Amazon, Bloomberg, Microsoft, Walmart

---

## ❓ Problem
Return the index of the first non-repeating character in `s`, or -1 if none exists.

```
Input:  "leetcode"
Output: 0   ('l')

Input:  "loveleetcode"
Output: 2   ('v')

Input:  "aabb"
Output: -1
```

---

## 💡 Quick Concept (2 lines only)
Pass 1: count each character. Pass 2: return the first index whose count is 1.
हिंदी: पहले हर character गिनो, फिर left से पहला character ढूँढो जिसकी count 1 हो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute Force — O(n²) time, O(1) space
// ============================================

function firstUniqCharBrute(s) {
  for (let i = 0; i < s.length; i++) {               // candidate character
    let unique = true;                               // assume unique
    for (let j = 0; j < s.length; j++) {             // compare with all others
      if (i !== j && s[i] === s[j]) { unique = false; break; } // repeat found
    }
    if (unique) return i;                            // first unique index
  }
  return -1;                                         // none unique
}

// ============================================
// APPROACH 2: Two-pass frequency count — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function firstUniqChar(s) {
  const count = new Map();                           // char → frequency
  for (const ch of s) {                              // pass 1: count
    count.set(ch, (count.get(ch) || 0) + 1);         // increment
  }
  for (let i = 0; i < s.length; i++) {               // pass 2: left to right
    if (count.get(s[i]) === 1) return i;             // first char with count 1
  }
  return -1;                                         // no unique char
}

// ============================================
// APPROACH 3: indexOf check — O(n·26) with lowercase letters
// ============================================

function firstUniqCharIndexOf(s) {
  let best = Infinity;                               // smallest unique index
  for (const ch of 'abcdefghijklmnopqrstuvwxyz') {   // each possible letter
    const first = s.indexOf(ch);                     // first position
    if (first !== -1 && first === s.lastIndexOf(ch)) { // appears exactly once
      best = Math.min(best, first);                  // keep smallest index
    }
  }
  return best === Infinity ? -1 : best;              // convert no-result to -1
}

// ============================================
// TEST CASES
// ============================================

console.log(firstUniqChar('leetcode'));              // 0
console.log(firstUniqChar('loveleetcode'));          // 2
console.log(firstUniqChar('aabb'));                  // -1
console.log(firstUniqChar(''));                      // -1
console.log(firstUniqCharBrute('abcabcd'));          // 6
console.log(firstUniqCharIndexOf('dddccdbba'));      // 8
```

---

## 🔍 Why It Works
```
"loveleetcode"
counts: l:2 o:2 v:1 e:4 t:1 c:1 d:1
scan: l(2) o(2) v(1) → index 2
```
Counting first guarantees we know every character's total before choosing the earliest unique one.
हिंदी: Count पहले पूरा बनाओ, फिर order में check करो — इसलिए पहला unique मिलता है।

---

## 📊 Complexity
```
Brute Force: Time O(n²) | Space O(1)
Two-pass:    Time O(n)  | Space O(1) (alphabet bounded) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: First non-repeating character itself (return char, or '' if none)
function firstUniqLetter(s) {
  const i = firstUniqChar(s);                        // reuse index solution
  return i === -1 ? '' : s[i];                       // map index to character
}
console.log(firstUniqLetter('swiss'));               // "w"

// VARIANT 2: Most frequent character
function mostFrequent(s) {
  const count = new Map();                           // frequencies
  let best = '', max = 0;                            // answer
  for (const ch of s) {                              // scan
    const c = (count.get(ch) || 0) + 1;              // updated count
    count.set(ch, c);                                // store
    if (c > max) { max = c; best = ch; }             // track maximum
  }
  return best;
}
console.log(mostFrequent('banana'));                 // "a"
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: returning the character instead of the index
// ❌ Wrong: iterating the Map for "first" — Map keeps insertion order but
//          you still need the string index; iterate the string instead
// ✅ Correct: second pass over the string itself
```

---

## 🎯 Interview Tip
Say: "Two passes with a frequency map — O(n) time. Space is O(1) because the alphabet is fixed." Ask whether the input is lowercase only.

---

## 🔗 Related Problems
→ D106 (Valid Anagram) | D107 (Group Anagrams) | D102 (Contains Duplicate)
