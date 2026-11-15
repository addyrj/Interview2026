---

# D042. Valid Parentheses
# Category: DSA — Stack & Queue
# Difficulty: ⭐ Easy | LeetCode #20 | Asked: Amazon, Google, Microsoft, Meta

---

## ❓ Problem
Given a string containing only `()[]{}`, determine whether it is valid: every opening bracket is closed by the same type, in the correct order.

```
Input:  s = "()[]{}"   Output: True
Input:  s = "(]"       Output: False
Input:  s = "([)]"     Output: False
```

---

## 💡 Quick Concept (2 lines only)
Push every opening bracket on a stack; on a closing bracket the top must be its matching opener. At the end the stack must be empty.
हिंदी: Opening bracket stack में डालो, closing आए तो top से match करो; अंत में stack खाली होना चाहिए।

---

## ✅ Solution

```python
# ============================================
# APPROACH 1: Brute force — repeatedly delete "()", "[]", "{}"
# O(n^2) time, O(n) space
# ============================================
def is_valid_brute(s: str) -> bool:
    prev = None                                 # remember the previous string
    while prev != s:                            # stop when nothing changes
        prev = s                                # snapshot current string
        s = s.replace("()", "").replace("[]", "").replace("{}", "")  # strip adjacent pairs
    return s == ""                              # valid only if everything vanished


# ============================================
# APPROACH 2: Stack with closing->opening map — O(n) time, O(n) space ✅ PREFERRED
# ============================================
def is_valid(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}      # closing -> expected opening
    stack: list[str] = []                       # holds unmatched openers
    for ch in s:                                # scan left to right
        if ch in pairs:                         # it's a closing bracket
            if not stack or stack.pop() != pairs[ch]:  # nothing to match, or wrong type
                return False                    # invalid immediately
        else:
            stack.append(ch)                    # opening bracket -> push
    return not stack                            # leftover openers mean invalid


# ============================================
# TEST CASES
# ============================================
for case in ["()[]{}", "(]", "([)]", "{[]}", "", "(", "]"]:   # mix of valid/invalid
    print(repr(case), is_valid_brute(case), is_valid(case))   # both must agree
# '()[]{}' True True
# '(]' False False
# '([)]' False False
# '{[]}' True True
# '' True True
# '(' False False
# ']' False False
```

---

## 🔍 Why It Works
```
s = "{[]}"
{  push -> [{]
[  push -> [{, []
]  top [ matches -> [{]
}  top { matches -> []   => empty => True

s = "([)]":  ( [ pushed, ')' sees top '[' != '(' => False
```
हिंदी: सबसे आखिर में खुला bracket सबसे पहले बंद होना चाहिए — यही LIFO यानी stack का काम है।

---

## 📊 Complexity
```
Brute force: Time O(n^2) | Space O(n)
Stack:       Time O(n)   | Space O(n) ← preferred
```

---

## ⚡ Variations

```python
# VARIANT 1: Only one bracket type -> a counter is enough (O(1) space)
def balanced(s: str) -> bool:
    depth = 0                                   # open count
    for ch in s:                                # scan
        depth += 1 if ch == "(" else -1         # open +1, close -1
        if depth < 0:                           # closed too early
            return False                        # invalid
    return depth == 0                           # all opened were closed
print(balanced("(()())"), balanced("())("))     # True False

# VARIANT 2: Minimum insertions to make valid -> track unmatched opens and closes
# VARIANT 3: Longest valid parentheses (LeetCode #32) -> stack of indices
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only counting brackets — accepts "([)]" because counts match
def bad(s: str) -> bool:
    return s.count("(") == s.count(")") and s.count("[") == s.count("]")
print(bad("([)]"))                              # True  (wrong!)

# ❌ Wrong: stack.pop() on an empty stack for input like "]" -> IndexError
# ✅ Correct: check `not stack` before popping (as in the solution above)
```

---

## 🎯 Interview Tip
Say: "LIFO matches nesting, so a stack. I handle three failure cases: closing with empty stack, mismatched type, and leftover openers at the end." Mention the counter shortcut for a single bracket type.

---

## 🔗 Related Problems
→ D043 (Min Stack) | D049 (Decode String) | D047 (Evaluate Reverse Polish Notation)
