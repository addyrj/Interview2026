"""461. Merge Two Sorted Lists - linked list + plain lists (run: python3 main.py)."""
from __future__ import annotations  # allow Node in its own annotations
from dataclasses import dataclass  # compact node class
from typing import List, Optional  # type hints
import heapq  # for the stdlib one-liner


@dataclass
class ListNode:
    """Singly linked list node."""
    val: int  # stored value
    next: Optional[ListNode] = None  # next node or None


def build(values: List[int]) -> Optional[ListNode]:
    """Build a linked list from a Python list."""
    dummy: ListNode = ListNode(0)  # placeholder head
    tail: ListNode = dummy  # last node so far
    for v in values:  # append each value
        tail.next = ListNode(v)  # new node
        tail = tail.next  # move tail
    return dummy.next  # real head


def to_list(head: Optional[ListNode]) -> List[int]:
    """Convert a linked list back to a Python list."""
    out: List[int] = []  # result
    while head:  # until the end
        out.append(head.val)  # collect value
        head = head.next  # advance
    return out  # list of values


def merge_lists(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
    """O(n+m) time, O(1) extra space: relink existing nodes."""
    dummy: ListNode = ListNode(0)  # avoids special-casing the head
    tail: ListNode = dummy  # last node of merged list
    while a and b:  # both have nodes
        if a.val <= b.val:  # <= keeps the merge stable
            tail.next, a = a, a.next  # take from a
        else:
            tail.next, b = b, b.next  # take from b
        tail = tail.next  # move tail
    tail.next = a or b  # attach the leftover tail
    return dummy.next  # merged head


def merge_arrays(a: List[int], b: List[int]) -> List[int]:
    """Same idea for Python lists using two pointers."""
    i = j = 0  # pointers
    out: List[int] = []  # result
    while i < len(a) and j < len(b):  # both lists have items
        if a[i] <= b[j]:  # smaller goes first
            out.append(a[i]); i += 1  # take from a
        else:
            out.append(b[j]); j += 1  # take from b
    out.extend(a[i:]); out.extend(b[j:])  # leftovers
    return out  # merged list


if __name__ == "__main__":
    print(to_list(merge_lists(build([1, 2, 4]), build([1, 3, 4]))))  # [1,1,2,3,4,4]
    print(to_list(merge_lists(None, build([0]))))  # [0]
    print(list(heapq.merge([1, 2, 4], [1, 3, 4])))  # stdlib lazy merge
    assert to_list(merge_lists(build([1, 2, 4]), build([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]  # basic
    assert to_list(merge_lists(None, None)) == []  # both empty
    assert to_list(merge_lists(build([5]), None)) == [5]  # one empty
    assert to_list(merge_lists(build([1, 2, 3]), build([7, 8]))) == [1, 2, 3, 7, 8]  # no interleave
    assert merge_arrays([1, 5], [2, 3, 9]) == [1, 2, 3, 5, 9]  # arrays
    assert list(heapq.merge([1, 5], [2, 3, 9])) == merge_arrays([1, 5], [2, 3, 9])  # agree
    print("all tests passed")
