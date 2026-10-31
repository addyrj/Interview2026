---

# 039. while Loop
# हिंदी में: while Loop (शर्त पर चलने वाला loop)

---

## 🔵 Simple Definition (English)
A `while` loop keeps running its body as long as a condition stays `True`. Python checks the condition before every round. Use it when you do not know in advance how many times you need to repeat.

## 🔵 सरल परिभाषा (Hindi)
`while` loop तब तक अपनी body चलाता रहता है जब तक condition `True` रहती है। हर round से पहले condition check होती है। जब पहले से पता न हो कि कितनी बार दोहराना है, तब `while` इस्तेमाल करते हैं।

---

## 🔴 Problem it Solves
A `for` loop needs a collection or a known count. Many real tasks are "repeat until something happens": retry an API until it succeeds, poll a job until it finishes, read input until the user types "quit", keep a server loop alive. `while` handles all these condition-driven repeats.

## 🔴 यह क्यों बना? (Hindi)
`for` को collection या fixed count चाहिए। लेकिन कई काम "जब तक कुछ हो न जाए" वाले होते हैं: API तब तक retry करो जब तक success न मिले, job के finish होने तक poll करो, user के "quit" लिखने तक input लो। इन सबके लिए `while` है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Evaluate the condition
Step 2 → If False → skip body, go to optional else, exit
Step 3 → If True  → run the body
Step 4 → Body must change something so condition can become False
Step 5 → Jump back to Step 1
Step 6 → break exits immediately (and skips else)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Condition check होती है
Step 2 → False हो तो body skip, loop खत्म
Step 3 → True हो तो body चलती है
Step 4 → Body में कुछ बदलना ज़रूरी है, वरना infinite loop
Step 5 → वापस Step 1 पर; break से तुरंत बाहर
```

---

## 🟡 Real World Example
Razorpay webhook delivery: try sending an event, and if the merchant server fails, wait and retry with a growing delay until success or max attempts. An AI app polls a batch job ("is the OpenAI batch done?") every few seconds with a `while` loop. A chat bot runs `while True` reading messages.

## 🟡 Real Example Hindi mein
Razorpay webhook भेजते समय अगर merchant server fail हो, तो बढ़ती delay के साथ success या max attempts तक retry होता है। AI app में batch job का status हर कुछ सेकंड में `while` से poll होता है। Chat bot `while True` में messages पढ़ता है।

---

## 💻 Code Example — Basic
```python
# Basic while loop examples - every line commented
count: int = 0  # starting value of the counter

while count < 3:  # condition is checked before each round
    print("count is", count)  # show the current value
    count += 1  # change state, otherwise this loops forever
# Output:
# count is 0
# count is 1
# count is 2

n: int = 5  # number to count down from
while n > 0:  # runs while n is positive
    print(n, end=" ")  # print on the same line
    n -= 1  # reduce n each round
print()  # move to a new line
# Output: 5 4 3 2 1

# Walrus operator: assign and test in one line
data: list[str] = ["a", "b", "c"]  # a small stack of items
while (item := data.pop() if data else None) is not None:  # pop until empty
    print("got", item)  # use the popped item
# Output:
# got c
# got b
# got a

# while ... else: else runs when the condition becomes False (no break)
tries: int = 0  # attempts counter
while tries < 2:  # at most two tries
    tries += 1  # count this attempt
else:  # reached because no break happened
    print("finished after", tries)  # Output: finished after 2

# while True with break: the standard "loop until" pattern
total: int = 0  # running sum
numbers = iter([10, 20, 0, 99])  # fake user input, 0 means stop
while True:  # loop forever...
    value: int = next(numbers)  # take next number
    if value == 0:  # stop signal
        break  # ...until we break out
    total += value  # add to the total
print(total)  # Output: 30
```

## 💻 Code Example — Advanced
```python
# Production style: retry with exponential backoff + polling with timeout
import time  # for sleep and clocks
from typing import Callable  # type hint for functions


class TemporaryError(Exception):  # error that is worth retrying
    pass  # no extra behaviour needed


def retry(func: Callable[[], str], max_attempts: int = 4, base_delay: float = 0.01) -> str:
    attempt: int = 0  # how many tries so far
    while True:  # keep trying until success or give up
        attempt += 1  # count this try
        try:  # guard the risky call
            return func()  # success: leave the function
        except TemporaryError as exc:  # only retry known temporary errors
            if attempt >= max_attempts:  # no tries left
                raise  # re-raise the original error
            delay: float = base_delay * (2 ** (attempt - 1))  # 0.01, 0.02, 0.04...
            print(f"attempt {attempt} failed ({exc}); sleeping {delay}s")  # log it
            time.sleep(delay)  # wait before the next try


calls: dict[str, int] = {"n": 0}  # mutable counter shared with the function


def flaky() -> str:  # fails twice, then works
    calls["n"] += 1  # count calls
    if calls["n"] < 3:  # first two calls fail
        raise TemporaryError("server busy")  # simulate a failure
    return "OK"  # third call succeeds


print(retry(flaky))  # runs the retry loop
# Output:
# attempt 1 failed (server busy); sleeping 0.01s
# attempt 2 failed (server busy); sleeping 0.02s
# OK


def wait_until_done(check: Callable[[], bool], timeout: float = 0.2, every: float = 0.05) -> bool:
    deadline: float = time.monotonic() + timeout  # absolute stop time
    while time.monotonic() < deadline:  # condition uses a real clock
        if check():  # job finished?
            return True  # yes, stop polling
        time.sleep(every)  # no, wait and look again
    return False  # timed out


