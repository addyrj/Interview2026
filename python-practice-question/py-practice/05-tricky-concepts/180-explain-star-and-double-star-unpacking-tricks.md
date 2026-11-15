---

# Q180. Explain * and ** Unpacking Tricks
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show the different uses of `*` and `**`: star-assignment, building collections, merging dicts, calling functions, and keyword-only/positional-only markers.

---

## 💡 Quick Concept (2 lines only)
`*` unpacks any iterable (or collects extras); `**` unpacks mappings into keyword arguments or dict literals. A bare `*` or `/` in a signature marks keyword-only / positional-only.
हिंदी: `*` iterable खोलता है, `**` dict खोलता है; function signature में `*` और `/` arguments का तरीका तय करते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
first, *mid, last = [1, 2, 3, 4, 5]          # Step 1: star-assignment collects the middle
print(first, mid, last)                      # Expected: 1 [2, 3, 4] 5
a, *b = "xyz"                                # works on any iterable; star target is always a list
print(a, b)                                  # Expected: x ['y', 'z']
print([*range(3), *"ab"])                    # Step 2: build lists   -> Expected: [0, 1, 2, 'a', 'b']
print({*[1, 2], *[2, 3]})                    # build sets            -> Expected: {1, 2, 3}
d1 = {"a": 1, "b": 2}
d2 = {"b": 20, "c": 3}
print({**d1, **d2})                          # Step 3: merge dicts, later wins -> Expected: {'a': 1, 'b': 20, 'c': 3}
print(d1 | d2)                               # 3.9+ operator, same result      -> Expected: {'a': 1, 'b': 20, 'c': 3}

def f(a: int, b: int, *rest: int, key: str = "k", **extra: int) -> str:
    return f"{a} {b} {rest} {key} {extra}"   # shows how args are split
print(f(*[1, 2, 3, 4], **{"key": "z", "x": 9}))  # Step 4: Expected: 1 2 (3, 4) z {'x': 9}

def only_kw(*, x: int) -> int:               # everything after bare * is keyword-only
    return x
print(only_kw(**{"x": 1}))                   # Expected: 1
def pos_only(a: int, /, b: int) -> int:      # everything before / is positional-only
    return a + b

# ============================================
# TEST CASES
# ============================================
print(pos_only(1, b=2))                      # Expected: 3
try:
    pos_only(a=1, b=2)                       # a given by keyword -> not allowed
except TypeError as e:
    print("TypeError:", e)                   # Expected: TypeError: pos_only() got some positional-only arguments passed as keyword arguments: 'a'
```

---

## 🔍 Why This Works (3 lines max)
Unpacking in a call expands before the call happens; in a signature, `*args`/`**kwargs` collect extras into a tuple/dict. In a dict merge, later keys override earlier ones, and duplicate keyword arguments in a call raise `TypeError`.
हिंदी: Call में unpacking पहले होती है, signature में extras tuple/dict में जमा होते हैं; दोहराया keyword error देता है।

---

## ⚡ Alternative Solution
```python
for (x, *y) in [(1, 2, 3), (4,)]:            # star target in loops
    print(x, y)                              # Expected: 1 [2, 3]  then  4 []
(a1, b1), c1 = (1, 2), 3                     # nested unpacking
print(a1, b1, c1)                            # Expected: 1 2 3
print(list(zip(*[[1, 2], [3, 4], [5, 6]])))  # transpose a matrix -> Expected: [(1, 3, 5), (2, 4, 6)]
print(print(*[1, 2], sep="-"))               # Expected: 1-2 then None

try:
    f(1, 2, **{"key": "a"}, **{"key": "b"})  # duplicate keyword
except TypeError as e:
    print("TypeError:", e)                   # Expected: TypeError: __main__.f() got multiple values for keyword argument 'key'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: unpacking without a star when lengths differ
try:
    x, y = [1, 2, 3]                         # too many values
except ValueError as e:
    print("ValueError:", e)                  # Output: ValueError: too many values to unpack (expected 2)

# ✅ Correct: x, *y = [1, 2, 3]  ->  x=1, y=[2, 3]
# (Only ONE starred target is allowed: `*p, *q = ...` is a SyntaxError.)
```

---

## 🎯 Interview Tip (1 line)
Say: "`*` and `**` work on both sides — collecting in signatures/assignments, expanding in calls/literals; `*`/`/` markers enforce keyword-only/positional-only."

---

## 🔗 Related Questions
→ Q046 (*args/**kwargs unpacking) | Q242 (unpacking examples) | Q259 (*args/**kwargs tricks) | Q295 (*args and **kwargs)
