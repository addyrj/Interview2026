---

# D053. Invert Binary Tree
# Category: DSA — Trees
# Difficulty: ⭐ Easy | LeetCode #226 | Asked: Google, Amazon, Microsoft

---

## ❓ Problem
Invert a binary tree — swap the left and right children of every node — and return its root.

```
Input:       4                Output:      4
           /   \                         /   \
          2     7                       7     2
         / \   / \                     / \   / \
        1   3 6   9                   9   6 3   1
```

---

## 💡 Quick Concept (2 lines only)
At every node swap `left` and `right`, then do the same for both subtrees. Any traversal order works as long as each node is swapped once.
हिंदी: हर node पर left और right बदल दो, फिर दोनों subtrees के लिए यही दोहराओ।

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
    if not vals or vals[0] is None:             # empty tree
        return None                             # nothing to build
    root = TreeNode(vals[0])                    # root
    q = deque([root])                           # parents waiting for children
    i = 1                                       # next value index
    while q and i < len(vals):                  # while values remain
        node = q.popleft()                      # next parent
        if i < len(vals) and vals[i] is not None:   # left child present
            node.left = TreeNode(vals[i])       # create left
            q.append(node.left)                 # queue it
        i += 1                                  # consume left slot
        if i < len(vals) and vals[i] is not None:   # right child present
            node.right = TreeNode(vals[i])      # create right
            q.append(node.right)                # queue it
        i += 1                                  # consume right slot
    return root                                 # finished tree


def level_order(root: Optional[TreeNode]) -> list[list[int]]:
    out: list[list[int]] = []                   # values per level
    q = deque([root] if root else [])           # start with the root
    while q:                                    # per level
        out.append([n.val for n in q])          # snapshot of this level
        for _ in range(len(q)):                 # expand the level
            n = q.popleft()                     # next node
            if n.left: q.append(n.left)         # enqueue left
            if n.right: q.append(n.right)       # enqueue right
    return out                                  # level-order values


# ============================================
# APPROACH 1: Brute force — build a brand-new mirrored tree
# O(n) time, O(n) extra space (allocates every node again)
# ============================================
def invert_copy(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:                            # empty subtree
        return None                             # mirror of nothing
    return TreeNode(root.val, invert_copy(root.right), invert_copy(root.left))  # swapped copy


# ============================================
# APPROACH 2: Recursive in-place swap — O(n) time, O(h) space ✅ PREFERRED
# ============================================
def invert_tree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:                            # base case
        return None                             # nothing to swap
    root.left, root.right = invert_tree(root.right), invert_tree(root.left)  # swap inverted children
    return root                                 # same root, mutated


# ============================================
# APPROACH 3: Iterative BFS — O(n) time, O(w) space (no recursion limit)
# ============================================
def invert_iter(root: Optional[TreeNode]) -> Optional[TreeNode]:
    q = deque([root] if root else [])           # start with the root
    while q:                                    # until all nodes processed
        node = q.popleft()                      # next node
        node.left, node.right = node.right, node.left  # swap its children
        if node.left: q.append(node.left)       # continue with children
        if node.right: q.append(node.right)     # continue with children
    return root                                 # same root, mutated


# ============================================
# TEST CASES
# ============================================
vals = [4, 2, 7, 1, 3, 6, 9]                    # sample tree
print(level_order(invert_copy(build(vals))))    # [[4], [7, 2], [9, 6, 3, 1]]
print(level_order(invert_tree(build(vals))))    # [[4], [7, 2], [9, 6, 3, 1]]
print(level_order(invert_iter(build(vals))))    # [[4], [7, 2], [9, 6, 3, 1]]
print(level_order(invert_tree(build([2, 1, 3]))))   # [[2], [3, 1]]
print(level_order(invert_tree(build([]))))      # []
```

---

## 🔍 Why It Works
```
node 4: swap children (2,7) -> (7,2), and recursively invert both
node 2: (1,3) -> (3,1)    node 7: (6,9) -> (9,6)
Python's tuple assignment swaps without a temp variable:
root.left, root.right = invert(root.right), invert(root.left)
```
हिंदी: Tuple assignment से temp variable के बिना swap हो जाता है, और हर node ठीक एक बार visit होता है।

---

## 📊 Complexity
```
Copy-based:      Time O(n) | Space O(n)
Recursive swap:  Time O(n) | Space O(h) ← preferred
Iterative BFS:   Time O(n) | Space O(w)
```

---

## ⚡ Variations

```python
# VARIANT 1: Check if a tree is symmetric (D055) — compare left with the mirror of right
# VARIANT 2: Flip equivalent binary trees (LeetCode #951) — children may or may not be swapped
# VARIANT 3: Invert using an explicit stack (DFS) instead of a queue — same code with pop()
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: overwriting before saving -> both children end up the same subtree
#    root.left = invert(root.right)
#    root.right = invert(root.left)     # root.left is already the new value!
# ✅ Correct: tuple swap, or temp = root.left first
#    root.left, root.right = invert(root.right), invert(root.left)
```

---

## 🎯 Interview Tip
Say: "Swap the children at each node and recurse — O(n) time, O(h) space. I use tuple assignment to avoid the temp-variable bug, and BFS if recursion depth is a concern."

---

## 🔗 Related Problems
→ D052 (Maximum Depth of Binary Tree) | D054 (Same Tree) | D055 (Symmetric Tree)
