---

# D140. Min Stack
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #155 | Asked: Amazon, Microsoft, Flipkart, Google

---

## ❓ Problem
Design a stack that supports `push`, `pop`, `top` and `getMin` — all in O(1) time.

```
push(-2), push(0), push(-3)
getMin() → -3
pop()
top()    → 0
getMin() → -2
```

---

## 💡 Quick Concept (2 lines only)
Keep a second "min stack" that stores the minimum seen so far at every level. When you pop the main stack, pop the min stack too, so the min always matches the current state.
हिंदी: दूसरा stack रखो जिसमें हर level का minimum हो — pop पर दोनों pop करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Brute force — O(n) getMin
// ============================================

class MinStackBrute {
  constructor() {
    this.data = [];                        // single array
  }
  push(x) { this.data.push(x); }           // O(1)
  pop() { return this.data.pop(); }        // O(1)
  top() { return this.data[this.data.length - 1]; } // O(1)
  getMin() { return Math.min(...this.data); }       // O(n) scan — too slow
}

// ============================================
// APPROACH 2: Two stacks — O(1) everything ✅ PREFERRED
// ============================================

class MinStack {
  constructor() {
    this.stack = [];     // normal values
    this.minStack = [];  // minStack[i] = min of stack[0..i]
  }

  push(x) {
    this.stack.push(x);                                   // store value
    const curMin = this.minStack.length
      ? Math.min(x, this.minStack[this.minStack.length - 1]) // compare with previous min
      : x;                                                // first element is the min
    this.minStack.push(curMin);                           // record min at this level
  }

  pop() {
    this.minStack.pop();       // drop min for this level
    return this.stack.pop();   // drop and return value
  }

  top() {
    return this.stack[this.stack.length - 1]; // peek last value
  }

  getMin() {
    return this.minStack[this.minStack.length - 1]; // peek last min
  }
}

// ============================================
// TEST CASES
// ============================================

const s = new MinStack();      // create stack
s.push(-2);                    // stack: -2
s.push(0);                     // stack: -2, 0
s.push(-3);                    // stack: -2, 0, -3
console.log(s.getMin());       // -3
s.pop();                       // remove -3
console.log(s.top());          // 0
console.log(s.getMin());       // -2

const b = new MinStackBrute(); // brute version check
b.push(5); b.push(2); b.push(7);
console.log(b.getMin());       // 2

const s2 = new MinStack();
s2.push(2); s2.push(2); s2.push(1); // duplicates of min are fine
s2.pop();
console.log(s2.getMin());      // 2
```

---

## 🔍 Why It Works
```
push -2 → stack [-2]        minStack [-2]
push  0 → stack [-2,0]      minStack [-2,-2]
push -3 → stack [-2,0,-3]   minStack [-2,-2,-3]
pop     → stack [-2,0]      minStack [-2,-2]   → min is -2 again
```
हिंदी: हर element के नीचे का minimum पहले से saved है, इसलिए pop के बाद भी min तुरंत मिल जाता है।

---

## 📊 Complexity
```
Brute force: push/pop/top O(1) | getMin O(n) | Space O(n)
Two stacks:  all ops O(1)      | Space O(n) extra
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Single stack storing [value, currentMin] pairs
class MinStackPairs {
  constructor() { this.s = []; }                         // each item = [val, min]
  push(x) {
    const min = this.s.length ? Math.min(x, this.s[this.s.length - 1][1]) : x; // new min
    this.s.push([x, min]);                               // store pair
  }
  pop() { return this.s.pop()[0]; }                      // return value only
  top() { return this.s[this.s.length - 1][0]; }         // top value
  getMin() { return this.s[this.s.length - 1][1]; }      // top min
}

// VARIANT 2: Max Stack — same idea with Math.max
// VARIANT 3: Space optimised — push to minStack only when x <= current min
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: keeping one `min` variable — after popping the min you lose the previous min
this.min = Math.min(this.min, x);

// ❌ Wrong: minStack only on strictly smaller values, then popping duplicates breaks it
// ✅ Use <= if you do the space-optimised version, or store min at every level
```

---

## 🎯 Interview Tip
Say: "A single min variable breaks on pop, so I keep a parallel stack of running minimums. Every operation is O(1) at the cost of O(n) extra space." Mention the single-stack-with-encoded-difference trick as a follow-up.

---

## 🔗 Related Problems
→ D141 (Queue using Stacks) | D142 (Stack using Queues) | D143 (Daily Temperatures)
