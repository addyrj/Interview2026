---

# D131. Swap Nodes in Pairs
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #24 | Asked: Amazon, Microsoft, Bloomberg, Samsung

---

## ❓ Problem
Given a linked list, swap every two adjacent nodes and return the head. Swap the nodes themselves, not just their values.

```
Input:  1 → 2 → 3 → 4
Output: 2 → 1 → 4 → 3
```

---

## 💡 Quick Concept (2 lines only)
Use a dummy node and a prev pointer before each pair. For pair (a, b): prev → b → a → next-pair. Then move prev to a.
हिंदी: हर pair (a, b) के लिए prev → b → a → आगे का हिस्सा जोड़ो, फिर prev को a पर ले जाओ।

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
// APPROACH 1: Swap values (NOT allowed by the problem, but simple) — O(n) time, O(1) space
// ============================================
function swapPairsValues(head) {
  for (let p = head; p && p.next; p = p.next.next) { // step 2 nodes at a time
    const t = p.val; p.val = p.next.val; p.next.val = t; // swap the two values
  }
  return head;                                // same head
}

// ============================================
// APPROACH 2: Iterative relinking with dummy — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function swapPairs(head) {
  const dummy = new ListNode(0, head);        // dummy before head
  let prev = dummy;                           // node before the current pair

  while (prev.next !== null && prev.next.next !== null) { // a full pair exists
    const a = prev.next;                      // first node of pair
    const b = a.next;                         // second node of pair

    a.next = b.next;                          // a points past the pair
    b.next = a;                               // b points back to a
    prev.next = b;                            // previous part points to b (new first)

    prev = a;                                 // a is now the tail of the swapped pair
  }
  return dummy.next;                          // new head
}

// ============================================
// APPROACH 3: Recursive — O(n) time, O(n) stack space
// ============================================
function swapPairsRec(head) {
  if (head === null || head.next === null) return head; // 0 or 1 node: nothing to swap
  const second = head.next;                   // will become the new head of the pair
  head.next = swapPairsRec(second.next);      // swap the rest and attach after head
  second.next = head;                         // second points back to head
  return second;                              // new head of this pair
}

// ============================================
// TEST CASES
// ============================================
console.log(printList(swapPairsValues(createList([1, 2, 3, 4]))));    // 2 → 1 → 4 → 3
console.log(printList(swapPairs(createList([1, 2, 3, 4]))));          // 2 → 1 → 4 → 3
console.log(printList(swapPairs(createList([1, 2, 3, 4, 5]))));       // 2 → 1 → 4 → 3 → 5
console.log(printList(swapPairsRec(createList([1, 2, 3]))));          // 2 → 1 → 3
console.log(printList(swapPairs(createList([1]))));                   // 1
console.log(printList(swapPairs(createList([]))));                    // null
```

---

## 🔍 Why It Works
```
dummy → 1 → 2 → 3 → 4
prev=dummy, a=1, b=2
a.next = b.next (3)   : 1 → 3
b.next = a            : 2 → 1
prev.next = b         : dummy → 2 → 1 → 3 → 4
prev = a (1)
Next pair: a=3, b=4 -> dummy → 2 → 1 → 4 → 3
```
हिंदी: तीन links बदलनी हैं — a→आगे, b→a, prev→b; आखिर में prev को a पर ले जाओ।

---

## 📊 Complexity
```
Values swap: Time O(n) | Space O(1) (not valid when nodes must be swapped)
Iterative:   Time O(n) | Space O(1) ← preferred
Recursive:   Time O(n) | Space O(n)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Reverse nodes in k-group (LeetCode #25) - see D020 Variation 2
// VARIANT 2: Swap kth node from start and end (LeetCode #1721) - gap technique from D124
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: order of pointer updates
b.next = a;
a.next = b.next;     // b.next is now a, so a.next = a -> cycle!

// ✅ Correct: a.next = b.next FIRST, then b.next = a, then prev.next = b

// ❌ Wrong: no dummy node -> head change needs special handling
```

---

## 🎯 Interview Tip
Say: "Swapping values is not allowed here, so I relink. A dummy node means the head swap is handled uniformly; the order of the three pointer updates matters." Mention the recursive version as a concise alternative.

---

## 🔗 Related Problems
→ D020 (Reverse Linked List) | D130 (Odd Even Linked List) | D129 (Reorder List)
