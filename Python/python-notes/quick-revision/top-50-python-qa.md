---

# Top 50 Python Interview Q&A — Quick Revision
# हिंदी में: Python Interview के लिए 50 सबसे Important Questions

---

## Category 1: Core Python Fundamentals (Q1–Q10)

**Q1: What is the difference between `==` and `is`?**
`==` checks value equality — `[1,2] == [1,2]` is `True`. `is` checks identity (same object in memory) — `[1,2] is [1,2]` is `False`. `is` is for `None`, `True`, `False` comparisons: `if x is None:` (not `if x == None:`).

**Q2: What are mutable vs immutable types? Give examples.**
Immutable: `int`, `float`, `str`, `tuple`, `frozenset`, `bytes` — can't be changed after creation. Mutable: `list`, `dict`, `set`, `bytearray` — can be changed in place. Immutable objects are hashable (can be dict keys). Mutable objects passed to functions can be modified (shared reference).

**Q3: What is the difference between `*args` and `**kwargs`?**
`*args` collects extra positional arguments into a tuple: `def f(*args): # args = (1, 2, 3)`. `**kwargs` collects extra keyword arguments into a dict: `def f(**kwargs): # kwargs = {'a': 1}`. Order: regular args → `*args` → keyword-only args → `**kwargs`.

**Q4: What is a list comprehension vs generator expression?**
`[x**2 for x in range(n)]` — list comprehension: creates a list immediately, O(n) memory. `(x**2 for x in range(n))` — generator expression: lazy, O(1) memory. Use `[]` when you need random access or multiple iterations; use `()` for large data or single-pass processing.

**Q5: What is the difference between `deepcopy` and `copy`?**
`copy.copy()` (shallow copy): creates new object but nested objects are still references. `copy.deepcopy()` (deep copy): recursively copies all nested objects. For `[[1,2],[3,4]]`: shallow copy → inner lists are still shared; deep copy → inner lists are new independent lists.

**Q6: What are Python's built-in data types?**
Numeric: `int`, `float`, `complex`. Sequence: `str`, `list`, `tuple`, `range`. Mapping: `dict`. Set: `set`, `frozenset`. Boolean: `bool`. Binary: `bytes`, `bytearray`. None: `NoneType`. Plus: `type`, `function`, `module`, `generator`, etc.

**Q7: What is duck typing?**
"If it walks like a duck and quacks like a duck, it is a duck." Python doesn't check the type — it checks if the object supports the required operations. `for x in obj` works if `obj` has `__iter__` — whether it's a list, tuple, generator, custom class, doesn't matter. Enables more flexible, reusable code.

**Q8: What is the walrus operator `:=` (Python 3.8+)?**
Assignment expression — assigns and returns a value in one step. Use in `while` loops and comprehensions: `while chunk := f.read(8192): process(chunk)`. In comprehension: `[y for x in data if (y := transform(x)) > 0]` — avoids calling `transform(x)` twice.

**Q9: What is `__all__` in a Python module?**
`__all__ = ["func1", "ClassA"]` defines what names are exported when someone does `from module import *`. Without `__all__`, `import *` imports all names that don't start with `_`. Best practice: always define `__all__` in public modules to explicitly control the public API.

**Q10: What is the difference between `classmethod`, `staticmethod`, and regular method?**
Regular method: first arg is `self` (instance). `@classmethod`: first arg is `cls` (class itself) — can create instances (`cls()`), can be overridden in subclasses. `@staticmethod`: no implicit first arg — just a function in the class namespace. Use `classmethod` for factory methods; `staticmethod` for utility functions that logically belong to the class.

---

## Category 2: OOP (Q11–Q17)

**Q11: What is MRO (Method Resolution Order)?**
The order Python searches classes when looking up a method in inheritance. Python uses C3 linearization algorithm. `ClassName.__mro__` shows the order. In multiple inheritance: `class C(A, B)` — MRO is C → A → B → object. This prevents the "diamond problem."

**Q12: What is `__init__` vs `__new__`?**
`__new__(cls)` is called first — creates and returns a new instance. `__init__(self)` is called second — initializes the instance. Override `__new__` for: Singleton pattern, subclassing immutable types (`int`, `str`), instance caching/pooling. For most classes, only `__init__` is needed.

**Q13: What are abstract classes?**
`from abc import ABC, abstractmethod`. A class with `@abstractmethod` can't be instantiated — you must subclass it and implement all abstract methods. Use for defining interfaces/contracts: `class Shape(ABC): @abstractmethod def area(self): ...`. Subclass that doesn't implement `area` → `TypeError` on instantiation.

