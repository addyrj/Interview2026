---

# Q175. Explain Mutability and Hashability
# Category: Tricky Concepts
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Why can a tuple be a dict key but a list cannot? Why is `(1, [2, 3])` unhashable? What happens if you define `__eq__` without `__hash__`?

---

## 💡 Quick Concept (2 lines only)
Hashable = has a stable `__hash__` consistent with `__eq__`; dict/set keys must be hashable. Mutable built-ins (list, dict, set) are not; a tuple is hashable only if all its items are.
हिंदी: Dict key वही बन सकता है जिसका hash कभी न बदले — इसलिए list नहीं, tuple (सिर्फ immutable items के साथ) चलता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
t = (1, 2, 3)                                # Step 1: immutable tuple
d = {t: "ok"}                                # usable as key
print(d[(1, 2, 3)], hash(t) == hash((1, 2, 3)))  # Expected: ok True
try:
    {[1, 2]: "x"}                            # Step 2: list key
except TypeError as e:
    print("TypeError:", e)                   # Expected: TypeError: unhashable type: 'list'
t2 = (1, [2, 3])                             # tuple holding a mutable item
try:
    hash(t2)                                 # hash needs hash of every item
except TypeError as e:
    print("TypeError:", e)                   # Expected: TypeError: unhashable type: 'list'
t2[1].append(4)                              # tuple is "immutable" but its list item isn't
print(t2)                                    # Expected: (1, [2, 3, 4])

# ============================================
# TEST CASES — mutation vs rebinding, __eq__/__hash__
# ============================================
lst = [1]                                    # list: += mutates in place
before = id(lst)
lst += [2]
print(id(lst) == before)                     # Expected: True
tup = (1,)                                   # tuple: += builds a new object
before = id(tup)
tup += (2,)
print(id(tup) == before, tup)                # Expected: False (1, 2)

class P:                                     # defines __eq__ only
    def __init__(self, v: int) -> None:
        self.v = v                           # state
    def __eq__(self, o: object) -> bool:
        return isinstance(o, P) and self.v == o.v   # value equality
print(P.__hash__)                            # Expected: None  (Python sets __hash__ = None)
try:
    {P(1)}                                   # not hashable now
except TypeError as e:
    print("TypeError:", e)                   # Expected: TypeError: unhashable type: 'P'

class H(P):                                  # add __hash__ consistent with __eq__
    def __hash__(self) -> int:
        return hash(self.v)                  # equal objects -> equal hash
print(len({H(1), H(1)}))                     # Expected: 1
```

---

## 🔍 Why This Works (3 lines max)
Sets/dicts find items by hash, so a key's hash must never change while stored — hence mutable containers refuse to hash. Defining `__eq__` alone sets `__hash__` to `None`; equal objects must also have equal hashes.
हिंदी: Hash बदल जाए तो dict में key खो जाती है, इसलिए mutable unhashable हैं; सिर्फ `__eq__` लिखने से `__hash__` None हो जाता है।

---

## ⚡ Alternative Solution
```python
fs = frozenset({1, 2})                       # immutable set is hashable
print({fs: "set key"}[frozenset([2, 1])])    # Expected: set key
print(hash(1) == hash(1.0) == hash(True))    # Expected: True (1 == 1.0 == True, so same dict key)
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: hashing on a field you later mutate -> object is "lost" in the set
class Key:
    def __init__(self, v: int) -> None:
        self.v = v                           # mutable field
    def __eq__(self, o: object) -> bool:
        return isinstance(o, Key) and self.v == o.v
    def __hash__(self) -> int:
        return hash(self.v)                  # hash depends on mutable state
k = Key(1)
bucket = {k}                                 # stored under hash(1)
k.v = 2                                      # mutate after insertion
print(k in bucket, Key(2) in bucket, Key(1) in bucket, len(bucket))  # Output: False False False 1

# ✅ Correct: hash only immutable fields (frozen dataclass / NamedTuple)
```

---

## 🎯 Interview Tip (1 line)
Say: "Hashable means immutable-in-spirit: `__hash__` must be stable and match `__eq__`; `@dataclass(frozen=True)` gives you both."

---

## 🔗 Related Questions
→ Q034 (__eq__ without __hash__) | Q134 (fix __eq__ without __hash__) | Q292 (mutable vs immutable) | Q012 (dict key collision)
