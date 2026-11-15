---

# Q259. *args / **kwargs Tricks
# Category: PYTHONIC + MODERN PYTHON FEATURES
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 6 `*args` / `**kwargs` tricks: variadic functions, keyword-only args, positional-only args (`/`), unpacking when calling, merging dicts into a call, and forwarding arguments in a wrapper.

```python
def f(a, b, *args, key=None, **kwargs): ...
# f(1, 2, 3, 4, key="x", z=9)  -> a=1, b=2, args=(3, 4), key='x', kwargs={'z': 9}
```

---

## 💡 Quick Concept (2 lines only)
`*args` collects extra positional arguments into a tuple, `**kwargs` collects extra keyword arguments into a dict. At a call site, `*` and `**` do the reverse: they unpack. Parameters after `*` are keyword-only; those before `/` are positional-only.
हिंदी: Definition में `*args` इकट्ठा करता है, call में `*` खोलता (unpack करता) है — `*` के बाद वाले parameters सिर्फ keyword से दिए जाते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
def f(a, b, *args, key=None, **kwargs):          # full signature
    print(a, b, args, key, kwargs)               # show what each name received

f(1, 2, 3, 4, key="x", z=9)                      # 1. extras go to args, named extras to kwargs

def only_kw(x: int, *, scale: int = 1) -> int:   # 2. after bare *, scale is keyword-only
    return x * scale                             # use it

print(only_kw(5, scale=3))                       # must name scale

def pos_only(a: int, b: int, /) -> int:          # 3. before /, args are positional-only
    return a + b                                 # sum

print(pos_only(1, 2))                            # ok; pos_only(a=1, b=2) would fail

nums = [1, 2, 3]                                 # a list to unpack
print(*nums)                                     # 4. * at call site spreads items as arguments

defaults = {"a": 1, "b": 2}                      # base config
overrides = {"b": 20, "c": 3}                    # overrides
print({**defaults, **overrides})                 # 5. ** merges dicts, later wins

def wrapper(*args, **kwargs):                    # 6. forward everything untouched
    return sum_three(*args, **kwargs)            # pass through unchanged

def sum_three(x: int, y: int, z: int = 0) -> int:
    return x + y + z                             # target function

print(wrapper(1, 2), wrapper(1, y=2, z=3))       # works for any call style

# Output:
# 1 2 (3, 4) x {'z': 9}
# 15
# 3
# 1 2 3
# {'a': 1, 'b': 20, 'c': 3}
# 3 6
```

---

## 🔍 Why This Works (3 lines max)
Python binds positional args first, collects leftovers into the `*args` tuple, then binds keywords; unknown keywords land in `**kwargs`. A bare `*` forces everything after it to be named, which makes APIs self-documenting and safe to extend. `*args, **kwargs` forwarding is how decorators wrap any function.
हिंदी: Wrapper में `*args, **kwargs` आगे pass करने से कोई भी function बिना signature जाने wrap हो जाता है।

---

## ⚡ Alternative Solution
```python
# Unpacking in assignments and duplicate-key error
first, *middle, last = [1, 2, 3, 4, 5]           # star-assignment: middle collects the rest
print(first, middle, last)

def show(**kwargs):
    print(kwargs)                                # kwargs is a plain dict (a copy)

show(**{"a": 1}, b=2)                            # mix unpacking and explicit keywords

try:
    show(**{"a": 1}, a=2)                        # same keyword twice -> error
except TypeError as e:
    print(e)

# Output:
# 1 [2, 3, 4] 5
# {'a': 1, 'b': 2}
# __main__.show() got multiple values for keyword argument 'a'   (3.13 prefixes the module; older versions print just show())
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: passing a keyword-only parameter positionally
def connect(host, *, port=80):
    return f"{host}:{port}"

try:
    connect("h", 8080)                           # ❌ port is keyword-only
except TypeError as e:
    print(e)

# ✅ Correct: name it
print(connect("h", port=8080))

# Output:
# connect() takes 1 positional argument but 2 were given
# h:8080
```

---

## 🎯 Interview Tip (1 line)
Say: "`*args` is a tuple, `**kwargs` is a dict; bare `*` makes keyword-only, `/` makes positional-only, and I forward both in decorators."

---

## 🔗 Related Questions
→ Q046 (*args/**kwargs unpacking output) | Q180 (* and ** unpacking tricks) | Q242 (unpacking — 10 examples) | Q295 (*args and **kwargs)
