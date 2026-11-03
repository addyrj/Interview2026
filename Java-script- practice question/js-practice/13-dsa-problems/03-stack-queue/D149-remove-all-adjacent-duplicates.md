---

# D149. Remove All Adjacent Duplicates
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #1047 | Asked: Amazon, Google, Microsoft, Bloomberg

---

## ❓ Problem
Repeatedly remove two adjacent equal letters from a string until no more can be removed. Return the final string.

```
Input:  "abbaca"
Output: "ca"      // abbaca -> aaca -> ca
```

---

## 💡 Quick Concept (2 lines only)
Scan with a stack. If the current character equals the stack top, pop (they cancel); otherwise push. The stack at the end is the answer.
हिंदी: Stack का top current जैसा हो तो pop करो, वरना push — आख़िर में stack ही answer है।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — repeat replace until stable, O(n^2)
// ============================================

function removeDuplicatesBrute(s) {
  let changed = true;                                // loop flag
  while (changed) {
    changed = false;
    for (let i = 0; i < s.length - 1; i++) {
      if (s[i] === s[i + 1]) {                       // adjacent pair found
        s = s.slice(0, i) + s.slice(i + 2);          // remove the pair
        changed = true;                              // need another pass
        break;
      }
    }
  }
  return s;
}

// ============================================
// APPROACH 2: Stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function removeDuplicates(s) {
  const stack = [];                                  // kept characters
  for (const ch of s) {
    if (stack.length && stack[stack.length - 1] === ch) {
      stack.pop();                                   // same as top -> cancel both
    } else {
      stack.push(ch);                                // different -> keep
    }
  }
  return stack.join('');                             // build result
}

// ============================================
// TEST CASES
// ============================================

console.log(removeDuplicates("abbaca"));             // ca
console.log(removeDuplicates("azxxzy"));             // ay
console.log(removeDuplicates("aaaa"));               // (empty string)
console.log(removeDuplicates("abc"));                // abc
console.log(removeDuplicates(""));                   // (empty string)
console.log(removeDuplicatesBrute("abbaca"));        // ca

// ============================================
// VARIANT: Remove K adjacent duplicates (LeetCode #1209)
// ============================================

function removeKDuplicates(s, k) {
  const stack = [];                                  // [char, count]
  for (const ch of s) {
    const top = stack[stack.length - 1];
    if (top && top[0] === ch) {
      top[1]++;                                      // extend the run
      if (top[1] === k) stack.pop();                 // run reached k -> remove
    } else {
      stack.push([ch, 1]);                           // new run
    }
  }
  return stack.map(([c, n]) => c.repeat(n)).join('');
}
console.log(removeKDuplicates("deeedbbcccbdaa", 3)); // aa
```

---

## 🔍 Why It Works
```
"abbaca"
a   push        [a]
b   push        [a,b]
b   == top pop  [a]
a   == top pop  []
c   push        [c]
a   push        [c,a]  -> "ca"
```
हिंदी: Pop होने के बाद नई pair अपने आप बन जाती है, stack यही cascading संभाल लेता है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(n)
Stack:       Time O(n)   | Space O(n)
```

---

## ⚡ Variations
```
- Remove K duplicates (#1209) — shown above
- Backspace String Compare (#844) — '#' pops the stack
- Make The String Great (#1544) — pop when letters differ only in case
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: a single left-to-right pass without a stack — misses new pairs formed after removal
// ✅ Stack handles "abba" -> "" correctly
```

---

## 🎯 Interview Tip
Say: "Removing a pair can expose a new pair, which is exactly what a stack models." Mention the two-pointer in-place variant if asked for O(1) extra space.

---

## 🔗 Related Problems
→ D148 (Decode String) | D010 (Valid Parentheses) | D150 (Simplify Path)
