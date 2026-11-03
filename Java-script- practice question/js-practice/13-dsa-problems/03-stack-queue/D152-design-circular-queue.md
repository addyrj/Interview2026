---

# D152. Design Circular Queue
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #622 | Asked: Amazon, Microsoft, Apple, Samsung

---

## ❓ Problem
Design a fixed-size circular queue with `enQueue`, `deQueue`, `Front`, `Rear`, `isEmpty`, `isFull`.

```
k = 3
enQueue(1) → true, enQueue(2) → true, enQueue(3) → true
enQueue(4) → false (full)
Rear() → 3, isFull() → true
deQueue() → true, enQueue(4) → true, Rear() → 4
```

---

## 💡 Quick Concept (2 lines only)
Use a fixed array with a `head` index and a `count`. The tail slot is `(head + count) % k`, so indices wrap around and freed slots get reused.
हिंदी: Array + head + count रखो; modulo से index घूमकर वापस शुरू में आ जाता है।

---

## ✅ Solution

```javascript
// ============================================
// APPROACH 1: Naive array queue — deQueue uses shift() O(n)
// ============================================

class NaiveQueue {
  constructor(k) { this.k = k; this.a = []; }        // dynamic array with capacity check
  enQueue(x) { if (this.a.length === this.k) return false; this.a.push(x); return true; }
  deQueue() { if (!this.a.length) return false; this.a.shift(); return true; } // O(n) shift
  Front() { return this.a.length ? this.a[0] : -1; }
  Rear() { return this.a.length ? this.a[this.a.length - 1] : -1; }
  isEmpty() { return this.a.length === 0; }
  isFull() { return this.a.length === this.k; }
}

// ============================================
// APPROACH 2: Circular buffer with head + count — all O(1) ✅ PREFERRED
// ============================================

class MyCircularQueue {
  constructor(k) {
    this.k = k;                          // capacity
    this.data = new Array(k).fill(0);    // fixed storage
    this.head = 0;                       // index of front element
    this.count = 0;                      // number of stored elements
  }

  enQueue(value) {
    if (this.isFull()) return false;                     // no room
    const tail = (this.head + this.count) % this.k;      // next free slot (wraps)
    this.data[tail] = value;                             // store
    this.count++;                                        // size grows
    return true;
  }

  deQueue() {
    if (this.isEmpty()) return false;                    // nothing to remove
    this.head = (this.head + 1) % this.k;                // advance head (wraps)
    this.count--;                                        // size shrinks
    return true;
  }

  Front() {
    return this.isEmpty() ? -1 : this.data[this.head];   // oldest element
  }

  Rear() {
    if (this.isEmpty()) return -1;                       // nothing stored
    return this.data[(this.head + this.count - 1) % this.k]; // newest element
  }

  isEmpty() { return this.count === 0; }                 // no elements
  isFull() { return this.count === this.k; }             // at capacity
}

// ============================================
// TEST CASES
// ============================================

const q = new MyCircularQueue(3);
console.log(q.enQueue(1));     // true
console.log(q.enQueue(2));     // true
console.log(q.enQueue(3));     // true
console.log(q.enQueue(4));     // false
console.log(q.Rear());         // 3
console.log(q.isFull());       // true
console.log(q.deQueue());      // true
console.log(q.enQueue(4));     // true  (reuses freed slot)
console.log(q.Rear());         // 4
console.log(q.Front());        // 2
const e = new MyCircularQueue(1);
console.log(e.Front(), e.Rear(), e.isEmpty()); // -1 -1 true
const n = new NaiveQueue(2);
n.enQueue(9);
console.log(n.Front());        // 9
```

---

## 🔍 Why It Works
```
k=3 slots: [_, _, _]  head=0 count=0
enQ 1,2,3 -> [1,2,3] count=3 (full)
deQ       -> head=1 count=2
enQ 4     -> tail=(1+2)%3=0 -> [4,2,3]  front=2 rear=4
```
हिंदी: Modulo की वजह से array के आख़िर के बाद index 0 पर लौट आते हैं, इसलिए जगह बर्बाद नहीं होती।

---

## 📊 Complexity
```
Naive array: enQueue O(1) | deQueue O(n) | Space O(k)
Circular:    all ops O(1)                | Space O(k)
```

---

## ⚡ Variations
```
- Circular Deque (#641): add insertFront/insertLast with (head - 1 + k) % k
- Using head + tail pointers needs one wasted slot (or a count) to tell full from empty
- Ring buffer for streaming/logging
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: using only head and tail -> full and empty look identical
// ✅ Track count (or leave one slot empty)

// ❌ Wrong: Rear = data[(head + count) % k]  -> that is the NEXT free slot
// ✅ (head + count - 1) % k
```

---

## 🎯 Interview Tip
Say: "I track a count so full and empty are unambiguous, and use modulo for wrap-around — everything is O(1)." Clarify the capacity and empty return value (-1).

---

## 🔗 Related Problems
→ D141 (Queue using Stacks) | D142 (Stack using Queues) | D147 (Sliding Window Maximum)
