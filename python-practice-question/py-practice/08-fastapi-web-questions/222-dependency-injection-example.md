---

# Q222. Dependency injection example
# Category: FASTAPI + WEB QUESTIONS
# Difficulty: ⭐⭐ Medium

---

## ❓ Question
Use FastAPI `Depends` to inject (1) a DB session with setup/teardown and (2) the current user, built on top of the DB dependency. Then override the DB dependency in a test.

```python
def me(user = Depends(current_user)): ...
```

---

## 💡 Quick Concept (2 lines only)
`Depends(fn)` makes FastAPI call `fn` per request and pass the result in; `yield` dependencies run cleanup after the response; `dependency_overrides` swaps them in tests.
हिंदी: Depends से FastAPI खुद function call करके value inject करता है; yield से teardown; tests में override।

---

## ✅ Answer / Solution

```python
# ============================================
# SOLUTION
# ============================================

from collections.abc import Iterator              # type for yield dependency
from typing import Annotated                      # modern Depends style
from fastapi import Depends, FastAPI, Header, HTTPException  # DI tools
from fastapi.testclient import TestClient         # test client

app = FastAPI()                                   # create app
events: list[str] = []                            # to show dependency lifecycle


class FakeDB:                                     # stand-in for a DB session
    def __init__(self) -> None:
        self.users = {"a1": "Aditya"}             # fake table


def get_db() -> Iterator[FakeDB]:
    events.append("open db")                      # setup (before the endpoint)
    try:
        yield FakeDB()                            # value injected into the endpoint
    finally:
        events.append("close db")                 # teardown (after the response)


DB = Annotated[FakeDB, Depends(get_db)]           # reusable alias


def current_user(db: DB, x_token: Annotated[str, Header()]) -> str:  # dependency with sub-dependency
    name = db.users.get(x_token)                  # look the token up
    if name is None:                              # unknown token
        raise HTTPException(401, "bad token")     # stop here: endpoint never runs
    return name                                   # injected as `user`


@app.get("/me")
def me(user: Annotated[str, Depends(current_user)]) -> dict:
    return {"user": user}                         # no auth code inside the endpoint


# ---------- TEST CASES ----------
c = TestClient(app)                               # normal run
print(c.get("/me", headers={"x-token": "a1"}).json())  # authorised
print(c.get("/me", headers={"x-token": "zz"}).status_code)  # 401
print(events)                                     # db opened/closed for each request


class StubDB(FakeDB):                             # test double
    def __init__(self) -> None:
        self.users = {"t": "Tester"}              # different data


app.dependency_overrides[get_db] = lambda: StubDB()  # swap dependency in tests
print(c.get("/me", headers={"x-token": "t"}).json())  # uses StubDB

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'user': 'Aditya'}
# 401
# ['open db', 'close db', 'open db', 'close db']
# {'user': 'Tester'}
```

---

## 🔍 Why This Works (3 lines max)
Dependencies can depend on other dependencies (`current_user` uses `get_db`). The log shows `open db` / `close db` once per request. The 401 is raised inside the dependency, so the endpoint body never runs. `dependency_overrides[get_db]` replaces it with a stub.
हिंदी: Dependency chain बन सकती है; auth fail पर endpoint चलता ही नहीं; test में dependency_overrides।

---

## ⚡ Alternative Solution
```python
from typing import Annotated                      # Annotated
from fastapi import Depends, FastAPI              # DI
from fastapi.testclient import TestClient         # test client

app = FastAPI()                                   # create app


class Pagination:                                 # a class is also a dependency
    def __init__(self, page: int = 1, size: int = 10) -> None:
        self.page = page                          # query param ?page=
        self.size = min(size, 50)                 # query param ?size= (capped)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size        # SQL OFFSET


@app.get("/list")
def list_things(p: Annotated[Pagination, Depends()]) -> dict:  # Depends() = use the annotation
    return {"page": p.page, "size": p.size, "offset": p.offset}


c = TestClient(app)                               # test client
print(c.get("/list").json())                      # defaults
print(c.get("/list?page=3&size=100").json())      # size capped at 50

# ============================================
# OUTPUT (real run, Python 3.13):
# ============================================

# {'page': 1, 'size': 10, 'offset': 0}
# {'page': 3, 'size': 50, 'offset': 100}
```

---

## ⚠️ Common Mistake
```python
# ❌ Wrong: calling the dependency yourself / creating the DB inside every endpoint
@app.get("/me")
def me():
    db = FakeDB()                     # hard-coded: cannot be replaced in tests, never closed
    ...

# ❌ Wrong: Depends(get_db()) - with parentheses you pass the RESULT, not the function
# ✅ Correct: Depends(get_db)
```

---

## 🎯 Interview Tip (1 line)
Say: "Depends gives reusable, testable, per-request wiring; yield for cleanup; dependency_overrides for tests."

---

## 🔗 Related Questions
→ Q221 (CRUD) | Q224 (JWT auth) | Q237 (async DB session) | Q238 (OAuth2 password flow)
