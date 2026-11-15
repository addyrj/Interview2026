---

# 295. Fixtures Scope
# हिंदी में: Fixtures का Scope (कितनी देर तक जीवित रहे)

---

## 🔵 Simple Definition (English)
A fixture's scope decides how often it is created and destroyed: for every test (`function`, the default), once per class, module, package, or once for the whole test run (`session`). Wider scope means faster tests but more risk of shared state.

## 🔵 सरल परिभाषा (Hindi)
Fixture का scope तय करता है कि वह कितनी बार बनेगा और खत्म होगा: हर test के लिए (`function`, default), हर class, module, package के लिए एक बार, या पूरे test run में एक बार (`session`)। बड़ा scope मतलब तेज़ tests, पर साझा state का खतरा भी ज़्यादा।

---

## 🔴 Problem it Solves
Starting a database container or loading an ML model can take seconds. If it is rebuilt for each of 500 tests the suite takes forever. But sharing one object everywhere lets one test dirty the data for the next. Scope lets you choose the balance: expensive things are shared, cheap mutable things are fresh.

## 🔴 यह क्यों बना? (Hindi)
Database container शुरू करने या ML model load करने में कई सेकंड लगते हैं। 500 tests के लिए हर बार बनाएँ तो suite बहुत धीमा हो जाता है। लेकिन एक ही object सब जगह बाँटें तो एक test दूसरे का data बिगाड़ देता है। Scope से संतुलन चुनते हैं: महँगी चीज़ें साझा, सस्ती बदलने वाली चीज़ें हर बार नई।

---

## 🟢 How it Works — Step by Step

```
Step 1 → @pytest.fixture(scope="...") sets the lifetime
Step 2 → pytest sets up higher scopes first: session → package → module → class → function
Step 3 → A fixture is created the first time a test needs it
Step 4 → It is reused for all later tests inside the same scope
Step 5 → When the scope ends, code after yield runs (teardown), in reverse order
Step 6 → A fixture may only depend on fixtures with the same or WIDER scope
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → @pytest.fixture(scope="...") उसकी उम्र तय करता है
Step 2 → पहले बड़े scopes बनते हैं: session → package → module → class → function
Step 3 → Fixture पहली बार तब बनता है जब किसी test को उसकी ज़रूरत हो
Step 4 → उसी scope के बाकी tests में वही दोबारा इस्तेमाल होता है
Step 5 → scope खत्म होने पर yield के बाद वाला code (teardown) उल्टे क्रम में चलता है
Step 6 → Fixture सिर्फ बराबर या बड़े scope वाले fixtures पर निर्भर हो सकता है
```

---

## 🟡 Real World Example
A Swiggy-like backend test suite: `session` scope starts a PostgreSQL test container once (8 seconds). `module` scope creates tables for each test file. `function` scope wraps every test in a transaction that is rolled back, so every test sees a clean database but nothing is recreated. Total time falls from 40 minutes to 2 minutes.

## 🟡 Real Example Hindi mein
Swiggy जैसे backend के test suite में: `session` scope एक बार PostgreSQL test container चालू करता है (8 सेकंड)। `module` scope हर test file के लिए tables बनाता है। `function` scope हर test को एक transaction में लपेटता है जो rollback हो जाती है, इसलिए हर test को साफ database मिलता है पर कुछ दोबारा नहीं बनता। कुल समय 40 मिनट से 2 मिनट हो जाता है।

---

## 💻 Code Example — Basic
```python
# Basic: see scope in action with --setup-show (verified on pytest 9.2, Python 3.13)
# ---------- conftest.py ----------
import pytest  # fixtures


@pytest.fixture(scope="session")  # created ONCE for the whole run
def session_cfg() -> dict[str, str]:
    return {"env": "test"}  # cheap config object


@pytest.fixture(scope="module")  # once per test FILE
def module_db() -> list[str]:
    data: list[str] = []  # pretend this is an expensive database
    yield data  # give it to tests
    # code after yield = teardown for this module


@pytest.fixture  # default scope = "function": fresh for every test
def fn_item(module_db: list[str]) -> str:
    module_db.append("x")  # side effect on the shared module-level data
    return "item"


# ---------- test_a.py ----------
def test_1(session_cfg, module_db, fn_item):  # first test
    assert len(module_db) == 1  # one append so far


def test_2(session_cfg, module_db, fn_item):  # second test, SAME module_db
    assert len(module_db) == 2  # state leaked between tests -> shows the danger


# ---------- test_b.py ----------
def test_3(session_cfg, module_db):  # different file -> NEW module_db
    assert module_db == []  # empty again

# Run: pytest -q --setup-show test_a.py test_b.py
```

