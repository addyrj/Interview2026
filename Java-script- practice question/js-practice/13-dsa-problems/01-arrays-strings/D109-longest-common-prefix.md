---

# D109. Longest Common Prefix
# Category: DSA — Arrays & Strings
# Difficulty: ⭐ Easy | LeetCode #14 | Asked: Amazon, Google, Microsoft, TCS

---

## ❓ Problem
Find the longest common prefix among an array of strings. Return "" if none.

```
Input:  ["flower","flow","flight"]
Output: "fl"

Input:  ["dog","racecar","car"]
Output: ""
```

---

## 💡 Quick Concept (2 lines only)
Take the first string as the candidate prefix and shrink it until every other string starts with it. Or compare column by column.
हिंदी: पहली string को prefix मानो, जब तक बाकी सब उससे शुरू न हों, उसे छोटा करते जाओ।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Horizontal scan (shrink prefix) — O(S) time, O(1) space
// ============================================

function longestCommonPrefixShrink(strs) {
  if (strs.length === 0) return '';                  // no strings
  let prefix = strs[0];                              // candidate prefix
  for (let i = 1; i < strs.length; i++) {            // check each other string
    while (!strs[i].startsWith(prefix)) {            // prefix doesn't match yet
      prefix = prefix.slice(0, -1);                  // drop last char
      if (prefix === '') return '';                  // nothing in common
    }
  }
  return prefix;                                     // survived all strings
}

// ============================================
// APPROACH 2: Vertical scan (column by column) — O(S) time, O(1) space ✅ PREFERRED
// ============================================

function longestCommonPrefix(strs) {
  if (strs.length === 0) return '';                  // no strings
  for (let i = 0; i < strs[0].length; i++) {         // each column of the first string
    const ch = strs[0][i];                           // char to match
    for (let j = 1; j < strs.length; j++) {          // check all other strings
      if (i === strs[j].length || strs[j][i] !== ch) { // too short or mismatch
        return strs[0].slice(0, i);                  // prefix ends before column i
      }
    }
  }
  return strs[0];                                    // whole first string is common
}

// ============================================
// APPROACH 3: Sort — O(n log n · k) time
// ============================================

function longestCommonPrefixSort(strs) {
  if (strs.length === 0) return '';                  // no strings
  const sorted = [...strs].sort();                   // lexicographic order
  const first = sorted[0];                           // smallest string
  const last = sorted[sorted.length - 1];            // largest string
  let i = 0;                                         // match length
  while (i < first.length && first[i] === last[i]) i++; // compare extremes only
  return first.slice(0, i);                          // common part of extremes
}

// ============================================
// TEST CASES
// ============================================

console.log(JSON.stringify(longestCommonPrefix(['flower', 'flow', 'flight']))); // "fl"
console.log(JSON.stringify(longestCommonPrefix(['dog', 'racecar', 'car'])));    // ""
console.log(JSON.stringify(longestCommonPrefix(['a'])));                        // "a"
console.log(JSON.stringify(longestCommonPrefix(['', 'b'])));                    // ""
console.log(JSON.stringify(longestCommonPrefixShrink(['interview', 'internet', 'internal']))); // "inter"
console.log(JSON.stringify(longestCommonPrefixSort(['abc', 'abd', 'ab'])));     // "ab"
```

---

## 🔍 Why It Works
```
["flower","flow","flight"]
col0: f f f ✓
col1: l l l ✓
col2: o o i ✗ → stop → "fl"
```
The common prefix of all strings equals the common prefix of the lexicographically smallest and largest ones (sort approach).
हिंदी: जैसे ही किसी column में अक्षर अलग मिले, वहीं रुक जाओ।

---

## 📊 Complexity
```
Horizontal: Time O(S) | Space O(1)
Vertical:   Time O(S) | Space O(1) ← preferred (S = total characters)
Sort:       Time O(n log n · k) | Space O(n)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Longest common SUFFIX — reverse each string, reuse the prefix solution
function longestCommonSuffix(strs) {
  const rev = strs.map((s) => s.split('').reverse().join('')); // reverse every string
  const p = longestCommonPrefix(rev);                          // prefix of reversed
  return p.split('').reverse().join('');                       // reverse back
}
console.log(longestCommonSuffix(['running', 'jumping', 'ping'])); // "ping"
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not checking string length → strs[j][i] is undefined, may pass wrongly
// ❌ Wrong: forgetting empty array / empty string cases
// ✅ Correct: check i === strs[j].length before comparing
```

---

## 🎯 Interview Tip
Say: "Vertical scan stops at the first mismatch, so it never does extra work. Worst case is O(total characters)." Mention the Trie alternative for many queries.

---

## 🔗 Related Problems
→ D106 (Valid Anagram) | D108 (Valid Palindrome) | D107 (Group Anagrams)
