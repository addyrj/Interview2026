
---

# D031. Fruit Into Baskets
# Category: DSA — Sliding Window
# Difficulty: ⭐⭐ Medium | LeetCode #904

---

## ❓ Problem
`fruits[i]` is the type of fruit on tree `i`. You have two baskets, each holding only one fruit type (unlimited quantity). Starting at any tree, pick exactly one fruit from each tree moving right, and stop when a fruit does not fit. Return the maximum number of fruits you can pick.

```
Input:  fruits = [1,2,3,2,2]
Output: 4      (pick 2,3,2,2)
```

---

## 💡 Quick Concept (2 lines only)
This is "longest subarray with at most 2 distinct values". Expand right, keep a count dict, and shrink left while the dict has more than 2 types.
हिंदी: असल में सवाल है "ज़्यादा से ज़्यादा 2 अलग types वाला सबसे लंबा subarray"; 3 types होते ही left बढ़ाओ।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — every start, extend while <= 2 types
# O(n^2) time, O(1) space
# ============================================
def total_fruit_brute(fruits: list[int]) -> int:
    best = 0                                   # best count so far
    for i in range(len(fruits)):               # every starting tree
        types: set[int] = set()                # fruit types in baskets
        for j in range(i, len(fruits)):        # walk right
            types.add(fruits[j])               # try to pick this fruit
            if len(types) > 2:                 # third type -> must stop
                break                          # stop this start
            best = max(best, j - i + 1)        # update best count
    return best                                # maximum fruits


# ============================================
# APPROACH 2: Sliding window with count dict — O(n) time, O(1) space  PREFERRED
# ============================================
def total_fruit(fruits: list[int]) -> int:
    counts: dict[int, int] = {}                # fruit type -> count in window
    left = 0                                   # left edge of the window
    best = 0                                   # answer
    for right, f in enumerate(fruits):         # expand with each tree
        counts[f] = counts.get(f, 0) + 1       # pick fruit f
        while len(counts) > 2:                 # more than two types in baskets
            counts[fruits[left]] -= 1          # drop the leftmost fruit
            if counts[fruits[left]] == 0:      # type fully removed
                del counts[fruits[left]]       # remove the key so len() is right
            left += 1                          # shrink the window
        best = max(best, right - left + 1)     # update the answer
    return best                                # maximum fruits


# ============================================
# TEST CASES
# ============================================
for fn in (total_fruit_brute, total_fruit):  # run both approaches
    print(fn([1, 2, 1]))           # 3
    print(fn([0, 1, 2, 2]))        # 3
    print(fn([1, 2, 3, 2, 2]))     # 4
    print(fn([3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]))  # 5
    print(fn([]))                  # 0
```

---

## 🔍 Why It Works
```
fruits = [1,2,3,2,2]
right=0,1: {1,2} size 2, best=2
right=2:   {1,2,3} size 3 -> drop left '1' -> {2,3}, window [2,3] best=2
right=3,4: {2,3} with 2,2 -> window [2,3,2,2] length 4, best=4
```
हिंदी: Dict में 2 से ज़्यादा keys होते ही left से तब तक हटाओ जब तक फिर 2 types न बचें।

---

## 📊 Complexity
```
Brute force:    Time O(n^2) | Space O(1)
Sliding window: Time O(n)   | Space O(1)  <- preferred (dict holds at most 3 keys)
```

---

## ⚡ Variations

```python
# VARIANT 1: At most K distinct characters (LeetCode 340) — replace "> 2" with "> k"
# VARIANT 2: Exactly K distinct — atMost(k) - atMost(k - 1)
# VARIANT 3: Return the starting index of the best window — store left when best improves
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: leaving zero-count keys in the dict
#    counts = {1: 0, 2: 3} still has len 2 but we think 3 types exist later -> shrinks too much
# ❌ Wrong: resetting the window to just the last fruit when a 3rd type comes
#    loses the repeated run of the previous type (e.g. [1,2,2,2,3])
# ✅ Correct: delete a key when its count reaches 0, and shrink one step at a time
```

---

## 🎯 Interview Tip
Say: "It is just longest subarray with at most two distinct values. A dict of counts plus shrinking when len > 2 gives O(n)." Then generalize to K distinct.

---

## 🔗 Related Problems
→ D025 (Longest Substring Without Repeating Characters) | D027 (Longest Repeating Character Replacement) | D026 (Minimum Size Subarray Sum)
