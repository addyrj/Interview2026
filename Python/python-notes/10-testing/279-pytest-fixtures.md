---

# 279. pytest Fixtures
# हिंदी में: pytest Fixtures (test के लिए तैयार सामान)

---

## 🔵 Simple Definition (English)
A fixture is a function marked with `@pytest.fixture` that prepares something a test needs (data, a database, an API client) and optionally cleans it up afterwards. A test asks for it simply by naming it as a parameter, and pytest injects the value.

## 🔵 सरल परिभाषा (Hindi)
Fixture एक function है जिस पर `@pytest.fixture` लगा होता है। यह test के लिए ज़रूरी चीज़ (data, database, API client) तैयार करता है और बाद में उसे साफ भी कर सकता है। Test को बस उसका नाम parameter में लिखना होता है, pytest खुद value दे देता है।

---

## 🔴 Problem it Solves
In `unittest`, shared setup lives in `setUp` and is tied to one class. Reusing it across files needs inheritance, and every test pays for setup it does not use. Fixtures solve this: setup is a small named function, reusable across the whole project through `conftest.py`, can depend on other fixtures, has a scope (per test, module, session), and cleanup is placed right next to setup with `yield`.

## 🔴 यह क्यों बना? (Hindi)
`unittest` में shared setup `setUp` में रहता है और एक class से बंधा होता है। उसे कई files में दोबारा इस्तेमाल करने के लिए inheritance चाहिए और हर test वह setup भी भरता है जो उसे चाहिए ही नहीं। Fixtures यह हल करते हैं: setup एक छोटा नाम वाला function है, `conftest.py` से पूरे project में reuse होता है, दूसरे fixtures पर निर्भर हो सकता है, scope (हर test, module, session) रखता है और cleanup `yield` से setup के ठीक नीचे लिखा जाता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → Define a function with @pytest.fixture
Step 2 → A test lists the fixture NAME as a parameter
Step 3 → pytest runs the fixture first (and fixtures it depends on)
Step 4 → Returned (or yielded) value is passed into the test
Step 5 → Code after "yield" runs as teardown, even if the test failed
Step 6 → Scope decides reuse: function (default) | class | module | package | session

setup (before yield) -> test body -> teardown (after yield)
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → @pytest.fixture लगाकर function लिखो
Step 2 → Test अपने parameter में fixture का NAME लिखता है
Step 3 → pytest पहले fixture चलाता है (और जिन fixtures पर वह निर्भर है)
Step 4 → Return (या yield) की value test में पहुंचती है
Step 5 → "yield" के बाद का code teardown की तरह चलता है, test fail हो तब भी
Step 6 → Scope तय करता है reuse: function (default) | class | module | package | session
```

---

## 🟡 Real World Example
A Swiggy-style order API has tests that need a database connection, a logged-in user, and an HTTP client. Instead of repeating that in 200 tests, the team writes three fixtures in `conftest.py`: `db` (session scope: one connection for the whole run), `user` (function scope: a fresh user per test, deleted after), and `client` (depends on `db`). Every test just writes `def test_place_order(client, user):`.

## 🟡 Real Example Hindi mein
Swiggy जैसी order API के tests को database connection, logged-in user और HTTP client चाहिए। 200 tests में यह दोहराने की जगह team `conftest.py` में तीन fixtures लिखती है: `db` (session scope: पूरे run के लिए एक connection), `user` (function scope: हर test के लिए नया user, बाद में delete) और `client` (`db` पर निर्भर)। हर test बस `def test_place_order(client, user):` लिखता है।

---

## 💻 Code Example — Basic
```python
# Basic fixtures (verified with pytest 9.x, Python 3.13) — file: test_basic_fix.py
import pytest                                     # test framework


@pytest.fixture                                   # register a fixture
def numbers() -> list[int]:                       # fixture returns test data
    return [1, 2, 3]                              # fresh list per test


def test_sum(numbers: list[int]) -> None:         # request fixture by parameter name
    assert sum(numbers) == 6                      # plain assert


def test_len(numbers: list[int]) -> None:         # gets a NEW list (not the one from test_sum)
    numbers.append(4)                             # mutate it
    assert len(numbers) == 4                      # only this test sees the change


@pytest.fixture
def resource():                                   # yield fixture = setup + teardown
    print("setup")                                # runs before the test
    yield {"open": True}                          # value given to the test
    print("teardown")                             # runs after the test, even on failure


def test_resource(resource: dict) -> None:
    assert resource["open"] is True               # use the resource

# Run: pytest -v -s --setup-show test_basic_fix.py
# Output (trimmed): 3 passed ; with -s you see "setup" before and "teardown" after test_resource
# --setup-show prints lines like:  SETUP    F numbers  /  TEARDOWN F numbers   (F = function scope)
```

## 💻 Code Example — Advanced
```python
# conftest.py — shared fixtures, auto-discovered (no import needed)
from collections.abc import Iterator              # type for yield fixtures
import pytest                                     # test framework
from fastapi import FastAPI                       # app
from fastapi.testclient import TestClient         # in-process HTTP client


