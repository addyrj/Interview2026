---

# 137. Iterables vs Iterators
# हिंदी में: Iterable और Iterator में अंतर

---

## 🔵 Simple Definition (English)
An iterable is anything you can loop over: it has `__iter__()` that returns a new iterator (list, tuple, str, dict, set, file). An iterator is the object that does the walking: it has `__next__()` and remembers its position. Every iterator is iterable, but not every iterable is an iterator.

## 🔵 सरल परिभाषा (Hindi)
Iterable वह चीज़ है जिस पर loop चल सकता है: उसमें `__iter__()` होता है जो नया iterator देता है (list, tuple, str, dict, set, file)। Iterator वह object है जो असल में चलता है: उसमें `__next__()` होता है और वह अपनी position याद रखता है। हर iterator iterable होता है, पर हर iterable iterator नहीं होता।

---

## 🔴 Problem it Solves
If a list stored its own "current position", two loops over the same list would disturb each other. Separating the container (iterable) from the cursor (iterator) lets many loops run on the same data independently, and lets one-shot sources like files or sockets work with the same `for` syntax.

## 🔴 यह क्यों बना? (Hindi)
अगर list अपनी "current position" खुद रखती, तो एक ही list पर दो loops एक-दूसरे को बिगाड़ देते। Container (iterable) और cursor (iterator) को अलग रखने से एक ही data पर कई loops स्वतंत्र चल सकते हैं, और file या socket जैसे एक बार वाले sources भी वही `for` syntax इस्तेमाल कर पाते हैं।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Iterable (list) is the storage; it holds no position
Step 2 → iter(list) creates a NEW iterator with position = 0
Step 3 → next(iterator) returns item at position and moves forward
Step 4 → A second iter(list) gives a separate iterator, position = 0 again
Step 5 → iter(iterator) returns the SAME iterator (no reset)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Iterable (list) सिर्फ data रखता है, position नहीं
Step 2 → iter(list) नया iterator बनाता है जिसकी position = 0 होती है
Step 3 → next(iterator) position वाला item देकर आगे बढ़ता है
Step 4 → दूसरा iter(list) अलग iterator देता है, position फिर 0
Step 5 → iter(iterator) वही iterator लौटाता है (reset नहीं होता)
```

---

## 🟡 Real World Example
A Swiggy `Menu` object is iterable: two waiters can each loop over the same menu at the same time. A `MenuCursor` reading page by page is the iterator that remembers which page it is on. In a data job, a CSV file object is an iterator: reading it twice gives nothing the second time, which is a famous production bug.

## 🟡 Real Example Hindi mein
Swiggy का `Menu` object iterable है: दो waiters एक ही समय में उसी menu पर loop चला सकते हैं। Page-by-page पढ़ने वाला `MenuCursor` iterator है जो याद रखता है कि कौन सा page चल रहा है। Data job में CSV file object एक iterator है: उसे दो बार पढ़ो तो दूसरी बार कुछ नहीं मिलता, यह production का मशहूर bug है।

---

## 💻 Code Example — Basic
```python
# Iterable vs iterator - every line commented
from collections.abc import Iterable, Iterator  # abstract base classes for checks

menu: list[str] = ["dosa", "idli", "vada"]  # a list is an ITERABLE

print(isinstance(menu, Iterable), isinstance(menu, Iterator))  # iterable, not iterator
# Output: True False
print(hasattr(menu, "__iter__"), hasattr(menu, "__next__"))  # only __iter__ exists
# Output: True False

cursor = iter(menu)  # create an ITERATOR from the iterable
print(isinstance(cursor, Iterator), isinstance(cursor, Iterable))  # both true
# Output: True True
print(iter(cursor) is cursor)  # an iterator returns itself from iter()
# Output: True

print(next(cursor))  # take one value
# Output: dosa
print(list(cursor))  # the rest - cursor remembers the position
# Output: ['idli', 'vada']
print(list(cursor))  # now exhausted
# Output: []

# An iterable can be looped any number of times
print(list(menu), list(menu))  # new iterator each time
# Output: ['dosa', 'idli', 'vada'] ['dosa', 'idli', 'vada']

# Two independent iterators on the same list
a = iter(menu)  # first cursor
b = iter(menu)  # second cursor
print(next(a), next(a), next(b))  # a moved twice, b once
# Output: dosa idli dosa