**Q14: What is the difference between `__str__` and `__repr__`?**
`__str__`: human-readable, called by `print()` and `str()` — e.g., `"₹500.00"`. `__repr__`: developer-readable, called by `repr()` and REPL — should be unambiguous, ideally `eval(repr(obj)) == obj` — e.g., `"Money(500.0, 'INR')"`. Always define `__repr__`; define `__str__` for user-facing output. `__str__` falls back to `__repr__` if not defined.

**Q15: What is a dataclass?**
`@dataclass` auto-generates `__init__`, `__repr__`, `__eq__` from type-annotated class attributes. `@dataclass(frozen=True)` also generates `__hash__`. Reduces boilerplate. `field(default_factory=list)` for mutable defaults. Pydantic `BaseModel` is like `@dataclass` + validation.

**Q16: What is `super()` and when should you use it?**
`super()` returns a proxy to the parent class. `super().__init__()` calls the parent's `__init__`. In multiple inheritance, `super()` follows MRO — it doesn't always call the direct parent. Always use `super()` instead of `ParentClass.__init__(self)` to properly support multiple inheritance.

**Q17: What is the Descriptor Protocol?**
An object is a descriptor if it defines `__get__`, `__set__`, or `__delete__`. When a class attribute is a descriptor, accessing it calls `__get__`. Python's `property`, `classmethod`, `staticmethod` are implemented as descriptors. `@property` is syntactic sugar for creating a descriptor for a computed attribute.

---

## Category 3: Functional Programming (Q18–Q24)

**Q18: What is a closure?**
An inner function that captures variables from its enclosing scope — even after the outer function returns. Three conditions: (1) nested function, (2) inner function uses outer variable, (3) outer function returns inner function. Captured variables stored in `__closure__` cells. Foundation of decorators.

**Q19: What is a decorator?**
A function that takes a function and returns a modified function. Applied with `@decorator` syntax. Standard pattern: define `wrapper(*args, **kwargs)` inside, call `func(*args, **kwargs)`, add before/after logic, return `wrapper`. Always use `@functools.wraps(func)` to preserve `func.__name__` and `__doc__`.

**Q20: What is `functools.partial`?**
Creates a new function with some arguments pre-filled: `double = partial(multiply, factor=2)`. Avoids lambda for simple cases, creates cleaner APIs. Useful for: click handlers, callback registration, `sorted(key=partial(operator.itemgetter, 'name'))`.

**Q21: What does `map`, `filter`, `reduce` do?**
`map(func, iterable)` → lazy iterator of `func(item)` for each item. `filter(func, iterable)` → lazy iterator of items where `func(item)` is truthy. `reduce(func, iterable)` → single value by applying `func(accumulator, item)` left to right (from `functools`). In modern Python, prefer list comprehensions/generator expressions over `map`/`filter` for readability.

**Q22: What is the difference between `sorted()` and `list.sort()`?**
`sorted(iterable, key=..., reverse=...)` → returns NEW sorted list (works on any iterable). `list.sort(key=..., reverse=...)` → sorts in-place, returns `None`. Both use Timsort — O(n log n) stable sort. `key` function is called once per element for comparison (Schwartzian transform). Example: `sorted(users, key=lambda u: u.age)`.

**Q23: What is `itertools` and name 5 important functions?**
`itertools` provides lazy iterators for combinatorial operations: `chain(*iterables)` — flatten multiple iterables. `islice(iterable, n)` — take first n items lazily. `groupby(iterable, key)` — group consecutive items. `combinations(iterable, r)` — all r-length combinations. `product(*iterables)` — Cartesian product. All are lazy (memory efficient).

**Q24: What is `functools.lru_cache`?**
Decorator that caches function results based on arguments. `@lru_cache(maxsize=128)` — LRU cache with 128 entries. `@cache` (Python 3.9+) — unbounded cache. Works only with hashable arguments. `func.cache_info()` returns hits, misses, maxsize, currsize. `func.cache_clear()` empties the cache.

---

## Category 4: Generators and Iterators (Q25–Q28)

**Q25: What is the iterator protocol?**
An object is iterable if it has `__iter__()` which returns an iterator. An iterator has `__next__()` that returns next value or raises `StopIteration`. `for` loop calls `iter(obj)` then repeatedly calls `next()` until `StopIteration`. Every iterator is iterable (`__iter__` returns `self`).

**Q26: What is `yield from`?**
`yield from iterable` delegates to a sub-generator: yields each item from the sub-generator. Equivalent to `for item in iterable: yield item` but more efficient (C-level loop). Also properly forwards `.send()`, `.throw()`, `.close()` to the sub-generator. Used for generator composition and tree traversal.

**Q27: What is a generator expression vs list comprehension performance?**
`list(x**2 for x in range(1_000_000))` and `[x**2 for x in range(1_000_000)]` produce the same result but at different times. Generator expression: O(1) memory — computes lazily. List comprehension: O(n) memory — computes all at once. When passing to `sum()`, `min()`, `max()`: use generator expression (no need to build intermediate list): `sum(x**2 for x in data)`.