@pytest.fixture(scope="session")                  # created once per test run
def app() -> FastAPI:
    app = FastAPI()                               # build the app
    db: dict[int, str] = {}                       # fake DB

    @app.post("/users/{uid}")
    def create(uid: int, name: str) -> dict:
        db[uid] = name                            # store
        return {"id": uid, "name": name}

    @app.get("/users/{uid}")
    def get(uid: int) -> dict:
        return {"id": uid, "name": db.get(uid, "?")}
    return app


@pytest.fixture                                   # function scope (default)
def client(app: FastAPI) -> Iterator[TestClient]: # depends on the app fixture
    with TestClient(app) as c:                    # runs startup/shutdown events
        yield c                                   # give to the test


# test_adv_fix.py — scopes, params, autouse, factory, builtin fixtures
ORDER: list[str] = []                             # records setup order


@pytest.fixture(scope="module")                   # once per file
def module_res() -> str:
    ORDER.append("module")                        # runs only once
    return "M"


@pytest.fixture(autouse=True)                     # applied to every test automatically
def each() -> None:
    ORDER.append("each")                          # before every test


@pytest.fixture(params=["sqlite", "postgres"])    # every test using it runs twice
def db_kind(request: pytest.FixtureRequest) -> str:
    return request.param                          # current param


@pytest.fixture
def make_user():                                  # factory fixture: returns a function
    def _make(name: str = "amit") -> dict[str, str]:
        return {"name": name}                     # build custom data per call
    return _make


def test_b(module_res: str) -> None:
    assert ORDER.count("module") == 1             # module fixture ran once


def test_db(db_kind: str) -> None:
    assert db_kind in {"sqlite", "postgres"}      # runs 2 times


def test_factory(make_user) -> None:
    assert make_user("ria") == {"name": "ria"}


def test_api(client: TestClient) -> None:         # fixtures from conftest.py
    client.post("/users/1", params={"name": "asha"})
    assert client.get("/users/1").json() == {"id": 1, "name": "asha"}


