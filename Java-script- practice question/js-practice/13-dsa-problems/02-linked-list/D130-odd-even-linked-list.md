---

# D130. Odd Even Linked List
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #328 | Asked: Amazon, Microsoft, Bloomberg

---

## ❓ Problem
Given the head of a singly linked list, group all nodes at odd positions together followed by nodes at even positions (positions, not values; 1-indexed). Keep the relative order inside each group. Use O(1) extra space and O(n) time.

```
Input:  1 → 2 → 3 → 4 → 5
Output: 1 → 3 → 5 → 2 → 4
```

---

## 💡 Quick Concept (2 lines only)
Keep two chains: odd and even. Link odd.next = even.next, even.next = odd.next, advancing alternately. Finally attach the even chain's head after the odd tail.
हिंदी: दो chains बनाओ — odd positions और even positions की, अंत में even chain को odd chain के पीछे जोड़ दो।

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
// APPROACH 1: Two arrays then rebuild — O(n) time, O(n) space
// ============================================
function oddEvenArray(head) {
  const odd = [], even = [];                  // values by position parity
  let i = 1;                                  // 1-indexed position
  for (let p = head; p; p = p.next, i++) {    // walk list
    (i % 2 === 1 ? odd : even).push(p.val);   // route to odd or even bucket
  }
  return createList([...odd, ...even]);       // odd first, then even
}

// ============================================
// APPROACH 2: In-place two pointers — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function oddEvenList(head) {
  if (head === null || head.next === null) return head; // 0 or 1 node: unchanged

  let odd = head;                             // tail of odd chain
  let even = head.next;                       // tail of even chain
  const evenHead = even;                      // remember start of even chain

  while (even !== null && even.next !== null) { // while an odd node follows even
    odd.next = even.next;                     // odd skips over even
    odd = odd.next;                           // advance odd tail
    even.next = odd.next;                     // even skips over the new odd
    even = even.next;                         // advance even tail
  }

  odd.next = evenHead;                        // attach even chain after the odd chain
  return head;                                // head unchanged
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(oddEvenArray(createList([1, 2, 3, 4, 5]))));        // 1 → 3 → 5 → 2 → 4
console.log(printList(oddEvenList(createList([1, 2, 3, 4, 5]))));         // 1 → 3 → 5 → 2 → 4
console.log(printList(oddEvenList(createList([2, 1, 3, 5, 6, 4, 7]))));   // 2 → 3 → 6 → 7 → 1 → 5 → 4
console.log(printList(oddEvenList(createList([1, 2, 3, 4]))));            // 1 → 3 → 2 → 4
console.log(printList(oddEvenList(createList([1, 2]))));                  // 1 → 2
console.log(printList(oddEvenList(createList([1]))));                     // 1
console.log(printList(oddEvenList(null)));                                // null
```

---

## 🔍 Why It Works
```
1 → 2 → 3 → 4 → 5     odd=1, even=2, evenHead=2
iter 1: 1.next=3, odd=3; 2.next=4, even=4
iter 2: 3.next=5, odd=5; 4.next=null, even=null -> stop
odd chain: 1→3→5, even chain: 2→4
5.next = evenHead(2)  =>  1 → 3 → 5 → 2 → 4
```
हिंदी: Odd और even pointers एक-दूसरे के आगे के node को छोड़कर अपनी chain बनाते हैं; evenHead save रखने से अंत में जोड़ना आसान है।

---

## 📊 Complexity
```
Arrays:    Time O(n) | Space O(n)
In-place:  Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Partition list around value x (LeetCode #86) - same two-chain idea
function partition(head, x) {
  const small = new ListNode(0), big = new ListNode(0); // two dummy chains
  let s = small, b = big;                     // tails of each chain
  for (let p = head; p; p = p.next) {         // walk
    if (p.val < x) { s.next = p; s = s.next; }  // smaller values chain
    else { b.next = p; b = b.next; }            // greater-or-equal chain
  }
  b.next = null;                              // end the big chain (avoid cycle)
  s.next = big.next;                          // join chains
  return small.next;                          // head
}
console.log(printList(partition(createList([1, 4, 3, 2, 5, 2]), 3)));  // 1 → 2 → 2 → 4 → 3 → 5
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: grouping by VALUE (odd/even numbers) instead of POSITION
// ❌ Wrong: losing the head of the even chain
odd.next = even;           // even has already moved on - original start is lost

// ✅ Correct: save evenHead = head.next at the start, attach it at the end
// ❌ Wrong: while (even.next) without checking even !== null -> crash on odd length
```

---

## 🎯 Interview Tip
Say: "Position-based, so I keep two chains and relink in place. The invariants: odd always points at the last odd node, even at the last even node, and I save evenHead to stitch the chains." Mention the loop condition handles both even and odd lengths.

---

## 🔗 Related Problems
→ D131 (Swap Nodes in Pairs) | D129 (Reorder List) | D120 (Merge Two Sorted Lists)
