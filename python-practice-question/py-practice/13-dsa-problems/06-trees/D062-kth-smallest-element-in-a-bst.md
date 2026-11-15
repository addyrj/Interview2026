---

# D062. Kth Smallest Element in a BST
# Category: DSA — Trees
# Difficulty: ⭐⭐ Medium | LeetCode #230

---

## ❓ Problem
Given the root of a BST and an integer `k` (1-indexed), return the k-th smallest value in the tree.

```
Input:  root = [3,1,4,None,2], k = 1   Output: 1
Input:  root = [5,3,6,2,4,None,None,1], k = 3   Output: 3
```

---

## 💡 Quick Concept (2 lines only)
Inorder traversal of a BST visits values in sorted order, so the k-th node visited is the answer. Stop early instead of traversing the whole tree.
हिंदी: BST का inorder हमेशा sorted होता है, इसलिए k-वाँ node ही जवाब है; k पर पहुँचते ही रुक जाओ।

---

## ✅ Solution

```python
from __future__ import annotations           # allow forward type hints
from collections import deque                # queue used by build()
from typing import Optional                  # Optional type hint


class TreeNode:                              # node class (given in interview)
    def __init__(self, val: int = 0, left: Optional[TreeNode] = None, right: Optional[TreeNode] = None):
        self.val = val                       # value stored in node
        self.left = left                     # left child
        self.right = right                   # right child


def build(arr: list) -> Optional[TreeNode]:  # helper: LeetCode-style level-order list -> tree
    if not arr or arr[0] is None:            # empty tree
        return None                          # nothing to build
    root = TreeNode(arr[0])                  # first value is the root
    q = deque([root])                        # nodes waiting for children
    i = 1                                    # index of next value
    while q and i < len(arr):                # while values remain
        node = q.popleft()                   # take next parent
        if i < len(arr) and arr[i] is not None:  # left child exists?
            node.left = TreeNode(arr[i])     # create it
            q.append(node.left)              # queue it
        i += 1                               # next slot
        if i < len(arr) and arr[i] is not None:  # right child exists?
            node.right = TreeNode(arr[i])    # create it
            q.append(node.right)             # queue it
        i += 1                               # next slot
    return root                              # finished tree


# ============================================
# APPROACH 1: Brute force — full recursive inorder into a list, then index
# O(n) time, O(n) space (visits every node even if k is small)
# ============================================
def kth_brute(root: Optional[TreeNode], k: int) -> int:
    out: list[int] = []                      # sorted values collected here

    def inorder(node: Optional[TreeNode]) -> None:   # left, node, right
        if node is None:                     # base case
            return                           # nothing to do
        inorder(node.left)                   # smaller values first
        out.append(node.val)                 # visit node
        inorder(node.right)                  # larger values last

    inorder(root)                            # fill the list
    return out[k - 1]                        # k is 1-indexed


# ============================================
# APPROACH 2: Iterative inorder with explicit stack + early stop ✅ PREFERRED
# O(h + k) time, O(h) space
# ============================================
def kth_smallest(root: Optional[TreeNode], k: int) -> int:
    stack: list[TreeNode] = []               # nodes whose left side is being explored
    node = root                              # current pointer
    while stack or node:                     # until nothing left to visit
        while node:                          # dive as far left as possible
            stack.append(node)               # remember the path
            node = node.left                 # go left
        node = stack.pop()                   # smallest unvisited node
        k -= 1                               # one more node counted
        if k == 0:                           # this is the k-th
            return node.val                  # done, stop early
        node = node.right                    # then explore right subtree
    raise ValueError("k is larger than tree size")  # k out of range


# ============================================
# TEST CASES
# ============================================
t1 = build([3, 1, 4, None, 2])               # small tree
t2 = build([5, 3, 6, 2, 4, None, None, 1])   # deeper tree
print(kth_brute(t1, 1))                      # Expected: 1
print(kth_smallest(t1, 1))                   # Expected: 1
print(kth_smallest(t2, 3))                   # Expected: 3
print(kth_smallest(t2, 6))                   # Expected: 6
print(kth_smallest(build([1]), 1))           # Expected: 1
```

---

## 🔍 Why It Works
```
        5
       / \
      3   6        inorder = 1,2,3,4,5,6
     / \
    2   4          k=3 -> third visited node = 3
   /
  1
```
हिंदी: Stack से left-left जाते हैं, pop करते ही सबसे छोटा unvisited node मिलता है; k बार pop = जवाब।

---

## 📊 Complexity
```
Brute force: Time O(n)     | Space O(n)
Iterative:   Time O(h + k) | Space O(h) ← preferred (h = tree height)
```

---

## ⚡ Variations

```python
# Alternative: generator-based inorder, take the k-th item lazily
from itertools import islice                 # slice any iterator


def inorder_gen(node: Optional[TreeNode]):   # yields values in sorted order
    if node:                                 # skip empty subtrees
        yield from inorder_gen(node.left)    # left subtree first
        yield node.val                       # then this node
        yield from inorder_gen(node.right)   # then right subtree


def kth_gen(root: Optional[TreeNode], k: int) -> int:
    return next(islice(inorder_gen(root), k - 1, None))  # skip k-1 items, take next


print(kth_gen(build([5, 3, 6, 2, 4, None, None, 1]), 3))  # Expected: 3

# VARIANT 1: Kth largest -> reverse inorder (right, node, left)
# VARIANT 2: Frequent kth queries with inserts/deletes -> store subtree sizes in each node (O(h) per query)
# VARIANT 3: Kth smallest in a plain binary tree (not BST) -> heap of size k
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: walking down the left spine only
#   node = root; for _ in range(k-1): node = node.left   # ignores right children

# ❌ Wrong: using k as 0-indexed -> returns (k+1)-th smallest

# ✅ Correct: inorder traversal, decrement k per visited node, return when k == 0
```

---

## 🎯 Interview Tip
Say: "Inorder of a BST is sorted, so I do an iterative inorder and stop at the k-th node: O(h + k)." Follow-up: "for many queries on a changing tree, augment nodes with subtree size."

---

## 🔗 Related Problems
→ D056 (Validate BST) | D057 (LCA of a BST) | D063 (Serialize and Deserialize Binary Tree)
