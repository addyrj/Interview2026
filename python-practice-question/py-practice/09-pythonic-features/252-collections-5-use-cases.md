---

# Q252. collections — 5 Use Cases
# Category: Pythonic + Modern Python Features
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Show 5 `collections` tools: `Counter`, `defaultdict`, `deque`, `namedtuple`, and `ChainMap` (also `OrderedDict`).

---

## 💡 Quick Concept (2 lines only)
`collections` has specialised containers: `Counter` counts, `defaultdict` auto-creates values, `deque` is a fast two-ended queue, `namedtuple` gives names to tuple fields.
हिंदी: collections = खास containers — गिनती के लिए Counter, auto-default के लिए defaultdict, fast queue के लिए deque।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections import ChainMap, Counter, defaultdict, deque, namedtuple  # Step 1: imports

c = Counter("mississippi")                            # Use case 1: count items
print(c)                                              # Expected: Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
print(c.most_common(2))                               # Expected: [('i', 4), ('s', 4)]
print(c["z"])                                         # Expected: 0  (missing -> 0, no KeyError)

groups: defaultdict[int, list[str]] = defaultdict(list)  # Use case 2: default = empty list
for w in ["a", "bb", "cc", "d"]:                      # group words by length
    groups[len(w)].append(w)                          # no key check needed
print(dict(groups))                                   # Expected: {1: ['a', 'd'], 2: ['bb', 'cc']}

dq: deque[int] = deque([1, 2, 3], maxlen=3)           # Use case 3: O(1) at both ends, bounded
dq.append(4)                                          # right add -> drops 1 from left
dq.appendleft(0)                                      # left add  -> drops 4 from right
print(dq)                                             # Expected: deque([0, 2, 3], maxlen=3)
print(dq.popleft(), dq.pop())                         # Expected: 0 3

Point = namedtuple("Point", ["x", "y"])               # Use case 4: tuple with field names
p = Point(1, 2)                                       # create
print(p, p.x, p[1], p._asdict())                      # Expected: Point(x=1, y=2) 1 2 {'x': 1, 'y': 2}

defaults = {"theme": "light", "lang": "en"}           # Use case 5: layered config
user = {"theme": "dark"}                              # overrides
cfg = ChainMap(user, defaults)                        # lookup: user first, then defaults
print(cfg["theme"], cfg["lang"])                      # Expected: dark en

# ============================================
# TEST CASES
# ============================================
print(Counter("aab") + Counter("bc"))                 # Expected: Counter({'b': 2, 'a': 2, 'c': 1})
print(Counter("aab") - Counter("a"))                  # Expected: Counter({'a': 1, 'b': 1})
d = defaultdict(int)                                  # default int -> 0
d["x"] += 1                                           # works without initialising
print(dict(d))                                        # Expected: {'x': 1}
```

---

## 🔍 Why This Works (3 lines max)
`defaultdict` calls its factory on a missing key; `deque` is a doubly-linked block list so both ends are O(1) (a list's `pop(0)` is O(n)); `ChainMap` searches maps in order without copying them.
हिंदी: defaultdict missing key पर factory चलाता है — deque दोनों सिरों पर O(1) है, list का `pop(0)` O(n)।

---

## ⚡ Alternative Solution
```python
# Same counting/grouping with plain dicts (more code)
counts: dict[str, int] = {}                           # manual counter
for ch in "mississippi":                              # loop over characters
    counts[ch] = counts.get(ch, 0) + 1                # get with default 0
print(counts)                                         # Expected: {'m': 1, 'i': 4, 's': 4, 'p': 2}

groups: dict[int, list[str]] = {}                     # manual grouping
for w in ["a", "bb", "cc", "d"]:                      # loop
    groups.setdefault(len(w), []).append(w)           # setdefault = defaultdict-lite
print(groups)                                         # Expected: {1: ['a', 'd'], 2: ['bb', 'cc']}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: reading a missing key on defaultdict CREATES it
from collections import defaultdict                   # import
d = defaultdict(list)                                 # default list
_ = d["missing"]                                      # just reading...
print(dict(d))                                        # Expected: {'missing': []}  (key was inserted!)

# ✅ Correct: use `in` or d.get("missing") to check without creating
print(d.get("other"), "other" in d)                   # Expected: None False
```

---

## 🎯 Interview Tip (1 line)
Say: "Counter for frequencies, defaultdict(list) for grouping, deque for queues/sliding windows (O(1) popleft), namedtuple/dataclass for light records."

---

## 🔗 Related Questions
→ Q066 (count occurrences) | Q064 (group list by key) | Q101 (implement queue) | Q099 (LRU cache)
