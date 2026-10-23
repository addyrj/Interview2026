# Python Quick Cheatsheet — Interview Ready
# हिंदी में: Python Quick Reference

---

## 🔷 Data Types & Operations

```python
# Lists
lst = [1, 2, 3]
lst.append(4)      # [1,2,3,4]
lst.extend([5,6])  # [1,2,3,4,5,6]
lst.pop()          # removes last → 6
lst.pop(0)         # removes first → 1
lst.sort()         # in-place sort
sorted(lst)        # new sorted list
lst[::-1]          # reversed (new list)
lst[1:4]           # slice [2,3,4]

# Dicts
d = {"a": 1, "b": 2}
d.get("c", 0)      # safe access, default 0
d.items()          # [(key, val), ...]
d.keys(); d.values()
{**d1, **d2}       # merge (d2 wins)
d1 | d2            # Python 3.9+ merge

# Sets
s = {1, 2, 3}
s.add(4); s.discard(99)   # discard = no error
s1 | s2   # union
s1 & s2   # intersection
s1 - s2   # difference
2 in s    # O(1) membership

# Strings
f"Hello {name!r}"   # repr in f-string
s.strip()           # remove whitespace
s.split(",")        # split to list
",".join(lst)       # join list to string
s.lower(); s.upper(); s.title()
s.startswith("ab"); s.endswith("cd")
s.replace("old", "new")
```

---

## 🔷 Functions

```python
def func(pos, /, standard, *, kw_only, **kwargs):
    pass
# / = positional-only, * = keyword-only

# Mutable default = BUG:
def bad(lst=[]): lst.append(1)   # shared!
def good(lst=None): lst = lst or []

# Lambda:
square = lambda x: x**2
sorted(data, key=lambda d: d["age"])

# Unpacking:
first, *rest = [1,2,3,4,5]
a, b = b, a   # swap!
```

---

## 🔷 OOP

```python
class Animal:
    count = 0              # class attr

    def __init__(self, name):
        self.name = name   # instance attr
        Animal.count += 1

    def speak(self):       # instance method
        raise NotImplementedError

    @classmethod
    def create(cls, name):  # factory
        return cls(name)

    @staticmethod
    def is_valid(name):    # no self/cls
        return bool(name)

    @property
    def info(self):        # attribute-style
        return f"{self.name}"

    def __repr__(self): return f"Animal({self.name!r})"
    def __str__(self): return self.name
    def __len__(self): return len(self.name)
    def __eq__(self, other): return self.name == other.name
```

---

## 🔷 Decorators

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)   # preserve __name__, __doc__
    def wrapper(*args, **kwargs):
        # before
        result = func(*args, **kwargs)
        # after
        return result
    return wrapper

@my_decorator
def my_func(): pass

# With arguments:
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
```

---

## 🔷 Generators

```python
# Generator function:
def count_up(n):
    for i in range(n):
        yield i

# Generator expression (O(1) memory):
gen = (x**2 for x in range(1_000_000))
total = sum(x**2 for x in range(1000))  # no list!