state: dict[str, int] = {"polls": 0}  # counts how often we looked


def job_finished() -> bool:  # pretend job completes on 3rd check
    state["polls"] += 1  # count the check
    return state["polls"] >= 3  # True from the third check


print(wait_until_done(job_finished))  # Output: True
print(wait_until_done(lambda: False))  # Output: False
```

---

## 🟠 JavaScript vs Python Comparison

```python
# Python
i = 0
while i < 3:
    print(i)
    i += 1               # no i++ in Python

while True:
    line = input_line()  # hypothetical
    if line == "q":
        break
# no do...while in Python: use while True + break
```

```javascript
// JavaScript
let i = 0;
while (i < 3) {
  console.log(i);
  i++;                   // i++ exists
}

do {
  line = readLine();
} while (line !== "q"); // do...while exists in JS
```

Key differences: Python has no `do...while` and no `++`/`--`. Python `while` supports an `else` clause. Python uses `and`/`or`/`not` in conditions instead of `&&`/`||`/`!`.

---

## 🟠 FastAPI Connection
In FastAPI, `while` shows up in long-lived connections (WebSocket receive loops), polling endpoints, and background workers. In `async` code never use a blocking `time.sleep` inside the loop; use `await asyncio.sleep`.

```python
# FastAPI WebSocket echo loop (needs: pip install fastapi)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect  # FastAPI parts

app: FastAPI = FastAPI()  # create app


@app.websocket("/ws")  # WebSocket route
async def ws_echo(ws: WebSocket) -> None:  # one function per connection
    await ws.accept()  # accept the handshake
    try:  # catch the client leaving
        while True:  # keep serving this client
            text: str = await ws.receive_text()  # wait for a message
            await ws.send_text(f"echo: {text}")  # reply
    except WebSocketDisconnect:  # client closed the socket
        pass  # loop ends cleanly
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Forgetting to update the condition variable (infinite loop)
```python
# Wrong - i never changes, loop never ends:
i = 0
# while i < 3:
#     print(i)

# Correct:
i = 0
while i < 3:
    print(i)
    i += 1
```

❌ Mistake 2: Blocking sleep in an async server loop
```python
# Wrong - blocks the whole event loop (all users freeze):
# async def poll():
#     while True:
#         time.sleep(5)

# Correct - yields control while waiting:
# async def poll():
#     while True:
#         await asyncio.sleep(5)
```

❌ Mistake 3: Retrying forever with no limit or delay
```python
# Wrong: while True: try_call()   -> hammers the server, never gives up
# Correct: use max_attempts + exponential backoff + a timeout (see Advanced example)
```

---

## 🧠 Tricky Interview Question

**Q**: What does this print?

```python
n = 0
while n < 3:
    n += 1
    if n == 2:
        continue
    print(n)
else:
    print("else", n)
```

**Answer**: `1`, `3`, then `else 3`. When `n == 2`, `continue` jumps to the condition check, skipping the print. The loop ends because the condition became False (not because of `break`), so `else` runs.

---

## ⚫ Interview Questions + Answers

Q1: When do you choose `while` over `for`?
A1: When the number of repeats is unknown and depends on a condition: retries, polling, reading until EOF, game loops. If you are walking a known collection, use `for`.

Q2: How do you write a do-while loop in Python?
A2: Python has none. Use `while True:` with the body first and a `break` at the end when the exit condition is met.

Q3: What is the walrus operator and how does it help `while`?
A3: `:=` assigns a value inside an expression. `while (chunk := f.read(1024)):` reads and tests in one line, avoiding a duplicated read before and inside the loop.

Q4: How do you prevent infinite loops in production?
A4: Use a max-attempt counter or deadline (`time.monotonic()`), add sleeps with backoff, handle cancellation (`KeyboardInterrupt`, `asyncio.CancelledError`), and log each iteration.

Q5: What does `while` `else` do?
A5: `else` runs when the condition turns False naturally. It is skipped if the loop exits through `break` (or `return`/exception).

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Retry, polling, backoff and wait-until patterns
- Reading streams or sockets until they close
- Algorithms with a changing state (binary search, two pointers)

❌ Avoid when:
- You can loop over a collection (use `for`)
- A fixed count is known (use `for ... in range(n)`)
- There is no timeout or exit path (risk of an infinite loop)

---

## 📊 Visual Diagram

```
        ┌──────────────┐
  ┌────►│ condition?   │── False ──► else (if any) ──► exit
  │     └──────┬───────┘
  │          True
  │            ▼
  │     ┌──────────────┐
  └─────│  run body    │── break ──► exit (else skipped)
        └──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Condition | Boolean test checked each round | हर round की जाँच |
| Infinite loop | Loop that never ends | कभी खत्म न होने वाला loop |
| Sentinel | Special value that means stop | रुकने का संकेत देने वाली value |
| Backoff | Growing wait between retries | retries के बीच बढ़ती देरी |
| Polling | Repeatedly checking status | बार-बार status देखना |
| Walrus `:=` | Assign inside an expression | expression के अंदर assign |

---

## ⚡ 3-Line Summary
English: `while` repeats while a condition is True and is ideal for retries, polling and "until" logic. Always change state inside the body and give the loop a limit or timeout. Python has no do-while; use `while True` plus `break`.
Hindi: `while` condition True रहने तक दोहराता है; retry, polling और "जब तक" वाले काम के लिए सही है। Body में state बदलें और limit/timeout रखें। do-while नहीं है; `while True` + `break` इस्तेमाल करें।

---

## ➡️ Next Topic
**040. break + continue + pass** — control exactly how and when a loop stops, skips or does nothing.
