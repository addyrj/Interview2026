---

# 138. __iter__ + __next__
# हिंदी में: __iter__ और __next__ (अपना iterator class बनाना)

---

## 🔵 Simple Definition (English)
`__iter__` and `__next__` are the two special methods of the iterator protocol. `__iter__` returns the iterator object. `__next__` returns the next value or raises `StopIteration`. If your class has both, it works with `for`, `list()`, `sum()`, `zip()` and unpacking.

## 🔵 सरल परिभाषा (Hindi)
`__iter__` और `__next__` iterator protocol के दो special methods हैं। `__iter__` iterator object लौटाता है। `__next__` अगली value देता है या `StopIteration` raise करता है। अगर आपकी class में दोनों हों, तो वह `for`, `list()`, `sum()`, `zip()` और unpacking के साथ चलती है।

---

## 🔴 Problem it Solves
Built-in lists and generators cover most cases, but sometimes you need custom traversal with state: paginated API calls, a countdown, Fibonacci with a limit, a tree walker. Writing the two methods lets your own class behave like a built-in sequence with no extra glue code.

## 🔴 यह क्यों बना? (Hindi)
Built-in list और generators ज़्यादातर काम कर देते हैं, पर कभी state के साथ custom traversal चाहिए: paginated API calls, countdown, limit वाला Fibonacci, tree walker। ये दो methods लिखने से आपकी class built-in sequence की तरह चलती है और अलग से कोई जोड़-तोड़ नहीं करनी पड़ती।

---

## 🟢 How it Works — Step by Step

```
Step 1 → for x in obj  calls  obj.__iter__()  once
Step 2 → The returned object must have __next__
Step 3 → Each loop turn calls  iterator.__next__()
Step 4 → __next__ updates its own state and returns a value
Step 5 → When finished, __next__ raises StopIteration → loop stops
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → for x in obj, obj.__iter__() को एक बार call करता है
Step 2 → जो object मिले उसमें __next__ होना ज़रूरी है
Step 3 → हर बार loop iterator.__next__() बुलाता है
Step 4 → __next__ अपनी state बदलकर value लौटाता है
Step 5 → काम खत्म होने पर __next__ StopIteration raise करता है → loop रुकता है
```

---

## 🟡 Real World Example
A Razorpay reconciliation tool pulls transactions from a paginated API: `PaymentPages(api)` is an iterator that fetches page 1, yields each payment, then silently fetches page 2, and stops when the API returns an empty page. The caller just writes `for payment in PaymentPages(api)`. The same pattern is used by database cursors and S3 object listings.

## 🟡 Real Example Hindi mein
Razorpay का reconciliation tool paginated API से transactions लाता है: `PaymentPages(api)` iterator पहले page 1 fetch करता है, हर payment देता है, फिर चुपचाप page 2 लाता है, और API खाली page दे तो रुक जाता है। Caller बस `for payment in PaymentPages(api)` लिखता है। Database cursors और S3 object listing भी यही pattern इस्तेमाल करते हैं।

---

## 💻 Code Example — Basic
```python
# Custom iterator class - every line commented
class Countdown:  # an iterator that counts down
    def __init__(self, start: int) -> None:  # set initial state
        self.current: int = start  # where to begin

    def __iter__(self) -> "Countdown":  # iterator returns itself
        return self  # required by the protocol

    def __next__(self) -> int:  # produce the next value
        if self.current <= 0:  # nothing left
            raise StopIteration  # tell the loop to stop
        value: int = self.current  # remember the value to return
        self.current -= 1  # move the state forward
        return value  # hand over the value


for n in Countdown(3):  # for calls __iter__ then __next__ repeatedly
    print(n)  # body runs once per value
# Output:
# 3
# 2
# 1

print(list(Countdown(5)))  # list() also uses the protocol
# Output: [5, 4, 3, 2, 1]
print(sum(Countdown(4)), max(Countdown(4)))  # sum and max too
# Output: 10 4

a, b, c = Countdown(3)  # unpacking works
print(a, b, c)  # show them
# Output: 3 2 1

it = Countdown(2)  # manual stepping
print(next(it), next(it))  # two calls to __next__
# Output: 2 1
try:  # the third call raises
    next(it)  # StopIteration
except StopIteration:  # handle it
    print("done")  # finished
# Output: done

print(list(zip(Countdown(3), "abc")))  # zip works with it
# Output: [(3, 'a'), (2, 'b'), (1, 'c')]
```