# yield from:
def flat(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flat(item)
        else:
            yield item
```

---

## 🔷 Context Managers

```python
# Using:
with open("file.txt") as f:
    data = f.read()

# Creating with class:
class Timer:
    def __enter__(self): 
        self.start = time.time(); return self
    def __exit__(self, *args): 
        self.elapsed = time.time() - self.start

# Creating with contextlib:
from contextlib import contextmanager
@contextmanager
def managed():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

---

## 🔷 Error Handling

```python
try:
    risky()
except (ValueError, TypeError) as e:
    logger.error(str(e))
    raise                     # re-raise with original traceback
except Exception as e:
    raise NewError("wrapped") from e  # chain
else:
    pass   # runs if NO exception
finally:
    cleanup()   # ALWAYS runs

# Custom exception:
class AppError(Exception): pass
class ValidationError(AppError):
    def __init__(self, field, msg):
        self.field = field
        super().__init__(f"{field}: {msg}")
```

---

## 🔷 Async / Asyncio

```python
import asyncio

# Define:
async def fetch(url): 
    await asyncio.sleep(1)
    return "data"

# Run:
asyncio.run(main())

# Concurrent (not sequential!):
results = await asyncio.gather(
    fetch(url1), fetch(url2), fetch(url3)
)   # all run at same time!

# Limit concurrency:
sem = asyncio.Semaphore(10)
async def limited():
    async with sem:
        await do_work()

# Timeout:
result = await asyncio.wait_for(fetch(url), timeout=5.0)
```

---

## 🔷 FastAPI Patterns

```python
from fastapi import FastAPI, Depends, HTTPException, Query, Path, status
from pydantic import BaseModel

# Dependency:
async def get_db():
    async with Session() as db:
        yield db

# Endpoint:
@app.get("/items/{id}", response_model=ItemResponse)
async def get_item(
    id: int = Path(..., ge=1),
    search: str = Query(None, min_length=3),
    db: Session = Depends(get_db),
):
    item = await db.get(Item, id)
    if not item: raise HTTPException(404, "Not found")
    return item

# Background task:
@app.post("/orders")
async def create_order(order: OrderIn, bg: BackgroundTasks):
    result = await order_service.create(order)
    bg.add_task(send_email, order.user_id)
    return result
```

---

## 🔷 Pydantic v2

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: str
    age: Optional[int] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("invalid email")
        return v.lower()

    model_config = ConfigDict(
        from_attributes=True,  # was: orm_mode=True in v1
        str_strip_whitespace=True,
    )

user = UserCreate(name="Priya", email="P@TEST.COM")
print(user.email)   # "p@test.com" — lowercased
user.model_dump()   # dict
user.model_dump_json()   # JSON string
UserCreate.model_validate({"name": "Priya", "email": "p@test.com"})
```

---

## 🔷 SQLAlchemy Async

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import selectinload

engine = create_async_engine("postgresql+asyncpg://...")
Session = async_sessionmaker(engine, expire_on_commit=False)  # KEY!

async def get_user_with_orders(user_id: int):
    async with Session() as session:
        result = await session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.orders))  # N+1 fix!
        )
        return result.scalar_one_or_none()
```

---

## 🔷 Testing Patterns

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.get_user.return_value = {"id": 1, "name": "Test"}
    return db

@pytest.mark.parametrize("input,expected", [
    ("hello", 5),
    ("", 0),
    ("python", 6),
])
def test_length(input, expected):
    assert len(input) == expected

# FastAPI:
app.dependency_overrides[get_db] = lambda: mock_db
client = TestClient(app)
response = client.get("/users/1")
app.dependency_overrides.clear()
```

---

## 🔷 Performance Quick Hits

| Slow | Fast |
|------|------|
| `for x in lst: if x in other_lst` | Convert to set first |
| `list(map(lambda x: x**2, lst))` | `[x**2 for x in lst]` |
| Load entire file | `for line in f:` |
| Re-compute every call | `@lru_cache` |
| Sequential awaits | `asyncio.gather()` |
| `defaultdict(list)` not used | Group with `defaultdict(list)` |

---

## 🔷 One-Liners Worth Knowing

```python
# Flatten list one level:
flat = [x for row in nested for x in row]

# Dict from two lists:
d = dict(zip(keys, values))

# Invert a dict:
inv = {v: k for k, v in d.items()}

# Remove duplicates (preserve order):
unique = list(dict.fromkeys(lst))

# Most common element:
from collections import Counter
most_common = Counter(lst).most_common(1)[0][0]

# Chunk list:
chunks = [lst[i:i+n] for i in range(0, len(lst), n)]

# Safe dict access chain:
val = config.get("db", {}).get("host", "localhost")

# Group by key:
from collections import defaultdict
groups = defaultdict(list)
for item in items: groups[item["category"]].append(item)
```

---

## 🔷 Key Rules

1. **Mutable defaults** → `def f(lst=None): lst = lst or []`
2. **String concat in loop** → `"".join(parts)` not `s += x`
3. **`in` on list** → convert to set for repeated lookups
4. **Async endpoint** → never call sync blocking code directly
5. **`b = a`** → NOT a copy for lists/dicts. Use `.copy()` or `copy.deepcopy()`
6. **`except:`** → always use `except Exception:` or specific type
7. **`for line in f:`** → memory efficient large file reading
8. **`asyncio.gather()`** → concurrent, not sequential
9. **`response_model=`** → always set to filter sensitive fields
10. **`expire_on_commit=False`** → SQLAlchemy async ORM essential
