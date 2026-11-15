---

# 243. asyncio.wait()
# हिंदी में: asyncio.wait() — (done, pending) देने वाला low-level waiting tool

---

## 🔵 Simple Definition (English)
`asyncio.wait(tasks, timeout=None, return_when=ALL_COMPLETED)` waits for a set of Tasks and returns two sets: `done` and `pending`. Unlike `gather`, it can return early: when the FIRST task finishes, when the first one fails, or when a timeout expires. It never cancels anything and never raises the tasks' errors.

## 🔵 सरल परिभाषा (Hindi)
`asyncio.wait(tasks, timeout=None, return_when=ALL_COMPLETED)` Tasks के एक set का इंतज़ार करता है और दो sets लौटाता है: `done` और `pending`। `gather` से अलग, यह जल्दी भी लौट सकता है: जब पहला task खत्म हो, पहला fail हो, या timeout पूरा हो। यह कुछ cancel नहीं करता और tasks की errors raise नहीं करता।

---

## 🔴 Problem it Solves
`gather` waits for everything. Sometimes you want "the first answer wins" (several replicas, hedged requests), "stop waiting after 2 seconds but keep what is done", or "react as soon as any task fails". `wait` gives that control and leaves the decision about the unfinished tasks (cancel them, wait more) to you.

## 🔴 यह क्यों बना? (Hindi)
`gather` सब का इंतज़ार करता है। कभी चाहिए होता है "जो पहले जवाब दे वही जीते" (कई replicas, hedged requests), "2 सेकंड बाद इंतज़ार छोड़ो पर जो हो चुका वह रखो", या "कोई भी task fail हो तो तुरंत react करो"। `wait` यह control देता है और अधूरे tasks का फैसला (cancel करें या और इंतज़ार) आप पर छोड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Pass a collection of Tasks/Futures (NOT bare coroutines, error in 3.11+)
Step 2 → Choose return_when:
         ALL_COMPLETED (default) | FIRST_COMPLETED | FIRST_EXCEPTION
Step 3 → Optionally pass timeout=seconds (no exception on timeout, just returns)
Step 4 → wait() suspends until the condition is met
Step 5 → Returns (done, pending): two sets of tasks (order is not defined)
Step 6 → YOU read results: task.result() (raises if the task failed) or
         task.exception(); you cancel or re-wait on `pending`

done, pending = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Tasks/Futures का collection दें (bare coroutines नहीं, 3.11+ में error)
Step 2 → return_when चुनें:
         ALL_COMPLETED (default) | FIRST_COMPLETED | FIRST_EXCEPTION
Step 3 → चाहें तो timeout=seconds दें (timeout पर exception नहीं, बस लौट आता है)
Step 4 → शर्त पूरी होने तक wait() रुकता है
Step 5 → (done, pending) लौटाता है: tasks के दो sets (क्रम तय नहीं)
Step 6 → results आप पढ़ते हैं: task.result() (task fail हुआ तो raise करता है) या
         task.exception(); `pending` को आप cancel करते हैं या दोबारा wait करते हैं
```

---

## 🟡 Real World Example
A Zomato delivery-ETA service asks three routing providers at once and uses whichever answers first, cancelling the others (hedged request). A health-check dashboard pings 20 services and waits at most 2 seconds: the finished ones are shown green, the pending ones red. A job runner stops all workers as soon as one raises (`FIRST_EXCEPTION`).

## 🟡 Real Example Hindi mein
Zomato की delivery-ETA service तीन routing providers से एक साथ पूछती है और जो पहले जवाब दे वही इस्तेमाल करती है, बाकी cancel (hedged request)। Health-check dashboard 20 services को ping करता है और ज़्यादा से ज़्यादा 2 सेकंड रुकता है: जो पूरी हुईं हरी दिखती हैं, pending वाली लाल। Job runner जैसे ही कोई worker raise करे सबको रोक देता है (`FIRST_EXCEPTION`)।

---

## 💻 Code Example — Basic
```python
# Basic: asyncio.wait
import asyncio                                              # asyncio


