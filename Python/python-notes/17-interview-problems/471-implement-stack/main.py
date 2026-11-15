"""471. Implement Stack - list-backed, linked, min-stack (run: python3 main.py)."""
from __future__ import annotations  # allow forward references in annotations
from collections import deque  # alternative backing store
from typing import Generic, List, Optional, TypeVar  # type hints

T = TypeVar("T")  # element type


class Stack(Generic[T]):
    """LIFO stack backed by a list. push/pop/peek are O(1) amortized."""

    def __init__(self) -> None:
        self._items: List[T] = []  # end of the list is the top

    def push(self, item: T) -> None:
        """Add an item on top."""
        self._items.append(item)  # amortized O(1)

    def pop(self) -> T:
        """Remove and return the top item."""
        if not self._items:  # empty stack
            raise IndexError("pop from empty stack")  # clear error
        return self._items.pop()  # O(1) from the end

    def peek(self) -> T:
        """Look at the top item without removing it."""
        if not self._items:  # empty stack
            raise IndexError("peek from empty stack")  # clear error
        return self._items[-1]  # last item is the top

    def is_empty(self) -> bool:
        """True when there is nothing in the stack."""
        return not self._items  # empty list is falsy

    def __len__(self) -> int:
        return len(self._items)  # number of items

    def __bool__(self) -> bool:
        return bool(self._items)  # truthy when not empty

    def __repr__(self) -> str:
        return f"Stack({self._items!r})"  # bottom -> top


class _Node(Generic[T]):
    """Linked-list node."""

    def __init__(self, value: T, below: Optional[_Node[T]]) -> None:
        self.value: T = value  # stored value
        self.below: Optional[_Node[T]] = below  # node under this one


class LinkedStack(Generic[T]):
    """Stack as a singly linked list: every operation is true O(1)."""

    def __init__(self) -> None:
        self._top: Optional[_Node[T]] = None  # head is the top
        self._size: int = 0  # item count

    def push(self, item: T) -> None:
        self._top = _Node(item, self._top)  # new head points to old head
        self._size += 1  # count

    def pop(self) -> T:
        if self._top is None:  # empty
            raise IndexError("pop from empty stack")  # error
        node = self._top  # current top
        self._top = node.below  # move head down
        self._size -= 1  # count
        return node.value  # return value

    def peek(self) -> T:
        if self._top is None:  # empty
            raise IndexError("peek from empty stack")  # error
        return self._top.value  # top value

    def __len__(self) -> int:
        return self._size  # count


class MinStack:
    """Stack that returns the minimum in O(1) (classic follow-up)."""

    def __init__(self) -> None:
        self._data: List[int] = []  # values
        self._mins: List[int] = []  # min so far at each depth

    def push(self, x: int) -> None:
        self._data.append(x)  # store value
        self._mins.append(x if not self._mins else min(x, self._mins[-1]))  # running min

    def pop(self) -> int:
        self._mins.pop()  # drop min snapshot
        return self._data.pop()  # drop value

    def top(self) -> int:
        return self._data[-1]  # top value

    def get_min(self) -> int:
        return self._mins[-1]  # current minimum


if __name__ == "__main__":
    s: Stack[int] = Stack()  # new stack
    for n in (1, 2, 3):  # push three values
        s.push(n)  # push
    print(s, s.peek(), len(s))  # Stack([1, 2, 3]) 3 3
    print(s.pop(), s.pop(), s.pop(), s.is_empty())  # 3 2 1 True
    try:  # popping empty
        s.pop()  # error
    except IndexError as exc:  # expected
        print("IndexError:", exc)  # message
    ls: LinkedStack[str] = LinkedStack()  # linked version
    ls.push("a"); ls.push("b")  # two items
    assert ls.pop() == "b" and ls.peek() == "a" and len(ls) == 1  # LIFO order
    ms = MinStack()  # min stack
    for v in (5, 3, 7, 3, 1):  # pushes
        ms.push(v)  # push
    assert ms.get_min() == 1  # min is 1
    ms.pop()  # remove 1
    assert ms.get_min() == 3 and ms.top() == 3  # back to 3
    ms.pop(); ms.pop()  # remove 3 and 7
    assert ms.get_min() == 3  # still 3 (first 3)
    ms.pop()  # remove first 3
    assert ms.get_min() == 5  # now 5
    d: deque = deque()  # deque also works as a stack
    d.append(1); d.append(2)  # push
    assert d.pop() == 2  # pop from the same end
    st: Stack[int] = Stack()  # fresh
    assert not st and len(st) == 0  # falsy when empty
    st.push(1)  # push
    assert st and st.peek() == 1  # truthy
    print("all tests passed")
