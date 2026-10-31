---

# Q157. Complete Queue Class
# Category: Complete the Code
# Difficulty: ⭐ Easy

---

## ❓ Question
Fill in the blanks for a FIFO queue.

```javascript
class Queue {
  constructor() { this.items = []; }
  enqueue(x) { this.items.____(x); }             // add at back
  dequeue() { return this.items.____(); }        // remove from front
  front() { return this.items[____]; }           // see front
  isEmpty() { return this.items.length === ____; }
  get size() { return this.items.length; }
}
```

---

## 💡 Quick Concept (2 lines only)
A queue is First-In-First-Out: add at the back, remove from the front.
हिंदी: Queue में पहले आया पहले जाता है (FIFO) — पीछे जोड़ो, आगे से निकालो।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Queue {
  constructor() { this.items = []; }               // Step 1: backing array
  enqueue(x) { this.items.push(x); }               // blank 1: add to back
  dequeue() { return this.items.shift(); }         // blank 2: remove first
  front() { return this.items[0]; }                // blank 3: first element
  isEmpty() { return this.items.length === 0; }    // blank 4: empty check
  get size() { return this.items.length; }         // count
}

// ============================================
// TEST CASES
// ============================================

const q = new Queue();
q.enqueue('a'); q.enqueue('b'); q.enqueue('c');
console.log(q.front());     // Expected: a
console.log(q.dequeue());   // Expected: a
console.log(q.size);        // Expected: 2
console.log(new Queue().dequeue()); // Expected: undefined
```

---

## 🔍 Why This Works (3 lines max)
`push` appends to the back and `shift` removes from the front, preserving arrival order. `shift` is O(n) on big arrays.
हिंदी: `push` पीछे जोड़ता है और `shift` आगे से हटाता है, इसलिए क्रम बना रहता है।

---

## ⚡ Alternative Solution
```javascript
// O(1) dequeue with an object and two pointers
class Queue2 {
  items = {}; head = 0; tail = 0;
  enqueue(x) { this.items[this.tail++] = x; }
  dequeue() { const v = this.items[this.head]; delete this.items[this.head++]; return v; }
}
const q2 = new Queue2(); q2.enqueue(1); console.log(q2.dequeue()); // 1
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using pop() makes it a stack (LIFO)
// ✅ Correct: shift() for FIFO
```

---

## 🎯 Interview Tip (1 line)
Say: "Queues drive BFS, task scheduling and the event loop's callback queue."

---

## 🔗 Related Questions
→ Q101 (queue using array) | Q156 (stack class) | Q184 (request queue) | Q216 (queue async tasks)
