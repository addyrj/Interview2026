"""466. Find Missing Number in 0..n (run: python3 main.py)."""
from functools import reduce  # for XOR fold
from operator import xor  # XOR as a function
from typing import List  # type hints


def missing_sum(nums: List[int]) -> int:
    """Gauss formula: expected sum minus actual. O(n) time, O(1) space."""
    n: int = len(nums)  # numbers should be 0..n
    return n * (n + 1) // 2 - sum(nums)  # difference is the missing one


def missing_xor(nums: List[int]) -> int:
    """XOR trick: x ^ x = 0, so pairs cancel. No overflow concerns elsewhere."""
    n: int = len(nums)  # length
    return reduce(xor, nums, 0) ^ reduce(xor, range(n + 1), 0)  # leftover = missing


def missing_set(nums: List[int]) -> int:
    """Set difference: clear but O(n) space."""
    return (set(range(len(nums) + 1)) - set(nums)).pop()  # the single leftover


def missing_in_range(nums: List[int], lo: int, hi: int) -> int:
    """Variant: numbers lo..hi inclusive with one missing."""
    return (lo + hi) * (hi - lo + 1) // 2 - sum(nums)  # arithmetic series sum


if __name__ == "__main__":
    print(missing_sum([3, 0, 1]), missing_xor([9, 6, 4, 2, 3, 5, 7, 0, 1]))  # 2 8
    print(missing_in_range([1, 2, 4, 5], 1, 5))  # 3
    for fn in (missing_sum, missing_xor, missing_set):  # all approaches
        assert fn([3, 0, 1]) == 2  # middle missing
        assert fn([0, 1]) == 2  # last missing
        assert fn([1]) == 0  # first missing
        assert fn([0]) == 1  # n=1 edge
    import random  # random cross-check
    random.seed(2)  # reproducible
    for _ in range(200):  # random cases
        n = random.randint(1, 50)  # size
        full = list(range(n + 1))  # 0..n
        gone = random.choice(full)  # remove one
        full.remove(gone)  # build input
        random.shuffle(full)  # random order
        assert missing_sum(full) == missing_xor(full) == missing_set(full) == gone  # all agree
    print("all tests passed")
