"""462. Binary Search - iterative, recursive, bisect (run: python3 main.py)."""
from bisect import bisect_left, bisect_right  # stdlib helpers
from typing import List  # type hints


def binary_search(nums: List[int], target: int) -> int:
    """Return index of target or -1. O(log n) time, O(1) space."""
    lo, hi = 0, len(nums) - 1  # inclusive search window
    while lo <= hi:  # window not empty
        mid: int = lo + (hi - lo) // 2  # middle (overflow-safe habit)
        if nums[mid] == target:  # found
            return mid  # done
        if nums[mid] < target:  # target is on the right
            lo = mid + 1  # drop left half
        else:  # target is on the left
            hi = mid - 1  # drop right half
    return -1  # not found


def binary_search_rec(nums: List[int], target: int, lo: int = 0, hi: int = -2) -> int:
    """Recursive version (depth O(log n))."""
    if hi == -2:  # first call: default hi
        hi = len(nums) - 1  # last index
    if lo > hi:  # empty window
        return -1  # not found
    mid: int = (lo + hi) // 2  # middle
    if nums[mid] == target:  # found
        return mid  # index
    if nums[mid] < target:  # go right
        return binary_search_rec(nums, target, mid + 1, hi)
    return binary_search_rec(nums, target, lo, mid - 1)  # go left


def lower_bound(nums: List[int], target: int) -> int:
    """First index with nums[i] >= target (insert position)."""
    lo, hi = 0, len(nums)  # half-open window [lo, hi)
    while lo < hi:  # until window is empty
        mid: int = (lo + hi) // 2  # middle
        if nums[mid] < target:  # too small
            lo = mid + 1  # go right
        else:  # could be the answer
            hi = mid  # keep mid in window
    return lo  # insertion point


if __name__ == "__main__":
    data = [1, 3, 5, 7, 9, 11]  # sorted input
    print(binary_search(data, 7), binary_search(data, 4))  # 3 -1
    print(binary_search_rec(data, 11), lower_bound(data, 4))  # 5 2
    print(bisect_left(data, 4), bisect_right([1, 2, 2, 2, 3], 2))  # 2 4
    assert binary_search([], 1) == -1  # empty
    assert binary_search([5], 5) == 0 and binary_search([5], 4) == -1  # single
    for x in range(0, 14):  # every value in and around the data
        expected = data.index(x) if x in data else -1  # reference answer
        assert binary_search(data, x) == expected  # iterative
        assert binary_search_rec(data, x) == expected  # recursive
        assert lower_bound(data, x) == bisect_left(data, x)  # matches bisect
    print("all tests passed")
