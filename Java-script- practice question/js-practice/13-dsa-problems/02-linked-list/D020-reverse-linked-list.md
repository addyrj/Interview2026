---

# D020. Reverse a Linked List
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #206 | Asked: Microsoft, Razorpay, Atlassian

---

## ❓ Problem
Given the head of a singly linked list, reverse it and return the new head.

```
Input:  1 → 2 → 3 → 4 → 5 → null
Output: 5 → 4 → 3 → 2 → 1 → null
```

---

## 💡 Quick Concept (2 lines only)
Iterative: use three pointers (prev, curr, next). At each step: save next, reverse the link, advance all three. Recursive: reverse rest of list, attach head at end.
हिंदी: Three pointers — prev, curr, next; हर step में link reverse करो और आगे बढ़ो।

---

## ✅ Solution

```javascript
// ============================================
// Node class (given in interview):
// ============================================

class ListNode {
  constructor(val, next = null) {
    this.val = val;
    this.next = next;
  }
}

// Helper to create list from array:
function createList(arr) {
  if (!arr.length) return null;
  const head = new ListNode(arr[0]);
  let curr = head;
  for (let i = 1; i < arr.length; i++) {
    curr.next = new ListNode(arr[i]);
    curr = curr.next;
  }
  return head;
}

// Helper to print list:
function printList(head) {
  const vals = [];
  while (head) { vals.push(head.val); head = head.next; }
  return vals.join(' → ');
}

// ============================================
// APPROACH 1: Iterative — O(n) time, O(1) space ✅ PREFERRED
// ============================================

function reverseList(head) {
  let prev = null;
  let curr = head;
  
  while (curr !== null) {
    const nextNode = curr.next;  // Step 1: save next (we're about to overwrite it)
    curr.next = prev;             // Step 2: reverse the link
    prev = curr;                  // Step 3: advance prev
    curr = nextNode;              // Step 4: advance curr
  }
  
  return prev;  // prev is now the new head
}

// ============================================
// APPROACH 2: Recursive — O(n) time, O(n) space (call stack)
// ============================================

function reverseListRecursive(head) {
  // Base case: empty or single node
  if (head === null || head.next === null) return head;
  
  // Step 1: reverse the rest of the list
  const newHead = reverseListRecursive(head.next);
  
  // Step 2: make next node point back to current
  head.next.next = head;
  
  // Step 3: remove current's forward pointer
  head.next = null;
  
  return newHead;  // new head (was the tail)
}

// ============================================
// TEST CASES
// ============================================

let list1 = createList([1, 2, 3, 4, 5]);
console.log(printList(reverseList(list1)));         // 5 → 4 → 3 → 2 → 1

let list2 = createList([1, 2]);
console.log(printList(reverseList(list2)));         // 2 → 1

let list3 = createList([1]);
console.log(printList(reverseList(list3)));         // 1

console.log(reverseList(null));                     // null
```

---

## 🔍 Why Three Pointers Work
```
Before:  prev=null, curr=1→2→3→4→5
Step 1: save next=2, reverse: 1→null, advance prev=1, curr=2
Step 2: save next=3, reverse: 2→1,    advance prev=2, curr=3
Step 3: save next=4, reverse: 3→2,    advance prev=3, curr=4
Step 4: save next=5, reverse: 4→3,    advance prev=4, curr=5
Step 5: save next=null, reverse: 5→4, advance prev=5, curr=null
Loop ends: prev=5 (new head)
```
हिंदी: Prev=null से शुरू करो — हर step में link reverse करो, तीनों pointers आगे बढ़ाओ।

---

## 📊 Complexity
```
Iterative:  Time O(n) | Space O(1) ← preferred
Recursive:  Time O(n) | Space O(n) — call stack
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Reverse between positions left and right (LeetCode #92)
function reverseBetween(head, left, right) {
  if (!head || left === right) return head;
  
  const dummy = new ListNode(0);
  dummy.next = head;
  let prev = dummy;
  
  // Move prev to node just before left
  for (let i = 1; i < left; i++) prev = prev.next;
  
  let curr = prev.next;  // node at position left
  
  // Reverse (right - left) times
  for (let i = 0; i < right - left; i++) {
    const nextNode = curr.next;
    curr.next = nextNode.next;
    nextNode.next = prev.next;
    prev.next = nextNode;
  }
  
  return dummy.next;
}
// Input: 1→2→3→4→5, left=2, right=4 → 1→4→3→2→5

// VARIANT 2: Reverse in groups of K (LeetCode #25)
function reverseKGroup(head, k) {
  let curr = head;
  let count = 0;
  while (curr && count < k) { curr = curr.next; count++; }
  if (count < k) return head;  // less than k nodes remaining
  
  // Reverse first k nodes
  let prev = null, node = head;
  for (let i = 0; i < k; i++) {
    const next = node.next;
    node.next = prev;
    prev = node;
    node = next;
  }
  // head is now the tail of reversed group — connect to next group
  head.next = reverseKGroup(node, k);
  return prev;  // prev is new head
}

// VARIANT 3: Check if linked list is palindrome
function isPalindrome(head) {
  // Find middle
  let slow = head, fast = head;
  while (fast && fast.next) { slow = slow.next; fast = fast.next.next; }
  
  // Reverse second half
  let prev = null, curr = slow;
  while (curr) { const next = curr.next; curr.next = prev; prev = curr; curr = next; }
  
  // Compare first and reversed second half
  let left = head, right = prev;
  while (right) {
    if (left.val !== right.val) return false;
    left = left.next; right = right.next;
  }
  return true;
}
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: forgetting to save next before reversing
curr.next = prev;   // link reversed
curr = curr.next;   // curr.next is now prev! We lost the original next!

// ✅ Correct: save next FIRST
const nextNode = curr.next;  // save before modifying
curr.next = prev;             // then reverse
curr = nextNode;              // use saved reference

// ❌ Wrong: forgetting to return prev (returning head)
return head;  // head is now the TAIL — wrong!
// ✅ return prev — that's the new head
```

---

## 🎯 Interview Tip
Say: "Draw it out — three pointer solution: save next, flip link, advance both pointers. Iterative is O(1) space; recursive uses O(n) call stack — prefer iterative. Common follow-up: reverse in groups of K."

---

## 🔗 Related Problems
→ D021 (Detect Cycle in LL) | D022 (Merge Two Sorted Lists) | D023 (Find Middle of LL)
