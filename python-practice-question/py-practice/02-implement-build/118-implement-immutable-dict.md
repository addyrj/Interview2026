---

# Q118. Implement immutable dict
# Category: IMPLEMENT / BUILD
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement `FrozenDict`: a read-only mapping that behaves like a dict for reading, rejects any modification, is hashable (usable as a dict key), and supports a `.set(k, v)` that returns a NEW FrozenDict.

```python
fd = FrozenDict(a=1, b=2)
fd["c"] = 3   # TypeError
```

---

## 💡 Quick Concept (2 lines only)
Subclass `collections.abc.Mapping` (read-only interface), keep data private, never define `__setitem__`, and hash the frozenset of items.
हिंदी: Mapping से inherit करो, `__setitem__` मत बनाओ, और hash के लिए items का frozenset लो।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Mapping                     # read-only dict interface
from typing import Any, Iterator                        # type hints

class FrozenDict(Mapping):
    __slots__ = ("_data", "_hash")                      # no instance __dict__ -> fewer back doors

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", dict(*args, **kwargs))  # private copy of the data
        object.__setattr__(self, "_hash", None)         # lazy hash cache

    def __getitem__(self, key: Any) -> Any:
        return self._data[key]                          # read access

    def __iter__(self) -> Iterator:
        return iter(self._data)                         # iterate keys

    def __len__(self) -> int:
        return len(self._data)                          # size

    def __hash__(self) -> int:
        if self._hash is None:                          # compute once
            object.__setattr__(self, "_hash", hash(frozenset(self._data.items())))
        return self._hash                               # usable as dict key / set member

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("FrozenDict is immutable") # block attribute writes

    def __repr__(self) -> str:
        return f"FrozenDict({self._data!r})"            # readable repr

    def set(self, key: Any, value: Any) -> "FrozenDict":
        return FrozenDict({**self._data, key: value})   # "modify" = return a new copy

# ============================================
# TEST CASES
# ============================================
fd = FrozenDict(a=1, b=2)
print(fd, fd["a"], len(fd), list(fd))     # Expected: FrozenDict({'a': 1, 'b': 2}) 1 2 ['a', 'b']
try:
    fd["c"] = 3                           # no __setitem__
except TypeError as e:
    print("TypeError:", e)                # Expected: TypeError: 'FrozenDict' object does not support item assignment
try:
    fd.x = 1                              # blocked by __setattr__
except AttributeError as e:
    print("AttributeError:", e)           # Expected: AttributeError: FrozenDict is immutable
print(fd.set("c", 3), fd)                 # Expected: FrozenDict({'a': 1, 'b': 2, 'c': 3}) FrozenDict({'a': 1, 'b': 2})
print(fd == {"a": 1, "b": 2})             # Expected: True  (Mapping provides __eq__)
print({fd: "works as key"}[FrozenDict(a=1, b=2)])   # Expected: works as key
print(hash(fd) == hash(FrozenDict(b=2, a=1)))       # Expected: True  (order-independent)
```

---

## 🔍 Why This Works (3 lines max)
`Mapping` supplies `get`, `items`, `==` etc. from just `__getitem__/__iter__/__len__`, and with no `__setitem__` writes fail naturally. `frozenset(items)` gives an order-independent hash, equal dicts hash equally.
हिंदी: `Mapping` सिर्फ read methods देता है, इसलिए write अपने-आप fail होता है।

---

## ⚡ Alternative Solution
```python
# Built-in: types.MappingProxyType — a read-only VIEW (not a copy, not hashable)
from types import MappingProxyType                      # stdlib
d = {"a": 1}                                            # underlying dict
proxy = MappingProxyType(d)                             # read-only view
try:
    proxy["b"] = 2                                      # write through the view
except TypeError as e:
    print("TypeError:", e)                              # Output: TypeError: 'mappingproxy' object does not support item assignment
d["b"] = 2                                              # original can still change!
print(proxy)                                            # Output: {'a': 1, 'b': 2}
try: hash(proxy)                                        # views of dicts are unhashable
except TypeError as e: print("TypeError:", e)           # Output: TypeError: unhashable type: 'dict'
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: assuming "frozen" means deeply immutable — values can still be mutable
fz = FrozenDict({"a": [1]})
fz["a"].append(2)                     # list inside is still mutable
print(fz)                             # Output: FrozenDict({'a': [1, 2]})
try:
    hash(fz)                          # and hashing breaks
except TypeError as e:
    print("TypeError:", e)            # Output: TypeError: unhashable type: 'list'

# ✅ Correct: store immutable values (tuples, frozensets, other FrozenDicts)
```

---

## 🎯 Interview Tip (1 line)
Say: "Mapping ABC + no setters + hash of frozenset(items); it's shallowly immutable, and MappingProxyType is only a read-only view of a still-mutable dict."

---

## 🔗 Related Questions
→ Q175 (mutability and hashability) | Q292 (mutable vs immutable) | Q071 (deep clone a dict) | Q169 (__slots__)
