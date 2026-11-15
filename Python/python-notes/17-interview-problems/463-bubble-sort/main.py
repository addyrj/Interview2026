"""463. Bubble Sort with early exit (run: python3 main.py)."""
from typing import List  # type hints
import random  # for test data


def bubble_sort(items: List[int]) -> List[int]:
    """Return a new sorted list. O(n^2) worst, O(n) best, stable, O(1) extra."""
    arr: List[int] = list(items)  # copy so input is untouched
    n: int = len(arr)  # length
    for end in range(n - 1, 0, -1):  # last unsorted index shrinks
        swapped: bool = False  # track whether we swapped this pass
        for i in range(end):  # compare neighbours
            if arr[i] > arr[i + 1]:  # out of order (strict > keeps stability)
                arr[i], arr[i + 1] = arr[i + 1], arr[i]  # swap
                swapped = True  # remember
        if not swapped:  # no swap means already sorted
            break  # early exit
    return arr  # sorted copy


def passes_needed(items: List[int]) -> int:
    """Count passes to show the early-exit benefit."""
    arr = list(items)  # copy
    passes = 0  # counter
    for end in range(len(arr) - 1, 0, -1):  # same loop
        passes += 1  # one more pass
        swapped = False  # reset flag
        for i in range(end):  # compare
            if arr[i] > arr[i + 1]:  # swap if needed
                arr[i], arr[i + 1] = arr[i + 1], arr[i]  # swap
                swapped = True  # flag
        if not swapped:  # sorted
            break  # stop
    return passes  # number of passes


if __name__ == "__main__":
    print(bubble_sort([5, 1, 4, 2, 8]))  # [1, 2, 4, 5, 8]
    print(passes_needed([1, 2, 3, 4, 5]), passes_needed([5, 4, 3, 2, 1]))  # 1 4
    assert bubble_sort([]) == [] and bubble_sort([1]) == [1]  # edges
    assert bubble_sort([3, 3, 1]) == [1, 3, 3]  # duplicates
    random.seed(7)  # reproducible
    for _ in range(300):  # random tests
        arr = [random.randint(-50, 50) for _ in range(random.randint(0, 20))]  # data
        assert bubble_sort(arr) == sorted(arr)  # matches built-in
    print("all tests passed")
