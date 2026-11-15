---

# 478. Implement Iterator
# हिंदी में: Iterator बनाना (iter और next protocol)

Runnable solution with tests: [main.py](./main.py) (run: `python main.py`, verified on Python 3.13).

---

## 🔵 Simple Definition (English)
An iterator is an object that gives you one item at a time through `__next__()` and raises `StopIteration` when finished. An iterable is anything with `__iter__()` that returns an iterator; `for` loops work on iterables.

## 🔵 सरल परिभाषा (Hindi)
Iterator ऐसा object है जो `__next__()` से एक-एक करके item देता है और खत्म होने पर `StopIteration` raise करता है। Iterable वह है जिसमें `__iter__()` हो और जो iterator लौटाए; `for` loop iterables पर चलता है।

---

## 🔴 Problem it Solves
Loading a million rows or an infinite stream into a list wastes memory. The iterator protocol lets any object (a DB cursor, a file, a paginated API) be consumed lazily with the same `for` syntax. It also gives one common interface to `list()`, `sum()`, `zip()`, unpacking, and comprehensions.

## 🔴 यह क्यों बना? (Hindi)
दस लाख rows या अनंत stream को list में भरना memory बर्बाद करता है। Iterator protocol से कोई भी object (DB cursor, file, paginated API) उसी `for` syntax से lazily इस्तेमाल हो सकता है। `list()`, `sum()`, `zip()`, unpacking और comprehensions सबके लिए एक ही interface मिलता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → for x in obj:  calls iter(obj)  -> obj.__iter__()
Step 2 → __iter__ returns an iterator (often self)
Step 3 → The loop calls next(it) -> it.__next__() repeatedly
Step 4 → Each call returns the next value and updates internal state
Step 5 → When there is nothing left: raise StopIteration
Step 6 → The loop catches StopIteration silently and ends
Step 7 → Iterator = single-use (exhausted after one pass); Iterable = can create fresh iterators
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → for x in obj:  iter(obj) बुलाता है  -> obj.__iter__()
Step 2 → __iter__ एक iterator लौटाता है (अक्सर self)
Step 3 → Loop बार-बार next(it) -> it.__next__() बुलाता है
Step 4 → हर call अगली value देती है और अंदरूनी state बदलती है
Step 5 → कुछ बचा न हो तो StopIteration raise करो
Step 6 → Loop StopIteration को चुपचाप पकड़कर खत्म हो जाता है
Step 7 → Iterator = एक बार का (एक pass में खत्म); Iterable = नए iterators बना सकता है
```

---

## 🟡 Real World Example
A paginated API client (Razorpay payments list, GitHub repos) that fetches page 1, yields its items, then fetches page 2 only when the loop needs it. A CSV/log reader over a 5 GB file. A DB cursor streaming rows. An infinite ID generator.

## 🟡 Real Example Hindi mein
Paginated API client (Razorpay payments list, GitHub repos) जो page 1 लाता है, उसके items देता है, और page 2 तभी लाता है जब loop को ज़रूरत हो। 5 GB की CSV/log file का reader। Rows को stream करने वाला DB cursor। अनंत ID generator।

---

## 💻 Code Example — Basic
```python
# Basic custom iterator
class Countdown:
    def __init__(self, start: int) -> None:
        self.cur: int = start                  # current number

    def __iter__(self) -> "Countdown":
        return self                            # an iterator returns itself

    def __next__(self) -> int:
        if self.cur <= 0:                      # nothing left
            raise StopIteration                # tell the loop to stop
        self.cur -= 1                          # move state forward
        return self.cur + 1                    # return the previous value

c = Countdown(3)                               # make it
print(list(c))                                 # consume everything
print(list(c))                                 # exhausted: single use!

it = iter([10, 20])                            # what a for-loop does manually
print(next(it), next(it))                      # two values
print(next(it, "done"))                        # default instead of StopIteration

# Output:
# [3, 2, 1]
# []
# 10 20
# done
```

## 💻 Code Example — Advanced
```python
# Production style: re-iterable container + lazy paginator (tests in main.py)
from typing import Any, Generic, Iterator, Sequence, TypeVar

T = TypeVar("T")


class _PlaylistIterator(Generic[T]):
    def __init__(self, items: list[T]) -> None:
        self._items, self._i = items, 0        # private cursor per iterator

    def __iter__(self) -> "_PlaylistIterator[T]":
        return self                            # iterators are iterable

    def __next__(self) -> T:
        if self._i >= len(self._items):        # end reached
            raise StopIteration
        v = self._items[self._i]               # current item
        self._i += 1                           # advance cursor
        return v


class Playlist(Generic[T]):
    """Iterable: each iter() call gets a FRESH iterator, so it can loop many times."""
    def __init__(self, items: Sequence[T]) -> None:
        self._items = list(items)              # defensive copy

    def __iter__(self) -> Iterator[T]:
        return _PlaylistIterator(self._items)  # new cursor each time


class Paginator:
    """Yield data in pages lazily (generator-based __iter__)."""
    def __init__(self, data: Sequence[Any], size: int) -> None:
        self.data, self.size = data, size

    def __iter__(self) -> Iterator[Sequence[Any]]:
        for i in range(0, len(self.data), self.size):
            yield self.data[i:i + self.size]   # one page at a time


p = Playlist(["a", "b"])
print(list(p), list(p))                        # works twice
print(list(Paginator([1, 2, 3, 4, 5], 2)))     # pages of 2

