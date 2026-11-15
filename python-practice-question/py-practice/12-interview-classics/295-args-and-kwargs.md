---

# Q295. *args and **kwargs
# Category: INTERVIEW CLASSICS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What do `*args` and `**kwargs` mean? Write a function that accepts any positional and keyword arguments, and show how `*` / `**` also unpack on the call side.

```python
def report(*args, **kwargs):
    ...

report(1, 2, x=10, y=20)
```

---

## 💡 Quick Concept (2 lines only)
`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword arguments into a dict. On a call, `*seq` and `**mapping` do the reverse (unpack).
हिंदी: `*args` = extra positional का tuple, `**kwargs` = extra keyword का dict; call में `*`/`**` unpack करते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

def report(first: int, *args: int, sep: str = "-", **kwargs: int) -> str:
    # first: normal param; args: extra positionals; sep: keyword-only (after *args); kwargs: rest
    print(type(args).__name__, args)          # args is always a tuple
    print(type(kwargs).__name__, kwargs)      # kwargs is always a dict
    parts = [first, *args]                    # build one list from first + extras
    return sep.join(map(str, parts))          # join them using the keyword-only separator


# ============================================
# TEST CASES
# ============================================

print(report(1, 2, 3, x=10, y=20))   # extras: (2, 3) and {'x': 10, 'y': 20}
print(report(1))                     # no extras: () and {}
print(report(1, 2, sep="+"))         # sep is keyword-only, so it is NOT swallowed by kwargs

nums = [4, 5, 6]                     # a list to unpack
opts = {"sep": "/", "z": 1}          # a dict to unpack
print(report(*nums, **opts))         # same as report(4, 5, 6, sep="/", z=1)

# Expected output:
# tuple (2, 3)
# dict {'x': 10, 'y': 20}
# 1-2-3
# tuple ()
# dict {}
# 1
# tuple (2,)
# dict {}
# 1+2
# tuple (5, 6)
# dict {'z': 1}
# 4/5/6
```

---

## 🔍 Why This Works (3 lines max)
The names `args`/`kwargs` are only convention; the `*` and `**` do the work. Parameters after `*args` become keyword-only, which is why `sep` is never captured by `kwargs`. On the call side `*` unpacks any iterable and `**` unpacks a mapping.
हिंदी: नाम convention है, असली जादू `*` और `**` का है; `*args` के बाद वाले params keyword-only होते हैं।

---

## ⚡ Alternative Solution
```python
# Pass-through wrapper: forward everything untouched (the classic decorator use)
def logged(fn):
    def wrapper(*args, **kwargs):                  # accept anything
        print(f"calling {fn.__name__} {args} {kwargs}")  # log what we got
        return fn(*args, **kwargs)                 # forward exactly the same arguments
    return wrapper

@logged
def add(a: int, b: int = 0) -> int:
    return a + b                                   # normal function body

print(add(2, b=5))

# Merging dicts and lists with unpacking
a = {"x": 1}
b = {"y": 2, "x": 99}
print({**a, **b})          # later keys win on conflict
print([*range(3), *"ab"])  # unpack any iterables into a list

# Expected output:
# calling add (2,) {'b': 5}
# 7
# {'x': 99, 'y': 2}
# [0, 1, 2, 'a', 'b']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: wrong order of parameters is a SyntaxError
# def bad(**kwargs, *args): ...     # SyntaxError: arguments cannot follow var-keyword argument

# ❌ Wrong: passing a dict without ** gives ONE positional argument
def show(**kwargs):
    return kwargs

try:
    show({"a": 1})                  # dict passed positionally
except TypeError as e:
    print(e)

# ✅ Correct: unpack with **
print(show(**{"a": 1}))

# Expected output:
# show() takes 0 positional arguments but 1 was given
# {'a': 1}
```

---

## 🎯 Interview Tip (1 line)
Say: "Order is positional, `*args`, keyword-only, `**kwargs`; `args` is a tuple, `kwargs` is a dict, and wrappers/decorators forward with `fn(*args, **kwargs)`."

---

## 🔗 Related Questions
→ Q046 (*args/**kwargs unpacking output) | Q296 (decorators) | Q084 (curry) | Q088 (partial application)
