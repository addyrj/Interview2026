---

# D148. Decode String
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #394 | Asked: Amazon, Google, Microsoft, Uber, Zomato

---

## ❓ Problem
Decode a string of the form `k[encoded]`, meaning `encoded` repeated `k` times. Nesting is allowed.

```
Input:  "3[a2[c]]"
Output: "accaccacc"
```

---

## 💡 Quick Concept (2 lines only)
Use a stack. On `[`, push the current string and number then reset them. On `]`, pop, and build `prevString + currentString.repeat(k)`.
हिंदी: `[` पर अभी तक का string और number stack में रखो, `]` पर उसे repeat करके जोड़ दो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Recursion — O(output) time
// ============================================

function decodeStringRec(s) {
  let i = 0;                                         // shared index across recursion

  function helper() {
    let res = '';                                    // decoded part at this level
    let num = 0;                                     // current repeat count
    while (i < s.length) {
      const ch = s[i];
      if (ch >= '0' && ch <= '9') {
        num = num * 10 + Number(ch);                 // multi-digit numbers
        i++;
      } else if (ch === '[') {
        i++;                                         // skip '['
        const inner = helper();                      // decode the bracket content
        res += inner.repeat(num);                    // repeat it
        num = 0;                                     // reset count
      } else if (ch === ']') {
        i++;                                         // skip ']' and return to caller
        return res;
      } else {
        res += ch;                                   // normal letter
        i++;
      }
    }
    return res;
  }
  return helper();
}

// ============================================
// APPROACH 2: Stack — O(output) time ✅ PREFERRED
// ============================================

function decodeString(s) {
  const stack = [];                                  // holds [prevString, repeatCount]
  let cur = '';                                      // string being built
  let num = 0;                                       // number being read

  for (const ch of s) {
    if (ch >= '0' && ch <= '9') {
      num = num * 10 + Number(ch);                   // build multi-digit number
    } else if (ch === '[') {
      stack.push([cur, num]);                        // save state
      cur = '';                                      // start fresh inside bracket
      num = 0;
    } else if (ch === ']') {
      const [prev, k] = stack.pop();                 // restore state
      cur = prev + cur.repeat(k);                    // combine
    } else {
      cur += ch;                                     // plain letter
    }
  }
  return cur;
}

// ============================================
// TEST CASES
// ============================================

console.log(decodeString("3[a]2[bc]"));              // aaabcbc
console.log(decodeString("3[a2[c]]"));               // accaccacc
console.log(decodeString("2[abc]3[cd]ef"));          // abcabccdcdcdef
console.log(decodeString("10[a]"));                  // aaaaaaaaaa
console.log(decodeString("abc"));                    // abc
console.log(decodeStringRec("3[a2[c]]"));            // accaccacc
```

---

## 🔍 Why It Works
```
"3[a2[c]]"
3   num=3
[   push ["",3]   cur="" num=0
a   cur="a"
2   num=2
[   push ["a",2]  cur=""
c   cur="c"
]   pop ["a",2]   cur="a"+"cc"="acc"
]   pop ["",3]    cur=""+"acc"x3="accaccacc"
```
हिंदी: हर `[` एक नया level बनाता है और `]` उस level को पिछले level में जोड़ देता है।

---

## 📊 Complexity
```
Recursion: Time O(output length) | Space O(depth)
Stack:     Time O(output length) | Space O(depth)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Encode string (reverse) - run-length encoding
// VARIANT 2: Number of Atoms (#726) - similar stack of maps
// VARIANT 3: Brace Expansion - recursion with sets
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: num = Number(ch)  -> "10[a]" breaks (only reads 1 then 0)
// ✅ num = num * 10 + Number(ch)

// ❌ Wrong: not resetting num after '['  -> counts leak into next group
```

---

## 🎯 Interview Tip
Say: "Two things to save at each bracket: the string so far and the multiplier. Handle multi-digit numbers." Offer recursion as the alternative.

---

## 🔗 Related Problems
→ D145 (Evaluate RPN) | D149 (Remove Adjacent Duplicates) | D154 (Basic Calculator II)
