---

# D127. Remove Duplicates from Sorted List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #83 | Asked: Amazon, Microsoft, Infosys, Wipro

---

## ❓ Problem
Given the head of a sorted linked list, delete all duplicates so each value appears only once. Return the sorted list.

```
Input:  1 → 1 → 2 → 3 → 3
Output: 1 → 2 → 3
```

---

## 💡 Quick Concept (2 lines only)
Because the list is sorted, duplicates are adjacent. If curr.val equals curr.next.val, skip the next node; otherwise move forward.
हिंदी: List sorted है, तो duplicates पास-पास होते हैं — अगर अगला node same value का है तो उसे skip कर दो, वरना आगे बढ़ो।

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

// ============================================
// APPROACH 1: Set of seen values (works even if NOT sorted) — O(n) time, O(n) space
// ============================================
function deleteDuplicatesSet(head) {
  const seen = new Set();                     // values already kept
  const dummy = new ListNode(0, head);        // dummy head
  let prev = dummy;                           // last kept node
  while (prev.next) {                         // look at the next node
    if (seen.has(prev.next.val)) {            // value already seen
      prev.next = prev.next.next;             // unlink duplicate
    } else {
      seen.add(prev.next.val);                // remember value
      prev = prev.next;                       // keep node, advance
    }
  }
  return dummy.next;                          // head
}

// ============================================
// APPROACH 2: Single pass using sortedness — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function deleteDuplicates(head) {
  let curr = head;                            // walker
  while (curr !== null && curr.next !== null) { // need a next node to compare
    if (curr.val === curr.next.val) {         // next is a duplicate
      curr.next = curr.next.next;             // skip it (stay on curr to check again)
    } else {
      curr = curr.next;                       // different value: move on
    }
  }
  return head;                                // head never changes
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(deleteDuplicatesSet(createList([1, 1, 2, 3, 3]))));  // 1 → 2 → 3
console.log(printList(deleteDuplicates(createList([1, 1, 2, 3, 3]))));     // 1 → 2 → 3
console.log(printList(deleteDuplicates(createList([1, 1, 1]))));           // 1
console.log(printList(deleteDuplicates(createList([1, 2, 3]))));           // 1 → 2 → 3
console.log(printList(deleteDuplicates(createList([]))));                  // null
console.log(printList(deleteDuplicates(createList([5]))));                 // 5
```

---

## 🔍 Why It Works
```
1 → 1 → 2 → 3 → 3
curr=1, next=1 equal  -> 1 → 2 → 3 → 3 (stay at curr)
curr=1, next=2 differ -> move
curr=2, next=3 differ -> move
curr=3, next=3 equal  -> 3 → null
Result: 1 → 2 → 3
```
हिंदी: Equal मिलने पर curr वहीं रुकता है ताकि तीन-चार duplicates भी एक-एक करके हट जाएँ।

---

## 📊 Complexity
```
Set:        Time O(n) | Space O(n)
Sorted scan: Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Remove ALL nodes that have duplicates (LeetCode #82)
function deleteAllDuplicates(head) {
  const dummy = new ListNode(0, head);        // dummy for head removal
  let prev = dummy;                           // last node known to be unique
  while (head) {                              // walk
    if (head.next && head.val === head.next.val) { // start of a duplicate run
      while (head.next && head.val === head.next.val) head = head.next; // skip whole run
      prev.next = head.next;                  // drop the run, including its last node
    } else {
      prev = prev.next;                       // unique node: keep it
    }
    head = head.next;                         // advance
  }
  return dummy.next;                          // head
}
console.log(printList(deleteAllDuplicates(createList([1, 2, 3, 3, 4, 4, 5]))));  // 1 → 2 → 5
console.log(printList(deleteAllDuplicates(createList([1, 1, 1, 2, 3]))));        // 2 → 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: advancing curr after deleting
if (curr.val === curr.next.val) { curr.next = curr.next.next; curr = curr.next; }
// skips checking the new next -> misses 1→1→1

// ❌ Wrong: not checking curr.next !== null -> TypeError on curr.next.val

// ✅ Correct: advance only in the else branch
```

---

## 🎯 Interview Tip
Say: "Sorted means duplicates are adjacent, so one pass with O(1) space is enough. If the list were unsorted I'd use a Set." Clarify whether to keep one copy (#83) or remove all (#82).

---

## 🔗 Related Problems
→ D120 (Merge Two Sorted Lists) | D134 (Delete Node in LL) | D124 (Remove Nth From End)