## 💻 Code Example — Advanced
```python
# Production style: expensive session resource + per-test rollback (SQLite via SQLAlchemy)
# pip install sqlalchemy pytest
from collections.abc import Iterator  # generator fixture type
import pytest  # fixtures
from sqlalchemy import create_engine, text, Engine  # SQL toolkit
from sqlalchemy.orm import Session  # transaction-aware session


@pytest.fixture(scope="session")  # engine/tables built ONE time
def engine() -> Iterator[Engine]:
    eng: Engine = create_engine("sqlite://")  # in-memory db (StaticPool-like single conn)
    with eng.begin() as conn:  # create schema once
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"))
    yield eng  # tests run
    eng.dispose()  # teardown at the very end


@pytest.fixture  # function scope: new session for each test
def db(engine: Engine) -> Iterator[Session]:
    conn = engine.connect()  # take a connection
    trans = conn.begin()  # outer transaction
    session: Session = Session(bind=conn)  # session uses that connection
    yield session  # test works with the session
    session.close()  # close the session
    trans.rollback()  # throw away everything the test inserted
    conn.close()  # release the connection


def test_insert_is_visible(db: Session) -> None:
    db.execute(text("INSERT INTO users (name) VALUES ('Asha')"))  # write
    count: int = db.execute(text("SELECT COUNT(*) FROM users")).scalar_one()  # read
    assert count == 1  # visible inside this test


def test_database_is_clean_again(db: Session) -> None:
    count: int = db.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
    assert count == 0  # rollback removed Asha: isolation + speed

# Verified setup order from real --setup-show output (S=session, M=module, C=class, F=function):
# SETUP    S session_cfg
#     SETUP    M module_db
#         SETUP    F fn_item (fixtures used: module_db)
#         test_a.py::test_1 .
#         TEARDOWN F fn_item
#         ... test_2 ...
#       SETUP    C cls_res
#       TEARDOWN C cls_res
#     TEARDOWN M module_db
#     SETUP    M module_db        <- new module -> created again
# TEARDOWN S session_cfg
```

---

## 🟠 JavaScript vs Python Comparison
Jest's `beforeAll` / `afterAll` are like module or class scope, and `beforeEach` / `afterEach` are like function scope. Python makes it explicit per fixture, and pairs setup and teardown in one function using `yield`.

```python
# Python
@pytest.fixture(scope="module")      # like beforeAll + afterAll
def db() -> Iterator[Conn]:
    conn = connect()
    yield conn
    conn.close()
```
```javascript
// JavaScript (Jest)
let conn;
beforeAll(async () => { conn = await connect(); });   // once per file
afterAll(async () => { await conn.close(); });
beforeEach(() => { /* per test */ });
```

Key differences: Jest has only two lifetimes (all / each) per describe block, pytest has five, and each fixture picks its own. Pytest also reuses the same fixture by name across files.

---

## 🟠 FastAPI Connection
In FastAPI tests, creating `TestClient(app)` as a context manager triggers the lifespan startup and shutdown events. That is expensive if the app loads a model or opens a pool, so use `scope="module"` or `"session"` for the client when the app is stateless, and `function` scope when tests change `dependency_overrides` or data.

```python
# FastAPI: session-scoped client for a stateless app (needs: pip install fastapi httpx pytest)
from collections.abc import Iterator  # type
import pytest  # fixtures
from fastapi import FastAPI  # framework
from fastapi.testclient import TestClient  # client

app: FastAPI = FastAPI()  # normally imported from your package


@app.get("/ping")  # trivial stateless route
def ping() -> dict[str, str]:
    return {"pong": "ok"}


@pytest.fixture(scope="session")  # startup/shutdown runs ONCE, not per test
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:  # lifespan startup here
        yield c  # all tests share it
    # lifespan shutdown happens here


def test_ping(client: TestClient) -> None:
    assert client.get("/ping").json() == {"pong": "ok"}  # fast: no new startup
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Using a wide scope for a mutable object
✅ Correct: Share only read-only or reset-able things; reset or roll back per test.

```python
# Wrong: module-scoped list that tests append to -> test order now matters
@pytest.fixture(scope="module")
def cart() -> list[str]: return []
# Right: function scope (default), or a module-scoped DB with a per-test rollback
```

❌ Mistake 2: Wider-scope fixture depending on a narrower one
✅ Correct: The dependency must be the same or wider scope.

```python
# Wrong
@pytest.fixture
def small() -> int: return 1
@pytest.fixture(scope="session")
def big(small: int) -> int: return small   # ScopeMismatch error
# Right: make "small" session scope too, or make "big" function scope
```

❌ Mistake 3: Forgetting teardown or using `return` when cleanup is needed
✅ Correct: Use `yield` and put cleanup after it, so it runs even if the test fails.

```python
# Wrong: file/connection is never closed
@pytest.fixture
def f(): return open("x.txt", "w")
# Right
@pytest.fixture
def f() -> Iterator[IO[str]]:
    h = open("x.txt", "w"); yield h; h.close()
