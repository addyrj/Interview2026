---

# Q030. __init__ vs __new__ call order output
# Category: OUTPUT QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
What will this print, and when is `__init__` skipped?

```python
class Demo:
    def __new__(cls, *args, **kwargs):
        print("__new__", args)
        return super().__new__(cls)
    def __init__(self, name: str) -> None:
        print("__init__", name)

Demo("a")
```

---

## 💡 Quick Concept (2 lines only)
`__new__` creates the object, then `__init__` initializes it — but only if `__new__` returned an instance of that class.
हिंदी: पहले `__new__` object बनाता है, फिर `__init__` उसे set करता है — अगर `__new__` उसी class का object लौटाए।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Demo:
    def __new__(cls, *args, **kwargs):
        print("__new__", args)             # Step 1: runs first, before the object exists
        instance = super().__new__(cls)    # Step 2: actually allocate the object
        return instance                    # Step 3: instance of cls -> Python calls __init__
    def __init__(self, name: str) -> None:
        print("__init__", name)            # Step 4: runs second on the new object
        self.name = name                   # store state

class Other:
    def __init__(self) -> None:
        print("Other.__init__ (never runs)")  # not called by Weird()

class Weird:
    def __new__(cls):
        print("Weird.__new__")             # runs
        return Other()                     # returns a NON-Weird object
    def __init__(self) -> None:
        print("Weird.__init__ (never runs)")  # skipped: result is not a Weird

# ============================================
# TEST CASES
# ============================================
d = Demo("a")
# Expected:
# __new__ ('a',)
# __init__ a
print(type(d).__name__)   # Expected: Demo
w = Weird()
# Expected:
# Weird.__new__
# Other.__init__ (never runs)
print(type(w).__name__)   # Expected: Other
```

---

## 🔍 Why This Works (3 lines max)
`Demo("a")` calls `type.__call__`, which runs `__new__` then, if the result is an instance of `Demo`, `__init__` with the same arguments. In `Weird`, `Other()` is returned, so `Weird.__init__` is skipped (and `Other()` ran its own `__init__` when called).
हिंदी: Result उसी class का instance न हो तो उस class का `__init__` नहीं चलता।

---

## ⚡ Alternative Solution
```python
# Classic use of __new__: Singleton (note __init__ still runs every call!)
class Single:
    _inst = None                              # cached instance
    def __new__(cls):
        if cls._inst is None:                 # first call only
            cls._inst = super().__new__(cls)  # create once
        return cls._inst                      # always return the same object
    def __init__(self) -> None:
        print("init called")                  # runs on EVERY Single() call

s1, s2 = Single(), Single()                   # Expected: init called (printed twice)
print(s1 is s2)                               # Expected: True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: forgetting to return the instance from __new__
# class Bad:
#     def __new__(cls):
#         super().__new__(cls)   # no return -> Bad() is None, __init__ never runs
# ✅ Correct: always `return super().__new__(cls)` (not run: Bad() would return None)
```

---

## 🎯 Interview Tip (1 line)
Say: "`__new__` is a static constructor that returns the object; `__init__` only initializes it — use `__new__` for immutables, singletons and metaclass tricks."

---

## 🔗 Related Questions
→ Q031 (inheritance and super) | Q300 (__init__ vs __new__) | Q261 (singleton pattern) | Q168 (metaclasses)
