---

# D054. Same Tree
# Category: DSA — Trees
# Difficulty: ⭐ Easy | LeetCode #100 | Asked: Amazon, Microsoft, LinkedIn

---

## ❓ Problem
Given the roots of two binary trees `p` and `q`, check whether they are the same: structurally identical and with equal node values.

```
Input:  p = [1,2,3], q = [1,2,3]   Output: True
Input:  p = [1,2],   q = [1,None,2] Output: False   (different structure)
Input:  p = [1,2,1], q = [1,1,2]   Output: False   (different values)
```

---

## 💡 Quick Concept (2 lines only)
Compare node by node: both None is equal; one None or different values is not; otherwise both left subtrees and both right subtrees must match.
हिंदी: दोनों None हों तो बराबर; एक None या value अलग हो तो अलग; वरना left-left और right-right दोनों match होने चाहिए।

---

## ✅ Solution

```python
from collections import deque                   # queue for BFS / building
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


# ============================================
# APPROACH 1: Brute force — serialise both trees (with None markers) and compare strings
# O(n) time, O(n) space
# ============================================
def serialize(root: Optional[TreeNode]) -> str:
    if root is None:                            # empty marker keeps structure info
        return "#"                              # distinguishes missing children
    return f"{root.val},{serialize(root.left)},{serialize(root.right)}"  # preorder with markers


def is_same_brute(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    return serialize(p) == serialize(q)         # identical strings <=> identical trees


# ============================================
# APPROACH 2: Recursive DFS — O(n) time, O(h) space ✅ PREFERRED
# ============================================
def is_same_tree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if p is None and q is None:                 # both empty
        return True                             # equal
    if p is None or q is None:                  # exactly one empty
        return False                            # structure differs
    if p.val != q.val:                          # values differ
        return False                            # not same
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)  # compare subtrees


# ============================================
# APPROACH 3: Iterative with a stack — no recursion limit
# ============================================
def is_same_iter(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    stack = [(p, q)]                            # pairs still to compare
    while stack:                                # until all pairs checked
        a, b = stack.pop()                      # next pair
        if a is None and b is None:             # both empty
            continue                            # fine, keep going
        if a is None or b is None or a.val != b.val:  # mismatch in structure or value
            return False                        # not same
        stack.append((a.left, b.left))          # compare left children
        stack.append((a.right, b.right))        # compare right children
    return True                                 # no mismatch found


# ============================================
# TEST CASES
# ============================================
cases = [
    ([1, 2, 3], [1, 2, 3]),                     # identical
    ([1, 2], [1, None, 2]),                     # different structure
    ([1, 2, 1], [1, 1, 2]),                     # different values
    ([], []),                                   # both empty
    ([], [1]),                                  # one empty
]
for a, b in cases:                              # run all three methods
    pa, pb = build(a), build(b)                 # build trees
    print(is_same_brute(pa, pb), is_same_tree(pa, pb), is_same_iter(pa, pb))
# True True True
# False False False
# False False False
# True True True
# False False False
```

---

## 🔍 Why It Works
```
p = [1,2]  (2 is LEFT)     q = [1,None,2]  (2 is RIGHT)
compare roots 1 == 1 ok
compare p.left=2 with q.left=None -> exactly one is None -> False
```
हिंदी: दोनों trees को एक साथ चलाओ; जहाँ भी structure या value में फर्क मिले वहीं False लौटा दो।

---

## 📊 Complexity
```
Serialise:    Time O(n) | Space O(n)
Recursive:    Time O(n) | Space O(h) ← preferred (stops at first mismatch)
Iterative:    Time O(n) | Space O(h) to O(n)
```

---

## ⚡ Variations

```python
# VARIANT 1: Subtree of Another Tree (LeetCode #572) — run is_same_tree at every node of the big tree
def is_subtree(root: Optional[TreeNode], sub: Optional[TreeNode]) -> bool:
    if root is None:                            # ran out of nodes
        return sub is None                      # only matches an empty subtree
    return is_same_tree(root, sub) or is_subtree(root.left, sub) or is_subtree(root.right, sub)
print(is_subtree(build([3, 4, 5, 1, 2]), build([4, 1, 2])))   # True

# VARIANT 2: Symmetric Tree (D055) — same idea comparing left with right mirrored
# VARIANT 3: Leaf-similar trees — compare leaf sequences instead
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: comparing only values via traversal without None markers
#    inorder of [1,2] (2 left) and [1,None,2] (2 right) are different here, but
#    preorder values [1,2] == [1,2] for both -> reports True (wrong!)
# ❌ Wrong: only `if not p and not q: return True` and then p.val -> AttributeError when one is None
# ✅ Correct: handle both-None, then one-None, then compare values and recurse
```

---

## 🎯 Interview Tip
Say: "Three checks in order: both None, exactly one None, value mismatch — then recurse on both pairs. It short-circuits at the first difference." Mention that serialisation needs None markers.

---

## 🔗 Related Problems
→ D052 (Maximum Depth of Binary Tree) | D053 (Invert Binary Tree) | D055 (Symmetric Tree)
