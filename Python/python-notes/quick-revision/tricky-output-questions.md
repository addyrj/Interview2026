# Tricky Output Questions — Interview Ready
# हिंदी में: Output बताओ वाले Tricky Interview Questions

> Picked from the "Tricky Interview Question" sections across the notes (01-basics ... 11-fastapi). Short answer first, source note last.

## 🔷 Basics & Data Structures

### 1. Mutable default argument
```python
def add_item(item: int, bucket: list[int] = []) -> list[int]:
    bucket.append(item)  # mutates the default list
    return bucket  # returns it

print(add_item(1))
print(add_item(2))
```
**Answer:** `[1]` then `[1, 2]`. The default is evaluated once at definition time and shared by every call. Fix: `bucket=None` and create the list inside.  
**हिंदी:** default value function बनते समय एक बार बनती है, इसलिए हर call में वही list शेयर होती है। · *Source: 01-basics/002-python-vs-javascript.md*

### 2. bool is an int
```python
print(True == 1)
print(True is 1)       # SyntaxWarning, but runs
print(isinstance(True, int))
print({True: "a", 1: "b", 1.0: "c"})
print(sum([True, True, False]))
```
**Answer:** `True`, `False`, `True`, `{True: 'c'}`, `2`. `True`, `1`, `1.0` hash and compare equal, so they are one key: the first key stays, the last value wins.  
**हिंदी:** bool, int का subclass है; `True`, `1`, `1.0` एक ही dict key बन जाते हैं। · *Source: 01-basics/017-bool-boolean.md*

### 3. `items or [1]` with an empty list
```python
def f(items=None):
    items = items or [1]
    return items

print(f([]))
print(f(None))
print(None is None, None == None)
print(bool(None), type(None).__name__)
```
**Answer:** `[1]`, `[1]`, `True True`, `False NoneType`. An empty list is falsy, so `[] or [1]` picks `[1]` even though the caller passed `[]`. Use `if items is None:`.  
**हिंदी:** खाली list falsy है, इसलिए `or` default चुन लेता है; `is None` से जाँचो। · *Source: 01-basics/018-none-nonetype.md*

### 4. Chained `in`
```python
print("a" in "abc" in "xabcx")
```
**Answer:** `True`. It means `("a" in "abc") and ("abc" in "xabcx")`. `in`, `is`, `<`, `==` all chain.  
**हिंदी:** comparison operators chain होते हैं: `a in b in c` का मतलब `(a in b) and (b in c)` है। · *Source: 01-basics/033-membership-operators.md*

### 5. Precedence and `or` result
```python
print(not 1 + 1 == 2 and 3 > 2 or 0)
```
**Answer:** Prints `0` (an int, not `False`). `not True` is `False`, `False and ...` short-circuits, then `False or 0` returns the last evaluated operand.  
**हिंदी:** `or` आख़िरी evaluate हुआ operand लौटाता है, इसलिए `False` की जगह `0` छपता है। · *Source: 01-basics/034-operator-precedence.md*

### 6. zip with iterators
```python
a = iter([1, 2, 3])
b = iter("ab")
print(list(zip(a, b)))
print(next(a))
```
**Answer:** `[(1, 'a'), (2, 'b')]`, then `next(a)` raises `StopIteration`. `zip` pulled `3` from `a` before it found `b` exhausted, so `3` is lost. Put the shortest first or use `strict=True`.  
**हिंदी:** zip पहले `a` से `3` निकाल लेता है, फिर `b` खत्म दिखता है; वह `3` हमेशा के लिए गया। · *Source: 01-basics/043-zip.md*

### 7. Lambda in a loop (late binding)
```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])
```
**Answer:** `[2, 2, 2]`. Lambdas capture the variable `i`, not its value. Fix: `lambda i=i: i`.  
**हिंदी:** lambda variable को पकड़ता है, value को नहीं; इसलिए सब में आख़िरी `i` दिखता है। Fix: `i=i`। · *Source: 01-basics/044-functions.md*

### 8. Grid with `[[0] * 3] * 3`
```python
rows = [[0] * 3] * 3
rows[0][0] = 1
print(rows)

rows2 = [[0] * 3 for _ in range(3)]
rows2[0][0] = 1
print(rows2)
```
**Answer:** First: `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`. Second (comprehension): only the first row changes. `[x] * 3` repeats the SAME inner list.  
**हिंदी:** `[x] * 3` एक ही inner list को तीन बार दोहराता है; grid हमेशा comprehension से बनाओ। · *Source: 02-data-structures/053-list-comprehension.md*

