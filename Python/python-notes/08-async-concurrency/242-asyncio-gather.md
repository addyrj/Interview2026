---

# 242. asyncio.gather()
# हिंदी में: asyncio.gather() — कई कामों को एक साथ चलाकर नतीजे इकट्ठा करना

---

## 🔵 Simple Definition (English)
`asyncio.gather(*awaitables)` runs many coroutines or tasks at the same time and waits until all are done. It returns a list of results in the SAME ORDER as the arguments, not in the order they finished.

## 🔵 सरल परिभाषा (Hindi)
`asyncio.gather(*awaitables)` कई coroutines या tasks को एक ही समय में चलाता है और सब खत्म होने तक रुकता है। यह results की list उसी क्रम में लौटाता है जिस क्रम में आपने arguments दिए, खत्म होने के क्रम में नहीं।

---

## 🔴 Problem it Solves
Calling `await` one after another is sequential: three API calls of 1 second each take 3 seconds. You could create tasks by hand and await each, but that is verbose. `gather` is the one-line way to fan out N independent I/O calls and get all answers back together: about 1 second in total.

## 🔴 यह क्यों बना? (Hindi)
एक के बाद एक `await` करना क्रमवार है: 1-1 सेकंड की तीन API calls में 3 सेकंड लगते हैं। हाथ से tasks बनाकर हर एक को await करना लंबा है। `gather` N independent I/O calls को एक line में फैलाने और सब जवाब साथ में पाने का तरीका है: कुल लगभग 1 सेकंड।

---

## 🟢 How it Works — Step by Step

```
Step 1 → gather wraps every coroutine argument in a Task (tasks stay as they are)
Step 2 → All tasks are scheduled on the loop and run concurrently
Step 3 → gather returns a Future that finishes when ALL tasks finish
Step 4 → Result list = results ordered by ARGUMENT position
Step 5 → return_exceptions=False (default): the FIRST exception is raised at once;
         the other tasks are NOT cancelled, they keep running in background
Step 6 → return_exceptions=True: exceptions are placed in the list as values
Step 7 → Cancelling the gather() future cancels all its children

await gather(a(), b(), c())  ->  [ra, rb, rc]   (even if c finishes first)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → gather हर coroutine argument को Task में लपेटता है (tasks वैसे ही रहते हैं)
Step 2 → सभी tasks loop पर schedule होकर एक साथ चलते हैं
Step 3 → gather एक Future लौटाता है जो सभी tasks खत्म होने पर पूरा होता है
Step 4 → Result list = ARGUMENT की position के क्रम में results
Step 5 → return_exceptions=False (default): पहली exception तुरंत raise होती है;
         बाकी tasks cancel नहीं होते, background में चलते रहते हैं
Step 6 → return_exceptions=True: exceptions list में values की तरह रखी जाती हैं
Step 7 → gather() वाले future को cancel करने से उसके सभी children cancel होते हैं
```

---

## 🟡 Real World Example
A Swiggy home screen needs user profile, nearby restaurants, active offers and cart count. These four calls are independent, so the backend runs them with `gather` and returns in the time of the slowest one, not the sum. A price-comparison bot queries 10 e-commerce APIs concurrently. An AI app calls three embedding or LLM providers at once and uses all answers.

## 🟡 Real Example Hindi mein
Swiggy की home screen को user profile, nearby restaurants, active offers और cart count चाहिए। ये चारों calls independent हैं, इसलिए backend इन्हें `gather` से चलाता है और सबसे धीमी call के समय में लौटता है, जोड़ के समय में नहीं। Price-comparison bot 10 e-commerce APIs को एक साथ query करता है। AI app तीन embedding या LLM providers को एक साथ बुलाकर सभी जवाब इस्तेमाल करता है।

---

