---

# D066. Course Schedule (topological sort)
# Category: DSA — Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #207

---

## ❓ Problem
There are `numCourses` courses labelled `0..n-1`. `prerequisites[i] = [a, b]` means you must take `b` before `a`. Return `True` if you can finish all courses (i.e. the directed graph has no cycle).

```
Input:  numCourses = 2, prerequisites = [[1,0]]        Output: True
Input:  numCourses = 2, prerequisites = [[1,0],[0,1]]  Output: False
```

---

## 💡 Quick Concept (2 lines only)
Model courses as a directed graph (b -> a). It is schedulable iff there is no cycle. Kahn's algorithm: repeatedly remove nodes with in-degree 0; if you remove all of them, no cycle.
हिंदी: Graph में cycle न हो तो सारे courses हो सकते हैं; in-degree 0 वाले हटाते जाओ, सब हट गए तो ठीक।

---

## ✅ Solution

```python
from collections import deque, defaultdict   # queue + adjacency dict


# ============================================
# APPROACH 1: Brute force — DFS from every node, tracking the current path
# O(V*(V+E)) worst case (no global "done" memo)
# ============================================
def can_finish_brute(n: int, prereqs: list[list[int]]) -> bool:
    graph = defaultdict(list)                # b -> [a, ...]
    for a, b in prereqs:                     # build edges
        graph[b].append(a)                   # b must come before a

    def has_cycle(node: int, path: set[int]) -> bool:   # does a cycle pass through node?
        if node in path:                     # revisited a node on current path
            return True                      # cycle found
        path.add(node)                       # enter node
        for nxt in graph[node]:              # follow edges
            if has_cycle(nxt, path):         # cycle deeper down
                return True                  # propagate
        path.remove(node)                    # leave node (backtrack)
        return False                         # no cycle from here

    return not any(has_cycle(i, set()) for i in range(n))   # no start node leads to a cycle


# ============================================
# APPROACH 2: Kahn's algorithm (BFS topological sort) ✅ PREFERRED
# O(V+E) time, O(V+E) space
# ============================================
def can_finish(n: int, prereqs: list[list[int]]) -> bool:
    graph: list[list[int]] = [[] for _ in range(n)]   # adjacency list
    indeg = [0] * n                          # prerequisites remaining per course
    for a, b in prereqs:                     # each rule
        graph[b].append(a)                   # edge b -> a
        indeg[a] += 1                        # a has one more prerequisite
    q = deque(i for i in range(n) if indeg[i] == 0)   # courses with no prerequisites
    taken = 0                                # courses finished
    while q:                                 # while something can be taken
        cur = q.popleft()                    # take it
        taken += 1                           # count it
        for nxt in graph[cur]:               # courses unlocked by cur
            indeg[nxt] -= 1                  # one prerequisite satisfied
            if indeg[nxt] == 0:              # all satisfied now
                q.append(nxt)                # can take it
    return taken == n                        # all taken <=> no cycle


def find_order(n: int, prereqs: list[list[int]]) -> list[int]:   # same idea, returns an order
    graph: list[list[int]] = [[] for _ in range(n)]   # adjacency list
    indeg = [0] * n                          # in-degrees
    for a, b in prereqs:                     # build graph
        graph[b].append(a)                   # edge b -> a
        indeg[a] += 1                        # count prerequisite
    q = deque(i for i in range(n) if indeg[i] == 0)   # start nodes
    order: list[int] = []                    # result order
    while q:                                 # process queue
        cur = q.popleft()                    # next course
        order.append(cur)                    # record it
        for nxt in graph[cur]:               # unlock neighbours
            indeg[nxt] -= 1                  # reduce in-degree
            if indeg[nxt] == 0:              # ready
                q.append(nxt)                # enqueue
    return order if len(order) == n else []  # empty list if impossible


# ============================================
# TEST CASES
# ============================================
print(can_finish_brute(2, [[1, 0]]))         # Expected: True
print(can_finish(2, [[1, 0]]))               # Expected: True
print(can_finish(2, [[1, 0], [0, 1]]))       # Expected: False
print(can_finish(4, [[1, 0], [2, 1], [3, 2], [1, 3]]))   # Expected: False  (cycle 1->2->3->1)
print(can_finish(3, []))                     # Expected: True
print(find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]]))   # Expected: [0, 1, 2, 3]
print(find_order(2, [[1, 0], [0, 1]]))       # Expected: []
```

---

## 🔍 Why It Works
```
0 -> 1 -> 3        indeg: 0:0 1:1 2:1 3:2
0 -> 2 -> 3        take 0 -> 1,2 become 0 -> take them -> 3 becomes 0 -> take 3
```
हिंदी: Cycle के nodes का in-degree कभी 0 नहीं होता, इसलिए वे queue में आते ही नहीं और taken < n रह जाता है।

---

## 📊 Complexity
```
Brute force DFS: Time O(V*(V+E)) | Space O(V+E)
Kahn's BFS:      Time O(V+E)     | Space O(V+E) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: DFS with 3 colors (0 = new, 1 = in progress, 2 = done)
def can_finish_dfs(n: int, prereqs: list[list[int]]) -> bool:
    graph: list[list[int]] = [[] for _ in range(n)]   # adjacency list
    for a, b in prereqs:                     # build edges
        graph[b].append(a)                   # b -> a
    state = [0] * n                          # colour per node

    def dfs(u: int) -> bool:                 # True if a cycle is found
        if state[u] == 1:                    # back edge to node in progress
            return True                      # cycle
        if state[u] == 2:                    # already fully explored
            return False                     # safe
        state[u] = 1                         # mark in progress
        if any(dfs(v) for v in graph[u]):    # any neighbour closes a cycle
            return True                      # propagate
        state[u] = 2                         # mark done
        return False                         # no cycle here

    return not any(dfs(i) for i in range(n))   # check every component


print(can_finish_dfs(2, [[1, 0], [0, 1]]))   # Expected: False
print(can_finish_dfs(4, [[1, 0], [2, 0], [3, 1], [3, 2]]))   # Expected: True

# VARIANT 1: Course Schedule II -> return the order (find_order above)
# VARIANT 2: Alien Dictionary -> topological sort on letter precedence
# VARIANT 3: Parallel courses -> longest path (levels) in the DAG
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: edge direction reversed (a -> b) -> in-degrees count the wrong thing, wrong order
# ❌ Wrong: DFS with only a visited set -> reports false cycles on diamonds (0->1,0->2,1->3,2->3)

# ✅ Correct: Kahn with in-degrees, or DFS with 3 states (new / in-progress / done)
```

---

## 🎯 Interview Tip
Say: "It's cycle detection in a directed graph. I'll use Kahn's algorithm: if I can pop all n nodes, there's no cycle. O(V+E)." Be ready to code the DFS 3-colour version too.

---

## 🔗 Related Problems
→ D065 (Clone Graph) | D069 (Graph Valid Tree) | D071 (Dijkstra's Algorithm)
