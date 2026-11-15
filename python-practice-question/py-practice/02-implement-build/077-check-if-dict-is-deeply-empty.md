---

# Q077. Check if dict is (deeply) empty
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Write `is_deeply_empty(obj)` that returns `True` if a dict contains no real data at any depth — only empty dicts, empty lists or `None`. Values like `0` and `""` count as real data.

```python
is_deeply_empty({"a": {}, "b": {"c": {}}})  # True
is_deeply_empty({"a": {"b": 0}})            # False
```

---

## 💡 Quick Concept (2 lines only)
`not d` only checks the top level — `{"a": {}}` is truthy. Recurse: a container is deeply empty if ALL of its children are; a leaf is "empty" only if it is `None`.
हिंदी: `not d` सिर्फ ऊपर का level देखता है; अंदर तक जाने के लिए recursion चाहिए।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any                                 # type hint

def is_deeply_empty(obj: Any) -> bool:
    if isinstance(obj, dict):                          # Step 1: dict -> check all its values
        return all(is_deeply_empty(v) for v in obj.values())  # all() of empty dict is True
    if isinstance(obj, (list, tuple, set)):            # Step 2: other containers -> check all items
        return all(is_deeply_empty(v) for v in obj)    # empty list -> True
    return obj is None                                 # Step 3: leaf counts as empty only if None

# ============================================
# TEST CASES
# ============================================
print(is_deeply_empty({}))                             # Expected: True
print(is_deeply_empty({"a": {}, "b": {"c": {}}}))      # Expected: True
print(is_deeply_empty({"a": {"b": None}, "c": []}))    # Expected: True
print(is_deeply_empty({"a": {"b": 0}}))                # Expected: False  (0 is real data)
print(is_deeply_empty({"a": {"b": ""}}))               # Expected: False  (empty string is real data)
print(is_deeply_empty({"a": [{}, {"x": {}}]}))         # Expected: True
print(not {"a": {}})                                   # Expected: False  <- plain truthiness is fooled
```

---

## 🔍 Why This Works (3 lines max)
`all()` on an empty iterable returns `True`, so `{}` and `[]` are naturally "empty" and the recursion needs no special case. One non-empty leaf anywhere makes `all()` return `False` and bubbles up.
हिंदी: खाली container पर `all()` True देता है, इसलिए base case अपने आप बन जाता है।

---

## ⚡ Alternative Solution
```python
# Truthiness-based one-liner: treats 0, "", False as empty too (different rule!)
def is_deeply_empty2(o: object) -> bool:
    return not o or (isinstance(o, dict) and all(map(is_deeply_empty2, o.values())))  # falsy leaf or all-empty dict

print(is_deeply_empty2({"a": {"b": {}}}), is_deeply_empty2({"a": {"b": 0}}), is_deeply_empty2({"a": {"b": 1}}))  # Expected: True True False
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: only checks the top level
d = {"a": {}, "b": {"c": {}}}                          # looks empty but has keys
print(not d)                                           # Output: False  <- reported "not empty"
print(len(d) == 0)                                     # Output: False
# ✅ Correct: recurse with all(...) as in the solution
# ⚠️ Also decide: should 0 / "" / False count as empty? State your rule explicitly.
```

---

## 🎯 Interview Tip (1 line)
Ask first: "Does 0, '' or False count as empty?" — defining the rule before coding is what interviewers look for.

---

## 🔗 Related Questions
→ Q017 (truthy/falsy) | Q049 (any/all empty) | Q068 (remove falsy) | Q078 (deep equal)