# Other examples
print(isinstance("hi", Iterable), isinstance("hi", Iterator))  # str is iterable
# Output: True False
print(isinstance(range(3), Iterator), isinstance(iter(range(3)), Iterator))
# Output: False True
gen = (x for x in menu)  # generator expression
print(isinstance(gen, Iterator))  # generators are iterators
# Output: True
```

## 💻 Code Example — Advanced
```python
# Production style: iterable class that makes a fresh iterator every time
import io  # for a fake file
from collections.abc import Iterator  # type hint


class Playlist:  # ITERABLE: holds data, no position
    def __init__(self, songs: list[str]) -> None:  # store the data
        self._songs: list[str] = songs  # private list

    def __iter__(self) -> Iterator[str]:  # called by for loop / iter()
        return iter(self._songs)  # new independent iterator each call

    def __len__(self) -> int:  # bonus: len() works because we store a list
        return len(self._songs)  # size


pl = Playlist(["a", "b", "c"])  # create the iterable
print(list(pl), list(pl))  # reusable
# Output: ['a', 'b', 'c'] ['a', 'b', 'c']
print([(x, y) for x in pl for y in pl][:4])  # nested loops on same object work
# Output: [('a', 'a'), ('a', 'b'), ('a', 'c'), ('b', 'a')]


class OneShot:  # BAD design: iterable that is its own iterator
    def __init__(self, n: int) -> None:  # limit
        self.i: int = 0  # position stored inside the iterable itself
        self.n: int = n  # stop value

    def __iter__(self) -> "OneShot":  # returns self - no fresh cursor
        return self  # same object every time

    def __next__(self) -> int:  # next value
        if self.i >= self.n:  # finished
            raise StopIteration  # signal end
        self.i += 1  # move forward
        return self.i  # give value


shot = OneShot(3)  # create
print(list(shot), list(shot))  # second pass is empty!
# Output: [1, 2, 3] []
print([(x, y) for x in OneShot(2) for y in OneShot(2)])  # works only because new objects
# Output: [(1, 1), (1, 2), (2, 1), (2, 2)]

# Classic bug: a file object is an iterator
f = io.StringIO("line1\nline2\n")  # pretend open("log.txt")
print(sum(1 for _ in f))  # first pass counts 2 lines
# Output: 2
print(sum(1 for _ in f))  # second pass finds nothing
# Output: 0
f.seek(0)  # rewind a file by hand (iterators in general cannot rewind)
print(sum(1 for _ in f))  # works again
# Output: 2


def ensure_reusable(data: "Iterator[int] | list[int]") -> list[int]:  # defensive helper
    return list(data)  # materialise once, safe for many passes


gen = (i * 2 for i in range(3))  # one-shot generator
safe = ensure_reusable(gen)  # convert to list
print(sum(safe), max(safe))  # both calls see all data
# Output: 6 4
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript uses the same split: an *iterable* has `[Symbol.iterator]()`, which returns an *iterator* with `next()`. Arrays, strings, Maps and Sets are iterable; generator objects are iterators and iterable.

```python
# Python way
menu = ["a", "b"]
it = iter(menu)             # iterator
print(next(it))             # a
print(list(menu))           # menu still intact ['a', 'b']
print(iter(it) is it)       # True
```
```javascript
// JavaScript way
const menu = ["a", "b"];
const it = menu[Symbol.iterator]();   // iterator
console.log(it.next().value);         // a
console.log([...menu]);               // ["a", "b"] - array unchanged
console.log(it[Symbol.iterator]() === it);   // true (iterators are iterable)
```

Key differences: Python uses `iter()`/`next()` builtins and `__iter__`/`__next__`, JS uses `Symbol.iterator` and `.next()` returning `{value, done}`. Plain objects are not iterable in JS; in Python dicts are.

---

## 🟠 FastAPI Connection
A common FastAPI bug: returning an iterator from a function and using it twice, or caching a generator inside a global. Keep data as a list (iterable, reusable) in shared state and create iterators per request. Streaming endpoints need an iterator, but each request must build a fresh one.

```python
# FastAPI: fresh iterator per request (pip install fastapi httpx)
from collections.abc import Iterator  # type hint
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # stream
from fastapi.testclient import TestClient  # test

app: FastAPI = FastAPI()  # app
ROWS: list[str] = ["a\n", "b\n"]  # shared ITERABLE (safe to reuse)
BROKEN: Iterator[str] = iter(ROWS)  # shared ITERATOR (used up after one request)


@app.get("/good")  # good endpoint
def good() -> StreamingResponse:  # builds a new iterator every request
    return StreamingResponse(iter(ROWS), media_type="text/plain")  # fresh cursor


@app.get("/broken")  # buggy endpoint
def broken() -> StreamingResponse:  # reuses the global iterator
    return StreamingResponse(BROKEN, media_type="text/plain")  # empty on request 2


client = TestClient(app)  # test client
print(repr(client.get("/good").text), repr(client.get("/good").text))  # always full
# Output: 'a\nb\n' 'a\nb\n'
print(repr(client.get("/broken").text), repr(client.get("/broken").text))  # second empty
# Output: 'a\nb\n' ''
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Returning `self` from `__iter__` for a re-iterable collection
```python
# Wrong - the collection can be looped only once
# def __iter__(self): return self

