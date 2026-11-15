"""Factorial - recursive, iterative, math.factorial, with tests. Run: python main.py"""
import math  # reference implementation
import sys  # recursion limit
from functools import reduce  # fold
from operator import mul  # multiplication as a function


def factorial_recursive(n: int) -> int:
    """n! = n * (n-1)!  Base case: 0! = 1. Depth = n (limit ~1000)."""
    if n < 0:  # factorial undefined for negatives
        raise ValueError("factorial is not defined for negative numbers")
    if n <= 1:  # base case stops the recursion
        return 1
    return n * factorial_recursive(n - 1)  # shrink the problem by 1


def factorial_iterative(n: int) -> int:
    """Loop version: O(n) time, O(1) stack. Prefer this in production."""
    if n < 0:
        raise ValueError("factorial is not defined for negative numbers")
    result: int = 1  # multiplicative identity
    for i in range(2, n + 1):  # 2..n (1 changes nothing)
        result *= i  # accumulate
    return result


def factorial_reduce(n: int) -> int:
    """Functional one-liner."""
    if n < 0:
        raise ValueError("factorial is not defined for negative numbers")
    return reduce(mul, range(2, n + 1), 1)  # initial 1 handles n=0 and n=1


def main() -> None:
    for n in range(0, 30):  # compare against the stdlib
        expected: int = math.factorial(n)
        assert factorial_recursive(n) == factorial_iterative(n) == factorial_reduce(n) == expected
    assert factorial_iterative(5) == 120
    assert len(str(factorial_iterative(100))) == 158  # Python ints never overflow
    try:  # invalid input must raise
        factorial_recursive(-1)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    limit: int = sys.getrecursionlimit()  # usually 1000
    try:  # recursion depth explodes for large n
        factorial_recursive(limit + 500)
        raise AssertionError("expected RecursionError")
    except RecursionError:
        print("recursive version hit RecursionError, iterative handled:", len(str(factorial_iterative(limit + 500))), "digits")
    print("All factorial tests passed")


if __name__ == "__main__":
    main()