**Q28: What is the difference between `return` and `yield`?**
`return` ends the function completely, destroys the frame. `yield` pauses execution, saves the entire frame (local variables, instruction pointer), sends a value to the caller. On the next `next()` call, execution resumes from after the `yield`. A function with any `yield` statement becomes a generator function — calling it returns a generator object without running any code.

---

## Category 5: Async and Concurrency (Q29–Q36)

**Q29: What is the GIL?**
Global Interpreter Lock — a mutex that allows only one thread to execute Python bytecode at a time in CPython. Reason: CPython's memory management (reference counting) is not thread-safe without a lock. Effect: Python threads can't run Python code in parallel on multiple cores. Workaround: use `multiprocessing` for CPU-bound, or `asyncio` for I/O-bound.

**Q30: When are threads effective despite the GIL?**
When threads are waiting for I/O (network, file, DB), the GIL is released during the wait. So 10 threads doing network requests concurrently DO run effectively in parallel from a wall-clock time perspective. The GIL blocks CPU-bound Python code, not C-level I/O operations.

**Q31: What is an event loop in asyncio?**
The event loop is the core of asyncio — it manages and runs coroutines and I/O callbacks. It continuously checks: (1) are any I/O operations ready? (2) are any tasks scheduled to run? It runs tasks that are ready and suspends tasks waiting for I/O. `asyncio.run(main())` creates an event loop and runs `main()` until it completes.

**Q32: What is the difference between `asyncio.gather()` and `asyncio.create_task()`?**
`create_task(coro)` schedules a coroutine to run, returns a `Task` immediately (fire and forget or track later). `gather(*coroutines)` creates tasks AND waits for all of them, returns results in input order (not completion order). Use `create_task` when you want tasks to run in background; use `gather` when you need all results before proceeding.

**Q33: What is `async with` and `async for`?**
`async with` uses `__aenter__` and `__aexit__` — async context manager (for resources that require async I/O to set up/tear down, e.g., DB connections). `async for` uses `__aiter__` and `__anext__` — async iterable (for data that arrives asynchronously, e.g., streaming WebSocket messages, async DB cursor).

**Q34: Why can't you use `time.sleep()` in an async function?**
`time.sleep()` blocks the thread — the event loop can't run other coroutines during the sleep. Use `await asyncio.sleep(seconds)` which yields control back to the event loop during the pause. Rule: never call blocking I/O, `time.sleep()`, `requests.get()`, or other synchronous blocking code directly in an `async def` function.

**Q35: What is `asyncio.Semaphore` and when to use it?**
`Semaphore(n)` allows at most `n` coroutines to execute a section simultaneously. Use it to limit concurrent requests to an external API (rate limiting), limit DB connection pool usage, prevent overwhelming a service. `async with sem: await make_request()` — if `n` slots are taken, the coroutine waits.

**Q36: When to use threads vs asyncio vs multiprocessing?**
**asyncio**: I/O-bound, async-compatible code (best for new code). **threads**: I/O-bound, can't use async (legacy sync libraries). **multiprocessing**: CPU-bound (image processing, ML inference, data crunching). Never: threads for CPU-bound (GIL), asyncio for CPU-heavy work (blocks the event loop).

---

## Category 6: FastAPI and Pydantic (Q37–Q43)

**Q37: What is FastAPI's dependency injection system?**
`Depends(callable)` declares a dependency. FastAPI calls the callable, injects the return value into the route function parameter. Dependencies can depend on other dependencies (nested). Same dependency is called only ONCE per request (caching, controlled by `use_cache=True` default). Use `yield` for cleanup-based dependencies (DB sessions, locks).

**Q38: What is the difference between Pydantic v1 and v2?**
V2 is 5-50x faster (Rust core). Key API changes: `@validator` → `@field_validator` (must be `@classmethod`), `.dict()` → `.model_dump()`, `.json()` → `.model_dump_json()`, `parse_obj()` → `model_validate()`, `class Config` → `model_config = ConfigDict(...)`, `orm_mode = True` → `from_attributes = True`.

**Q39: What does `response_model` do in FastAPI?**
`@app.get("/path", response_model=SomeModel)` filters the route's return value through `SomeModel`. Fields not in `SomeModel` are excluded (security: prevents leaking `hashed_password`). Fields in `SomeModel` but not in the return value use defaults. Also auto-generates OpenAPI response schema.

**Q40: What is FastAPI's `lifespan`?**
`@asynccontextmanager async def lifespan(app):` — code before `yield` runs on startup, code after `yield` runs on shutdown. Used for: creating DB connection pools, connecting to Redis, loading ML models. Passed as `FastAPI(lifespan=lifespan)`. Replaces deprecated `@app.on_event("startup")`.

