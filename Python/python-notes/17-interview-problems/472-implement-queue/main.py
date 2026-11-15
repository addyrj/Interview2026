# Implement Queue: three ways (list-bad, deque, linked ring buffer) + tests
from __future__ import annotations                # allow forward type references
from collections import deque                     # O(1) both ends
from typing import Generic, Optional, TypeVar     # generic typing helpers

T = TypeVar("T")                                  # element type


class Queue(Generic[T]):
    """FIFO queue backed by deque: enqueue/dequeue are O(1)."""

    def __init__(self) -> None:
        self._items: deque[T] = deque()           # storage

    def enqueue(self, item: T) -> None:
        self._items.append(item)                  # add at the back

    def dequeue(self) -> T:
        if not self._items:                       # guard empty queue
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()              # remove from the front

    def peek(self) -> T:
        if not self._items:                       # guard empty queue
            raise IndexError("peek from empty queue")
        return self._items[0]                     # look at the front

    def is_empty(self) -> bool:
        return not self._items                    # True when no items

    def __len__(self) -> int:
        return len(self._items)                   # number of items


class CircularQueue(Generic[T]):
    """Fixed-capacity queue using a ring buffer (no resizing, O(1))."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:                         # validate capacity
            raise ValueError("capacity must be positive")
        self._buf: list[Optional[T]] = [None] * capacity   # preallocated slots
        self._cap = capacity                      # max size
        self._head = 0                            # index of the front
        self._size = 0                            # current count

    def enqueue(self, item: T) -> bool:
        if self._size == self._cap:               # full -> reject
            return False
        self._buf[(self._head + self._size) % self._cap] = item   # write at tail
        self._size += 1                           # one more item
        return True

    def dequeue(self) -> T:
        if self._size == 0:                       # empty -> error
            raise IndexError("dequeue from empty queue")
        item = self._buf[self._head]              # read the front
        self._buf[self._head] = None              # release reference
        self._head = (self._head + 1) % self._cap # move head forward, wrap around
        self._size -= 1                           # one less item
        return item  # type: ignore[return-value]

    def __len__(self) -> int:
        return self._size                         # current count


class QueueWithTwoStacks(Generic[T]):
    """Classic interview variant: queue using two stacks (amortized O(1))."""

    def __init__(self) -> None:
        self._in: list[T] = []                    # receives new items
        self._out: list[T] = []                   # serves old items

    def enqueue(self, item: T) -> None:
        self._in.append(item)                     # push on the inbox stack

    def dequeue(self) -> T:
        if not self._out:                         # outbox empty -> refill
            while self._in:                       # move everything over
                self._out.append(self._in.pop())  # reverses the order -> FIFO
        if not self._out:                         # still empty -> nothing stored
            raise IndexError("dequeue from empty queue")
        return self._out.pop()                    # oldest item


if __name__ == "__main__":
    q: Queue[int] = Queue()
    for n in (1, 2, 3):
        q.enqueue(n)
    assert q.peek() == 1 and len(q) == 3
    assert [q.dequeue(), q.dequeue(), q.dequeue()] == [1, 2, 3]
    assert q.is_empty()
    try:
        q.dequeue()
        raise AssertionError("should raise")
    except IndexError as e:
        print("empty ->", e)

    c: CircularQueue[str] = CircularQueue(2)
    assert c.enqueue("a") and c.enqueue("b") and not c.enqueue("c")   # third rejected
    assert c.dequeue() == "a" and c.enqueue("c")      # wrap-around works
    assert [c.dequeue(), c.dequeue()] == ["b", "c"]

    t: QueueWithTwoStacks[int] = QueueWithTwoStacks()
    t.enqueue(1); t.enqueue(2)
    assert t.dequeue() == 1
    t.enqueue(3)
    assert [t.dequeue(), t.dequeue()] == [2, 3]
    print("all queue tests passed")
