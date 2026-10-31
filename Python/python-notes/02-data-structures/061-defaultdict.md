---

# 061. defaultdict
# हिंदी में: defaultdict (अपने-आप default value वाला dict)

---

## 🔵 Simple Definition (English)
`defaultdict` is a dict from the `collections` module that creates a default value automatically when you access a missing key. You give it a factory (like `list`, `int`, `set`) and it calls that factory to make the value. No `KeyError`, no `if key in d` checks.

## 🔵 सरल परिभाषा (Hindi)
`defaultdict` `collections` module का dict है जो missing key access करने पर default value अपने-आप बना देता है। आप factory देते हैं (जैसे `list`, `int`, `set`), और वह value बनाती है। `KeyError` नहीं, `if key in d` check नहीं।

---

## 🔴 Problem it Solves
Grouping and counting with a normal dict needs boilerplate: check if the key exists, create an empty list or 0, then update. Forget the check and you get `KeyError`. `defaultdict` removes that boilerplate, making grouping (`d[k].append(x)`) and counting (`d[k] += 1`) one-liners.

## 🔴 यह क्यों बना? (Hindi)
Normal dict से group/count करने में boilerplate लगता है: key check करो, खाली list या 0 बनाओ, फिर update। Check भूले तो `KeyError`। `defaultdict` यह सब हटा देता है: `d[k].append(x)` और `d[k] += 1` सीधे चलते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → d = defaultdict(list)       → stores list as default_factory
Step 2 → d["a"]  (key missing)       → dict calls __missing__("a")
Step 3 → __missing__ calls list()    → creates [] and stores it as d["a"]
Step 4 → d["a"].append(1)            → works on the new list
Step 5 → d["a"]  (key exists)        → normal lookup; factory NOT called
Step 6 → d.get("zzz")                → get() does NOT trigger the factory (returns None)
```

## 🟢 कैसे काम करता है? (Hindi)
```
defaultdict(list) → factory = list
d["a"] (नहीं है) → __missing__ चलता है → list() से [] बनता है और store होता है
d["a"] (है) → normal lookup, factory नहीं चलती
d.get("x") → factory trigger नहीं करता
```

---

## 🟡 Real World Example
Swiggy analytics: group orders by city → `orders_by_city[order.city].append(order)`. Count orders per restaurant → `defaultdict(int)`. Build an unique-customers-per-day map → `defaultdict(set)`. In a FastAPI background job, you aggregate millions of log lines into per-endpoint counters with `defaultdict(int)`.

## 🟡 Real Example Hindi mein
Swiggy analytics में city के हिसाब से orders group: `orders_by_city[order.city].append(order)`। हर restaurant के orders गिनना: `defaultdict(int)`। रोज़ के unique customers: `defaultdict(set)`। FastAPI background job में logs को per-endpoint counters में `defaultdict(int)` से aggregate करते हैं।

---

## 💻 Code Example — Basic
```python
# Basic: defaultdict with list, int and set
from collections import defaultdict          # import the class

# 1. Grouping with list
groups: defaultdict[str, list[str]] = defaultdict(list)   # missing key -> []
for word in ["apple", "avocado", "banana"]:  # sample words
    groups[word[0]].append(word)             # no key check needed
print(dict(groups))                          # Output: {'a': ['apple', 'avocado'], 'b': ['banana']}

# 2. Counting with int
counts: defaultdict[str, int] = defaultdict(int)          # missing key -> 0
for ch in "hello":                           # count letters
    counts[ch] += 1                          # starts from 0 automatically
print(dict(counts))                          # Output: {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# 3. Unique values with set
tags: defaultdict[str, set[str]] = defaultdict(set)       # missing key -> set()
tags["post1"].add("python")                  # add tag
tags["post1"].add("python")                  # duplicate ignored
tags["post1"].add("fastapi")                 # second tag
print(sorted(tags["post1"]))                 # Output: ['fastapi', 'python']

