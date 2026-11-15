---

# 294. conftest.py
# हिंदी में: conftest.py (pytest की साझा configuration file)

---

## 🔵 Simple Definition (English)
`conftest.py` is a special file that pytest loads automatically. Fixtures and hooks defined in it are available to all tests in the same folder and its sub-folders, without any `import`. It is the place for shared test setup.

## 🔵 सरल परिभाषा (Hindi)
`conftest.py` एक खास file है जिसे pytest अपने-आप load करता है। इसमें लिखे fixtures और hooks उसी folder और उसके sub-folders के सभी tests में बिना `import` किए मिल जाते हैं। साझा test setup रखने की यही सही जगह है।

---

## 🔴 Problem it Solves
Without `conftest.py` you copy the same `client` or `db` fixture into every test file, or import fixtures from a helper module (which breaks pytest's fixture discovery and confuses linters). Shared setup gets duplicated, drifts apart, and one fix has to be made in 30 places.

## 🔴 यह क्यों बना? (Hindi)
`conftest.py` के बिना वही `client` या `db` fixture हर test file में कॉपी करना पड़ता है, या helper module से import करना पड़ता है (इससे fixture discovery बिगड़ती है और linters भ्रमित होते हैं)। साझा setup दोहराया जाता है, अलग-अलग बदल जाता है, और एक fix 30 जगह करना पड़ता है।

---

## 🟢 How it Works — Step by Step

```
Step 1 → pytest starts and walks from the rootdir down to each test file
Step 2 → For every folder on the path it loads conftest.py (outer first, inner last)
Step 3 → Fixtures in conftest become visible to tests at that level and below
Step 4 → A fixture with the same name in an inner conftest overrides the outer one
Step 5 → Special functions named pytest_* (hooks) change pytest behaviour
Step 6 → Test files never import conftest.py - pytest injects fixtures by argument name
```

## 🟢 कैसे काम करता है? (Hindi)
```
Step 1 → pytest rootdir से नीचे हर test file तक के रास्ते पर चलता है
Step 2 → रास्ते के हर folder की conftest.py load होती है (बाहर वाली पहले, अंदर वाली बाद में)
Step 3 → conftest के fixtures उस स्तर और उसके नीचे के tests को दिखते हैं
Step 4 → अंदर की conftest में वही नाम हो तो वह बाहर वाले को override करता है
Step 5 → pytest_* नाम के special functions (hooks) pytest का behaviour बदलते हैं
Step 6 → Test files conftest.py को import नहीं करतीं - fixtures argument के नाम से मिलते हैं
```

---

## 🟡 Real World Example
A FoodApp backend has `tests/conftest.py` with a `client` fixture (FastAPI `TestClient` with an in-memory SQLite database) and `tests/api/conftest.py` that adds an `auth_headers` fixture with a fake JWT. A CLI option `--runslow` in the root conftest lets CI run slow tests only at night.

## 🟡 Real Example Hindi mein
FoodApp backend में `tests/conftest.py` में `client` fixture है (in-memory SQLite वाला FastAPI `TestClient`), और `tests/api/conftest.py` में `auth_headers` fixture है जो नकली JWT देता है। Root conftest में `--runslow` CLI option है जिससे CI भारी tests सिर्फ रात में चलाता है।

---

## 💻 Code Example — Basic
```python
# Basic: one shared fixture, no import needed in the test file
# ---------- tests/conftest.py ----------
import pytest  # pytest provides the fixture decorator


@pytest.fixture  # makes this function a fixture
def user() -> dict[str, str]:  # tests ask for it by name "user"
    return {"name": "root-user"}  # value injected into the test


# ---------- tests/test_root.py ----------
def test_root_user(user: dict[str, str]) -> None:  # NOTE: no import of conftest
    assert user == {"name": "root-user"}  # pytest injected the fixture

# Run: pytest -q
# Output: .  (1 passed)
```

## 💻 Code Example — Advanced
```python
# Production style: nested conftest override + hooks + CLI option (verified, pytest 9.2)
# ---------- tests/conftest.py (root level) ----------
import pytest  # test framework


def pytest_addoption(parser: pytest.Parser) -> None:  # hook: add a CLI flag
    parser.addoption(  # define --runslow
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config: pytest.Config) -> None:  # hook: register the marker
    config.addinivalue_line("markers", "slow: slow test")  # avoids unknown marker warning


def pytest_collection_modifyitems(  # hook: edit the list of collected tests
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--runslow"):  # user asked for slow tests
        return  # keep everything
    skip = pytest.mark.skip(reason="need --runslow")  # reason is shown with -rs
    for item in items:  # loop over every collected test
        if "slow" in item.keywords:  # test has @pytest.mark.slow
            item.add_marker(skip)  # mark it skipped


@pytest.fixture  # base fixture
def user() -> dict[str, str]:
    return {"name": "root-user"}


# ---------- tests/api/conftest.py (inner level) ----------
@pytest.fixture  # same name -> overrides the parent for tests/api only
def user(user: dict[str, str]) -> dict[str, str]:  # asks for the parent "user" too
    return {**user, "role": "api"}  # extend the parent's value


# ---------- tests/api/test_u.py ----------
@pytest.mark.slow  # slow test
def test_slow() -> None:
    pass


def test_user(user: dict[str, str]) -> None:
    assert user == {"name": "root-user", "role": "api"}  # got the overridden fixture

# Real runs:
# pytest -q -rs            -> 2 passed, 1 skipped   (SKIPPED: need --runslow)
# pytest -q --runslow      -> 3 passed
# pytest --fixtures -q     -> lists "user" twice: tests/conftest.py and tests/api/conftest.py
```

---

## 🟠 JavaScript vs Python Comparison
Jest has `setupFiles`, `setupFilesAfterEach` and `jest.config.js` for shared setup, all configured in one place. pytest uses folder-based `conftest.py` files, so setup can differ per folder with zero configuration.

```python
# Python: conftest.py fixture, injected by argument name
@pytest.fixture
def db() -> Iterator[Session]:
    session = make_session()
    yield session           # test runs
    session.close()         # teardown
```
```javascript
// JavaScript (Jest): beforeEach/afterEach in a setup file, shared via globals
let db;
beforeEach(() => { db = makeSession(); });
afterEach(() => { db.close(); });
// (the test file uses the global "db"; no injection by name)
```

Key differences: Jest shares state through global variables; pytest passes fixtures as function arguments, so dependencies are explicit and each fixture can have its own scope.

---

## 🟠 FastAPI Connection
In FastAPI projects `conftest.py` is where the test `client`, test database and `dependency_overrides` live. One override in conftest means every endpoint test automatically avoids the real database or payment gateway.

```python
# FastAPI: tests/conftest.py (needs: pip install fastapi httpx pytest)
from collections.abc import Iterator  # type for generator fixtures
import pytest  # fixtures
from fastapi import FastAPI, Depends  # framework
from fastapi.testclient import TestClient  # test client


def real_settings() -> dict[str, str]:  # production dependency
    return {"db": "postgres://prod"}


app: FastAPI = FastAPI()  # normally imported from your app package


@app.get("/db-url")  # endpoint using the dependency
def db_url(s: dict[str, str] = Depends(real_settings)) -> dict[str, str]:
    return s


@pytest.fixture  # shared by all tests in this folder tree
def client() -> Iterator[TestClient]:
    app.dependency_overrides[real_settings] = lambda: {"db": "sqlite://"}  # fake DB
    with TestClient(app) as c:  # start app
        yield c  # tests run here
    app.dependency_overrides.clear()  # always restore


def test_uses_fake_db(client: TestClient) -> None:
    assert client.get("/db-url").json() == {"db": "sqlite://"}  # override worked
```

---

## ⚠️ Common Mistakes to Avoid

❌ Mistake 1: Importing from conftest in a test file
✅ Correct: Never `from conftest import x`. Ask for the fixture by argument name. For plain helper functions, use a normal module like `tests/helpers.py`.

```python
# Wrong
from conftest import user  # breaks when conftest is loaded twice; hides the fixture system
# Right
def test_x(user): ...
```

❌ Mistake 2: One huge root conftest with everything
✅ Correct: Keep only truly shared fixtures at the root. Put api-only fixtures in `tests/api/conftest.py`, db-only ones in `tests/integration/conftest.py`.

```python
# Wrong: tests/conftest.py has 800 lines, including fixtures only 2 tests use
# Right: nested conftest files near the tests that need them
```

❌ Mistake 3: Expecting a fixture to be visible in a sibling or parent folder
✅ Correct: A conftest fixture is visible only at its level and below. A test in `tests/other/` cannot see a fixture defined in `tests/api/conftest.py` (error: `fixture 'x' not found`, verified).

---

## 🧠 Tricky Interview Question

**Q**: Both `tests/conftest.py` and `tests/api/conftest.py` define a fixture named `user`. A test in `tests/api/` and another in `tests/` request `user`. Which version does each get?

```python
# tests/conftest.py        -> user() returns {"name": "root-user"}
# tests/api/conftest.py    -> user(user) returns {**user, "role": "api"}
# tests/test_root.py       -> def test_root_user(user): ...
# tests/api/test_u.py      -> def test_user(user): ...
```

**Answer**:
```
tests/test_root.py   -> {"name": "root-user"}
tests/api/test_u.py  -> {"name": "root-user", "role": "api"}
```
The closest conftest wins (override), and the inner fixture can still ask for the outer one by using the same name as an argument. Both tests pass (verified).

---

## ⚫ Interview Questions + Answers

Q1: Can I have more than one conftest.py?
A1: Yes, one per directory. They are layered: outer loads first, inner can override.

Q2: What is the difference between a fixture in conftest.py and one in the test file?
A2: A fixture in the test file is visible only in that file. In conftest it is shared with the whole folder tree.

Q3: What are hooks like `pytest_addoption`?
A3: Functions with special names that pytest calls at specific moments (add CLI options, modify collected tests, report results). They are allowed in conftest.py or plugins, not in normal test files.

Q4: Why not import fixtures from a helper module?
A4: It works only if you also import it into each test module, which linters flag as unused, and it bypasses pytest's discovery. If you need a plugin-like module, register it with `pytest_plugins = ["tests.fixtures.db"]` in the root conftest.

Q5: Can `autouse=True` fixtures live in conftest?
A5: Yes. An autouse fixture in conftest runs for every test at that level and below, for example resetting a clock or clearing a cache.

---

## 🔷 When to Use + When Not to Use

✅ Use when:
- More than one test file needs the same fixture
- You need a CLI option, marker registration or collection hook
- You want folder-specific setup (api vs integration)

❌ Avoid when:
- Only one file uses the fixture (keep it in that file)
- You want to share plain helper functions (use a normal module)
- You are tempted to put application code in it (conftest is test-only)

---

## 📊 Visual Diagram

```
 tests/
 ├── conftest.py            ← level 1: user, --runslow hook
 ├── test_root.py           sees: user (root version)
 └── api/
     ├── conftest.py        ← level 2: user (overrides + extends level 1)
     └── test_u.py          sees: user (api version)

 Resolution: nearest conftest → parent → ... → pytest built-ins
```

---

## 📝 Key Terms (English + Hindi)
| Term | Meaning | Hindi |
|------|---------|-------|
| Fixture | Reusable setup/teardown injected by name | नाम से मिलने वाला setup |
| Hook | Special `pytest_*` function pytest calls | pytest द्वारा बुलाया जाने वाला function |
| Override | Inner fixture replaces the outer one | अंदर वाला बाहर वाले को बदलता है |
| rootdir | Top folder pytest uses as base | pytest का आधार folder |
| autouse | Fixture applied without asking | बिना माँगे लागू होने वाला fixture |
| Plugin | Extension module for pytest | pytest का extension |

---

## ⚡ 3-Line Summary
English: `conftest.py` holds shared fixtures and hooks that pytest loads automatically for its folder tree. Never import it; just ask for fixtures by argument name. Inner conftest files override outer ones.
Hindi: `conftest.py` में साझा fixtures और hooks होते हैं जिन्हें pytest अपने folder tree के लिए अपने-आप load करता है। इसे कभी import न करें, बस argument के नाम से fixture माँगें। अंदर की conftest बाहर वाली को override करती है।

---

## ➡️ Next Topic
**295. Fixtures Scope** — function, class, module, package and session scope, and how they affect speed and isolation.
