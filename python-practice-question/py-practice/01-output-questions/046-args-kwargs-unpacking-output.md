---

# Q046. *args/**kwargs Unpacking Output
# Category: Output Questions
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this code print?

```python
def show(*args, **kwargs):
    print(args, kwargs)

nums = [1, 2, 3]
d = {"x": 1, "y": 2}

show(1, 2, a=3)
show(*nums, **d)
show(*"ab", *[3], **{"k": 1}, z=2)
print([*nums, *"hi"])
print({**d, "y": 20, "z": 3})

def f(a, b=2, *rest, c, d=4, **kw):
    return a, b, rest, c, d, kw

print(f(1, c=3))
print(f(1, 2, 3, 4, c=5, e=6))

try:
    show(**{"a": 1}, **{"a": 2})
except TypeError as e:
    print("TypeError:", e)
```

---

## 💡 Quick Concept (2 lines only)
In a `def`, `*args` packs extra positionals into a tuple and `**kwargs` packs extra keywords into a dict. In a call or literal, `*` and `**` unpack iterables and mappings.
हिंदी: `def` में `*`/`**` इकट्ठा करते हैं (pack), call में बिखेरते हैं (unpack)।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def show(*args: int, **kwargs: int) -> None:
    print(args, kwargs)                       # args is a tuple, kwargs is a dict

nums = [1, 2, 3]                              # list to unpack
d = {"x": 1, "y": 2}                          # dict to unpack

show(1, 2, a=3)                               # Step 1: plain call -> packed
show(*nums, **d)                              # Step 2: unpack list + dict into the call
show(*"ab", *[3], **{"k": 1}, z=2)            # Step 3: multiple unpackings allowed; str unpacks to chars
print([*nums, *"hi"])                         # Step 4: unpack inside a list literal
print({**d, "y": 20, "z": 3})                 # Step 5: dict merge, later keys win

def f(a, b=2, *rest, c, d=4, **kw):           # c is keyword-only (after *rest)
    return a, b, rest, c, d, kw               # return everything to inspect

print(f(1, c=3))                              # Step 6: defaults fill b, d
print(f(1, 2, 3, 4, c=5, e=6))                # Step 7: 3,4 -> rest; e -> kw

try:
    show(**{"a": 1}, **{"a": 2})              # Step 8: duplicate key across ** unpackings
except TypeError as e:
    print("TypeError:", e)                    # error, NOT a silent override

# ============================================
# TEST CASES (real output, Python 3.13)
# ============================================
# (1, 2) {'a': 3}
# (1, 2, 3) {'x': 1, 'y': 2}
# ('a', 'b', 3) {'k': 1, 'z': 2}
# [1, 2, 3, 'h', 'i']
# {'x': 1, 'y': 20, 'z': 3}
# (1, 2, (), 3, 4, {})
# (1, 2, (3, 4), 5, 4, {'e': 6})
# TypeError: __main__.show() got multiple values for keyword argument 'a'
#   (message prefix like "__main__.show()" vs "show()" varies by Python version)
```

---

## 🔍 Why This Works (3 lines max)
`*` unpacks any iterable (strings too) into positionals; `**` unpacks a mapping into keywords, and a duplicate key raises `TypeError` in calls. In dict literals `{**a, **b}` the later value wins instead. Parameters after `*rest` are keyword-only, so `c` must be passed by name.
हिंदी: Call में duplicate keyword = error, dict literal में बाद वाली value जीतती है; `*rest` के बाद वाले parameters सिर्फ नाम से मिलते हैं।

---

## ⚡ Alternative Solution
```python
first, *mid, last = range(5)                  # star-unpacking in assignment
print(first, mid, last)                       # Output: 0 [1, 2, 3] 4

print(*[1, 2, 3], sep="-")                    # unpack into print's args -> Output: 1-2-3

def pos(a, b, /, c):                          # a, b are positional-only
    return a, b, c                            # return all three

try:
    pos(1, b=2, c=3)                          # b passed by keyword -> not allowed
except TypeError as e:
    print("TypeError:", e)
# Output: TypeError: pos() got some positional-only arguments passed as keyword arguments: 'b'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: passing a list/dict without unpacking
def add(a, b, c): return a + b + c
# add([1, 2, 3])        # TypeError: missing 2 required positional arguments  (not run)

# ✅ Correct: unpack with * (and ** for dicts)
print(add(*[1, 2, 3]))                  # Output: 6
print(add(**{"a": 1, "b": 2, "c": 3}))  # Output: 6
```

---

## 🎯 Interview Tip (1 line)
Say: "`*args` is a tuple, `**kwargs` is a dict; params after `*` are keyword-only, before `/` positional-only; duplicate `**` keys raise TypeError."

---

## 🔗 Related Questions
→ Q241 (comprehensions) | Q242 (unpacking examples) | Q259 (*args/**kwargs tricks) | Q295 (*args and **kwargs)
