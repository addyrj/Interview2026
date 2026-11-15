---

# 141. yield from
# हिंदी में: yield from (दूसरे generator को काम सौंपना)

---

## 🔵 Simple Definition (English)
`yield from <iterable>` makes a generator hand over control to another iterable or generator. Every value of the inner one is passed straight to the caller. It replaces the loop `for x in inner: yield x` and also forwards `send()`, `throw()` and the inner generator's return value.

## 🔵 सरल परिभाषा (Hindi)
`yield from <iterable>` एक generator को दूसरे iterable या generator को control सौंपने देता है। अंदर वाले की हर value सीधे caller तक पहुँचती है। यह `for x in inner: yield x` वाले loop की जगह लेता है और `send()`, `throw()` तथा inner generator की return value भी आगे पहुँचाता है।

---

## 🔴 Problem it Solves
When a generator is split into smaller generators (for readability or recursion), the outer one must re-yield every value by hand with a loop. That is noisy, slow, and it breaks two-way communication (`send`) and return values. `yield from` does all of it correctly in one line.

## 🔴 यह क्यों बना? (Hindi)
जब एक generator को छोटे generators में बाँटते हैं (पढ़ने में आसानी या recursion के लिए), तो outer generator को हर value हाथ से loop लगाकर दोबारा yield करनी पड़ती थी। यह गंदा और धीमा है, और `send` तथा return value को भी तोड़ देता है। `yield from` यह सब एक line में सही तरीके से करता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Outer generator reaches:  result = yield from inner()
Step 2 → Python starts inner() and forwards each of its yields to the caller
Step 3 → send()/throw() from the caller go directly into inner
Step 4 → When inner finishes, its `return value` becomes the result of yield from
Step 5 → Outer continues with the next line after yield from
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → Outer generator में आता है:  result = yield from inner()
Step 2 → Python inner() शुरू करता है और उसकी हर yield caller तक भेजता है
Step 3 → caller के send()/throw() सीधे inner में जाते हैं
Step 4 → inner खत्म हो तो उसकी `return value` yield from का result बनती है
Step 5 → Outer, yield from के बाद वाली line से आगे बढ़ता है
```

---

## 🟡 Real World Example
A Swiggy catalogue crawler walks nested categories (Food → Indian → South Indian → Dosa). A recursive generator uses `yield from` to flatten the tree into one stream of dishes. An ETL job chains `yield from read_file(a)` and `yield from read_file(b)` to treat several files as one stream. Before `async`/`await`, `yield from` was how Python coroutines were written.

## 🟡 Real Example Hindi mein
Swiggy का catalogue crawler nested categories (Food → Indian → South Indian → Dosa) घूमता है। Recursive generator `yield from` से पूरे tree को dishes की एक stream में flatten कर देता है। ETL job `yield from read_file(a)` और `yield from read_file(b)` जोड़कर कई files को एक stream की तरह देखता है। `async`/`await` से पहले Python coroutines `yield from` से ही लिखी जाती थीं।

---

## 💻 Code Example — Basic
```python
# yield from basics - every line commented
from collections.abc import Generator, Iterable  # type hints


def old_way() -> Generator[int, None, None]:  # manual delegation
    for x in [1, 2, 3]:  # loop over inner values
        yield x  # re-yield each one


def new_way() -> Generator[int, None, None]:  # with yield from
    yield from [1, 2, 3]  # same result, one line


print(list(old_way()), list(new_way()))  # identical output
# Output: [1, 2, 3] [1, 2, 3]


def letters() -> Generator[str, None, None]:  # a small generator
    yield "a"  # first letter
    yield "b"  # second letter


def numbers() -> Generator[int, None, None]:  # another small generator
    yield 1  # first number
    yield 2  # second number


def combined() -> Generator[object, None, None]:  # joins them
    yield from letters()  # delegate to letters
    yield from numbers()  # then delegate to numbers
    yield "end"  # then yield own value


print(list(combined()))  # one flat stream
# Output: ['a', 'b', 1, 2, 'end']


def chars() -> Generator[str, None, None]:  # yield from works on any iterable
    yield from "hi"  # a string
    yield from (10, 20)  # a tuple (values are ints, hint is loose on purpose)
    yield from {"k": 1}  # a dict yields keys


print(list(chars()))  # mixed iterables
# Output: ['h', 'i', 10, 20, 'k']


def inner() -> Generator[int, None, str]:  # generator with a return value
    yield 1  # a value
    return "done"  # becomes the result of yield from


def outer() -> Generator[int, None, None]:  # catches the return value
    result: str = yield from inner()  # result == "done"
    print("inner returned", result)  # prove it


