---

# D055. Symmetric Tree
# Category: DSA — Trees
# Difficulty: ⭐ Easy | LeetCode #101

---

## ❓ Problem
Given the root of a binary tree, check whether it is a mirror of itself (symmetric around its center).

```
Input:  root = [1,2,2,3,4,4,3]   Output: True
Input:  root = [1,2,2,None,3,None,3]   Output: False
```

---

## 💡 Quick Concept (2 lines only)
A tree is symmetric if its left and right subtrees are mirrors: same value, and left.left mirrors right.right, left.right mirrors right.left.
हिंदी: Left और right subtree एक-दूसरे का mirror होने चाहिए — बाहर वाले जोड़े और अंदर वाले जोड़े compare करो।

---

## ✅ Solution

```python
from __future__ import annotations           # allow forward type hints
from collections import deque                # queue for the iterative version
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
            q.append(node.left)              # it needs children later
        i += 1                               # move past left slot
        if i < len(arr) and arr[i] is not None:  # right child exists?
            node.right = TreeNode(arr[i])    # create it
            q.append(node.right)             # it needs children later
        i += 1                               # move past right slot
    return root                              # finished tree


# ============================================
# APPROACH 1: Brute force — mirror a copy, then compare
# O(n) time, O(n) space (builds a whole extra tree)
# ============================================
def mirror(node: Optional[TreeNode]) -> Optional[TreeNode]:  # returns a mirrored copy
    if node is None:                         # empty -> empty
        return None                          # base case
    return TreeNode(node.val, mirror(node.right), mirror(node.left))  # swap children


def same(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:  # structural equality
    if a is None and b is None:              # both empty
        return True                          # equal
    if a is None or b is None or a.val != b.val:  # one missing or values differ
        return False                         # not equal
    return same(a.left, b.left) and same(a.right, b.right)  # compare both sides


def is_symmetric_brute(root: Optional[TreeNode]) -> bool:  # brute force check
    return same(root, mirror(root))          # tree equals its own mirror


# ============================================
# APPROACH 2: Recursive mirror check — O(n) time, O(h) space ✅ PREFERRED
# ============================================
def is_symmetric(root: Optional[TreeNode]) -> bool:  # optimal recursive
    def mirror_eq(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:  # are a and b mirrors?
        if a is None and b is None:          # both empty
            return True                      # mirrors
        if a is None or b is None:           # only one empty
            return False                     # not mirrors
        return (a.val == b.val               # same value
                and mirror_eq(a.left, b.right)   # outer pair
                and mirror_eq(a.right, b.left))  # inner pair

    return root is None or mirror_eq(root.left, root.right)  # empty tree is symmetric


# ============================================
# APPROACH 3: Iterative with a queue — O(n) time, O(w) space
# ============================================
def is_symmetric_iter(root: Optional[TreeNode]) -> bool:  # BFS pairs
    if root is None:                         # empty tree
        return True                          # symmetric
    q = deque([(root.left, root.right)])     # start with the two subtrees
    while q:                                 # until no pairs left
        a, b = q.popleft()                   # take a pair
        if a is None and b is None:          # both empty
            continue                         # fine, next pair
        if a is None or b is None or a.val != b.val:  # mismatch
            return False                     # not symmetric
        q.append((a.left, b.right))          # outer pair
        q.append((a.right, b.left))          # inner pair
    return True                              # every pair matched


# ============================================
# TEST CASES
# ============================================
t1 = build([1, 2, 2, 3, 4, 4, 3])            # symmetric tree
t2 = build([1, 2, 2, None, 3, None, 3])      # not symmetric
for fn in (is_symmetric_brute, is_symmetric, is_symmetric_iter):  # run all approaches
    print(fn.__name__, fn(t1), fn(t2), fn(build([])), fn(build([1])))
# Expected (each line): True False True True
```

---

## 🔍 Why It Works
```
      1
     / \
    2   2        pair (2,2) -> values equal
   / \ / \       pair (3,3) outer  -> equal
  3  4 4  3      pair (4,4) inner  -> equal   => symmetric
```
हिंदी: दो pointers एक साथ चलाओ — एक left side, दूसरा right side, और children उल्टे क्रम में compare करो।

---

## 📊 Complexity
```
Brute force: Time O(n) | Space O(n) — extra mirrored tree
Recursive:   Time O(n) | Space O(h) — call stack (O(n) worst case)
Iterative:   Time O(n) | Space O(w) — queue width
```

---

## ⚡ Variations

```python
# VARIANT 1: Same Tree (D054) — compare a.left with b.left instead of crossing
# VARIANT 2: Subtree of Another Tree — run same() at every node
# VARIANT 3: Symmetric by values only (ignore structure) — compare inorder lists
# (inorder list palindrome is NOT enough: [1,2,3] shapes can fool it)
print(same(build([1, 2, 3]), build([1, 2, 3])))  # Expected: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing left with right directly (that is Same Tree, not mirror)
# return a.val == b.val and f(a.left, b.left) and f(a.right, b.right)

# ❌ Wrong: only checking values level by level without None markers
# [1,2,2,None,3,None,3] has symmetric-looking values but different shape

# ✅ Correct: cross compare (a.left, b.right) and (a.right, b.left)
```

---

## 🎯 Interview Tip
Say: "Symmetric is Same Tree with a twist: I compare outer pair and inner pair. Recursion is O(h) space; I can also do it iteratively with a queue of pairs." Mention the None check first.

---

## 🔗 Related Problems
→ D054 (Same Tree) | D053 (Invert Binary Tree) | D052 (Maximum Depth of Binary Tree)
