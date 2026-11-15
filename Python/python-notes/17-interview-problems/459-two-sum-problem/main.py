"""459. Two Sum - brute force vs hash map (run: python3 main.py)."""
from typing import Dict, List, Optional, Tuple  # type hints


def two_sum_brute(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """O(n^2) time, O(1) space: try every pair."""
    n: int = len(nums)  # number of items
    for i in range(n):  # first index
        for j in range(i + 1, n):  # second index, always after i
            if nums[i] + nums[j] == target:  # pair found
                return (i, j)  # return the indices
    return None  # no pair exists


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    """O(n) time, O(n) space: remember value -> index in a dict."""
    seen: Dict[int, int] = {}  # value -> index
    for i, value in enumerate(nums):  # one pass
        need: int = target - value  # the partner we are looking for
        if need in seen:  # partner already seen?
            return (seen[need], i)  # earlier index first
        seen[value] = i  # remember this value
    return None  # nothing matched


if __name__ == "__main__":
    print(two_sum([2, 7, 11, 15], 9))  # (0, 1)
    print(two_sum([3, 2, 4], 6))  # (1, 2)
    print(two_sum([3, 3], 6))  # (0, 1) duplicates work
    print(two_sum([1, 2], 10))  # None
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)  # basic
    assert two_sum([3, 3], 6) == (0, 1)  # duplicates
    assert two_sum([], 5) is None  # empty
    assert two_sum([5], 10) is None  # one element cannot pair with itself
    assert two_sum([-3, 4, 3, 90], 0) == (0, 2)  # negatives
    import random  # random cross-check against brute force
    random.seed(1)  # reproducible
    for _ in range(500):  # many random cases
        arr = [random.randint(-10, 10) for _ in range(random.randint(0, 8))]  # data
        t = random.randint(-15, 15)  # target
        a, b = two_sum(arr, t), two_sum_brute(arr, t)  # both solvers
        assert (a is None) == (b is None)  # agree on existence
        if a:  # if found, verify it is valid
            assert a[0] != a[1] and arr[a[0]] + arr[a[1]] == t  # valid pair
    print("all tests passed")
