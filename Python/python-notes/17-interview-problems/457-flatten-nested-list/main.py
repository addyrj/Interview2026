"""Flatten a nested list - recursive, generator, iterative stack. Run: python main.py"""
from typing import Any, Iterator, List  # type hints


def flatten_recursive(data: List[Any]) -> List[Any]:
    """Recursive: simple, but depth is limited by the recursion limit (~1000)."""
    result: List[Any] = []  # flat output
    for item in data:
        if isinstance(item, list):  # nested -> dive in
            result.extend(flatten_recursive(item))
        else:  # leaf value
            result.append(item)
    return result


def flatten_gen(data: List[Any]) -> Iterator[Any]:
    """Generator with yield from: lazy, memory friendly."""
    for item in data:
        if isinstance(item, list):
            yield from flatten_gen(item)  # delegate to the sub-generator
        else:
            yield item


def flatten_iterative(data: List[Any]) -> List[Any]:
    """Explicit stack: no recursion limit, handles very deep nesting."""
    result: List[Any] = []
    stack: List[Iterator[Any]] = [iter(data)]  # stack of iterators
    while stack:
        try:
            item: Any = next(stack[-1])  # next item of the innermost list
        except StopIteration:
            stack.pop()  # this level is finished
            continue
        if isinstance(item, list):
            stack.append(iter(item))  # go one level deeper
        else:
            result.append(item)
    return result


def flatten_one_level(data: List[List[Any]]) -> List[Any]:
    """Only 2D -> 1D: comprehension."""
    return [x for sub in data for x in sub]


def main() -> None:
    nested: List[Any] = [1, [2, [3, [4, 5]], 6], [], [[7]], "ab"]
    flat: List[Any] = [1, 2, 3, 4, 5, 6, 7, "ab"]  # strings stay whole
    assert flatten_recursive(nested) == flat
    assert list(flatten_gen(nested)) == flat
    assert flatten_iterative(nested) == flat
    assert flatten_one_level([[1, 2], [3], []]) == [1, 2, 3]
    assert flatten_recursive([]) == [] and flatten_recursive([[], [[]]]) == []
    deep: List[Any] = [1]  # 5000 levels deep
    for _ in range(5000):
        deep = [deep]
    assert flatten_iterative(deep) == [1]  # stack version survives
    try:
        flatten_recursive(deep)  # recursive version cannot
        raise AssertionError("expected RecursionError")
    except RecursionError:
        pass
    print("flat:", flatten_recursive(nested))
    print("All flatten tests passed")


if __name__ == "__main__":
    main()
