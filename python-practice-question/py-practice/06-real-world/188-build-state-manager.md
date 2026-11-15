---

# Q188. Build State Manager
# Category: Real World Problems
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Build a tiny Redux-style `Store(reducer, initial)` with `get_state()`, `dispatch(action)` and `subscribe(fn)`. State must never be mutated in place, and subscribers are notified only when the state actually changes.

```python
store.dispatch({"type": "inc"})   # subscribers get {'count': 1}
```

---

## 💡 Quick Concept (2 lines only)
A pure reducer `(state, action) -> new_state` plus a list of subscribers. Returning the same object means "no change", so nobody is notified.
हिंदी: Reducer पुराने state से नया state बनाता है (mutate नहीं); state बदला तभी subscribers को खबर मिलती है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from typing import Any, Callable  # type hints

class Store:
    def __init__(self, reducer: Callable[[Any, dict], Any], initial: Any) -> None:
        self._reducer = reducer  # pure function (state, action) -> new state
        self._state = initial  # current state
        self._subs: list[Callable[[Any], None]] = []  # subscribers

    def get_state(self) -> Any:
        return self._state  # read-only access

    def dispatch(self, action: dict) -> None:
        new = self._reducer(self._state, action)  # compute next state
        if new is not self._state:  # only notify on change
            self._state = new  # commit
            for s in list(self._subs):
                s(new)  # notify subscribers

    def subscribe(self, fn: Callable[[Any], None]) -> Callable[[], None]:
        self._subs.append(fn)  # add
        return lambda: self._subs.remove(fn)  # unsubscribe handle

def reducer(state: dict, action: dict) -> dict:
    match action["type"]:  # pattern match on action type
        case "inc":
            return {**state, "count": state["count"] + action.get("by", 1)}  # new dict, never mutate
        case "reset":
            return {**state, "count": 0}  # reset
        case _:
            return state  # unknown -> same object (no notify)

# ============================================
# TEST CASES
# ============================================
store = Store(reducer, {"count": 0})  # initial state
unsub = store.subscribe(lambda s: print("state ->", s))  # log changes
store.dispatch({"type": "inc"})  # Expected: state -> {'count': 1}
store.dispatch({"type": "inc", "by": 5})  # Expected: state -> {'count': 6}
store.dispatch({"type": "noop"})  # Expected: (no output)
unsub()  # stop listening
store.dispatch({"type": "reset"})  # Expected: (no output, unsubscribed)
print(store.get_state())  # Expected: {'count': 0}
```

---

## 🔍 Why This Works (3 lines max)
The reducer builds a new dict with `{**state, ...}`, so old states stay valid (great for undo/time-travel). The `is not` identity check is a cheap "did anything change" test. `match/case` keeps action routing readable.
हिंदी: `{**state}` से नया dict बनता है, पुराना सुरक्षित रहता है; `is not` से बदलाव का सस्ता check होता है।

---

## ⚡ Alternative Solution
```python
from dataclasses import dataclass, replace  # immutable updates

@dataclass(frozen=True)  # instances cannot be modified
class State:
    count: int = 0  # counter
    items: tuple[str, ...] = ()  # immutable list

s0 = State()  # initial
s1 = replace(s0, count=s0.count + 1)  # copy with change
s2 = replace(s1, items=(*s1.items, "a"))  # append immutably
print(s0, s1, s2, sep="\n")  # Expected: State(count=0, items=()) / State(count=1, items=()) / State(count=1, items=('a',))
try:
    s2.count = 9  # mutation blocked
except Exception as e:
    print(type(e).__name__)  # Expected: FrozenInstanceError
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: mutating state in the reducer -> old and new are the same object, so no notification (not run)
# def reducer(state, action):
#     state["count"] += 1      # mutates in place
#     return state             # `new is self._state` -> subscribers never called

# ✅ Correct: return a NEW object ({**state, "count": ...} or dataclasses.replace)
```

---

## 🎯 Interview Tip (1 line)
Say: "Single source of truth, pure reducers, immutable updates, subscribe/unsubscribe — the same idea as Redux."

---

## 🔗 Related Questions
→ Q187 (event bus) | Q200 (undo/redo system) | Q246 (dataclasses) | Q245 (match/case)
