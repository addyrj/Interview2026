---

# D058. Binary Tree Level Order Traversal
# Category: DSA — Trees
# Difficulty: ⭐⭐ Medium | LeetCode #102

---

## ❓ Problem
Given the root of a binary tree, return its node values level by level (left to right), as a list of lists.

```
Input:      3
           / \
          9  20
             / \
            15  7
Output: [[3], [9, 20], [15, 7]]
```

---

## 💡 Quick Concept (2 lines only)
BFS with a queue. At each round, process exactly `len(queue)` nodes (one level), collecting their values and enqueueing their children.
हिंदी: Queue में root डालो; हर round में उस समय की queue की length जितने nodes निकालो — वही एक level है — और उनके बच्चे queue में डालो।

---

## ✅ Solution

```python
from __future__ import annotations             # allow TreeNode self-reference in hints
from collections import deque                  # O(1) popleft for BFS queue
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
# APPROACH 1: Recursive DFS with a depth parameter — O(n) time, O(h) stack
# ============================================
def level_order_dfs(root: Optional[TreeNode]) -> list[list[int]]:
    levels: list[list[int]] = []               # result grouped by depth

    def dfs(node: Optional[TreeNode], depth: int) -> None:
        if node is None:                       # empty subtree
            return                             # stop
        if depth == len(levels):               # first time reaching this depth
            levels.append([])                  # open a new level bucket
        levels[depth].append(node.val)         # record the value at its depth
        dfs(node.left, depth + 1)              # left child is one level deeper
        dfs(node.right, depth + 1)             # right child is one level deeper

    dfs(root, 0)                               # start at depth 0
    return levels                              # grouped values


# ============================================
# APPROACH 2: BFS with queue, one level per round — O(n) time, O(w) space  PREFERRED
# ============================================
def level_order(root: Optional[TreeNode]) -> list[list[int]]:
    if root is None:                           # empty tree
        return []                              # no levels
    result: list[list[int]] = []               # answer
    queue = deque([root])                      # start with the root
    while queue:                               # while nodes remain
        level: list[int] = []                  # values of this level
        for _ in range(len(queue)):            # freeze the current level size
            node = queue.popleft()             # take the next node
            level.append(node.val)             # record value
            if node.left:                      # enqueue left child
                queue.append(node.left)        # next level
            if node.right:                     # enqueue right child
                queue.append(node.right)       # next level
        result.append(level)                   # finished one level
    return result                              # all levels


# ============================================
# TEST CASES
# ============================================
t = build_tree([3, 9, 20, None, None, 15, 7])
print(level_order_dfs(t))                      # [[3], [9, 20], [15, 7]]
print(level_order(t))                          # [[3], [9, 20], [15, 7]]
print(level_order(build_tree([1])))            # [[1]]
print(level_order(build_tree([])))             # []
print(level_order(build_tree([1, 2, 3, 4, None, None, 5])))  # [[1], [2, 3], [4, 5]]
print(level_order(build_tree([1, None, 2, None, 3])))        # [[1], [2], [3]]
```

---

## 🔍 Why It Works
```
queue: [3]            -> level [3]       enqueue 9, 20
queue: [9, 20]        -> level [9, 20]   enqueue 15, 7
queue: [15, 7]        -> level [15, 7]
queue: []             -> done
```
हिंदी: `len(queue)` को loop शुरू होने से पहले fix कर लेते हैं, इसलिए नए बच्चे उसी round में नहीं गिने जाते।

---

## 📊 Complexity
```
DFS with depth: Time O(n) | Space O(h) stack (+ output)
BFS queue:      Time O(n) | Space O(w) where w = max width  <- preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Zigzag level order (LeetCode #103) — reverse every other level
# VARIANT 2: Right side view (LeetCode #199) — take the last node of each level
# VARIANT 3: Bottom-up level order (LeetCode #107) — reverse the final result
```

---

## ⚠️ Common Mistake
```python
# Wrong: using list.pop(0) as the queue -> O(n) per pop, O(n^2) total
# Wrong: looping `while queue` for the inner loop too -> mixes levels together
# Right: collections.deque and `for _ in range(len(queue))`
```

---

## 🎯 Interview Tip
Say: "BFS with a deque, freezing the queue size per level." Mention `deque.popleft()` is O(1) while `list.pop(0)` is O(n). Handle the empty tree first.

---

## 🔗 Related Problems
→ D052 (Maximum Depth of Binary Tree) | D059 (Binary Tree Inorder/Preorder/Postorder) | D055 (Symmetric Tree)
