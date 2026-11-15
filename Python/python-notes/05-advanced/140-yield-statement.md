---

# 140. yield Statement
# हिंदी में: yield Statement (function को रोककर value देना)

---

## 🔵 Simple Definition (English)
`yield` pauses a function, hands one value to the caller, and remembers exactly where it stopped. The next `next()` call resumes after the `yield`. Any function containing `yield` becomes a generator function: calling it does not run the body, it returns a generator object.

## 🔵 सरल परिभाषा (Hindi)
`yield` function को रोककर caller को एक value देता है और याद रखता है कि कहाँ रुका था। अगली `next()` call वहीं से आगे चलती है। जिस function में `yield` हो वह generator function बन जाता है: उसे call करने पर body नहीं चलती, बल्कि generator object मिलता है।

---

## 🔴 Problem it Solves
`return` ends a function and throws away all local variables. To produce many values you had to build a full list or write a class with `__next__`. `yield` gives you a lazy sequence in a few lines, with local variables and loop position preserved automatically.

## 🔴 यह क्यों बना? (Hindi)
`return` function को खत्म कर देता है और सारे local variables मिट जाते हैं। कई values देने के लिए पूरी list बनानी पड़ती थी या `__next__` वाली class लिखनी पड़ती थी। `yield` कुछ ही lines में lazy sequence देता है और local variables व loop की position अपने आप सुरक्षित रहती है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Calling gen() creates a generator object; no code runs yet
Step 2 → next(g) runs the body until the first yield
Step 3 → yield value → value goes to the caller, function is FROZEN
Step 4 → next(g) again → resumes on the line after yield, locals intact
Step 5 → Function ends (or return) → StopIteration is raised
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → gen() call से सिर्फ generator object बनता है, कोई code नहीं चलता
Step 2 → next(g) पहले yield तक body चलाता है
Step 3 → yield value → value caller को जाती है और function freeze हो जाता है
Step 4 → फिर next(g) → yield के बाद वाली line से चलता है, locals वैसे ही
Step 5 → function खत्म (या return) → StopIteration raise होता है
```

---

## 🟡 Real World Example
A Zomato analytics job reads a 5 GB orders file and yields one parsed order at a time, so memory stays flat. A RAG ingestion script yields text chunks one by one so embeddings are created in a stream. A FastAPI endpoint yields server-sent events for a live order tracker. An infinite ID generator yields invoice numbers forever without a list.

## 🟡 Real Example Hindi mein
Zomato का analytics job 5 GB की orders file पढ़कर एक-एक parsed order `yield` करता है, इसलिए memory स्थिर रहती है। RAG ingestion script text chunks एक-एक करके yield करती है ताकि embeddings stream में बनें। FastAPI endpoint live order tracker के लिए server-sent events yield करता है। Infinite ID generator बिना list के invoice numbers हमेशा देता रहता है।

---

## 💻 Code Example — Basic
```python
# Basic yield - every line commented
from collections.abc import Generator  # type hint for generators


def count_up(limit: int) -> Generator[int, None, None]:  # yields int, accepts nothing
    print("start")  # runs on the FIRST next(), not when calling count_up
    n: int = 1  # local variable survives between yields
    while n <= limit:  # loop until the limit
        yield n  # pause here and give n to the caller
        n += 1  # runs when we resume
    print("end")  # runs after the last resume


g = count_up(2)  # nothing printed: body has not started
print(type(g).__name__)  # it is a generator object
# Output: generator

print(next(g))  # runs until first yield
# Output:
# start
# 1
print(next(g))  # resumes, increments, yields again
# Output: 2
try:  # next call finishes the function
    next(g)  # prints "end", then raises StopIteration
except StopIteration:  # normal end signal
    print("finished")  # show it
# Output:
# end
# finished

print(list(count_up(3)))  # list() drives the generator to the end
# Output:
# start
# end
# [1, 2, 3]


def fruits() -> Generator[str, None, None]:  # several yields in a row
    yield "apple"  # first stop
    yield "banana"  # second stop
    yield "cherry"  # third stop


for f in fruits():  # for loop calls next() for us
    print(f)  # use each value
# Output:
# apple
# banana
# cherry

# A generator is single-use
g2 = fruits()  # create one
print(list(g2), list(g2))  # second list is empty
# Output: ['apple', 'banana', 'cherry'] []
```

## 💻 Code Example — Advanced
```python
# Production style: lazy file parsing, send(), return value, cleanup, errors
import io  # fake file for the demo
import sys  # memory check
from collections.abc import Generator, Iterator  # type hints
from typing import Any  # dict typing


