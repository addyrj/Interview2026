"""Threading Example: I/O-bound threads, Lock vs race, Queue producer/consumer, ThreadPoolExecutor."""
from __future__ import annotations

import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor


def fake_io(n: int) -> int:
    time.sleep(0.2)  # blocking I/O releases the GIL
    return n * 2


class Counter:
    def __init__(self) -> None:
        self.value = 0
        self.lock = threading.Lock()

    def inc_safe(self) -> None:
        with self.lock:  # only one thread inside at a time
            self.value += 1


def producer(q: "queue.Queue[int | None]", n: int) -> None:
    for i in range(n):
        q.put(i)
    q.put(None)  # sentinel = no more work


def consumer(q: "queue.Queue[int | None]", out: list[int]) -> None:
    while (item := q.get()) is not None:
        out.append(item * 10)


if __name__ == "__main__":
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as pool:
        res = list(pool.map(fake_io, range(5)))
    print(res, "took ~", round(time.perf_counter() - t0, 1), "s (sequential: 1.0s)")
    assert res == [0, 2, 4, 6, 8]

    c = Counter()
    threads = [threading.Thread(target=lambda: [c.inc_safe() for _ in range(50_000)]) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("locked counter:", c.value)
    assert c.value == 200_000

    q: "queue.Queue[int | None]" = queue.Queue(maxsize=3)  # bounded -> back-pressure
    out: list[int] = []
    tp = threading.Thread(target=producer, args=(q, 5)); tc = threading.Thread(target=consumer, args=(q, out))
    tp.start(); tc.start(); tp.join(); tc.join()
    print(out)
    assert out == [0, 10, 20, 30, 40]
    print("all ok")