## 💻 Code Example — Advanced
```python
# Production style: re-iterable collection + separate iterator + paginated source
from collections.abc import Iterator  # type hints
from typing import Any  # for dict typing


class Fibonacci:  # ITERABLE class: fresh iterator for each loop
    def __init__(self, limit: int) -> None:  # max count of numbers
        self.limit: int = limit  # how many numbers

    def __iter__(self) -> Iterator[int]:  # make a NEW iterator every time
        return _FibIterator(self.limit)  # separate state object


class _FibIterator:  # the ITERATOR: holds the changing state
    def __init__(self, limit: int) -> None:  # setup
        self._left: int = limit  # how many left to give
        self._a: int = 0  # current Fibonacci number
        self._b: int = 1  # next Fibonacci number

    def __iter__(self) -> "_FibIterator":  # iterators are iterable too
        return self  # same object

    def __next__(self) -> int:  # one value per call
        if self._left == 0:  # reached the limit
            raise StopIteration  # stop
        self._left -= 1  # use one slot
        value: int = self._a  # value to return
        self._a, self._b = self._b, self._a + self._b  # advance the pair
        return value  # return it


fib = Fibonacci(8)  # reusable object
print(list(fib), list(fib))  # works twice
# Output: [0, 1, 1, 2, 3, 5, 8, 13] [0, 1, 1, 2, 3, 5, 8, 13]


class PaymentPages:  # iterator over a paginated API (faked)
    def __init__(self, pages: dict[int, list[dict[str, Any]]]) -> None:  # fake API data
        self._pages = pages  # page number -> rows
        self._page_no: int = 1  # page we will fetch next
        self._buffer: list[dict[str, Any]] = []  # rows already fetched
        self.api_calls: int = 0  # count fetches to prove laziness

    def __iter__(self) -> "PaymentPages":  # self iterator
        return self  # returns itself

    def __next__(self) -> dict[str, Any]:  # one payment per call
        if not self._buffer:  # buffer empty -> fetch next page
            self._buffer = list(self._pages.get(self._page_no, []))  # "API call"
            self.api_calls += 1  # count it
            self._page_no += 1  # next time ask for next page
            if not self._buffer:  # empty page means no more data
                raise StopIteration  # end of data
        return self._buffer.pop(0)  # give the first buffered payment


api_data = {1: [{"id": 1}, {"id": 2}], 2: [{"id": 3}], 3: []}  # 3 payments, 3 pages
pages = PaymentPages(api_data)  # create iterator
first = next(pages)  # triggers only page 1
print(first, pages.api_calls)  # one API call so far
# Output: {'id': 1} 1
print([p["id"] for p in pages], pages.api_calls)  # rest of the data
# Output: [2, 3] 3


# Safe pattern: guard against endless loops with a clear error
class BadIter:  # forgets to raise StopIteration
    def __iter__(self) -> "BadIter":  # returns self
        return self  # self

    def __next__(self) -> int:  # never ends
        return 1  # always 1


from itertools import islice  # bound an infinite iterator
print(list(islice(BadIter(), 3)))  # islice saves us
# Output: [1, 1, 1]

# Returning a value without __next__ -> clear TypeError
class OnlyIter:  # has __iter__ but returns something without __next__
    def __iter__(self) -> int:  # type: ignore[override]
        return 5  # invalid


try:  # trying to loop
    for _ in OnlyIter():  # Python validates the returned object
        pass  # never reached
except TypeError as exc:  # explains the contract
    print("TypeError:", exc)  # show message
# Output: TypeError: iter() returned non-iterator of type 'int'
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript needs `[Symbol.iterator]()` and a `next()` method returning `{ value, done }`. Python needs `__iter__` and `__next__`, and ends with an exception rather than a `done` flag.

```python
# Python way
class Count:
    def __init__(self, n): self.i, self.n = 0, n
    def __iter__(self): return self
    def __next__(self):
        if self.i >= self.n: raise StopIteration
        self.i += 1
        return self.i
print(list(Count(3)))     # [1, 2, 3]
```
```javascript
// JavaScript way
class Count {
  constructor(n) { this.i = 0; this.n = n; }
  [Symbol.iterator]() { return this; }
  next() {
    if (this.i >= this.n) return { value: undefined, done: true };
    this.i += 1;
    return { value: this.i, done: false };
  }
}
console.log([...new Count(3)]);   // [1, 2, 3]
```

Key differences: JS signals the end with `done: true`; Python raises `StopIteration`. In both languages a generator (`function*` / `yield`) is a shorter way to write this class.

---

## 🟠 FastAPI Connection
An iterator class fits a streaming endpoint where producing rows needs state, such as reading a database in batches with a keyset cursor. FastAPI's `StreamingResponse` accepts any iterator.

```python
# FastAPI: class-based iterator streaming ids in batches (pip install fastapi httpx)
from collections.abc import Iterator  # type hints
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # response type
from fastapi.testclient import TestClient  # in-process test

app: FastAPI = FastAPI()  # app


