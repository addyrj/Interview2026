---

# Q005. List Multiplication Aliasing ([[0]]*3) Output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will the following code print?

```python
grid = [[0]] * 3
grid[0][0] = 9
print(grid)

grid2 = [[0] for _ in range(3)]
grid2[0][0] = 9
print(grid2)
```

---

## 💡 Quick Concept (2 lines only)
`[x] * n` repeats the SAME reference n times — it does not copy `x`. For mutable `x`, every slot points to one shared object.
हिंदी: `[[0]]*3` में तीनों जगह एक ही inner list है, copy नहीं बनती।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
# Step 1: multiplication copies references, not objects
grid = [[0]] * 3                        # outer list holds 3 references to ONE inner list
print(grid[0] is grid[1])               # Expected: True  (same object)
grid[0][0] = 9                          # mutate through row 0 -> affects the shared inner list
print(grid)                             # Expected: [[9], [9], [9]]

# Step 2: a comprehension runs [0] three times -> three separate lists
grid2 = [[0] for _ in range(3)]         # each iteration creates a fresh inner list
grid2[0][0] = 9                         # mutate only row 0
print(grid2)                            # Expected: [[9], [0], [0]]
```

---

## 🔍 Why This Works (3 lines max)
`*` on a list builds a new outer list whose elements are the same object repeated. `[0]` in the comprehension is evaluated on every iteration, producing independent lists. Ints inside are immutable, so `[0] * 3` is safe; nested lists are not.
हिंदी: हर row अलग चाहिए तो comprehension use करो, `*` नहीं।

---

## ⚡ Alternative Solution
```python
# Build a 2x3 matrix correctly, or show the bug with a wider row
rows, cols = 2, 3                       # matrix dimensions
safe = [[0] * cols for _ in range(rows)]  # inner [0]*cols is fine (ints), outer is a comprehension
safe[0].append(5)                       # grow only the first row
print(safe)                             # Expected: [[0, 0, 0, 5], [0, 0, 0]]

bad = [[0] * cols] * rows               # outer multiplication aliases the row
bad[0].append(5)                        # grows the shared row
print(bad)                              # Expected: [[0, 0, 0, 5], [0, 0, 0, 5]]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: creating a 2D grid / board with multiplication on the outer list
# board = [[None] * 3] * 3      # changing board[0][0] changes all rows

# ✅ Correct: comprehension on the outer dimension
# board = [[None] * 3 for _ in range(3)]
```

---

## 🎯 Interview Tip (1 line)
Say: "`*` copies references, not objects — safe for immutables, a trap for nested lists; use a comprehension for 2D grids."

---

## 🔗 Related Questions
→ Q006 (shallow vs deep copy) | Q001 (mutable default) | Q176 (copy semantics) | Q304 (pass by object reference)
