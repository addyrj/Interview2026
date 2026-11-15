"""468. Remove Duplicates (run: python3 main.py)."""
from typing import Hashable, Iterable, List, TypeVar  # type hints

T = TypeVar("T", bound=Hashable)  # hashable element type


def dedupe_ordered(items: Iterable[T]) -> List[T]:
    """Keep first occurrence, preserve order. O(n)."""
    return list(dict.fromkeys(items))  # dict keys are unique and ordered (3.7+)


def dedupe_seen(items: Iterable[T]) -> List[T]:
    """Same with an explicit set (works in any language style)."""
    seen: set = set()  # items already emitted
    out: List[T] = []  # result
    for x in items:  # each item
        if x not in seen:  # first time
            seen.add(x)  # mark
            out.append(x)  # keep
    return out  # unique list


def dedupe_sorted_inplace(nums: List[int]) -> int:
    """LeetCode 26: sorted list, O(1) space, return new length."""
    if not nums:  # nothing to do
        return 0  # empty
    write: int = 1  # next slot for a unique value
    for read in range(1, len(nums)):  # scan
        if nums[read] != nums[read - 1]:  # new value
            nums[write] = nums[read]  # copy forward
            write += 1  # advance writer
    return write  # unique count; nums[:write] is the answer


if __name__ == "__main__":
    print(dedupe_ordered([3, 1, 3, 2, 1]))  # [3, 1, 2]
    print(list(set([3, 1, 3, 2, 1])))  # order not guaranteed in general
    nums = [1, 1, 2, 2, 2, 3]  # sorted input
    k = dedupe_sorted_inplace(nums)  # in-place
    print(k, nums[:k])  # 3 [1, 2, 3]
    assert dedupe_ordered([]) == [] and dedupe_seen([]) == []  # empty
    assert dedupe_ordered("banana") == ["b", "a", "n"]  # strings too
    assert dedupe_ordered([3, 1, 3, 2, 1]) == dedupe_seen([3, 1, 3, 2, 1]) == [3, 1, 2]  # agree
    try:  # unhashable items fail
        dedupe_ordered([[1], [1]])  # lists are unhashable
    except TypeError as exc:  # expected
        print("TypeError:", exc)  # show message
    # unhashable fallback: O(n^2) membership on a list
    rows = [[1], [2], [1]]  # list of lists
    uniq: List[List[int]] = []  # result
    for r in rows:  # each row
        if r not in uniq:  # list membership uses ==
            uniq.append(r)  # keep
    assert uniq == [[1], [2]]  # fallback works
    print("all tests passed")
