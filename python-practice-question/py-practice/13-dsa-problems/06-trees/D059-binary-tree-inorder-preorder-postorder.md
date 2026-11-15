---

# D059. Binary Tree Inorder/Preorder/Postorder
# Category: DSA — Trees
# Difficulty: ⭐⭐ Medium | LeetCode #94 / #144 / #145

---

## ❓ Problem
Given the root of a binary tree, return its inorder (Left, Node, Right), preorder (Node, Left, Right) and postorder (Left, Right, Node) traversals. Implement both recursive and iterative versions.

```
Input:    1
           \
            2
           /
          3
Inorder:   [1, 3, 2]
Preorder:  [1, 2, 3]
Postorder: [3, 2, 1]
```

---

## 💡 Quick Concept (2 lines only)
The three orders differ only in when you visit the node: before, between, or after its children. Iteratively, use an explicit stack to replace the call stack.
हिंदी: तीनों traversal में फर्क बस इतना है कि node को बच्चों से पहले, बीच में या बाद में visit करते हैं; iterative में खुद का stack इस्तेमाल करते हैं।

---

## ✅ Solution

```python
from __future__ import annotations             # allow TreeNode self-reference in hints
from collections import deque                  # queue used by the builder
from typing import Optional                    # for Optional[TreeNode]


class TreeNode:
    def __init__(self, val: int = 0, left: Optional[TreeNode] = None,
                 right: Optional[TreeNode] = None) -> None:
        self.val = val                         # node value
        self.left = left                       # left child
        self.right = right                     # right child


def build_tree(values: list[Optional[int]]) -> Optional[TreeNode]:
    if not values or values[0] is None:        # empty tree
        return None                            # nothing to build
    root = TreeNode(values[0])                 # root node
    queue = deque([root])                      # nodes waiting for children
    i = 1                                      # index into values
    while queue and i < len(values):           # fill children level by level
        node = queue.popleft()                 # next parent
        if i < len(values) and values[i] is not None:  # left child present
            node.left = TreeNode(values[i])    # create left child
            queue.append(node.left)            # it needs children too
        i += 1                                 # consume left slot
        if i < len(values) and values[i] is not None:  # right child present
            node.right = TreeNode(values[i])   # create right child
            queue.append(node.right)           # it needs children too
        i += 1                                 # consume right slot
    return root                                # finished tree


# ============================================
# APPROACH 1: Recursive — O(n) time, O(h) stack (h can be n on a skewed tree)
# ============================================
def inorder_rec(root: Optional[TreeNode]) -> list[int]:
    if root is None:                           # base case
        return []                              # nothing to visit
    return inorder_rec(root.left) + [root.val] + inorder_rec(root.right)   # L, N, R


def preorder_rec(root: Optional[TreeNode]) -> list[int]:
    if root is None:                           # base case
        return []                              # nothing to visit
    return [root.val] + preorder_rec(root.left) + preorder_rec(root.right) # N, L, R


def postorder_rec(root: Optional[TreeNode]) -> list[int]:
    if root is None:                           # base case
        return []                              # nothing to visit
    return postorder_rec(root.left) + postorder_rec(root.right) + [root.val]  # L, R, N


# ============================================
# APPROACH 2: Iterative with explicit stack — O(n) time, O(h) space  PREFERRED
# ============================================
def inorder(root: Optional[TreeNode]) -> list[int]:
    result: list[int] = []                     # visit order
    stack: list[TreeNode] = []                 # nodes waiting for their turn
    curr = root                                # current node
    while curr or stack:                       # until everything is processed
        while curr:                            # go as far left as possible
            stack.append(curr)                 # remember the path
            curr = curr.left                   # descend left
        curr = stack.pop()                     # leftmost unvisited node
        result.append(curr.val)                # visit it (between children)
        curr = curr.right                      # then explore its right subtree
    return result                              # inorder values


def preorder(root: Optional[TreeNode]) -> list[int]:
    result: list[int] = []                     # visit order
    stack = [root] if root else []             # start with the root
    while stack:                               # while nodes remain
        node = stack.pop()                     # take the top node
        result.append(node.val)                # visit before children
        if node.right:                         # push right first
            stack.append(node.right)           # so left pops first
        if node.left:                          # push left second
            stack.append(node.left)            # processed next
    return result                              # preorder values


def postorder(root: Optional[TreeNode]) -> list[int]:
    result: list[int] = []                     # reversed visit order
    stack = [root] if root else []             # start with the root
    while stack:                               # while nodes remain
        node = stack.pop()                     # take the top node
        result.append(node.val)                # N, then R, then L (mirror of preorder)
        if node.left:                          # push left first
            stack.append(node.left)            # popped after right
        if node.right:                         # push right second
            stack.append(node.right)           # popped first
    return result[::-1]                        # reverse -> L, R, N


# ============================================
# TEST CASES
# ============================================
t = build_tree([1, None, 2, 3])
print(inorder_rec(t), preorder_rec(t), postorder_rec(t))   # [1, 3, 2] [1, 2, 3] [3, 2, 1]
print(inorder(t), preorder(t), postorder(t))               # [1, 3, 2] [1, 2, 3] [3, 2, 1]
b = build_tree([4, 2, 6, 1, 3, 5, 7])
print(inorder(b))                                          # [1, 2, 3, 4, 5, 6, 7]
print(preorder(b))                                         # [4, 2, 1, 3, 6, 5, 7]
print(postorder(b))                                        # [1, 3, 2, 5, 7, 6, 4]
print(inorder(None), preorder(None), postorder(None))      # [] [] []
```

---

## 🔍 Why It Works
```
        4
      /   \
     2     6
    / \   / \
   1   3 5   7
Inorder   (L N R): 1 2 3 4 5 6 7   (sorted for a BST!)
Preorder  (N L R): 4 2 1 3 6 5 7
Postorder (L R N): 1 3 2 5 7 6 4
```
हिंदी: Inorder में BST हमेशा sorted निकलता है; postorder को "N R L" लिखकर उलटने से आसानी से iterative बन जाता है।

---

## 📊 Complexity
```
Recursive: Time O(n) | Space O(h) stack (list concatenation here adds extra copying)
Iterative: Time O(n) | Space O(h)  <- preferred (no recursion limit issues)
```

---

## ⚡ Variations

```python
# VARIANT 1: Morris traversal — O(1) extra space by temporarily threading the tree
# VARIANT 2: N-ary tree traversals (LeetCode #589 / #590) — loop over children
# VARIANT 3: Kth Smallest Element in a BST (D062) — stop an inorder traversal at k
```

---

## ⚠️ Common Mistake
```python
# Wrong: iterative preorder pushing left before right -> visits right subtree first
#   stack.append(node.left); stack.append(node.right)
# Wrong: deep recursion on a skewed tree of 5000 nodes -> RecursionError (limit ~1000)
# Right: push right then left for preorder; use an explicit stack for deep trees
```

---

## 🎯 Interview Tip
Say: "Recursive is three lines; I'll also show the iterative version to avoid Python's recursion limit." Know the trick: postorder = reverse of (N, R, L). Inorder on a BST gives sorted order.

---

## 🔗 Related Problems
→ D056 (Validate Binary Search Tree) | D058 (Binary Tree Level Order Traversal) | D062 (Kth Smallest Element in a BST)
