---

# D061. Path Sum
# Category: DSA — Trees
# Difficulty: ⭐ Easy | LeetCode #112

---

## ❓ Problem
Given the root of a binary tree and an integer `target_sum`, return `True` if the tree has a **root-to-leaf** path whose node values add up to `target_sum`.

```
Input:        5
             / \
            4   8
           /   / \
          11  13  4
         /  \      \
        7    2      1
        target_sum = 22
Output: True   (5 → 4 → 11 → 2)
```

---

## 💡 Quick Concept (2 lines only)
Subtract the node's value from the target as you go down. At a leaf, check whether the remaining target equals the leaf's value.
हिंदी: नीचे जाते हुए target में से node की value घटाते जाओ; leaf पर पहुँचकर देखो कि बचा हुआ target उसी leaf की value के बराबर है या नहीं।

---

## ✅ Solution

```python
from __future__ import annotations             # allow TreeNode self-reference in hints
from collections import deque                  # queue used by the builder / BFS
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
# APPROACH 1: Brute force — enumerate all root-to-leaf paths, sum each
# O(n) time (each node visited once per path it is on -> O(n log n) balanced, O(n^2) skewed), O(n) space
# ============================================
def has_path_sum_brute(root: Optional[TreeNode], target_sum: int) -> bool:
    paths: list[list[int]] = []                # every root-to-leaf path

    def collect(node: Optional[TreeNode], path: list[int]) -> None:
        if node is None:                       # empty subtree
            return                             # stop
        path = path + [node.val]               # extend path (copy keeps siblings independent)
        if node.left is None and node.right is None:  # leaf reached
            paths.append(path)                 # store the full path
            return                             # done with this branch
        collect(node.left, path)               # explore left
        collect(node.right, path)              # explore right

    collect(root, [])                          # gather paths
    return any(sum(p) == target_sum for p in paths)  # does any path match?


# ============================================
# APPROACH 2: DFS subtracting from target — O(n) time, O(h) space  PREFERRED
# ============================================
def has_path_sum(root: Optional[TreeNode], target_sum: int) -> bool:
    if root is None:                           # empty tree has no path
        return False                           # no leaf to end on
    remaining = target_sum - root.val          # what is still needed below
    if root.left is None and root.right is None:  # a leaf
        return remaining == 0                  # path works only if nothing remains
    return (has_path_sum(root.left, remaining)       # try the left subtree
            or has_path_sum(root.right, remaining))  # or the right subtree


# ============================================
# APPROACH 3: Iterative DFS with (node, remaining) stack — O(n) time, O(h) space
# ============================================
def has_path_sum_iter(root: Optional[TreeNode], target_sum: int) -> bool:
    if root is None:                           # empty tree
        return False                           # no path
    stack = [(root, target_sum - root.val)]    # node with what is left after it
    while stack:                               # until all branches are checked
        node, remaining = stack.pop()          # next node
        if node.left is None and node.right is None and remaining == 0:  # matching leaf
            return True                        # found a path
        if node.right:                         # push right child
            stack.append((node.right, remaining - node.right.val))  # update remaining
        if node.left:                          # push left child
            stack.append((node.left, remaining - node.left.val))    # update remaining
    return False                               # no path matched


# ============================================
# TEST CASES
# ============================================
t = build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
print(has_path_sum_brute(t, 22))               # True
print(has_path_sum(t, 22))                     # True
print(has_path_sum_iter(t, 22))                # True
print(has_path_sum(t, 5))                      # False  (5 alone is not a leaf)
print(has_path_sum(build_tree([1, 2, 3]), 5))  # False
print(has_path_sum(build_tree([]), 0))         # False
print(has_path_sum(build_tree([1, 2]), 1))     # False  (node 1 has a child, not a leaf)
print(has_path_sum(build_tree([-2, None, -3]), -5))  # True
```

---

## 🔍 Why It Works
```
target 22 at 5 -> remaining 17 at 4 -> 13 at 11 -> 2 at leaf 2: remaining 0 -> True
At leaf 7: remaining 13-7=6 -> False (try the other branch)
```
हिंदी: सिर्फ़ leaf पर ही जवाब तय होता है; बीच के node पर सही sum मिलना काफ़ी नहीं (जैसे `[1,2]` में target 1 पर False)।

---

## 📊 Complexity
```
Collect paths: Time O(n * h) | Space O(n * h)
DFS subtract:  Time O(n)     | Space O(h)  <- preferred
Iterative DFS: Time O(n)     | Space O(h)
```

---

## ⚡ Variations

```python
# VARIANT 1: Path Sum II (LeetCode #113) — return all root-to-leaf paths with that sum (backtracking)
# VARIANT 2: Path Sum III (LeetCode #437) — any downward path; use prefix-sum hash map
# VARIANT 3: Sum Root to Leaf Numbers (LeetCode #129) — carry value*10 + digit downwards
```

---

## ⚠️ Common Mistake
```python
# Wrong: checking remaining == 0 at ANY node, not only at leaves
#   if remaining == 0: return True       # [1,2], target 1 gives True incorrectly
# Wrong: treating a node with one child as a leaf (a missing child is not a leaf)
# Right: leaf means left is None AND right is None
```

---

## 🎯 Interview Tip
Say: "I carry the remaining sum down, and only decide at leaves — a node with one child isn't a leaf. Negative values mean I can't prune early." Clarify with the interviewer that the path must end at a leaf.

---

## 🔗 Related Problems
→ D052 (Maximum Depth of Binary Tree) | D060 (Diameter of Binary Tree) | D056 (Validate Binary Search Tree)
