---

# D056. Validate Binary Search Tree
# Category: DSA — Trees
# Difficulty: ⭐⭐ Medium | LeetCode #98

---

## ❓ Problem
Given the root of a binary tree, determine whether it is a valid BST: every node's left subtree has only smaller values, right subtree only larger values (strictly), and both subtrees are BSTs too.

```
Input:  root = [2,1,3]        Output: True
Input:  root = [5,1,4,None,None,3,6]   Output: False  (3 is in right subtree of 5 but < 5)
```

---

## 💡 Quick Concept (2 lines only)
Checking only parent vs child is wrong; pass down a valid (low, high) range for each node. Or: inorder traversal of a BST must be strictly increasing.
हिंदी: हर node के लिए allowed range (low, high) साथ में भेजो; या inorder में values strictly बढ़ती होनी चाहिए।

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
# APPROACH 1: Brute force — for every node check ALL nodes in its subtrees
# O(n^2) worst case time, O(h) space
# ============================================
def values(node: Optional[TreeNode]) -> list[int]:  # all values in a subtree
    return [] if node is None else values(node.left) + [node.val] + values(node.right)


def is_valid_brute(root: Optional[TreeNode]) -> bool:  # check each node against whole subtrees
    if root is None:                         # empty is valid
        return True                          # base case
    if any(v >= root.val for v in values(root.left)):    # left must be all smaller
        return False                         # violation
    if any(v <= root.val for v in values(root.right)):   # right must be all larger
        return False                         # violation
    return is_valid_brute(root.left) and is_valid_brute(root.right)  # recurse


# ============================================
# APPROACH 2: Pass (low, high) bounds — O(n) time, O(h) space ✅ PREFERRED
# ============================================
def is_valid_bst(root: Optional[TreeNode]) -> bool:  # optimal
    def check(node: Optional[TreeNode], low: float, high: float) -> bool:  # node must be in (low, high)
        if node is None:                     # empty subtree
            return True                      # valid
        if not (low < node.val < high):      # strict range check
            return False                     # out of range
        return (check(node.left, low, node.val)      # left: upper bound becomes node.val
                and check(node.right, node.val, high))  # right: lower bound becomes node.val

    return check(root, float("-inf"), float("inf"))  # start with infinite range


# ============================================
# APPROACH 3: Iterative inorder — must be strictly increasing. O(n) time, O(h) space
# ============================================
def is_valid_inorder(root: Optional[TreeNode]) -> bool:  # iterative inorder
    stack: list[TreeNode] = []               # explicit stack
    prev = float("-inf")                     # previous inorder value
    node = root                              # current pointer
    while stack or node:                     # until traversal done
        while node:                          # go as far left as possible
            stack.append(node)               # remember path
            node = node.left                 # descend
        node = stack.pop()                   # visit node
        if node.val <= prev:                 # not strictly increasing
            return False                     # invalid BST
        prev = node.val                      # update previous
        node = node.right                    # go right
    return True                              # all increasing


# ============================================
# TEST CASES
# ============================================
cases = [[2, 1, 3], [5, 1, 4, None, None, 3, 6], [], [2, 2, 2], [5, 4, 6, None, None, 3, 7]]  # test trees
for fn in (is_valid_brute, is_valid_bst, is_valid_inorder):  # run all approaches
    print(fn.__name__, [fn(build(c)) for c in cases])
# Expected (each line): [True, False, True, False, False]
```

---

## 🔍 Why It Works
```
      5
     / \
    1   4        4 must be > 5 (range (5, inf)) -> fails
       / \
      3   6      even if 3 < 4, 3 is inside right subtree of 5 -> needs > 5
```
हिंदी: सिर्फ parent से compare करना गलत है, पूरे ancestor chain की limit (low/high) लागू होती है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) worst | Space O(h)
Bounds:      Time O(n)         | Space O(h) ← preferred
Inorder:     Time O(n)         | Space O(h)
```

---

## ⚡ Variations

```python
# VARIANT 1: Allow duplicates on the left — use low <= val < high
# VARIANT 2: Recover BST (two nodes swapped) — inorder, find the two inversions
# VARIANT 3: Largest BST subtree — return (is_bst, size, min, max) from each node
print(is_valid_bst(build([2, 2, 2])))  # Expected: False (strict BST)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only compares with direct children
# return node.left.val < node.val < node.right.val and f(left) and f(right)
# -> accepts [5,1,4,None,None,3,6] wrongly (3 < 4 but 3 < 5 in right subtree)

# ❌ Wrong: using float("-inf") / int min as a sentinel with <= (breaks if node == INT_MIN)
# ✅ Correct: pass bounds down; infinities with strict < are safe in Python
```

---

## 🎯 Interview Tip
Say: "Local parent-child checks aren't enough, so I carry a (low, high) range down; each node tightens one side. Equivalent view: inorder must be strictly increasing." Ask whether duplicates are allowed.

---

## 🔗 Related Problems
→ D057 (LCA of a BST) | D062 (Kth Smallest in a BST) | D054 (Same Tree)
