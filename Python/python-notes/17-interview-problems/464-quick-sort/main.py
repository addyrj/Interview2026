"""464. Quick Sort - simple and in-place versions (run: python3 main.py)."""
from typing import List  # type hints
import random  # random pivot


def quick_sort_simple(arr: List[int]) -> List[int]:
    """Readable version: O(n) extra space, new lists each call."""
    if len(arr) <= 1:  # base case
        return arr  # already sorted
    pivot: int = arr[len(arr) // 2]  # middle element as pivot
    left = [x for x in arr if x < pivot]  # smaller
    mid = [x for x in arr if x == pivot]  # equal (handles duplicates)
    right = [x for x in arr if x > pivot]  # larger
    return quick_sort_simple(left) + mid + quick_sort_simple(right)  # combine


def quick_sort(arr: List[int]) -> List[int]:
    """In-place (Lomuto partition, random pivot) on a copy. Avg O(n log n)."""
    data: List[int] = list(arr)  # copy input

    def partition(lo: int, hi: int) -> int:
        p: int = random.randint(lo, hi)  # random pivot defeats sorted-input worst case
        data[p], data[hi] = data[hi], data[p]  # move pivot to the end
        pivot: int = data[hi]  # pivot value
        store: int = lo  # boundary of the "< pivot" zone
        for i in range(lo, hi):  # scan the range
            if data[i] < pivot:  # belongs left
                data[i], data[store] = data[store], data[i]  # swap into zone
                store += 1  # grow zone
        data[store], data[hi] = data[hi], data[store]  # pivot to final place
        return store  # pivot index

    def sort(lo: int, hi: int) -> None:
        while lo < hi:  # loop on larger side to bound recursion
            p: int = partition(lo, hi)  # partition
            if p - lo < hi - p:  # left side smaller
                sort(lo, p - 1)  # recurse on smaller
                lo = p + 1  # loop on larger
            else:  # right side smaller
                sort(p + 1, hi)  # recurse on smaller
                hi = p - 1  # loop on larger

    sort(0, len(data) - 1)  # start
    return data  # sorted copy


if __name__ == "__main__":
    print(quick_sort_simple([3, 6, 8, 10, 1, 2, 1]))  # [1, 1, 2, 3, 6, 8, 10]
    print(quick_sort([3, 6, 8, 10, 1, 2, 1]))  # same
    assert quick_sort([]) == [] and quick_sort([4]) == [4]  # edges
    assert quick_sort([2] * 5000) == [2] * 5000  # all equal does not blow up
    assert quick_sort(list(range(3000))) == list(range(3000))  # already sorted
    random.seed(3)  # reproducible
    for _ in range(300):  # random tests
        arr = [random.randint(-30, 30) for _ in range(random.randint(0, 25))]  # data
        assert quick_sort(arr) == sorted(arr) == quick_sort_simple(arr)  # all agree
    print("all tests passed")
