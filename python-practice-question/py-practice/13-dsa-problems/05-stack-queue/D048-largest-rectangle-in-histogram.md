---

# D048. Largest Rectangle in Histogram
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐⭐ Hard | LeetCode #84 | Asked: Amazon, Google, Microsoft, Adobe

---

## ❓ Problem
Given bar heights of a histogram (each bar has width 1), return the area of the largest rectangle that fits inside it.

```
Input:  heights = [2, 1, 5, 6, 2, 3]
Output: 10   (bars of height 5 and 6 -> 5 * 2)
```

---

## 💡 Quick Concept (2 lines only)
Keep a stack of bars with increasing heights. When a shorter bar arrives, pop taller bars — each popped bar's rectangle extends left to the new stack top and right to the current index.
हिंदी: Increasing heights का stack रखो; छोटा bar आते ही बड़े bars pop करो और उनका सबसे चौड़ा rectangle निकालो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — expand from every bar
# O(n^2) time, O(1) space
# ============================================
def largest_rect_brute(heights: list[int]) -> int:
    best = 0                                    # best area so far
    for i, h in enumerate(heights):             # treat each bar as the limiting height
        left = i                                # extend left while bars are >= h
        while left > 0 and heights[left - 1] >= h:  # taller or equal neighbour
            left -= 1                           # move left boundary
        right = i                               # extend right while bars are >= h
        while right < len(heights) - 1 and heights[right + 1] >= h:  # taller or equal neighbour
            right += 1                          # move right boundary
        best = max(best, h * (right - left + 1))  # area = height * width
    return best                                 # answer


# ============================================
# APPROACH 2: Monotonic increasing stack — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def largest_rectangle_area(heights: list[int]) -> int:
    stack: list[int] = []                       # indices with increasing heights
    best = 0                                    # best area so far
    for i, h in enumerate(heights + [0]):       # sentinel 0 flushes the stack at the end
        while stack and heights[stack[-1]] > h:  # current bar is shorter -> resolve taller ones
            height = heights[stack.pop()]       # height of the popped bar
            left = stack[-1] if stack else -1   # first smaller bar on the left
            width = i - left - 1                # span between the two smaller bars
            best = max(best, height * width)    # candidate area
        stack.append(i)                         # push current index
    return best                                 # answer


# ============================================
# TEST CASES
# ============================================
print(largest_rect_brute([2, 1, 5, 6, 2, 3]))           # 10
print(largest_rectangle_area([2, 1, 5, 6, 2, 3]))       # 10
print(largest_rectangle_area([2, 4]))                   # 4
print(largest_rectangle_area([1, 1, 1, 1]))             # 4
print(largest_rectangle_area([5]))                      # 5
print(largest_rectangle_area([6, 5, 4, 3]))             # 12
print(largest_rectangle_area([]))                       # 0
```

---

## 🔍 Why It Works
```
heights = [2,1,5,6,2,3] + sentinel 0
push 0(2) | i=1 h=1: pop 2, width=1-(-1)-1=1 area 2, push 1
push 2(5), push 3(6) | i=4 h=2: pop 6 -> width 4-2-1=1 area 6; pop 5 -> width 4-1-1=2 area 10
...
Best = 10
```
हिंदी: Pop होने वाले bar के बाएं और दाएं पहला छोटा bar ही उसकी सीमा तय करता है — बीच की चौड़ाई × height।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1)
Stack:       Time O(n)   | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Maximal Rectangle in a binary matrix (LeetCode #85) — build a histogram per row
# VARIANT 2: Trapping Rain Water (LeetCode #42) — stack or two pointers
# VARIANT 3: Divide and conquer around the minimum bar (O(n log n) average, O(n^2) worst)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting the sentinel / final flush -> bars left on the stack are never evaluated
#    [2, 4] would return 0 instead of 4
# ❌ Wrong: width = i - stack[-1] (off by one) — should be i - stack[-1] - 1
# ✅ Correct: append 0 to heights and use width = i - left - 1 with left = -1 for empty stack
```

---

## 🎯 Interview Tip
Say: "For each bar I need the nearest smaller bar on both sides. A monotonic increasing stack finds both in one pass — the left is the new top, the right is the current index." Mention the sentinel trick.

---

## 🔗 Related Problems
→ D045 (Daily Temperatures) | D046 (Next Greater Element) | D043 (Min Stack)