async def work(name: str, secs: float) -> str:              # simple job
    await asyncio.sleep(secs)                               # delay
    return name                                             # result


async def main() -> None:
    tasks = {asyncio.create_task(work("a", 0.05)),          # wait() needs Tasks (not bare coroutines)
             asyncio.create_task(work("b", 0.1)),           # second task
             asyncio.create_task(work("c", 0.3))}           # slow task
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)   # return at first finish
    print(sorted(t.result() for t in done), len(pending))   # ['a'] 2
    done, pending = await asyncio.wait(pending, timeout=0.15)   # wait up to 0.15s more, no exception
    print(sorted(t.result() for t in done), len(pending))   # ['b'] 1
    for t in pending:                                       # wait() never cancels for you
        t.cancel()                                          # cancel leftovers
    await asyncio.gather(*pending, return_exceptions=True)  # let cancellation finish


asyncio.run(main())

# Output (verified on Python 3.13):
# ['a'] 2
# ['b'] 1
```

## 💻 Code Example — Advanced
```python
# Production style: hedged requests (first successful answer wins) + as_completed
import asyncio                                              # asyncio


async def replica(name: str, secs: float, fail: bool = False) -> str:   # one replica of a service
    await asyncio.sleep(secs)                               # latency
    if fail:                                                # simulate crash
        raise ConnectionError(f"{name} down")               # error
    return f"answer from {name}"                            # success


async def first_success(coros: list[tuple[str, float, bool]], timeout: float = 1.0) -> str:
    tasks = {asyncio.create_task(replica(*c)) for c in coros}   # start all replicas
    pending = tasks                                         # not finished yet
    try:                                                    # always clean up in finally
        while pending:                                      # keep waiting until one succeeds
            done, pending = await asyncio.wait(pending, timeout=timeout,
                                               return_when=asyncio.FIRST_COMPLETED)
            if not done:                                    # timeout with nothing finished
                raise TimeoutError("no replica answered")   # give up
            for t in done:                                  # inspect finished tasks
                if t.exception() is None:                   # exception() is safe on done tasks
                    return t.result()                       # winner
                print("ignored:", t.exception())            # failed replica
        raise RuntimeError("all replicas failed")           # nobody succeeded
    finally:
        for t in tasks:                                     # cancel the losers
            t.cancel()                                      # no-op for finished tasks
        await asyncio.gather(*tasks, return_exceptions=True)   # wait for cancellations


async def main() -> None:
    print(await first_success([("r1", 0.01, True), ("r2", 0.05, False), ("r3", 0.5, False)]))
    try:                                                    # all fail case
        await first_success([("x", 0.01, True), ("y", 0.02, True)])
    except RuntimeError as exc:                             # expected
        print("error:", exc)                                # all failed
    jobs = [asyncio.create_task(replica(n, s)) for n, s in [("slow", 0.1), ("fast", 0.01)]]
    for fut in asyncio.as_completed(jobs):                  # yields awaitables in finish order
        print(await fut)                                    # fast first


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13):
# ignored: r1 down
# answer from r2
# ignored: x down
# ignored: y down
# error: all replicas failed
# answer from fast
# answer from slow
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| First to finish (value) | `wait(FIRST_COMPLETED)` | `Promise.race` |
| First SUCCESS | loop with `wait` (above) | `Promise.any` |
| All finished, no throw | `wait()` (done/pending) | `Promise.allSettled` |
| Timeout without error | `wait(timeout=...)` | `Promise.race` with a timer |
| Leftover tasks | you cancel them | keep running, cannot cancel |
| Input | Tasks only | any promises |

