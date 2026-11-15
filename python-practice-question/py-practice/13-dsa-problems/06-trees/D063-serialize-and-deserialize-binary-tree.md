---

# D063. Serialize and Deserialize Binary Tree
# Category: DSA — Trees
# Difficulty: ⭐⭐⭐ Hard | LeetCode #297

---

## ❓ Problem
Design an algorithm to convert a binary tree into a string (`serialize`) and rebuild the exact same tree from that string (`deserialize`). Any format is allowed as long as the round trip works.

```
Input:  root = [1,2,3,None,None,4,5]
serialize   -> "1,2,#,#,3,4,#,#,5,#,#"
deserialize -> the same tree back
```

---

## 💡 Quick Concept (2 lines only)
Preorder DFS writing a `#` marker for every missing child makes the string unambiguous. To rebuild, read tokens in the same order: a value creates a node and recurses left then right, a `#` returns None.
हिंदी: Preorder में None की जगह `#` लिखो; वापस बनाते समय उसी क्रम में tokens पढ़ो — value आए तो node, `#` आए तो None।

---

## ✅ Solution

```python
from __future__ import annotations           # allow forward type hints
from collections import deque                # queue used by build() and BFS codec
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


def same(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:  # structural equality check
    if a is None or b is None:               # one side empty
        return a is b                        # equal only if both empty
    return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)  # compare recursively


# ============================================
# APPROACH 1: Brute force — serialize with plain recursion and string concatenation
# O(n^2) worst case because repeated string concatenation copies text
# ============================================
def serialize_brute(root: Optional[TreeNode]) -> str:
    if root is None:                         # empty subtree
        return "#"                           # marker
    return f"{root.val}," + serialize_brute(root.left) + "," + serialize_brute(root.right)  # preorder text


# ============================================
# APPROACH 2: Preorder DFS with token list + iterator ✅ PREFERRED
# O(n) time, O(n) space (O(h) recursion)
# ============================================
class Codec:
    def serialize(self, root: Optional[TreeNode]) -> str:
        out: list[str] = []                  # tokens collected here

        def dfs(node: Optional[TreeNode]) -> None:   # preorder walk
            if node is None:                 # missing child
                out.append("#")              # write marker
                return                       # stop this branch
            out.append(str(node.val))        # write node value
            dfs(node.left)                   # then left subtree
            dfs(node.right)                  # then right subtree

        dfs(root)                            # start at root
        return ",".join(out)                 # one string

    def deserialize(self, data: str) -> Optional[TreeNode]:
        tokens = iter(data.split(","))       # iterator keeps position across recursion

        def dfs() -> Optional[TreeNode]:     # rebuild in same preorder
            tok = next(tokens)               # consume next token
            if tok == "#":                   # marker means no node
                return None                  # empty subtree
            node = TreeNode(int(tok))        # create node from value
            node.left = dfs()                # rebuild left subtree first
            node.right = dfs()               # then right subtree
            return node                      # finished subtree

        return dfs()                         # rebuild whole tree


# ============================================
# TEST CASES
# ============================================
codec = Codec()                              # codec instance
t = build([1, 2, 3, None, None, 4, 5])       # sample tree
s = codec.serialize(t)                       # serialize it
print(s)                                     # Expected: 1,2,#,#,3,4,#,#,5,#,#
print(serialize_brute(t) == s)               # Expected: True
print(same(codec.deserialize(s), t))         # Expected: True
print(codec.serialize(None))                 # Expected: #
print(codec.deserialize("#"))                # Expected: None
neg = build([-1, 0, 1])                      # negative values work too
print(same(codec.deserialize(codec.serialize(neg)), neg))  # Expected: True
```

---

## 🔍 Why It Works
```
    1
   / \
  2   3        preorder: 1 2 # # 3 4 # # 5 # #
     / \
    4   5      every node consumes exactly its own tokens,
               so the iterator is always at the right place
```
हिंदी: `#` markers से tree का shape पक्का हो जाता है, इसलिए सिर्फ preorder से भी unique tree वापस मिलता है।

---

## 📊 Complexity
```
Brute (string +): Time O(n^2) worst | Space O(n)
Preorder + join:  Time O(n)         | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: level-order (BFS) format, same as LeetCode's own display
class CodecBFS:
    def serialize(self, root: Optional[TreeNode]) -> str:
        if root is None:                     # empty tree
            return ""                        # empty string
        out: list[str] = []                  # tokens
        q = deque([root])                    # BFS queue
        while q:                             # until queue empty
            node = q.popleft()               # next node
            if node is None:                 # missing child
                out.append("#")              # marker
                continue                     # nothing to expand
            out.append(str(node.val))        # write value
            q.append(node.left)              # queue left (maybe None)
            q.append(node.right)             # queue right (maybe None)
        return ",".join(out)                 # join tokens

    def deserialize(self, data: str) -> Optional[TreeNode]:
        if not data:                         # empty string -> empty tree
            return None                      # no nodes
        vals = data.split(",")               # tokens
        root = TreeNode(int(vals[0]))        # first token is root
        q = deque([root])                    # parents waiting for children
        i = 1                                # next token index
        while q:                             # while parents remain
            node = q.popleft()               # next parent
            if vals[i] != "#":               # left child present
                node.left = TreeNode(int(vals[i]))  # create it
                q.append(node.left)          # queue it
            i += 1                           # advance token
            if vals[i] != "#":               # right child present
                node.right = TreeNode(int(vals[i]))  # create it
                q.append(node.right)         # queue it
            i += 1                           # advance token
        return root                          # rebuilt tree


bfs = CodecBFS()                             # BFS codec instance
print(bfs.serialize(t))                      # Expected: 1,2,3,#,#,4,5,#,#,#,#
print(same(bfs.deserialize(bfs.serialize(t)), t))  # Expected: True

# VARIANT 1: Serialize/Deserialize a BST -> preorder only, no markers (use value bounds)
# VARIANT 2: Serialize an N-ary tree -> store child count after each value
# VARIANT 3: Use JSON (json.dumps of nested dicts) -> simple but heavier
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: preorder WITHOUT null markers -> "1,2,3" fits many different trees
# ❌ Wrong: values containing the delimiter, or '#'-vs-negative confusion if you use '-' as a marker

# ✅ Correct: write a marker for every None child, split on a delimiter,
#            and consume tokens through one shared iterator
```

---

## 🎯 Interview Tip
Say: "Preorder with null markers is unambiguous, and a shared iterator makes deserialize a mirror image of serialize." Mention BFS as the alternative; ask whether values can be arbitrary strings.

---

## 🔗 Related Problems
→ D062 (Kth Smallest in BST) | D056 (Validate BST) | D060 (Diameter of Binary Tree)
