---

# 457. Flatten Nested List
# हिंदी में: Nested List को सपाट (flat) करना

Runnable solution with asserts: `main.py` in this folder (`python3 main.py` prints `flat: [1, 2, 3, 4, 5, 6, 7, 'ab']` and `All flatten tests passed`, verified on Python 3.13.3).

---

## 🔵 Simple Definition (English)
Flattening turns a list that contains lists (to any depth) into one single-level list: `[1, [2, [3]]]` becomes `[1, 2, 3]`. Common solutions are recursion, a generator with `yield from`, or an explicit stack.

## 🔵 सरल परिभाषा (Hindi)
Flatten करना यानी list के अंदर list (किसी भी गहराई तक) को एक ही level की list बनाना: `[1, [2, [3]]]` से `[1, 2, 3]`। आम हल हैं recursion, `yield from` वाला generator, या explicit stack।

---

## 🔴 Problem it Solves
Real data is often nested: JSON from an API, category trees, comment threads, directory listings. Many tools (pandas columns, CSV export, search indexing) need a flat sequence. Writing the traversal tests recursion, generators and the limits of the call stack.

## 🔴 यह क्यों बना? (Hindi)
असली data अक्सर nested होता है: API का JSON, category trees, comment threads, directory listings। कई tools (pandas columns, CSV export, search indexing) को flat sequence चाहिए। इसका traversal लिखना recursion, generators और call stack की सीमा को परखता है।

---

## 🟢 How it Works — Step by Step

```
Recursive:
Step 1 → result = []
Step 2 → For each item: if it is a list -> extend result with flatten(item)
Step 3 → Otherwise append the item
Generator: same logic but `yield from flatten(item)` / `yield item` (lazy)
Iterative stack:
Step 1 → stack = [iter(data)]
Step 2 → next(stack[-1]); if it is a list -> push iter(item); else collect it
Step 3 → StopIteration -> pop the exhausted level; stop when stack is empty
```

## 🟢 कैसे काम करता है? (Hindi)
```
Recursive:
Step 1 → result = []
Step 2 → हर item के लिए: list हो तो result में flatten(item) जोड़ो
Step 3 → वरना item को append करो
Generator: वही logic पर `yield from flatten(item)` / `yield item` (lazy)
Iterative stack:
Step 1 → stack = [iter(data)]
Step 2 → next(stack[-1]); list हो तो iter(item) push करो; वरना collect करो
Step 3 → StopIteration -> खत्म हुआ level pop करो; stack खाली होने पर रुको
```

---

## 🟡 Real World Example
A Flipkart category tree is nested (Electronics > Mobiles > Android > ...). To index every category name in Elasticsearch, a job flattens the tree into one list of names. A comment system flattens a nested reply thread into a chronological list for display.

## 🟡 Real Example Hindi mein
Flipkart का category tree nested होता है (Electronics > Mobiles > Android > ...)। हर category नाम को Elasticsearch में index करने के लिए job tree को एक list में flatten करती है। Comment system nested replies को दिखाने के लिए समय क्रम की flat list बनाता है।

---

## 💻 Code Example — Basic
```python
# Basic: recursive flatten (full version in main.py)
from typing import Any  # type hint for "anything"


def flatten(data: list[Any]) -> list[Any]:  # returns a flat list
    result: list[Any] = []  # output list
    for item in data:  # visit each element
        if isinstance(item, list):  # nested list -> go deeper
            result.extend(flatten(item))  # add all flattened values
        else:  # plain value
            result.append(item)  # keep it
    return result


print(flatten([1, [2, [3, [4, 5]], 6], [], [[7]]]))  # mixed depths and an empty list
# Output: [1, 2, 3, 4, 5, 6, 7]
print(flatten([[], [[]]]))  # nothing but empty lists
# Output: []
print(flatten([1, "ab", [2]]))  # strings are treated as single values
# Output: [1, 'ab', 2]
```

## 💻 Code Example — Advanced
```python
# From main.py: lazy generator and explicit stack that survives very deep nesting
from typing import Any, Iterator, List  # type hints


def flatten_gen(data: List[Any]) -> Iterator[Any]:
    for item in data:
        if isinstance(item, list):
            yield from flatten_gen(item)  # delegate to the sub-generator
        else:
            yield item  # leaf value


def flatten_iterative(data: List[Any]) -> List[Any]:
    result: List[Any] = []  # flat output
    stack: List[Iterator[Any]] = [iter(data)]  # stack of iterators = our own call stack
    while stack:  # until every level is finished
        try:
            item: Any = next(stack[-1])  # next element of the innermost list
        except StopIteration:
            stack.pop()  # that level is exhausted
            continue
        if isinstance(item, list):
            stack.append(iter(item))  # go one level deeper
        else:
            result.append(item)  # collect leaf
    return result


nested: List[Any] = [1, [2, [3]], 4]
print(list(flatten_gen(nested)))  # Output: [1, 2, 3, 4]
print(next(flatten_gen(nested)))  # lazy: only the first value is computed. Output: 1

deep: List[Any] = [1]  # build 5000 levels of nesting
for _ in range(5000):
    deep = [deep]
print(flatten_iterative(deep))  # no recursion, so no limit
# Output: [1]
try:
    list(flatten_gen(deep))  # recursive generator hits the recursion limit
except RecursionError:
    print("RecursionError")  # Output: RecursionError
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python: no built-in deep flatten; recursion or itertools.chain for one level
from itertools import chain
one_level = list(chain.from_iterable([[1, 2], [3]]))   # [1, 2, 3]
```
```javascript
// JavaScript: built-in!
[1, [2, [3, [4]]]].flat(Infinity);   // [1, 2, 3, 4]
[[1, 2], [3]].flat();                // one level: [1, 2, 3]
```

