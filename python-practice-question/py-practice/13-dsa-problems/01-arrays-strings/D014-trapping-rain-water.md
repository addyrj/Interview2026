---

# D014. Trapping Rain Water
# Category: DSA — Arrays & Strings
# Difficulty: ⭐⭐⭐ Hard | LeetCode #42

---

## ❓ Problem
Given `n` non-negative integers representing an elevation map (bar width 1), compute how much water it can trap after raining.

```
Input:  height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
```

---

## 💡 Quick Concept (2 lines only)
Water above a bar = `min(tallest bar to its left, tallest bar to its right) - its own height`. Two pointers let you compute this in one pass without storing prefix arrays.
हिंदी: हर bar पर पानी = (बाएँ और दाएँ की सबसे ऊँची bar में से छोटी) − अपनी height; two pointers से यह O(1) space में हो जाता है।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — scan left and right for every bar
# O(n^2) time, O(1) space
# ============================================
def trap_brute(height: list[int]) -> int:
    total = 0  # accumulated water
    for i, h in enumerate(height):  # for every bar
        left_max = max(height[: i + 1])  # tallest bar from 0..i
        right_max = max(height[i:])  # tallest bar from i..end
        total += min(left_max, right_max) - h  # water above this bar
    return total  # total trapped water

# ============================================
# APPROACH 2: Prefix/suffix max arrays — O(n) time, O(n) space
# ============================================
def trap_prefix(height: list[int]) -> int:
    n = len(height)  # number of bars
    if n == 0:  # empty map traps nothing
        return 0  # nothing to compute
    left = [0] * n  # left[i] = tallest bar in 0..i
    right = [0] * n  # right[i] = tallest bar in i..n-1
    left[0] = height[0]  # base case
    for i in range(1, n):  # fill left to right
        left[i] = max(left[i - 1], height[i])  # running maximum
    right[-1] = height[-1]  # base case
    for i in range(n - 2, -1, -1):  # fill right to left
        right[i] = max(right[i + 1], height[i])  # running maximum
    return sum(min(left[i], right[i]) - height[i] for i in range(n))  # sum water per bar

# ============================================
# APPROACH 3: Two pointers — O(n) time, O(1) space ✅ PREFERRED
# ============================================
def trap(height: list[int]) -> int:
    l, r = 0, len(height) - 1  # pointers at both ends
    left_max = right_max = 0  # best wall seen from each side
    total = 0  # accumulated water
    while l < r:  # until pointers meet
        if height[l] < height[r]:  # left side is the limiting side
            left_max = max(left_max, height[l])  # update left wall
            total += left_max - height[l]  # water is bounded by left_max
            l += 1  # move left pointer inward
        else:  # right side is limiting (or equal)
            right_max = max(right_max, height[r])  # update right wall
            total += right_max - height[r]  # water is bounded by right_max
            r -= 1  # move right pointer inward
    return total  # total trapped water

# ============================================
# TEST CASES
# ============================================
print(trap_brute([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # 6
print(trap_prefix([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # 6
print(trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # 6
print(trap([4, 2, 0, 3, 2, 5]))  # 9
print(trap([]))  # 0
print(trap([3]))  # 0
print(trap([1, 2, 3, 4]))  # 0
```

---

## 🔍 Why It Works
```
Bar i holds min(max_left, max_right) - h[i].
If h[l] < h[r], then right wall >= h[r] > h[l],
so only left_max decides the water at l. Same logic mirrored for r.
```
हिंदी: जो तरफ छोटी है वही water का level तय करती है, इसलिए उसी तरफ का pointer आगे बढ़ाकर पानी जोड़ दो।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Prefix max:  Time O(n)   | Space O(n)
Two pointers: Time O(n)  | Space O(1) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Monotonic stack — O(n) time, O(n) space
def trap_stack(height: list[int]) -> int:
    stack: list[int] = []  # indices of bars with decreasing heights
    total = 0  # accumulated water
    for i, h in enumerate(height):  # scan bars left to right
        while stack and h > height[stack[-1]]:  # current bar closes a valley
            bottom = height[stack.pop()]  # valley floor
            if not stack:  # no left wall
                break  # cannot hold water
            width = i - stack[-1] - 1  # distance between the two walls
            total += width * (min(h, height[stack[-1]]) - bottom)  # layer of water
        stack.append(i)  # push current bar
    return total  # total trapped water

print(trap_stack([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))  # 6
print(trap_stack([4, 2, 0, 3, 2, 5]))  # 9
# VARIANT 2: Trapping Rain Water II (2D grid) — min-heap from the border inwards
# VARIANT 3: Return water per index instead of the total
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using only the neighbours instead of the max on each side
water += min(height[i - 1], height[i + 1]) - height[i]   # ignores far-away tall walls

# ❌ Wrong: not clamping at 0 when mixing up left_max/right_max updates (negative water)

# ✅ Correct: always use running max from each side (prefix/suffix or two pointers)
```

---

## 🎯 Interview Tip
Say: "Brute force is O(n^2). I precompute prefix/suffix maxima for O(n) space, then compress to two pointers since the smaller wall decides the water." Mention the stack solution as an alternative.

---

## 🔗 Related Problems
→ D019 (Container With Most Water) | D004 (Product of Array Except Self) | D005 (Maximum Subarray)
