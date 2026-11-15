---

# D071. Dijkstra's Algorithm
# Category: DSA — Graphs
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Problem
Given a weighted directed graph with non-negative edge weights and a source node, return the shortest distance from the source to every node (`inf` if unreachable).

```
Input:  n = 5, edges = [(0,1,4),(0,2,1),(2,1,2),(1,3,1),(2,3,5)], src = 0
Output: [0, 3, 1, 4, inf]
```

---

## 💡 Quick Concept (2 lines only)
Keep a min-heap of `(distance, node)`. Always pop the closest unfinalized node and relax its outgoing edges; skip stale heap entries. Works only when no edge weight is negative.
हिंदी: Min-heap से सबसे नज़दीकी node निकालो और उसके neighbours की distance घटाओ (relax); negative weights पर काम नहीं करता।

---

## ✅ Solution

```python
import heapq                                  # priority queue
from collections import defaultdict           # adjacency list

INF = float("inf")                            # "unreachable" marker

def build_graph(edges: list[tuple[int, int, int]]) -> dict[int, list[tuple[int, int]]]:
    graph: dict[int, list[tuple[int, int]]] = defaultdict(list)  # node -> [(next, weight)]
    for u, v, w in edges:                     # each directed edge
        graph[u].append((v, w))               # store neighbour with weight
    return graph                              # adjacency list

# ============================================
# APPROACH 1: Brute force — Bellman-Ford style: relax all edges n-1 times
# O(n * e) time, O(n) space (also handles negative weights)
# ============================================
def dijkstra_brute(n: int, edges: list[tuple[int, int, int]], src: int) -> list[float]:
    dist: list[float] = [INF] * n             # distances start at infinity
    dist[src] = 0                             # source is distance 0
    for _ in range(n - 1):                    # at most n-1 rounds needed
        for u, v, w in edges:                 # relax every edge
            if dist[u] + w < dist[v]:         # shorter path via u?
                dist[v] = dist[u] + w         # update distance
    return dist                               # final distances

# ============================================
# APPROACH 2: Min-heap Dijkstra — O((n + e) log n) time, O(n + e) space ✅ PREFERRED
# ============================================
def dijkstra(n: int, edges: list[tuple[int, int, int]], src: int) -> list[float]:
    graph = build_graph(edges)                # adjacency list
    dist: list[float] = [INF] * n             # best known distance per node
    dist[src] = 0                             # source distance is 0
    heap: list[tuple[float, int]] = [(0, src)]  # (distance, node)
    while heap:                               # while candidates remain
        d, u = heapq.heappop(heap)            # closest unprocessed node
        if d > dist[u]:                       # stale entry, a better one was already used
            continue                          # skip it
        for v, w in graph[u]:                 # relax outgoing edges
            nd = d + w                        # distance through u
            if nd < dist[v]:                  # improves v?
                dist[v] = nd                  # record better distance
                heapq.heappush(heap, (nd, v)) # push new candidate
    return dist                               # shortest distances

# ============================================
# TEST CASES
# ============================================
E = [(0,1,4),(0,2,1),(2,1,2),(1,3,1),(2,3,5)]  # sample edges
print(dijkstra_brute(5, E, 0))                              # [0, 3, 1, 4, inf]
print(dijkstra(5, E, 0))                                    # [0, 3, 1, 4, inf]
print(dijkstra(1, [], 0))                                   # [0]
print(dijkstra(3, [(0,1,5)], 0))                            # [0, 5, inf]
print(dijkstra(4, [(0,1,1),(1,2,1),(0,2,5),(2,3,1)], 0))    # [0, 1, 2, 3]
print(dijkstra(4, [(0,1,1),(1,2,1),(0,2,5),(2,3,1)], 2))    # [inf, inf, 0, 1]
```

---

## 🔍 Why It Works
```
heap: (0,0)            pop 0 -> dist[1]=4, dist[2]=1
heap: (1,2),(4,1)      pop 2 -> dist[1]=3 (1+2), dist[3]=6
heap: (3,1),(4,1)*,(6,3)  pop 1 -> dist[3]=4
(4,1)* is stale: 4 > dist[1]=3 -> skipped
```
With non-negative weights, the first time a node is popped its distance can never improve.
हिंदी: Non-negative weights में node पहली बार pop होते ही उसकी distance final होती है; पुरानी entries skip करो।

---

## 📊 Complexity
```
Bellman-Ford: Time O(n·e)          | Space O(n)
Heap Dijkstra: Time O((n+e) log n) | Space O(n + e) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Network Delay Time (LeetCode #743) — max of dijkstra distances, -1 if any inf
def network_delay(times: list[list[int]], n: int, k: int) -> int:
    edges = [(u - 1, v - 1, w) for u, v, w in times]  # convert to 0-indexed edges
    dist = dijkstra(n, edges, k - 1)                  # shortest distances
    worst = max(dist)                                 # farthest node
    return -1 if worst == INF else int(worst)         # unreachable => -1

print(network_delay([[2,1,1],[2,3,1],[3,4,1]], 4, 2)) # 2
# VARIANT 2: Return the actual path — keep a parent[] array updated on every relaxation
# VARIANT 3: Negative edges -> use Bellman-Ford; unweighted -> plain BFS (D070)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: no stale check -> still correct but re-processes nodes, can degrade to O(n·e)
# ❌ Wrong: using Dijkstra with negative edges -> a finalized node may later improve
# ❌ Wrong: pushing (node, dist) -> heap orders by node, not distance
# ✅ Correct: heap items are (distance, node) and skip when d > dist[node]
```

---

## 🎯 Interview Tip
Say: "Greedy by smallest distance using a min-heap; lazy deletion skips stale entries; it needs non-negative weights, otherwise Bellman-Ford." Know the O((V+E) log V) bound.

---

## 🔗 Related Problems
→ D070 (Shortest Path in Binary Matrix) | D068 (Word Ladder) | D066 (Course Schedule)
