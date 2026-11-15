---

# D067. Rotting Oranges
# Category: DSA — Graphs
# Difficulty: ⭐⭐ Medium | LeetCode #994

---

## ❓ Problem
Grid cells: `0` empty, `1` fresh orange, `2` rotten orange. Every minute, fresh oranges 4-directionally adjacent to a rotten one become rotten. Return the minutes until no fresh orange remains, or `-1` if impossible.

```
Input:  [[2,1,1],[1,1,0],[0,1,1]]   Output: 4
Input:  [[2,1,1],[0,1,1],[1,0,1]]   Output: -1  (bottom-left orange is isolated)
```

---

## 💡 Quick Concept (2 lines only)
Multi-source BFS: push ALL rotten oranges into the queue at time 0 and expand level by level. Each BFS level is one minute.
हिंदी: सारे सड़े संतरे एक साथ queue में डालो और level-by-level BFS चलाओ; हर level = 1 मिनट।

---

## ✅ Solution

```python
from collections import deque                # queue for BFS


# ============================================
# APPROACH 1: Brute force — simulate minute by minute, scanning the whole grid each time
# O(R*C*T) time where T = minutes (up to R*C)
# ============================================
def oranges_rotting_brute(grid: list[list[int]]) -> int:
    g = [row[:] for row in grid]             # copy grid
    rows, cols = len(g), len(g[0])           # dimensions
    minutes = 0                              # elapsed time
    while True:                              # simulate rounds
        to_rot = []                          # fresh cells that rot this minute
        for r in range(rows):                # scan rows
            for c in range(cols):            # scan columns
                if g[r][c] == 1:             # fresh orange
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):   # neighbours
                        nr, nc = r + dr, c + dc   # neighbour cell
                        if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 2:  # touches rotten
                            to_rot.append((r, c))   # will rot
                            break            # one rotten neighbour is enough
        if not to_rot:                       # nothing changed
            break                            # simulation over
        for r, c in to_rot:                  # apply all changes together
            g[r][c] = 2                      # becomes rotten
        minutes += 1                         # one minute passed
    fresh_left = any(1 in row for row in g)  # any fresh remaining?
    return -1 if fresh_left else minutes     # impossible or time


# ============================================
# APPROACH 2: Multi-source BFS ✅ PREFERRED
# O(R*C) time, O(R*C) space
# ============================================
def oranges_rotting(grid: list[list[int]]) -> int:
    g = [row[:] for row in grid]             # copy so the input is untouched
    rows, cols = len(g), len(g[0])           # dimensions
    q: deque[tuple[int, int]] = deque()      # all rotten oranges, time 0
    fresh = 0                                # count of fresh oranges
    for r in range(rows):                    # scan rows
        for c in range(cols):                # scan columns
            if g[r][c] == 2:                 # rotten
                q.append((r, c))             # BFS source
            elif g[r][c] == 1:               # fresh
                fresh += 1                   # count it
    minutes = 0                              # elapsed minutes
    while q and fresh:                       # stop early when nothing fresh is left
        for _ in range(len(q)):              # process exactly one level = one minute
            r, c = q.popleft()               # rotten cell
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):   # neighbours
                nr, nc = r + dr, c + dc      # neighbour coords
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:   # fresh neighbour
                    g[nr][nc] = 2            # rots now
                    fresh -= 1               # one less fresh
                    q.append((nr, nc))       # spreads next minute
        minutes += 1                         # level finished
    return -1 if fresh else minutes          # leftovers => unreachable


# ============================================
# TEST CASES
# ============================================
a = [[2, 1, 1], [1, 1, 0], [0, 1, 1]]        # reachable
b = [[2, 1, 1], [0, 1, 1], [1, 0, 1]]        # isolated orange
print(oranges_rotting_brute(a))              # Expected: 4
print(oranges_rotting(a))                    # Expected: 4
print(oranges_rotting(b))                    # Expected: -1
print(oranges_rotting([[0, 2]]))             # Expected: 0
print(oranges_rotting([[0]]))                # Expected: 0
print(oranges_rotting([[1]]))                # Expected: -1
```

---

## 🔍 Why It Works
```
t=0: 2 1 1     t=1: 2 2 1     t=2: 2 2 2   ... t=4 last orange (2,2) rots
     1 1 0          2 1 0          2 2 0
     0 1 1          0 1 1          0 1 1
```
हिंदी: सारे sources एक साथ फैलते हैं, इसलिए BFS का level number ही मिनटों की संख्या है।

---

## 📊 Complexity
```
Brute simulation: Time O(R*C*T) | Space O(R*C)
Multi-source BFS: Time O(R*C)   | Space O(R*C) ← preferred
```

---

## ⚡ Variations

```python
# Alternative: store the minute with each cell instead of counting levels
def oranges_rotting_timed(grid: list[list[int]]) -> int:
    g = [row[:] for row in grid]             # copy grid
    rows, cols = len(g), len(g[0])           # dimensions
    q = deque((r, c, 0) for r in range(rows) for c in range(cols) if g[r][c] == 2)   # (r, c, minute)
    fresh = sum(row.count(1) for row in g)   # fresh count
    last = 0                                 # time of last infection
    while q:                                 # BFS
        r, c, t = q.popleft()                # current cell and its minute
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):   # neighbours
            nr, nc = r + dr, c + dc          # neighbour
            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == 1:   # fresh
                g[nr][nc] = 2                # rot it
                fresh -= 1                   # update count
                last = t + 1                 # latest minute so far
                q.append((nr, nc, t + 1))    # spread next minute
    return -1 if fresh else last             # result


print(oranges_rotting_timed(a))              # Expected: 4

# VARIANT 1: 01 Matrix (LeetCode 542) -> multi-source BFS from all zeros
# VARIANT 2: Walls and Gates -> multi-source BFS from gates
# VARIANT 3: Count fresh oranges that survive -> return `fresh` instead of -1
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: BFS from one rotten orange at a time -> sums times instead of taking parallel spread
# ❌ Wrong: incrementing minutes per popped cell (not per level) -> huge answer
# ❌ Wrong: returning `minutes` when fresh > 0 -> should be -1

# ✅ Correct: seed the queue with every rotten orange, count levels, then check fresh == 0
```

---

## 🎯 Interview Tip
Say: "All rotten oranges spread simultaneously, so this is multi-source BFS and the number of BFS levels is the answer; leftover fresh oranges mean -1."

---

## 🔗 Related Problems
→ D064 (Number of Islands) | D070 (Shortest Path in Binary Matrix) | D068 (Word Ladder)
