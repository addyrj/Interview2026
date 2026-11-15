---

# D041. Merge K Sorted Lists
# Category: DSA — Linked List
# Difficulty: ⭐⭐⭐ Hard | LeetCode #23 | Asked: Amazon, Google, Microsoft, Meta

---

## ❓ Problem
You are given an array of `k` sorted linked lists. Merge them all into one sorted linked list and return its head.

```
Input:  lists = [1→4→5, 1→3→4, 2→6]
Output: 1→1→2→3→4→4→5→6
```

---

## 💡 Quick Concept (2 lines only)
Keep the current head of every list in a min-heap; pop the smallest, attach it, push that node's next. The heap always holds at most k nodes, so each pop/push is O(log k).
हिंदी: हर list का head min-heap में रखो, सबसे छोटा निकालो, जोड़ो, और उसका next heap में डालो।

---

## ✅ Solution

```python
import heapq                                   # min-heap from stdlib
from typing import Optional                     # for Optional[ListNode]


class ListNode:
    def __init__(self, val: int = 0, next: "Optional[ListNode]" = None) -> None:
        self.val = val                          # value stored in node
        self.next = next                        # pointer to next node


def create_list(arr: list[int]) -> Optional[ListNode]:
    dummy = ListNode(0)                         # dummy head simplifies building
    curr = dummy                                # tail pointer
    for v in arr:                               # go through each value
        curr.next = ListNode(v)                 # append new node
        curr = curr.next                        # move tail forward
    return dummy.next                           # real head (None if arr empty)


def to_str(head: Optional[ListNode]) -> str:
    vals: list[str] = []                        # collect values as text
    while head:                                 # walk the list
        vals.append(str(head.val))              # record value
        head = head.next                        # advance
    return "→".join(vals) if vals else "None"   # readable output


# ============================================
# APPROACH 1: Brute force — collect all, sort, rebuild
# O(N log N) time, O(N) space (N = total nodes), ignores sortedness
# ============================================
def merge_brute(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    vals: list[int] = []                        # all values together
    for head in lists:                          # visit each list
        while head:                             # walk the list
            vals.append(head.val)               # collect value
            head = head.next                    # advance
    return create_list(sorted(vals))            # sort and rebuild


# ============================================
# APPROACH 2: Min-heap — O(N log k) time, O(k) space  ✅ PREFERRED
# ============================================
def merge_k_lists(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    heap: list[tuple[int, int, ListNode]] = []  # (value, list index, node)
    for i, head in enumerate(lists):            # seed heap with each head
        if head:                                # skip empty lists
            heapq.heappush(heap, (head.val, i, head))  # index breaks ties (nodes aren't comparable)
    dummy = ListNode(0)                         # dummy head for result
    tail = dummy                                # tail of merged list
    while heap:                                 # until all lists exhausted
        _, i, node = heapq.heappop(heap)        # smallest current node
        tail.next = node                        # attach it
        tail = node                             # move tail
        if node.next:                           # that list has more nodes
            heapq.heappush(heap, (node.next.val, i, node.next))  # push its next
    return dummy.next                           # skip dummy


# ============================================
# APPROACH 3: Divide and conquer — O(N log k) time, O(1) extra space
# ============================================
def merge_two(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
    dummy = tail = ListNode(0)                  # dummy head and tail pointer
    while a and b:                              # both have nodes
        if a.val <= b.val:                      # a is smaller (stable)
            tail.next, a = a, a.next            # attach a, advance a
        else:
            tail.next, b = b, b.next            # attach b, advance b
        tail = tail.next                        # move tail forward
    tail.next = a or b                          # attach leftovers
    return dummy.next                           # skip dummy


def merge_dc(lists: list[Optional[ListNode]]) -> Optional[ListNode]:
    if not lists:                               # no lists at all
        return None                             # nothing to merge
    step = 1                                    # distance between paired lists
    while step < len(lists):                    # merge pairs, doubling step
        for i in range(0, len(lists) - step, step * 2):  # pair i with i+step
            lists[i] = merge_two(lists[i], lists[i + step])  # merge the pair
        step *= 2                               # next round
    return lists[0]                             # everything merged into index 0


# ============================================
# TEST CASES
# ============================================
def build() -> list[Optional[ListNode]]:
    return [create_list([1, 4, 5]), create_list([1, 3, 4]), create_list([2, 6])]  # fresh lists each time

print(to_str(merge_brute(build())))             # 1→1→2→3→4→4→5→6
print(to_str(merge_k_lists(build())))           # 1→1→2→3→4→4→5→6
print(to_str(merge_dc(build())))                # 1→1→2→3→4→4→5→6
print(to_str(merge_k_lists([])))                # None
print(to_str(merge_k_lists([None, None])))      # None
print(to_str(merge_k_lists([None, create_list([7])])))  # 7
```

---

## 🔍 Why It Works
```
heap = [(1,L0), (1,L1), (2,L2)]
pop 1(L0) -> push 4(L0) | pop 1(L1) -> push 3(L1) | pop 2(L2) -> push 6(L2)
pop 3 -> push 4(L1) | pop 4(L0) -> push 5 | pop 4(L1) | pop 5 | pop 6
Each of N nodes is pushed/popped once, each op costs O(log k).
```
हिंदी: heap हमेशा k से ज़्यादा nodes नहीं रखता, इसलिए हर operation सिर्फ O(log k) है।

---

## 📊 Complexity
```
Brute force:      Time O(N log N) | Space O(N)
Min-heap:         Time O(N log k) | Space O(k) ← preferred
Divide & conquer: Time O(N log k) | Space O(1) extra (iterative)
Merging one by one into an accumulator: O(N·k) — avoid
```

---

## ⚡ Variations

```python
# VARIANT 1: Merge K sorted arrays -> heapq.merge(*arrays) returns a lazy sorted iterator
import heapq
print(list(heapq.merge([1, 4, 5], [1, 3, 4], [2, 6])))   # [1, 1, 2, 3, 4, 4, 5, 6]

# VARIANT 2: Smallest range covering one element from each list — same heap, track current max
# VARIANT 3: Kth smallest in k sorted lists — pop the heap k times and stop
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: pushing (val, node) — when two vals tie Python compares ListNode objects
#    heapq.heappush(heap, (head.val, head))
#    -> TypeError: '<' not supported between instances of 'ListNode' and 'ListNode'
# (not run — it raises only when values tie)

# ✅ Correct: add a unique tie-breaker (list index or counter) between val and node
#    heapq.heappush(heap, (head.val, i, head))
```

---

## 🎯 Interview Tip
Say: "A heap of size k gives O(N log k). If heap comparisons on nodes are a problem in Python I add an index tie-breaker. Divide and conquer reaches the same time with O(1) extra space." Mention that merging sequentially is O(N·k).

---

## 🔗 Related Problems
→ D033 (Merge Two Sorted Lists) | D040 (Reorder List) | D039 (Add Two Numbers)
