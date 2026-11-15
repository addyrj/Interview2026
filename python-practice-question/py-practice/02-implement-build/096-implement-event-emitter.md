---

# Q096. Implement Event Emitter
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement an `EventEmitter` class with `on(event, fn)`, `off(event, fn)`, `once(event, fn)` and `emit(event, *args)`. `emit` returns `True` if any listener ran. A `once` listener must run only one time, even if it is removed during `emit`.

```python
em.on("greet", greet); em.emit("greet", "Ada")   # hello Ada
```

---

## 💡 Quick Concept (2 lines only)
Store a list of callbacks per event name in a dict. `emit` calls each one; `once` wraps the callback so it removes itself before running.
हिंदी: Event emitter हर event के callbacks की list रखता है — emit पर सब call होते हैं।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import defaultdict  # auto-creating lists
from typing import Any, Callable  # type hints


class EventEmitter:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)  # Step 1: event -> callbacks

    def on(self, event: str, fn: Callable[..., Any]) -> "EventEmitter":
        self._listeners[event].append(fn)  # Step 2: register
        return self  # allow chaining: em.on(...).on(...)

    def off(self, event: str, fn: Callable[..., Any]) -> None:
        if fn in self._listeners.get(event, []):  # only if registered
            self._listeners[event].remove(fn)  # Step 3: unregister

    def once(self, event: str, fn: Callable[..., Any]) -> None:
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # Step 4: self-removing wrapper
            self.off(event, wrapper)  # remove first
            return fn(*args, **kwargs)  # then run original
        self.on(event, wrapper)  # register the wrapper

    def emit(self, event: str, *args: Any, **kwargs: Any) -> bool:
        listeners = list(self._listeners.get(event, []))  # Step 5: COPY so removals are safe
        for fn in listeners:
            fn(*args, **kwargs)  # call each listener
        return bool(listeners)  # True if anyone listened


# ============================================
# TEST CASES
# ============================================
em = EventEmitter()  # create emitter


def greet(name: str) -> None:  # normal listener
    print(f"hello {name}")  # output


em.on("greet", greet)  # permanent listener
em.once("greet", lambda n: print(f"first time only: {n}"))  # one-shot listener
print(em.emit("greet", "Ada"))  # Expected: hello Ada / first time only: Ada / True
print(em.emit("greet", "Bob"))  # Expected: hello Bob / True
em.off("greet", greet)  # remove listener
print(em.emit("greet", "Cy"))  # Expected: False
print(em.emit("nothing"))  # Expected: False
```

---

## 🔍 Why This Works (3 lines max)
A dict of lists maps each event to its callbacks. `emit` iterates over a **copy**, so `once` wrappers can remove themselves without skipping other listeners.
हिंदी: emit में list की copy पर loop करते हैं, ताकि बीच में हटाने से कोई listener skip न हो।

---

## ⚡ Alternative Solution
```python
class Mini:  # minimal version using setdefault
    def __init__(self):
        self.h = {}  # event -> list
    def on(self, e, f):
        self.h.setdefault(e, []).append(f)  # register
    def emit(self, e, *a):
        [f(*a) for f in self.h.get(e, [])]  # call all


m = Mini()
m.on("x", print)  # use print as listener
m.emit("x", 1, 2)  # Expected: 1 2
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: iterating the live list while a once-listener removes itself
class Bad(EventEmitter):
    def emit(self, event, *a):
        for fn in self._listeners[event]:  # ❌ list mutated during iteration
            fn(*a)

b = Bad()
b.once("x", lambda: print("A"))
b.on("x", lambda: print("B"))
b.emit("x")  # A          <- "B" was SKIPPED
b.emit("x")  # B

# ✅ Correct: loop over list(self._listeners[event])
```

---

## 🎯 Interview Tip (1 line)
Say: "Dict of lists, emit over a copy, once via a self-removing wrapper — then mention error isolation and async listeners as extensions."

---

## 🔗 Related Questions
→ Q097 (pub/sub) | Q098 (observable) | Q187 (event bus) | Q263 (observer pattern) | Q126 (mutating list while iterating)
