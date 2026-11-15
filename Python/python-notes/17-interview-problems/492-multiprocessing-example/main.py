"""Multiprocessing Example: CPU-bound work with ProcessPoolExecutor and multiprocessing.Pool."""
from __future__ import annotations

import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor


def count_primes(limit: int) -> int:
    """Deliberately CPU heavy."""
    count = 0
    for n in range(2, limit):
        if all(n % d for d in range(2, int(n ** 0.5) + 1)):
            count += 1
    return count


def worker(q: "mp.Queue[int]", n: int) -> None:
    q.put(n * n)  # processes do not share memory; send results via a Queue


if __name__ == "__main__":  # REQUIRED: spawn start method (macOS/Windows) re-imports this file
    limits = [250_000] * 4
    t0 = time.perf_counter()
    serial = [count_primes(n) for n in limits]
    t_serial = time.perf_counter() - t0

    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        parallel = list(pool.map(count_primes, limits))  # results keep input order
    t_par = time.perf_counter() - t0
    print(serial, parallel == serial)
    print(f"serial {t_serial:.2f}s parallel {t_par:.2f}s (timings vary)")
    assert parallel == serial

    q: "mp.Queue[int]" = mp.Queue()
    procs = [mp.Process(target=worker, args=(q, i)) for i in range(4)]
    for p in procs: p.start()
    got = sorted(q.get() for _ in procs)  # read before join to avoid deadlock on big payloads
    for p in procs: p.join()
    print(got, "start method:", mp.get_start_method())
    assert got == [0, 1, 4, 9]
    print("all ok")