**Q41: What are Pydantic validators — `field_validator` vs `model_validator`?**
`@field_validator("field_name") @classmethod def validate_field(cls, v): ...` — validates one field, receives its value, must return the (possibly transformed) value. `@model_validator(mode="after") def validate_model(self): ...` — runs after all fields are set, receives the whole model, used for cross-field validation.

**Q42: How does FastAPI handle validation errors automatically?**
FastAPI catches Pydantic's `ValidationError` and returns `422 Unprocessable Entity` with a JSON body listing all validation errors — `[{"loc": ["body", "email"], "msg": "value is not a valid email", "type": "value_error.email"}]`. No manual try/except needed. For custom errors, raise `HTTPException(status_code=..., detail=...)`.

**Q43: What is `BackgroundTasks` in FastAPI?**
`from fastapi import BackgroundTasks`. Add tasks with `background_tasks.add_task(func, *args)`. They run after the response is sent to the client — useful for sending emails, logging, cache invalidation. Not for long tasks (no retry, no persistence). Use Celery/RQ/BullMQ for reliable background jobs.

---

## Category 7: Testing (Q44–Q47)

**Q44: What is a pytest fixture and what scopes are available?**
Fixtures are functions decorated with `@pytest.fixture` that provide setup (and optional teardown via `yield`) for tests. Scopes: `function` (default — new per test), `class`, `module` (once per file), `session` (once per run). Tests request fixtures by parameter name — pytest injects them automatically.

**Q45: How do you mock a function in pytest?**
`from unittest.mock import patch, MagicMock`. As context manager: `with patch("module.function") as mock: mock.return_value = {...}`. As decorator: `@patch("module.function")`. For async: `AsyncMock`. `mock.assert_called_once()`, `mock.assert_called_with(arg1, arg2)`, `mock.call_count` for verification.

**Q46: What is `dependency_overrides` in FastAPI tests?**
`app.dependency_overrides[original_dep] = fake_dep` replaces a dependency for all tests. Allows testing routes without real DB connections, auth tokens, etc. Always `app.dependency_overrides.clear()` in teardown. The `TestClient` from `fastapi.testclient` wraps the app and runs the ASGI interface synchronously.

**Q47: What is `@pytest.mark.parametrize`?**
Runs the same test function multiple times with different arguments. `@pytest.mark.parametrize("input,expected", [(1,1), (2,4), (3,9)])` — each tuple is one test case. Pytest reports each case separately. Use it instead of copy-pasting test functions for boundary conditions.

---

## Category 8: Performance and Advanced (Q48–Q50)

**Q48: What is `__slots__`?**
`__slots__ = ['x', 'y']` prevents creation of `__dict__` per instance — uses a fixed C-level array instead. Benefits: 30-50% less memory per instance, slightly faster attribute access. Downsides: can't add new attributes dynamically, can't use `__dict__`, inheritance with non-slots classes is tricky. Best for: data-heavy classes with millions of instances.

**Q49: What is `functools.cache` vs `functools.lru_cache`?**
`@lru_cache(maxsize=128)` — bounded LRU cache, evicts least-recently-used when full. `@cache` (Python 3.9+) — unbounded cache, never evicts. Both require hashable arguments. `@cache` is simpler and faster (no LRU bookkeeping). Use `@lru_cache` when unbounded growth would be a problem.

**Q50: What are Python 3.10+ structural pattern matching (`match`/`case`) use cases?**
`match command: case "quit": ... case ("go", direction): ... case _: ...` — matches values, sequences, mappings, class instances. More readable than chains of `elif`. Use cases: command parsing, handling HTTP status codes, processing AST nodes, discriminated unions. Not a drop-in for `if/elif` — use when the structure of data drives behavior.

---

## 📝 Quick Reference Table

| Topic | Key Point | Tricky |
|-------|-----------|--------|
| GIL | Released during I/O — threads OK for I/O | CPU-bound → slower with threads |
| Generators | `yield` pauses, `next()` resumes | Exhausted after one pass |
| Closures | Captures variable reference, not value | Loop: `lambda i=i:` fix |
| Decorators | `@wraps(func)` preserves metadata | Stack order: outer→inner→body→inner→outer |
| asyncio | `await` yields control back to event loop | Never `time.sleep()` in async |
| Pydantic v2 | `@field_validator` needs `@classmethod` | `.dict()` → `.model_dump()` |
| pytest | `yield` in fixture = setup/teardown | `scope="function"` for mutable state |
| `==` vs `is` | `is` only for None/True/False | `is` checks identity not equality |
| `__eq__` | Must define `__hash__` too! | `return NotImplemented` not raise |
| `nonlocal` | Needed to ASSIGN outer variable | Reading doesn't need nonlocal |