# Output:
# ['a', 'b'] ['a', 'b']
# [[1, 2], [3, 4], [5]]
```

---

## 🟠 JavaScript vs Python Comparison
JS: iterator protocol is `[Symbol.iterator]()` returning `{ next() { return {value, done} } }`. Python: `__iter__` and `__next__`, and the end is signalled by an exception instead of `done: true`.

```python
# Python way
class Count:
    def __init__(self, n): self.n, self.i = n, 0
    def __iter__(self): return self
    def __next__(self):
        if self.i >= self.n: raise StopIteration
        self.i += 1; return self.i
print(list(Count(3)))    # [1, 2, 3]
```
```javascript
// JavaScript way
class Count {
  constructor(n) { this.n = n; }
  [Symbol.iterator]() {
    let i = 0, n = this.n;
    return { next: () => i < n ? { value: ++i, done: false } : { value: undefined, done: true } };
  }
}
console.log([...new Count(3)]);   // [1, 2, 3]
```

---

## 🟠 FastAPI Connection
FastAPI's `StreamingResponse` accepts any iterator/generator, so you can stream big exports without building the whole list in memory. Database cursors (`yield_per`) feed it row by row.

```python
from typing import Iterator
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient

app = FastAPI()

def csv_rows(n: int) -> Iterator[str]:
    yield "id,name\n"                          # header first
    for i in range(1, n + 1):                  # then rows lazily
        yield f"{i},user{i}\n"

@app.get("/export")
def export() -> StreamingResponse:
    return StreamingResponse(csv_rows(3), media_type="text/csv")   # streamed, not buffered

print(TestClient(app).get("/export").text)

# Output:
# id,name
# 1,user1
# 2,user2
# 3,user3
```

---

## ⚠️ Common Mistakes to Avoid
❌ Mistake 1: iterating an iterator twice and getting nothing the second time.
✅ Correct: make the class an iterable that returns a fresh iterator, or wrap with `list()` if small.

```python
# Wrong
it = iter([1, 2, 3]); list(it); list(it)   # second is []
# Right
data = [1, 2, 3]; list(data); list(data)   # a list is re-iterable
```

❌ Mistake 2: forgetting `__iter__` on the iterator (works with `next()` but not in `for`).
✅ Correct: implement both and return `self` from `__iter__`.

❌ Mistake 3: returning a sentinel (`None`) instead of raising `StopIteration` (infinite loop), or raising `StopIteration` inside a generator (becomes `RuntimeError` since Python 3.7).
✅ Correct: `raise StopIteration` in `__next__`; use plain `return` in generators.

---

## 🧠 Tricky Interview Question
```python
nums = [1, 2, 3]
it = iter(nums)
print(sum(it))
print(sum(it))
print(list(zip(nums, nums)))
```
Answer: `6`, `0`, `[(1, 1), (2, 2), (3, 3)]`. `sum(it)` exhausts the iterator, so the second sum has nothing left. The list `nums` itself is an iterable and can be iterated again and again.

---

## ⚫ Interview Questions + Answers

Q1: Iterable vs iterator?
A1: Iterable has `__iter__` returning an iterator; iterator has `__next__` and `__iter__` (returns self). A list is iterable, not an iterator; `iter(list)` is an iterator.

Q2: What does a `for` loop really do?
A2: `it = iter(obj)`, then `while True: try: x = next(it) except StopIteration: break`.

Q3: How do you make an infinite iterator safely?
A3: `__next__` never raises; the consumer stops with `break` or `itertools.islice`.

Q4: Iterator class vs generator?
A4: A generator function is a shorter way to build an iterator. Use a class when you need extra methods, `__len__`, or complex state.

Q5: How does `iter(callable, sentinel)` work?
A5: It calls `callable()` repeatedly until it returns `sentinel`, e.g. `iter(lambda: f.read(1024), b"")` to read a file in chunks.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Data is large, remote, or infinite and should be consumed lazily
- You expose a custom collection to `for`, `list()`, `sum()`
- You need separate cursors over the same data

❌ Avoid when:
- You need random access or `len()` (use a list)
- A generator function is simpler and enough
- You must read the data several times and it is small (just materialize it)

---

## 📊 Visual Diagram
```
 iterable                iterator
 [ 10, 20, 30 ] --iter()--> cursor ^
                                  |
 next() -> 10   cursor moves ->   10 [20] 30
 next() -> 20                     10  20 [30]
 next() -> 30                     10  20  30 [ ]
 next() -> raises StopIteration  --> for-loop ends quietly
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Iterable | Can produce an iterator (`__iter__`) | जिस पर loop चल सके |
| Iterator | Produces values with `__next__` | एक-एक value देने वाला |
| StopIteration | Signal that items are finished | समाप्ति का संकेत |
| Exhausted | Iterator has no items left | खाली हो चुका |
| Lazy | Compute only when asked | ज़रूरत पर ही गणना |
| Sentinel | Special end value | अंत बताने वाला विशेष मान |

---

## ⚡ 3-Line Summary
English: An iterator implements `__next__`; an iterable implements `__iter__` returning an iterator.
English: Raise `StopIteration` at the end; iterators are single-use, iterables can be reused.
English: Use iterators for lazy, memory-friendly streams and custom collections.

Hindi: Iterator `__next__` लागू करता है; iterable `__iter__` लागू करके iterator लौटाता है।
Hindi: अंत में `StopIteration` raise करो; iterators एक बार के होते हैं, iterables दोबारा इस्तेमाल हो सकते हैं।
Hindi: Lazy, कम-memory streams और custom collections के लिए iterators इस्तेमाल करो।

---

## ➡️ Next Topic
**479. Implement Generator** — the shortcut that builds iterators with `yield`.

---