print(list(outer()))  # run it
# Output:
# inner returned done
# [1]
```

## 💻 Code Example — Advanced
```python
# Production style: recursion, merging sources, sub-generator return values
from collections.abc import Generator, Iterator  # type hints
from typing import Any  # for nested dicts


def flatten(tree: dict[str, Any]) -> Iterator[str]:  # walk a nested category tree
    for name, child in tree.items():  # each node
        if isinstance(child, dict):  # a sub-category
            yield from flatten(child)  # recursion delegated with yield from
        else:  # a leaf (dish)
            yield f"{name}:{child}"  # output name and price


menu: dict[str, Any] = {  # nested menu
    "South Indian": {"dosa": 60, "idli": 40},
    "North Indian": {"thali": 180, "paneer": {"butter": 220, "tikka": 240}},
}
print(list(flatten(menu)))  # fully flat list
# Output: ['dosa:60', 'idli:40', 'thali:180', 'butter:220', 'tikka:240']


def read_source(name: str, rows: list[int]) -> Generator[tuple[str, int], None, int]:
    for r in rows:  # each row
        yield name, r  # tag with the source name
    return len(rows)  # tell how many rows were read


def read_all() -> Generator[tuple[str, int], None, dict[str, int]]:  # chain sources
    counts: dict[str, int] = {}  # row counts per source
    counts["a"] = yield from read_source("a", [1, 2])  # collect return value
    counts["b"] = yield from read_source("b", [10])  # second source
    return counts  # final summary


gen = read_all()  # create
collected: list[tuple[str, int]] = []  # values seen
while True:  # manual loop to capture the final return
    try:  # next item
        collected.append(next(gen))  # store it
    except StopIteration as stop:  # finished
        print(collected, stop.value)  # data and summary
        break  # leave
# Output: [('a', 1), ('a', 2), ('b', 10)] {'a': 2, 'b': 1}


# send() is forwarded to the inner generator (a manual loop would break this)
def accumulator() -> Generator[int, int, int]:  # inner: sums sent numbers
    total: int = 0  # running sum
    while True:  # until None arrives
        n = yield total  # yield running total, receive a number
        if n is None:  # sentinel to stop
            return total  # return final sum
        total += n  # add


def session() -> Generator[int, int, None]:  # outer delegates everything
    final: int = yield from accumulator()  # forwards send() to the inner one
    print("final total", final)  # runs after inner returns


s = session()  # create
next(s)  # prime to first yield
print(s.send(5), s.send(7))  # values go straight into accumulator
# Output: 5 12
try:  # send None to finish
    s.send(None)  # type: ignore[arg-type]
except StopIteration:  # outer ends too
    pass  # ignore
# Output: final total 12


# Performance idea: yield from avoids a Python-level loop for simple delegation
import itertools  # for chain comparison


def chained() -> Iterator[int]:  # same result via itertools.chain
    return itertools.chain([1, 2], [3])  # no generator needed here


print(list(chained()))  # check
# Output: [1, 2, 3]
```

---

## 🟠 JavaScript vs Python Comparison
JavaScript has the same delegation with `yield*` inside `function*`. Python's `yield from` additionally returns the inner generator's `return` value as an expression result.

```python
# Python way
def inner():
    yield 1
    yield 2
    return "r"
def outer():
    r = yield from inner()     # r == "r"
    yield r
print(list(outer()))           # [1, 2, 'r']
```
```javascript
// JavaScript way
function* inner() { yield 1; yield 2; return "r"; }
function* outer() {
  const r = yield* inner();    // r === "r"
  yield r;
}
console.log([...outer()]);     // [1, 2, "r"]
```

Key differences: syntax is `yield*` in JS and `yield from` in Python. Both allow any iterable (arrays, strings, other generators). In Python `yield from` also works inside old-style generator coroutines; today use `await` for async code.

---

## 🟠 FastAPI Connection
Streaming endpoints often combine sources: header, many database pages, footer. `yield from` keeps the streaming function short and each part testable. Note: `yield from` cannot be used inside `async def`; there use `async for ... : yield`.

```python
# FastAPI: composed streaming report (pip install fastapi httpx)
from collections.abc import Iterator  # type hints
from fastapi import FastAPI  # app
from fastapi.responses import StreamingResponse  # streaming
from fastapi.testclient import TestClient  # test

app: FastAPI = FastAPI()  # app


def header() -> Iterator[str]:  # first part
    yield "id,amount\n"  # csv header


def body(n: int) -> Iterator[str]:  # middle part
    for i in range(1, n + 1):  # rows
        yield f"{i},{i * 100}\n"  # one row


