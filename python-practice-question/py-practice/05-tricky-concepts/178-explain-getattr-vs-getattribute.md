---

# Q178. Explain __getattr__ vs __getattribute__
# Category: Tricky Concepts
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
What is the difference between `__getattr__` and `__getattribute__`? What prints when you access `d.real` and `d.missing`?

---

## 💡 Quick Concept (2 lines only)
`__getattribute__` runs on EVERY attribute access; `__getattr__` is only the fallback when normal lookup raises `AttributeError`.
हिंदी: `__getattribute__` हर access पर चलता है, `__getattr__` सिर्फ तब जब attribute मिले ही नहीं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
class Demo:
    def __init__(self) -> None:
        self.real = 1                        # normal instance attribute
    def __getattr__(self, name: str) -> str:
        print(f"__getattr__({name!r})")      # fallback only
        return f"fallback-{name}"            # value for missing names
    def __getattribute__(self, name: str):
        print(f"__getattribute__({name!r})") # runs for every lookup
        return super().__getattribute__(name)  # delegate (do NOT use self.x here)

# ============================================
# TEST CASES
# ============================================
d = Demo()                                   # create
print(d.real)                                # Expected: __getattribute__('real') then 1
print(d.missing)                             # Expected: __getattribute__('missing') -> __getattr__('missing') -> fallback-missing
```

---

## 🔍 Why This Works (3 lines max)
Attribute access calls `type(obj).__getattribute__`; if it raises `AttributeError`, Python then calls `__getattr__`. Inside `__getattribute__` always delegate to `super()` (or `object`), otherwise `self.x` re-enters it and recurses forever.
हिंदी: पहले `__getattribute__`, वहाँ `AttributeError` आए तो `__getattr__`; `__getattribute__` में `self.x` लिखा तो infinite recursion।

---

## ⚡ Alternative Solution
```python
import copy                                  # for copy demo

class OnlyGetattr:                           # the common, safer choice
    def __init__(self) -> None:
        self.real = 1                        # found normally
    def __getattr__(self, name: str) -> str:
        return f"fallback-{name}"            # only for missing names
o = OnlyGetattr()
print(o.real, o.ghost)                       # Expected: 1 fallback-ghost

class Strict:                                # guard dunder lookups
    def __getattr__(self, name: str):
        if name.startswith("__"):
            raise AttributeError(name)       # keep hasattr/copy/pickle sane
        return name.upper()                  # dynamic attributes
s = Strict()
print(s.abc, hasattr(s, "__len__"))          # Expected: ABC False
print(copy.copy(s).abc)                      # Expected: ABC
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: touching self.<anything> inside __getattribute__ -> infinite recursion
class Bad:
    def __getattribute__(self, name: str):
        return self.__dict__[name]           # self.__dict__ calls __getattribute__ again
try:
    Bad().x
except RecursionError:
    print("RecursionError")                  # Output: RecursionError

# ✅ Correct: return object.__getattribute__(self, name)
```

---

## 🎯 Interview Tip (1 line)
Say: "Use `__getattr__` for lazy/dynamic attributes (proxies, wrappers); override `__getattribute__` only for intercepting everything, and delegate via `super()`."

---

## 🔗 Related Questions
→ Q162 (descriptors) | Q266 (proxy pattern) | Q191 (lazy loader) | Q177 (name mangling)
