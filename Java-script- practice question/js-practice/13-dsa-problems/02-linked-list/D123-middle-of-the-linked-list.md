---

# D123. Middle of the Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #876 | Asked: Amazon, Microsoft, Zoho, TCS

---

## ❓ Problem
Given the head of a singly linked list, return the middle node. If there are two middle nodes, return the second one.

```
Input:  1 → 2 → 3 → 4 → 5
Output: node 3 (3 → 4 → 5)

Input:  1 → 2 → 3 → 4 → 5 → 6
Output: node 4 (4 → 5 → 6)
```

---

## 💡 Quick Concept (2 lines only)
Slow moves 1 step, fast moves 2 steps. When fast reaches the end, slow is at the middle.
हिंदी: Slow 1 step और fast 2 step चलाओ — fast जब end पर पहुँचे, slow ठीक बीच में होगा।

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

// Helper: print list from a node
function printList(head) {
  const vals = [];                                        // collected values
  while (head) { vals.push(head.val); head = head.next; } // walk
  return vals.length ? vals.join(' → ') : 'null';         // readable string
}

// ============================================
// APPROACH 1: Two passes — count then walk — O(n) time, O(1) space
// ============================================
function middleTwoPass(head) {
  let n = 0, curr = head;                     // n = length
  while (curr) { n++; curr = curr.next; }     // pass 1: count nodes
  curr = head;                                // restart
  for (let i = 0; i < Math.floor(n / 2); i++) curr = curr.next; // pass 2: walk n/2 steps
  return curr;                                // middle (second one if even)
}

// ============================================
// APPROACH 2: Slow/Fast pointers — O(n) time, O(1) space ✅ PREFERRED (one pass)
// ============================================
function middleNode(head) {
  let slow = head;                            // moves 1 step
  let fast = head;                            // moves 2 steps
  while (fast !== null && fast.next !== null) { // stop when fast cannot take 2 steps
    slow = slow.next;                         // slow: 1 step
    fast = fast.next.next;                    // fast: 2 steps
  }
  return slow;                                // slow is at the middle
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(middleTwoPass(createList([1, 2, 3, 4, 5]))));     // 3 → 4 → 5
console.log(printList(middleNode(createList([1, 2, 3, 4, 5]))));        // 3 → 4 → 5
console.log(printList(middleNode(createList([1, 2, 3, 4, 5, 6]))));     // 4 → 5 → 6
console.log(printList(middleNode(createList([1]))));                    // 1
console.log(printList(middleNode(createList([1, 2]))));                 // 2
console.log(printList(middleNode(null)));                               // null
```

---

## 🔍 Why It Works
```
List: 1 → 2 → 3 → 4 → 5
start:  slow=1, fast=1
step1:  slow=2, fast=3
step2:  slow=3, fast=5   (fast.next is null -> stop)
Middle = 3

List: 1 → 2 → 3 → 4
step1:  slow=2, fast=3
step2:  slow=3, fast=null (fast went past end) -> stop
Middle = 3 (second middle)
```
हिंदी: Fast की speed slow से दुगनी है, इसलिए fast के end पर पहुँचने तक slow आधी दूरी तय कर चुका होता है।

---

## 📊 Complexity
```
Two pass:      Time O(n) | Space O(1)
Slow/Fast:     Time O(n) | Space O(1) ← preferred (single traversal)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Return FIRST middle when length is even
function firstMiddle(head) {
  let slow = head, fast = head;                           // both start at head
  while (fast.next !== null && fast.next.next !== null) { // stop one step earlier
    slow = slow.next;                                     // slow: 1 step
    fast = fast.next.next;                                // fast: 2 steps
  }
  return slow;                                            // first middle
}
console.log(printList(firstMiddle(createList([1, 2, 3, 4]))));  // 2 → 3 → 4

// VARIANT 2: Used inside Palindrome LL (D125) and Reorder List (D129)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: loop condition checks only fast.next
while (fast.next !== null) { ... }          // crashes when head is null; also wrong parity

// ❌ Wrong: condition order — fast.next.next evaluated when fast is null
while (fast.next && fast) { ... }           // TypeError on null fast

// ✅ Correct: while (fast !== null && fast.next !== null)
```

---

## 🎯 Interview Tip
Say: "Counting length then walking n/2 is two passes; slow/fast gets it in one pass with O(1) space. For even length the loop condition `fast && fast.next` returns the second middle." This pattern is a building block for palindrome check, reorder list and merge sort on lists.

---

## 🔗 Related Problems
→ D125 (Palindrome LL) | D129 (Reorder List) | D121 (Linked List Cycle)
