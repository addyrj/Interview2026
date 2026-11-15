---

# Q133. Fix Circular Import Bug
# Category: Fix the Bug
# Difficulty: ⭐⭐⭐ Hard

---

## ❓ Question
Importing `models_user` crashes with `ImportError: cannot import name 'User' from 'models_user'`. `User` creates `Order`s and `Order` stores its owner `User`. Find and fix the bug.

```python
# --- file: models_user.py (BUGGY) ---
from models_order import Order        # runs models_order.py first

class User:
    def __init__(self, name: str) -> None:
        self.name = name              # store the name
    def make_order(self, item: str) -> "Order":
        return Order(item, self)      # create an order for this user

# --- file: models_order.py (BUGGY) ---
from models_user import User          # models_user is only HALF loaded -> no User yet

class Order:
    def __init__(self, item: str, owner: User) -> None:
        self.item = item              # product name
        self.owner = owner            # the user who ordered

# --- file: main_bad.py ---
from models_user import User          # ImportError
```

---

## 💡 Quick Concept (2 lines only)
`from a import X` runs module `a` top to bottom. If `a` imports `b` and `b` imports `a`, one of them is only half-initialised and `X` doesn't exist yet. Break the cycle: lazy import inside the function, `TYPE_CHECKING` import for type hints, or restructure.
हिंदी: दो modules एक-दूसरे को top पर import करें तो एक आधा load होता है — import को function के अंदर ले जाओ।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION  (3 files in the same folder)
# ============================================

# --- file: models_user.py (FIXED) ---
from __future__ import annotations         # type hints are not evaluated at runtime
from typing import TYPE_CHECKING           # flag that is False at runtime

if TYPE_CHECKING:                          # only type checkers (mypy/pyright) enter here
    from models_order import Order         # no runtime import -> no cycle

class User:
    def __init__(self, name: str) -> None:
        self.name = name                   # store the name
    def make_order(self, item: str) -> Order:
        from models_order import Order     # Step 1: lazy import at CALL time (both modules loaded by then)
        return Order(item, self)           # create the order

# --- file: models_order.py (FIXED) ---
from __future__ import annotations         # postponed annotations
from models_user import User               # safe: models_user no longer imports us at top

class Order:
    def __init__(self, item: str, owner: User) -> None:
        self.item = item                   # product name
        self.owner = owner                 # owning user

# --- file: main.py ---
from models_user import User               # works now

# ============================================
# TEST CASES
# ============================================
o = User("Aditya").make_order("book")      # create user then order
print(o.item, o.owner.name)                # Expected: book Aditya

# Before the fix (main_bad.py), the traceback ends with:
# ImportError: cannot import name 'User' from 'models_user' (consider renaming ... )
```

---

## 🔍 Why This Works (3 lines max)
Python registers a module in `sys.modules` BEFORE finishing execution, so a cyclic `from x import Name` sees a partially built module without `Name`. The lazy import runs after both modules are fully loaded, and `TYPE_CHECKING` keeps type hints without a runtime import. The best long-term fix is a design change (extract shared code to a third module).
हिंदी: cycle में module आधा बना होता है — import को use के समय (function में) करो।

---

## ⚡ Alternative Solution
```python
# Alternative: import the MODULE (not the name) and use attribute access later

# --- file: a.py ---
import b                                  # module import: nothing is looked up yet
def fa() -> str:
    return "A" + b.fb_name()              # b.fb_name resolved at call time
def fa_name() -> str:
    return "a"                            # simple helper

# --- file: b.py ---
import a                                  # cycle, but harmless with `import a`
def fb_name() -> str:
    return "b"                            # simple helper
def fb() -> str:
    return "B" + a.fa_name()              # a.fa_name resolved at call time

# --- file: main.py ---
import a, b                               # both import fine
print(a.fa(), b.fb())                     # Output: Ab Ba

# Best fix: move the shared piece into a third module (e.g. types.py) that both import.
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: "fixing" by shuffling import order or wrapping in try/except ImportError
try:
    from models_order import Order        # may fail depending on who imported first
except ImportError:
    Order = None                          # hides the design problem, fails later with NoneType error

# ✅ Correct: break the cycle (lazy import / TYPE_CHECKING / third module)
```

---

## 🎯 Interview Tip (1 line)
Say: "A circular import means my dependency graph has a cycle — I fix the design first (extract a shared module), and otherwise use `TYPE_CHECKING` for hints and a lazy import inside the function."

---

## 🔗 Related Questions
→ Q041 (LEGB scope) | Q191 (build lazy loader) | Q247 (typing: Protocol, TypedDict, Literal) | Q308 (if __name__ == '__main__')
