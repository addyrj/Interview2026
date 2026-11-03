---

# D129. Reorder List
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #143 | Asked: Amazon, Microsoft, Facebook, Uber

---

## ❓ Problem
Given head of a singly linked list L0 → L1 → … → Ln-1 → Ln, reorder it in place to L0 → Ln → L1 → Ln-1 → L2 → Ln-2 → … Do not change node values, only links.

```
Input:  1 → 2 → 3 → 4 → 5
Output: 1 → 5 → 2 → 4 → 3
```

---

## 💡 Quick Concept (2 lines only)
Three steps: find the middle, reverse the second half, then interleave the two halves.
हिंदी: Middle ढूँढो, दूसरे half को reverse करो, फिर दोनों halves को एक-एक करके मिला दो (zip)।

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
// APPROACH 1: Array of nodes + two pointers — O(n) time, O(n) space
// ============================================
function reorderListArray(head) {
  if (!head) return;                          // nothing to do
  const nodes = [];                           // all nodes in order
  for (let p = head; p; p = p.next) nodes.push(p); // collect references
  let i = 0, j = nodes.length - 1;            // front and back indexes
  while (i < j) {                             // until they meet
    nodes[i].next = nodes[j];                 // front -> back
    i++;                                      // move front
    if (i === j) break;                       // even/odd meet point
    nodes[j].next = nodes[i];                 // back -> next front
    j--;                                      // move back
  }
  nodes[i].next = null;                       // terminate the list (avoid a cycle)
}

// ============================================
// APPROACH 2: Middle + reverse + merge — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function reorderList(head) {
  if (!head || !head.next) return;            // 0 or 1 node: already fine

  // Step 1: find the middle
  let slow = head, fast = head;               // slow/fast pointers
  while (fast.next !== null && fast.next.next !== null) { // first middle for even length
    slow = slow.next;                         // 1 step
    fast = fast.next.next;                    // 2 steps
  }

  // Step 2: reverse the second half
  let prev = null, curr = slow.next;          // second half starts after slow
  slow.next = null;                           // cut the list into two halves
  while (curr !== null) {                     // standard reverse
    const nextNode = curr.next;               // save next
    curr.next = prev;                         // flip link
    prev = curr;                              // advance prev
    curr = nextNode;                          // advance curr
  }

  // Step 3: merge alternately
  let first = head, second = prev;            // heads of both halves
  while (second !== null) {                   // second half is shorter or equal
    const t1 = first.next;                    // save next of first half
    const t2 = second.next;                   // save next of second half
    first.next = second;                      // first -> second
    second.next = t1;                         // second -> original next of first
    first = t1;                               // advance first
    second = t2;                              // advance second
  }
}

// ============================================
// TEST CASES
// ============================================
let a = createList([1, 2, 3, 4, 5]); reorderListArray(a);
console.log(printList(a));                    // 1 → 5 → 2 → 4 → 3
let b = createList([1, 2, 3, 4, 5]); reorderList(b);
console.log(printList(b));                    // 1 → 5 → 2 → 4 → 3
let c = createList([1, 2, 3, 4]); reorderList(c);
console.log(printList(c));                    // 1 → 4 → 2 → 3
let d = createList([1, 2]); reorderList(d);
console.log(printList(d));                    // 1 → 2
let e = createList([1]); reorderList(e);
console.log(printList(e));                    // 1
```

---

## 🔍 Why It Works
```
1 → 2 → 3 → 4 → 5
Step 1: middle = 3, split: [1 → 2 → 3] and [4 → 5]
Step 2: reverse second: [5 → 4]
Step 3: merge alternately:
  1 → 5 → 2 → 4 → 3
```
हिंदी: दूसरा half reverse होने से उसका last node पहले आता है — इसलिए alternately जोड़ने पर L0, Ln, L1, Ln-1 वाला pattern बन जाता है।

---

## 📊 Complexity
```
Array:               Time O(n) | Space O(n)
Mid + reverse + merge: Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Palindrome check uses the same first two steps (D125)
// VARIANT 2: Sort list (LeetCode #148) uses middle-split + merge (D120)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: not cutting the first half (slow.next = null)
// the first half still links into the old second half -> infinite loop / cycle

// ❌ Wrong: forgetting to save both next pointers before relinking
first.next = second;  second.next = first.next;   // second.next now points to second itself!

// ✅ Correct: save t1 and t2 first, then relink
```

---

## 🎯 Interview Tip
Say: "This is three classic patterns combined: slow/fast to find the middle, reverse the second half, and merge two lists alternately. All in place with O(1) space." Mention you cut the list at the middle to avoid cycles.

---

## 🔗 Related Problems
→ D020 (Reverse Linked List) | D123 (Middle of LL) | D125 (Palindrome LL)
