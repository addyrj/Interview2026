---

# D122. Linked List Cycle II (find start)
# Category: DSA — Linked List
# Difficulty: ⭐⭐ Medium | LeetCode #142 | Asked: Amazon, Microsoft, Flipkart, Goldman Sachs

---

## ❓ Problem
Given the head of a linked list, return the node where the cycle begins. If there is no cycle, return null. Do not modify the list.

```
Input:  3 → 2 → 0 → -4 → (back to node index 1)
Output: node with value 2
```

---

## 💡 Quick Concept (2 lines only)
Run Floyd until slow and fast meet. Then reset one pointer to head; move both 1 step at a time — they meet exactly at the cycle start.
हिंदी: पहले slow/fast को मिलाओ, फिर एक pointer head पर रखो और दोनों को 1-1 step चलाओ — जहाँ मिलें वही cycle की शुरुआत है।

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

// Helper: build list; pos = index tail connects to (-1 = no cycle)
function createList(arr, pos = -1) {
  const dummy = new ListNode(0);       // dummy head
  let curr = dummy;                    // tail pointer
  const nodes = [];                    // node references
  for (const v of arr) {               // build nodes
    curr.next = new ListNode(v);       // append
    curr = curr.next;                  // advance
    nodes.push(curr);                  // remember
  }
  if (pos >= 0 && nodes.length) curr.next = nodes[pos]; // close the cycle
  return dummy.next;                   // real head
}

// ============================================
// APPROACH 1: Hash Set — O(n) time, O(n) space
// ============================================
function detectCycleSet(head) {
  const seen = new Set();              // visited nodes
  while (head) {                       // walk list
    if (seen.has(head)) return head;   // first repeated node = cycle start
    seen.add(head);                    // mark visited
    head = head.next;                  // advance
  }
  return null;                         // no cycle
}

// ============================================
// APPROACH 2: Floyd's two phases — O(n) time, O(1) space ✅ PREFERRED
// ============================================
function detectCycle(head) {
  let slow = head;                     // tortoise
  let fast = head;                     // hare

  // Phase 1: detect the meeting point inside the cycle
  while (fast !== null && fast.next !== null) {
    slow = slow.next;                  // 1 step
    fast = fast.next.next;             // 2 steps
    if (slow === fast) {               // met => cycle exists
      // Phase 2: find the entrance
      let start = head;                // pointer from the head
      while (start !== slow) {         // move both 1 step until they meet
        start = start.next;            // advance head pointer
        slow = slow.next;              // advance meeting-point pointer
      }
      return start;                    // cycle entrance
    }
  }
  return null;                         // fast reached the end => no cycle
}

// ============================================
// TEST CASES
// ============================================
let a = createList([3, 2, 0, -4], 1);
console.log(detectCycleSet(a).val);          // 2
console.log(detectCycle(a).val);             // 2
console.log(detectCycle(createList([1, 2], 0)).val);   // 1
console.log(detectCycle(createList([1], 0)).val);      // 1
console.log(detectCycle(createList([1, 2, 3])));       // null
console.log(detectCycle(null));                        // null
```

---

## 🔍 Why It Works
```
Let: a = distance head -> cycle start
     b = distance cycle start -> meeting point
     c = rest of the cycle (cycle length L = b + c)

At meeting: slow walked a + b, fast walked 2(a + b)
fast also = a + b + k*L  (extra full laps)
=> a + b = k*L  =>  a = k*L - b = (k-1)*L + c

So walking a steps from the meeting point lands at cycle start
(c steps to the start, then full laps). A pointer from head also
takes a steps to reach the start => both meet at the entrance.
```
हिंदी: Math से a = c + (पूरे चक्कर) निकलता है, इसलिए head और meeting point से बराबर चलने पर दोनों cycle के start पर मिलते हैं।

---

## 📊 Complexity
```
Hash Set: Time O(n) | Space O(n)
Floyd:    Time O(n) | Space O(1) ← preferred
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Find a duplicate number in array (LeetCode #287)
// Treat nums[i] as "next index" -> duplicate is the cycle entrance.
function findDuplicate(nums) {
  let slow = nums[0], fast = nums[0];        // start at index 0's value
  do {
    slow = nums[slow];                       // 1 step
    fast = nums[nums[fast]];                 // 2 steps
  } while (slow !== fast);                   // phase 1: meet in cycle
  slow = nums[0];                            // reset one pointer
  while (slow !== fast) {                    // phase 2: find entrance
    slow = nums[slow];                       // 1 step
    fast = nums[fast];                       // 1 step
  }
  return slow;                               // duplicate value
}
console.log(findDuplicate([1, 3, 4, 2, 2]));  // 2
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: returning the meeting point instead of the entrance
if (slow === fast) return slow;      // meeting point is usually NOT the start

// ❌ Wrong: in phase 2 moving fast 2 steps again
// both pointers must move 1 step in phase 2

// ✅ Correct: reset one pointer to head, move both by 1 until equal
```

---

## 🎯 Interview Tip
Say: "Phase 1 finds whether a cycle exists, phase 2 finds the entrance. Distance from head to entrance equals distance from meeting point to entrance (mod cycle length)." Mention the hash-set approach first, then optimize.

---

## 🔗 Related Problems
→ D121 (Linked List Cycle) | D126 (Intersection of Two LLs) | D123 (Middle of LL)
