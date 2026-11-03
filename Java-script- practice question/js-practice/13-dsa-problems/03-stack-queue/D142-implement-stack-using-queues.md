---

# D142. Implement Stack using Queues
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #225 | Asked: Amazon, Microsoft, Bloomberg

---

## ❓ Problem
Implement a LIFO stack using only queue operations (enqueue at back, dequeue from front). Support `push`, `pop`, `top`, `empty`.

```
push(1), push(2)
top() → 2
pop() → 2
empty() → false
```

---

## 💡 Quick Concept (2 lines only)
After pushing a new element into a single queue, rotate the queue (size-1) times so the new element comes to the front. Then pop/top are just dequeue/peek.
हिंदी: Push के बाद queue को घुमाओ ताकि नया element सबसे आगे आ जाए — तब pop = dequeue।

---

## ✅ Solution

```javascript
// Note: JS arrays used as queue: push() = enqueue, shift() = dequeue.

// ============================================
// APPROACH 1: Two queues — push O(n), pop O(1)
// ============================================

class StackTwoQueues {
  constructor() {
    this.q1 = [];  // main queue (front = top of stack)
    this.q2 = [];  // helper queue
  }
  push(x) {
    this.q2.push(x);                                   // new item goes in empty helper
    while (this.q1.length) this.q2.push(this.q1.shift()); // append old items behind it
    [this.q1, this.q2] = [this.q2, this.q1];           // swap roles
  }
  pop() { return this.q1.shift(); }                    // front is the top
  top() { return this.q1[0]; }                         // peek front
  empty() { return this.q1.length === 0; }
}

// ============================================
// APPROACH 2: One queue with rotation ✅ PREFERRED
// ============================================

class MyStack {
  constructor() {
    this.q = [];  // single queue
  }

  push(x) {
    this.q.push(x);                          // enqueue at back
    for (let i = 0; i < this.q.length - 1; i++) {
      this.q.push(this.q.shift());           // rotate older items behind the new one
    }
  }

  pop() {
    return this.q.shift();                   // front = most recent push
  }

  top() {
    return this.q[0];                        // peek front
  }

  empty() {
    return this.q.length === 0;              // nothing left
  }
}

// ============================================
// TEST CASES
// ============================================

const s = new MyStack();
s.push(1);                     // q: [1]
s.push(2);                     // q: [2,1]
s.push(3);                     // q: [3,2,1]
console.log(s.top());          // 3
console.log(s.pop());          // 3
console.log(s.pop());          // 2
console.log(s.empty());        // false
console.log(s.pop());          // 1
console.log(s.empty());        // true

const t = new StackTwoQueues();
t.push(10); t.push(20);
console.log(t.pop());          // 20
console.log(t.top());          // 10
```

---

## 🔍 Why It Works
```
push 1 → [1]
push 2 → [1,2] → rotate once → [2,1]
push 3 → [2,1,3] → rotate twice → [3,2,1]
front is always newest => LIFO
```
हिंदी: हर push के बाद queue का front सबसे नया element होता है, इसलिए pop सीधा dequeue है।

---

## 📊 Complexity
```
Two queues:   push O(n) | pop/top O(1) | Space O(n)
One queue:    push O(n) | pop/top O(1) | Space O(n)
```
(`shift()` on a JS array is O(n) in worst case; use a linked-list queue for true O(1).)

---

## ⚡ Variations

```javascript
// VARIANT 1: Make pop costly, push cheap
// push: q.push(x)   pop: rotate (len-1) items to back, then shift()
// VARIANT 2: Queue using Stacks -> D141
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: rotating `this.q.length` times (full circle) -> order is unchanged
for (let i = 0; i < this.q.length; i++) ...

// ✅ Rotate length - 1 times so only the new element stays in front
```

---

## 🎯 Interview Tip
Say: "One queue is enough: after enqueue, rotate n-1 elements behind the new one. Push is O(n), pop O(1)." Mention the alternative trade-off (cheap push, costly pop).

---

## 🔗 Related Problems
→ D141 (Queue using Stacks) | D140 (Min Stack) | D152 (Design Circular Queue)