# 4. Reading a missing key CREATES it (important!)
d: defaultdict[str, int] = defaultdict(int)  # empty
print(d["x"])                                # Output: 0
print("x" in d)                              # Output: True  (key was inserted by the read)
print(d.get("y"))                            # Output: None  (get does not create)
print("y" in d)                              # Output: False

# 5. Factory is stored here
print(d.default_factory)                     # Output: <class 'int'>
```

## 💻 Code Example — Advanced
```python
# Advanced: nested defaultdict, custom factory, lambda trap and safe conversion
from __future__ import annotations           # modern hints
from collections import defaultdict          # main class
from typing import Callable                  # factory type


def tree() -> defaultdict:
    """Recursive factory: every missing key becomes another tree."""
    return defaultdict(tree)                 # factory returns a new defaultdict using itself


# 1. Auto-vivifying nested dict (no need to create levels manually)
config = tree()                              # root
config["db"]["host"] = "localhost"           # 'db' created automatically
config["db"]["port"] = 5432                  # reuse same 'db' level
config["cache"]["ttl"] = 60                  # another branch
print(config["db"]["host"], config["cache"]["ttl"])   # Output: localhost 60


def to_plain(d: object) -> object:
    """Convert nested defaultdicts to normal dicts (needed for JSON/FastAPI)."""
    if isinstance(d, defaultdict):           # nested defaultdict found
        return {k: to_plain(v) for k, v in d.items()}   # convert recursively
    return d                                 # leaf value


print(to_plain(config))                      # Output: {'db': {'host': 'localhost', 'port': 5432}, 'cache': {'ttl': 60}}

# 2. Custom default via lambda (non-empty default)
scores: defaultdict[str, int] = defaultdict(lambda: 100)   # every new key starts at 100
scores["bob"] -= 10                          # 100 - 10
print(scores["bob"], scores["alice"])        # Output: 90 100

# 3. Aggregate log lines per endpoint: count and total latency
Log = tuple[str, float]                      # (endpoint, latency_ms)
logs: list[Log] = [("/users", 12.0), ("/users", 8.0), ("/orders", 30.0)]
count: defaultdict[str, int] = defaultdict(int)       # hits per endpoint
total: defaultdict[str, float] = defaultdict(float)   # time per endpoint (float() == 0.0)
for endpoint, ms in logs:                    # walk logs
    count[endpoint] += 1                     # increment hits
    total[endpoint] += ms                    # add latency
avg: dict[str, float] = {e: total[e] / count[e] for e in count}   # average latency
print(avg)                                   # Output: {'/users': 10.0, '/orders': 30.0}

# 4. Without a factory it behaves like a normal dict
plain: defaultdict[str, int] = defaultdict()           # default_factory=None
try:                                         # missing key
    plain["missing"]                         # KeyError as in normal dict
except KeyError as err:                      # handle it
    print("KeyError:", err)                  # Output: KeyError: 'missing'

# 5. Converting back: dict(dd) stops auto-creation
safe: dict[str, int] = dict(count)           # now a normal dict
print(safe.get("/nope", 0))                  # Output: 0
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
from collections import defaultdict
groups = defaultdict(list)
for w in ["apple", "avocado", "banana"]:
    groups[w[0]].append(w)           # no existence check
```

```javascript
// JavaScript
const groups = {};
for (const w of ["apple", "avocado", "banana"]) {
  (groups[w[0]] ??= []).push(w);     // must write the default yourself (?? = operator)
  // older style: if (!groups[w[0]]) groups[w[0]] = [];
}
// Map version: if (!m.has(k)) m.set(k, []); m.get(k).push(w);
```

Key difference: JS has no built-in default-value dictionary; you repeat the "create if missing" step each time. Python's `defaultdict` bakes it in. FastAPI link: `defaultdict` is a normal `dict` subclass, so FastAPI can serialize it, but convert nested ones with `dict()` / a helper to keep the OpenAPI response clean and avoid accidental key creation.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing a value instead of a factory
```python
# Wrong:
# d = defaultdict([])        # TypeError: first argument must be callable or None
# Correct:
d = defaultdict(list)        # pass the callable, not an instance
```

❌ Mistake 2: Accidentally creating keys by reading
```python
d = defaultdict(int)
if d["user"] > 0:            # Wrong: this INSERTS "user": 0 as a side effect
    pass