### 9. Dict keys `1`, `1.0`, `True`
```python
d = {}
d[1] = "one"
d[1.0] = "ONE"
d[True] = "TRUE"
print(len(d))
print(d)
```
**Answer:** `len(d) == 1` and `d == {1: 'TRUE'}`. Equal hash and equal value means the same key; the last value overwrites.  
**हिंदी:** `1`, `1.0` और `True` का hash और equality एक जैसा है, इसलिए तीनों एक ही key हैं। · *Source: 02-data-structures/058-dictionary-complete.md*

### 10. `append` returns None, `+=` vs `+`
```python
a = [1, 2, 3]
b = a.append(4)
c = a + [5]
a += [6]
print(a, b, c)
```
**Answer:** `[1, 2, 3, 4, 6] None [1, 2, 3, 4, 5]`. `a + [5]` makes a new list; `a += [6]` mutates in place.  
**हिंदी:** `append` का return `None` होता है; list पर `+=` उसी object को बदलता है, `+` नई list बनाता है। · *Source: 02-data-structures/052-list-methods.md*

## 🔷 Functions, Closures, Iterators

### 11. Closure captures the variable
```python
def outer():
    x = 10
    def inner():
        print(x)        # reads 'x' from outer scope
    x = 20              # MUTATES 'x' AFTER inner is defined
    return inner

f = outer()
f()     # What does this print?
```
**Answer:** `20`. The closure holds the variable (cell), not the value at definition time.  
**हिंदी:** closure variable को पकड़ता है, value को नहीं; call के समय का मौजूदा मान दिखता है। · *Source: 04-functional/124-closures.md*

### 12. When does a decorator run?
```python
def reg(f):
    print("registering", f.__name__)
    return f

@reg
def one():
    pass

print("after def")
one()
one()
```
**Answer:** Prints `registering one` then `after def`; the two `one()` calls print nothing. The decorator body runs once, at definition (import) time.  
**हिंदी:** decorator definition (import) के समय एक बार चलता है, हर call पर नहीं। · *Source: 05-advanced/148-decorators-deep-dive.md*

### 13. List iterator vs dict iterator
```python
nums = [1, 2, 3]
it = iter(nums)
nums.append(4)
print(list(it))

d = {"a": 1}
it2 = iter(d)
try:
    d["b"] = 2
    next(it2)
except RuntimeError as e:
    print("RuntimeError:", e)

print(list(map(str, range(2))) == list(map(str, range(2))))
```
**Answer:** `[1, 2, 3, 4]`, `RuntimeError: dictionary changed size during iteration`, `True`. A list iterator reads the live list; a dict iterator detects a size change.  
**हिंदी:** list iterator live list पढ़ता है; dict iterate करते समय size बदले तो RuntimeError आती है। · *Source: 05-advanced/137-iterables-vs-iterators.md*

### 14. property beats the instance dict
```python
class A:
    def __init__(self):
        self._x = 0

    @property
    def x(self):
        return self._x

a = A()
a.__dict__["x"] = 99
print(a.x)
```
**Answer:** `0`. `property` is a data descriptor, so it wins over `__dict__`. A non-data descriptor such as `cached_property` would lose to the dict entry.  
**हिंदी:** property data descriptor है, इसलिए `__dict__` में लिखी value उसे नहीं हरा सकती। · *Source: 05-advanced/153-property-vs-descriptor.md*

### 15. `return` inside `finally`
```python
def f() -> str:
    try:
        return "try"
    finally:
        print("cleanup")

def g() -> str:
    for _ in range(1):
        try:
            raise ValueError("x")
        finally:
            return "swallowed"

print(f())
print(g())
```
**Answer:** `cleanup`, `try`, `swallowed`. `finally` runs before the function returns; a `return` in `finally` silently discards the in-flight exception (Python 3.14 warns via PEP 765).  
**हिंदी:** `finally` में `return` लिखा तो चल रही exception चुपचाप गायब हो जाती है। · *Source: 09-error-handling/267-suppressing-exceptions.md*

