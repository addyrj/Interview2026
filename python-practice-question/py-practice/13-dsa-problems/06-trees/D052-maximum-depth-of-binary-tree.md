---

# D052. Maximum Depth of Binary Tree
# Category: DSA — Trees
# Difficulty: ⭐ Easy | LeetCode #104 | Asked: Amazon, Microsoft, Google, LinkedIn

---

## ❓ Problem
Given the root of a binary tree, return its maximum depth — the number of nodes along the longest path from the root down to a leaf.

```
Input:      3
           / \
          9  20
             / \
            15  7
Output: 3
```

---

## 💡 Quick Concept (2 lines only)
Depth of a node = 1 + max(depth of left, depth of right); an empty tree has depth 0. Or count levels with BFS.
हिंदी: Depth = 1 + (left और right में से बड़ी depth); खाली tree की depth 0 होती है।

---

## ✅ Solution

```python
from collections import deque                   # queue for BFS
from typing import Optional                     # nodes may be None


class TreeNode:
    def __init__(self, val: int = 0, left: "Optional[TreeNode]" = None,
                 right: "Optional[TreeNode]" = None) -> None:
        self.val = val                          # node value
        self.left = left                        # left child
        self.right = right                      # right child


def build(vals: list[Optional[int]]) -> Optional[TreeNode]:
    # Build a tree from a level-order list (LeetCode style, None = missing child)
    if not vals or vals[0] is None:             # empty tree
        return None                             # nothing to build
    root = TreeNode(vals[0])                    # root node
    q = deque([root])                           # parents waiting for children
    i = 1                                       # next value index
    while q and i < len(vals):                  # while values remain
        node = q.popleft()                      # next parent
        if i < len(vals) and vals[i] is not None:   # left child present
            node.left = TreeNode(vals[i])       # create left
            q.append(node.left)                 # it needs children too
        i += 1                                  # consume the left slot
        if i < len(vals) and vals[i] is not None:   # right child present
            node.right = TreeNode(vals[i])      # create right
            q.append(node.right)                # it needs children too
        i += 1                                  # consume the right slot
    return root                                 # finished tree


# ============================================
# APPROACH 1: Brute force — collect every root-to-leaf path, take the longest
# O(n) time, O(n * h) space for the stored paths
# ============================================
def depth_brute(root: Optional[TreeNode]) -> int:
    paths: list[list[int]] = []                 # all root-to-leaf paths

    def walk(node: Optional[TreeNode], path: list[int]) -> None:
        if not node:                            # fell off the tree
            return                              # nothing to add
        path = path + [node.val]                # extend path (copy)
        if not node.left and not node.right:    # leaf
            paths.append(path)                  # store full path
            return                              # done with this branch
        walk(node.left, path)                   # explore left
        walk(node.right, path)                  # explore right

    walk(root, [])                              # start at the root
    return max((len(p) for p in paths), default=0)  # longest path, 0 if empty


# ============================================
# APPROACH 2: Recursive DFS — O(n) time, O(h) space ✅ PREFERRED
# ============================================
def max_depth(root: Optional[TreeNode]) -> int:
    if root is None:                            # base case: empty tree
        return 0                                # depth 0
    return 1 + max(max_depth(root.left), max_depth(root.right))  # this node + deeper side


# ============================================
# APPROACH 3: Iterative BFS — O(n) time, O(w) space (w = max width)
# ============================================
def max_depth_bfs(root: Optional[TreeNode]) -> int:
    if not root:                                # empty tree
        return 0                                # depth 0
    q = deque([root])                           # current level
    depth = 0                                   # levels counted
    while q:                                    # while levels remain
        depth += 1                              # entering a new level
        for _ in range(len(q)):                 # process exactly this level
            node = q.popleft()                  # next node
            if node.left:                       # enqueue children
                q.append(node.left)             # left
            if node.right:                      # enqueue children
                q.append(node.right)            # right
    return depth                                # number of levels


# ============================================
# TEST CASES
# ============================================
t = build([3, 9, 20, None, None, 15, 7])        # sample tree
print(depth_brute(t), max_depth(t), max_depth_bfs(t))   # 3 3 3
print(max_depth(build([1, None, 2])))           # 2
print(max_depth(build([])))                     # 0
print(max_depth(build([1])))                    # 1
print(max_depth(build([1, 2, None, 3, None, 4])))   # 4
```

---

## 🔍 Why It Works
```
        3                depth(3) = 1 + max(depth(9), depth(20))
       / \               depth(9) = 1
      9  20              depth(20) = 1 + max(1, 1) = 2
         / \             => 1 + max(1, 2) = 3
        15  7
```
हिंदी: हर node अपने बच्चों की depth माँगता है और उसमें 1 जोड़कर ऊपर लौटाता है।

---

## 📊 Complexity
```
Brute force (paths): Time O(n) | Space O(n*h)
Recursive DFS:       Time O(n) | Space O(h) — h = height, O(n) worst (skewed) ← preferred
BFS:                 Time O(n) | Space O(w)
```

---

## ⚡ Variations

```python
# VARIANT 1: Minimum depth (LeetCode #111) — first leaf found by BFS; careful with one-child nodes
# VARIANT 2: Check if the tree is balanced (LeetCode #110) — return -1 on imbalance
# VARIANT 3: N-ary tree max depth (LeetCode #559) — 1 + max(depth of each child)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: returning 1 for None -> every answer is off by one
#    if root is None: return 1
# ❌ Wrong: forgetting the "+ 1" for the current node
# ❌ Python caveat: recursion limit is ~1000 -> a skewed tree of 10^5 nodes raises RecursionError
# ✅ Correct: None -> 0, return 1 + max(...), and use BFS for very deep trees
```

---

## 🎯 Interview Tip
Say: "Recursively, depth is 1 + max of the children, with an empty tree as 0. In Python I mention the recursion limit and offer BFS as the iterative alternative." Both are O(n).

---

## 🔗 Related Problems
→ D053 (Invert Binary Tree) | D054 (Same Tree) | D060 (Diameter of Binary Tree)
