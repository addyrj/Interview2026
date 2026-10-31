---

# Q155. Complete Linked List
# Category: Complete the Code
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Fill in the blanks for `append` and `toArray`.

```javascript
class Node { constructor(val) { this.val = val; this.next = ____; } }

class LinkedList {
  constructor() { this.head = null; this.size = 0; }
  append(val) {
    const node = new ____(val);
    if (!this.head) this.head = ____;            // first node
    else {
      let cur = this.head;
      while (cur.____) cur = cur.next;           // go to last
      cur.next = node;
    }
    this.size++;
  }
  toArray() {
    const out = []; let cur = this.head;
    while (cur) { out.push(cur.val); cur = cur.____; }
    return out;
  }
}
```

---

## 💡 Quick Concept (2 lines only)
A linked list is nodes where each holds a value and a pointer to the next node; the end has `next = null`.
हिंदी: Linked list में हर node अपनी value और अगले node का pointer रखता है, आखिरी का next null होता है।

---

## ✅ Answer / Solution

```javascript
// ============================================
// SOLUTION
// ============================================

class Node {
  constructor(val) { this.val = val; this.next = null; } // blank 1: no next yet
}

class LinkedList {
  constructor() { this.head = null; this.size = 0; }     // Step 1: empty list
  append(val) {
    const node = new Node(val);                          // blank 2: create node
    if (!this.head) this.head = node;                    // blank 3: becomes head
    else {
      let cur = this.head;                               // start at head
      while (cur.next) cur = cur.next;                   // blank 4: walk to tail
      cur.next = node;                                   // link new node
    }
    this.size++;                                         // track length
  }
  toArray() {
    const out = []; let cur = this.head;                 // traverse from head
    while (cur) { out.push(cur.val); cur = cur.next; }   // blank 5: step forward
    return out;
  }
}

// ============================================
// TEST CASES
// ============================================

const l = new LinkedList();
l.append(1); l.append(2); l.append(3);
console.log(l.toArray());     // Expected: [ 1, 2, 3 ]
console.log(l.size);          // Expected: 3
console.log(new LinkedList().toArray()); // Expected: []
```

---

## 🔍 Why This Works (3 lines max)
`append` walks until the node whose `next` is null and links the new node there. Traversal follows `next` until it hits null.
हिंदी: tail तक `next` follow करके नया node जोड़ा जाता है।

---

## ⚡ Alternative Solution
```javascript
// Keep a tail pointer for O(1) append
// append(v){ const n = new Node(v); this.tail ? (this.tail.next = n) : (this.head = n); this.tail = n; }
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: while (cur) ends with cur = null, so you lose the last node to link to
// ✅ Correct: while (cur.next)
```

---

## 🎯 Interview Tip (1 line)
Say: "Append is O(n) without a tail pointer, O(1) with one; insert/delete at head is O(1)."

---

## 🔗 Related Questions
→ Q102 (linked list) | Q156 (stack class) | Q157 (queue class) | Q152 (LRU cache)
