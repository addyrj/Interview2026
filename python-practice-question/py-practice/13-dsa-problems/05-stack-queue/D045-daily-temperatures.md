---

# D045. Daily Temperatures
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #739 | Asked: Amazon, Google, Meta, Microsoft

---

## ❓ Problem
Given daily temperatures, return an array where `answer[i]` is the number of days you must wait after day `i` for a warmer temperature. Use `0` if there is none.

```
Input:  [73, 74, 75, 71, 69, 72, 76, 73]
Output: [1, 1, 4, 2, 1, 1, 0, 0]
```

---

## 💡 Quick Concept (2 lines only)
Keep a stack of indices whose temperatures are still waiting for a warmer day (decreasing temps). When today is warmer than the stack top, pop it and record the gap.
हिंदी: Stack में उन दिनों के index रखो जिन्हें अभी गर्म दिन नहीं मिला; आज ज़्यादा गर्म हो तो pop करके दूरी लिख दो।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — for each day scan forward
# O(n^2) time, O(1) extra space
# ============================================
def daily_temps_brute(temps: list[int]) -> list[int]:
    n = len(temps)                              # number of days
    ans = [0] * n                               # default: never warmer
    for i in range(n):                          # each day
        for j in range(i + 1, n):               # look at later days
            if temps[j] > temps[i]:             # first warmer day
                ans[i] = j - i                  # days to wait
                break                           # stop at the first one
    return ans                                  # result


# ============================================
# APPROACH 2: Monotonic decreasing stack — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def daily_temperatures(temps: list[int]) -> list[int]:
    ans = [0] * len(temps)                      # default 0 for unresolved days
    stack: list[int] = []                       # indices awaiting a warmer day
    for i, t in enumerate(temps):               # scan days in order
        while stack and temps[stack[-1]] < t:   # today beats the waiting day(s)
            j = stack.pop()                     # resolve that earlier day
            ans[j] = i - j                      # wait = distance in days
        stack.append(i)                         # today now waits
    return ans                                  # leftovers stay 0


# ============================================
# TEST CASES
# ============================================
print(daily_temps_brute([73, 74, 75, 71, 69, 72, 76, 73]))   # [1, 1, 4, 2, 1, 1, 0, 0]
print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))  # [1, 1, 4, 2, 1, 1, 0, 0]
print(daily_temperatures([30, 40, 50, 60]))                  # [1, 1, 1, 0]
print(daily_temperatures([30, 60, 90]))                      # [1, 1, 0]
print(daily_temperatures([90, 80, 70]))                      # [0, 0, 0]
print(daily_temperatures([]))                                # []
```

---

## 🔍 Why It Works
```
temps: 73 74 75 71 69 72 76 73
i=0 push 0 | i=1 74>73 pop0 ans[0]=1, push 1 | i=2 75>74 pop1 ans[1]=1, push 2
i=3 push 3 | i=4 push 4 | i=5 72>69 pop4 ans[4]=1; 72>71 pop3 ans[3]=2; push 5
i=6 76>72 pop5 ans[5]=1; 76>75 pop2 ans[2]=4; push 6 | i=7 push 7
Stack holds temps in decreasing order; each index pushed/popped once.
```
हिंदी: हर index एक बार push और एक बार pop होता है, इसलिए कुल काम O(n) है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(1) extra
Stack:       Time O(n)   | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Scan from the right with jump pointers — O(n) time, O(1) extra space
def daily_right_to_left(temps: list[int]) -> list[int]:
    n = len(temps)                              # days
    ans = [0] * n                               # result
    for i in range(n - 2, -1, -1):              # from second-last backwards
        j = i + 1                               # candidate day
        while j < n and temps[j] <= temps[i]:   # not warmer yet
            if ans[j] == 0:                     # j has no warmer day -> none for i
                j = n                           # force exit
                break                           # leave loop
            j += ans[j]                         # jump to j's next warmer day
        if j < n:                               # found a warmer day
            ans[i] = j - i                      # distance
    return ans                                  # result
print(daily_right_to_left([73, 74, 75, 71, 69, 72, 76, 73]))  # [1, 1, 4, 2, 1, 1, 0, 0]

# VARIANT 2: Next Greater Element (D046) — same stack, returns values
# VARIANT 3: Stock Span problem — monotonic stack looking backwards
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: using <= in the pop condition -> equal temps get resolved as "warmer"
#    while stack and temps[stack[-1]] <= t:   # [70, 70] would give [1, 0]
# ❌ Wrong: storing temperatures instead of indices -> you can't compute day distance
# ✅ Correct: strict < comparison and store indices
```

---

## 🎯 Interview Tip
Say: "Brute force is O(n²). A monotonic decreasing stack of indices resolves each day when a warmer one arrives — amortized O(n)." Mention strict comparison for equal temperatures.

---

## 🔗 Related Problems
→ D046 (Next Greater Element) | D048 (Largest Rectangle in Histogram) | D043 (Min Stack)
