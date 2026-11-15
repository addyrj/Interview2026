# Implement a singly linked list: append, prepend, delete, find, reverse, cycle check
from __future__ import annotations                # forward references
from dataclasses import dataclass                 # node as a dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")                                  # value type


@dataclass
class Node(Generic[T]):
    value: T                                      # payload
    next: Optional["Node[T]"] = None              # pointer to next node


class LinkedList(Generic[T]):
    def __init__(self) -> None:
        self.head: Optional[Node[T]] = None       # first node
        self._size = 0                            # cached length

    def prepend(self, value: T) -> None:          # O(1)
        self.head = Node(value, self.head)        # new node points to old head
        self._size += 1

    def append(self, value: T) -> None:           # O(n) without a tail pointer
        node = Node(value)                        # new node
        if self.head is None:                     # empty list
            self.head = node
        else:
            cur = self.head                       # walk to the last node
            while cur.next is not None:
                cur = cur.next
            cur.next = node                       # link at the end
        self._size += 1

    def find(self, value: T) -> Optional[Node[T]]:    # O(n)
        cur = self.head
        while cur is not None:                    # scan node by node
            if cur.value == value:
                return cur
            cur = cur.next
        return None                               # not found

    def delete(self, value: T) -> bool:           # O(n)
        dummy: Node[T] = Node(None)  # type: ignore[arg-type]   # dummy simplifies head removal
        dummy.next = self.head
        prev, cur = dummy, self.head
        while cur is not None:
            if cur.value == value:
                prev.next = cur.next              # unlink the node
                self.head = dummy.next            # head may have changed
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def reverse(self) -> None:                    # O(n) time, O(1) space
        prev: Optional[Node[T]] = None
        cur = self.head
        while cur is not None:
            nxt = cur.next                        # remember the rest
            cur.next = prev                       # flip the pointer
            prev, cur = cur, nxt                  # advance
        self.head = prev                          # prev is the new head

    def has_cycle(self) -> bool:                  # Floyd's tortoise and hare
        slow = fast = self.head
        while fast is not None and fast.next is not None:
            slow = slow.next                      # 1 step
            fast = fast.next.next                 # 2 steps
            if slow is fast:                      # they met -> cycle
                return True
        return False

    def __iter__(self) -> Iterator[T]:
        cur = self.head
        while cur is not None:
            yield cur.value                       # lazily yield values
            cur = cur.next

    def __len__(self) -> int:
        return self._size


if __name__ == "__main__":
    ll: LinkedList[int] = LinkedList()
    for n in (2, 3, 4):
        ll.append(n)
    ll.prepend(1)
    assert list(ll) == [1, 2, 3, 4] and len(ll) == 4
    assert ll.find(3) is not None and ll.find(99) is None
    assert ll.delete(1) and ll.delete(4) and not ll.delete(42)
    assert list(ll) == [2, 3]
    ll.reverse()
    assert list(ll) == [3, 2]
    assert not ll.has_cycle()
    last = ll.head.next                           # type: ignore[union-attr]
    last.next = ll.head                           # create a cycle on purpose
    assert ll.has_cycle()
    print("all linked list tests passed")