class IdStream:  # iterator producing lines
    def __init__(self, total: int) -> None:  # setup
        self.i: int = 0  # position
        self.total: int = total  # how many lines

    def __iter__(self) -> "IdStream":  # return self
        return self  # self

    def __next__(self) -> str:  # one line per call
        if self.i >= self.total:  # finished
            raise StopIteration  # stop
        self.i += 1  # advance
        return f"{self.i}\n"  # line


@app.get("/ids/{total}")  # GET /ids/3
def ids(total: int) -> StreamingResponse:  # new iterator per request
    return StreamingResponse(IdStream(total), media_type="text/plain")  # stream


client = TestClient(app)  # client
print(repr(client.get("/ids/3").text))  # body
# Output: '1\n2\n3\n'
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using `return` of a value instead of raising `StopIteration`
```python
# Wrong - returning None forever makes an infinite loop
# def __next__(self):
#     if self.i >= self.n: return None

# Right
# def __next__(self):
#     if self.i >= self.n: raise StopIteration
```

❌ Mistake 2: Forgetting to update state (infinite loop)
```python
# Wrong - self.current never changes
# def __next__(self): return self.current

# Right - change state, then return the value
# value = self.current; self.current -= 1; return value
```

❌ Mistake 3: Putting state in `__iter__` reset logic wrongly
```python
# Wrong - returns self but forgets to reset, second loop is empty
c = [1, 2, 3]
class C:
    def __init__(self): self.it = iter(c)
    def __iter__(self): return self
    def __next__(self): return next(self.it)
x = C()
print(list(x), list(x))      # [1, 2, 3] []

# Right - make an iterable class that returns a NEW iterator in __iter__
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
class Gen:
    def __iter__(self):
        print("iter called")
        return iter([1, 2])

g = Gen()
print(list(g))
print(list(g))
print(sum(g))

def stopper():
    raise StopIteration

class Weird:
    def __iter__(self): return self
    def __next__(self): return stopper()

print(list(Weird()))
```

**Answer**:
```
iter called
[1, 2]
iter called
[1, 2]
iter called
3
[]
```
`__iter__` runs once per loop or conversion, so every pass prints. `Weird.__next__` raises `StopIteration` through a helper function, which also ends iteration, so `list()` returns `[]`. (Inside a generator this would become `RuntimeError` since PEP 479.)

---

## ⚫ Interview Questions + Answers

Q1: What is the iterator protocol?
A1: A class implements `__iter__()` returning an iterator and `__next__()` returning the next value or raising `StopIteration`.

Q2: Should `__iter__` of an iterator return `self`?
A2: Yes. That lets iterators be used wherever iterables are expected, such as in `for` loops.

Q3: Can a class have only `__getitem__` and still be iterable?
A3: Yes, the legacy protocol: Python calls `__getitem__(0)`, `(1)`, ... until `IndexError`. Prefer `__iter__` in new code.

Q4: Class iterator or generator?
A4: Use a generator for simplicity. Use a class when you need extra methods, public state (like `api_calls`), reset ability or a reusable iterable with separate iterators.

Q5: What happens if `__next__` never stops?
A5: The loop is infinite. Guard with `itertools.islice` or a counter.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- You need iteration with extra state or methods
- You build a library class that should work with `for`
- You wrap a paginated or cursor-based data source

❌ Avoid when:
- A generator function (`yield`) does the job in 5 lines
- A plain list is enough
- You would mix iterable and iterator roles in one reusable class

---

## 📊 Visual Diagram

```
 for n in Countdown(3):
        │
        ▼
  iter(obj) ──► obj.__iter__() ──► returns self
        │
        ▼ (loop)
  obj.__next__() ──► 3
  obj.__next__() ──► 2
  obj.__next__() ──► 1
  obj.__next__() ──► raise StopIteration ──► loop ends
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `__iter__` | Returns the iterator | iterator लौटाने वाला method |
| `__next__` | Returns next value or stops | अगली value देने वाला method |
| `StopIteration` | Exception that ends iteration | iteration खत्म करने वाला exception |
| Protocol | Agreed set of methods | तय methods का समूह |
| State | Data the iterator remembers | iterator की याद रखी हुई जानकारी |
| Sentinel | Special value marking the end | अंत बताने वाली खास value |

---

## ⚡ 3-Line Summary
English: Implement `__iter__` (return the iterator) and `__next__` (return a value or raise `StopIteration`) to make a class loopable. Update your state in `__next__` and end with `StopIteration`. For simple cases, a generator is shorter.
Hindi: Class को loop योग्य बनाने के लिए `__iter__` (iterator लौटाए) और `__next__` (value दे या `StopIteration` raise करे) लिखें। `__next__` में state बदलें और अंत में `StopIteration` दें। सरल मामलों में generator छोटा रास्ता है।

---

## ➡️ Next Topic
**140. yield Statement** — let Python build the iterator for you with a generator function.
