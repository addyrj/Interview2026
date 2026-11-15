"""Find duplicates in a list - set, Counter, sort, brute force. Run: python main.py"""
from collections import Counter  # frequency counting
from typing import Hashable, List, Set, TypeVar  # type hints

T = TypeVar("T", bound=Hashable)  # items must be hashable


def duplicates_set(items: List[T]) -> List[T]:
    """One pass with a 'seen' set. O(n) time, O(n) space. Keeps first-duplicate order."""
    seen: Set[T] = set()  # items met so far
    dupes: List[T] = []  # items met 2+ times (listed once)
    already: Set[T] = set()  # to avoid listing the same dupe twice
    for item in items:
        if item in seen and item not in already:  # second time we see it
            dupes.append(item)
            already.add(item)
        seen.add(item)
    return dupes


def duplicates_counter(items: List[T]) -> List[T]:
    """Counter version: also gives counts if needed."""
    counts: Counter[T] = Counter(items)  # item -> count
    return [item for item, c in counts.items() if c > 1]  # keep count>1


def duplicates_sort(items: List[int]) -> List[int]:
    """O(n log n) time, O(1) extra if sorted in place: neighbours are equal."""
    data: List[int] = sorted(items)  # copy then sort
    out: List[int] = []
    for i in range(1, len(data)):
        if data[i] == data[i - 1] and (not out or out[-1] != data[i]):  # new duplicate
            out.append(data[i])
    return out


def duplicates_brute(items: List[T]) -> List[T]:
    """O(n^2) - shown only to explain why we avoid it (works for unhashable-ish thinking)."""
    out: List[T] = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in out:
                out.append(items[i])
    return out


def has_duplicates(items: List[T]) -> bool:
    """Existence check only: compare lengths. O(n)."""
    return len(items) != len(set(items))


def main() -> None:
    data: List[int] = [1, 2, 3, 2, 4, 5, 1, 2, 6]
    assert duplicates_set(data) == [2, 1]  # order of 2nd occurrence
    assert duplicates_counter(data) == [1, 2]  # order of first occurrence
    assert duplicates_sort(data) == [1, 2]
    assert sorted(duplicates_brute(data)) == [1, 2]
    assert duplicates_set([]) == [] and duplicates_set([1, 2, 3]) == []
    assert duplicates_set(["a", "b", "a"]) == ["a"]
    assert has_duplicates(data) and not has_duplicates([1, 2])
    print("duplicates:", duplicates_set(data))
    print("All duplicate tests passed")


if __name__ == "__main__":
    main()