```python
# Python way — first one wins, cancel the rest
import asyncio                                           # stdlib

async def job(n: int) -> int:                            # coroutine
    await asyncio.sleep(n / 10)                          # different delays
    return n                                             # value

async def main() -> None:
    tasks = [asyncio.create_task(job(n)) for n in (3, 1, 2)]   # must be tasks
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    print(done.pop().result())                           # 1
    for t in pending: t.cancel()                         # stop the others

asyncio.run(main())
```
```javascript
// JavaScript way — Promise.race
const job = n => new Promise(r => setTimeout(() => r(n), n * 100));
Promise.race([3, 1, 2].map(job)).then(console.log);     // 1  (others keep running, no cancel)
```

Key difference: `Promise.race` returns just the first value and rejects if the first settled promise rejected. `asyncio.wait` hands you the task objects, so you decide what to do with errors, with pending tasks, and whether to wait again.

---

## 🟠 FastAPI Connection
Typical FastAPI uses: a "fastest replica wins" lookup, or a bounded-time dashboard endpoint that returns whatever finished within the time budget plus a list of timed-out services.

```python
# FastAPI example — return what finished within a time budget
import asyncio                                            # wait, tasks
from fastapi import FastAPI                               # FastAPI

app: FastAPI = FastAPI()                                  # create app


async def check(service: str, delay: float) -> str:       # pretend health check
    await asyncio.sleep(delay)                            # latency
    return service                                        # name


@app.get("/health")                                       # GET /health
async def health() -> dict[str, list[str]]:
    services = {"db": 0.01, "cache": 0.02, "search": 5.0}   # search is very slow
    tasks = {asyncio.create_task(check(n, d), name=n) for n, d in services.items()}
    done, pending = await asyncio.wait(tasks, timeout=0.2)  # budget of 0.2 seconds
    for t in pending:                                     # give up on slow ones
        t.cancel()                                        # stop them (no leaks)
    return {"up": sorted(t.result() for t in done),       # finished in time
            "timed_out": sorted(t.get_name() for t in pending)}   # did not finish
# expected JSON: {"up": ["cache", "db"], "timed_out": ["search"]}
```
(The `wait(timeout=...)` splitting into done/pending was run in the basic example on 3.13; this endpoint itself was not run.)

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Passing bare coroutines to `wait`
✅ Correct: wrap them with `create_task` first (passing coroutines is forbidden since 3.11)

```python
# Wrong — TypeError: Passing coroutines is forbidden, use tasks explicitly.
# await asyncio.wait([work()])
# Right
# await asyncio.wait([asyncio.create_task(work())])
```

❌ Mistake 2: Forgetting to cancel `pending` tasks
✅ Correct: after an early return, cancel (and await) leftovers, or they run on as leaks

```python
# Wrong
# done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
# ... return done result, pending tasks keep running forever
# Right
# for t in pending: t.cancel()
# await asyncio.gather(*pending, return_exceptions=True)
```

❌ Mistake 3: Expecting `wait` to raise task errors or timeouts
✅ Correct: errors stay inside the tasks; call `task.result()` (raises) or `task.exception()`; a timeout simply returns with tasks in `pending`

```python
# Wrong — assuming an exception will come out of wait()
# await asyncio.wait(tasks)            # no error here even if a task failed
# Right
# done, _ = await asyncio.wait(tasks)
# for t in done:
#     if t.exception(): handle(t.exception())
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
async def ok() -> int:
    return 1
async def main() -> None:
    try:
        await asyncio.wait([ok()])
    except TypeError as e:
        print("TypeError:", e)
    t = asyncio.create_task(ok())
    done, pending = await asyncio.wait([t])
    print(len(done), len(pending))
asyncio.run(main())
```
Answer: `TypeError: Passing coroutines is forbidden, use tasks explicitly.` and then `1 0` (verified on 3.13). Python also prints a `RuntimeWarning: coroutine 'ok' was never awaited` to stderr for the rejected coroutine. In Python 3.10 and earlier, passing coroutines only gave a DeprecationWarning and they were wrapped into tasks automatically, which is why old tutorials still show it. Since 3.11 you must pass Tasks.