Key differences: JavaScript has `Array.prototype.flat(depth)`; Python has no deep-flatten built-in, so you write it (or use `more_itertools.collapse`). In Python, remember that strings are iterable, so never flatten "anything iterable" without excluding `str`.

---

## 🟠 FastAPI Connection
Flattening is used to turn nested Pydantic errors, nested JSON filters or category trees into flat lists in response handlers. Validate depth to avoid abuse, since a malicious payload could nest thousands of levels.

```python
# FastAPI: flatten a nested list posted by a client (pip install fastapi)
from typing import Any  # type hint

from fastapi import FastAPI, HTTPException  # framework + errors

app: FastAPI = FastAPI()  # create app


def flatten_iterative(data: list[Any]) -> list[Any]:  # stack version: safe for deep input
    out: list[Any] = []
    stack: list[Any] = [iter(data)]
    while stack:
        try:
            item = next(stack[-1])
        except StopIteration:
            stack.pop()
            continue
        if isinstance(item, list):
            stack.append(iter(item))
        else:
            out.append(item)
    return out


@app.post("/flatten")  # POST /flatten with a JSON list
def flatten(payload: list[Any]) -> dict[str, list[Any]]:
    flat: list[Any] = flatten_iterative(payload)  # iterative, so deep nesting cannot crash it
    if len(flat) > 10_000:  # guard the response size
        raise HTTPException(status_code=413, detail="too many items")
    return {"flat": flat}  # flat list
```

Not run as a server here; flatten logic is verified in `main.py`.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Treating strings as nested iterables
✅ Correct: test for `list` (or `(list, tuple)`), not "iterable".

```python
# Wrong: any iterable is recursed into, and a 1-char string iterates to itself forever
def flat(x):
    for i in x:
        if hasattr(i, "__iter__"): yield from flat(i)   # "a".__iter__ exists -> infinite recursion
        else: yield i
# Right
def flat(x):
    for i in x:
        if isinstance(i, (list, tuple)): yield from flat(i)
        else: yield i
```

❌ Mistake 2: Mutating the input list while looping
✅ Correct: build a new result list.

❌ Mistake 3: Assuming recursion handles any depth
✅ Correct: recursion fails near depth 1000; use the explicit stack for untrusted or very deep data.

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def flat(x):
    for i in x:
        try:
            iter(i)
            yield from flat(i)
        except TypeError:
            yield i

try:
    print(list(flat(["ab"])))
except RecursionError:
    print("RecursionError")
```

**Answer**: `RecursionError`. A string is iterable, and iterating over `"ab"` gives `"a"`, and iterating over `"a"` gives `"a"` again, so the recursion never reaches a non-iterable leaf. Exclude `str` and `bytes` (or check `isinstance(i, list)`).

---

## ⚫ Interview Questions + Answers

Q1: Recursion vs explicit stack: which is better?
A1: Recursion is shorter and clearer, but limited by Python's recursion limit (about 1000). The explicit stack has no such limit and is safe for deep or untrusted data.

Q2: Why use a generator?
A2: It yields values lazily, using O(depth) memory, and the caller can stop early (for example `next()` or `itertools.islice`).

Q3: How do you flatten only one level?
A3: `[x for sub in data for x in sub]` or `itertools.chain.from_iterable(data)`.

Q4: Time and space complexity?
A4: O(N) time where N is the total number of elements and nested lists. Space is O(N) for the output list plus O(depth) for the stack.

Q5: How would you flatten a nested dict?
A5: Recurse over `items()` and join keys with a separator (`{"a": {"b": 1}}` -> `{"a.b": 1}`), the same pattern as flattening lists.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Preparing tree-like data for export, search or analytics
- Input depth is small and known (recursion is fine)
- You want lazy output (generator)

❌ Avoid when:
- Depth is unbounded or attacker-controlled (use the iterative stack plus a size limit)
- You only have two levels (use a comprehension or `chain`)
- You need to preserve the structure (flattening loses hierarchy)

---

## 📊 Visual Diagram

```
 [1, [2, [3, [4, 5]], 6], [], [[7]], "ab"]

 stack (our own call stack):
   [iter(top)]                      -> 1                collected
   [iter(top), iter([2,..])]        -> 2                collected
   [.., iter([3,..])]               -> 3, 4, 5          collected, pop back
   ...                              -> 6, 7, "ab"       collected
 stack empty -> done:  [1, 2, 3, 4, 5, 6, 7, 'ab']
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Flatten | Make multi-level into one level | कई level को एक level बनाना |
| Nested | Inside another structure | किसी के अंदर रखा हुआ |
| `yield from` | Delegate to a sub-generator | sub-generator को काम सौंपना |
| Recursion limit | Max call depth | अधिकतम call गहराई |
| Stack | Last-in-first-out structure | आख़िरी आया पहले जाए |
| Lazy | Computed on demand | माँगने पर बनना |

---

## ⚡ 3-Line Summary
English: Flatten by recursing into lists and collecting leaf values; a generator with `yield from` does it lazily. Use an explicit stack of iterators to avoid the recursion limit on deep input. Never recurse into strings.
Hindi: Lists में recursion करके leaf values इकट्ठा करें; `yield from` वाला generator यही lazily करता है। गहरे input पर recursion limit से बचने के लिए iterators का explicit stack इस्तेमाल करें। Strings में कभी recursion न करें।

---

## ➡️ Next Topic
**458. Group Anagrams** — hashing with a sorted-letters key and `defaultdict`.
