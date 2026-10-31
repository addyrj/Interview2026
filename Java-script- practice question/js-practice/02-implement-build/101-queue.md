---

# Q101. Implement Queue Using Array
# Category: Implement / Build
# Difficulty: ⭐ Easy

---

## ❓ Question
Implement a `Queue` class (FIFO) using an array with `enqueue`, `dequeue`, `peek`, `isEmpty` and `size`.
First item added must be the first item removed.

```javascript
const q = new Queue();
q.enqueue(1).enqueue(2);
q.dequeue(); // 1
```

---

## 💡 Quick Concept (2 lines only)
Queue = First In First Out. Add at the back (`push`), remove from the front (`shift`).
हिंदी: Queue में जो पहले आता है वही पहले निकलता है — जैसे टिकट की लाइन।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: keep items in an internal array
// Step 2: enqueue adds at the end, dequeue removes from the front
// Step 3: helper methods read state without changing it

class Queue {
  constructor() {
    this.items = [];                 // internal storage
  }
  enqueue(item) {
    this.items.push(item);           // add to the back
    return this;                     // return this so calls can be chained
  }
  dequeue() {
    return this.items.shift();       // remove front (undefined if empty)
  }
  peek() {
    return this.items[0];            // look at front without removing
  }
  isEmpty() {
    return this.items.length === 0;  // true when nothing inside
  }
  size() {
    return this.items.length;        // number of items
  }
}

// ============================================
// TEST CASES
// ============================================

const q = new Queue();                          // create queue
q.enqueue(1).enqueue(2).enqueue(3);             // add 3 items
console.log(q.dequeue());  // Expected: 1
console.log(q.peek());     // Expected: 2
console.log(q.size());     // Expected: 2
console.log(q.isEmpty());  // Expected: false
q.dequeue(); q.dequeue();                       // empty the queue
console.log(q.dequeue());  // Expected: undefined
console.log(q.isEmpty());  // Expected: true
```

---

## 🔍 Why This Works (3 lines max)
`push` adds at the end and `shift` removes from the start, which gives FIFO order. Returning `this` from `enqueue` allows chaining.
हिंदी: push पीछे जोड़ता है और shift आगे से निकालता है, इसलिए FIFO order मिलता है।

---

## ⚡ Alternative Solution
```javascript
// O(1) dequeue using an object + head/tail pointers (shift() is O(n))
class FastQueue {
  constructor() { this.data = {}; this.head = 0; this.tail = 0; } // pointers
  enqueue(x) { this.data[this.tail++] = x; }                      // add at tail
  dequeue() {
    if (this.head === this.tail) return undefined;  // empty check
    const x = this.data[this.head];                 // read front
    delete this.data[this.head++];                  // remove + move head
    return x;                                       // return value
  }
}
const f = new FastQueue(); f.enqueue('a'); f.enqueue('b');
console.log(f.dequeue()); // Expected: a
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: pop() removes from the back -> that is a Stack (LIFO), not Queue
dequeue() { return this.items.pop(); }

// ✅ Correct: shift() removes from the front
dequeue() { return this.items.shift(); }
```

---

## 🎯 Interview Tip (1 line)
Mention that `shift()` is O(n) and show the head/tail pointer version for O(1) dequeue.

---

## 🔗 Related Questions
→ Q100 (stack) | Q095 (async queue) | Q102 (linked list) | Q157 (complete queue class)