# Right - return a new iterator each time
# def __iter__(self): return iter(self._items)
```

❌ Mistake 2: Passing a generator where two passes are needed
```python
# Wrong - mean() sees nothing after sum() consumed the generator
data = (x for x in [1, 2, 3])
total = sum(data)
count = len(list(data))
print(total, count)         # 6 0

# Right - build a list first
data = [x for x in [1, 2, 3]]
print(sum(data), len(data)) # 6 3
```

❌ Mistake 3: Assuming `iter(x)` resets an iterator
```python
# Wrong - iter(it) is it, so there is no reset
it = iter([1, 2, 3])
next(it)
print(list(iter(it)))       # [2, 3]  (not [1, 2, 3])

# Right - call iter() on the original iterable
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
nums = [1, 2, 3]
it = iter(nums)
nums.append(4)
print(list(it))

d = {"a": 1}
it2 = iter(d)
try:
    d["b"] = 2
    next(it2)
except RuntimeError as e:
    print("RuntimeError:", e)

print(list(map(str, range(2))) == list(map(str, range(2))))
```

**Answer**:
```
[1, 2, 3, 4]
RuntimeError: dictionary changed size during iteration
True
```
A list iterator reads the live list, so the appended `4` is seen. A dict iterator detects a size change and raises `RuntimeError`. Each `map(...)` call makes its own fresh iterator, so comparing two separate lists is `True`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between an iterable and an iterator?
A1: An iterable has `__iter__` returning an iterator; an iterator has `__next__` (and `__iter__` returning itself) and keeps the position.

Q2: Is a list an iterator?
A2: No. `next([1, 2])` raises `TypeError`. You need `iter([1, 2])` first.

Q3: Is a generator iterable or iterator?
A3: Both. A generator is an iterator (it has `__next__`) and, since `iter(gen) is gen`, it is also iterable.

Q4: Why can a file be read only once with `for`?
A4: A file object is an iterator with an internal file pointer. After the end, nothing is left unless you `seek(0)` or reopen it.

Q5: How do you check them in code?
A5: `isinstance(x, collections.abc.Iterable)` and `isinstance(x, collections.abc.Iterator)`.

---

## 🔷 When to Use + When Not to Use

✅ Use when (make a class iterable):
- You own a collection and want many independent loops
- You want `for`, `list()`, `sum()` to work on your class
- You can create a fresh iterator cheaply

❌ Avoid when (making the class its own iterator):
- Callers might loop twice or nest loops
- The object is shared between requests or threads
- You only need one pass: then a generator is simpler

---

## 📊 Visual Diagram

```
   ITERABLE (container)                  ITERATORS (cursors)
   ┌──────────────────┐   iter() ──►  cursor A: ▶ dosa  idli  vada
   │ dosa  idli  vada │   iter() ──►  cursor B:   dosa ▶ idli  vada
   └──────────────────┘
   has __iter__                         has __next__ + __iter__ (returns self)
   no position                          remembers position, one direction only
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Iterable | Can produce an iterator via `__iter__` | जिस पर loop चल सके |
| Iterator | Has `__next__`, remembers position | position याद रखने वाला cursor |
| Exhausted | No values left | values खत्म |
| Re-iterable | Can be looped many times | कई बार loop हो सकने वाला |
| `collections.abc` | Standard abstract types for checks | type जाँच के abstract classes |
| Cursor | Informal word for iterator position | position बताने वाला pointer |

---

## ⚡ 3-Line Summary
English: An iterable stores data and gives a fresh iterator through `__iter__`. An iterator has `__next__`, remembers its position and is used up after one pass. Make your collection an iterable, not its own iterator.
Hindi: Iterable data रखता है और `__iter__` से नया iterator देता है। Iterator में `__next__` होता है, position याद रहती है और एक pass में खत्म हो जाता है। अपनी collection को iterable बनाओ, खुद का iterator नहीं।

---

## ➡️ Next Topic
**138. `__iter__` + `__next__`** — write your own iterator classes by hand.
