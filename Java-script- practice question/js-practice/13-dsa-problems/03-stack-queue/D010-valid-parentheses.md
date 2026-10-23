---

# D010. Valid Parentheses
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #20 | Asked: Almost EVERY company

---

## ❓ Problem
Given a string `s` containing only `(`, `)`, `{`, `}`, `[`, `]`, determine if the input string is valid. Valid means: open brackets must be closed by the same type in the correct order.

```javascript
isValid('()');        // true
isValid('()[]{}');   // true
isValid('(]');        // false
isValid('([)]');      // false
isValid('{[]}');      // true
isValid('');          // true
```

---

## 💡 Quick Concept (2 lines only)
Use a stack. Push open brackets. On closing bracket: if top of stack is matching open bracket, pop it. At end, stack must be empty.
हिंदी: Stack use करो — open bracket push करो, closing bracket आने पर stack top match करो और pop करो।

---

## ✅ Solution

```javascript
// ============================================
// SOLUTION — O(n) time, O(n) space
// ============================================

function isValid(s) {
  const stack = [];
  
  // Map: closing bracket → its matching opening bracket
  const matchMap = {
    ')': '(',
    '}': '{',
    ']': '['
  };
  
  for (const char of s) {
    if (char === '(' || char === '{' || char === '[') {
      stack.push(char);           // open bracket — push to stack
    } else {
      // closing bracket — check if it matches the top of stack
      if (stack.length === 0 || stack[stack.length - 1] !== matchMap[char]) {
        return false;             // mismatch or empty stack
      }
      stack.pop();                // valid match — pop the open bracket
    }
  }
  
  return stack.length === 0;      // valid only if all brackets matched
}

// ============================================
// TEST CASES
// ============================================

console.log(isValid('()'));       // true
console.log(isValid('()[]{}')); // true
console.log(isValid('(]'));       // false
console.log(isValid('([)]'));     // false — ([ ok, then ) doesn't match [
console.log(isValid('{[]}'));     // true
console.log(isValid(''));         // true (empty = valid)
console.log(isValid('{'));        // false (unclosed bracket)

// WALKTHROUGH for '([)]':
// '(' → stack: ['(']
// '[' → stack: ['(', '[']
// ')' → matchMap[')']='(', top='[' → '(' ≠ '[' → return false ✅
```

---

## 🔍 Why Stack Works
Brackets are LIFO — the most recently opened bracket must be closed first. Stack naturally tracks this: push open brackets, pop when matching close bracket arrives.
हिंदी: Brackets LIFO होते हैं — last open bracket पहले close होना चाहिए — Stack इसी के लिए perfect है।

---

## 📊 Complexity
```
Time:  O(n) — one pass through string
Space: O(n) — stack can hold all chars in worst case: "((((("
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Minimum removals to make valid
function minRemoveToMakeValid(s) {
  const arr = s.split('');
  const stack = [];  // stack of indices
  
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] === '(') stack.push(i);
    else if (arr[i] === ')') {
      if (stack.length > 0) stack.pop();  // matched
      else arr[i] = '';                   // unmatched closing → remove
    }
  }
  // Remaining in stack = unmatched opening brackets
  for (const i of stack) arr[i] = '';
  return arr.join('');
}
console.log(minRemoveToMakeValid('lee(t(c)o)de)'));  // 'lee(t(c)o)de'

// VARIANT 2: Longest valid parentheses substring length (LeetCode #32)
function longestValidParentheses(s) {
  const stack = [-1];  // base index for calculating lengths
  let max = 0;
  
  for (let i = 0; i < s.length; i++) {
    if (s[i] === '(') {
      stack.push(i);
    } else {
      stack.pop();
      if (stack.length === 0) stack.push(i);  // new base
      else max = Math.max(max, i - stack[stack.length - 1]);
    }
  }
  return max;
}
console.log(longestValidParentheses(')()())'));  // 4

// VARIANT 3: Generate all valid parentheses (LeetCode #22)
function generateParentheses(n) {
  const result = [];
  function backtrack(str, open, close) {
    if (str.length === 2 * n) { result.push(str); return; }
    if (open < n) backtrack(str + '(', open + 1, close);
    if (close < open) backtrack(str + ')', open, close + 1);
  }
  backtrack('', 0, 0);
  return result;
}
console.log(generateParentheses(3));  // ['((()))','(()())','(())()','()(())','()()()']
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: only handling one type of bracket
function isValid(s) {
  let count = 0;
  for (const c of s) {
    if (c === '(') count++;
    else count--;
    if (count < 0) return false;
  }
  return count === 0;
}
// Works for () only — fails for ([)] which should be false

// ❌ Wrong: forgetting empty stack check before pop
if (stack[stack.length - 1] !== matchMap[char]) return false;
// stack might be empty! stack[undefined] = undefined
// ✅ Always check stack.length === 0 first

// ❌ Wrong: returning true when stack is non-empty at end
// '(' never matched — stack has '(' but we return true without checking
// ✅ return stack.length === 0
```

---

## 🎯 Interview Tip
Say: "Classic stack problem — push open brackets, pop on matching close; two failure cases: closing without matching open (empty stack or mismatch) and leftover opens at end."

---

## 🔗 Related Problems
→ D011 (Min Stack) | D012 (Daily Temperatures) | D013 (Largest Rectangle in Histogram)