def footer(n: int) -> Iterator[str]:  # last part
    yield f"# {n} rows\n"  # summary comment


def report(n: int) -> Iterator[str]:  # full report
    yield from header()  # delegate part 1
    yield from body(n)  # delegate part 2
    yield from footer(n)  # delegate part 3


@app.get("/report")  # GET /report?n=2
def get_report(n: int = 2) -> StreamingResponse:  # endpoint
    return StreamingResponse(report(n), media_type="text/csv")  # stream


client = TestClient(app)  # client
print(client.get("/report?n=2").text)  # body
# Output:
# id,amount
# 1,100
# 2,200
# # 2 rows
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using plain `yield` of a generator (yields the object, not its values)
```python
# Wrong - yields the generator object itself
def g():
    yield (x for x in [1, 2])
print(len(list(g())))        # 1   (one generator object)

# Right
def g():
    yield from (x for x in [1, 2])
print(list(g()))             # [1, 2]
```

❌ Mistake 2: Forgetting that `yield from` on a string splits characters
```python
# Wrong - wanted the whole word
def g():
    yield from "cat"
print(list(g()))             # ['c', 'a', 't']

# Right
def g():
    yield "cat"
print(list(g()))             # ['cat']
```

❌ Mistake 3: Using `yield from` inside `async def`
```python
# Wrong - SyntaxError
# async def f():
#     yield from [1, 2]

# Right
async def f():
    for x in [1, 2]:
        yield x
```

---

## 🧠 Tricky Interview Question

**Q**: What is the output?

```python
def inner():
    x = yield 1
    print("inner got", x)
    return "R"

def outer():
    r = yield from inner()
    print("outer got", r)
    yield "last"

g = outer()
print(next(g))
print(g.send("hello"))
print(list(outer()))
```

**Answer**:
```
1
inner got hello
outer got R
last
inner got None
outer got R
[1, 'last']
```
`send("hello")` goes straight through `yield from` into `inner`. When `inner` returns `"R"`, `outer` receives it as the value of `yield from`. In `list(outer())` no value is sent, so `x` is `None`, and `list` collects `1` and `"last"`.

---

## ⚫ Interview Questions + Answers

Q1: What is the difference between `yield from gen` and `for x in gen: yield x`?
A1: `yield from` also forwards `send()`, `throw()` and `close()`, and returns the sub-generator's `return` value. The loop does none of that and is slower.

Q2: What can follow `yield from`?
A2: Any iterable: list, tuple, string, dict, generator, `range`, etc.

Q3: How do you get the return value of a sub-generator?
A3: `result = yield from sub()`. Outside a generator, catch `StopIteration` and read `.value`.

Q4: Where is `yield from` used historically?
A4: In `asyncio` coroutines before Python 3.5 (`@asyncio.coroutine`). Modern code uses `async`/`await`.

Q5: Does `yield from` work in async generators?
A5: No, it is a `SyntaxError` there. Use `async for` with `yield`.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- Splitting a big generator into smaller ones
- Walking trees or nested structures recursively
- Combining several sources into one stream

❌ Avoid when:
- You must transform each value (use a normal loop with `yield f(x)`)
- You are inside an `async def`
- `itertools.chain` is enough (no generator needed)

---

## 📊 Visual Diagram

```
 caller ◄── a ◄── b ◄── 1 ◄── 2 ◄── "end"
              ▲                │
   combined() │ yield from letters()   (a, b)
              │ yield from numbers()   (1, 2)
              └ yield "end"

 send()/throw() flow DOWN into the active inner generator
 return value of inner flows UP as the value of `yield from`
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| `yield from` | Delegate to a sub-iterable | sub-iterable को सौंपना |
| Delegation | Passing the work to another generator | काम किसी और generator को देना |
| Sub-generator | The inner generator | अंदर वाला generator |
| Flatten | Turn nested data into one stream | nested data को सीधी stream बनाना |
| `StopIteration.value` | Where a generator's return value lives | return value का ठिकाना |
| `yield*` | JavaScript's equivalent | JavaScript में इसका रूप |

---

## ⚡ 3-Line Summary
English: `yield from x` passes every value of `x` to the caller and forwards `send`/`throw`. It also gives you the sub-generator's `return` value. Use it for recursion and composing streams.
Hindi: `yield from x` x की हर value caller को देता है और `send`/`throw` आगे भेजता है। यह sub-generator की `return` value भी देता है। Recursion और streams जोड़ने में इस्तेमाल करें।

---

## ➡️ Next Topic
**142. Generator Pipeline** — chain generators so data flows through stages one item at a time.
