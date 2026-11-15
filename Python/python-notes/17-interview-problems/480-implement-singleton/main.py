# Singleton: module-level, __new__, decorator, metaclass (thread-safe), and why FastAPI prefers DI
import threading
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class SingletonNew:
    """Way 1: override __new__. Caveat: __init__ runs on every call."""
    _instance: "SingletonNew | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "SingletonNew":
        if cls._instance is None:                 # fast check without lock
            with cls._lock:
                if cls._instance is None:         # double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance


def singleton(cls: type[T]) -> Callable[..., T]:
    """Way 2: decorator. Note: cls becomes a function, not a class."""
    instances: dict[type, Any] = {}
    lock = threading.Lock()

    def get(*a: Any, **kw: Any) -> T:
        with lock:
            if cls not in instances:
                instances[cls] = cls(*a, **kw)
            return instances[cls]
    return get


class SingletonMeta(type):
    """Way 3: metaclass. Keeps real classes and subclass support."""
    _instances: dict[type, Any] = {}
    _lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Settings(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.created = True


@singleton
class Logger:
    def __init__(self, name: str = "app") -> None:
        self.name = name


if __name__ == "__main__":
    assert SingletonNew() is SingletonNew()
    assert Settings() is Settings()
    assert Logger("a") is Logger("b") and Logger().name == "a"   # later args ignored!

    found: list[int] = []
    def worker() -> None:
        found.append(id(Settings()))              # 20 threads race for it
    ts = [threading.Thread(target=worker) for _ in range(20)]
    [t.start() for t in ts]; [t.join() for t in ts]
    assert len(set(found)) == 1                   # all got the same object

    import functools
    @functools.lru_cache(maxsize=None)            # Way 4: cached factory (FastAPI style)
    def get_settings() -> dict[str, str]:
        return {"env": "prod"}
    assert get_settings() is get_settings()
    print("all singleton tests passed")
