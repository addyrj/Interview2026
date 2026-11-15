---

# D069. Graph Valid Tree
# Category: DSA — Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #261

---

## ❓ Problem
You have `n` nodes labeled `0..n-1` and a list of undirected `edges`. Return `True` if the edges form a valid tree (connected and no cycles), else `False`.

```
Input:  n = 5, edges = [[0,1],[0,2],[0,3],[1,4]]  -> True
Input:  n = 5, edges = [[0,1],[1,2],[2,3],[1,3],[1,4]] -> False (cycle 1-2-3)
```

---

## 💡 Quick Concept (2 lines only)
A graph is a tree if and only if it has exactly `n - 1` edges AND is connected (so no cycle can exist). Check the edge count first, then prove connectivity with DFS or Union-Find.
हिंदी: Tree = ठीक n-1 edges + सारे nodes connected; edge count गलत हो तो तुरंत False।

---

## ✅ Solution

```python
from collections import defaultdict  # adjacency list with default empty lists

# ============================================
# APPROACH 1: Brute force — DFS cycle detection with parent tracking + connectivity
# O(n + e) time, O(n + e) space
# ============================================
def valid_tree_dfs(n: int, edges: list[list[int]]) -> bool:
    graph: dict[int, list[int]] = defaultdict(list)  # adjacency list
    for a, b in edges:                               # build undirected graph
        graph[a].append(b)                           # a -> b
        graph[b].append(a)                           # b -> a
    seen: set[int] = set()                           # visited nodes

    def has_cycle(node: int, parent: int) -> bool:
        seen.add(node)                               # mark visited
        for nxt in graph[node]:                      # look at neighbours
            if nxt == parent:                        # ignore the edge we came from
                continue                             # skip parent
            if nxt in seen:                          # reached a visited node => cycle
                return True                          # cycle found
            if has_cycle(nxt, node):                 # recurse deeper
                return True                          # propagate cycle
        return False                                 # no cycle from here

    if has_cycle(0, -1):                             # start DFS from node 0
        return False                                 # cycle => not a tree
    return len(seen) == n                            # all nodes reached => connected

# ============================================
# APPROACH 2: Edge count + Union-Find — O(n + e * α(n)) time, O(n) space ✅ PREFERRED
# ============================================
def valid_tree(n: int, edges: list[list[int]]) -> bool:
    if len(edges) != n - 1:                          # tree must have exactly n-1 edges
        return False                                 # quick reject
    parent = list(range(n))                          # each node is its own root

    def find(x: int) -> int:
        while parent[x] != x:                        # climb until root
            parent[x] = parent[parent[x]]            # path halving for speed
            x = parent[x]                            # move up
        return x                                     # root of x

    for a, b in edges:                               # process each edge
        ra, rb = find(a), find(b)                    # roots of both endpoints
        if ra == rb:                                 # already connected => cycle
            return False                             # not a tree
        parent[ra] = rb                              # union the two components
    return True                                      # n-1 edges and no cycle => tree

# ============================================
# TEST CASES
# ============================================
print(valid_tree_dfs(5, [[0,1],[0,2],[0,3],[1,4]]))        # True
print(valid_tree(5, [[0,1],[0,2],[0,3],[1,4]]))            # True
print(valid_tree(5, [[0,1],[1,2],[2,3],[1,3],[1,4]]))      # False
print(valid_tree(4, [[0,1],[2,3]]))                        # False
print(valid_tree(1, []))                                   # True
print(valid_tree_dfs(4, [[0,1],[2,3]]))                    # False
```

---

## 🔍 Why It Works
```
n=4, edges=[[0,1],[2,3]]  -> 2 edges != n-1 (3) -> disconnected -> False
n=5 cycle case            -> edge (1,3): find(1) == find(3) -> already joined -> cycle
```
n-1 edges with no cycle means exactly one component, so connectivity is free.
हिंदी: n-1 edges और cycle नहीं = एक ही component, इसलिए अलग से connectivity check नहीं चाहिए।

---

## 📊 Complexity
```
DFS:        Time O(n + e)      | Space O(n + e) — graph + recursion
Union-Find: Time O(n + e·α(n)) | Space O(n)     ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Number of Connected Components — count unions that succeed
def count_components(n: int, edges: list[list[int]]) -> int:
    parent = list(range(n))                  # each node its own root
    def find(x: int) -> int:
        while parent[x] != x:                # climb to root
            parent[x] = parent[parent[x]]    # path halving
            x = parent[x]                    # move up
        return x                             # root
    comps = n                                # start with n components
    for a, b in edges:                       # each edge
        ra, rb = find(a), find(b)            # roots
        if ra != rb:                         # different components
            parent[ra] = rb                  # merge
            comps -= 1                       # one fewer component
    return comps                             # remaining components

print(count_components(5, [[0,1],[1,2],[3,4]]))  # 2
# VARIANT 2: Redundant Connection — return the first edge where find(a) == find(b)
# VARIANT 3: Directed graph "is it a tree?" — also check every node has in-degree <= 1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: DFS cycle check without parent => every undirected edge looks like a cycle
#    (A -> B, then at B the neighbour A is "already seen")
# ❌ Wrong: only checking "no cycle" and forgetting connectivity
#    n=4, edges=[[0,1],[2,3]] has no cycle but is NOT a tree
# ✅ Correct: len(edges) == n - 1 AND no cycle (or full DFS reach)
```

---

## 🎯 Interview Tip
Say: "A tree has exactly n-1 edges, so I reject on that count first, then Union-Find detects any cycle; with n-1 edges and no cycle the graph is automatically connected." Follow-up: connected components count (variant 1).

---

## 🔗 Related Problems
→ D064 (Number of Islands) | D065 (Clone Graph) | D066 (Course Schedule)