def parse_orders(lines: Iterator[str]) -> Generator[dict[str, Any], None, int]:
    bad: int = 0  # count malformed lines
    for line in lines:  # stream the input
        parts: list[str] = line.strip().split(",")  # id,item,price
        if len(parts) != 3 or not parts[2].isdigit():  # validate row
            bad += 1  # remember the bad line
            continue  # skip it, do not crash the job
        yield {"id": int(parts[0]), "item": parts[1], "price": int(parts[2])}  # one order
    return bad  # becomes StopIteration.value


raw = io.StringIO("1,dosa,60\nbroken\n2,idli,40\n3,vada,x\n4,tea,10\n")  # fake file
orders = parse_orders(iter(raw))  # create generator
total: int = 0  # running total
while True:  # manual loop so we can read the return value
    try:  # ask for the next order
        order = next(orders)  # parse one line lazily
    except StopIteration as stop:  # end of data
        print("bad lines:", stop.value)  # return value is stored on the exception
        break  # leave loop
    total += order["price"]  # use the order
print("total:", total)  # sum of valid orders
# Output:
# bad lines: 2
# total: 110


def running_average() -> Generator[float, float, None]:  # two-way generator
    total_sum: float = 0.0  # sum so far
    count: int = 0  # items so far
    average: float = 0.0  # value to give back
    while True:  # runs until closed
        value: float = yield average  # yield average, RECEIVE next number
        total_sum += value  # update sum
        count += 1  # update count
        average = total_sum / count  # new average


avg = running_average()  # create
next(avg)  # prime: run to first yield
print(avg.send(10), avg.send(20), avg.send(60))  # push numbers in
# Output: 10.0 15.0 30.0
avg.close()  # stop generator (raises GeneratorExit inside)


def with_cleanup() -> Generator[int, None, None]:  # try/finally inside generator
    try:  # protect resources
        yield 1  # first value
        yield 2  # second value
    finally:  # always runs, even on close()
        print("cleanup")  # release resources


cg = with_cleanup()  # create
print(next(cg))  # take one value
# Output: 1
cg.close()  # closing triggers finally
# Output: cleanup


def naturals() -> Generator[int, None, None]:  # infinite generator
    n: int = 0  # start
    while True:  # never ends
        yield n  # give a value
        n += 1  # next


big = (i for i in range(1_000_000))  # generator expression
print(sys.getsizeof(big) < 500)  # stays tiny regardless of size
# Output: True
nat = naturals()  # infinite source
print([next(nat) for _ in range(4)])  # take only four
# Output: [0, 1, 2, 3]
```

---

## 🟠 JavaScript vs Python Comparison
Python's `yield` matches JavaScript's `yield` inside `function*`. A major difference: in Python the keyword `yield` alone makes the function a generator, and the end is signalled by `StopIteration` (JS gives `{done: true}`).

```python
# Python way
def numbers():
    yield 1
    yield 2
g = numbers()
print(next(g), next(g))      # 1 2
print(list(numbers()))       # [1, 2]
```
```javascript
// JavaScript way
function* numbers() {
  yield 1;
  yield 2;
}
const g = numbers();
console.log(g.next().value, g.next().value);   // 1 2
console.log([...numbers()]);                   // [1, 2]
```

Key differences: JS needs `function*`; Python detects `yield` automatically. JS `next()` returns `{value, done}`; Python's `next()` returns the value and raises `StopIteration` at the end. Both support two-way communication (`g.send(x)` in Python, `g.next(x)` in JS).

---

## 🟠 FastAPI Connection
Two big uses: (1) streaming large responses with `StreamingResponse(generator)`, and (2) **dependencies with `yield`** such as a database session that opens before the request and closes after it. The code after `yield` is the cleanup.

```python
# FastAPI: yield dependency (setup + cleanup) and streaming (pip install fastapi httpx)
from collections.abc import Generator, Iterator  # type hints
from fastapi import Depends, FastAPI  # core
from fastapi.responses import StreamingResponse  # streaming
from fastapi.testclient import TestClient  # tests

app: FastAPI = FastAPI()  # create app
events: list[str] = []  # record what happened


def get_session() -> Generator[dict[str, str], None, None]:  # dependency with yield
    events.append("open")  # runs before the endpoint
    session: dict[str, str] = {"user": "asha"}  # pretend DB session
    try:  # guarantee cleanup
        yield session  # injected into the endpoint
    finally:  # runs after the response is built
        events.append("close")  # cleanup