## 💻 Code Example — Basic
```python
# Basic: asyncio.gather
import asyncio                                              # asyncio


async def fetch(name: str, secs: float) -> str:             # fake API call
    await asyncio.sleep(secs)                               # simulate latency
    return name                                             # return its name


async def _bad() -> str:                                    # always fails
    raise ValueError("boom")                                # error


async def main() -> None:
    results = await asyncio.gather(fetch("slow", 0.2), fetch("fast", 0.05), fetch("mid", 0.1))   # run together
    print(results)                                          # order = ARGUMENT order, not finish order
    mixed = await asyncio.gather(                           # mix good and bad
        fetch("ok", 0.01), _bad(), return_exceptions=True   # exceptions returned as values
    )
    print(mixed)                                            # [ 'ok', ValueError(...) ]
    names = ["a", "b", "c"]                                 # dynamic list of work
    print(await asyncio.gather(*(fetch(n, 0.01) for n in names)))   # * unpacks a generator


asyncio.run(main())

# Output (verified on Python 3.13):
# ['slow', 'fast', 'mid']
# ['ok', ValueError('boom')]
# ['a', 'b', 'c']
```

## 💻 Code Example — Advanced
```python
# Production style: gather with limit, per-item errors, timeout, and error behaviour
import asyncio                                              # asyncio
from dataclasses import dataclass                           # result container


@dataclass
class Result:                                               # uniform result for success/failure
    url: str                                                # which request
    ok: bool                                                # did it work
    value: str | None = None                                # payload
    error: str | None = None                                # error text


async def call_api(url: str) -> str:                        # fake HTTP call
    await asyncio.sleep(0.01)                               # latency
    if "bad" in url:                                        # simulate a failing endpoint
        raise ConnectionError(f"cannot reach {url}")        # error
    return f"200 {url}"                                     # success


async def safe_call(url: str, sem: asyncio.Semaphore) -> Result:
    async with sem:                                         # limit concurrent calls
        try:                                                # isolate failure to this URL
            return Result(url, True, await asyncio.wait_for(call_api(url), timeout=1))
        except (ConnectionError, TimeoutError) as exc:      # asyncio.TimeoutError is TimeoutError in 3.11+
            return Result(url, False, error=str(exc))       # convert to data


async def fetch_all(urls: list[str], limit: int = 2) -> list[Result]:
    sem = asyncio.Semaphore(limit)                          # at most `limit` at once
    return await asyncio.gather(*(safe_call(u, sem) for u in urls))   # results keep input order


async def main() -> None:
    res = await fetch_all(["/a", "/bad1", "/b", "/c"])      # four calls, one fails
    for r in res:                                           # print each
        print(r.url, r.ok, r.value or r.error)              # compact line

    # default gather: first exception propagates, siblings keep running (NOT cancelled)
    done: list[str] = []                                    # track sibling completion

    async def slow_ok() -> None:                            # sibling that finishes later
        await asyncio.sleep(0.05)                           # slower than the failure
        done.append("sibling finished")                     # proves it kept running

    async def fail_fast() -> None:                          # fails quickly
        await asyncio.sleep(0.01)                           # shorter
        raise RuntimeError("early failure")                 # error

    try:                                                    # catch the propagated error
        await asyncio.gather(slow_ok(), fail_fast())        # default return_exceptions=False
    except RuntimeError as exc:                             # raised as soon as it happens
        print("gather raised:", exc, "| done so far:", done)   # sibling not finished yet
    await asyncio.sleep(0.1)                                # give sibling time
    print("later:", done)                                   # sibling was not cancelled


if __name__ == "__main__":
    asyncio.run(main())

# Output (verified on 3.13):
# /a True 200 /a
# /bad1 False cannot reach /bad1
# /b True 200 /b
# /c True 200 /c
# gather raised: early failure | done so far: []
# later: ['sibling finished']
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | Python | JavaScript |
|---------|--------|-----------|
| Run all, wait for all | `asyncio.gather(*aws)` | `Promise.all(promises)` |
| Collect errors as values | `return_exceptions=True` | `Promise.allSettled` |
| Order of results | argument order | array order |
| On first error | raises; others keep running | rejects; others keep running |
| Cancel the rest | not automatic (use `TaskGroup`) | not possible |
| Unpack dynamic list | `gather(*list)` | `Promise.all(list)` |

```python
# Python way — note the * to unpack a list
import asyncio                                           # stdlib

