# Context managers: class-based, @contextmanager, async, ExitStack
import asyncio
import time
from contextlib import ExitStack, asynccontextmanager, contextmanager
from types import TracebackType
from typing import AsyncIterator, Iterator, Optional


class Timer:
    """Class-based: __enter__ / __exit__."""
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self                               # value bound by 'as'

    def __exit__(self, exc_type: Optional[type[BaseException]],
                 exc: Optional[BaseException],
                 tb: Optional[TracebackType]) -> bool:
        self.elapsed = time.perf_counter() - self.start
        return False                              # False -> do NOT swallow exceptions


@contextmanager
def transaction(log: list[str]) -> Iterator[list[str]]:
    """Generator-based: code before yield = enter, after = exit."""
    log.append("BEGIN")
    try:
        yield log
        log.append("COMMIT")                      # only if body succeeded
    except Exception:
        log.append("ROLLBACK")
        raise                                     # re-raise so caller knows
    finally:
        log.append("CLOSE")                       # always runs


class Suppress:
    """Swallows chosen exceptions (like contextlib.suppress)."""
    def __init__(self, *excs: type[BaseException]) -> None:
        self.excs = excs

    def __enter__(self) -> None:
        return None

    def __exit__(self, et, ev, tb) -> bool:       # type: ignore[no-untyped-def]
        return et is not None and issubclass(et, self.excs)   # True -> swallow


@asynccontextmanager
async def db_session(log: list[str]) -> AsyncIterator[str]:
    log.append("open")
    try:
        yield "session"
    finally:
        log.append("close")


async def _async_demo() -> list[str]:
    log: list[str] = []
    async with db_session(log) as s:
        assert s == "session"
    return log


if __name__ == "__main__":
    with Timer() as t:
        sum(range(1000))
    assert t.elapsed >= 0

    log: list[str] = []
    with transaction(log):
        pass
    assert log == ["BEGIN", "COMMIT", "CLOSE"]

    log2: list[str] = []
    try:
        with transaction(log2):
            raise RuntimeError("fail")
    except RuntimeError:
        pass
    assert log2 == ["BEGIN", "ROLLBACK", "CLOSE"]

    with Suppress(KeyError):
        {}["missing"]                             # swallowed
    try:
        with Suppress(KeyError):
            1 / 0                                 # not KeyError -> propagates
        raise AssertionError("should raise")
    except ZeroDivisionError:
        pass

    closed: list[str] = []
    with ExitStack() as stack:                    # dynamic number of contexts
        for name in ("a", "b"):
            stack.callback(closed.append, name)   # cleanups run LIFO
    assert closed == ["b", "a"]

    assert asyncio.run(_async_demo()) == ["open", "close"]
    print("all context manager tests passed")
