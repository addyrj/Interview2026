"""465. Merge Sort - stable O(n log n) (run: python3 main.py)."""
from typing import List  # type hints
import random  # test data


def merge(left: List[int], right: List[int]) -> List[int]:
    """Merge two sorted lists into one."""
    out: List[int] = []  # result
    i = j = 0  # pointers
    while i < len(left) and j < len(right):  # both have items
        if left[i] <= right[j]:  # <= keeps equal items in original order (stable)
            out.append(left[i]); i += 1  # take left
        else:
            out.append(right[j]); j += 1  # take right
    out.extend(left[i:]); out.extend(right[j:])  # leftovers
    return out  # merged


def merge_sort(arr: List[int]) -> List[int]:
    """Always O(n log n) time, O(n) extra space, stable."""
    if len(arr) <= 1:  # base case
        return list(arr)  # copy
    mid: int = len(arr) // 2  # split point
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))  # sort halves then merge


def count_inversions(arr: List[int]) -> int:
    """Bonus: merge sort counts out-of-order pairs in O(n log n)."""
    def go(a: List[int]):  # returns (sorted, inversions)
        if len(a) <= 1:  # base
            return list(a), 0  # nothing to count
        m = len(a) // 2  # middle
        l, x = go(a[:m])  # left half
        r, y = go(a[m:])  # right half
        out, i, j, c = [], 0, 0, x + y  # merge with counter
        while i < len(l) and j < len(r):  # both non-empty
            if l[i] <= r[j]:  # in order
                out.append(l[i]); i += 1  # take left
            else:  # right item jumps over all remaining left items
                out.append(r[j]); j += 1; c += len(l) - i  # count them
        out += l[i:] + r[j:]  # leftovers
        return out, c  # result
    return go(arr)[1]  # inversion count


if __name__ == "__main__":
    print(merge_sort([38, 27, 43, 3, 9, 82, 10]))  # sorted
    print(count_inversions([2, 4, 1, 3, 5]))  # 3
    pairs = [(1, "b"), (0, "x"), (1, "a")]  # stability check data
    assert sorted(pairs, key=lambda p: p[0]) == [(0, "x"), (1, "b"), (1, "a")]  # built-in is stable
    assert merge_sort([]) == [] and merge_sort([1]) == [1]  # edges
    assert count_inversions([5, 4, 3, 2, 1]) == 10 and count_inversions([1, 2, 3]) == 0  # known values
    random.seed(5)  # reproducible
    for _ in range(300):  # random tests
        arr = [random.randint(-30, 30) for _ in range(random.randint(0, 25))]  # data
        assert merge_sort(arr) == sorted(arr)  # matches built-in
    print("all tests passed")