async def double(n: int) -> int:                         # coroutine
    await asyncio.sleep(0.01)                            # wait
    return n * 2                                         # value

async def main() -> None:
    print(await asyncio.gather(*(double(n) for n in [1, 2, 3])))   # [2, 4, 6]

asyncio.run(main())
```
```javascript
// JavaScript way — Promise.all takes an array
const double = async (n) => { await new Promise(r => setTimeout(r, 10)); return n * 2; };
Promise.all([1, 2, 3].map(double)).then(console.log);   // [ 2, 4, 6 ]
// Promise.allSettled(...) is the closest to gather(return_exceptions=True)
```

Key difference: `gather` takes arguments (`*list`), `Promise.all` takes one array. `return_exceptions=True` returns exception objects mixed with results; `allSettled` returns `{status, value/reason}` objects. In Python the coroutines are lazy, so `gather` is what actually starts them.

---

## 🟠 FastAPI Connection
`gather` is the standard way to call several independent services from one endpoint (profile + orders + recommendations). Total latency becomes the slowest call. Run with `TestClient` on 3.13:

```python
# FastAPI example — fan out independent calls
import asyncio                                            # gather
from fastapi import FastAPI                               # FastAPI

app: FastAPI = FastAPI()                                  # create app


async def part(name: str) -> str:                         # one downstream call
    await asyncio.sleep(0.01)                             # pretend network
    return name                                           # value


@app.get("/summary")                                      # GET /summary
async def summary() -> dict[str, list[str]]:
    a, b = await asyncio.gather(part("users"), part("orders"))   # both calls overlap
    return {"parts": [a, b]}                              # {"parts": ["users", "orders"]}
```
Real services use `return_exceptions=True` plus a check per result, so one failing downstream call (for example recommendations) returns a partial response instead of a 500.

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Awaiting in a loop instead of using `gather`
✅ Correct: build the awaitables first, then gather

```python
# Wrong — sequential, N x latency
# results = [await fetch(u) for u in urls]
# Right — concurrent
# results = await asyncio.gather(*(fetch(u) for u in urls))
```

❌ Mistake 2: Assuming results come in finish order, or that failures cancel the siblings
✅ Correct: results follow argument order; with default settings siblings keep running after an error. Use `TaskGroup` if you want automatic cancel

```python
# Wrong — thinking the fastest result is first
# first = (await asyncio.gather(slow(), fast()))[0]      # this is slow()'s result
# Right — use as_completed / wait(FIRST_COMPLETED) for "first finished"
```

❌ Mistake 3: Gathering thousands of calls without a limit
✅ Correct: guard each call with a `Semaphore` so you do not overload the server or hit rate limits

```python
# Wrong — 10,000 simultaneous connections
# await asyncio.gather(*(fetch(u) for u in ten_thousand_urls))
# Right
# sem = asyncio.Semaphore(50)
# async def limited(u): 
#     async with sem: return await fetch(u)
# await asyncio.gather(*(limited(u) for u in ten_thousand_urls))
```

---

## 🧠 Tricky Interview Question

```python
# What will this output?
import asyncio
async def ok(n: int, d: float) -> int:
    await asyncio.sleep(d)
    return n
async def bad() -> int:
    raise KeyError("k")
async def main() -> None:
    print(await asyncio.gather(ok(1, 0.05), ok(2, 0.01)))
    print(await asyncio.gather(ok(1, 0.01), bad(), return_exceptions=True))
    g = asyncio.gather(ok(1, 0.01), bad())
    try:
        await g
    except KeyError as e:
        print("KeyError", e)
    print(await asyncio.gather())
