---

# D120. Merge Two Sorted Lists
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #21 | Asked: Amazon, Microsoft, Flipkart, Adobe

---

## ❓ Problem
Given the heads of two sorted linked lists, merge them into one sorted list by splicing together the existing nodes. Return the head of the merged list.

```
Input:  l1 = 1 → 2 → 4, l2 = 1 → 3 → 4
Output: 1 → 1 → 2 → 3 → 4 → 4
```

---

## 💡 Quick Concept (2 lines only)
Use a dummy head node and a tail pointer. Compare the two current nodes, attach the smaller one to tail, advance that list. When one list ends, attach the rest of the other.
हिंदी: Dummy node बनाओ, दोनों lists के heads compare करो, छोटा वाला जोड़ते जाओ, बचा हुआ बाकी list सीधे attach कर दो।

---

## ✅ Solution

```javascript
// Node class (given in interview):
class ListNode {
  constructor(val, next = null) {
    this.val = val;     // value stored in node
    this.next = next;   // pointer to next node
  }
}

// Helper: build list from array
function createList(arr) {
  const dummy = new ListNode(0);   // dummy head to simplify building
  let curr = dummy;                // tail pointer
  for (const v of arr) {           // go through each value
    curr.next = new ListNode(v);   // append new node
    curr = curr.next;              // move tail forward
  }
  return dummy.next;               // real head (null if arr empty)
}

// Helper: print list as string
function printList(head) {
  const vals = [];                                   // collect values
  while (head) { vals.push(head.val); head = head.next; } // walk list
  return vals.length ? vals.join(' → ') : 'null';    // readable output
}

// ============================================
// APPROACH 1: Brute force — collect, sort, rebuild
// O(n log n) time, O(n) space (ignores that lists are already sorted)
// ============================================
function mergeBrute(l1, l2) {
  const vals = [];                                   // all values together
  while (l1) { vals.push(l1.val); l1 = l1.next; }    // read list 1
  while (l2) { vals.push(l2.val); l2 = l2.next; }    // read list 2
  vals.sort((a, b) => a - b);                        // sort numerically
  return createList(vals);                           // rebuild new list
}

// ============================================
// APPROACH 2: Iterative two-pointer with dummy — O(n+m) time, O(1) space ✅ PREFERRED
// ============================================
function mergeTwoLists(l1, l2) {
  const dummy = new ListNode(-1);   // dummy avoids special case for head
  let tail = dummy;                 // tail of the merged list

  while (l1 !== null && l2 !== null) {   // both lists still have nodes
    if (l1.val <= l2.val) {              // l1 node is smaller (<= keeps it stable)
      tail.next = l1;                    // attach l1 node
      l1 = l1.next;                      // advance l1
    } else {
      tail.next = l2;                    // attach l2 node
      l2 = l2.next;                      // advance l2
    }
    tail = tail.next;                    // move tail to newly attached node
  }

  tail.next = l1 !== null ? l1 : l2;     // attach whichever list has leftovers
  return dummy.next;                     // skip dummy
}

// ============================================
// APPROACH 3: Recursive — O(n+m) time, O(n+m) stack space
// ============================================
function mergeRecursive(l1, l2) {
  if (l1 === null) return l2;            // l1 empty -> rest is l2
  if (l2 === null) return l1;            // l2 empty -> rest is l1
  if (l1.val <= l2.val) {                // l1 head is smaller
    l1.next = mergeRecursive(l1.next, l2); // merge rest after l1
    return l1;                           // l1 is head of this merge
  }
  l2.next = mergeRecursive(l1, l2.next); // else l2 head is smaller
  return l2;                             // l2 is head of this merge
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(mergeBrute(createList([1, 2, 4]), createList([1, 3, 4]))));      // 1 → 1 → 2 → 3 → 4 → 4
console.log(printList(mergeTwoLists(createList([1, 2, 4]), createList([1, 3, 4]))));   // 1 → 1 → 2 → 3 → 4 → 4
console.log(printList(mergeRecursive(createList([1, 2, 4]), createList([1, 3, 4]))));  // 1 → 1 → 2 → 3 → 4 → 4
console.log(printList(mergeTwoLists(createList([]), createList([]))));                 // null
console.log(printList(mergeTwoLists(createList([]), createList([0]))));                // 0
console.log(printList(mergeTwoLists(createList([5, 6]), createList([1, 2, 3]))));      // 1 → 2 → 3 → 5 → 6
```

---

## 🔍 Why It Works
```
l1: 1→2→4   l2: 1→3→4   dummy→
Step 1: 1(l1) <= 1(l2)  -> dummy→1(l1)
Step 2: 2(l1) >  1(l2)  -> dummy→1→1(l2)
Step 3: 2(l1) <= 3(l2)  -> dummy→1→1→2
Step 4: 4(l1) >  3(l2)  -> dummy→1→1→2→3
Step 5: 4(l1) <= 4(l2)  -> ...→3→4(l1); l1 ends
Leftover l2 (4) attached directly.
```
हिंदी: हर step में दोनों में से छोटा node चुनो; एक list खत्म होते ही दूसरी को सीधे जोड़ दो क्योंकि वो पहले से sorted है।

---

## 📊 Complexity
```
Brute force: Time O((n+m) log(n+m)) | Space O(n+m)
Iterative:   Time O(n+m)            | Space O(1) ← preferred
Recursive:   Time O(n+m)            | Space O(n+m) — call stack
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Merge K sorted lists (see D133) — repeatedly use mergeTwoLists
// VARIANT 2: Merge into a descending list — reverse the result or compare with >=
// VARIANT 3: Remove duplicates while merging — skip when tail.val === chosen.val
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no dummy node -> messy head handling, easy null bugs
let head = l1.val < l2.val ? l1 : l2;   // crashes if either list is null

// ❌ Wrong: forgetting leftover nodes
// loop ends but tail.next never set -> remaining nodes are lost

// ✅ Correct: dummy node + attach leftover with tail.next = l1 || l2
```

---

## 🎯 Interview Tip
Say: "I'll use a dummy node so I never special-case the head, then a tail pointer. At the end I attach the non-empty remainder in O(1) since it's already sorted. This reuses nodes, so space is O(1)." Follow-up: merge K lists (D133).

---

## 🔗 Related Problems
→ D133 (Merge K Sorted Lists) | D127 (Remove Duplicates from Sorted List) | D128 (Add Two Numbers)
