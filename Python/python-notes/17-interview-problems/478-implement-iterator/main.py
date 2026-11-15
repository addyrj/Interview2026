# Iterator protocol: __iter__ + __next__, separate iterable vs iterator, reverse, paginator
from typing import Any, Generic, Iterator, Sequence, TypeVar

T = TypeVar("T")


class Countdown:
    """Iterator that is also its own iterable (single use)."""
    def __init__(self, start: int) -> None:
        self.cur = start

    def __iter__(self) -> "Countdown":
        return self                               # an iterator returns itself

    def __next__(self) -> int:
        if self.cur <= 0:
            raise StopIteration                   # signals the end
        self.cur -= 1
        return self.cur + 1


class Playlist(Generic[T]):
    """Re-iterable container: each iter() call returns a FRESH iterator."""
    def __init__(self, items: Sequence[T]) -> None:
        self._items = list(items)

    def __iter__(self) -> Iterator[T]:
        return _PlaylistIterator(self._items)


class _PlaylistIterator(Generic[T]):
    def __init__(self, items: list[T]) -> None:
        self._items, self._i = items, 0

    def __iter__(self) -> "_PlaylistIterator[T]":
        return self

    def __next__(self) -> T:
        if self._i >= len(self._items):
            raise StopIteration
        v = self._items[self._i]
        self._i += 1
        return v


class Paginator:
    """Lazy pages from a list, like cursor-based API paging."""
    def __init__(self, data: Sequence[Any], size: int) -> None:
        self.data, self.size = data, size

    def __iter__(self) -> Iterator[Sequence[Any]]:
        for i in range(0, len(self.data), self.size):
            yield self.data[i:i + self.size]      # slices are the pages


class Fib:
    """Infinite iterator: caller must stop (islice / break)."""
    def __init__(self) -> None:
        self.a, self.b = 0, 1

    def __iter__(self) -> "Fib":
        return self

    def __next__(self) -> int:
        v = self.a
        self.a, self.b = self.b, self.a + self.b
        return v


if __name__ == "__main__":
    c = Countdown(3)
    assert list(c) == [3, 2, 1] and list(c) == []     # exhausted after one pass

    p = Playlist(["a", "b"])
    assert list(p) == ["a", "b"] and list(p) == ["a", "b"]   # re-iterable

    assert list(Paginator([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]

    from itertools import islice
    assert list(islice(Fib(), 8)) == [0, 1, 1, 2, 3, 5, 8, 13]

    it = iter([10, 20])                           # what a for-loop does under the hood
    assert next(it) == 10 and next(it) == 20
    assert next(it, "done") == "done"             # default avoids StopIteration
    print("all iterator tests passed")