# Correct: check without creating
if d.get("user", 0) > 0:
    pass
```

❌ Mistake 3: Using one shared mutable default
```python
# Wrong idea: lambda: shared_list   -> every key shares the SAME list
# Correct: defaultdict(list)        -> a NEW list for every key
```

---

## 🧠 Tricky Interview Question

**Q**: "`d = defaultdict(list)`. After `d['a']` and `d.get('b')`, what does `len(d)` return? Also, does `'c' in d` create 'c'?"

**Answer**: `len(d)` is `1`. Subscript `d['a']` calls `__missing__` and inserts `'a': []`. `d.get('b')` does not call `__missing__`; it returns `None` and inserts nothing. `'c' in d` is a membership test and also does not create the key; it returns `False`. Only `d[key]` (`__getitem__`) triggers the default factory.

---

## ⚫ Interview Questions + Answers

Q1: What is defaultdict and how is it different from dict?
A1: `defaultdict` is a dict subclass with a `default_factory`. On `d[missing]`, it calls the factory with no arguments, stores the result under that key and returns it. A normal dict raises `KeyError`. Everything else (ordering, methods, JSON conversion) is the same as dict.

Q2: How does it work internally?
A2: Normal `dict.__getitem__` calls `__missing__(key)` when a key is not found. A normal dict does not define it, so `KeyError` is raised. `defaultdict` defines `__missing__`, which runs `default_factory()`, stores it, and returns it. If `default_factory` is `None`, it raises `KeyError`.

Q3: Which factories are common?
A3: `list` (grouping), `int` (counting, default 0), `float` (sums, 0.0), `set` (unique collection), `dict` (two-level maps), `lambda: value` (custom default), and a recursive function for infinite nesting. Any no-argument callable works.

Q4: defaultdict vs `dict.setdefault` vs `Counter`?
A4: `setdefault(k, [])` creates a new empty list every call even if the key exists (wasted work) and is more verbose. `defaultdict(list)` creates only when needed. For pure counting, `Counter` is better since it has `most_common()` and arithmetic. Use defaultdict for grouping and custom aggregation.

Q5: Does `d.get(key)` or `key in d` trigger the factory?
A5: No. Only `d[key]` does. So you can safely check with `in` or `get`. This is also the usual source of bugs: a read like `if d[key]:` silently inserts the key and grows the dict.

---

## 🔷 When to Use defaultdict

✅ Use when:
- Grouping items by key (`list`)
- Counting or summing (`int`, `float`)
- Collecting unique values per key (`set`)
- Building nested structures

❌ Avoid when:
- Missing key should be an error (use plain dict)
- Pure counting where `Counter` fits
- Returning to clients as-is (convert to dict first)

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| default_factory | Callable that makes the default | Default बनाने वाली callable |
| `__missing__` | Hook called when key not found | Key न मिलने पर चलने वाला hook |
| Grouping | Collect items under a key | Key के नीचे items इकट्ठा करना |
| Auto-vivification | Nested levels created on access | Access पर nested levels अपने-आप बनना |
| Side effect | Unexpected change by reading | Read से अनचाहा बदलाव |
| Callable | Anything you can call like a function | जिसे function की तरह call कर सकें |

---

## ⚡ 3-Line Summary
English: `defaultdict(factory)` auto-creates a value for missing keys, perfect for grouping (`list`), counting (`int`) and unique sets (`set`). Only `d[key]` creates the key; `get` and `in` do not. Convert to a plain dict before returning it from an API.
Hindi: `defaultdict(factory)` missing key पर value अपने-आप बनाता है — grouping (`list`), counting (`int`), unique (`set`) के लिए बढ़िया। सिर्फ `d[key]` key बनाता है; `get` और `in` नहीं। API से लौटाने से पहले plain dict में बदलें।

---

## ➡️ Next Topic
**062. OrderedDict** — dict with order-aware features: `move_to_end`, `popitem(last=False)`, LRU cache idea.
