---

# Q268. Iterator Pattern
# Category: Design Patterns
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Implement the Iterator pattern: build a `BookShelf` collection that can be looped with `for`, and give it a reusable iterator class that walks the books in order. Then show how Python's generator makes the same thing shorter.

---

## 💡 Quick Concept (2 lines only)
Iterator gives sequential access to a collection without exposing its internals. In Python: iterable has `__iter__`, iterator has `__next__` and raises `StopIteration` at the end.
हिंदी: Iterator collection के अंदर की बनावट दिखाए बिना एक-एक element देता है; `__iter__` और `__next__` से बनता है।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================
from collections.abc import Iterator  # Step 1: type hint for iterators


class ShelfIterator:  # Step 2: the iterator - holds position state
    def __init__(self, books: list[str]) -> None:
        self._books = books  # reference to underlying data
        self._i = 0  # current position

    def __iter__(self) -> "ShelfIterator":
        return self  # an iterator is its own iterable

    def __next__(self) -> str:
        if self._i >= len(self._books):  # Step 3: out of items?
            raise StopIteration  # signal the end to the for loop
        book = self._books[self._i]  # take current item
        self._i += 1  # advance for next call
        return book  # hand it out


class BookShelf:  # Step 4: the iterable collection
    def __init__(self) -> None:
        self._books: list[str] = []  # hidden storage

    def add(self, title: str) -> None:
        self._books.append(title)  # add a book

    def __iter__(self) -> Iterator[str]:
        return ShelfIterator(self._books)  # fresh iterator per loop


# ============================================
# TEST CASES
# ============================================
shelf = BookShelf()  # create collection
for t in ("Dune", "Emma", "Ulysses"):  # add three books
    shelf.add(t)  # fill the shelf
print(list(shelf))  # Expected: ['Dune', 'Emma', 'Ulysses']
print(list(shelf))  # Expected: ['Dune', 'Emma', 'Ulysses']  (reusable - new iterator each time)
it = iter(shelf)  # manual iteration
print(next(it), next(it), next(it))  # Expected: Dune Emma Ulysses
try:
    next(it)  # one past the end
except StopIteration:
    print("done")  # Expected: done
```

---

## 🔍 Why This Works (3 lines max)
`for` calls `iter(shelf)` which returns a new `ShelfIterator`, then calls `next()` until `StopIteration`. Because the shelf makes a fresh iterator per loop, it can be looped many times.
हिंदी: `for` पहले `iter()` फिर बार-बार `next()` बुलाता है; हर loop को नया iterator मिलता है।

---

## ⚡ Alternative Solution
```python
# Pythonic: __iter__ as a generator - state is handled by yield
from collections.abc import Iterator  # type hint


class BookShelf:
    def __init__(self, *titles: str) -> None:
        self._books = list(titles)  # store titles

    def __iter__(self) -> Iterator[str]:
        yield from self._books  # generator auto-creates the iterator

    def reversed_books(self) -> Iterator[str]:
        yield from reversed(self._books)  # second traversal style, no extra class


s = BookShelf("Dune", "Emma")  # build shelf
print(list(s))  # Expected: ['Dune', 'Emma']
print(list(s.reversed_books()))  # Expected: ['Emma', 'Dune']
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: __iter__ returns self on the collection - it can be looped only once
class BadShelf:
    def __init__(self) -> None:
        self.books = ["a", "b"]  # data
        self.i = 0  # position stored on the collection itself!

    def __iter__(self):
        return self  # shared state

    def __next__(self):
        if self.i >= len(self.books):
            raise StopIteration
        self.i += 1
        return self.books[self.i - 1]


bad = BadShelf()
print(list(bad))  # Output: ['a', 'b']
print(list(bad))  # Output: []   <- exhausted, second loop gets nothing

# ✅ Correct: return a NEW iterator from __iter__ (or use yield)
```

---

## 🎯 Interview Tip (1 line)
Say: "Iterable has `__iter__`, iterator has `__next__`; separate them (or use a generator) so the collection can be looped many times."

---

## 🔗 Related Questions
→ Q120 (iterator class) | Q147 (complete iterator) | Q171 (iterators vs iterables) | Q297 (generators vs iterators)
