---

# D121. Linked List Cycle (Floyd)
# Category: DSA — Linked List
# Difficulty: ⭐ Easy | LeetCode #141 | Asked: Amazon, Microsoft, Paytm, Infosys

---

## ❓ Problem
Given the head of a linked list, return true if the list has a cycle (some node's next points back to an earlier node), otherwise false.

```
Input:  3 → 2 → 0 → -4 → (back to node 2)
Output: true

Input:  1 → 2 → null
Output: false
```

---

## 💡 Quick Concept (2 lines only)
Floyd's Tortoise and Hare: slow moves 1 step, fast moves 2 steps. If there is a cycle, fast eventually laps slow and they meet; if no cycle, fast hits null.
हिंदी: Slow 1 step, fast 2 steps चलता है — cycle हो तो दोनों कहीं न कहीं मिलेंगे, वरना fast null पर पहुँच जाएगा।

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

// Helper: build list from array; pos = index the tail connects to (-1 = no cycle)
function createList(arr, pos = -1) {
  const dummy = new ListNode(0);       // dummy head
  let curr = dummy;                    // tail pointer
  const nodes = [];                    // keep references to every node
  for (const v of arr) {               // build nodes
    curr.next = new ListNode(v);       // append
    curr = curr.next;                  // advance tail
    nodes.push(curr);                  // remember node
  }
  if (pos >= 0 && nodes.length) curr.next = nodes[pos]; // create the cycle
  return dummy.next;                   // real head
}

// ============================================
// APPROACH 1: Hash Set of visited nodes — O(n) time, O(n) space
// ============================================
function hasCycleSet(head) {
  const seen = new Set();              // stores node references
  while (head) {                       // until list ends
    if (seen.has(head)) return true;   // revisiting a node => cycle
    seen.add(head);                    // mark as visited
    head = head.next;                  // move on
  }
  return false;                        // reached null => no cycle
}

// ============================================
// APPROACH 2: Floyd's slow/fast pointers — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function hasCycle(head) {
  let slow = head;                     // tortoise: 1 step at a time
  let fast = head;                     // hare: 2 steps at a time
  while (fast !== null && fast.next !== null) { // fast must have 2 nodes ahead
    slow = slow.next;                  // move slow by 1
    fast = fast.next.next;             // move fast by 2
    if (slow === fast) return true;    // they met inside the cycle
  }
  return false;                        // fast fell off the end => no cycle
}

// ============================================
// TEST CASES
// ============================================
console.log(hasCycleSet(createList([3, 2, 0, -4], 1)));  // true
console.log(hasCycle(createList([3, 2, 0, -4], 1)));     // true
console.log(hasCycle(createList([1, 2], 0)));            // true
console.log(hasCycle(createList([1], 0)));               // true (self loop)
console.log(hasCycle(createList([1, 2])));               // false
console.log(hasCycle(createList([1])));                  // false
console.log(hasCycle(null));                             // false
```

---

## 🔍 Why It Works
```
Inside a cycle the gap between fast and slow shrinks by 1 each step
(fast gains 1 node per iteration). Gap goes ... 3, 2, 1, 0 => they meet.
They can never "jump over" each other because the gap reduces by exactly 1.
```
हिंदी: Cycle के अंदर fast हर step में slow से 1 कदम पास आता है, इसलिए gap 0 होगा ही — दोनों मिलेंगे।

---

## 📊 Complexity
```
Hash Set: Time O(n) | Space O(n)
Floyd:    Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Find where the cycle starts (see D122)
// VARIANT 2: Find the cycle length — after meeting, walk one pointer until it returns
function cycleLength(head) {
  let slow = head, fast = head;                          // start both at head
  while (fast && fast.next) {                            // standard Floyd loop
    slow = slow.next; fast = fast.next.next;             // 1x and 2x
    if (slow === fast) {                                 // met in cycle
      let len = 1, p = slow.next;                        // count from meeting point
      while (p !== slow) { len++; p = p.next; }          // walk around once
      return len;                                        // cycle length
    }
  }
  return 0;                                              // no cycle
}
console.log(cycleLength(createList([3, 2, 0, -4], 1)));  // 3
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: only checking fast !== null -> fast.next.next crashes on odd length
while (fast !== null) { fast = fast.next.next; }   // TypeError when fast.next is null

// ❌ Wrong: comparing values instead of node references
if (slow.val === fast.val) return true;            // duplicate values give false positives

// ✅ Correct: check fast && fast.next, compare node references (===)
```

---

## 🎯 Interview Tip
Say: "Hash set is the easy O(n) space answer; Floyd's slow/fast pointers get O(1) space. They must meet because fast closes the gap by one per step." Be ready for the follow-up: find the cycle start (D122).

---

## 🔗 Related Problems
→ D122 (Cycle II — find start) | D123 (Middle of LL) | D126 (Intersection of Two LLs)
