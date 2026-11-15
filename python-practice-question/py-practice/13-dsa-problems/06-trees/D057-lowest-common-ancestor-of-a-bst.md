---

# D057. Lowest Common Ancestor of a BST
# Category: DSA — Trees
# Difficulty: ⭐⭐ Medium | LeetCode #235

---

## ❓ Problem
Given a BST and two nodes p and q (both present), return their lowest common ancestor: the deepest node that has both p and q as descendants (a node may be a descendant of itself).

```
Input:  root = [6,2,8,0,4,7,9,None,None,3,5], p = 2, q = 8   Output: 6
Input:  same tree, p = 2, q = 4                              Output: 2
```

---

## 💡 Quick Concept (2 lines only)
Use the BST order: if both values are smaller than node go left, if both larger go right, otherwise this node is the split point and is the LCA.
हिंदी: दोनों values छोटी हैं तो left, दोनों बड़ी हैं तो right, वरना जहाँ रास्ता बँटे वही LCA है।

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


def find(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:  # helper: locate node by value in BST
    while root and root.val != val:          # walk down using BST order
        root = root.left if val < root.val else root.right  # choose side
    return root                              # node or None


# ============================================
# APPROACH 1: Brute force — store root-to-node paths, find last common node
# O(h) time, O(h) space
# ============================================
def path_to(root: TreeNode, target: TreeNode) -> list[TreeNode]:  # path from root to target
    path = []                                # nodes along the way
    node = root                              # start at root
    while node:                              # walk until we fall off
        path.append(node)                    # record node
        if node is target:                   # reached target
            break                            # stop
        node = node.left if target.val < node.val else node.right  # follow BST order
    return path                              # the path


def lca_brute(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:  # compare two paths
    lca = root                               # root is always a common ancestor
    for a, b in zip(path_to(root, p), path_to(root, q)):  # walk both paths together
        if a is b:                           # still the same node
            lca = a                          # deeper common ancestor
        else:                                # paths diverged
            break                            # stop
    return lca                               # last shared node


# ============================================
# APPROACH 2: Iterative BST walk — O(h) time, O(1) space ✅ PREFERRED
# ============================================
def lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:  # optimal
    node = root                              # start at the root
    while node:                              # until found
        if p.val < node.val and q.val < node.val:    # both on the left
            node = node.left                 # go left
        elif p.val > node.val and q.val > node.val:  # both on the right
            node = node.right               # go right
        else:                                # split point (or node equals p or q)
            return node                      # this is the LCA
    return root                              # unreachable for valid input


# ============================================
# APPROACH 3: Recursive — O(h) time, O(h) stack
# ============================================
def lca_recursive(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:  # recursive version
    if p.val < root.val and q.val < root.val:    # both smaller
        return lca_recursive(root.left, p, q)   # search left
    if p.val > root.val and q.val > root.val:    # both larger
        return lca_recursive(root.right, p, q)  # search right
    return root                              # split point


# ============================================
# TEST CASES
# ============================================
tree = build([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])  # classic BST
for a, b in [(2, 8), (2, 4), (3, 5), (0, 5), (7, 9)]:  # value pairs
    p, q = find(tree, a), find(tree, b)      # locate the nodes
    print(a, b, lca_brute(tree, p, q).val, lowest_common_ancestor(tree, p, q).val, lca_recursive(tree, p, q).val)
# Expected:
# 2 8 6 6 6
# 2 4 2 2 2
# 3 5 4 4 4
# 0 5 2 2 2
# 7 9 8 8 8
```

---

## 🔍 Why It Works
```
        6
      /   \
     2     8      p=3, q=5: at 6 both < 6 -> left
    / \   / \     at 2 both > 2 -> right
   0   4 7   9    at 4: 3 < 4 < 5 -> split -> LCA = 4
      / \
     3   5
```
हिंदी: BST में order पता है, इसलिए पूरा tree search नहीं करना — बस एक रास्ता नीचे उतरो।

---

## 📊 Complexity
```
Brute force: Time O(h) | Space O(h) — two stored paths
Iterative:   Time O(h) | Space O(1) ← preferred
Recursive:   Time O(h) | Space O(h) — call stack
(h = height; O(log n) balanced, O(n) skewed)
```

---

## ⚡ Variations

```python
# VARIANT 1: LCA of a general binary tree — recurse both sides, return node if left & right both found
# VARIANT 2: p or q may be missing — first verify both exist with find()
# VARIANT 3: Nodes have parent pointers — walk up like intersection of two linked lists
print(find(tree, 99))  # Expected: None
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using the general-tree algorithm and visiting every node -> O(n), ignores BST property
# ❌ Wrong: using <= / >= so that when node == p you keep descending and skip the answer
# ✅ Correct: go left only if BOTH are strictly smaller, right only if BOTH strictly larger
```

---

## 🎯 Interview Tip
Say: "Because it's a BST, the LCA is the first node whose value lies between p and q (inclusive). I walk down iteratively, so O(h) time and O(1) space." If it was a plain binary tree, switch to the recursive left/right approach.

---

## 🔗 Related Problems
→ D056 (Validate BST) | D062 (Kth Smallest in a BST) | D052 (Maximum Depth of Binary Tree)