asyncio.run(main())
```
Answer: `[1, 2]`, then `[1, KeyError('k')]`, then `KeyError 'k'`, then `[]` (verified on 3.13). The first result is `[1, 2]` even though task 2 finished first, because order follows the arguments. With `return_exceptions=True` the error is returned as a value inside the list. Without it, the first exception is raised from `await g`. Calling `gather()` with no arguments is allowed and gives an empty list immediately.

---

## ⚫ Interview Questions + Answers

Q1: How is `gather` different from calling `create_task` several times?
A1: `gather` creates the tasks, waits for all of them and returns the ordered list of results in one call. With `create_task` you manage the tasks and awaits yourself. Internally `gather` uses tasks, so behaviour is concurrent in both.

Q2: What happens to the other tasks when one raises in `gather`?
A2: With the default `return_exceptions=False`, the first exception is raised to the awaiter but the other tasks are not cancelled: they continue in the background and their results/errors are ignored (later errors may only produce log warnings). For all-or-nothing semantics use `asyncio.TaskGroup` (3.11+), which cancels the siblings.

Q3: When do I use `return_exceptions=True`?
A3: When partial success is acceptable: batch jobs, fan-out to optional services, cleanup of many resources. Then loop over the results and check `isinstance(r, Exception)`. Note that `CancelledError` of the outer gather still propagates.

Q4: Does `gather` run things in parallel?
A4: It runs them concurrently on one thread: when one awaits I/O, another runs. CPU-bound coroutines do not speed up. For real parallelism put CPU work in a process pool and gather the `run_in_executor` futures.

Q5: Does the order of arguments matter?
A5: It decides the order of the returned list and the order the tasks are scheduled, but not completion time. The completion order is shown by `as_completed` or `asyncio.wait`.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- You have independent awaitables and need all of their results
- A fixed small group of calls (profile + orders + offers)
- Total time should equal the slowest call
- Combine with `return_exceptions=True` for partial results

❌ Avoid when:
- You need all-or-nothing safety with automatic cancellation; use `TaskGroup`
- You want the first finished result only; use `asyncio.wait` / `as_completed`
- Thousands of items without a concurrency limit
- Work is CPU-bound and runs in the event loop thread

---

## 📊 Visual Diagram
```
 sequential:  [ A: 1s ][ B: 1s ][ C: 1s ]            = 3 s

 gather:      [ A: 1s ]
              [ B: 1s ]                              = ~1 s
              [ C: 1s ]

 results = [ resultA, resultB, resultC ]    <- argument order, always
                 even if C finishes first

 error (default):  B raises -> gather raises now; A and C keep running unseen
 error (return_exceptions=True): results = [ra, Exception(B), rc]
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| gather | Run awaitables together, collect all results | कई awaitables साथ चलाकर results इकट्ठा करना |
| Fan-out | Start many calls from one request | एक request से कई calls शुरू करना |
| `return_exceptions` | Put errors in the result list instead of raising | Errors को raise करने की जगह list में रखना |
| Concurrency | Overlapping waits on one thread | एक thread पर waits का overlap |
| Semaphore | Limits how many run at once | एक साथ चलने वालों की सीमा |
| Partial result | Some succeeded, some failed | कुछ सफल, कुछ असफल |

---

## ⚡ 3-Line Summary
English: `gather` runs awaitables concurrently and returns results in argument order. By default the first error is raised and the siblings keep running; `return_exceptions=True` returns errors as list items. Add a `Semaphore` to limit load, and use `TaskGroup` when you want automatic cancellation.
Hindi: `gather` awaitables को concurrently चलाता है और results argument के क्रम में लौटाता है। Default में पहली error raise होती है और siblings चलते रहते हैं; `return_exceptions=True` errors को list के items बनाता है। Load सीमित करने के लिए `Semaphore` लगाएं, और automatic cancellation चाहिए तो `TaskGroup` इस्तेमाल करें।

---

## ➡️ Next Topic
**243. asyncio.wait()** — a lower-level tool that returns `(done, pending)` sets and can stop at the FIRST completed task or at a timeout.
