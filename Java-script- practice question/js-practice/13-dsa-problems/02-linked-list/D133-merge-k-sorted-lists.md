---

# D133. Merge K Sorted Lists
# Category: DSA — Linked List
# Difficulty: ⭐⭐⭐ Hard | LeetCode #23 | Asked: Amazon, Google, Microsoft, Facebook, Uber

---

## ❓ Problem
You are given an array of k sorted linked lists. Merge all of them into one sorted linked list and return it.

```
Input:  [1→4→5, 1→3→4, 2→6]
Output: 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
```

---

## 💡 Quick Concept (2 lines only)
Divide and conquer: merge lists in pairs (like merge sort) using the two-list merge, halving the number of lists each round. Alternative: a min-heap of the k current heads.
हिंदी: Lists को जोड़ी में merge करते जाओ (merge sort की तरह) — हर round में lists आधी हो जाती हैं; या min-heap से सबसे छोटा head निकालो।

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

// Merge two sorted lists (see D120)
function mergeTwo(l1, l2) {
  const dummy = new ListNode(0);              // dummy head
  let tail = dummy;                           // tail of result
  while (l1 && l2) {                          // both non-empty
    if (l1.val <= l2.val) { tail.next = l1; l1 = l1.next; } // take smaller from l1
    else { tail.next = l2; l2 = l2.next; }                  // or from l2
    tail = tail.next;                         // advance tail
  }
  tail.next = l1 || l2;                       // attach remainder
  return dummy.next;                          // merged head
}

// ============================================
// APPROACH 1: Brute force — collect all values, sort, rebuild
// O(N log N) time, O(N) space  (N = total nodes)
// ============================================
function mergeKBrute(lists) {
  const vals = [];                            // every value
  for (let h of lists) {                      // each list
    while (h) { vals.push(h.val); h = h.next; } // collect values
  }
  vals.sort((a, b) => a - b);                 // sort numerically
  return createList(vals);                    // rebuild
}

// ============================================
// APPROACH 2: Merge one by one — O(k*N) time, O(1) space (slow for large k)
// ============================================
function mergeKSequential(lists) {
  let result = null;                          // merged so far
  for (const l of lists) result = mergeTwo(result, l); // fold lists in one at a time
  return result;                              // final list
}

// ============================================
// APPROACH 3: Divide and conquer — O(N log k) time, O(log k) stack ✅ PREFERRED
// ============================================
function mergeKLists(lists) {
  if (lists.length === 0) return null;        // no lists
  while (lists.length > 1) {                  // until one list remains
    const merged = [];                        // lists after this round
    for (let i = 0; i < lists.length; i += 2) { // take pairs
      const a = lists[i];                     // first of pair
      const b = i + 1 < lists.length ? lists[i + 1] : null; // second (may be missing)
      merged.push(mergeTwo(a, b));            // merge the pair
    }
    lists = merged;                           // halve the number of lists
  }
  return lists[0];                            // the single merged list
}

// ============================================
// APPROACH 4: Min-heap of k heads — O(N log k) time, O(k) space
// ============================================
class MinHeap {
  constructor() { this.h = []; }              // array-based heap of nodes
  size() { return this.h.length; }            // number of items
  push(node) {
    const h = this.h; h.push(node);           // add at the end
    let i = h.length - 1;                     // sift up
    while (i > 0) {
      const p = (i - 1) >> 1;                 // parent index
      if (h[p].val <= h[i].val) break;        // heap property OK
      [h[p], h[i]] = [h[i], h[p]]; i = p;     // swap with parent
    }
  }
  pop() {
    const h = this.h, top = h[0], last = h.pop(); // remove root
    if (h.length) {
      h[0] = last;                            // move last to root
      let i = 0;                              // sift down
      for (;;) {
        let l = 2 * i + 1, r = l + 1, m = i;  // children, smallest index
        if (l < h.length && h[l].val < h[m].val) m = l; // left smaller
        if (r < h.length && h[r].val < h[m].val) m = r; // right smaller
        if (m === i) break;                   // done
        [h[m], h[i]] = [h[i], h[m]]; i = m;   // swap down
      }
    }
    return top;                               // smallest node
  }
}

function mergeKHeap(lists) {
  const heap = new MinHeap();                 // holds current head of each list
  for (const l of lists) if (l) heap.push(l); // seed with non-empty heads
  const dummy = new ListNode(0);              // dummy head
  let tail = dummy;                           // result tail
  while (heap.size()) {                       // while any list has nodes
    const node = heap.pop();                  // smallest head overall
    tail.next = node;                         // append to result
    tail = node;                              // advance tail
    if (node.next) heap.push(node.next);      // push that list's next node
  }
  return dummy.next;                          // merged head
}

// ============================================
// TEST CASES
// ============================================
const build = () => [createList([1, 4, 5]), createList([1, 3, 4]), createList([2, 6])];
console.log(printList(mergeKBrute(build())));       // 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
console.log(printList(mergeKSequential(build())));  // 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
console.log(printList(mergeKLists(build())));       // 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
console.log(printList(mergeKHeap(build())));        // 1 → 1 → 2 → 3 → 4 → 4 → 5 → 6
console.log(printList(mergeKLists([])));            // null
console.log(printList(mergeKLists([null])));        // null
console.log(printList(mergeKHeap([null, createList([2]), createList([1])])));  // 1 → 2
```

---

## 🔍 Why It Works
```
Lists: L1, L2, L3, L4, L5   (k = 5)
Round 1: (L1+L2), (L3+L4), L5      -> 3 lists
Round 2: (L12+L34), L5             -> 2 lists
Round 3: (L1234+L5)                -> 1 list
log k rounds, each round touches all N nodes => O(N log k)
```
हिंदी: हर round में सारे N nodes एक बार छुए जाते हैं और rounds सिर्फ log k होते हैं, इसलिए O(N log k)।

---

## 📊 Complexity
```
Brute (sort):        Time O(N log N) | Space O(N)
Sequential merge:    Time O(k * N)   | Space O(1)
Divide and conquer:  Time O(N log k) | Space O(1) extra ← preferred
Min-heap:            Time O(N log k) | Space O(k)
```

---

## ⚡ Variations

```javascript
// VARIANT 1: Merge K sorted arrays - same heap idea with (value, arrayIndex, position)
// VARIANT 2: Smallest range covering elements from K lists (LeetCode #632)
// VARIANT 3: Kth smallest element in a sorted matrix (LeetCode #378)
```

---

## ⚠️ Common Mistake
```javascript
// ❌ Wrong: merging sequentially  -> O(k*N), TLE for large k
// ❌ Wrong: heap push of null nodes -> crash when comparing .val
heap.push(l);           // skip empty lists first: if (l) heap.push(l)

// ❌ Wrong: odd count of lists, accessing lists[i+1] out of range
// ✅ Correct: handle the missing partner (use null) in divide and conquer
```

---

## 🎯 Interview Tip
Say: "Naive is sort-all O(N log N). Better: min-heap of k heads or divide-and-conquer pairwise merges, both O(N log k). D&C reuses the two-list merge with no extra data structure." JS has no built-in heap, so mention you'd write a small one.

---

## 🔗 Related Problems
→ D120 (Merge Two Sorted Lists) | D128 (Add Two Numbers) | D129 (Reorder List)
