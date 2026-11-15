---

# D070. Shortest Path in Binary Matrix
# Category: DSA — Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #1091

---

## ❓ Problem
Given an `n x n` binary grid, return the length of the shortest clear path from the top-left `(0,0)` to the bottom-right `(n-1,n-1)`. A clear path only visits cells with value `0` and moves in 8 directions. Length counts cells visited. Return `-1` if no path exists.

```
Input:  grid = [[0,1],[1,0]]            -> 2
Input:  grid = [[0,0,0],[1,1,0],[1,1,0]] -> 4
Input:  grid = [[1,0,0],[1,1,0],[1,1,0]] -> -1  (start blocked)
```

---

## 💡 Quick Concept (2 lines only)
All moves cost 1, so BFS from the start finds the shortest path the first time it reaches the target. Mark cells visited when you enqueue them to avoid duplicates.
हिंदी: Unweighted grid में shortest path = BFS; पहली बार target मिले तो वही answer है।

---

## ✅ Solution

```python
from collections import deque  # O(1) pops from the left for BFS

DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]  # 8 neighbours

# ============================================
# APPROACH 1: Brute force — DFS over all paths, keep the minimum
# Exponential time in the worst case (only fine for tiny grids)
# ============================================
def shortest_path_dfs(grid: list[list[int]]) -> int:
    n = len(grid)                                    # grid size
    if grid[0][0] or grid[n-1][n-1]:                 # blocked start or end
        return -1                                    # impossible
    best = float("inf")                              # best length found so far
    on_path: set[tuple[int, int]] = set()            # cells in the current path

    def dfs(r: int, c: int, length: int) -> None:
        nonlocal best                                # update outer variable
        if length >= best:                           # prune worse paths
            return                                   # stop exploring
        if (r, c) == (n-1, n-1):                     # reached target
            best = length                            # record better length
            return                                   # done with this branch
        on_path.add((r, c))                          # mark current cell
        for dr, dc in DIRS:                          # try 8 directions
            nr, nc = r + dr, c + dc                  # neighbour cell
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0 and (nr, nc) not in on_path:
                dfs(nr, nc, length + 1)              # go deeper
        on_path.discard((r, c))                      # backtrack

    dfs(0, 0, 1)                                     # start path length is 1
    return -1 if best == float("inf") else int(best) # convert result

# ============================================
# APPROACH 2: BFS — O(n²) time, O(n²) space ✅ PREFERRED
# ============================================
def shortest_path_binary_matrix(grid: list[list[int]]) -> int:
    n = len(grid)                                    # grid size
    if grid[0][0] or grid[n-1][n-1]:                 # start or end blocked
        return -1                                    # no path
    queue = deque([(0, 0, 1)])                       # (row, col, path length)
    grid[0][0] = 1                                   # mark visited in place
    while queue:                                     # until no cells left
        r, c, dist = queue.popleft()                 # next cell in BFS order
        if r == n - 1 and c == n - 1:                # first arrival is shortest
            return dist                              # answer
        for dr, dc in DIRS:                          # explore 8 directions
            nr, nc = r + dr, c + dc                  # neighbour
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                grid[nr][nc] = 1                     # mark when enqueued
                queue.append((nr, nc, dist + 1))     # one more cell on path
    return -1                                        # queue empty, never reached

# ============================================
# TEST CASES
# ============================================
print(shortest_path_binary_matrix([[0,1],[1,0]]))                 # 2
print(shortest_path_binary_matrix([[0,0,0],[1,1,0],[1,1,0]]))     # 4
print(shortest_path_binary_matrix([[1,0,0],[1,1,0],[1,1,0]]))     # -1
print(shortest_path_binary_matrix([[0]]))                         # 1
print(shortest_path_dfs([[0,0,0],[1,1,0],[1,1,0]]))               # 4
print(shortest_path_dfs([[0,1],[1,1]]))                           # -1
```

---

## 🔍 Why It Works
```
grid: 0 0 0      BFS levels:  (0,0) d=1
      1 1 0                   (0,1) d=2
      1 1 0                   (0,2),(1,2) d=3
                              (2,2) d=4  <- first time we hit target
```
BFS explores cells in increasing distance, so the first visit to the target is the minimum.
हिंदी: BFS distance के हिसाब से level-by-level चलता है, इसलिए target पर पहली बार पहुँचना ही shortest है।

---

## 📊 Complexity
```
Brute force (DFS): Time exponential | Space O(n²) — path + recursion
BFS:               Time O(n²)       | Space O(n²) — queue ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Only 4 directions — replace DIRS with [(-1,0),(1,0),(0,-1),(0,1)]
# VARIANT 2: Return the path itself — store a parent map and walk back from the target
# VARIANT 3: Cells have costs -> BFS no longer works, use Dijkstra (D071)
def path_length_4dir(grid: list[list[int]]) -> int:
    n = len(grid)                                    # size
    if grid[0][0] or grid[-1][-1]:                   # blocked ends
        return -1                                    # impossible
    q = deque([(0, 0, 1)])                           # BFS queue
    seen = {(0, 0)}                                  # visited set (no mutation)
    while q:                                         # loop
        r, c, d = q.popleft()                        # next cell
        if (r, c) == (n - 1, n - 1):                 # target
            return d                                 # length
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):   # 4 directions
            nr, nc = r + dr, c + dc                  # neighbour
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0 and (nr, nc) not in seen:
                seen.add((nr, nc))                   # mark visited
                q.append((nr, nc, d + 1))            # enqueue
    return -1                                        # unreachable

print(path_length_4dir([[0,0,0],[1,1,0],[1,1,0]]))   # 5
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: marking visited when dequeuing -> same cell is enqueued many times (slow / TLE)
# ❌ Wrong: forgetting the start/end cell can itself be 1
# ❌ Wrong: returning dist - 1 / counting moves instead of cells (answer counts cells)
# ✅ Correct: check blocked ends first, mark visited on enqueue, start distance at 1
```

---

## 🎯 Interview Tip
Say: "Unit-cost edges, so BFS gives the shortest path; I mark cells visited when pushing so each cell enters the queue once, giving O(n²)." Follow-up: weighted cells -> Dijkstra (D071).

---

## 🔗 Related Problems
→ D067 (Rotting Oranges) | D068 (Word Ladder) | D071 (Dijkstra's Algorithm)
