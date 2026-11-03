---

# D154. Basic Calculator II
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #227 | Asked: Amazon, Microsoft, Facebook, Google

---

## ❓ Problem
Evaluate a string expression with non-negative integers and `+ - * /`, with spaces. No parentheses. Integer division truncates toward zero.

```
Input:  "3+2*2"
Output: 7
```

---

## 💡 Quick Concept (2 lines only)
Remember the previous operator. When a number ends: `+` push n, `-` push -n, `*` / `/` combine with the stack top. The answer is the sum of the stack.
हिंदी: पिछला operator याद रखो — `*` और `/` तुरंत top पर लगाओ, `+`/`-` के numbers push करके आख़िर में जोड़ दो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — two passes (collapse * and / first, then + and -)
// ============================================

function calculateBrute(s) {
  const tokens = s.replace(/\s+/g, '').match(/\d+|[+\-*\/]/g); // numbers and operators
  const stage = [Number(tokens[0])];                 // numbers separated by + or -
  const signs = [];                                  // the + / - operators
  for (let i = 1; i < tokens.length; i += 2) {
    const op = tokens[i], n = Number(tokens[i + 1]);
    if (op === '*') stage[stage.length - 1] *= n;    // high priority now
    else if (op === '/') stage[stage.length - 1] = Math.trunc(stage[stage.length - 1] / n);
    else { signs.push(op); stage.push(n); }          // defer + / -
  }
  let res = stage[0];
  for (let i = 0; i < signs.length; i++) {
    res += signs[i] === '+' ? stage[i + 1] : -stage[i + 1]; // low priority pass
  }
  return res;
}

// ============================================
// APPROACH 2: Single pass with stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function calculate(s) {
  const stack = [];                                  // signed numbers to be summed
  let num = 0;                                       // number being read
  let op = '+';                                      // operator before `num`

  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (ch >= '0' && ch <= '9') {
      num = num * 10 + Number(ch);                   // build multi-digit number
    }
    // when we hit an operator (or end), apply the PREVIOUS operator
    if ((ch < '0' || ch > '9') && ch !== ' ' || i === s.length - 1) {
      if (op === '+') stack.push(num);               // add later
      else if (op === '-') stack.push(-num);         // subtract = add negative
      else if (op === '*') stack.push(stack.pop() * num);            // combine with top
      else if (op === '/') stack.push(Math.trunc(stack.pop() / num)); // truncate toward 0
      op = ch;                                       // remember current operator
      num = 0;                                       // reset number
    }
  }
  return stack.reduce((a, b) => a + b, 0);           // sum everything
}

// ============================================
// TEST CASES
// ============================================

console.log(calculate("3+2*2"));                     // 7
console.log(calculate(" 3/2 "));                     // 1
console.log(calculate(" 3+5 / 2 "));                 // 5
console.log(calculate("14-3/2"));                    // 13
console.log(calculate("42"));                        // 42
console.log(calculate("1-1+1"));                     // 1
console.log(calculateBrute("3+2*2"));                // 7
console.log(calculateBrute("14-3/2"));               // 13
```

---

## 🔍 Why It Works
```
"3+2*2"
read 3, hit '+': op was '+' -> push 3   stack [3]   op='+'
read 2, hit '*': op was '+' -> push 2   stack [3,2] op='*'
read 2, end    : op was '*' -> pop 2 * 2 = 4 push   stack [3,4]
sum = 7
```
हिंदी: `*` और `/` का result तुरंत top में मिल जाता है, इसलिए precedence अपने आप सही रहती है।

---

## 📊 Complexity
```
Brute force: Time O(n) | Space O(n)  (two passes)
Stack:       Time O(n) | Space O(n)  (single pass)
O(1) space version: track `last` and `result` variables instead of a stack
```

---

## ⚡ Variations

```javascript
// VARIANT 1: O(1) space — keep result and last term
function calculateO1(s) {
  let result = 0, last = 0, num = 0, op = '+';       // running total, last term
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (ch >= '0' && ch <= '9') num = num * 10 + Number(ch);
    if ((ch < '0' || ch > '9') && ch !== ' ' || i === s.length - 1) {
      if (op === '+') { result += last; last = num; }
      else if (op === '-') { result += last; last = -num; }
      else if (op === '*') last = last * num;
      else last = Math.trunc(last / num);
      op = ch; num = 0;
    }
  }
  return result + last;
}
console.log(calculateO1("3+2*2"));                   // 7
// VARIANT 2: Basic Calculator I (#224) with parentheses — stack of sign contexts
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: applying the CURRENT operator to the number just read (off by one)
// ✅ Apply the PREVIOUS operator when a new operator (or end of string) arrives

// ❌ Wrong: forgetting to process the last number when the string has no trailing operator
// ❌ Wrong: Math.floor for negatives -> use Math.trunc
```

---

## 🎯 Interview Tip
Say: "I apply the previous operator when I see the next one. Multiplication and division resolve immediately against the top of the stack; additions are deferred and summed at the end." Offer the O(1) space refinement.

---

## 🔗 Related Problems
→ D145 (Evaluate RPN) | D148 (Decode String) | D010 (Valid Parentheses)
