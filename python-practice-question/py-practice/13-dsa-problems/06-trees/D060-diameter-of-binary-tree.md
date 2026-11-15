---

# D060. Diameter of Binary Tree
# Category: DSA — Trees
# Difficulty: ⭐ Easy | LeetCode #543

---

## ❓ Problem
Return the length of the diameter of a binary tree: the number of **edges** on the longest path between any two nodes. The path may or may not pass through the root.

```
Input:      1
           / \
          2   3
         / \
        4   5
Output: 3   (path 4 → 2 → 1 → 3 or 5 → 2 → 1 → 3)
```

---

## 💡 Quick Concept (2 lines only)
For each node, the longest path through it is `height(left) + height(right)`. Compute heights bottom-up and keep the maximum of that sum across all nodes.
हिंदी: हर node पर left height + right height उस node से गुज़रने वाला सबसे लंबा path है; सबका maximum ही diameter है।

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
# APPROACH 1: Brute force — height() recomputed at every node
# O(n^2) worst case time (skewed tree), O(h) space
# ============================================
def diameter_brute(root: Optional[TreeNode]) -> int:
    def height(node: Optional[TreeNode]) -> int:
        if node is None:                       # empty subtree has height 0
            return 0                           # base case
        return 1 + max(height(node.left), height(node.right))  # nodes on longest downward path

    if root is None:                           # empty tree
        return 0                               # no edges
    through_root = height(root.left) + height(root.right)  # longest path through this node
    return max(through_root, diameter_brute(root.left), diameter_brute(root.right))  # best of all


# ============================================
# APPROACH 2: Single DFS returning height, updating best — O(n) time, O(h) space  PREFERRED
# ============================================
def diameter_of_binary_tree(root: Optional[TreeNode]) -> int:
    best = 0                                   # longest path (in edges) seen so far

    def height(node: Optional[TreeNode]) -> int:
        nonlocal best                          # we update the outer variable
        if node is None:                       # empty subtree
            return 0                           # height 0
        left = height(node.left)               # height of left subtree
        right = height(node.right)             # height of right subtree
        best = max(best, left + right)         # path through this node (edges)
        return 1 + max(left, right)            # height reported to the parent

    height(root)                               # one traversal fills `best`
    return best                                # diameter


# ============================================
# TEST CASES
# ============================================
t = build_tree([1, 2, 3, 4, 5])
print(diameter_brute(t))                       # 3
print(diameter_of_binary_tree(t))              # 3
print(diameter_of_binary_tree(build_tree([1, 2])))        # 1
print(diameter_of_binary_tree(build_tree([1])))           # 0
print(diameter_of_binary_tree(build_tree([])))            # 0
print(diameter_of_binary_tree(build_tree([1, 2, None, 3, None, 4])))  # 3
```

---

## 🔍 Why It Works
```
        1
       / \
      2   3
     / \
    4   5
height(4)=1 height(5)=1 -> at node 2: 1+1=2, returns 2
height(3)=1
at node 1: left=2, right=1 -> 3  <- best
```
हिंदी: Height लौटाते हुए ही हर node पर "left+right" check करने से पूरा tree सिर्फ़ एक बार घूमना पड़ता है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) worst | Space O(h)
Single DFS:  Time O(n)         | Space O(h)  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Binary Tree Maximum Path Sum (LeetCode #124) — same pattern with values, ignore negative branches
# VARIANT 2: Diameter counted in nodes instead of edges -> add 1
# VARIANT 3: Longest univalue path (LeetCode #687) — only extend when values match
```

---

## ⚠️ Common Mistake
```python
# Wrong: assuming the longest path goes through the root
#   return height(root.left) + height(root.right)   # fails for a deep path inside a subtree
# Wrong: counting nodes instead of edges -> answer off by one
# Right: track a global max updated at every node
```

---

## 🎯 Interview Tip
Say: "The answer at each node is left height plus right height, but the function must return only 1 + max(left, right) to its parent. I keep a nonlocal max." This 'return one thing, record another' pattern appears in many tree problems.

---

## 🔗 Related Problems
→ D052 (Maximum Depth of Binary Tree) | D056 (Validate Binary Search Tree) | D061 (Path Sum)
