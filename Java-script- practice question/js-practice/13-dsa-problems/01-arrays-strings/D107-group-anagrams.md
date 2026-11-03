---

# D107. Group Anagrams
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐ Medium | LeetCode #49 | Asked: Amazon, Facebook, Uber, Google

---

## ❓ Problem
Given an array of strings, group the anagrams together. Any order is fine.

```
Input:  ["eat","tea","tan","ate","nat","bat"]
Output: [["eat","tea","ate"],["tan","nat"],["bat"]]
```

---

## 💡 Quick Concept (2 lines only)
Anagrams share the same canonical key — either the sorted string or a 26-letter count signature. Use a Map from key → list of words.
हिंदी: हर word की एक "key" बनाओ (sorted letters), same key वाले words एक group में।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Sorted key — O(n · k log k) time, O(n·k) space
// ============================================

function groupAnagramsSort(strs) {
  const map = new Map();                             // key → group array
  for (const word of strs) {                         // process each word
    const key = word.split('').sort().join('');      // "eat" → "aet"
    if (!map.has(key)) map.set(key, []);             // first word with this key
    map.get(key).push(word);                         // add word to its group
  }
  return [...map.values()];                          // list of groups
}

// ============================================
// APPROACH 2: Count key — O(n · k) time, O(n·k) space ✅ PREFERRED
// ============================================

function groupAnagrams(strs) {
  const map = new Map();                             // key → group array
  for (const word of strs) {                         // process each word
    const count = new Array(26).fill(0);             // letter counts
    for (const ch of word) count[ch.charCodeAt(0) - 97]++; // count letters
    const key = count.join('#');                     // unique signature e.g. "1#0#0#..."
    if (!map.has(key)) map.set(key, []);             // create group if missing
    map.get(key).push(word);                         // add to group
  }
  return [...map.values()];                          // return all groups
}

// ============================================
// TEST CASES
// ============================================

console.log(groupAnagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat']));
// [ [ 'eat', 'tea', 'ate' ], [ 'tan', 'nat' ], [ 'bat' ] ]

console.log(groupAnagrams(['']));                    // [ [ '' ] ]
console.log(groupAnagrams(['a']));                   // [ [ 'a' ] ]
console.log(groupAnagramsSort(['abc', 'bca', 'xyz'])); // [ [ 'abc', 'bca' ], [ 'xyz' ] ]
console.log(groupAnagrams([]));                      // []
```

---

## 🔍 Why It Works
```
"eat" → sorted "aet"
"tea" → sorted "aet"   ← same key → same group
"tan" → sorted "ant"
"bat" → sorted "abt"
```
Anagrams have identical letter multisets, so any canonical form of that multiset is a valid key.
हिंदी: Anagrams के letters same होते हैं, इसलिए sorted form भी same आता है।

---

## 📊 Complexity
```
Sorted key: Time O(n · k log k) | Space O(n·k)
Count key:  Time O(n · k)       | Space O(n·k) ← preferred
(n = number of words, k = max word length)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Count how many anagram groups exist
function countGroups(strs) {
  const keys = new Set(strs.map((w) => w.split('').sort().join(''))); // unique keys
  return keys.size;                                  // number of groups
}
console.log(countGroups(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])); // 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: count key without a separator — [1,11] and [11,1] both become "111"
count.join('');

// ✅ Correct: use a separator
count.join('#');
```

---

## 🎯 Interview Tip
Say: "Hash map keyed by a canonical form. Sorting is easy; count signature is faster for long words." Clarify lowercase-only input.

---

## 🔗 Related Problems
→ D106 (Valid Anagram) | D112 (First Unique Character) | D001 (Two Sum)
