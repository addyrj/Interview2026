"""Fibonacci - recursive, memoized, iterative, generator, fast doubling. Run: python main.py"""
import time  # to show the speed difference
from functools import lru_cache  # memoization
from typing import Iterator, List, Tuple  # type hints


def fib_naive(n: int) -> int:
    """O(2^n) time - the 'wrong' answer interviewers want you to improve."""
    if n < 2:  # base cases: fib(0)=0, fib(1)=1
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)  # two recursive calls


@lru_cache(maxsize=None)  # remember results
def fib_memo(n: int) -> int:
    """O(n) time, O(n) space (cache + recursion depth)."""
    if n < 2:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


def fib_iter(n: int) -> int:
    """Best simple answer: O(n) time, O(1) space."""
    a: int = 0  # fib(0)
    b: int = 1  # fib(1)
    for _ in range(n):  # slide the pair forward n times
        a, b = b, a + b  # tuple swap, no temp variable
    return a  # after n slides a == fib(n)


def fib_gen() -> Iterator[int]:
    """Infinite lazy generator."""
    a, b = 0, 1
    while True:  # never ends; caller decides when to stop
        yield a  # hand out current value
        a, b = b, a + b  # advance


def fib_series(count: int) -> List[int]:
    """First `count` numbers using the generator."""
    out: List[int] = []
    for value in fib_gen():
        if len(out) == count:  # enough numbers
            break
        out.append(value)
    return out


def fib_fast(n: int) -> Tuple[int, int]:
    """Fast doubling: returns (fib(n), fib(n+1)) in O(log n)."""
    if n == 0:
        return (0, 1)
    a, b = fib_fast(n // 2)  # solve half the problem
    c: int = a * (2 * b - a)  # fib(2k)
    d: int = a * a + b * b  # fib(2k+1)
    return (d, c + d) if n % 2 else (c, d)  # pick by parity


def main() -> None:
    assert fib_series(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    for n in range(25):  # all approaches agree
        assert fib_naive(n) == fib_memo(n) == fib_iter(n) == fib_fast(n)[0]
    assert fib_iter(90) == 2880067194370816120  # big values are exact (no overflow in Python)
    assert fib_fast(1000)[0] == fib_iter(1000)
    start: float = time.perf_counter()
    fib_naive(27)  # exponential
    naive: float = time.perf_counter() - start
    start = time.perf_counter()
    fib_iter(27)  # linear
    fast: float = time.perf_counter() - start
    assert naive > fast  # naive is always slower here
    print("fib series:", fib_series(10))
    print("All Fibonacci tests passed")


if __name__ == "__main__":
    main()
