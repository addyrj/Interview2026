---

# D064. Number of Islands
# Category: DSA — Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #200

---

## ❓ Problem
Given a 2D grid of `"1"` (land) and `"0"` (water), count the islands. An island is land connected horizontally or vertically.

```
Input:  grid = [["1","1","0"],
                ["1","0","0"],
                ["0","0","1"]]
Output: 2
```

---

## 💡 Quick Concept (2 lines only)
Scan every cell; when you find unvisited land, count one island and flood-fill (DFS/BFS) all connected land so it is never counted again.
हिंदी: हर cell देखो; land मिले तो island +1 करो और उससे जुड़ी सारी land को visited कर दो।

---

## ✅ Solution

```python
from collections import deque                # queue for BFS


# ============================================
# APPROACH 1: Brute force — copy the grid and use a separate visited set of tuples
# O(R*C) time, extra O(R*C) space (grid copy + visited set)
# ============================================
def num_islands_brute(grid: list[list[str]]) -> int:
    rows, cols = len(grid), len(grid[0]) if grid else 0   # grid size
    seen: set[tuple[int, int]] = set()       # visited cells
    count = 0                                # islands found

    def dfs(r: int, c: int) -> None:         # recursive flood fill
        if not (0 <= r < rows and 0 <= c < cols):   # out of bounds
            return                           # stop
        if grid[r][c] != "1" or (r, c) in seen:     # water or already seen
            return                           # stop
        seen.add((r, c))                     # mark visited
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # four directions
            dfs(r + dr, c + dc)              # visit neighbour

    for r in range(rows):                    # every row
        for c in range(cols):                # every column
            if grid[r][c] == "1" and (r, c) not in seen:   # new island start
                count += 1                   # count it
                dfs(r, c)                    # mark whole island
    return count                             # total islands


# ============================================
# APPROACH 2: Iterative BFS, sink land in place ✅ PREFERRED
# O(R*C) time, O(min(R,C)) queue space, no recursion limit issue
# ============================================
def num_islands(grid: list[list[str]]) -> int:
    if not grid:                             # empty grid
        return 0                             # no islands
    g = [row[:] for row in grid]             # copy so we do not mutate the caller's data
    rows, cols = len(g), len(g[0])           # dimensions
    count = 0                                # islands found
    for r in range(rows):                    # scan rows
        for c in range(cols):                # scan columns
            if g[r][c] != "1":               # water or already sunk
                continue                     # skip
            count += 1                       # new island
            g[r][c] = "0"                    # sink starting cell
            q = deque([(r, c)])              # BFS queue
            while q:                         # until island exhausted
                x, y = q.popleft()           # current land cell
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # neighbours
                    nx, ny = x + dx, y + dy  # neighbour coords
                    if 0 <= nx < rows and 0 <= ny < cols and g[nx][ny] == "1":  # unvisited land
                        g[nx][ny] = "0"      # sink when enqueued (prevents duplicates)
                        q.append((nx, ny))   # explore later
    return count                             # total islands


# ============================================
# TEST CASES
# ============================================
a = [list("110"), list("100"), list("001")]                      # 2 islands
b = [list("11000"), list("11000"), list("00100"), list("00011")]  # 3 islands
print(num_islands_brute(a))                  # Expected: 2
print(num_islands(a))                        # Expected: 2
print(num_islands(b))                        # Expected: 3
print(num_islands([list("000")]))            # Expected: 0
print(num_islands([]))                       # Expected: 0
print(a[0])                                  # Expected: ['1', '1', '0']  (input untouched)
```

---

## 🔍 Why It Works
```
1 1 0
1 0 0     scan finds (0,0) -> count=1, flood sinks (0,0),(0,1),(1,0)
0 0 1     scan finds (2,2) -> count=2
```
हिंदी: हर island का flood fill एक ही बार चलता है, इसलिए हर cell ज़्यादा से ज़्यादा एक बार visit होता है।

---

## 📊 Complexity
```
Brute (visited set): Time O(R*C) | Space O(R*C)
BFS sink in place:   Time O(R*C) | Space O(min(R,C)) queue ← preferred
```

---

## ⚡ Variations

```python
# Alternative: Union-Find — useful when land is added over time (Number of Islands II)
def num_islands_uf(grid: list[list[str]]) -> int:
    if not grid:                             # empty grid
        return 0                             # nothing
    rows, cols = len(grid), len(grid[0])     # dimensions
    parent = list(range(rows * cols))        # each cell is its own root
    comps = sum(ch == "1" for row in grid for ch in row)   # start: every land cell separate

    def find(x: int) -> int:                 # root with path compression
        while parent[x] != x:                # climb to root
            parent[x] = parent[parent[x]]    # halve the path
            x = parent[x]                    # move up
        return x                             # root id

    for r in range(rows):                    # each cell
        for c in range(cols):                # each column
            if grid[r][c] != "1":            # skip water
                continue                     # nothing to union
            for dr, dc in ((1, 0), (0, 1)):  # only look down and right
                nr, nc = r + dr, c + dc      # neighbour
                if nr < rows and nc < cols and grid[nr][nc] == "1":  # neighbour is land
                    a_, b_ = find(r * cols + c), find(nr * cols + nc)  # roots
                    if a_ != b_:             # different components
                        parent[a_] = b_      # merge
                        comps -= 1           # one fewer island
    return comps                             # remaining components


print(num_islands_uf(b))                     # Expected: 3

# VARIANT 1: Max area of island (LeetCode 695) -> return the largest flood-fill size
# VARIANT 2: 8-directional islands -> add the four diagonals
# VARIANT 3: Number of Islands II (add land online) -> Union-Find
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: marking visited only when popped from the queue -> same cell enqueued many times
# ❌ Wrong: grid[r][c] == 1 (int) when cells are the strings "1"
# ❌ Wrong: recursive DFS on a 300x300 grid -> RecursionError (default limit ~1000)

# ✅ Correct: mark visited when enqueued, compare to "1", prefer iterative traversal
```

---

## 🎯 Interview Tip
Say: "Each land cell is visited once, so O(R*C). I'll mutate the grid to avoid a visited set — and ask if mutating the input is allowed, otherwise I copy." Mention Union-Find for the streaming follow-up.

---

## 🔗 Related Problems
→ D065 (Clone Graph) | D067 (Rotting Oranges) | D070 (Shortest Path in Binary Matrix)