@app.get("/me")  # GET /me
def me(session: dict[str, str] = Depends(get_session)) -> dict[str, str]:  # inject
    events.append("handle")  # endpoint body
    return session  # response


def ticker() -> Iterator[str]:  # generator for streaming
    for i in range(3):  # three lines
        yield f"tick {i}\n"  # each line is sent as produced


@app.get("/ticks")  # GET /ticks
def ticks() -> StreamingResponse:  # stream response
    return StreamingResponse(ticker(), media_type="text/plain")  # stream


client = TestClient(app)  # client
print(client.get("/me").json(), events)  # show order of events
# Output: {'user': 'asha'} ['open', 'handle', 'close']
print(repr(client.get("/ticks").text))  # streamed body
# Output: 'tick 0\ntick 1\ntick 2\n'
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Expecting the body to run when the function is called
```python
# Wrong - nothing prints here
def g():
    print("hello")
    yield 1
x = g()                      # no "hello" yet

# Right - start it with next() or a loop
next(x)                      # prints hello
```

❌ Mistake 2: Using `return value` and expecting the caller to get it
```python
# Wrong - the value is hidden inside StopIteration.value
def g():
    yield 1
    return 99
print(list(g()))             # [1]   (99 is not in the list)

# Right - yield the value if the caller must see it
```

❌ Mistake 3: Consuming a generator twice
```python
# Wrong
nums = (n for n in range(3))
print(sum(nums), sum(nums))  # 3 0

# Right - recreate the generator or store a list
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def g():
    x = yield 1
    print("got", x)
    y = yield 2
    print("got", y)

it = g()
print(next(it))
print(it.send("A"))
try:
    it.send("B")
except StopIteration:
    print("stop")

def h():
    yield
print(list(h()))
```

**Answer**:
```
1
got A
2
got B
stop
[None]
```
`yield 1` pauses; `send("A")` resumes and `x` becomes `"A"`, then runs to `yield 2`. The next `send("B")` makes `y = "B"`, prints it and the function ends, raising `StopIteration`. A bare `yield` produces `None`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `return` and `yield`?
A1: `return` ends the function and discards its state. `yield` pauses it, keeps the state and can be resumed.

Q2: What does calling a generator function return?
A2: A generator object. No code runs until `next()` (or a loop) asks for a value.

Q3: How do you send a value into a generator?
A3: With `gen.send(value)`; the paused `yield` expression evaluates to that value. Call `next(gen)` once first to prime it.

Q4: What happens on `gen.close()`?
A4: `GeneratorExit` is raised at the paused `yield`, so `finally` blocks run. Catching it and yielding again causes a `RuntimeError`.

Q5: What is a generator expression?
A5: `(x * x for x in data)`: a one-line generator. It is lazy, unlike a list comprehension `[x * x for x in data]`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Data is large or infinite and processed item by item
- You build pipelines (read, clean, transform, write)
- You need setup/cleanup around a request (FastAPI `yield` dependencies)

❌ Avoid when:
- You need `len()`, indexing or several passes (use a list)
- The result is small and a list is clearer
- You must keep results after the producer is closed

---

## 📊 Visual Diagram

```
 caller                      generator body
   │  next(g) ───────────►  runs ... until yield 1
   │  ◄────────── 1         [FROZEN, locals kept]
   │  next(g) ───────────►  resumes after yield
   │  ◄────────── 2         runs ... until yield 2 [FROZEN]
   │  next(g) ───────────►  resumes ... reaches end
   │  ◄─ StopIteration ───  generator finished (value = return value)
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `yield` | Pause and give a value | रोककर value देना |
| Generator | Object made by a function with `yield` | yield वाले function से बना object |
| `send()` | Push a value into a paused generator | रुके generator में value भेजना |
| `close()` | Stop the generator early | generator को जल्दी बंद करना |
| Priming | First `next()` to reach first yield | पहले yield तक पहुँचाना |
| Lazy | Compute on demand | माँगने पर ही बनाना |

---

## ⚡ 3-Line Summary
English: `yield` pauses a function, returns a value and keeps all local state for the next resume. A function with `yield` returns a lazy, single-use generator. It is perfect for large streams, pipelines and FastAPI dependencies with cleanup.
Hindi: `yield` function को रोकता है, value देता है और अगली बार के लिए सारी local state रखता है। `yield` वाला function lazy, एक बार चलने वाला generator लौटाता है। बड़ी streams, pipelines और cleanup वाले FastAPI dependencies के लिए यह बढ़िया है।

---

## ➡️ Next Topic
**141. yield from** — delegate to another generator without writing a loop.
