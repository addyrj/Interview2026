# Decorators from scratch: timer, retry (with args), cache, class-based counter
import functools
import time
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")                                # parameters of wrapped function
R = TypeVar("R")                                  # return type


def timer(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)                        # keep name/docstring
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:                                  # runs even on exceptions
            wrapper.last_duration = time.perf_counter() - start   # type: ignore[attr-defined]
    return wrapper


def retry(times: int = 3, delay: float = 0.0,
          exceptions: tuple[type[BaseException], ...] = (Exception,)
          ) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator FACTORY: retry(...) returns the real decorator."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: BaseException | None = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:         # only retry expected errors
                    last = exc
                    if attempt < times:
                        time.sleep(delay)
            raise last  # type: ignore[misc]      # out of attempts
        return wrapper
    return decorator


def memoize(func: Callable[..., R]) -> Callable[..., R]:
    cache: dict[tuple[Any, ...], R] = {}          # closure state
    @functools.wraps(func)
    def wrapper(*args: Any) -> R:
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    wrapper.cache = cache                         # type: ignore[attr-defined]
    return wrapper


class CountCalls:
    """Class-based decorator: __init__ takes func, __call__ runs it."""
    def __init__(self, func: Callable[..., Any]) -> None:
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        return self.func(*args, **kwargs)


if __name__ == "__main__":
    @timer
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    assert add(1, 2) == 3 and add.__name__ == "add" and add.__doc__ == "Add two numbers."
    assert add.last_duration >= 0                 # type: ignore[attr-defined]

    state = {"n": 0}
    @retry(times=3, exceptions=(ValueError,))
    def flaky() -> str:
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError("boom")
        return "ok"
    assert flaky() == "ok" and state["n"] == 3

    @retry(times=2, exceptions=(ValueError,))
    def always_fail() -> None:
        raise ValueError("nope")
    try:
        always_fail(); raise AssertionError("should raise")
    except ValueError:
        pass

    @memoize
    def fib(n: int) -> int:
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    assert fib(50) == 12586269025

    @CountCalls
    def hi() -> str:
        return "hi"
    hi(); hi()
    assert hi.calls == 2
    print("all decorator tests passed")
