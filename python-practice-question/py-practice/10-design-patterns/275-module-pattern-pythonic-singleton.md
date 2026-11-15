---

# Q275. Module Pattern (Pythonic Singleton)
# Category: Design Patterns
# Difficulty: ⭐ Easy

---

## ❓ Question
Python modules are imported only once, so a module is a natural singleton. Show a `config` "module" that holds shared state, and prove that two importers see the same object. Compare with a class-based singleton.

---

## 💡 Quick Concept (2 lines only)
The first `import` runs the module and caches it in `sys.modules`; later imports return the same object. So module-level variables are shared singletons — no class needed.
हिंदी: Module सिर्फ एक बार चलता है और `sys.modules` में cache होता है, इसलिए module-level variable अपने आप singleton है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
import sys  # Step 1: sys.modules is the import cache
import types  # to build a module object in memory

# Step 2: simulate a file "config.py" with module-level state
config = types.ModuleType("config")  # an empty module object
config.DEBUG = False  # shared setting
config.settings = {"db": "sqlite"}  # shared mutable state


def set_debug(value: bool) -> None:
    config.DEBUG = value  # helper that mutates the shared module


config.set_debug = set_debug  # attach function to the module
sys.modules["config"] = config  # Step 3: register in the import cache

# ============================================
# TEST CASES
# ============================================
import config as a  # first importer - gets the cached module
import config as b  # second importer - same cached module
print(a is b)  # Expected: True
a.set_debug(True)  # one place changes the state
print(b.DEBUG)  # Expected: True  (the other sees it)
b.settings["db"] = "postgres"  # mutate shared dict
print(a.settings)  # Expected: {'db': 'postgres'}
```

---

## 🔍 Why This Works (3 lines max)
`import` first looks in `sys.modules`; if found, it returns that same object without re-running the code. Every importer therefore shares one instance. (Real code: just put the variables in `config.py`.)
हिंदी: `import` पहले `sys.modules` देखता है; मिल जाए तो वही object मिलता है, इसलिए सब जगह एक ही instance रहता है।

---

## ⚡ Alternative Solution
```python
# Class-based singleton with __new__ (more code, same result)
class Settings:
    _instance: "Settings | None" = None  # holds the single instance

    def __new__(cls) -> "Settings":
        if cls._instance is None:  # first call creates it
            cls._instance = super().__new__(cls)  # allocate object
            cls._instance.debug = False  # init state once
        return cls._instance  # later calls reuse it


s1, s2 = Settings(), Settings()  # two "constructions"
s1.debug = True  # change via one name
print(s1 is s2, s2.debug)  # Expected: True True
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: `from config import DEBUG` copies the VALUE (name binding) at import time
import sys, types  # build a tiny module again
m = types.ModuleType("cfg")
m.DEBUG = False
sys.modules["cfg"] = m

from cfg import DEBUG  # DEBUG is now a separate name bound to False
m.DEBUG = True  # change the module attribute
print(DEBUG)  # Output: False   <- stale copy
print(m.DEBUG)  # Output: True

# ✅ Correct: `import cfg` and read `cfg.DEBUG` each time
```

---

## 🎯 Interview Tip (1 line)
Say: "In Python the simplest singleton is a module; use `__new__`/metaclass only if you need lazy creation, and remember tests need a way to reset it."

---

## 🔗 Related Questions
→ Q261 (singleton) | Q030 (`__init__` vs `__new__`) | Q133 (circular import)
