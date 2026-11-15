# Generators: yield, send(), yield from, pipelines, streaming file reader
from itertools import islice
from typing import Generator, Iterable, Iterator


def countdown(n: int) -> Iterator[int]:
    while n > 0:
        yield n                                   # pause here, resume on next()
        n -= 1


def running_average() -> Generator[float, float, None]:
    """Coroutine style: receives values with send()."""
    total, count, avg = 0.0, 0, 0.0
    while True:
        x = yield avg                             # yield current avg, receive next x
        total += x
        count += 1
        avg = total / count


def flatten(nested: Iterable) -> Iterator:        # type: ignore[type-arg]
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)              # delegate to sub-generator
        else:
            yield item


def read_lines(lines: Iterable[str]) -> Iterator[str]:   # stage 1: clean
    for ln in lines:
        yield ln.strip()


def only_errors(lines: Iterable[str]) -> Iterator[str]:  # stage 2: filter
    return (ln for ln in lines if "ERROR" in ln)          # generator expression


def chunked(it: Iterable[int], size: int) -> Iterator[list[int]]:
    iterator = iter(it)
    while chunk := list(islice(iterator, size)):  # walrus: stop when empty
        yield chunk


def gen_with_cleanup(log: list[str]) -> Iterator[int]:
    try:
        yield 1
        yield 2
    finally:
        log.append("cleanup")                     # runs on close()


if __name__ == "__main__":
    assert list(countdown(3)) == [3, 2, 1]

    avg = running_average()
    next(avg)                                     # prime: run to first yield
    assert avg.send(10) == 10.0 and avg.send(20) == 15.0

    assert list(flatten([1, [2, [3, 4]], 5])) == [1, 2, 3, 4, 5]

    logs = ["ok\n", "ERROR disk\n", "ok\n", "ERROR net\n"]
    assert list(only_errors(read_lines(logs))) == ["ERROR disk", "ERROR net"]

    assert list(chunked(range(5), 2)) == [[0, 1], [2, 3], [4]]

    g = countdown(2)
    assert next(g) == 2 and next(g) == 1
    try:
        next(g); raise AssertionError("should stop")
    except StopIteration:
        pass

    lg: list[str] = []
    g2 = gen_with_cleanup(lg)
    next(g2); g2.close()                          # GeneratorExit triggers finally
    assert lg == ["cleanup"]

    import sys
    big_list, big_gen = [i for i in range(100_000)], (i for i in range(100_000))
    assert sys.getsizeof(big_gen) < sys.getsizeof(big_list)
    print("all generator tests passed")
