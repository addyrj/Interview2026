---

# D134. Delete Node in a Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #237 | Asked: Amazon, Microsoft, Apple, Adobe

---

## ❓ Problem
Delete a node (not the tail) from a singly linked list when you are given only access to that node, not the head. All values are unique.

```
Input:  head = 4 → 5 → 1 → 9, node = 5
Output: 4 → 1 → 9
```

---

## 💡 Quick Concept (2 lines only)
You cannot reach the previous node, so copy the next node's value into this node, then skip the next node.
हिंदी: Previous node तक नहीं पहुँच सकते, इसलिए अगले node की value इसी node में copy करो और अगले node को हटा दो।

---

## ✅ Solution

```javascript
// Node class (given in interview):
class ListNode {
  constructor(val, next = null) {
    this.val = val;     // node value
    this.next = next;   // next pointer
  }
}

// Helper: build list from array
function createList(arr) {
  const dummy = new ListNode(0);              // dummy head
  let curr = dummy;                           // tail pointer
  for (const v of arr) {                      // each value
    curr.next = new ListNode(v);              // append node
    curr = curr.next;                         // advance tail
  }
  return dummy.next;                          // real head
}

// Helper: print list
function printList(head) {
  const vals = [];                                        // collected values
  while (head) { vals.push(head.val); head = head.next; } // walk
  return vals.length ? vals.join(' → ') : 'null';         // readable string
}

// Helper: find node by value (only for tests)
function findNode(head, val) {
  while (head && head.val !== val) head = head.next;      // search
  return head;                                            // node or null
}

// ============================================
// APPROACH 1: Standard delete with head access — O(n) time, O(1) space
// (Shown for comparison; needs the head, which this problem does NOT give)
// ============================================
function deleteWithHead(head, target) {
  const dummy = new ListNode(0, head);        // dummy handles head deletion
  let prev = dummy;                           // trailing pointer
  while (prev.next && prev.next !== target) prev = prev.next; // find node before target
  if (prev.next) prev.next = prev.next.next;  // unlink target
  return dummy.next;                          // head
}

// ============================================
// APPROACH 2: Copy next value and skip next — O(1) time, O(1) space ✅ PREFERRED
// ============================================
function deleteNode(node) {
  node.val = node.next.val;                   // overwrite value with next node's value
  node.next = node.next.next;                 // unlink the next node (now a duplicate)
}

// ============================================
// TEST CASES
// ============================================
let h1 = createList([4, 5, 1, 9]);
console.log(printList(deleteWithHead(h1, findNode(h1, 5))));  // 4 → 1 → 9

let h2 = createList([4, 5, 1, 9]);
deleteNode(findNode(h2, 5));
console.log(printList(h2));                   // 4 → 1 → 9

let h3 = createList([4, 5, 1, 9]);
deleteNode(findNode(h3, 1));
console.log(printList(h3));                   // 4 → 5 → 9

let h4 = createList([4, 5, 1, 9]);
deleteNode(findNode(h4, 4));                  // deleting the head node via its reference
console.log(printList(h4));                   // 5 → 1 → 9

let h5 = createList([0, 1]);
deleteNode(findNode(h5, 0));
console.log(printList(h5));                   // 1
```

---

## 🔍 Why It Works
```
4 → 5 → 1 → 9, node = 5
node.val = node.next.val  : 4 → 1 → 1 → 9   (5 overwritten with 1)
node.next = node.next.next: 4 → 1 → 9        (second 1 dropped)
```
हिंदी: हम असल में node को नहीं हटाते — उसकी value बदलकर अगले node को हटाते हैं; बाहर से list वैसी ही दिखती है।

---

## 📊 Complexity
```
With head:      Time O(n) | Space O(1)
Copy-and-skip:  Time O(1) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Delete all nodes with a given value (LeetCode #203) - head available
function removeElements(head, val) {
  const dummy = new ListNode(0, head);        // dummy for head removals
  let curr = dummy;                           // walker
  while (curr.next) {                         // look ahead
    if (curr.next.val === val) curr.next = curr.next.next; // skip matching node
    else curr = curr.next;                    // otherwise advance
  }
  return dummy.next;                          // head
}
console.log(printList(removeElements(createList([1, 2, 6, 3, 4, 5, 6]), 6)));  // 1 → 2 → 3 → 4 → 5
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: node = node.next;     // only reassigns the local variable, list unchanged

// ❌ Wrong: calling deleteNode on the tail -> node.next is null -> TypeError
//    (the problem guarantees the node is not the tail)

// ✅ Correct: node.val = node.next.val; node.next = node.next.next;
```

---

## 🎯 Interview Tip
Say: "Without the head I can't fix the previous node's pointer, so I copy the successor's value into this node and bypass the successor. It only works for non-tail nodes, and the node object that actually disappears is the next one."

---

## 🔗 Related Problems
→ D124 (Remove Nth From End) | D127 (Remove Duplicates from Sorted List) | D020 (Reverse Linked List)
