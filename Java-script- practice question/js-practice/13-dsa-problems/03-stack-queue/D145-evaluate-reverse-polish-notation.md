---

# D145. Evaluate Reverse Polish Notation
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #150 | Asked: Amazon, LinkedIn, Google, Atlassian

---

## ❓ Problem
Evaluate an arithmetic expression in Reverse Polish Notation (postfix). Operators: `+ - * /`. Division truncates toward zero.

```
Input:  ["2","1","+","3","*"]
Output: 9      // (2 + 1) * 3
```

---

## 💡 Quick Concept (2 lines only)
Push numbers on a stack. On an operator, pop two operands (right first, then left), compute, push the result back. The last item left is the answer.
हिंदी: Number मिले तो push, operator मिले तो दो pop करके calculate करो और result वापस push करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — repeatedly find first operator and collapse (O(n^2))
// ============================================

function evalRPNBrute(tokens) {
  const arr = [...tokens];                           // copy so input is not mutated
  const ops = new Set(['+', '-', '*', '/']);
  while (arr.length > 1) {
    const i = arr.findIndex(t => ops.has(t));        // first operator
    const a = Number(arr[i - 2]);                    // left operand
    const b = Number(arr[i - 1]);                    // right operand
    let r;
    if (arr[i] === '+') r = a + b;
    else if (arr[i] === '-') r = a - b;
    else if (arr[i] === '*') r = a * b;
    else r = Math.trunc(a / b);                      // truncate toward zero
    arr.splice(i - 2, 3, String(r));                 // replace 3 tokens by result
  }
  return Number(arr[0]);
}

// ============================================
// APPROACH 2: Stack — O(n) time, O(n) space ✅ PREFERRED
// ============================================

function evalRPN(tokens) {
  const stack = [];                                  // operands
  for (const t of tokens) {
    if (t === '+' || t === '-' || t === '*' || t === '/') {
      const b = stack.pop();                         // right operand (popped first!)
      const a = stack.pop();                         // left operand
      if (t === '+') stack.push(a + b);              // add
      else if (t === '-') stack.push(a - b);         // subtract: a - b
      else if (t === '*') stack.push(a * b);         // multiply
      else stack.push(Math.trunc(a / b));            // divide, truncate toward zero
    } else {
      stack.push(Number(t));                         // operand -> push as number
    }
  }
  return stack.pop();                                // final result
}

// ============================================
// TEST CASES
// ============================================

console.log(evalRPN(["2","1","+","3","*"]));                  // 9
console.log(evalRPN(["4","13","5","/","+"]));                  // 6
console.log(evalRPN(["10","6","9","3","+","-11","*","/","*","17","+","5","+"])); // 22
console.log(evalRPN(["7","-2","/"]));                          // -3
console.log(evalRPN(["5"]));                                   // 5
console.log(evalRPNBrute(["2","1","+","3","*"]));              // 9
```

---

## 🔍 Why It Works
```
["4","13","5","/","+"]
push 4, 13, 5     stack [4,13,5]
"/"  b=5 a=13 -> 2     stack [4,2]
"+"  b=2 a=4  -> 6     stack [6]
```
हिंदी: Postfix में brackets की ज़रूरत नहीं — operator हमेशा अपने दो पिछले operands पर लगता है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(n)
Stack:       Time O(n)   | Space O(n)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Infix -> postfix (Shunting-yard) then evaluate
// VARIANT 2: Basic Calculator II -> D154
// VARIANT 3: Support '^' operator: stack.push(a ** b)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: a = pop(); b = pop();  -> reverses operands, breaks - and /
// ✅ b = pop() first (right), then a = pop() (left)

// ❌ Wrong: Math.floor(a / b) -> -3.5 becomes -4; need truncation
// ✅ Math.trunc(a / b)
```

---

## 🎯 Interview Tip
Say: "Right operand comes off the stack first, so I pop b then a. Division must truncate toward zero, so Math.trunc, not Math.floor."

---

## 🔗 Related Problems
→ D154 (Basic Calculator II) | D148 (Decode String) | D010 (Valid Parentheses)
