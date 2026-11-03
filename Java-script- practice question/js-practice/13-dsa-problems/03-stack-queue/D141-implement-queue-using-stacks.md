---

# D141. Implement Queue using Stacks
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #232 | Asked: Amazon, Microsoft, Adobe, Paytm

---

## ❓ Problem
Implement a FIFO queue using only two stacks. Support `push`, `pop`, `peek`, `empty`.

```
push(1), push(2)
peek() → 1
pop()  → 1
empty() → false
```

---

## 💡 Quick Concept (2 lines only)
Use an `inStack` for pushes and an `outStack` for pops. Only when `outStack` is empty, move everything from `inStack` — this reverses the order so the oldest element ends up on top.
हिंदी: Push के लिए एक stack, pop के लिए दूसरा — out खाली हो तभी in से सब कुछ transfer करो।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Move on every push — push O(n), pop O(1)
// ============================================

class QueueCostlyPush {
  constructor() {
    this.main = [];                      // holds items, oldest on top
  }
  push(x) {
    const tmp = [];                      // temporary stack
    while (this.main.length) tmp.push(this.main.pop()); // empty main into tmp
    this.main.push(x);                   // put new item at the bottom
    while (tmp.length) this.main.push(tmp.pop());       // restore old items on top
  }
  pop() { return this.main.pop(); }      // oldest is on top
  peek() { return this.main[this.main.length - 1]; }
  empty() { return this.main.length === 0; }
}

// ============================================
// APPROACH 2: Two stacks, lazy transfer — amortized O(1) ✅ PREFERRED
// ============================================

class MyQueue {
  constructor() {
    this.inStack = [];   // receives new pushes
    this.outStack = [];  // serves pop/peek (oldest on top)
  }

  push(x) {
    this.inStack.push(x);  // always O(1)
  }

  _move() {
    if (this.outStack.length === 0) {                 // only refill when empty
      while (this.inStack.length) {
        this.outStack.push(this.inStack.pop());       // reverses order
      }
    }
  }

  pop() {
    this._move();                  // make sure out has data
    return this.outStack.pop();    // oldest element
  }

  peek() {
    this._move();                                     // make sure out has data
    return this.outStack[this.outStack.length - 1];   // oldest without removing
  }

  empty() {
    return this.inStack.length === 0 && this.outStack.length === 0; // both empty
  }
}

// ============================================
// TEST CASES
// ============================================

const q = new MyQueue();
q.push(1);                     // in: [1]
q.push(2);                     // in: [1,2]
console.log(q.peek());         // 1
console.log(q.pop());          // 1
console.log(q.empty());        // false
q.push(3);                     // in: [3], out: [2]
console.log(q.pop());          // 2  (not 3 — FIFO preserved)
console.log(q.pop());          // 3
console.log(q.empty());        // true

const c = new QueueCostlyPush();
c.push(7); c.push(8);
console.log(c.pop());          // 7
```

---

## 🔍 Why It Works
```
push 1,2,3  → in [1,2,3]   out []
pop         → move: out [3,2,1] → pop gives 1
push 4      → in [4]       out [3,2]   (4 must wait behind 2,3)
pop         → 2, pop → 3, then out empty → move 4
```
हिंदी: दो बार reverse करने से LIFO, FIFO बन जाता है; हर element ज़्यादा से ज़्यादा एक बार move होता है।

---

## 📊 Complexity
```
Costly push: push O(n) | pop O(1) | Space O(n)
Lazy two-stack: push O(1) | pop/peek amortized O(1) | Space O(n)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Stack using Queues -> D142
// VARIANT 2: Queue with getMax in O(1) — keep a monotonic deque alongside (see D147)
// VARIANT 3: Size helper
// size() { return this.inStack.length + this.outStack.length; }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: moving inStack -> outStack on every pop even if outStack is non-empty
// This breaks order: new items land under older ones.

// ✅ Move ONLY when outStack is empty
```

---

## 🎯 Interview Tip
Say: "Each element is moved at most once from in to out, so pop is amortized O(1)." Interviewers love the word "amortized" here.

---

## 🔗 Related Problems
→ D140 (Min Stack) | D142 (Stack using Queues) | D152 (Design Circular Queue)