### 16. `raise ... from` vs implicit chaining
```python
try:
    try:
        1 / 0
    except ZeroDivisionError as e:
        raise ValueError("bad") from e
except ValueError as v:
    print(type(v.__cause__).__name__, type(v.__context__).__name__)
    print(v.__cause__ is v.__context__)

try:
    try:
        1 / 0
    except ZeroDivisionError:
        raise ValueError("bad")
except ValueError as v:
    print(v.__cause__, type(v.__context__).__name__, v.__suppress_context__)
```
**Answer:** `ZeroDivisionError ZeroDivisionError True`, then `None ZeroDivisionError False`. With `from e`, `__cause__` is set; without it only `__context__` is set.  
**हिंदी:** `from e` लगाने पर `__cause__` भरता है; बिना `from` के सिर्फ `__context__` भरता है। · *Source: 09-error-handling/266-exception-chaining-raise-from.md*

## 🔷 OOP

### 17. Bound method vs patched class
```python
class P:
    def show(self):
        return "P"
p = P()
f = p.show
P.show = lambda self: "patched"
print(f(), p.show())
p.show = lambda: "instance"
print(p.show(), P().show())
```
**Answer:** `P patched` then `instance patched`. `f = p.show` keeps the ORIGINAL function; the instance attribute wins over the class one.  
**हिंदी:** `p.show` पहले से bound हो चुका है, इसलिए बाद में class patch करने पर `f()` पुराना ही चलता है। · *Source: 03-oop/085-instance-methods.md*

### 18. `__eq__` priority for subclasses
```python
class X:
    def __eq__(self, other: object) -> bool:
        print("X.__eq__")
        return True

class Y(X):
    def __eq__(self, other: object) -> bool:
        print("Y.__eq__")
        return False

print(X() == Y())
print(Y() == X())
print(X() == 1)
print(X() != 1)
```
**Answer:** `Y.__eq__ False`, `Y.__eq__ False`, `X.__eq__ True`, `X.__eq__ False`. A right operand that is a subclass and overrides the reflected method is tried FIRST.  
**हिंदी:** right side का subclass अपना `__eq__` override करे तो Python उसे पहले आज़माता है। · *Source: 03-oop/105-eq-lt-gt.md*

### 19. `__slots__` and subclasses
```python
class A:
    __slots__ = ("x",)

class B(A):
    pass

b = B()
b.x = 1
b.y = 2
print(b.y, hasattr(b, "__dict__"))
a = A()
try:
    a.y = 2
except AttributeError:
    print("A blocked")
```
**Answer:** `2 True`, then `A blocked`. A subclass that skips `__slots__` gets a normal `__dict__`, so slots are not enforced for it.  
**हिंदी:** subclass ने `__slots__` नहीं लिखा तो उसे `__dict__` मिल जाता है, इसलिए पाबंदी हट जाती है। · *Source: 03-oop/108-slots.md*

## 🔷 Concurrency & Async

### 20. Two threads, `counter += 1`
```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(1_000_000):
        counter += 1    # is this thread-safe?

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)  # What will this print?
```
**Answer:** NOT 2,000,000: some smaller, non-deterministic value. `+=` is LOAD, ADD, STORE and threads can switch in between. Fix with `threading.Lock()`.  
**हिंदी:** GIL के बावजूद `counter += 1` atomic नहीं है; Lock से बचाओ। · *Source: 08-async-concurrency/229-gil.md*

### 21. Global changed in a child process
```python
import multiprocessing as mp
total = 0
def add(n):
    global total
    total += n
if __name__ == "__main__":
    ps = [mp.Process(target=add, args=(i,)) for i in range(1, 4)]
    [p.start() for p in ps]; [p.join() for p in ps]
    print(total)
```
**Answer:** `0`. Each child changes its own copy. Use `Pool.map` return values, `mp.Value`, a Queue or shared memory.  
**हिंदी:** child process अपनी copy बदलता है, parent का `total` नहीं बदलता। · *Source: 08-async-concurrency/231-multiprocessing-in-python.md*

