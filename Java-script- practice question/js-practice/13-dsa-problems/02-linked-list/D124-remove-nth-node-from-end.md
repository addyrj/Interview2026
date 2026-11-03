---

# D124. Remove Nth Node From End
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #19 | Asked: Amazon, Microsoft, Facebook, Swiggy

---

## ❓ Problem
Given the head of a linked list, remove the nth node from the end of the list and return its head.

```
Input:  1 → 2 → 3 → 4 → 5, n = 2
Output: 1 → 2 → 3 → 5
```

---

## 💡 Quick Concept (2 lines only)
Move fast n+1 steps ahead of slow (starting both at a dummy). Then move both together; when fast hits null, slow is just before the node to delete.
हिंदी: Fast को n+1 step आगे भेजो, फिर दोनों साथ चलाओ — fast null पर पहुँचे तो slow ठीक delete होने वाले node से पहले होगा।

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
// APPROACH 1: Two passes — length then delete — O(n) time, O(1) space
// ============================================
function removeNthTwoPass(head, n) {
  let len = 0, curr = head;                   // count length
  while (curr) { len++; curr = curr.next; }   // pass 1
  const dummy = new ListNode(0, head);        // dummy handles deleting the head
  curr = dummy;                               // start at dummy
  for (let i = 0; i < len - n; i++) curr = curr.next; // stop before target node
  curr.next = curr.next.next;                 // unlink target
  return dummy.next;                          // new head
}

// ============================================
// APPROACH 2: One pass, fast/slow gap of n — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function removeNthFromEnd(head, n) {
  const dummy = new ListNode(0, head);        // dummy so head removal works
  let fast = dummy;                           // leading pointer
  let slow = dummy;                           // trailing pointer

  for (let i = 0; i < n + 1; i++) fast = fast.next; // create gap of n+1 nodes

  while (fast !== null) {                     // move together until fast falls off
    fast = fast.next;                         // advance fast
    slow = slow.next;                         // advance slow
  }

  slow.next = slow.next.next;                 // slow is right before target: skip it
  return dummy.next;                          // new head
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(removeNthTwoPass(createList([1, 2, 3, 4, 5]), 2)));  // 1 → 2 → 3 → 5
console.log(printList(removeNthFromEnd(createList([1, 2, 3, 4, 5]), 2)));  // 1 → 2 → 3 → 5
console.log(printList(removeNthFromEnd(createList([1, 2, 3, 4, 5]), 5)));  // 2 → 3 → 4 → 5 (remove head)
console.log(printList(removeNthFromEnd(createList([1, 2, 3, 4, 5]), 1)));  // 1 → 2 → 3 → 4 (remove tail)
console.log(printList(removeNthFromEnd(createList([1]), 1)));              // null
console.log(printList(removeNthFromEnd(createList([1, 2]), 1)));           // 1
```

---

## 🔍 Why It Works
```
1→2→3→4→5, n=2, dummy=D
Gap n+1 = 3: fast moves D→1→2→3 (fast=3, slow=D)
Move together:
  fast=4, slow=1
  fast=5, slow=2
  fast=null, slow=3
slow=3 is just before node 4 (2nd from end) -> 3.next = 5
Result: 1→2→3→5
```
हिंदी: दोनों pointers के बीच हमेशा n+1 का gap रहता है, इसलिए fast के end पर पहुँचते ही slow target से ठीक पहले होता है।

---

## 📊 Complexity
```
Two pass:  Time O(n) | Space O(1)
One pass:  Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Find the nth node from end (do not delete)
function nthFromEnd(head, n) {
  let fast = head, slow = head;               // both at head
  for (let i = 0; i < n; i++) fast = fast.next; // gap of n
  while (fast) { fast = fast.next; slow = slow.next; } // slide window
  return slow.val;                            // nth from end
}
console.log(nthFromEnd(createList([1, 2, 3, 4, 5]), 2));  // 4

// VARIANT 2: Rotate list by k (LeetCode #61) — uses the same length/gap idea
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: no dummy node -> removing the head (n == length) breaks
let slow = head;                // slow can never be "before head"

// ❌ Wrong: gap of n instead of n+1 when starting at dummy
// slow lands ON the target, so you cannot unlink it

// ✅ Correct: dummy node + gap of n+1, then slow.next = slow.next.next
```

---

## 🎯 Interview Tip
Say: "Two pointers n apart is a sliding window over the list — one pass, O(1) space. I add a dummy node so deleting the head needs no special case." Mention the two-pass version as the simpler baseline.

---

## 🔗 Related Problems
→ D123 (Middle of LL) | D134 (Delete Node in LL) | D127 (Remove Duplicates from Sorted List)
