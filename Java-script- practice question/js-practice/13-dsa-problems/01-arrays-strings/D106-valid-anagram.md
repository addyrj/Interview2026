---

# D106. Valid Anagram
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #242 | Asked: Amazon, Microsoft, Bloomberg, Swiggy

---

## ❓ Problem
Given strings `s` and `t`, return `true` if `t` is an anagram of `s` (same letters, same counts).

```
Input:  s = "anagram", t = "nagaram"
Output: true

Input:  s = "rat", t = "car"
Output: false
```

---

## 💡 Quick Concept (2 lines only)
Count letters of s up, count letters of t down; if every count ends at 0 they are anagrams. Different lengths → false immediately.
हिंदी: s के letters गिनो, t के letters घटाओ — सब zero हो तो anagram।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Sort both — O(n log n) time, O(n) space
// ============================================

function isAnagramSort(s, t) {
  if (s.length !== t.length) return false;           // length mismatch → no
  const a = s.split('').sort().join('');             // sorted s
  const b = t.split('').sort().join('');             // sorted t
  return a === b;                                    // equal if anagrams
}

// ============================================
// APPROACH 2: Frequency count — O(n) time, O(1) space (26 letters) ✅ PREFERRED
// ============================================

function isAnagram(s, t) {
  if (s.length !== t.length) return false;           // quick reject
  const count = new Array(26).fill(0);               // one counter per letter a-z
  for (let i = 0; i < s.length; i++) {               // single loop over both strings
    count[s.charCodeAt(i) - 97]++;                   // letter in s → +1
    count[t.charCodeAt(i) - 97]--;                   // letter in t → -1
  }
  return count.every((c) => c === 0);                // all zero → anagram
}

// ============================================
// Unicode-safe version using a Map
// ============================================

function isAnagramMap(s, t) {
  if (s.length !== t.length) return false;           // quick reject
  const map = new Map();                             // char → count
  for (const ch of s) map.set(ch, (map.get(ch) || 0) + 1); // count s
  for (const ch of t) {                              // consume with t
    if (!map.get(ch)) return false;                  // missing or exhausted → false
    map.set(ch, map.get(ch) - 1);                    // decrement
  }
  return true;                                       // all matched
}

// ============================================
// TEST CASES
// ============================================

console.log(isAnagram('anagram', 'nagaram'));        // true
console.log(isAnagram('rat', 'car'));                // false
console.log(isAnagram('a', 'ab'));                   // false
console.log(isAnagram('', ''));                      // true
console.log(isAnagramSort('listen', 'silent'));      // true
console.log(isAnagramMap('héllo', 'olléh'));         // true
```

---

## 🔍 Why Counting Works
```
s="rat", t="car"
r:+1  c:-1
a:+1  a:-1
t:+1  r:-1
Result: r=0, a=0, t=+1, c=-1 → not all zero → false
```
हिंदी: एक भी count non-zero रहा तो दोनों strings के letters अलग हैं।

---

## 📊 Complexity
```
Sort:      Time O(n log n) | Space O(n)
Count[26]: Time O(n)       | Space O(1) ← preferred
Map:       Time O(n)       | Space O(k) distinct chars
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Ransom Note (LeetCode #383) — can magazine build the note?
function canConstruct(note, magazine) {
  const count = new Array(26).fill(0);               // letter counts of magazine
  for (const ch of magazine) count[ch.charCodeAt(0) - 97]++; // count
  for (const ch of note) {                           // consume for the note
    if (--count[ch.charCodeAt(0) - 97] < 0) return false; // ran out
  }
  return true;                                       // enough letters
}
console.log(canConstruct('aa', 'aab'));              // true
console.log(canConstruct('aa', 'ab'));               // false
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: comparing only Sets of characters — "aab" vs "abb" would pass
new Set(s).size === new Set(t).size;

// ✅ Correct: compare counts, not just presence
```

---

## 🎯 Interview Tip
Say: "Sort is simplest; frequency array is O(n) time, O(1) space for lowercase letters. For Unicode I'd use a Map." Ask about the character set first.

---

## 🔗 Related Problems
→ D107 (Group Anagrams) | D112 (First Unique Character) | D108 (Valid Palindrome)