### 22. Order in the event loop
```python
import asyncio
async def main() -> None:
    loop = asyncio.get_running_loop()
    async def coro() -> None:
        print("task")
    loop.call_soon(print, "callback")
    asyncio.create_task(coro())
    print("before await")
    await asyncio.sleep(0)
    print("after await")
asyncio.run(main())
```
**Answer:** `before await`, `callback`, `task`, `after await`. Nothing runs until `main` yields; then ready items run in scheduling order.  
**हिंदी:** `await` पर रुकने से ही loop दूसरे काम चलाता है; schedule करने भर से code नहीं चलता। · *Source: 08-async-concurrency/238-event-loop-in-python.md*

### 23. create_task ordering
```python
import asyncio
async def job(n: int) -> None:
    print("start", n)
    await asyncio.sleep(0)
    print("end", n)
async def main() -> None:
    t = asyncio.create_task(job(1))
    print("created")
    await job(2)
    print("awaited 2")
    await t
asyncio.run(main())
```
**Answer:** `created`, `start 2`, `start 1`, `end 2`, `awaited 2`, `end 1`. `create_task` only schedules; task 1 gets its first step when job 2 yields.  
**हिंदी:** `create_task` सिर्फ schedule करता है; task तभी चलता है जब main yield करे। · *Source: 08-async-concurrency/241-tasks-in-asyncio.md*

## 🔷 FastAPI & Pydantic

### 24. async def vs def with blocking sleep
```python
@app.get("/a")
async def a(): await asyncio.sleep(0.2)
@app.get("/b")
async def b(): time.sleep(0.2)
@app.get("/c")
def c(): time.sleep(0.2)
```
**Answer:** `/a` ~0.20 s, `/b` ~2.05 s, `/c` ~0.23 s. Blocking inside `async def` freezes the loop; plain `def` runs in the threadpool (40 threads by default).  
**हिंदी:** `async def` में blocking `time.sleep` loop रोकता है, जबकि `def` threadpool में चलता है। · *Source: 11-fastapi/298-fastapi-performance.md*

### 25. Route order
```python
@app.get("/orders/{order_id}")
def get_order(order_id: int): return {"order_id": order_id}

@app.get("/orders/me")
def me(): return {"order": "mine"}
```
**Answer:** Both requests give `422`. The first route matches any string, validation fails, and FastAPI does not fall back. Declare `/orders/me` first.  
**हिंदी:** पहला dynamic route हर string पकड़ लेता है; fixed path पहले declare करो। · *Source: 11-fastapi/300-path-parameters.md*

### 26. Status code of a decorator
```python
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/a", status_code=201)
def a():
    return {"x": 1}

@app.get("/b", status_code=201)
def b():
    raise HTTPException(status_code=404, detail="no")

@app.get("/c")
def c(n: int):
    return {"n": n}

cl = TestClient(app)
print(cl.get("/a").status_code, cl.get("/b").status_code, cl.get("/c?n=abc").status_code)
```
**Answer:** `201 404 422`. The decorator code is for a normal return; a raised `HTTPException` overrides it; `n=abc` fails validation before the function runs.  
**हिंदी:** decorator का status code सिर्फ सामान्य return पर लगता है; HTTPException उसे बदल देती है। · *Source: 11-fastapi/307-status-codes-in-fastapi.md*

### 27. Lax int coercion in Pydantic v2
```python
class A(BaseModel):
    n: int

for v in ("12", 12.0, 12.5, True):
    try: print(A(n=v).n)
    except ValidationError as e: print("error")
```
**Answer:** `12`, `12`, `error`, `1`. `"12"` and `12.0` convert, `12.5` loses data so it is rejected, `True` becomes `1`. With `strict=True` all four are rejected.  
**हिंदी:** lax mode में जानकारी न खोए तो convert होता है (`12.5` reject); strict mode में सब reject। · *Source: 11-fastapi/305-pydantic-v1-vs-v2.md*

### 28. Query bool and int parsing
```python
@app.get("/s")
def s(flag: bool = False, n: int = 1):
    return {"flag": flag, "n": n}

# 1) GET /s?flag=yes
# 2) GET /s?flag=maybe
# 3) GET /s?n=1.0
# 4) GET /s?n=1.5
```
**Answer:** `flag=yes` gives 200 with `True`; `flag=maybe` gives 422; `n=1.0` gives 200 with `1`; `n=1.5` gives 422.  
**हिंदी:** `yes`, `true`, `on`, `1` bool में `True` बनते हैं; `1.5` int के लिए reject होता है। · *Source: 11-fastapi/301-query-parameters.md*
