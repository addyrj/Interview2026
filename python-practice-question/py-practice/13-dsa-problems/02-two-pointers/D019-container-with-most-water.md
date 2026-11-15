---

# D019. Container With Most Water
# Category: DSA — Two Pointers
# Difficulty: ⭐⭐ Medium | LeetCode #11

---

## ❓ Problem
Given `height[i]` as vertical lines at positions `i`, pick two lines that, with the x-axis, form a container holding the most water. Return that maximum area.

```
Input:  height = [1, 8, 6, 2, 5, 4, 8, 3, 7]
Output: 49          # lines at index 1 and 8: min(8,7) * 7
```

---

## 💡 Quick Concept (2 lines only)
Area = `min(h[l], h[r]) * (r - l)`. Start with the widest container and always move the pointer at the shorter line, since moving the taller one can never help.
हिंदी: सबसे चौड़े container से शुरू करो और हमेशा छोटी line वाला pointer हिलाओ, क्योंकि बड़ी line हिलाने से area बढ़ नहीं सकता।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — every pair
# O(n^2) time, O(1) space
# ============================================
def max_area_brute(height: list[int]) -> int:
    best = 0  # best area found
    n = len(height)  # number of lines
    for i in range(n):  # left line
        for j in range(i + 1, n):  # right line
            best = max(best, min(height[i], height[j]) * (j - i))  # area of this pair
    return best  # maximum area

# ============================================
# APPROACH 2: Two pointers — O(n) time, O(1) space ✅ PREFERRED
# ============================================
def max_area(height: list[int]) -> int:
    l, r = 0, len(height) - 1  # start with the widest container
    best = 0  # best area so far
    while l < r:  # until the pointers meet
        best = max(best, min(height[l], height[r]) * (r - l))  # area of current pair
        if height[l] < height[r]:  # left line is shorter
            l += 1  # try a taller left line
        else:  # right line is shorter or equal
            r -= 1  # try a taller right line
    return best  # maximum area

# ============================================
# TEST CASES
# ============================================
print(max_area_brute([1, 8, 6, 2, 5, 4, 8, 3, 7]))  # 49
print(max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]))  # 49
print(max_area([1, 1]))  # 1
print(max_area([4, 3, 2, 1, 4]))  # 16
print(max_area([1, 2, 1]))  # 2
print(max_area([5]))  # 0
```

---

## 🔍 Why It Works
```
Width shrinks every step, so area can only grow if the
limiting (shorter) line gets taller.
Moving the taller line keeps the same limit but less width -> never better.
```
हिंदी: Width हर कदम घटती है, इसलिए area तभी बढ़ेगा जब छोटी line बदलकर बड़ी मिले; बड़ी line हिलाना बेकार है।

---

## 📊 Complexity
```
Brute force:  Time O(n^2) | Space O(1)
Two pointers: Time O(n)   | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Also return the pair of indices
def max_area_with_indices(height: list[int]) -> tuple[int, int, int]:
    l, r = 0, len(height) - 1  # widest container
    best = (0, l, r)  # (area, left index, right index)
    while l < r:  # shrink inward
        area = min(height[l], height[r]) * (r - l)  # current area
        if area > best[0]:  # new best
            best = (area, l, r)  # store it
        if height[l] < height[r]:  # shorter line decides
            l += 1  # move left
        else:  # right is shorter or equal
            r -= 1  # move right
    return best  # (area, l, r)

print(max_area_with_indices([1, 8, 6, 2, 5, 4, 8, 3, 7]))  # (49, 1, 8)
print(max_area_with_indices([4, 3, 2, 1, 4]))  # (16, 0, 4)
# VARIANT 2: Trapping Rain Water (D014) — water between ALL bars, not just two
# VARIANT 3: 3D version / largest rectangle in histogram (D048)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: always moving the pointer at the taller line
if height[l] > height[r]: l += 1   # can only lose width while the limit stays the same

# ❌ Wrong: using max(h[l], h[r]) instead of min -> water spills over the shorter side

# ✅ Correct: area = min(h[l], h[r]) * (r - l); move the shorter side
```

---

## 🎯 Interview Tip
Say: "Brute force is O(n^2). Starting widest and moving the shorter line is safe because the other line already caps the area; that gives O(n)." Be ready to prove it.

---

## 🔗 Related Problems
→ D014 (Trapping Rain Water) | D017 (Two Sum II) | D048 (Largest Rectangle in Histogram)
