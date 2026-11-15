---

# D043. Min Stack
# Category: DSA — Stack & Queue
# Difficulty: ⭐⭐ Medium | LeetCode #155 | Asked: Amazon, Microsoft, Google, Bloomberg

---

## ❓ Problem
Design a stack supporting `push`, `pop`, `top` and `get_min` — all in O(1) time.

```
push(-2), push(0), push(-3)
get_min() -> -3
pop()
top()     -> 0
get_min() -> -2
```

---

## 💡 Quick Concept (2 lines only)
Store, alongside each value, the minimum of the stack up to that point. Popping then automatically restores the previous minimum.
हिंदी: हर element के साथ "अब तक का minimum" भी रखो; pop करने पर पुराना minimum अपने आप वापस आ जाता है।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — get_min scans the stack
# push/pop/top O(1), get_min O(n)
# ============================================
class MinStackBrute:
    def __init__(self) -> None:
        self.data: list[int] = []               # plain stack

    def push(self, x: int) -> None:
        self.data.append(x)                     # O(1)

    def pop(self) -> None:
        self.data.pop()                         # O(1)

    def top(self) -> int:
        return self.data[-1]                    # O(1)

    def get_min(self) -> int:
        return min(self.data)                   # O(n) scan — too slow


# ============================================
# APPROACH 2: Stack of (value, min_so_far) pairs — all O(1) ✅ PREFERRED
# ============================================
class MinStack:
    def __init__(self) -> None:
        self.stack: list[tuple[int, int]] = []  # each entry: (value, current minimum)

    def push(self, x: int) -> None:
        cur_min = min(x, self.stack[-1][1]) if self.stack else x  # min including x
        self.stack.append((x, cur_min))         # store both together

    def pop(self) -> None:
        self.stack.pop()                        # min history pops with it

    def top(self) -> int:
        return self.stack[-1][0]                # value part of the top entry

    def get_min(self) -> int:
        return self.stack[-1][1]                # min part of the top entry


# ============================================
# TEST CASES
# ============================================
for cls in (MinStackBrute, MinStack):           # same test for both
    s = cls()                                   # fresh stack
    s.push(-2); s.push(0); s.push(-3)           # build up
    print(s.get_min())                          # -3
    s.pop()                                     # remove -3
    print(s.top())                              # 0
    print(s.get_min())                          # -2
```

---

## 🔍 Why It Works
```
push -2 -> [(-2,-2)]
push  0 -> [(-2,-2), (0,-2)]
push -3 -> [(-2,-2), (0,-2), (-3,-3)]   get_min = -3
pop     -> [(-2,-2), (0,-2)]            get_min = -2 (restored for free)
```
हिंदी: हर entry अपने नीचे के सारे elements का minimum जानती है, इसलिए get_min हमेशा top देखकर O(1) में मिलता है।

---

## 📊 Complexity
```
Brute force: push/pop/top O(1), get_min O(n) | Space O(n)
Pair stack:  all operations O(1)             | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Two stacks — main stack + min stack (push to min only when x <= current min)
class MinStack2:
    def __init__(self) -> None:
        self.s: list[int] = []                  # main stack
        self.m: list[int] = []                  # monotonic min stack

    def push(self, x: int) -> None:
        self.s.append(x)                        # always push to main
        if not self.m or x <= self.m[-1]:       # <= keeps duplicate minimums
            self.m.append(x)                    # new (or equal) minimum

    def pop(self) -> None:
        if self.s.pop() == self.m[-1]:          # removed the current minimum
            self.m.pop()                        # drop it from min stack too

    def get_min(self) -> int:
        return self.m[-1]                       # current minimum

t = MinStack2(); t.push(2); t.push(2); t.push(1); t.pop(); t.pop()
print(t.get_min())                              # 2

# VARIANT 2: Max Stack (same idea with max)
# VARIANT 3: Min Stack with O(1) extra space by storing encoded differences
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: min stack pushes only when x < min (strict) — duplicates break it
#    push(2), push(2), pop() -> min stack lost the only 2 -> get_min() fails
# ✅ Correct: push to the min stack when x <= current min (or use the pair approach)
```

---

## 🎯 Interview Tip
Say: "Brute force makes get_min O(n). Carrying the running minimum with each element gives O(1) everything for O(n) extra space." Mention the `<=` duplicate pitfall in the two-stack version.

---

## 🔗 Related Problems
→ D042 (Valid Parentheses) | D044 (Implement Queue using Stacks) | D045 (Daily Temperatures)
