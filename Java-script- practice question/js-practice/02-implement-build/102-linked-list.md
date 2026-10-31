---

# Q102. Implement Linked List
# Category: Implement / Build
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement a singly `LinkedList` class with `append`, `prepend`, `remove(value)`, `reverse` and `toArray`.

```javascript
const list = new LinkedList();
list.append(1).append(2).prepend(0);
list.toArray(); // [0, 1, 2]
```

---

## 💡 Quick Concept (2 lines only)
A linked list is a chain of nodes; each node holds a `value` and a `next` pointer. No indexes — you walk node by node from `head`.
हिंदी: Linked list में हर node अपने अगले node को point करता है, index नहीं होता।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

// Step 1: Node holds value + next pointer
// Step 2: LinkedList keeps only the head
// Step 3: each method walks the chain using next

class Node {
  constructor(value) {
    this.value = value;   // data stored
    this.next = null;     // pointer to next node
  }
}

class LinkedList {
  constructor() {
    this.head = null;     // empty list
  }
  append(value) {
    const node = new Node(value);        // create new node
    if (!this.head) { this.head = node; return this; } // empty -> becomes head
    let cur = this.head;                 // start at head
    while (cur.next) cur = cur.next;     // walk to last node
    cur.next = node;                     // link at the end
    return this;                         // allow chaining
  }
  prepend(value) {
    const node = new Node(value);        // create new node
    node.next = this.head;               // point to old head
    this.head = node;                    // new node is head now
    return this;
  }
  remove(value) {
    if (!this.head) return this;         // nothing to remove
    if (this.head.value === value) { this.head = this.head.next; return this; } // remove head
    let cur = this.head;                 // start at head
    while (cur.next && cur.next.value !== value) cur = cur.next; // find previous node
    if (cur.next) cur.next = cur.next.next; // skip the target node
    return this;
  }
  reverse() {
    let prev = null, cur = this.head;    // two pointers
    while (cur) {
      const next = cur.next;             // save next
      cur.next = prev;                   // flip the pointer
      prev = cur;                        // move prev forward
      cur = next;                        // move cur forward
    }
    this.head = prev;                    // prev is the new head
    return this;
  }
  toArray() {
    const out = [];                      // result array
    for (let cur = this.head; cur; cur = cur.next) out.push(cur.value); // walk + collect
    return out;
  }
}

// ============================================
// TEST CASES
// ============================================

const list = new LinkedList();                   // empty list
list.append(1).append(2).append(3).prepend(0);   // build list
console.log(list.toArray());           // Expected: [ 0, 1, 2, 3 ]
list.remove(2);                                  // remove middle
console.log(list.toArray());           // Expected: [ 0, 1, 3 ]
list.reverse();                                  // reverse in place
console.log(list.toArray());           // Expected: [ 3, 1, 0 ]
console.log(new LinkedList().toArray()); // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
Every operation just rewires `next` pointers, so insert/remove at the head is O(1). Reverse flips each pointer while walking once.
हिंदी: हर operation सिर्फ next pointers बदलता है, और reverse एक ही चक्कर में सब pointers पलट देता है।

---

## ⚡ Alternative Solution
```javascript
// Keep a tail pointer so append becomes O(1)
class LinkedList2 {
  constructor() { this.head = null; this.tail = null; }  // track both ends
  append(value) {
    const node = { value, next: null };                  // plain object node
    if (this.tail) this.tail.next = node; else this.head = node; // link or set head
    this.tail = node;                                    // move tail
    return this;
  }
}
const l2 = new LinkedList2().append(1).append(2);
console.log(l2.head.next.value); // Expected: 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: reverse without saving next -> chain is lost
cur.next = prev;
cur = cur.next;     // goes backwards, infinite loop / lost nodes

// ✅ Correct: save next BEFORE changing the pointer
const next = cur.next;
cur.next = prev;
cur = next;
```

---

## 🎯 Interview Tip (1 line)
Say: "Insert/delete at head is O(1), access by index is O(n) — opposite of arrays."

---

## 🔗 Related Questions
→ Q100 (stack) | Q101 (queue) | Q099 (LRU cache) | Q155 (complete linked list)