```

---

## 🧠 Tricky Interview Question

**Q**: How many times is each fixture created, and does `test_3` pass?

```python
# conftest.py: module_db is scope="module"; fn_item is function scope and appends "x" to module_db
# test_a.py: test_1 and test_2 request fn_item; test_2 asserts len(module_db) == 2
# test_b.py: test_3 asserts module_db == []
```

**Answer**:
```
session_cfg : 1 time (whole run)
module_db   : 2 times (once for test_a.py, once for test_b.py)
fn_item     : 2 times (test_1, test_2)
test_3      : passes, because test_b.py gets a brand new module_db
```
test_2 sees the list left by test_1 (length 2), which proves shared state. This is exactly why mutable data should not use a wide scope. (All verified with `--setup-show`; 6 passed.)

---

## ⚫ Interview Questions + Answers

Q1: What are the fixture scopes?
A1: `function` (default), `class`, `module`, `package`, `session`. Pytest 8+ also supports a dynamic scope: pass a callable that returns the scope name, based on config.

Q2: What does `ScopeMismatch` mean?
A2: A wider-scope fixture asked for a narrower one, which could change between tests. Pytest refuses.

Q3: When does teardown for a session fixture run?
A3: After the last test of the run, after narrower teardown. Teardown order is the reverse of setup.

Q4: Does a wider scope always make tests faster?
A4: Only if setup is the bottleneck. It also risks hidden coupling between tests. Reset state per test (rollback, truncate) to keep both speed and isolation.

Q5: How do you see when fixtures are created?
A5: `pytest --setup-show` prints SETUP and TEARDOWN lines with S, P, M, C, F letters for the scope.

---

## 🔷 When to Use + When Not to Use

✅ Use wide scope (session/module) for:
- Starting a container, creating an engine, loading an ML model, reading big config
- Stateless clients (like `TestClient` for a read-only app)

❌ Avoid wide scope for:
- Lists, dicts and database rows that tests change
- Anything where a failing test could leave a corrupted state for the next one
- Fixtures that use `monkeypatch` (it is function scoped; use `pytest.MonkeyPatch.context()` for wider)

---

## 📊 Visual Diagram

```
 session  ┌──────────────────────────────────────────────┐ created 1x
 module   │ ┌── test_a.py ──────────┐ ┌── test_b.py ───┐ │ created per file
 class    │ │ ┌ TestK ┐             │ │                │ │ created per class
 function │ │ t1  t2   ta  tb       │ │ t3             │ │ created per test
          │ └───────────────────────┘ └────────────────┘ │
          └──────────────────────────────────────────────┘
 setup: outer → inner      teardown: inner → outer
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| scope | Lifetime of a fixture | fixture की उम्र |
| session | Whole test run | पूरा test run |
| teardown | Cleanup after the test | test के बाद सफाई |
| yield fixture | Setup before yield, cleanup after | yield से पहले setup, बाद में cleanup |
| ScopeMismatch | Wider fixture using narrower one | बड़े scope का छोटे पर निर्भर होना |
| Isolation | Tests do not share changes | tests में साझा बदलाव नहीं |

---

## ⚡ 3-Line Summary
English: Scope controls how long a fixture lives: function (default), class, module, package or session. Share expensive, read-only resources widely and reset mutable state for each test. Use `--setup-show` to see exactly when things are created.
Hindi: Scope तय करता है कि fixture कितनी देर रहे: function (default), class, module, package या session। महँगे, read-only resources को बड़े scope में साझा करें और बदलने वाली state हर test के लिए reset करें। कब क्या बनता है यह देखने के लिए `--setup-show` इस्तेमाल करें।

---

## ➡️ Next Topic
**296. FastAPI Complete** — then continue with **297. FastAPI vs Flask vs Django**.
