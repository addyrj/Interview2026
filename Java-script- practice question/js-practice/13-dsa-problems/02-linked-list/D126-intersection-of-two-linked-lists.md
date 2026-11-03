---

# D126. Intersection of Two Linked Lists
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #160 | Asked: Amazon, Microsoft, Google, Flipkart

---

## ❓ Problem
Given the heads of two singly linked lists, return the node where they intersect (share the same node, not just equal values). If they do not intersect, return null.

```
A:      4 → 1 ↘
                 8 → 4 → 5
B: 5 → 6 → 1 ↗

Output: node 8
```

---

## 💡 Quick Concept (2 lines only)
Two pointers: when one reaches the end, redirect it to the other list's head. Both then travel lenA + lenB and meet at the intersection (or both at null).
हिंदी: दोनों pointers अपनी list खत्म होने पर दूसरी list के head से शुरू करते हैं — दोनों की total दूरी बराबर हो जाती है, इसलिए intersection पर मिलते हैं।

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

// Helper: build list from array, ending at `tail` (shared node chain or null)
function createList(arr, tail = null) {
  let head = tail;                            // build from the back
  for (let i = arr.length - 1; i >= 0; i--) { // reverse iteration
    head = new ListNode(arr[i], head);        // prepend node
  }
  return head;                                // head of list
}

// Build test data: shared part 8 → 4 → 5
const shared = createList([8, 4, 5]);         // common tail
const A = createList([4, 1], shared);         // 4 → 1 → 8 → 4 → 5
const B = createList([5, 6, 1], shared);      // 5 → 6 → 1 → 8 → 4 → 5

// ============================================
// APPROACH 1: Hash Set — O(n+m) time, O(n) space
// ============================================
function getIntersectionSet(headA, headB) {
  const seen = new Set();                     // nodes of list A
  for (let p = headA; p; p = p.next) seen.add(p);  // store every node reference
  for (let p = headB; p; p = p.next) {        // walk B
    if (seen.has(p)) return p;                // first node of B also in A
  }
  return null;                                // no intersection
}

// ============================================
// APPROACH 2: Two pointers switching heads — O(n+m) time, O(1) space ✅ PREFERRED
// ============================================
function getIntersectionNode(headA, headB) {
  if (!headA || !headB) return null;          // empty list can't intersect
  let a = headA;                              // pointer on list A
  let b = headB;                              // pointer on list B
  while (a !== b) {                           // until they meet (or both null)
    a = a === null ? headB : a.next;          // after A ends, jump to head of B
    b = b === null ? headA : b.next;          // after B ends, jump to head of A
  }
  return a;                                   // intersection node or null
}

// ============================================
// TEST CASES
// ============================================
console.log(getIntersectionSet(A, B).val);    // 8
console.log(getIntersectionNode(A, B).val);   // 8
console.log(getIntersectionNode(A, B) === shared);  // true (same node reference)

const C = createList([1, 2, 3]);              // no shared nodes
const D = createList([1, 2, 3]);              // same values, different nodes
console.log(getIntersectionNode(C, D));       // null
console.log(getIntersectionNode(null, D));    // null
console.log(getIntersectionNode(shared, shared).val);  // 8 (same list)
```

---

## 🔍 Why It Works
```
lenA = 5 (4,1,8,4,5)  lenB = 6 (5,6,1,8,4,5)  shared length = 3
Pointer a travels: A (5 nodes) then B up to intersection (3 nodes before it) = 5 + 3 = 8
Pointer b travels: B (6 nodes) then A up to intersection (2 nodes before it) = 6 + 2 = 8
Same distance => both land on node 8 together.
No intersection: both walk lenA + lenB and become null at the same time -> loop ends with null.
```
हिंदी: दोनों pointers की कुल यात्रा lenA + lenB होती है, इसलिए अलग-अलग लंबाई का फर्क अपने-आप खत्म हो जाता है।

---

## 📊 Complexity
```
Hash Set:     Time O(n+m) | Space O(n)
Two pointers: Time O(n+m) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Length difference approach — advance the longer list first
function lengthOf(h) { let n = 0; while (h) { n++; h = h.next; } return n; } // list length

function getIntersectionByLength(headA, headB) {
  let la = lengthOf(headA), lb = lengthOf(headB);   // both lengths
  while (la > lb) { headA = headA.next; la--; }     // skip extra nodes in A
  while (lb > la) { headB = headB.next; lb--; }     // skip extra nodes in B
  while (headA !== headB) {                         // walk together
    headA = headA.next; headB = headB.next;         // advance both
  }
  return headA;                                     // intersection or null
}
console.log(getIntersectionByLength(A, B).val);     // 8
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: comparing values
if (a.val === b.val) return a;           // 1 === 1 matches but they are different nodes

// ❌ Wrong: jumping when a.next === null instead of a === null
// then the pointers never both become null in the no-intersection case => infinite loop

// ✅ Correct: compare node references (===) and switch after reaching null
```

---

## 🎯 Interview Tip
Say: "Intersection means same node reference, not same value. The head-switching trick equalizes path lengths so I don't need to compute lengths — O(1) space, one clean loop." Draw both lists with the shared tail to explain.

---

## 🔗 Related Problems
→ D121 (Linked List Cycle) | D122 (Cycle II) | D124 (Remove Nth From End)