---

## ⚫ Interview Questions + Answers

Q1: `gather` vs `wait`, which one when?
A1: `gather` when you need all results in order (and a simple error model). `wait` when you need control: first completed, first exception, a timeout without exception, or the done/pending sets. `wait` never raises task errors and never cancels.

Q2: What are the three `return_when` values?
A2: `ALL_COMPLETED` (default): return when all finish. `FIRST_COMPLETED`: return when any finishes (success, error or cancel). `FIRST_EXCEPTION`: return when any task raises, or when all finish if none raises.

Q3: What happens on timeout?
A3: `wait` returns normally with whatever was finished in `done`, and the rest in `pending`. Nothing is cancelled and no `TimeoutError` is raised. That is different from `asyncio.wait_for` (3.11+: `asyncio.timeout()`), which cancels the awaited work and raises `TimeoutError`.

Q4: How is `as_completed` different?
A4: `as_completed(tasks)` yields awaitables in the order they finish, so you can process each result right away. `wait(FIRST_COMPLETED)` in a loop does the same but gives you the sets and more control. In 3.13 `as_completed` also works as an async iterator (`async for fut in as_completed(...)`).

Q5: How do you get the "first successful" result?
A5: Loop on `wait(pending, return_when=FIRST_COMPLETED)`: for each finished task, return `t.result()` if `t.exception()` is None; otherwise continue with the remaining `pending`. Finally, cancel the leftover tasks, as in the advanced example.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- "First one wins" patterns (replicas, hedged requests)
- Time-budgeted work that returns partial results
- Reacting to the first failure in a group
- You want errors as data, not raised

❌ Avoid when:
- You just want all the results in order; use `gather`
- You want all-or-nothing safety; use `TaskGroup`
- You only need a timeout for one awaitable; use `asyncio.timeout()` / `wait_for`
- You cannot easily create Tasks first (wrap with `create_task`)

---

## 📊 Visual Diagram
```
 tasks:  A(0.05s)   B(0.1s)   C(0.3s)

 wait(FIRST_COMPLETED)      -> returns at 0.05s
        done = {A}   pending = {B, C}

 wait(pending, timeout=0.15) -> returns at 0.2s
        done = {B}   pending = {C}          (no exception on timeout)

 you cancel C  ->  nothing left running

 wait never cancels, never raises task errors: YOU manage done/pending
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `wait` | Wait for tasks, get (done, pending) | Tasks का इंतज़ार, (done, pending) पाना |
| `FIRST_COMPLETED` | Return when any task ends | कोई भी task खत्म हो तो लौटो |
| `FIRST_EXCEPTION` | Return at first error | पहली error पर लौटो |
| Hedged request | Ask several, use the first answer | कई से पूछो, पहला जवाब लो |
| Pending | Tasks not finished yet | जो अभी खत्म नहीं हुए |
| `as_completed` | Iterate results in finish order | खत्म होने के क्रम में results |

---

## ⚡ 3-Line Summary
English: `asyncio.wait` takes Tasks and returns `(done, pending)` sets, and can stop at the first completion, first exception or a timeout. It never cancels tasks and never raises their errors, so you inspect `done` and cancel `pending` yourself. Since 3.11 you must pass Tasks, not bare coroutines.
Hindi: `asyncio.wait` Tasks लेकर `(done, pending)` sets लौटाता है, और पहली completion, पहली exception या timeout पर रुक सकता है। यह न tasks cancel करता है न उनकी errors raise करता है, इसलिए `done` आप जाँचें और `pending` खुद cancel करें। 3.11 से bare coroutines नहीं, Tasks देने होंगे।

---

## ➡️ Next Topic
**244. asyncio.create_task()** — a closer look at the function that starts background work: references, names, context, error handling and shutdown.
