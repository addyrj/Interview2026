---

# D065. Clone Graph
# Category: DSA — Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #133

---

## ❓ Problem
Given a node in a connected undirected graph, return a deep copy of the graph. Each node has a value and a list of neighbors.

```
Input:  adjacency list [[2,4],[1,3],[2,4],[1,3]]  (node i has value i)
Output: a new graph with the same structure, no shared node objects
```

---

## 💡 Quick Concept (2 lines only)
Traverse the graph and keep a dict `old node -> new node`. Create the copy the first time you see a node, and reuse it afterwards so cycles do not loop forever.
हिंदी: Dict में old→new node रखो; पहली बार दिखे तो copy बनाओ, दोबारा दिखे तो वही copy लौटा दो (cycle से बचाव)।

---

## ✅ Solution

```python
from __future__ import annotations           # allow forward type hints
from collections import deque                # queue for BFS
from typing import Optional                  # Optional type hint


class Node:                                  # graph node (given in interview)
    def __init__(self, val: int = 0, neighbors: Optional[list[Node]] = None):
        self.val = val                       # node value
        self.neighbors = neighbors if neighbors is not None else []  # adjacent nodes


def build_graph(adj: list[list[int]]) -> Optional[Node]:   # helper: adjacency list (1-indexed) -> node 1
    if not adj:                              # empty graph
        return None                          # no node
    nodes = [Node(i + 1) for i in range(len(adj))]   # create all nodes
    for i, nbrs in enumerate(adj):           # wire up edges
        nodes[i].neighbors = [nodes[j - 1] for j in nbrs]   # neighbours by value
    return nodes[0]                          # entry node


def to_adj(start: Optional[Node]) -> list[list[int]]:      # helper: graph -> adjacency list
    if start is None:                        # empty graph
        return []                            # nothing
    seen = {start.val: start}                # discovered nodes by value
    q = deque([start])                       # BFS queue
    while q:                                 # explore
        n = q.popleft()                      # current node
        for m in n.neighbors:                # each neighbour
            if m.val not in seen:            # new node
                seen[m.val] = m              # remember it
                q.append(m)                  # visit later
    return [[m.val for m in seen[v].neighbors] for v in sorted(seen)]  # ordered adjacency


# ============================================
# APPROACH 1: Brute force — use copy.deepcopy (works, but hides the algorithm)
# O(V+E) time, but recursion depth can hit the limit on long chains
# ============================================
import copy                                  # stdlib deep copy


def clone_brute(node: Optional[Node]) -> Optional[Node]:
    return copy.deepcopy(node)               # deepcopy handles cycles via its memo dict


# ============================================
# APPROACH 2: BFS with old->new map ✅ PREFERRED
# O(V+E) time, O(V) space
# ============================================
def clone_graph(node: Optional[Node]) -> Optional[Node]:
    if node is None:                         # empty graph
        return None                          # nothing to clone
    copies = {node: Node(node.val)}          # old node -> its copy
    q = deque([node])                        # BFS queue of OLD nodes
    while q:                                 # until all reachable nodes done
        cur = q.popleft()                    # current old node
        for nb in cur.neighbors:             # each old neighbour
            if nb not in copies:             # first time we see it
                copies[nb] = Node(nb.val)    # create its copy
                q.append(nb)                 # expand it later
            copies[cur].neighbors.append(copies[nb])   # link copy to neighbour's copy
    return copies[node]                      # copy of the entry node


# ============================================
# TEST CASES
# ============================================
adj = [[2, 4], [1, 3], [2, 4], [1, 3]]       # 4-cycle
g = build_graph(adj)                         # original
c = clone_graph(g)                           # clone
print(to_adj(c))                             # Expected: [[2, 4], [1, 3], [2, 4], [1, 3]]
print(c is not g and c.neighbors[0] is not g.neighbors[0])   # Expected: True  (new objects)
print(to_adj(clone_brute(g)))                # Expected: [[2, 4], [1, 3], [2, 4], [1, 3]]
print(to_adj(clone_graph(build_graph([[]]))))   # Expected: [[]]  (single node)
print(clone_graph(None))                     # Expected: None
```

---

## 🔍 Why It Works
```
1 -- 2        copies: {1:1', 2:2', 3:3', 4:4'}
|    |        visiting 1: make 2',4', link 1'->2', 1'->4'
4 -- 3        visiting 2: 1 already copied -> reuse 1', link 2'->1' ...
```
हिंदी: Dict ही visited set भी है और copy का नक्शा भी; इसलिए हर node बिल्कुल एक बार copy होता है।

---

## 📊 Complexity
```
deepcopy:  Time O(V+E) | Space O(V) (recursive, can hit recursion limit)
BFS + map: Time O(V+E) | Space O(V) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: recursive DFS with a memo dict
def clone_dfs(node: Optional[Node], memo: Optional[dict] = None) -> Optional[Node]:
    if node is None:                         # empty graph
        return None                          # nothing
    memo = {} if memo is None else memo      # create memo on first call
    if node in memo:                         # already cloned
        return memo[node]                    # reuse
    memo[node] = new = Node(node.val)        # register BEFORE recursing (breaks cycles)
    new.neighbors = [clone_dfs(n, memo) for n in node.neighbors]   # clone neighbours
    return new                               # finished copy


print(to_adj(clone_dfs(g)))                  # Expected: [[2, 4], [1, 3], [2, 4], [1, 3]]

# VARIANT 1: Copy list with random pointer (LeetCode 138) -> same old->new map idea
# VARIANT 2: Clone a directed graph -> identical code
# VARIANT 3: Clone a binary tree/N-ary tree -> no map needed (no cycles)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no visited map -> infinite recursion on cycles
#   def clone(n): c = Node(n.val); c.neighbors = [clone(x) for x in n.neighbors]; return c

# ❌ Wrong: registering the copy AFTER recursing into neighbours -> cycle again

# ✅ Correct: put the new node in the dict first, then process neighbours
```

---

## 🎯 Interview Tip
Say: "The map from original to copy doubles as my visited set, so each node and edge is handled once: O(V+E)." Clarify that nodes are unique per value and the graph is connected.

---

## 🔗 Related Problems
→ D064 (Number of Islands) | D066 (Course Schedule) | D069 (Graph Valid Tree)
