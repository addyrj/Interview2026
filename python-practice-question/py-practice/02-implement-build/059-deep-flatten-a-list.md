---

# Q059. Deep Flatten a List
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Flatten a list of **any depth**: `[1, [2, [3, [4, [5]]]], [], [[6]]]` -> `[1, 2, 3, 4, 5, 6]`.
Strings must NOT be split into characters.

---

## 💡 Quick Concept (2 lines only)
Recurse: if an item is a list/tuple, flatten it too; otherwise keep it. Check the type explicitly (`list`, `tuple`) - never "is iterable", because strings are iterable.
हिंदी: Item अगर list है तो recursion से flatten करो, वरना सीधे जोड़ दो — string को कभी मत तोड़ो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from typing import Iterable  # type hint for any iterable input

def deep_flatten(items: Iterable) -> list:
    out = []                                        # Step 1: result list
    for it in items:                                # Step 2: visit each element
        if isinstance(it, (list, tuple)):           # Step 3: nested container? (NOT str)
            out.extend(deep_flatten(it))            # Step 4: recurse and splice results in
        else:
            out.append(it)                          # Step 5: plain value -> keep it
    return out                                      # Step 6: return flat list

# ============================================
# TEST CASES
# ============================================

print(deep_flatten([1, [2, [3, [4, [5]]]], [], [[6]]]))  # Expected: [1, 2, 3, 4, 5, 6]
print(deep_flatten(["ab", [("c",), "d"]]))               # Expected: ['ab', 'c', 'd']  (strings stay whole)
deep: list = []                                          # build a 2000-level nested list
for _ in range(2000):
    deep = [deep]                                        # wrap again and again
try:
    deep_flatten(deep)                                   # recursion depth > ~1000
except RecursionError:
    print("RecursionError")                              # Expected: RecursionError
```

---

## 🔍 Why This Works (3 lines max)
Each call handles one level and delegates deeper levels to itself; `extend` splices the returned flat list. The base case is any non-list/tuple value. Python's recursion limit (~1000) is the weakness.
हिंदी: हर call एक level संभालती है, गहरी nesting के लिए खुद को बुलाती है — limit लगभग 1000 है।

---

## ⚡ Alternative Solution
```python
def deep_flatten_gen(items):                         # generator version - lazy, no big list
    for it in items:                                 # visit each element
        if isinstance(it, (list, tuple)):            # nested?
            yield from deep_flatten_gen(it)          # delegate to sub-generator
        else:
            yield it                                 # plain value

print(list(deep_flatten_gen([1, [2, [3]], "xy"])))   # Expected: [1, 2, 3, 'xy']

def deep_flatten_iter(items):                        # iterative: no recursion limit
    stack = [iter(items)]                            # stack of iterators
    out = []                                         # result
    while stack:                                     # until all iterators are done
        for it in stack[-1]:                         # continue the top iterator
            if isinstance(it, (list, tuple)):        # nested -> dive in
                stack.append(iter(it))               # push its iterator
                break                                # restart loop on the new top
            out.append(it)                           # plain value
        else:
            stack.pop()                              # iterator exhausted -> go back up
    return out

print(deep_flatten_iter([1, [2, [3, [4]]], 5]))      # Expected: [1, 2, 3, 4, 5]
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: "is it iterable?" check -> strings recurse forever (each char is a 1-char string)
def bad(items):
    out = []
    for it in items:
        if hasattr(it, "__iter__"):       # str has __iter__ too!
            out.extend(bad(it))           # "a" -> iter -> "a" -> ... RecursionError
        else:
            out.append(it)
    return out
# bad(["ab"])  -> RecursionError (verified)

# ✅ Correct: isinstance(it, (list, tuple)) - or exclude (str, bytes) explicitly
```

---

## 🎯 Interview Tip (1 line)
Mention the string trap and the recursion limit, then offer the iterative stack or `yield from` version.

---

## 🔗 Related Questions
→ Q058 (flatten) | Q073 (flatten nested dict) | Q071 (deep clone) | Q254 (generator tricks)