def test_tmp_and_env(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:   # built-in fixtures
    f = tmp_path / "x.txt"                        # unique temp dir per test
    f.write_text("hi")                            # write a file
    monkeypatch.setenv("MODE", "test")            # env var restored after the test
    import os
    assert os.environ["MODE"] == "test" and f.read_text() == "hi"

# Output: 7 passed (test_a, test_b, test_db[sqlite], test_db[postgres], test_factory, test_api, test_tmp_and_env)
# Times vary. A harmless Starlette deprecation warning about httpx may appear depending on the versions.
```

---

## 🟠 JavaScript vs Python Comparison

| Concept | pytest | Jest |
|---------|--------|------|
| Prepare data | `@pytest.fixture` | `beforeEach` setting a variable |
| Inject into test | parameter name | closure variable |
| Cleanup | code after `yield` | `afterEach` |
| Run once | `scope="session"` / `"module"` | `beforeAll` |
| Share across files | `conftest.py` | `setupFilesAfterEach` / helper imports |
| Parametrize fixture | `params=[...]` | `describe.each` |

```python
# Python way — dependency injection by name
import pytest

@pytest.fixture
def user() -> dict[str, str]:
    return {"name": "asha"}                       # created on demand

def test_name(user: dict[str, str]) -> None:      # injected automatically
    assert user["name"] == "asha"
```
```javascript
// JavaScript way — shared mutable variable + hook
let user;                                         // declared outside
beforeEach(() => { user = { name: "asha" }; });   // reset before each test
test("name", () => { expect(user.name).toBe("asha"); });
```

Key difference: pytest injects exactly what each test names, so unused setup never runs. In Jest, `beforeEach` runs for every test in the block, and variables are shared through closures.

---

## 🟠 FastAPI Connection
FastAPI tests become short when `client` is a fixture. You can override dependencies (database session, current user, settings) inside the fixture and clear them after `yield`, so every test starts from a known state.

```python
# FastAPI test fixture with dependency override
from collections.abc import Iterator              # yield fixture type
import pytest                                     # pytest
from fastapi import Depends, FastAPI              # FastAPI
from fastapi.testclient import TestClient         # client

app: FastAPI = FastAPI()                          # production app (normally imported)


def get_db() -> dict[str, str]:                   # real dependency
    raise RuntimeError("real DB must not be used in tests")


@app.get("/whoami")
def whoami(db: dict[str, str] = Depends(get_db)) -> dict[str, str]:
    return db                                     # returns whatever db gives


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: {"user": "test"}   # fake DB
    with TestClient(app) as c:                    # start app
        yield c                                   # test runs here
    app.dependency_overrides.clear()              # teardown: always reset


def test_whoami(client: TestClient) -> None:
    assert client.get("/whoami").json() == {"user": "test"}
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Calling a fixture like a normal function
✅ Correct: request it as a test parameter (pytest raises an error for direct calls)

```python
import pytest

@pytest.fixture
def data() -> int:
    return 1

# Wrong — Fixture "data" called directly -> pytest error
# def test_x(): assert data() == 1
# Right
def test_x(data: int) -> None:
    assert data == 1
```

❌ Mistake 2: Mutable data in a wide scope shared between tests
✅ Correct: keep mutable fixtures function-scoped, or reset them

```python
@pytest.fixture(scope="session")
def cart() -> list[str]:        # Wrong — tests leak items into each other
    return []

@pytest.fixture
def cart2() -> list[str]:       # Right — new list per test
    return []
```

❌ Mistake 3: Cleanup written after `return`, so it never runs
✅ Correct: use `yield` (code after it runs even on failure)

```python
@pytest.fixture
def f_wrong():
    conn = open("x", "w")
    return conn
    conn.close()                # Wrong — unreachable

@pytest.fixture
def f_right():
    conn = open("x", "w")
    yield conn
    conn.close()                # Right — runs after the test
```

❌ Mistake 4: A higher-scope fixture depending on a lower-scope one
✅ Correct: a session fixture can only use session fixtures (ScopeMismatch error otherwise)

---

## 🧠 Tricky Interview Question

```python
# What will this output? (run with: pytest -s)
import pytest

@pytest.fixture(scope="module")
def m() -> None:
    print("M", end=" ")

@pytest.fixture
def f() -> None:
    print("F", end=" ")

@pytest.fixture(autouse=True)
def a() -> None:
    print("A", end=" ")

def test_1(f: None, m: None) -> None:
    print("T1", end=" ")

def test_2(m: None) -> None:
    print("T2", end=" ")
```
Answer: Higher-scoped fixtures are set up first, then autouse fixtures, then the rest in the order requested. Output (verified; pytest's own `.` progress dots are mixed in): `M A F T1 .A T2 .` i.e. `M A F T1 A T2`. `m` runs only once (module scope) and so appears only before test_1. `a` is autouse so it runs before each test, and `f` runs only for test_1. (Check the order with `pytest --setup-show` if unsure.)

---

## ⚫ Interview Questions + Answers

Q1: What are the fixture scopes and when do you use each?
A1: `function` (default, new for each test), `class`, `module`, `package`, `session`. Use wide scopes for expensive and read-only things (DB connection, loaded model, app), function scope for anything the test mutates.

Q2: What does `conftest.py` do?
A2: pytest auto-loads it and makes its fixtures and hooks available to all tests in that directory and below, with no import. You can have one at the project root and more in sub-folders; a closer one overrides a farther one.

Q3: How is teardown done in fixtures?
A3: Use `yield value` and put cleanup after it, or use `request.addfinalizer(fn)`. Teardown runs in reverse order of setup and still runs if the test fails (but not if setup before the yield crashed).

Q4: What is a factory fixture?
A4: A fixture that returns a function so a test can create many objects with different arguments (`make_user("ria")`). Good when a test needs several objects of the same kind.

Q5: What are `autouse=True` fixtures and the risks?
A5: They run for every test in their scope without being requested. Useful for resetting global state or freezing time, but they hide behaviour, so keep them few and documented.

---

## 🔷 When to Use + When Not to Use
✅ Use when:
- Setup/teardown is shared across many tests
- You need DB sessions, API clients, temp files, environment changes
- You want to parametrize the setup (`params=`)
- Expensive setup should happen once (`scope="session"`)

❌ Avoid when:
- A value is used by one test only: just build it inside the test
- Heavy "magic" autouse fixtures that make tests hard to read
- Sharing mutable data in wide scopes

---

## 📊 Visual Diagram
```
conftest.py                    test_orders.py
 ┌──────────────┐               def test_order(client, user):
 │ db  (session)│◄──┐                          │       │
 └──────────────┘   │                          │       │
 ┌──────────────┐   │ depends on               ▼       ▼
 │ client (func)│───┘             pytest builds:  db -> client, user -> test
 └──────────────┘                 then runs test, then tears down in reverse:
 ┌──────────────┐                 user, client (db stays until the session ends)
 │ user (func)  │
 └──────────────┘
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fixture | Reusable setup function | दोबारा इस्तेमाल होने वाला setup function |
| Scope | How long a fixture value lives | Fixture कितनी देर जीवित रहे |
| conftest.py | File for shared fixtures/hooks | Shared fixtures की file |
| yield fixture | Setup before, teardown after yield | Yield से पहले setup, बाद में teardown |
| autouse | Runs automatically | अपने आप चलना |
| Factory fixture | Fixture returning a builder function | Builder function लौटाने वाला fixture |

---

## ⚡ 3-Line Summary
English: A fixture is a named setup function that pytest injects into tests by parameter name. Use `yield` for teardown, `scope` for reuse, and `conftest.py` to share across files. Keep mutable fixtures function-scoped.
Hindi: Fixture एक नाम वाला setup function है जिसे pytest parameter के नाम से test में डालता है। Teardown के लिए `yield`, reuse के लिए `scope` और files में share करने के लिए `conftest.py` इस्तेमाल करें। Mutable fixtures को function scope में रखें।

---

## ➡️ Next Topic
**280. pytest Marks** — tag tests with `skip`, `xfail`, and custom markers like `slow`, and select them from the command line with `-m`.
